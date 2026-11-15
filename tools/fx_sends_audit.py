#!/usr/bin/env python3
"""Trace stock send controls and effect-slot ownership before adding DSP buses.

This is a read-only firmware investigation, not a new firmware generator or an
ESC2 arithmetic/timing emulator. --check compares the deterministic evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
    UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
    UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
)

from container_tool import COMPONENT_BY_NAME, component_unpacked
from routing_audio_extract import reconstruct
from routing_hardware_audit import AuditMachine, ORIGINAL_SHA256, MAIN_SHA256, STOP, u32

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'analysis/fx-sends-audit.json'
REGS = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)
SAVED = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
         UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)
SLOT_STATE = 0x600ccdbc


def digest(data):
    return hashlib.sha256(data).hexdigest()


class SendMachine(AuditMachine):
    def __init__(self, blob):
        super().__init__(blob)
        self.requests = []
        self.selecting = False
        self.loading = False
        self.load_request = None
        self.selections = []
        self.stubs = set()
        self.uc.hook_add(UC_HOOK_CODE, self.trace)
        # The actual stock constructors establish core and relocation contexts.
        self.checked(0x60024228, 0, 0)

    def trace(self, uc, address, size, user):
        args = [uc.reg_read(r) for r in REGS]
        sp = uc.reg_read(UC_ARM_REG_SP)
        if self.loading:
            if address in (0x6000c59e, 0x60026fec):
                # Scope ends before parameter replay and DSP memory clearing.
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
                return
            if address == 0x60026f66:
                self.load_request = args + list(struct.unpack('<4I', uc.mem_read(sp, 16)))
                uc.emu_stop()
                return
        if address == 0x0100b5ea:
            self.requests.append({'kind': 'coefficient', 'core': args[1],
                                  'index': args[2], 'float_bits': args[3],
                                  'smoothing': self.register(sp)})
        elif address == 0x0100baee:
            self.requests.append({'kind': 'embedded_float', 'core': args[1],
                                  'offset': args[2], 'format': args[3],
                                  'float_bits': self.register(sp)})
        # Neither writer is stubbed: its original command-register writes run.
        if self.selecting:
            if address in (0x6001e65e, 0x6001a1ce):
                self.stubs.add(hex(address))
                # Neutral MFX depth and a fixed 120 BPM; parameter DB modeled.
                uc.reg_write(UC_ARM_REG_R0, 64 if address == 0x6001e65e else 120)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == 0x60029ee4:
                self.selections.append({'slot': self.register(SLOT_STATE),
                                        'algorithm': args[1]})
                # Record the loader call, not its DSP/RTOS side effects.
                self.stubs.add(hex(address))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address in (0x6002a2cc, 0x6002a768, 0x60029e30):
                self.stubs.add(hex(address))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def checked(self, address, first, second):
        seeds = [0x44cc0000 + i * 0x101 for i in range(len(SAVED))]
        for reg, seed in zip(SAVED, seeds):
            self.uc.reg_write(reg, seed)
        self.requests.clear()
        self.writes.clear()
        self.call(address, first, second)
        assert [self.uc.reg_read(r) for r in SAVED] == seeds
        return list(self.requests)


def callback_registry(blob):
    # The original registration records are {global ID, callback, secondary}.
    # Strings live in a separate, ID-indexed table at decoded 0x6f278.
    records = {}
    for offset in range(0xb5594, 0xb710c, 12):
        parameter, callback, secondary = struct.unpack_from('<III', blob, offset)
        assert parameter < 0x700 and 0x60000000 < callback < 0x60060000
        assert parameter not in records
        records[parameter] = (callback & ~1, offset)
    return records


def audit_controls(blob):
    registry = callback_registry(blob)
    machine = SendMachine(blob)
    channels = []
    for channel in range(11):
        callback, record = registry[0x130 + channel]
        assert callback == 0x600299d6 + channel * 10
        values = []
        for value in range(128):
            requests = machine.checked(callback, 0, value)
            assert len(requests) == 1
            request = requests[0]
            assert request['kind'] == 'coefficient'
            assert (request['core'], request['index']) == (1, 0x2d + channel)
            assert request['smoothing'] == 0
            values.append(request['float_bits'])
            assert machine.writes, 'Original coefficient writer did not run'
        floats = [struct.unpack('<f', u32(x))[0] for x in values]
        assert floats[0] == 0 and floats[-1] == 1
        assert all(a < b for a, b in zip(floats, floats[1:]))
        channels.append({'channel': channel, 'global_parameter': 0x130 + channel,
                         'registration_decoded_offset': hex(record),
                         'callback_runtime': hex(callback),
                         'callback_decoded_offset': hex(callback - 0x60000000),
                         'core': 1, 'coefficient_index': 0x2d + channel,
                         'gain_table_sha256': digest(b''.join(map(u32, values))),
                         'gain_at_0_64_127': [floats[i] for i in (0, 64, 127)]})
    assert len({x['gain_table_sha256'] for x in channels}) == 1
    switches = []
    for parameter, callback, dsp_offset in ((6, 0x60029b98, 0x1a88),
                                             (7, 0x60029bbc, 0x1a34)):
        assert registry[parameter][0] == callback
        for value in (0, 1):
            requests = machine.checked(callback, 0, value)
            assert requests == [{'kind': 'embedded_float', 'core': 1,
                                 'offset': dsp_offset, 'format': 0,
                                 'float_bits': 0x3f800000 if value else 0}]
            assert machine.writes == [(0x40100900, 4, 0x40070000 + dsp_offset),
                                      (0x40100904, 4, 0x3f800000 if value else 0)]
            switches.append({'global_parameter': parameter, 'value': value,
                             'callback_runtime': hex(callback),
                             'callback_decoded_offset': hex(callback - 0x60000000),
                             'requests': requests})
    phones = []
    for parameter, callback, indices in ((0xac, 0x60027cc4, [0x28]),
                                         (0xad, 0x60027cce, [0x26, 0x27])):
        assert registry[parameter][0] == callback
        for value in (0, 64, 127):
            requests = machine.checked(callback, 0, value)
            assert [r['index'] for r in requests] == indices
            assert all(r['kind'] == 'coefficient' and r['core'] == 0 for r in requests)
            phones.append({'global_parameter': parameter, 'value': value,
                           'callback_runtime': hex(callback),
                           'callback_decoded_offset': hex(callback - 0x60000000),
                           'requests': requests})
    return {'channel_aux': channels, 'routing_switches': switches,
            'headphone_controls': phones, 'original_callback_cases': 11 * 128 + 4 + 6,
            'writer_stubs': [], 'parameter_stubs': []}


def audit_slot_ownership(blob):
    machine = SendMachine(blob)
    machine.selecting = True
    machine.uc.mem_write(SLOT_STATE, u32(0))
    for algorithm in (1, 4, 1):
        machine.checked(0x6002b132, 1, algorithm)
    assert machine.selections == [{'slot': 1, 'algorithm': 1},
                                   {'slot': 0, 'algorithm': 4},
                                   {'slot': 1, 'algorithm': 1}]
    return {'entry_runtime': '0x6002b132', 'entry_decoded_offset': '0x2b132',
            'slot_state_runtime': hex(SLOT_STATE),
            'input_first_argument': 1, 'loader_calls': machine.selections,
            'stubbed_calls': sorted(machine.stubs),
            'finding': 'The original type-change entry alternates both slots; neither is reserved for an independent send.'}


def audit_programs(blob):
    def word(address):
        return struct.unpack_from('<I', blob, address - 0x60000000)[0]

    baseline, _ = reconstruct()
    machine = SendMachine(blob)
    machine.loading = True
    effect_programs = []
    for algorithm in range(20):
        for slot, table in enumerate((0x600caaac, 0x600cab4c)):
            descriptor = word(table + algorithm * 4)
            offset, length, source = struct.unpack_from('<III', blob, descriptor - 0x60000000)
            assert offset == (0x4000, 0x6000)[slot]
            assert 0 < length <= 0x2000 and length % 2 == 0
            machine.uc.mem_write(SLOT_STATE, u32(slot))
            machine.uc.reg_write(UC_ARM_REG_SP, 0x2003f000)
            machine.uc.reg_write(UC_ARM_REG_LR, STOP | 1)
            machine.uc.reg_write(UC_ARM_REG_R0, 0)
            machine.uc.reg_write(UC_ARM_REG_R1, algorithm)
            machine.load_request = None
            machine.uc.emu_start(0x60029ee5, 0, count=1000)
            assert machine.uc.reg_read(UC_ARM_REG_PC) == 0x60026f66
            request = machine.load_request
            assert request is not None
            assert (request[1], request[2], request[6], request[7]) == (1, descriptor, offset, slot + 1)
            assert machine.register(SLOT_STATE + 0x60 + slot * 4) == algorithm
            data_offset, data_length, data_source = struct.unpack_from('<III', blob, request[3] - 0x60000000)
            # Same original descriptor wrapper, boundary logic and explicit DMA
            # byte-copy model as the existing routing uploader investigation.
            report, images = reconstruct(tables=(0x600ba008, descriptor), counts=(0, 1))
            assert report['chunks'][0]['core'] == 1
            logical = b''.join(struct.pack('>I', x) for x in struct.unpack('<8192I', images[1]))
            assert not any(logical[:offset]) and not any(logical[offset + length:])
            effect_programs.append({'algorithm': algorithm, 'slot': slot,
                                    'descriptor_runtime': hex(descriptor),
                                    'descriptor_decoded_offset': hex(descriptor - 0x60000000),
                                    'source_runtime': hex(source),
                                    'source_decoded_offset': hex(source - 0x60000000),
                                    'logical_program_offset': offset, 'length_bytes': length,
                                    'logical_program_sha256': digest(logical[offset:offset + length]),
                                    'loader_request': [hex(x) for x in request],
                                    'data_descriptor_runtime': hex(request[3]),
                                    'data_descriptor_decoded_offset': hex(request[3] - 0x60000000),
                                    'data_offset_bytes': data_offset, 'data_length_bytes': data_length,
                                    'data_source_runtime': hex(data_source)})
    return {'normal_program_sha256': baseline['instruction_memory_sha256'],
            'normal_chunks': baseline['chunks'], 'effect_programs': effect_programs,
            'program_upload_cases': len(effect_programs),
            'loader_prefix_cases': len(effect_programs),
            'loader_prefix_stubs': ['0x6000c59e parameter-view construction',
                                    '0x60026fec coefficient clearing'],
            'loader_prefix_stop_before': '0x60026f66 live load transaction',
            'maximum_effect_program_bytes': max(x['length_bytes'] for x in effect_programs),
            'not_established': ['Instruction-cycle budget', 'Simultaneous effect execution',
                                'Independent delay-buffer and coefficient ownership',
                                'Pre-pan mono tap and additional bus arithmetic']}


def audit():
    stock = (ROOT / 'inputs/MX1_UPD.original.bin').read_bytes()
    assert digest(stock) == ORIGINAL_SHA256, 'Unsupported stock update'
    blob = component_unpacked(stock, COMPONENT_BY_NAME['app_main'])
    assert digest(blob) == MAIN_SHA256
    assert blob == (ROOT / 'analysis/container_app_main.bin').read_bytes()
    return {'status': 'pass', 'scope': 'Stock ARM control and upload evidence only; no send implementation',
            'original_update_sha256': ORIGINAL_SHA256, 'main_sha256': MAIN_SHA256,
            'controls': audit_controls(blob), 'slot_ownership': audit_slot_ownership(blob),
            'programs': audit_programs(blob),
            'limitations': ['ESC2 arithmetic, external delay RAM and timing are not emulated.',
                            'MMIO is recorded storage; no physical DSP accepts these commands.',
                            'Uploader DMA is modeled as a byte copy.',
                            'Type-change parameter queries, loader and subsequent effect setup are stubbed only in the slot-ownership case.',
                            'No candidate, panel controls, output routing or hardware is changed.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare against checked-in audit evidence')
    args = parser.parse_args()
    report = audit()
    rendered = json.dumps(report, indent=2) + '\n'
    if args.check:
        assert REPORT.read_text() == rendered, 'Stock send audit evidence differs'
    else:
        REPORT.write_text(rendered)
    print(json.dumps({'status': 'pass', 'callback_cases': report['controls']['original_callback_cases'],
                      'program_upload_cases': report['programs']['program_upload_cases'],
                      'send_implementation': False, 'hardware_validation': False}))


if __name__ == '__main__':
    main()
