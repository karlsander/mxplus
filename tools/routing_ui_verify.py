#!/usr/bin/env python3
"""Exercise MX-1 original panel instructions and the compiled routing gesture.

The panel event decoder, event queue, key-state update, tempo renderer, and
four-character text loop run as original ARM instructions. Higher-level key
actions, modal actions, parameter storage, and final character/LED delivery are
stubbed. Panel-isolation cases capture routing API calls; final-candidate cases
also execute the real route state/label APIs with parameter and RTOS boundaries.
Audio correctness has independent tests. The verifier consumes the sole mainline build.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys

from elftools.elf.elffile import ELFFile
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
    UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
    UC_ARM_REG_LR, UC_ARM_REG_PC)

from container_tool import (ORIGINAL_SHA256, COMPONENT_BY_NAME,
                            component_unpacked, sha256)
from arm_machine import Machine

ROOT = Path(__file__).resolve().parents[1]
KEYS = 0x605129A4
PAGE = 0x600B4B5E
BOOT = 0x600B4B94
MODAL = 0x600B53A4
CONTEXT = 0x605141CC
PACKET = 0x20017000
LABEL = 0x20018000
REGS = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
        UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


def signed(value):
    return value - 0x100000000 if value & 0x80000000 else value


class UIMachine(Machine):
    def __init__(self, image, symbols=None, execute_tempo=False, *,
                 stub_routes=True, mixer_mode=0, dsp_mode=0):
        super().__init__(image)
        from routing_mpu_verify import protect_code
        protect_code(self)
        self.symbols = {k: v & ~1 for k, v in (symbols or {}).items()}
        self.execute_tempo = execute_tempo
        self.stub_routes = stub_routes
        self.system_values = {0x19: mixer_mode, 0x1a: 1234}
        self.queued = []
        self.key_actions = []
        self.encoders = []
        self.adjustments = []
        self.parameters = []
        self.characters = []
        self.original_events = []
        self.labels = []
        self.busy_queries = []
        self.system_reads = []
        self.event_posts = []
        self.write(KEYS, bytes(16))
        self.write(0x600B4B30, bytes(0x70))
        self.write(PAGE, struct.pack('<H', 15 if mixer_mode == 1 else 5))
        self.write(0x600B4B40, b'\xff\xff\xff\xff')
        self.write(0x60512E34, b'\xff' * 0x100)
        self.write(MODAL, u32(0))
        self.write(0x6051deb8, u32(dsp_mode))
        self.write(LABEL, b'A6  \0')
        self.uc.hook_add(UC_HOOK_CODE, self.instruction)

    def ret(self, result=0):
        self.uc.reg_write(UC_ARM_REG_R0, result & 0xffffffff)
        self.uc.reg_write(UC_ARM_REG_PC, self.uc.reg_read(UC_ARM_REG_LR))

    def instruction(self, uc, address, size, user):
        args = tuple(uc.reg_read(r) for r in
                     (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x60010B48:
            self.original_events.append(self.read(args[0], 4).hex())
        elif address == 0x60018258:
            self.busy_queries.append(args[0])
        elif address == 0x60010580:
            self.queued.append(self.read(args[0], 6).hex())
        elif address in (0x60010516, 0x60010538):
            self.key_actions.append((address, args[0]))
            self.ret()
        elif address == 0x600109D8 and not self.execute_tempo:
            self.encoders.append((args[0], signed(args[1])))
            self.ret()
        elif address in (0x6001823A, 0x6000FBA6, 0x6000FC06, 0x6000FF1C,
                         0x60009C2C):
            self.ret()
        elif address == 0x6001A1CE:
            self.ret({0: 0, 0x5a: 0, 0x5b: 1234}.get(args[1], 0))
        elif address == 0x6001e65e:
            self.ret(-1 if args[1] == 0xfb else 0)
        elif address == 0x6001F7C8:
            self.ret(-1)
        elif address == 0x6001A896:
            self.system_reads.append(args[:3])
            self.ret(self.system_values.get(args[1], 0))
        elif address in (0x600160EC, 0x600161F6):
            self.parameters.append((address, *args))
            self.ret(1)
        elif address == 0x0100280A:
            # Execute the original four-character loop, stop before font/LED I/O.
            self.characters.append((args[1], args[2], args[3] & 0xff))
            self.ret()
        elif address == self.symbols.get('mx1_route_adjust'):
            self.adjustments.append((args[0], signed(args[1])))
            if self.stub_routes:
                self.ret()
        elif address == self.symbols.get('mx1_route_label'):
            self.labels.append(args[0])
            if self.stub_routes:
                self.ret(LABEL)
        elif address == 0x0100e266:
            # Observe the original task-post boundary without a modeled RTOS.
            self.event_posts.append(args[:2])
            self.ret()

    def checked(self, address, *args):
        expected = [0x34440000 + i * 0x123 for i in range(len(REGS))]
        for reg, value in zip(REGS, expected):
            self.uc.reg_write(reg, value)
        result = self.call(address, *args, measure=True)
        assert [self.uc.reg_read(r) for r in REGS] == expected, 'AAPCS registers changed'
        return result

    def packet(self, kind, control, value=0, patched=False):
        self.write(PACKET, struct.pack('<BBh', kind, control, value))
        entry = self.symbols['mx1_route_ui_event'] if patched else 0x60010B48
        return self.checked(entry, PACKET)

    def held(self, *keys):
        state = bytearray(16)
        for key in keys:
            state[key >> 3] |= 1 << (key & 7)
        self.write(KEYS, state)


class StartupPageMachine(UIMachine):
    """Original startup page decision/request and page-state transition.

    Parameter storage, preset loading, audio/USB start, page object lifecycle,
    redraw scheduling and final startup cleanup are stubbed. Boot-mode lookup,
    held-key queries, branch decisions, request write and page-state stores run.
    """
    STUBS = (0x600164a8, 0x6001ab54, 0x6001e786, 0x6001fb4c,
             0x60018040, 0x6001a204, 0x6001a2fc, 0x600099e0,
             0x6000f3e0, 0x6000a3f8, 0x60017e60, 0x6000fb86,
             0x6000fb5c, 0x600104a8, 0x6000fcd4, 0x6000fc4e)

    def instruction(self, uc, address, size, user):
        if address in self.STUBS:
            self.ret()
        elif address == 0x6001e65e:
            self.ret(-1)  # No selected channel restored from a preset.
        else:
            super().instruction(uc, address, size, user)

    def startup_page(self):
        self.write(PAGE, bytes(2))  # Initial splash/startup page, not main UI.
        self.checked(0x6005693c)
        requested = struct.unpack('<h', self.read(PAGE - 2, 2))[0]
        self.checked(0x6000fd98, requested)
        assert struct.unpack('<h', self.read(PAGE, 2))[0] == requested
        self.parameters.clear()
        return requested


def verify(original: bytes, patched: bytes, build: dict) -> dict:
    """Verify the exact supplied candidate; compilation belongs only to CLI.

    The main routing verifier imports this entry point after building its final
    main component. No fixture is compiled, substituted, or inferred here.
    """
    groups = []
    symbols = build['symbols']

    def passed(name, **details):
        groups.append(dict(name=name, status='pass', **details))

    # These callbacks execute the original physical decoder, queue, dispatcher,
    # and key-state update. The final UI action is the stub boundary.
    stock = UIMachine(original)
    for strip in range(11):
        key = strip + 0x29
        stock.packet(2, key)
        assert stock.read(KEYS + (key >> 3), 1)[0] & (1 << (key & 7))
        assert stock.key_actions[-1] == (0x60010516, key)
        stock.packet(1, key)
        assert not (stock.read(KEYS + (key >> 3), 1)[0] & (1 << (key & 7)))
        assert stock.key_actions[-1] == (0x60010538, key)
    for encoder in (0, 1):
        for delta in (-32768, -1, 0, 1, 32767):
            stock.packet(4, encoder, delta)
            assert stock.encoders[-1] == (encoder, delta)
    passed('Original physical decoder, queue and logical key/encoder dispatch',
           key_press_type=2, key_release_type=1, encoder_move_type=4,
           select_ids=list(range(0x29, 0x34)), cases=32)

    tempo = UIMachine(original, execute_tempo=True)
    tempo.checked(0x600109d8, 1, 2)
    assert any(a[0] == 0x600160ec and a[2:] == (0x1a, 2, 10)
               for a in tempo.parameters), tempo.parameters
    tempo.parameters.clear()
    tempo.checked(0x600109d8, 0, 2)
    assert not any(a[0] == 0x600160ec and a[2] == 0x1a for a in tempo.parameters)
    passed('Original encoder1 reaches tempo parameter 0x1a; encoder0 does not',
           clock_mode='internal', parameter_store='stubbed; calls observed')

    # Independent callback-register and renderer-prologue guards.
    assert original[0xf5d8:0xf5dc] == u32(0x60010b49)
    assert patched[0xf5d8:0xf5dc] == u32(symbols.get('mx1_sources_ui_event', symbols['mx1_route_ui_event']) | 1)
    assert original[0x13356:0x13360] == bytes.fromhex('feb50446c54804f07cff')
    assert patched[0x13356:0x1335c] == bytes.fromhex('00bfdff800f0')
    assert patched[0x1335c:0x13360] == u32(symbols.get('mx1_sources_ui_tempo', symbols['mx1_route_ui_display']) | 1)
    passed('Registered callback and aligned renderer hook bytes match symbols')

    # Derive live page state through original startup instructions, rather
    # than assuming the zero written by early panel initialization is permanent.
    startup_cases = []
    for mode, expected_page in ((0, 5), (1, 15), (2, 5)):
        machine = StartupPageMachine(patched, symbols, mixer_mode=mode)
        assert machine.startup_page() == expected_page
        machine.packet(2, 0x2d, patched=True)
        assert machine.labels == [4], ('Startup-selected page rejected', mode, expected_page)
        machine.packet(4, 1, 1, patched=True)
        assert machine.adjustments == [(4, 1)]
        startup_cases.append({'system_mode': mode, 'page': expected_page})
    passed('Original startup page selection reaches routing gesture',
           cases=startup_cases, original_entry='0x6005693c',
           original_page_transition='0x6000fd98',
           stubbed=[hex(a) for a in StartupPageMachine.STUBS],
           parameters='Supplied system values; no selected preset channel')

    for page in range(33):
        machine = UIMachine(patched, symbols)
        machine.write(PAGE, struct.pack('<H', page))
        machine.held(0x2d)
        machine.packet(4, 1, 1, patched=True)
        assert bool(machine.adjustments) == (page in (5, 15)), page
    alternate = StartupPageMachine(patched, symbols)
    alternate.system_values[0x74] = 1
    assert alternate.startup_page() == 12
    alternate.packet(2, 0x2d, patched=True)
    alternate.packet(4, 1, 1, patched=True)
    assert not alternate.labels and not alternate.adjustments
    passed('Only pages 5 and 15 admit routing; original alternate-page startup stays excluded',
           pages_tested=list(range(33)), alternate_parameter='0x74=1 selects page 12')

    comparisons = []
    for state in ('idle', 'other_page', 'other_boot', 'modal'):
        old, new = UIMachine(original), UIMachine(patched, symbols)
        for machine in (old, new):
            if state == 'other_page': machine.write(PAGE, b'\x01\0')
            if state == 'other_boot': machine.write(BOOT, u32(1))
            if state == 'modal': machine.write(MODAL, u32(1))
            machine.checked(0x60013356, CONTEXT)
        assert old.characters == new.characters, (state, old.characters, new.characters)
        assert not new.labels
        comparisons.append({'state': state, 'characters': new.characters})
    passed('Inactive original display is preserved through displaced-instruction trampoline',
           cases=comparisons)

    for strip in range(11):
        machine = UIMachine(patched, symbols)
        key = strip + 0x29
        machine.packet(2, key, patched=True)
        assert machine.key_actions == [(0x60010516, key)]
        assert machine.labels[-1] == strip
        assert machine.characters[-4:] == [(1, i, c) for i, c in enumerate(b'A6  ')]
        queued_before = len(machine.queued)
        machine.packet(4, 1, 32767, patched=True)
        machine.packet(4, 1, -32768, patched=True)
        machine.packet(4, 1, 0, patched=True)
        assert machine.adjustments == [(strip, 1), (strip, -1)]
        assert not machine.encoders
        assert len(machine.queued) == queued_before
        machine.characters.clear()
        machine.packet(1, key, patched=True)
        assert machine.key_actions[-1] == (0x60010538, key)
        assert machine.read(KEYS, 16) == bytes(16)
        stock = UIMachine(original)
        stock.checked(0x60013356, CONTEXT)
        assert machine.characters == stock.characters
        machine.packet(4, 1, 3, patched=True)
        assert machine.encoders[-1] == (1, 3)
        assert all(x == 0x605144cc for x in machine.busy_queries)
    passed('All 11 strips: press, +/-/zero route rotation, release restores display/tempo',
           source_delta='one signed step per nonzero physical event',
           routes='API calls captured; audio tested separately')

    for strip in range(11):
        stock, machine = UIMachine(original), UIMachine(patched, symbols)
        key = strip + 0x29
        for event in (2, 1):
            stock.packet(event, key)
            machine.packet(event, key, patched=True)
        assert machine.key_actions == stock.key_actions
        # Key records initialize only the type and key fields. Do not require
        # unused stack bytes in their encoder-delta union to be identical.
        def key_records(records):
            return [(raw[0], int.from_bytes(raw[2:4], 'little'))
                    for raw in map(bytes.fromhex, records)]
        assert key_records(machine.queued) == key_records(stock.queued)
        assert machine.original_events == stock.original_events
        assert not machine.adjustments
        assert machine.read(KEYS, 16) == stock.read(KEYS, 16) == bytes(16)
        stock.checked(0x60013356, CONTEXT)
        assert machine.characters[-len(stock.characters):] == stock.characters
    passed('Plain SELECT taps preserve original press/release and never adjust a route',
           strips=11, high_level_select_actions='original calls observed; bodies stubbed')

    tempo = UIMachine(patched, symbols, execute_tempo=True)
    tempo.packet(4, 1, -3, patched=True)
    assert any(a[0] == 0x600160ec and a[2:] == (0x1a, 0xfffffffd, 10)
               for a in tempo.parameters), tempo.parameters
    assert not tempo.adjustments
    passed('Unheld TEMPO runs original decoded event through parameter adjustment',
           delta=-3, tempo_parameter=0x1a)

    blocked = []
    for name, keys, page, boot, modal in (
        ('no_select', [], 5, 0, 0),
        ('two_selects', [0x29, 0x2a], 5, 0, 0),
        ('modifier', [0x30, 0x11], 5, 0, 0),
        ('other_page', [0x30], 1, 0, 0),
        ('startup_page', [0x30], 0, 0, 0),
        ('alternate_page', [0x30], 12, 0, 0),
        ('other_boot', [0x30], 5, 1, 0),
        ('modal', [0x30], 5, 0, 1),
    ):
        machine = UIMachine(patched, symbols)
        machine.held(*keys)
        machine.write(PAGE, struct.pack('<H', page))
        machine.write(BOOT, u32(boot))
        machine.write(MODAL, u32(modal))
        machine.packet(4, 1, 2, patched=True)
        assert not machine.adjustments
        assert machine.original_events[-1] == '04010200'
        assert machine.encoders == [(1, 2)]
        blocked.append(name)
    passed('Existing modified gestures, modes and unheld tempo events pass unchanged',
           cases=blocked)

    # Each SELECT against every other physical key catches off-by-one and byte
    # boundary mistakes in the recovered key bitset, including all SELECT pairs.
    machine = UIMachine(patched, symbols)
    cases = 0
    for select in range(0x29, 0x34):
        for other in range(0x55):
            if other == select:
                continue
            machine.held(select, other)
            machine.packet(4, 1, 1, patched=True)
            assert not machine.adjustments
            assert machine.encoders[-1] == (1, 1)
            cases += 1
    passed('Every SELECT plus any second physical key disables route editing',
           physical_key_ids=[0, 0x54], ordered_pairs=cases)

    machine = UIMachine(patched, symbols)
    machine.packet(2, 0x29, patched=True)
    machine.characters.clear()
    machine.packet(2, 0x33, patched=True)
    stock = UIMachine(original)
    stock.checked(0x60013356, CONTEXT)
    assert machine.characters == stock.characters
    machine.packet(1, 0x29, patched=True)
    assert machine.labels[-1] == 10
    machine.packet(4, 1, 1, patched=True)
    assert machine.adjustments == [(10, 1)]
    machine.characters.clear()
    machine.packet(1, 0x33, patched=True)
    assert machine.characters == stock.characters
    assert machine.read(KEYS, 16) == bytes(16)
    passed('Overlapping SELECT presses suspend editing; remaining held SELECT resumes it',
           first_strip=0, second_strip=10)

    # A SELECT event on a menu must never force a main-page tempo redraw.
    machine = UIMachine(patched, symbols)
    machine.write(PAGE, b'\x01\0')
    machine.packet(2, 0x30, patched=True)
    machine.packet(1, 0x30, patched=True)
    assert not machine.characters and not machine.labels and not machine.adjustments
    assert machine.key_actions == [(0x60010516, 0x30), (0x60010538, 0x30)]
    passed('SELECT press/release on another page never overwrites its display')

    # VALUE encoder is untouched even while one destination SELECT is held.
    machine = UIMachine(patched, symbols)
    machine.held(0x30)
    machine.packet(4, 0, -4, patched=True)
    assert machine.encoders == [(0, -4)] and not machine.adjustments
    passed('VALUE encoder remains original while SELECT is held')

    if not build.get('test_fixture'):
        # These cases run the actual compiled label/get/adjust functions from
        # the supplied final candidate. Only parameter storage and RTOS event
        # posting are stubs; no route function is replaced by a return value.
        assert 'mx1_route_state' in symbols, 'Final candidate lacks route state symbol'
        state_address = symbols['mx1_route_state']
        for mode in (0, 1):
            for strip in range(11):
                machine = UIMachine(patched, symbols, execute_tempo=True,
                                    stub_routes=False, mixer_mode=mode)
                assert machine.read(state_address, 11) == bytes(11)
                key = strip + 0x29
                machine.packet(2, key, patched=True)
                assert machine.characters[-4:] == [
                    (1, i, c) for i, c in enumerate(b'Auto')]
                machine.packet(4, 1, 1, patched=True)
                assert machine.checked(symbols['mx1_route_get'], strip)[0] == 1
                assert machine.read(state_address, 11) == bytes(
                    1 if index == strip else 0 for index in range(11))
                assert machine.characters[-4:] == [
                    (1, i, c) for i, c in enumerate(b'An1 ')]
                machine.packet(4, 1, -1, patched=True)
                assert machine.read(state_address, 11) == bytes(11)
                assert machine.event_posts == [(0x6051dea8, 8)] * 2
                assert not machine.parameters, 'Held TEMPO reached original parameter adjustment'
                assert all(a == (0x600b5390, 0x19, 0)
                           for a in machine.system_reads if a[1] == 0x19)
        passed('Final UI and real route APIs change only the selected state and post DSP event 8',
               mixer_modes=[0, 1], strips_per_mode=11,
               boundaries=['Original parameter getter returns supplied mode',
                           'Original RTOS event-post call is recorded, not scheduled'],
               audio_execution='The DSP task is not run by this UI case')

        for name, mode, dsp_mode in (('external_mixer', 2, 0), ('diagnostic_program', 0, 4)):
            for strip in range(11):
                machine = UIMachine(patched, symbols, execute_tempo=True,
                                    stub_routes=False, mixer_mode=mode, dsp_mode=dsp_mode)
                desired = bytes([7] * 11)  # Existing An6 assignments must survive.
                machine.write(state_address, desired)
                machine.write(0x604f41e0, b"MXR1" + desired + b"\0")
                key = strip + 0x29
                machine.packet(2, key, patched=True)
                assert machine.characters[-4:] == [
                    (1, i, c) for i, c in enumerate(b'modE')]
                for delta in (32767, -32768, 0):
                    machine.packet(4, 1, delta, patched=True)
                assert machine.read(state_address, 11) == desired
                assert machine.checked(symbols['mx1_route_get'], strip)[0] == 7
                assert not machine.event_posts and not machine.parameters
                assert machine.characters[-4:] == [
                    (1, i, c) for i, c in enumerate(b'modE')]
                machine.characters.clear()
                machine.packet(1, key, patched=True)
                stock = UIMachine(original, execute_tempo=True, mixer_mode=mode)
                stock.checked(0x60013356, CONTEXT)
                assert machine.characters == stock.characters
                machine.packet(4, 1, 2, patched=True)
                stock.packet(4, 1, 2)
                assert machine.parameters == stock.parameters and machine.parameters
                assert machine.read(state_address, 11) == desired
                assert not machine.event_posts
        passed('Real mode guards show modE, preserve routes/tempo during hold, and restore tempo on release',
               cases=['external_mixer mode 2', 'diagnostic DSP program greater than 3'],
               strips_per_case=11, route_api_stubs=False,
               boundaries=['Original parameter getter returns supplied mode',
                           'DSP task mode is supplied memory state',
                           'Final parameter setter and character delivery are observed'])
    passed('All tested compiled/original callbacks preserve r4-r11, SP and return control')
    return {
        'status': 'OFFLINE UI INSTRUCTION TESTS; NO PHYSICAL PANEL OR AUDIO CLAIM',
        'original_app_sha256': sha256(original),
        'patched_app_sha256': sha256(patched),
        'ui_only_fixture': bool(build.get('test_fixture')),
        'symbols': symbols,
        'sources': {str(p.relative_to(ROOT)): sha256(p.read_bytes()) for p in (
            ROOT / 'patches/channel_routing_ui.c',
            ROOT / 'patches/channel_routing_ui.S',
            Path(__file__).resolve())},
        'groups': groups,
        'limits': [
            'Route APIs are stubbed in panel-isolation cases and execute unchanged in the final-candidate state/mode cases; DSP audio is not validated here',
            'Original parameter reads and RTOS event posts are explicit boundaries in UI/API integration cases',
            'Final LED delivery and physical button-to-event wiring are not emulated',
            'Modal actions and higher-level SELECT behavior are stubbed; their original calls are preserved',
            'Instruction counts are not CPU cycle or deadline measurements',
        ],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware', type=Path)
    p.add_argument('--build', type=Path, default=ROOT / 'build/mainline')
    p.add_argument('--output', type=Path,
                   default=ROOT / 'analysis/channel_routing_ui_verification.json')
    a = p.parse_args()
    raw = a.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256, 'input firmware hash mismatch'
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((a.build / 'build-report.json').read_text())
    patched = (a.build / 'app_main.mainline.bin').read_bytes()
    assert sha256(patched) == build['patched_app_sha256']
    report = verify(original, patched, build)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'ui_only_fixture': False,
                      'groups_passed': len(report['groups']),
                      'extension_bytes': build.get('extension_bytes',
                          build.get('scatter_extension', {}).get('insert_length'))}, indent=2))


if __name__ == '__main__':
    main()
