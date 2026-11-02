#!/usr/bin/env python3
"""Audit the original ARM sample callback and generator exchange-bank choice.

The original registration, interrupt dispatch, disconnected sample pump and
generic shared-port writer execute unchanged. Interrupt arrival, DSP numerical
execution, converter arithmetic and hardware timing are not emulated.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import struct

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine
from routing_audio_extract import reconstruct

ROOT = Path(__file__).resolve().parents[1]
MAIN_SHA256 = '256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b'
CONTEXT = 0x20000B24
CALLBACK_SLOT = CONTEXT + 0x80C
EXCHANGE = 0x40101000
GENERATOR_FIRST_INDEX = 0x40
GENERATOR_COUNT = 12


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


def original_offset(runtime):
    if 0x01000300 <= runtime < 0x0100f6a4:
        return 0xd0b8c + runtime - 0x01000300
    assert 0x60000000 <= runtime < 0x600d0b8c
    return runtime - 0x60000000


class AudioAuditMachine(Machine):
    def __init__(self, original, *, stub_mode_setup=False):
        super().__init__(original)
        self.uc.mem_map(0x40100000, 0x80000)
        self.visits = []
        self.mmio_writes = []
        self.stub_mode_setup = stub_mode_setup
        self.setup_calls = []
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)

    def _code(self, uc, address, size, user):
        self.visits.append(address)
        # Only unrelated normal-program setup bodies are isolated. The actual
        # program-mode switch and callback registration remain original code.
        if self.stub_mode_setup and address in (
                0x60023d12, 0x60023cd2, 0x600251f2, 0x60023c82):
            self.setup_calls.append(address)
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _write(self, uc, access, address, size, value, user):
        if 0x40000000 <= address < 0x40200000:
            self.mmio_writes.append((address, size, value))


def audit(original):
    assert sha256(original) == MAIN_SHA256, 'Unsupported main application'
    groups = []

    def passed(name, **details):
        groups.append({'name': name, 'status': 'pass', **details})

    # The pointer is the only production audio integration patch. Its original
    # target is guarded independently of the final candidate builder.
    assert original[0x168c:0x1690] == u32(0x01009841)
    assert original[0x1690:0x1694] == u32(CONTEXT)
    guards = (
        (0x60001670, '10b50022054b11460548'),
        (0x01009cc0, 'e4481c3801680022c1f303610260'),
        (0x0100c8e0, '00f60c00fef70cb8'),
        (0x0100a900, '50f82120002a01d0084610477047'),
    )
    # Guard strings below are captured from exact original instructions. Any
    # discrepancy is a source-evidence failure, not permission to accept it.
    site_evidence = []
    for runtime, expected_hex in guards:
        offset = original_offset(runtime)
        expected = bytes.fromhex(expected_hex)
        actual = original[offset:offset + len(expected)]
        assert actual == expected, (hex(runtime), actual.hex(), expected_hex)
        site_evidence.append({'runtime': hex(runtime), 'decoded_offset': hex(offset),
                              'bytes': actual.hex()})
    passed('Exact original sample registration and IRQ-dispatch instructions',
           component='app_main', pointer_decoded_offset='0x168c',
           original_callback='0x01009841', sites=site_evidence)

    machine = AudioAuditMachine(original)
    machine.call(0x60001670)
    assert machine.read(CALLBACK_SLOT, 4) == u32(0x01009841)
    # Existing registrations must not be silently replaced by the generic API.
    rc, _ = machine.call(0x0100c8f0, CONTEXT, 0, 0, 0x60000001)
    assert rc == 0 and machine.read(CALLBACK_SLOT, 4) == u32(0x01009841)
    passed('Unchanged registration fills DSP0 callback slot zero and refuses replacement',
           callback_table='0x20001330', usb_state='all endpoints inactive')

    cases = []
    for rate in (44100, 48000, 96000):
        machine = AudioAuditMachine(original)
        machine.write(CONTEXT, u32(rate))
        machine.call(0x60001670)
        machine.write(EXCHANGE, bytes([0xa5]) * 0x400)
        machine.visits.clear()
        machine.mmio_writes.clear()
        _, instructions = machine.call(0x01009cc0, measure=True)
        path = (0x01009cc0, 0x0100c8e0, 0x0100a900, 0x01009840)
        assert all(machine.visits.count(address) == 1 for address in path)
        assert machine.read(EXCHANGE, 18 * 4) == bytes(18 * 4)
        assert machine.read(EXCHANGE + 18 * 4, 0x400 - 18 * 4) == \
            bytes([0xa5]) * (0x400 - 18 * 4)
        writes = [entry for entry in machine.mmio_writes
                  if EXCHANGE <= entry[0] < EXCHANGE + 0x400]
        assert writes == [(EXCHANGE + lane * 4, 4, 0) for lane in range(18)]
        assert machine.mmio_writes[0] == (0x40100640, 4, 0)
        cases.append({'rate_state': rate, 'executed_arm_instructions': instructions,
                      'playback_writes': len(writes), 'capture_and_generator_slots_preserved': True})
    passed('Original DSP IRQ dispatch reaches one-frame pump with USB endpoints inactive',
           cases=cases, interrupt_arrival='Invoked explicitly; not timed or generated by emulated DSP',
           cadence='One frame per original callback; sample cadence remains hardware-derived inference')

    mode_cases = []
    for mode in range(13):
        machine = AudioAuditMachine(original, stub_mode_setup=True)
        machine.call(0x60023d84, 0x20016000, mode)
        registered = machine.read(CALLBACK_SLOT, 4) == u32(0x01009841)
        assert registered == (mode < 12)
        mode_cases.append({'program_mode': mode, 'registered': registered})
    passed('Original program-mode switch registers sample callback without USB connection test',
           cases=mode_cases,
           normal_generator_modes=[0, 1, 2, 3],
           diagnostic_modes='Original callback remains present; extension must exclude modes above 3',
           isolated_setup_bodies=['0x60023d12', '0x60023cd2', '0x600251f2', '0x60023c82'])

    # Same original CPU shared-port writer used by stock parameter code. The
    # descriptors below are supplied indices, not claimed stock allocations.
    # This proves the original ARM address calculation, not MMIO capacity.
    machine = AudioAuditMachine(original)
    descriptor = 0x20016000
    shared_cases = []
    for core in (0, 1):
        for index in range(GENERATOR_FIRST_INDEX, GENERATOR_FIRST_INDEX + GENERATOR_COUNT):
            value = 0x3e800000 + index
            machine.write(descriptor, u32(0) + u32(0) + u32(index))
            machine.mmio_writes.clear()
            machine.call(0x0100bdfc, CONTEXT, core, descriptor, value)
            address = EXCHANGE + core * 0x400 + index * 4
            assert machine.mmio_writes == [(address, 4, value)]
            assert machine.read(address, 4) == u32(value)
            shared_cases.append({'core': core, 'index': index, 'cpu_address': hex(address)})
    passed('Original generic shared-port writer establishes index-to-CPU-address calculation',
           cases=shared_cases, core_stride_bytes=0x400,
           limit='Core stride suggests 256 words; real register capacity is not measured')

    upload, programs = reconstruct()
    occupancy = []
    for core, image in enumerate(programs):
        # Scan every halfword, including immediate/data fields: this is a
        # conservative exclusion test, not a speculative DSP instruction decoder.
        logical = b''.join(struct.pack('>I', value)
                           for value in struct.unpack('<8192I', image))
        refs = defaultdict(list)
        for offset in range(0, len(logical), 2):
            value = struct.unpack_from('>H', logical, offset)[0]
            if 0xa000 <= value < 0xa100:
                refs[value].append(offset)
            assert not 0xa040 <= value <= 0xa04b, (core, offset, value)
        occupancy.append({'core': core,
            'program_sha256': sha256(image),
            'a0xx_halfwords': {hex(value): [hex(offset) for offset in offsets]
                              for value, offsets in sorted(refs.items())},
            'reserved_generator_halfwords_absent': ['0xa040', '0xa04b']})
    passed('All uploaded normal DSP programs contain no reference to proposed generator indices',
           cases=occupancy,
           source='Original uploader reconstruction, including boundary merge instructions',
           dynamic_reprogramming='Does not prove arbitrary diagnostic/debug program writes cannot touch these indices')

    return {'status': 'pass', 'component': 'app_main',
        'original_app_sha256': sha256(original), 'groups': groups,
        'generator_ports': {
            'noise': {'index': 0x40, 'dsp_operand': '0xa040', 'cpu_address': '0x40101100'},
            'bass_drum_first': {'index': 0x41, 'dsp_operand': '0xa041', 'cpu_address': '0x40101104'},
            'bass_drum_last': {'index': 0x4b, 'dsp_operand': '0xa04b', 'cpu_address': '0x4010112c'}},
        'limits': [
            'No physical DSP exchange reads, audio, callback timing, deadline or CPU margin measured',
            'The existing callback processes one frame; interrupt arrival cadence is not emulated',
            'Core-bank size is inferred from original address stride, not hardware register documentation',
            'Static bank exclusion covers reconstructed normal programs; diagnostic programs are excluded by the extension',
            'No DSP numerical arithmetic or hardware converter behavior is emulated',
        ]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware', type=Path)
    p.add_argument('--output', type=Path, default=ROOT / 'analysis/internal-sources-audio-audit.json')
    args = p.parse_args()
    raw = args.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256, 'Unsupported original firmware'
    report = audit(component_unpacked(raw, COMPONENT_BY_NAME['app_main']))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups_passed': len(report['groups'])}))


if __name__ == '__main__':
    main()
