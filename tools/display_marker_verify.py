#!/usr/bin/env python3
"""Verify the exact display diagnostic bytes and execute the original font path.

Only final segment delivery to the panel is stubbed for direct character/format
cases. Normal-renderer integration additionally uses the documented UIMachine
parameter/modal stubs. No firmware is installed and no USB hardware is opened.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP)

from build_display_marker import AFTER, BEFORE, FILENAME, OFFSET, ROOT, RUNTIME
from container_candidate_verify import verify as verify_container
from container_tool import COMPONENT_BY_NAME, ORIGINAL_SHA256, component_unpacked, sha256
from host_probe_verify import BASE, Machine
from memory_map import recover
from routing_ui_verify import UIMachine, REGS, CONTEXT

SEGMENTS = 0x0100D134


class CharacterMachine(Machine):
    def __init__(self, image):
        super().__init__(image)
        self.outputs = []
        self.uc.hook_add(UC_HOOK_CODE, self.delivery, begin=SEGMENTS, end=SEGMENTS)

    def delivery(self, uc, address, size, user):
        self.outputs.append(tuple(uc.reg_read(r) for r in
            (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def checked(self, address, *args, flags=0):
        saved = [0x56780000 + n * 0x101 for n in range(len(REGS))]
        for reg, value in zip(REGS, saved):
            self.uc.reg_write(reg, value)
        self.write(0x2001FFF0, flags.to_bytes(4, 'little'))
        self.outputs.clear()
        self.call(address, *args)
        assert [self.uc.reg_read(r) for r in REGS] == saved
        return list(self.outputs)


class RendererMachine(UIMachine):
    def __init__(self, image):
        self.outputs = []
        super().__init__(image)

    def instruction(self, uc, address, size, user):
        if address == SEGMENTS:
            self.outputs.append(tuple(uc.reg_read(r) for r in
                (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)))
            self.ret()
        elif address != 0x0100280A:
            super().instruction(uc, address, size, user)
        # Execute the actual character/font routine; do not use UIMachine's
        # earlier stub at this address, which could hide the diagnostic patch.


def verify(original_container, candidate, patched, build, *, check_committed=False):
    assert sha256(original_container) == ORIGINAL_SHA256 == build['input_sha256']
    assert sha256(candidate) == build['container_sha256']
    original = component_unpacked(original_container, COMPONENT_BY_NAME['app_main'])
    assert sha256(original) == build['original_app_sha256']
    assert patched == component_unpacked(candidate, COMPONENT_BY_NAME['app_main'])
    assert sha256(patched) == build['patched_app_sha256']
    assert len(patched) == len(original)
    assert original[OFFSET:OFFSET + 2] == BEFORE and patched[OFFSET:OFFSET + 2] == AFTER
    expected = bytearray(original)
    expected[OFFSET:OFFSET + 2] = AFTER
    assert patched == bytes(expected), 'Unrecorded decoded application change'
    assert {k: v for k, v in recover(original).items() if k != 'sha256'} == {
        k: v for k, v in recover(patched).items() if k != 'sha256'}
    assert original_container[:0x80000] == candidate[:0x80000]
    assert original_container[0x200000:] == candidate[0x200000:]
    assert build['patches'] == [{'label': 'Shared display character becomes ASCII 8 before original font lookup',
        'file_offset': OFFSET, 'runtime_address': RUNTIME, 'original': BEFORE.hex(),
        'replacement': AFTER.hex(), 'component': 'app_main'}]
    checks = [{'name': 'Exactly two decoded main bytes changed; startup and all other components preserved',
               'status': 'pass'}]

    # Execute startup rather than assuming the patched load-time bytes arrive
    # in the SRAM instruction stream used by display callers.
    for image, expected_instruction in ((original, BEFORE), (patched, AFTER)):
        machine = Machine(image, scatter=False)
        machine.uc.reg_write(UC_ARM_REG_SP, 0x2001FFF0)
        machine.uc.emu_start(BASE | 1, BASE + 0x7E, timeout=5_000_000, count=3_000_000)
        assert machine.uc.reg_read(UC_ARM_REG_PC) == BASE + 0x7E
        assert machine.read(RUNTIME, 2) == expected_instruction
        for op in recover(image)['operations']:
            if op['length']:
                data = (image[op['source'] - BASE:op['source'] - BASE + op['length']]
                        if op['kind'] == 'copy' else bytes(op['length']))
                assert machine.read(op['destination'], op['length']) == data
    checks.append({'name': 'Actual original startup copies the two-byte marker into its SRAM instruction site',
                   'status': 'pass'})

    old, new = CharacterMachine(original), CharacterMachine(patched)
    cases = 0
    for display, width in ((0, 3), (1, 4)):
        for position in range(width):
            for flags in (0, 0x40):
                reference = old.checked(0x0100280A, 0x60512984, display, position, ord('8'), flags=flags)
                assert reference == [(display, position, 0x7F, flags)]
                for character in range(256):
                    assert new.checked(0x0100280A, 0x60512984, display, position,
                                       character, flags=flags) == reference
                    cases += 1
    for display in (2, 3, 0x7FFFFFFF):
        assert new.checked(0x0100280A, 0x60512984, display, 0, ord('A')) == []
    assert old.checked(0x0100280A, 0x60512984, 1, 0, ord(' ')) != [(1, 0, 0x7F, 0)]
    checks.append({'name': 'All 256 character bytes map to the original 8 glyph at all seven display positions',
                   'status': 'pass', 'cases': cases, 'segment_bits': '0x7f',
                   'callee_saved_registers_and_stack_preserved': True,
                   'delivery_flags_preserved': [0, 0x40], 'invalid_display_positive_cases': 3})

    formats = []
    for display, width in ((0, 3), (1, 4)):
        new.write(0x20018000, b'ABCD')
        outputs = new.checked(0x01002A00, 0x60512984, display, 0x20018000, 0)
        assert outputs == [(display, i, 0x7F, 0) for i in range(width)]
        formats.append({'api': 'text', 'display': display, 'characters': width})
        for address in (0x0100282E, 0x0100297A):
            for number in (-1234, 0, 1234):
                outputs = new.checked(address, 0x60512984, display, number, 0)
                assert len(outputs) == width and all(o[0] == display and o[2] == 0x7F for o in outputs)
                formats.append({'api': hex(address), 'display': display, 'number': number})
    checks.append({'name': 'Original text, integer and decimal-format loops reach marker without SELECT',
                   'status': 'pass', 'cases': formats})

    old_renderer, new_renderer = RendererMachine(original), RendererMachine(patched)
    old_renderer.checked(0x60013356, CONTEXT)
    new_renderer.checked(0x60013356, CONTEXT)
    assert len(new_renderer.outputs) == 4
    assert new_renderer.outputs == [(1, position, 0x7F, 0) for position in (3, 2, 1, 0)]
    assert old_renderer.outputs != new_renderer.outputs
    checks.append({'name': 'Original normal tempo renderer produces four 8 glyphs without held keys',
                   'status': 'pass', 'stock_outputs': old_renderer.outputs,
                   'marker_outputs': new_renderer.outputs,
                   'modeled': 'Existing UIMachine parameter/modal boundaries; real character lookup now executes'})

    container = verify_container(original_container, candidate)
    assert [c['component'] for c in container['changed_decoded_components']] == ['app_main']
    checks.append({'name': 'Original decoder, updater write plan and post-write checksums accept exact candidate',
                   'status': 'pass'})
    if check_committed:
        for filename, data in ((FILENAME, candidate), ('app_main.display_marker.bin', patched)):
            path = 'build/display-marker/' + filename
            assert subprocess.check_output(['git', 'show', 'HEAD:' + path], cwd=ROOT) == data
        committed = json.loads(subprocess.check_output(
            ['git', 'show', 'HEAD:build/display-marker/build-report.json'], cwd=ROOT))
        assert committed == build
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    return {'status': 'pass', 'input_sha256': ORIGINAL_SHA256,
        'candidate_sha256': sha256(candidate), 'patched_app_sha256': sha256(patched),
        'checked_against_git_head': check_committed, 'hardware_access': False,
        'checks': checks, 'container_verification': container,
        'replacement_instruction': [i.mnemonic + ' ' + i.op_str for i in decoder.disasm(AFTER, RUNTIME)],
        'limits': ['Final segment delivery to the physical panel is stubbed at main runtime 0x0100d134',
                   'Normal-renderer parameter/modal/RTOS boundaries are explicitly modeled',
                   'No physical flashing, display, boot, audio or recovery result for this marker image',
                   'Normal menus/values are masked; raw segment writes can bypass this character routine']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, default=ROOT / 'build/display-marker')
    parser.add_argument('--check-committed', action='store_true')
    args = parser.parse_args()
    report = verify((ROOT / 'inputs/MX1_UPD.original.bin').read_bytes(),
        (args.build / FILENAME).read_bytes(),
        (args.build / 'app_main.display_marker.bin').read_bytes(),
        json.loads((args.build / 'build-report.json').read_text()),
        check_committed=args.check_committed)
    (args.build / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'candidate_sha256': report['candidate_sha256'],
        'checked_against_git_head': report['checked_against_git_head'],
        'checks': [c['name'] for c in report['checks']]}, indent=2))


if __name__ == '__main__':
    main()
