#!/usr/bin/env python3
"""Execute the compiled generator callback through the original DSP IRQ path.

The USB pump is the original code. Its FIFO readiness, clock phase and converter
are deliberately supplied fixtures. This verifies integration and regression
boundaries; it does not model a physical USB peripheral or DSP sample clock.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import struct

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R4,
    UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R9,
    UC_ARM_REG_R10, UC_ARM_REG_R11, UC_ARM_REG_LR, UC_ARM_REG_PC)

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine
from internal_sources_audio_audit import CONTEXT, CALLBACK_SLOT, EXCHANGE, GENERATOR_COUNT

ROOT = Path(__file__).resolve().parents[1]
USBF = 0x40010000
MODE = 0x6051DEB8
PORTS = 0x40101100
REGS = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
        UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


class AudioMachine(Machine):
    def __init__(self, image, symbols=None, *, stub_render=False):
        super().__init__(image)
        from routing_mpu_verify import protect_code
        protect_code(self)
        self.uc.mem_map(0x40100000, 0x80000)
        self.symbols = symbols or {}
        self.stub_render = stub_render
        self.tick = 0
        self.pump_visits = 0
        self.render_calls = []
        self.call_order = []
        self.trace = []
        self.generator_writes = []
        self.out_reads = []
        self.serial = 0
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_READ, self._read)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)

    def _code(self, uc, address, size, user):
        if address == 0x01009840:
            self.pump_visits += 1
            self.call_order.append('original_pump')
        if address == (self.symbols.get('mx1_internal_render', 0) & ~1):
            self.call_order.append('compiled_renderer')
            self.render_calls.append((uc.reg_read(UC_ARM_REG_R0),
                                      uc.reg_read(UC_ARM_REG_R1)))
            if self.stub_render:
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _read(self, uc, access, address, size, value, user):
        if address == USBF + 0x1f4:
            # Distinct positive words exercise actual copying and packet-tail
            # bookkeeping. Their identity conversion is not an audio model.
            self.serial += 1
            fixture = 0x11000000 + (self.serial & 0xffff)
            uc.mem_write(address, u32(fixture))
            self.out_reads.append((self.tick, fixture))

    def _write(self, uc, access, address, size, value, user):
        if PORTS <= address < PORTS + GENERATOR_COUNT * 4:
            self.generator_writes.append((self.tick, address, size, value))
        elif 0x40000000 <= address < 0x40200000:
            self.trace.append((self.tick, address, size, value))
        # Retain the earlier stock-pump harness's explicit identity converter
        # model. The generator renderer itself must not touch these registers.
        if address == 0x4004056c:
            uc.mem_write(0x40040574, u32(value))
        elif address == 0x40040574:
            uc.mem_write(0x4004056c, u32(value))

    def checked(self, address, *args, measure=False):
        saved = [0x55440000 + index * 0x101 for index in range(len(REGS))]
        for reg, value in zip(REGS, saved):
            self.uc.reg_write(reg, value)
        result = self.call(address, *args, measure=measure)
        assert [self.uc.reg_read(reg) for reg in REGS] == saved
        return result

    def register(self):
        self.checked(0x60001670)

    def frame(self, *, scenario='disconnected', out_stereo=False, in_stereo=False,
              phase_period=6):
        active = scenario not in ('disconnected',) and (
            scenario != 'stop_restart' or self.tick < 24 or self.tick >= 42)
        out_ready = scenario == 'duplex' or (
            scenario == 'playback_then_silent' and self.tick < 24)
        self.write(0x40003228, u32(2 if self.tick % phase_period < phase_period // 2 else 0))
        self.write(USBF + 0x16c, u32(8 if out_ready else 0))
        self.write(USBF + 0x174, u32(0x01010004 if active else 0))
        self.write(USBF + 0x17c, u32(((2 if out_stereo else 1) << 16) |
                                    ((2 if in_stereo else 1) << 12)))
        self.write(USBF + 0xd8, u32(112 if out_stereo else 1008))
        result = self.checked(0x01009cc0, measure=True)
        self.tick += 1
        return result


def verify(original, patched, build):
    symbols = build['symbols']
    assert sha256(patched) == build['patched_app_sha256']
    wrapper = symbols['mx1_internal_audio_frame'] | 1
    assert original[0x168c:0x1690] == u32(0x01009841)
    assert patched[0x168c:0x1690] == u32(wrapper)
    # Compare generator effects against the established mainline USB pump.
    # Capture-first is an intentional, separately verified mainline change.
    assert original[0xda292:0xda296] == bytes.fromhex('4ff0000c')
    assert patched[0xda292:0xda296] == bytes.fromhex('4ff0010c')
    baseline = bytearray(original)
    baseline[0xda292:0xda296] = bytes.fromhex('4ff0010c')
    baseline = bytes(baseline)
    groups = []

    def passed(name, **details):
        groups.append({'name': name, 'status': 'pass', **details})

    machine = AudioMachine(patched, symbols, stub_render=True)
    machine.register()
    assert machine.read(CALLBACK_SLOT, 4) == u32(wrapper)
    passed('Exact candidate callback literal registers the compiled wrapper through original code',
           decoded_offset='0x168c', callback_pointer=hex(wrapper),
           slot_address=hex(CALLBACK_SLOT))

    # The bank is inferred, not established hardware. A cold all-Auto boot
    # must never access it, including a diagnostic/normal transition. Trap
    # the exact port range: the stock pump uses other words on the same page.
    # Even zero writes must fail; zero-filled emulated MMIO is not evidence
    # of safe startup.
    for rate in (0, 44100, 48000, 96000):
        machine = AudioMachine(patched, symbols)
        def forbidden_port(uc, access, address, size, value, user):
            raise AssertionError(f'Idle callback accessed generator port {address:#x}')
        machine.uc.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, forbidden_port,
                            begin=PORTS, end=PORTS + GENERATOR_COUNT * 4 - 1)
        machine.write(CONTEXT, u32(rate))
        machine.register()
        for mode in (0, 0, 4, 4, 0, 0):
            machine.write(MODE, u32(mode))
            machine.frame()
        assert not machine.generator_writes
    passed('Cold all-Auto callback never accesses the guarded generator bank',
           rates=[0, 44100, 48000, 96000], modes=[0, 0, 4, 4, 0, 0],
           guarded_interval=['0x40101100', '0x40101130'])

    abi_cases = []
    for rate in (44100, 48000, 96000):
        for mode in (0, 1, 2, 3, 4, 11, 0xffffffff):
            machine = AudioMachine(patched, symbols, stub_render=True)
            machine.write(CONTEXT, u32(rate))
            machine.write(MODE, u32(mode))
            machine.register()
            _, count = machine.frame()
            assert machine.pump_visits == 1
            expected = [(rate, PORTS)] if mode <= 3 else []
            assert machine.render_calls == expected
            assert machine.call_order == (['original_pump', 'compiled_renderer']
                                          if expected else ['original_pump'])
            assert machine.read(EXCHANGE, 72) == bytes(72)
            abi_cases.append({'sample_rate': rate, 'program_mode': mode,
                              'render_called': bool(expected),
                              'irq_wrapper_instructions_with_render_stub': count})
    passed('Actual IRQ calls retained pump first and supplies rate/ports only in normal programs',
           cases=abi_cases, renderer='Isolated only in ABI cases; subsequent regression cases execute it')

    comparisons = []
    cases = [('disconnected', False, False), ('capture_only', False, False),
             ('duplex', False, False), ('duplex', True, True),
             ('duplex', False, True), ('duplex', True, False),
             ('stop_restart', False, False), ('playback_then_silent', False, False)]
    for rate in (44100, 48000, 96000):
        for scenario, out_stereo, in_stereo in cases:
            old = AudioMachine(baseline)
            new = AudioMachine(patched, symbols)
            for machine in (old, new):
                machine.write(CONTEXT, u32(rate))
                machine.write(MODE, u32(0))
                for lane in range(18):
                    machine.write(EXCHANGE + 0x48 + 4 * lane, u32(0x22000000 + lane))
                machine.register()
                machine.trace.clear()
            counts = []
            for tick in range(72):
                period = 12 if rate == 96000 else 6
                old.frame(scenario=scenario, out_stereo=out_stereo,
                          in_stereo=in_stereo, phase_period=period)
                _, count = new.frame(scenario=scenario, out_stereo=out_stereo,
                                     in_stereo=in_stereo, phase_period=period)
                counts.append(count)
            assert new.trace == old.trace, (rate, scenario, out_stereo, in_stereo)
            assert new.out_reads == old.out_reads
            assert new.read(EXCHANGE, 0x90) == old.read(EXCHANGE, 0x90)
            assert new.read(0x01010044, 16) == old.read(0x01010044, 16)
            assert new.read(0x2000041c, 8) == old.read(0x2000041c, 8)
            assert old.pump_visits == new.pump_visits == 72
            assert len(new.render_calls) == 72
            # Unassigned freshly initialized sources must remain silent.
            assert new.read(PORTS, GENERATOR_COUNT * 4) == bytes(GENERATOR_COUNT * 4)
            comparisons.append({'sample_rate': rate, 'scenario': scenario,
                'out_channels': 2 if out_stereo else 18,
                'in_channels': 2 if in_stereo else 18,
                'ticks': 72, 'original_mmio_writes_compared': len(old.trace),
                'original_fifo_reads_compared': len(old.out_reads),
                'candidate_irq_instructions': {'min': min(counts), 'max': max(counts)}})
    passed('Compiled idle renderer preserves mainline capture-first USB pump traces in 24 differential scenarios',
           cases=comparisons, render_stub=False,
           converter='Identity fixture for retained USB pump only',
           clock_phase='Explicit per-tick stimulus; 44.1 kHz physical scheduling is not modeled')

    active_cases = []
    for rate in (44100, 48000, 96000):
        for label, mask in (('noise_only', 0x10000), ('one_bd', 1),
                            ('eleven_bd', 0x7ff), ('noise_and_eleven_bd', 0x107ff)):
            old = AudioMachine(baseline)
            new = AudioMachine(patched, symbols)
            for machine in (old, new):
                machine.write(CONTEXT, u32(rate))
                machine.write(0x600b4834, b'\x01')
                machine.write(MODE, u32(0))
                for lane in range(18):
                    machine.write(EXCHANGE + 0x48 + 4 * lane, u32(0x33000000 + lane))
                machine.register()
            new.checked(symbols['mx1_internal_routes'], mask)
            for strip in range(11):
                if mask & (1 << strip):
                    new.checked(symbols['mx1_bd_step_toggle'], strip, 0)
            new.checked(symbols['mx1_internal_transport_reset'])
            new.checked(symbols['mx1_internal_step'])
            old.trace.clear()
            new.trace.clear()
            words = []
            counts = []
            old_counts = []
            for tick in range(64):
                kwargs = {'scenario': 'duplex', 'phase_period': 12 if rate == 96000 else 6}
                _, before = old.frame(**kwargs)
                _, after = new.frame(**kwargs)
                old_counts.append(before)
                counts.append(after)
                words.append(struct.unpack('<12I', new.read(PORTS, 48)))
            assert old.trace == new.trace, (rate, label, 'stock MMIO changed')
            assert old.out_reads == new.out_reads
            assert old.read(EXCHANGE, 0x90) == new.read(EXCHANGE, 0x90)
            for port in range(12):
                selected = bool(mask & (0x10000 if port == 0 else 1 << (port - 1)))
                values = [frame[port] for frame in words]
                if selected:
                    assert any(values), (rate, label, port)
                    assert len(set(values)) > 4
                    floats = [struct.unpack('<f', u32(value))[0] for value in values]
                    assert all(math.isfinite(value) and abs(value) <= 1 for value in floats)
                else:
                    assert set(values) == {0}, (rate, label, port)
            overhead = [after - before for before, after in zip(old_counts, counts)]
            active_cases.append({'sample_rate': rate, 'sources': label,
                'source_mask': hex(mask), 'ticks': 64,
                'original_mmio_writes_compared': len(old.trace),
                'full_irq_instructions': {'first_trigger': counts[0],
                    'minimum': min(counts), 'maximum': max(counts),
                    'post_crossfade_minimum': min(counts[33:]),
                    'post_crossfade_maximum': max(counts[33:])},
                'extra_instructions_over_identical_stock_irq': {
                    'first_trigger': overhead[0], 'minimum': min(overhead),
                    'maximum': max(overhead),
                    'post_crossfade_minimum': min(overhead[33:]),
                    'post_crossfade_maximum': max(overhead[33:])}})
    passed('Active compiled generators change only their twelve reserved exchange words',
           cases=active_cases, original_pump='Unchanged actual instructions in each case',
           external_numeric_model='Identity conversion applies only to original USB pump',
           performance='Instruction counts only; eleven-voice deadline margin is unmeasured')

    # Noise stays constant in operation while stopped; BD transport resets to
    # silence at the next sample boundary. Explicit source removal also clears
    # its sample rather than leaving a held nonzero DC word in the bank.
    machine = AudioMachine(patched, symbols)
    machine.write(CONTEXT, u32(48000))
    machine.write(0x600b4834, b'\x01')
    machine.register()
    machine.checked(symbols['mx1_internal_routes'], 0x10001)
    machine.checked(symbols['mx1_bd_step_toggle'], 0, 0)
    machine.checked(symbols['mx1_internal_transport_reset'])
    machine.checked(symbols['mx1_internal_step'])
    for _ in range(20):
        machine.frame()
    assert machine.read(PORTS + 4, 4) != bytes(4)
    machine.write(0x600b4834, b'\x00')
    noise = []
    for _ in range(12):
        machine.frame()
        noise.append(machine.read(PORTS, 4))
        assert machine.read(PORTS + 4, 44) == bytes(44)
    assert len(set(noise)) > 4
    machine.checked(symbols['mx1_internal_routes'], 0)
    machine.frame()
    assert machine.read(PORTS, 48) == bytes(48)
    machine.generator_writes.clear()
    for _ in range(4):
        machine.frame()
    assert not machine.generator_writes
    passed('Transport stop silences BD, noise continues, removal clears ports once then idle skips writes')

    # Diagnostics own a different graph, so the extension must neither write
    # their bank nor assume its old silent word survived on returning. The
    # foreign word is an explicit ownership-change fixture, not an emulated
    # diagnostic-program output.
    machine = AudioMachine(patched, symbols)
    machine.write(CONTEXT, u32(48000))
    machine.write(0x600b4834, b'\x00')
    machine.register()
    machine.checked(symbols['mx1_internal_routes'], 1)
    machine.frame()
    assert machine.read(PORTS + 4, 4) == bytes(4)
    machine.write(MODE, u32(4))
    machine.write(PORTS + 4, u32(0x3e800000))
    machine.generator_writes.clear()
    machine.frame()
    machine.frame()
    assert not machine.generator_writes
    assert machine.read(PORTS + 4, 4) == u32(0x3e800000)
    machine.write(MODE, u32(0))
    machine.frame()
    assert machine.read(PORTS + 4, 4) == bytes(4), \
        'Stopped BD retained a foreign diagnostic exchange value after normal-mode resume'
    passed('Diagnostic ownership is respected and normal-mode resume restores stopped BD silence',
           foreign_word='Explicit 0x3e800000 fixture; diagnostic DSP arithmetic is not emulated')

    return {'status': 'pass', 'original_app_sha256': sha256(original),
        'patched_app_sha256': sha256(patched),
        'candidate_container_sha256': build['container_sha256'],
        'groups': groups,
        'limits': ['Interrupts are invoked, not generated by a numerical DSP emulator',
                   'No hardware audio, converter scaling, FIFO capacities or deadline margin are tested',
                   'Instruction counts are not cycles',
                   'Active generator arithmetic and per-step sequencing have separate tests']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware', type=Path)
    p.add_argument('--build', type=Path, required=True)
    p.add_argument('--app', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    raw = args.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((args.build / 'build-report.json').read_text())
    app = args.app or args.build / 'app_main.mainline.bin'
    report = verify(original, app.read_bytes(), build)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups_passed': len(report['groups'])}))


if __name__ == '__main__':
    main()
