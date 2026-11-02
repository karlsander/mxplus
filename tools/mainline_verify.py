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


def verify_layout(original: bytes, patched: bytes, build: dict) -> list:
    assert sha256(original) == build['original_app_sha256']
    assert sha256(patched) == build['patched_app_sha256']
    scatter = build['scatter_extension']
    cut, size = scatter['insert_offset'], scatter['insert_length']
    assert cut == len(original) and len(patched) == cut+size
    assert scatter['runtime_address'] == 0x01017264
    assert scatter['code_address'] == 0x60664000
    assert 0 < scatter['code_length'] <= 0x2000 and scatter['code_length'] % 4 == 0
    assert build['code_bytes_remaining'] == 0x2000 - scatter['code_length']
    blob = patched[cut:]
    assert sha256(blob) == build['extension_sha256']
    assert size == scatter['data_length'] + scatter['code_length']
    assert scatter['data_length'] == build['writable_state']['size']
    assert scatter['code_load_offset'] == scatter['data_length']
    expected = bytearray(original+blob)
    occupied = set()
    for patch in build['patches']:
        assert patch['component'] == 'app_main'
        off = patch['file_offset']
        old,new = bytes.fromhex(patch['original']),bytes.fromhex(patch['replacement'])
        positions = set(range(off,off+len(old)))
        assert old and 0 <= off <= cut-len(old)
        assert not positions & occupied and len(old)==len(new)
        assert expected[off:off+len(old)] == old
        expected[off:off+len(new)] = new
        occupied.update(positions)
    assert bytes(expected) == patched
    old_ops,new_ops = recover(original)['operations'],recover(patched)['operations']
    assert len(old_ops)==len(new_ops)
    for i,(old,new) in enumerate(zip(old_ops,new_ops)):
        if i == 4:
            assert old == {'call':0x60000032,'kind':'copy','destination':0x01020000,'length':0,'source':0x600dffb4}
            assert new == dict(old,destination=0x01017264,length=scatter['data_length'],source=BASE+cut)
        elif i == 8:
            assert old == {'call':0x60000056,'kind':'copy','destination':0x40008000,'length':0,'source':0x600e0448}
            assert new == dict(old,destination=0x60664000,length=scatter['code_length'],
                              source=BASE+cut+scatter['data_length'])
        else: assert old == new
    machine=Machine(patched,scatter=False)
    machine.write(0x01017264,b'\xa5'*0xd9c)
    machine.write(0x60664000,b'\xa5'*0x2000)
    machine.uc.reg_write(UC_ARM_REG_SP,0x2001fff0)
    machine.uc.emu_start(BASE|1,BASE+0x7e,timeout=5_000_000,count=3_000_000)
    assert machine.uc.reg_read(UC_ARM_REG_PC)==BASE+0x7e
    for op in new_ops:
        if not op['length']:continue
        contents = (patched[op['source']-BASE:op['source']-BASE+op['length']]
                    if op['kind']=='copy' else bytes(op['length']))
        assert machine.read(op['destination'],op['length'])==contents
    assert machine.read(0x01017264,scatter['data_length'])==blob[:scatter['data_length']]
    assert machine.read(0x60664000,scatter['code_length'])==blob[scatter['data_length']:]
    sections=scatter['sections']
    assert [s['name'] for s in sections]==['.route_state','.usb_data','.usb_state','.generator_data','.text']
    covered=set()
    for section in sections:
        off=section['load_offset']
        assert off == (scatter['data_length'] if section['name']=='.text'
                       else section['address']-0x01017264)
        assert sha256(blob[off:off+section['size']])==section['sha256']
        assert not covered & set(range(off,off+section['size']))
        covered.update(range(off,off+section['size']))
        assert section['flags']&7 == (6 if section['name']=='.text' else 3)
    assert all(byte==0 for i,byte in enumerate(blob) if i not in covered)
    return [{'name':'Every changed byte is guarded; empty copies and the SDRAM heap base reserve extension memory',
             'status':'pass','extension_bytes':size,'code_address':hex(scatter['code_address']),
             'code_bytes_remaining':build['code_bytes_remaining']},
            {'name':'Original startup initializes all sections and preserves every original nonempty region',
             'status':'pass','sections':sections}]


def verify(original: bytes, patched: bytes, build: dict) -> tuple[dict, dict]:
    from routing_audio_verify import verify as verify_audio
    from routing_ui_verify import verify as verify_ui
    from routing_hardware_audit import verify_image as audit_hardware

    groups = verify_layout(original, patched, build)
    from routing_mpu_verify import verify as verify_mpu
    mpu = verify_mpu(original, patched, build)
    groups.extend(mpu['groups'])
    from sdram_code_verify import verify as verify_heap
    heap = verify_heap(original, patched, build)
    groups.extend(heap['groups'])
    from usb_audio_verify import verify as verify_usb
    usb = verify_usb(original, patched, build)
    assert usb['status'] == 'pass'
    groups.extend(usb['groups'])
    groups.extend(verify_shared_state(patched, build))
    from routing_storage_verify import verify as verify_storage
    storage = verify_storage(original, patched, build)
    groups.extend(storage['groups'])
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
        'details': {'heap': 'heap-verification.json', 'storage': 'storage-verification.json', 'ui': 'ui-verification.json', 'audio': 'audio-verification.json',
                    'hardware_initialization': 'hardware-audit.json'},
        'limits': [
            'This candidate has offline evidence only; prior panel observations do not validate its audio or recovery',
            'DSP execution and MMIO assumptions are stated in the separate audio report',
            'Instruction counts do not measure real-time deadline margin or CPU cycles',
        ],
    }
    return report, {'heap-verification.json': heap, 'usb-verification.json': usb, 'mpu-verification.json': mpu, 'storage-verification.json': storage, 'ui-verification.json': ui, 'audio-verification.json': audio,
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
