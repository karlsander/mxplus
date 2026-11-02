#!/usr/bin/env python3
"""Verify the combined mainline firmware without accessing hardware.

Original ARM startup and panel code, the compiled routing extension, and the
original DSP control helpers execute in explicit instruction-level harnesses.
DSP operand interpretation and command delivery have separately stated model
boundaries; this is not a complete MX-1 or a physical audio test.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_PC

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine, BASE
from memory_map import recover


def verify_layout(original: bytes, patched: bytes, build: dict) -> list[dict]:
    """Account for every changed byte and execute the complete startup copies."""
    assert sha256(original) == build['original_app_sha256']
    assert sha256(patched) == build['patched_app_sha256']
    scatter = build['scatter_extension']
    cut, size = scatter['insert_offset'], scatter['insert_length']
    assert cut == 0xdff30 and scatter['runtime_address'] == 0x0100f6a4
    code_size = scatter['code_length']
    assert 0 < code_size <= 0x95c and code_size % 4 == 0
    assert size == code_size + 356
    assert len(patched) == len(original) + size
    extension = patched[cut:cut + size]
    assert sha256(extension) == build['extension_sha256']
    assert build['sram_bytes_remaining'] == 0x95c - code_size

    # Independently replay the recorded changes. Unrecorded changes, overlapping
    # patches, wrong old bytes, or a shifted existing destination must fail.
    expected = bytearray(original[:cut] + extension + original[cut:])
    modified = set(range(cut, cut + size))
    updates = scatter['startup_updates']
    assert [u['offset'] for u in updates] == [0xe8, 0x100, 0x114, 0x128, 0x13c, 0x150]
    for update in updates:
        off = update['offset']
        assert struct.unpack_from('<I', expected, off)[0] == update['before']
        expected_after = (update['before'] + code_size if off == 0xe8 else
                          BASE + cut + code_size if off == 0x114 else update['before'] + size)
        assert update['after'] == expected_after
        struct.pack_into('<I', expected, off, update['after'])
        modified.update(range(off, off + 4))
    for patch in build['patches']:
        assert patch['component'] == 'app_main'
        off = patch['file_offset']
        before, after = bytes.fromhex(patch['original']), bytes.fromhex(patch['replacement'])
        assert before and len(before) == len(after)
        assert 0 <= off <= len(expected) - len(before)
        positions = set(range(off, off + len(before)))
        assert not positions & modified, 'Overlapping or unreviewed patch'
        assert expected[off:off + len(before)] == before
        expected[off:off + len(after)] = after
        modified.update(positions)
    assert bytes(expected) == patched, 'Unaccounted application byte changes'

    old_map = recover(original)['operations']
    new_map = recover(patched)['operations']
    assert len(old_map) == len(new_map)
    for index, (old, new) in enumerate(zip(old_map, new_map)):
        if index == 4:
            assert old['length'] == 0 and old['destination'] == 0x01020000
            assert new == dict(old, destination=0x0101727c, length=356, source=BASE + cut + code_size)
            continue
        assert old['kind'] == new['kind'] and old['destination'] == new['destination']
        assert new['length'] == old['length'] + (code_size if index == 0 else 400 if index == 3 else 0)
        if old['kind'] == 'copy':
            assert new['source'] == old['source'] + (size if old['source'] >= BASE + cut else 0)

    started = []
    for image in (original, patched):
        machine = Machine(image, scatter=False)
        machine.uc.reg_write(UC_ARM_REG_SP, 0x2001fff0)
        machine.write(0x0100f6a4, b'\xcc' * size)
        machine.uc.emu_start(BASE | 1, BASE + 0x7e, timeout=2_000_000, count=2_000_000)
        assert machine.uc.reg_read(UC_ARM_REG_PC) == BASE + 0x7e
        for index, operation in enumerate(recover(image)['operations']):
            length = operation['length']
            if not length:
                continue
            contents = (image[operation['source'] - BASE:operation['source'] - BASE + length]
                        if operation['kind'] == 'copy' else bytes(length))
            if image is patched and index == 3:
                contents = bytes(length - 376) + extension[code_size:] + bytes(20)
            assert machine.read(operation['destination'], length) == contents
        started.append(machine)
    for operation in old_map:
        if operation['destination'] != 0x01000300 and operation['length']:
            address, length = operation['destination'], operation['length']
            assert started[0].read(address, length) == started[1].read(address, length)
    assert started[1].read(0x0100f6a4, code_size) == extension[:code_size]
    assert started[1].read(0x0101727c, 356) == extension[code_size:]
    return [
        {'name': 'Every application change matches recorded guarded patches and scatter insertion',
         'status': 'pass', 'patch_sites': len(build['patches']), 'extension_bytes': size,
         'sram_bytes_remaining': 0x95c - code_size},
        {'name': 'Actual original startup installs routing code and preserves existing initialized data and BSS',
         'status': 'pass', 'runtime_interval': ['0x0100f6a4', hex(0x0100f6a4 + code_size)],
         'existing_nonempty_destinations_unchanged': True,
         'repurposed_empty_copy': 'USB descriptor at 0x0101727c'},
    ]


def verify(original: bytes, patched: bytes, build: dict) -> tuple[dict, dict]:
    from routing_audio_verify import verify as verify_audio
    from routing_ui_verify import verify as verify_ui
    from routing_hardware_audit import verify_image as audit_hardware

    groups = verify_layout(original, patched, build)
    from routing_mpu_verify import verify as verify_mpu
    mpu = verify_mpu(original, patched, build)
    groups.extend(mpu['groups'])
    from usb_audio_verify import verify as verify_usb
    usb = verify_usb(original, patched, build)
    assert usb['status'] == 'pass'
    groups.extend(usb['groups'])
    groups.extend(verify_shared_state(patched, build))
    ui = verify_ui(original, patched, build)
    assert ui['ui_only_fixture'] is False
    assert all(group['status'] == 'pass' for group in ui['groups'])
    audio = verify_audio(original, patched, build)
    assert audio['status'] == 'pass'
    assert all(group['status'] == 'pass' for group in audio['groups'])
    hardware = audit_hardware(original)
    assert hardware['status'] == 'pass'
    for audit in ('dsp_task_dispatch', 'pc_operand_format', 'native_input_gates'):
        assert hardware[audit]['status'] == 'pass'
    groups.extend(ui['groups'])
    groups.extend(audio['groups'])
    groups.append({'name': 'Original serial-I/O initialization at all three rates and both digital modes',
                   'status': 'pass', 'sample_rates': [44100, 48000, 96000], 'cases': 9})
    groups.append({'name': 'Original DSP event dispatch, harmless empty parameter queue and flag delivery',
                   'status': 'pass', 'event': 8, 'empty_handler_mmio_writes': 0})
    groups.append({'name': 'Independent factory graph audit matches all 18 raw PC and 18 serial read bindings',
                   'status': 'pass', 'numeric_dsp_execution': False})
    groups.append({'name': 'Original native input gates and connection callbacks distinguish native and PC paths',
                   'status': 'pass', 'native_gates': 13, 'connection_callback_cases': 20})
    report = {
        'status': 'pass', 'original_app_sha256': sha256(original),
        'patched_app_sha256': sha256(patched),
        'candidate_container_sha256': build['container_sha256'],
        'extension_sha256': build['extension_sha256'], 'groups': groups,
        'hardware_access': False,
        'scope': 'Integrated candidate ARM instructions with explicit DSP and peripheral models',
        'details': {'ui': 'ui-verification.json', 'audio': 'audio-verification.json',
                    'hardware_initialization': 'hardware-audit.json'},
        'limits': [
            'This candidate has offline evidence only; prior panel observations do not validate its audio or recovery',
            'DSP execution and MMIO assumptions are stated in the separate audio report',
            'Instruction counts do not measure real-time deadline margin or CPU cycles',
        ],
    }
    return report, {'usb-verification.json': usb, 'mpu-verification.json': mpu, 'ui-verification.json': ui, 'audio-verification.json': audio,
                    'hardware-audit.json': hardware}


def verify_shared_state(patched, build):
    """USB initialization/control requests and routing events share one RAM map."""
    from routing_ui_verify import UIMachine
    from usb_audio_verify import DeviceMachine, request, expect_reply
    class CombinedMachine(UIMachine, DeviceMachine):
        pass
    symbols = build['symbols']
    for rate in (44100, 48000, 96000):
        machine = CombinedMachine(patched, symbols, stub_routes=False)
        assert machine.call(0x6000d980, rate)[0] == 0
        descriptor = machine.read(symbols['mx1_uac2_configuration'], 355)
        for strip in range(11):
            machine.packet(2, strip + 0x29, patched=True)
            machine.packet(4, 1, 1, patched=True)
            machine.packet(1, strip + 0x29, patched=True)
            assert machine.read(symbols['mx1_route_state'], 11) == bytes(
                1 if i <= strip else 0 for i in range(11))
            machine.setup(request(0xa1, 1, 0x100, 0x1000, 4))
            expect_reply(machine, struct.pack('<I', rate))
            assert machine.read(symbols['mx1_uac2_configuration'], 355) == descriptor
            assert machine.read(symbols['mx1_route_state'], 11) == bytes(
                1 if i <= strip else 0 for i in range(11))
    return [{'name': 'USB clock requests and routing edits coexist in the same protected-memory machine',
             'status': 'pass', 'rates': [44100, 48000, 96000], 'strips_per_rate': 11,
             'boundaries': 'USB hardware start/FIFO, parameter store, panel delivery and RTOS posts stubbed; no scheduling or DSP arithmetic'}]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', type=Path)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256, 'Original firmware identity mismatch'
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((args.build / 'build-report.json').read_text())
    assert build['input_sha256'] == ORIGINAL_SHA256
    patched = (args.build / 'app_main.mainline.bin').read_bytes()
    report, details = verify(original, patched, build)
    for name, detail in details.items():
        (args.build / name).write_text(json.dumps(detail, indent=2) + '\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups': [g['name'] for g in report['groups']],
                      'patched_app_sha256': sha256(patched)}, indent=2))


if __name__ == '__main__':
    main()
