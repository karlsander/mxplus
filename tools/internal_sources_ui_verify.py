#!/usr/bin/env python3
"""Execute compiled BD UI and original panel instructions, with named boundaries.

Original packet decoding, queueing, held-key updates, renderer trampolines, font
loop and LED dispatch execute unchanged. Parameter storage, final page actions
and final hardware delivery are modeled. Broad gesture tests model the BD API;
final-candidate integration groups execute its actual compiled state and clock
APIs. Only the maintained mainline candidate is tested.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from internal_sources_ui_patch import UI_HOOKS, patch_ui
from routing_ui_verify import UIMachine, KEYS, PAGE, BOOT, MODAL, CONTEXT, PACKET, u32, signed

ROOT = Path(__file__).resolve().parents[1]
CORE_APIS = ('mx1_bd_step_get', 'mx1_bd_step_toggle', 'mx1_bd_step_adjust',
             'mx1_bd_current_step', 'mx1_route_get')


class SourceUIMachine(UIMachine):
    def __init__(self, image, symbols=None, *, extension=None, selected=7, focus=1, editing=True, real_select=False):
        self.real_select = real_select
        self.selected_bits = 1 << selected if 0 <= selected < 11 else 0
        self.select_leds = []
        self.selected = selected
        self.focus = focus
        self.routes = [0] * 11
        if 0 <= selected < 11:
            self.routes[selected] = 54
        self.steps = [[53 << 16 for _ in range(16)] for _ in range(11)]
        self.bd_calls = []
        self.native_actions = []
        self.rgb = []
        self.led_hardware = []
        self.palette_calls = []
        self.segment_hardware = []
        self.current_step = -1
        self.mix_reads = []
        self.ui_reads = []
        self.original_mask = 0
        super().__init__(image, symbols, stub_routes=True)
        if extension:
            self.write(extension[0], extension[1])
        if editing and symbols and focus <= 5 and 0 <= selected < 11:
            self.packet(2, 0x29 + selected)
            self.packet(1, 0x29 + selected)
            if focus <= 5: assert self.checked(symbols['mx1_sources_ui_edit_target'])[0] == selected
            self.native_actions.clear()
            self.characters.clear()
            self.labels.clear()
            self.bd_calls.clear()

    def instruction(self, uc, address, size, user):
        args = tuple(uc.reg_read(r) for r in
                     (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address in (0x60010516, 0x60010538):
            # Execute these original entry instructions or their actual hooks;
            # the inherited route-only harness stubs them too early for BD.
            return
        if address in (0x6001099c, 0x600109a6):
            # Final stock page dispatch, after the retained wrapper stored key.
            key = int.from_bytes(self.read(args[0] + 2, 2), 'little')
            self.native_actions.append((address, key))
            if 0x29 <= key <= 0x33:
                if self.real_select:
                    uc.reg_write(UC_ARM_REG_R0, 0x60514348)
                    uc.reg_write(UC_ARM_REG_R1, key)
                    uc.reg_write(UC_ARM_REG_R2, int(address == 0x6001099c))
                    uc.reg_write(UC_ARM_REG_PC, 0x60016533)
                    return
                if address == 0x600109a6 and key - 0x29 == self.selected:
                    self.selected = -1
                    self.selected_bits = 0
            self.ret(1)
        elif address == 0x6001a1ce:
            self.ui_reads.append(args[:3])
            self.ret({0: self.focus, 0x5a: 0, 0x5b: 1234, 0x5d: 0}.get(args[1], 0))
        elif address == 0x6001e65e:
            self.mix_reads.append(args[:3])
            values = {0xfb: self.selected, 0xe2: 64, 0xf9: 0}
            if 0x7e <= args[1] < 0x89:
                values[args[1]] = self.original_mask
            self.ret(((self.selected_bits >> args[1]) & 1) if args[1] < 11 else values.get(args[1], 0))
        elif address in (0x6001e694, 0x600161f6):
            if args[1] == 0xfb: self.selected = signed(args[2])
            elif args[1] < 11:
                self.selected_bits = ((self.selected_bits & ~(1 << args[1])) |
                                      (bool(args[2]) << args[1]))
            self.ret(1)
        elif address == 0x60014a78:
            self.select_leds.append(args[:3])
        elif address == self.symbols.get('mx1_route_get'):
            self.ret(self.routes[args[0]] if args[0] < 11 else 0)
        elif address == self.symbols.get('mx1_bd_step_get'):
            self.bd_calls.append(('get', args[0], args[1]))
            self.ret(self.steps[args[0]][args[1]])
        elif address == self.symbols.get('mx1_bd_step_toggle'):
            self.bd_calls.append(('toggle', args[0], args[1]))
            self.steps[args[0]][args[1]] ^= 1
            self.ret()
        elif address == self.symbols.get('mx1_bd_step_adjust'):
            self.bd_calls.append(('adjust', args[0], args[1], args[2], signed(args[3])))
            # State-value model is only to check formatting/correct step binding.
            value = self.steps[args[0]][args[1]]
            pitch = (value >> 8) & 255
            pitch = pitch - 256 if pitch & 128 else pitch
            decay = (value >> 16) & 255
            if args[2] == 0:
                pitch = max(-24, min(24, pitch + signed(args[3])))
            else:
                decay = max(0, min(100, decay + signed(args[3])))
            self.steps[args[0]][args[1]] = (value & 1) | ((pitch & 255) << 8) | (decay << 16)
            self.ret()
        elif address == self.symbols.get('mx1_bd_current_step'):
            self.ret(self.current_step)
        elif address == 0x0100280a:
            # Run the original character-to-segment font lookup as well as the
            # outer three/four-character loops. Only final delivery is stubbed.
            self.characters.append((args[1], args[2], args[3] & 0xff))
        elif address == 0x0100d134:
            self.segment_hardware.append(args)
            self.ret()
        elif address == 0x60014a8e:
            # Execute stock raw LED wrapper and SRAM dispatcher through final sink.
            self.rgb.append(args)
        elif address == 0x60014aa0:
            self.palette_calls.append(args[:2])
        elif address == 0x60002010:
            self.led_hardware.append(args)
            self.ret()
        else:
            super().instruction(uc, address, size, user)

    def packet(self, kind, control, value=0, patched=True):
        self.write(PACKET, struct.pack('<BBh', kind, control, value))
        entry = self.symbols['mx1_sources_ui_event'] if patched else 0x60010b48
        return self.checked(entry, PACKET)

    def taps(self, step):
        self.packet(2, step + 1)
        self.packet(1, step + 1)

    def display(self):
        self.characters.clear()
        self.checked(0x60013740, CONTEXT)
        self.checked(0x60013356, CONTEXT)
        return (''.join(chr(c) for d, _, c in self.characters if d == 0),
                ''.join(chr(c) for d, _, c in self.characters if d == 1))


class IntegratedSourceUIMachine(SourceUIMachine):
    """Run the real route/BD state APIs, retaining named device boundaries."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stub_routes = False

    def instruction(self, uc, address, size, user):
        if address in (self.symbols.get(name) for name in CORE_APIS):
            # The parent observes route adjustments and leaves them executing
            # when stub_routes is false; it does not intercept the BD APIs.
            UIMachine.instruction(self, uc, address, size, user)
        else:
            super().instruction(uc, address, size, user)


def verify(original: bytes, patched: bytes, build: dict, extension=None) -> dict:
    groups = []
    symbols = build['symbols']

    def passed(name, **details):
        groups.append(dict(name=name, status='pass', **details))

    def machine(**kwargs):
        return SourceUIMachine(patched, symbols, extension=extension, **kwargs)

    # Comparing all changed entry bytes verifies complete-instruction guards.
    expected = bytearray(original)
    changes = []
    patch_ui(expected, symbols, changes)
    for offset, old_hex, _, _ in UI_HOOKS:
        assert patched[offset:offset + len(bytes.fromhex(old_hex))] == \
               expected[offset:offset + len(bytes.fromhex(old_hex))]
    assert patched[0xf5d8:0xf5dc] == expected[0xf5d8:0xf5dc]
    passed('Exact original hook bytes and all final veneer targets match')

    # Run the original selection body, its actual held-key queries and the
    # compiled toggle; model only parameter storage and the page dispatch edge.
    for page in (5, 15):
        for strip in range(11):
            m = machine(selected=-1, editing=False, real_select=True)
            m.write(PAGE, struct.pack('<H', page))
            m.checked(0x600140c2, CONTEXT)
            assert len(m.palette_calls) == 16  # Startup gradient still exists.
            for editing in (False, True, False, True):
                m.packet(2, strip + 0x29)
                m.packet(1, strip + 0x29)
                assert m.selected == strip
                assert m.selected_bits == 1 << strip
                assert signed(m.checked(symbols['mx1_sources_ui_edit_target'])[0]) == (strip if editing else -1)
                m.select_leds.clear()
                m.checked(0x60014692, CONTEXT)
                states = {led: mode for led, mode, level in m.select_leds}
                assert states[0x34 + strip] == (3 if editing else 1)
                assert all(states[0x34 + i] == 0 for i in range(11) if i != strip)
            other = (strip + 1) % 11
            m.packet(2, other + 0x29)
            m.packet(1, other + 0x29)
            assert m.selected == other
            assert signed(m.checked(symbols['mx1_sources_ui_edit_target'])[0]) == -1
    passed('Original SELECT actions toggle steady normal / blinking source edit on both mixer pages',
           strips=11, pages=[5,15], startup_gradient_retained=True,
           original_select='0x60016532, held-key helpers execute unchanged',
           parameter_get_set='Modeled; final physical LED delivery recorded')

    for strip, link_id in ((0, 3), (2, 4)):
        m = machine(selected=strip, editing=False, real_select=True)
        m.system_values[link_id] = 1
        m.selected_bits = 3 << strip
        m.packet(2, strip + 0x29)
        m.packet(1, strip + 0x29)
        assert m.selected == strip and m.selected_bits == 3 << strip
        m.select_leds.clear()
        m.checked(0x60014692, CONTEXT)
        states = {led: mode for led, mode, level in m.select_leds}
        assert states[0x34 + strip] == 3 and states[0x35 + strip] == 0
    m = machine(selected=7, editing=False, real_select=True)
    m.packet(2, 0x30)
    m.packet(2, 0x11)  # Channel-setting modifier cancels ordinary-toggle arming.
    m.packet(1, 0x30)
    assert signed(m.checked(symbols['mx1_sources_ui_edit_target'])[0]) == -1
    passed('Original linked-pair selection and hidden right SELECT LED survive source editing; modifiers cancel toggle')

    # Execute the real stock step renderer, exposing the precise recovered mode.
    stock = SourceUIMachine(original, selected=-1)
    stock.checked(0x600140c2, CONTEXT)
    gradient = list(stock.palette_calls)
    assert len(gradient) == 16
    assert set(color for _, color in gradient) == {1, 2, 3, 4}
    stock = SourceUIMachine(original, selected=7)
    stock.checked(0x600140c2, CONTEXT)
    assert len(stock.palette_calls) == 16
    assert set(color for _, color in stock.palette_calls) == {11, 40}
    passed('Original gradient requires no current channel; selected channel renders BFX mask',
           gradient_current_channel=-1, selected_current_channel=7,
           interpretation='BD view uses selected BD channel with CHANNEL SETTING BFX unfocused')

    # Positive pitch must not use '+': that glyph is identical to '-' in the
    # stock seven-segment font. Verify the actual lookup and final segment data.
    font = int.from_bytes(stock.read(0x01002a9c, 4), 'little')
    assert font == 0x0100ecd4
    assert stock.read(font, 2) == b'\x03\x04'
    assert stock.read(font + 2 + ord('+'), 1) == stock.read(font + 2 + ord('-'), 1) == b'\x40'
    assert stock.read(font + 2 + ord(' '), 1) == b'\0'
    passed('Original display widths and font require a blank positive pitch sign',
           font_table='SRAM 0x0100ecd4', plus_and_minus_segments=64,
           positive=' 12', negative='-12')

    tested = 0
    for strip in range(11):
        for step in range(16):
            m = machine(selected=strip)
            m.packet(2, step + 1)
            assert m.read(KEYS + ((step + 1) >> 3), 1)[0] & (1 << ((step + 1) & 7))
            assert not [c for c in m.bd_calls if c[0] == 'toggle']
            m.packet(1, step + 1)
            assert [c for c in m.bd_calls if c[0] == 'toggle'] == [('toggle', strip, step)]
            assert not m.native_actions
            assert m.read(KEYS, 16) == bytes(16)
            assert m.steps[strip][step] & 1
            assert sum(value & 1 for row in m.steps for value in row) == 1
            tested += 1
    for focus in (0, 1, 2, 3, 5):
        m = machine(focus=focus)
        m.taps(15)
        assert [c for c in m.bd_calls if c[0] == 'toggle'] == [('toggle', 7, 15)]
    passed('All 16 pads on all 11 strips toggle only on release; all five channel focuses permit BD',
           address_cases=tested, channel_focuses=[0, 1, 2, 3, 5])

    for strip in range(11):
        for step in (0, 7, 8, 15):
            m = machine(selected=strip)
            m.packet(2, step + 1)
            assert m.display() == (' 00', 'd053')
            m.packet(4, 0, -32768)
            m.packet(4, 1, 32767)
            m.packet(4, 1, 0)
            assert m.display() == ('-01', 'd054')
            m.packet(1, step + 1)
            assert [c for c in m.bd_calls if c[0] == 'adjust'] == [
                ('adjust', strip, step, 0, -1), ('adjust', strip, step, 1, 1)]
            assert not [c for c in m.bd_calls if c[0] == 'toggle']
            assert not m.encoders and not m.adjustments and not m.native_actions
            m.packet(4, 0, -2)
            m.packet(4, 1, 3)
            assert m.encoders == [(0, -2)] and m.adjustments == [(strip, 1)]
    passed('Held-note encoders bind pitch/decay to that step, normalize deltas, suppress taps and restore',
           cases=44, encoder_zero='consumed without edit or toggle suppression')

    m = machine()
    m.packet(2, 1)
    m.packet(4, 0, 0)
    m.packet(1, 1)
    assert [c for c in m.bd_calls if c[0] == 'toggle'] == [('toggle', 7, 0)]
    passed('Zero encoder movement does not convert an ordinary tap into an edit')

    for pitch, decay in ((-24, 0), (0, 53), (24, 100)):
        m = machine()
        m.steps[7][15] = ((pitch & 255) << 8) | (decay << 16)
        m.packet(2, 16)
        assert m.display() == (f'{pitch: 03d}', f'd{decay:03d}')
        sign = [call for call in m.segment_hardware if call[0:2] == (0, 0)][-1]
        assert sign[2] == (0x40 if pitch < 0 else 0)
    passed('Pitch signed semitone and decay displays format all parameter limits',
           value_characters=3, tempo_characters=4)

    for change in ('channel', 'source', 'bfx_focus', 'page', 'modal', 'external', 'diagnostic'):
        m = machine()
        m.packet(2, 5)
        if change == 'channel': m.selected = 6; m.routes[6] = 54
        elif change == 'source': m.routes[7] = 0
        elif change == 'bfx_focus': m.focus = 4
        elif change == 'page': m.write(PAGE, b'\x01\0')
        elif change == 'modal': m.write(MODAL, u32(1))
        elif change == 'external': m.system_values[0x19] = 2
        elif change == 'diagnostic': m.write(0x6051deb8, u32(4))
        m.packet(1, 5)
        assert not [c for c in m.bd_calls if c[0] == 'toggle']
        assert not m.native_actions, (change, m.native_actions)
        assert m.read(KEYS, 16) == bytes(16)
    passed('Captured release stays owned and cannot toggle a different channel after context changes',
           cases=7)

    for first, second in ((1, 2), (1, 16), (8, 9), (16, 1)):
        m = machine()
        m.packet(2, first)
        m.packet(2, second)
        m.packet(4, 0, -1)
        m.packet(4, 1, 1)
        m.packet(1, first)
        m.packet(1, second)
        assert not [c for c in m.bd_calls if c[0] in ('adjust', 'toggle')]
        assert not m.native_actions and not m.encoders
    passed('Overlapping pad holds cancel taps and consume ambiguous encoders without touching BFX/PAN/TEMPO')

    for modifier in (0x11, 0x15, 0x29, 0x30, 0x4a, 0x4e, 0x4f):
        m = machine()
        m.packet(2, 8)
        m.packet(2, modifier)
        m.packet(1, modifier)
        m.packet(1, 8)
        assert not [c for c in m.bd_calls if c[0] == 'toggle']
        assert m.native_actions == [(0x6001099c, modifier), (0x600109a6, modifier)]
    passed('Modifier or SELECT arriving during a held pad cancels its tap and preserves other actions',
           cases=7)

    for focus in (4, 6, 7, 10, 13):
        m = machine(focus=focus)
        m.taps(3)
        assert m.native_actions == [(0x6001099c, 4), (0x600109a6, 4)]
        assert not m.bd_calls
    for kind in ('not_bd', 'unselected', 'other_page', 'boot', 'modal', 'external', 'diagnostic'):
        m = machine()
        if kind == 'not_bd': m.routes[7] = 53
        elif kind == 'unselected': m.selected = -1
        elif kind == 'other_page': m.write(PAGE, b'\x01\0')
        elif kind == 'boot': m.write(BOOT, u32(1))
        elif kind == 'modal': m.write(MODAL, u32(1))
        elif kind == 'external': m.system_values[0x19] = 2
        elif kind == 'diagnostic': m.write(0x6051deb8, u32(4))
        m.taps(15)
        assert m.native_actions == [(0x6001099c, 16), (0x600109a6, 16)], kind
        assert not m.bd_calls, kind
    passed('BFX focus, scene/control modes, non-BD sources and blocked states retain stock step actions',
           cases=12)

    # A modifier held BEFORE a pad must keep the whole stock gesture, too.
    for key in range(0x55):
        if 1 <= key <= 16:
            continue
        m = machine()
        m.held(key)
        m.taps(0)
        assert not m.bd_calls
        assert m.native_actions == [(0x6001099c, 1), (0x600109a6, 1)]
    passed('Every other physical button held before a pad preserves the original gesture', cases=69)

    # SELECT+TEMPO still enters the old picker; VALUE remains its native path.
    for strip in range(11):
        m = machine(selected=strip)
        m.packet(2, 0x29 + strip)
        m.packet(4, 1, 1)
        m.packet(4, 0, -1)
        m.packet(1, 0x29 + strip)
        assert m.adjustments == [(strip, 1)] and m.encoders == [(0, -1)]
        assert not m.bd_calls
    passed('Existing SELECT plus TEMPO source picker and unmodified VALUE survive on every strip')

    m = machine()
    m.steps[7][0] |= 1
    m.steps[7][8] |= 1
    m.current_step = 4
    m.checked(0x600140c2, CONTEXT)
    assert len(m.rgb) == 16 and len(m.led_hardware) == 16
    assert m.rgb[0] == (0x19, 1, 9, 18)
    assert m.rgb[1] == (0x1a, 0, 0, 18)
    assert m.rgb[4] == (0x1d, 1, 9, 22)
    assert m.rgb[8] == (0x21, 1, 9, 18)
    assert not m.palette_calls
    m.packet(2, 1)
    m.rgb.clear()
    m.checked(0x600140c2, CONTEXT)
    assert m.rgb[0] == (0x19, 1, 9, 7)
    passed('All sixteen RGB calls distinguish enabled notes, playhead, held note and off pads',
           enabled_color=18, playhead_color=22, held_color=7,
           hardware_sink='stock dispatcher executes; final LED driver call recorded')

    comparisons = []
    for focus in (0, 1, 2, 3, 4, 5, 6, 7, 13):
        old, new = SourceUIMachine(original, selected=7, focus=focus), machine(focus=focus)
        new.routes[7] = 0
        for m in (old, new):
            m.checked(0x600140c2, CONTEXT)
        assert old.palette_calls == new.palette_calls, focus
        assert old.led_hardware == new.led_hardware, focus
        assert old.rgb == new.rgb
        comparisons.append(focus)
    passed('Inactive step-renderer trampoline preserves exact stock palette and LED-dispatch calls',
           channel_focuses=comparisons)

    # VALUE and TEMPO original renderers are not replaced by display stubs.
    for focus in (0, 1, 3, 5):
        old, new = SourceUIMachine(original, focus=focus), machine(focus=focus, editing=False)
        assert old.display() == new.display(), focus
    passed('Unheld VALUE and TEMPO retain original character output through both trampolines')

    if not build.get('ui_only_fixture'):
        initial = struct.pack('<I', 53 << 16) * (11 * 16)
        for strip in range(11):
            m = IntegratedSourceUIMachine(patched, symbols, selected=strip, editing=False)
            assert m.read(symbols['mx1_bd_steps'], len(initial)) == initial
            assert m.read(symbols['mx1_route_state'], 11) == bytes(11)
            m.packet(2, 0x29 + strip)
            while m.checked(symbols['mx1_route_get'], strip)[0] != 54:
                m.packet(4, 1, 1)
            assert m.display()[1] == 'BD  '
            m.packet(1, 0x29 + strip)
            assert m.read(symbols['mx1_route_state'] + strip, 1) == b'\x36'
            assert m.event_posts and all(p == (0x6051dea8, 8) for p in m.event_posts)
            m.taps(15)
            m.packet(2, 16)
            assert m.display() == (' 00', 'd053')
            m.packet(4, 0, -32768)
            m.packet(4, 1, 32767)
            assert m.display() == ('-01', 'd054')
            m.packet(1, 16)
            address = symbols['mx1_bd_steps'] + 4 * (strip * 16 + 15)
            expected = bytearray(initial)
            struct.pack_into('<I', expected, 4 * (strip * 16 + 15), 0x0036ff01)
            assert m.read(symbols['mx1_bd_steps'], len(initial)) == expected
            assert m.checked(symbols['mx1_bd_step_get'], strip, 15)[0] == 0x0036ff01
            # Persistent blinking view edits sources with no SELECT held.
            m.packet(4, 1, -1)
            assert m.display()[1] == 'NSE '
            assert m.read(KEYS, 16) == bytes(16)
            assert m.read(symbols['mx1_route_state'] + strip, 1) == b'\x35'
            m.taps(0)
            assert m.read(address, 4) == u32(0x0036ff01)
            assert m.read(symbols['mx1_bd_steps'], len(initial)) == expected
            assert m.native_actions[-2:] == [(0x6001099c, 1), (0x600109a6, 1)]
        passed('Final candidate physical picker, labels, held encoders and displays execute real route/BD state',
               strips=11, initialized_steps=176, core_api='compiled, no state API stubs',
               preserved='Every other step and strip remains byte-identical')

        m = IntegratedSourceUIMachine(patched, symbols)
        while m.checked(symbols['mx1_route_get'], 7)[0] != 54:
            m.checked(symbols['mx1_route_adjust'], 7, 1)
        assert m.checked(symbols['mx1_bd_current_step'])[0] == 0xffffffff
        m.write(0x600b4834, b'\x01')
        m.checked(symbols['mx1_internal_transport_reset'])
        for step in range(20):
            m.checked(symbols['mx1_internal_step'])
            assert m.checked(symbols['mx1_bd_current_step'])[0] == step % 16
        m.checked(0x600140c2, CONTEXT)
        assert len(m.rgb) == 16
        assert m.rgb[3] == (0x1c, 1, 9, 22)
        assert sum(call[1] for call in m.rgb) == 1
        m.write(0x600b4834, b'\x00')
        assert m.checked(symbols['mx1_bd_current_step'])[0] == 0xffffffff
        m.rgb.clear()
        m.checked(0x600140c2, CONTEXT)
        assert len(m.rgb) == 16 and not any(call[1] for call in m.rgb)
        passed('Final candidate sixteen-step clock publication feeds actual LED playhead and stopped display',
               step_publications=20, transport='Explicit supplied running byte; clock hook has separate checks')

    passed('All executed entries preserve r4-r11, SP and normal return control')

    return {'status': 'pass',
        'original_app_sha256': sha256(original), 'patched_app_sha256': sha256(patched),
        'ui_only_fixture': bool(build.get('ui_only_fixture')), 'groups': groups,
        'sources': {str(p.relative_to(ROOT)): sha256(p.read_bytes()) for p in (
            ROOT / 'patches/internal_sources_ui.c', ROOT / 'patches/internal_sources_ui.h',
            ROOT / 'patches/internal_sources_ui.S', ROOT / 'tools/internal_sources_ui_patch.py',
            Path(__file__).resolve())},
        'boundaries': ['Parameter storage returns explicit supplied values',
            'Gesture isolation models BD APIs; final-candidate integration executes compiled route/BD state APIs',
            'Core/audio/clock hooks have separate checks; supplied UI transport state is not a timing test',
            'Page dispatch modeled; selection cases execute original 0x60016532 and held-key helpers; parameter access modeled',
            'Original packet decoder, event queue and physical key bits execute unchanged',
            'Original font loop, segment lookup and LED dispatcher execute; final hardware calls are observed',
            'No physical scan wiring, LED appearance, MIDI/clock jitter or deadline margin measured']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', type=Path)
    parser.add_argument('--build', type=Path, default=ROOT / 'build/mainline')
    parser.add_argument('--output', type=Path, default=ROOT / 'analysis/internal-sources-ui-verification.json')
    args = parser.parse_args()
    raw = args.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((args.build / 'build-report.json').read_text())
    patched = (args.build / 'app_main.mainline.bin').read_bytes()
    assert sha256(patched) == build['patched_app_sha256']
    report = verify(original, patched, build)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups_passed': len(report['groups']),
                      'ui_only_fixture': False}, indent=2))


if __name__ == '__main__':
    main()
