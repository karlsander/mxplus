#!/usr/bin/env python3
"""Actual main-app USB pump with finite packet FIFOs and explicit MMIO stimuli.

No USB bus, peripheral reset semantics, numeric converter, PLL or timing is
emulated. A read beyond the current supplied packet fails even if another
packet is queued. Original prologue/capture/epilogue and compiled playback run.
"""
import argparse
from collections import deque
import json
from pathlib import Path
import struct

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R12, UC_ARM_REG_R4, UC_ARM_REG_R5
from unicorn.arm_const import UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8, UC_ARM_REG_R10

from arm_machine import Machine
from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from routing_audio_verify import REGS
from routing_mpu_verify import protect_code

PUMP = 0x01009840
USBF = 0x40010000
STATE = 0x20000420
FLAG = 0x01010044
COUNTER = 0x01010050
ALT = 0x010173f2
CAPTURE = tuple(0x11000000 + i * 0x100 for i in range(18))


def word(value):
    return struct.pack('<I', value & 0xffffffff)


def converted(value):
    return 0xbf800000 if value == 0x80000000 else value


class PacketMachine(Machine):
    def __init__(self, image, out_channels=18, in_channels=18, rate=48000, *, fixed=True):
        super().__init__(image)
        protect_code(self)
        self.uc.mem_map(0x40100000, 0x20000)
        self.write(0x40101048, struct.pack('<18I', *CAPTURE))
        self.out_channels = out_channels
        self.in_channels = in_channels
        self.rate = rate
        self.fixed = fixed
        self.packets = deque()
        self.tick = 0
        self.trace = []
        self.current = None
        self.frame_reads = []
        self.capture_writes = []
        self.commits = []
        self.resets = []
        self.uc.hook_add(UC_HOOK_MEM_READ, self.read_fifo)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self.write_mmio)
        self.uc.hook_add(UC_HOOK_CODE, self.capture_entry)

    def read_fifo(self, uc, access, address, size, value, user):
        if address == USBF + 0x1f4:
            assert size == 4
            assert self.current is not None and self.current['words'], 'OUT FIFO read past supplied packet'
            sample = self.current['words'].popleft()
            self.frame_reads.append(sample)
            uc.mem_write(address, word(sample))

    def write_mmio(self, uc, access, address, size, value, user):
        if address == 0x4004056c:
            uc.mem_write(0x40040574, word(value))  # Explicit identity conversion.
        elif address == 0x40040574:
            uc.mem_write(0x4004056c, word(value))
        elif address == USBF + 0x1b8:
            self.capture_writes.append(value)
        elif address == USBF + 0x174:
            self.commits.append(value)
        elif address == USBF + 0x170:
            self.resets.append(value)

    def capture_entry(self, uc, address, size, user):
        if self.fixed and address == 0x01009a16:
            expected = ((UC_ARM_REG_R4, USBF), (UC_ARM_REG_R5, 0),
                        (UC_ARM_REG_R6, 0x40101000), (UC_ARM_REG_R7, FLAG),
                        (UC_ARM_REG_R8, 0x40040574), (UC_ARM_REG_R10, 0x4004056c),
                        (UC_ARM_REG_R12, 1))
            assert all(uc.reg_read(reg) == value for reg, value in expected)

    def add_packet(self, frames, serial=1, *, byte_length=None):
        channels = self.out_channels
        words = [serial + i for i in range(frames * channels)]
        expected = [tuple(converted(v) for v in words[i:i+channels])
                    for i in range(0, len(words), channels)]
        if channels == 2:
            expected = [(0,) * 16 + frame for frame in expected]
        self.packets.append({'words': deque(words),
                             'length': len(words)*4 if byte_length is None else byte_length})
        return expected

    def prime_running(self):
        """Explicit running-state fixture; separate cases execute real startup."""
        self.write(STATE, word(2))
        self.write(FLAG, b'\x01')
        self.write(ALT, bytes([2 if self.out_channels == 2 else 1]))

    def step(self, *, out_active=True, in_active=True, ready=None, phase=None):
        self.current = self.packets[0] if self.packets else None
        self.frame_reads, self.capture_writes, self.commits, self.resets = [], [], [], []
        out_alt = (2 if self.out_channels == 2 else 1) if out_active else 0
        in_alt = (2 if self.in_channels == 2 else 1) if in_active else 0
        self.write(USBF + 0x17c, word(out_alt << 16 | in_alt << 12))
        if ready is None:
            ready = out_active and self.current is not None
        self.write(USBF + 0x16c, word(8 if ready else 0))
        self.write(USBF + 0xd8, word(self.current['length'] if self.current else 0))
        self.write(USBF + 0x174, word(0x01010004 if in_active else 0))
        if phase is None:
            phase = 2 if (self.tick * 8000 % self.rate) * 2 < self.rate else 0
        self.write(0x40003228, word(phase))
        saved = tuple(0x34440000 + i * 0x123 for i in range(len(REGS)))
        for reg, value in zip(REGS, saved):
            self.uc.reg_write(reg, value)
        _, instructions = self.call(PUMP, count=10000, measure=True)
        assert tuple(self.uc.reg_read(r) for r in REGS) == saved
        output = struct.unpack('<18I', self.read(0x40101000, 72))
        item = {'output': output, 'out_reads': self.frame_reads.copy(),
                'in_writes': self.capture_writes.copy(), 'commits': self.commits.copy(),
                'resets': self.resets.copy(), 'instructions': instructions,
                'counter': int.from_bytes(self.read(COUNTER, 4), 'little'),
                'state': int.from_bytes(self.read(STATE, 4), 'little')}
        self.trace.append(item)
        if self.current is not None and not self.current['words']:
            assert self.packets.popleft() is self.current
        self.tick += 1
        return output


def verify(original, patched, build):
    assert sha256(original) == build['original_app_sha256']
    assert sha256(patched) == build['patched_app_sha256']
    assert build['symbols']['mx1_usb_playback_alt'] == ALT
    assert patched[0xda0cc:0xda0ec] == original[0xda0cc:0xda0ec]
    assert patched[0xda2a2:0xda3cc] == original[0xda2a2:0xda3cc]
    # Capture-first predecessor for a differential oracle. This is an in-memory
    # test fixture, not a second firmware build or written update artifact.
    predecessor = bytearray(original)
    assert predecessor[0xda292:0xda296] == bytes.fromhex('4ff0000c')
    predecessor[0xda292:0xda296] = bytes.fromhex('4ff0010c')
    groups = []

    # The exact reported failing packets now re-arm without unsigned wrapping.
    finite = []
    for channels in (2, 18):
        for frames in range(1, 15):
            m = PacketMachine(patched, channels)
            m.prime_running()
            expected = m.add_packet(frames)
            for frame in expected:
                assert m.step() == frame
            assert not m.packets and m.read(FLAG, 1) == b'\x01'
            assert m.read(STATE, 4) == word(2)
            assert all(t['counter'] <= frames * channels * 4 for t in m.trace)
            assert sum(len(t['out_reads']) for t in m.trace) == frames * channels
            finite.append({'channels': channels, 'frames': frames,
                           'largest_fifo_read_burst': max(len(t['out_reads']) for t in m.trace)})
    groups.append({'name': 'Finite stereo/18-channel packets of 1..14 complete frames preserve samples and re-arm',
                   'status': 'pass', 'cases': finite})

    # The old stereo counter fault is a real negative control for these tests.
    old = PacketMachine(bytes(predecessor), 2, fixed=False)
    old.prime_running()
    old.add_packet(6)
    old.step()
    assert old.trace[-1]['counter'] == 0xffffffe8
    groups.append({'name': 'Unfixed predecessor reproduces the 48-byte stereo counter underflow', 'status': 'pass'})

    # Exercise both direct and buffered conversion branches, including the
    # special minimum integer which bypasses the original conversion port.
    for channels in (2, 18):
        m = PacketMachine(patched, channels)
        m.prime_running()
        values = [0, 0x100, 0x7fffff00, 0x80000000, 0xffffff00, 0xffff0000] * channels
        m.packets.append({'words': deque(values), 'length': len(values)*4})
        for offset in range(0, len(values), channels):
            expected = tuple(converted(v) for v in values[offset:offset+channels])
            assert m.step() == (expected if channels == 18 else (0,) * 16 + expected)
        assert not m.packets and m.read(FLAG, 1) == b'\x01'
    groups.append({'name': 'Direct and buffered silence/full-scale/negative samples retain original conversion handling', 'status': 'pass'})

    # Continuous, independently selected IN/OUT alternates. Packet lengths vary
    # around the configured rate, including 44.1-kHz five/six-frame packets.
    continuous = []
    max_instructions = 0
    for rate, pattern in ((44100, [5, 6]), (48000, [6, 5, 7]), (96000, [12, 11, 13])):
        for out_channels in (2, 18):
            for in_channels in (2, 18):
                m = PacketMachine(patched, out_channels, in_channels, rate)
                m.prime_running()
                expected = []
                for index, frames in enumerate(pattern * 12):
                    expected.extend(m.add_packet(frames, 0x10000 + index * 0x1000))
                for frame in expected:
                    assert m.step() == frame
                assert not m.packets and m.read(FLAG, 1) == b'\x01'
                assert all(t['counter'] <= 1008 for t in m.trace)
                assert all(len(t['in_writes']) in (0, in_channels) for t in m.trace)
                assert tuple(m.trace[-1]['in_writes']) == (CAPTURE[-2:] if in_channels == 2 else CAPTURE)
                max_instructions = max(max_instructions, *(t['instructions'] for t in m.trace))
                if out_channels == 18:
                    before = PacketMachine(bytes(predecessor), out_channels, in_channels, rate, fixed=False)
                    before.prime_running()
                    for index, frames in enumerate(pattern * 12):
                        before.add_packet(frames, 0x10000 + index * 0x1000)
                    for _ in expected:
                        before.step()
                    for a, b in zip(before.trace, m.trace):
                        for key in ('output', 'out_reads', 'in_writes', 'commits', 'resets', 'counter', 'state'):
                            assert a[key] == b[key], (rate, in_channels, key)
                continuous.append({'rate': rate, 'out_channels': out_channels, 'in_channels': in_channels,
                                   'sample_frames': len(expected), 'stock_18_channel_trace_equal': out_channels == 18})
    groups.append({'name': 'All rate/alternate combinations stream finite varying packets; 18-channel traces match predecessor',
                   'status': 'pass', 'cases': continuous,
                   'maximum_observed_instructions': max_instructions, 'timing_measurement': False})

    # Real cold startup and idle/readiness loss; capture-first still reaches
    # state4 without playback. Stop/start must not replay old buffered samples.
    starts = []
    for channels in (2, 18):
        m = PacketMachine(patched, channels, channels)
        for _ in range(30):
            assert m.step(out_active=False) == (0,) * 18
        assert m.read(FLAG + 4, 4) == word(4)
        expected = m.add_packet(6, 0x20000)
        observed = []
        for _ in range(30):
            frame = m.step()
            if any(frame):
                observed.append(frame)
        assert observed == expected
        expected = m.add_packet(6, 0x30000)
        observed = []
        for _ in range(30):
            frame = m.step()
            if any(frame):
                observed.append(frame)
        assert observed == expected
        starts.append({'channels': channels, 'capture_first': True, 'readiness_restart': True})
    groups.append({'name': 'Cold startup, capture without OUT, and playback restart preserve priming and sample order',
                   'status': 'pass', 'cases': starts})

    switches = []
    for source in (2, 18):
        for target in (2, 18):
            for consumed in (1, 4, 5):  # FIFO, two-frame tail, one-frame tail.
                m = PacketMachine(patched, source)
                m.prime_running()
                m.add_packet(6, 0x40000)
                for _ in range(consumed):
                    m.step()
                # Alternate0 flush is an explicit peripheral fixture. IN remains
                # active; its original capture state must not be reset by OUT.
                m.packets.clear()
                assert m.step(out_active=False) == (0,) * 18
                assert m.read(STATE, 4) == word(0)
                m.out_channels = target
                expected = m.add_packet(6, 0x50000)
                observed = []
                for _ in range(30):
                    frame = m.step()
                    if any(frame):
                        observed.append(frame)
                assert observed == expected
                switches.append({'from': source, 'to': target, 'after_frames': consumed, 'via_alt0': True})
                if source != target:
                    direct = PacketMachine(patched, source)
                    direct.prime_running()
                    direct.add_packet(6, 0x60000)
                    for _ in range(consumed):
                        direct.step()
                    direct.packets.clear()  # Hardware alternate change flush modeled.
                    direct.out_channels = target
                    expected = direct.add_packet(6, 0x70000)
                    observed = []
                    for _ in range(30):
                        frame = direct.step()
                        if any(frame):
                            observed.append(frame)
                    assert observed == expected
                    switches.append({'from': source, 'to': target, 'after_frames': consumed, 'via_alt0': False})
    groups.append({'name': 'Stop/restart and 2/18-channel switches discard old FIFO/tail format without overreading',
                   'status': 'pass', 'cases': switches})

    bad_lengths = []
    for channels in (2, 18):
        for length in (0, 1, 3, channels * 4 - 1, channels * 4 + 1):
            m = PacketMachine(patched, channels)
            m.prime_running()
            m.add_packet(1, byte_length=length)
            assert m.step() == (0,) * 18
            assert not m.trace[-1]['out_reads']
            assert m.read(STATE, 4) == word(0) and m.read(COUNTER, 4) == word(0)
            bad_lengths.append({'channels': channels, 'bytes': length})
    groups.append({'name': 'Zero/partial-frame packet lengths fail silent before FIFO access', 'status': 'pass', 'cases': bad_lengths})

    return {'status': 'pass', 'patched_app_sha256': sha256(patched), 'groups': groups,
            'hardware_access': False,
            'boundaries': [
                'Original callback prologue/phase/capture/epilogue and replacement playback instructions execute with code write protection.',
                'Finite packet bytes/readiness and FIFO delivery are supplied; alternate changes explicitly flush modeled peripheral packets.',
                'Conversion registers use identity mocks except the executed original INT_MIN special-case semantics.',
                'RTOS scheduling, real USB packet arrival/feedback, numeric audio scaling, peripheral reset and PLL lock are not emulated.',
                'Instruction counts are not CPU-cycle or real-time deadline measurements.',
            ]}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build', type=Path, default=Path('build/mainline'))
    p.add_argument('--output', type=Path, default=Path('build/mainline/packet-verification.json'))
    args = p.parse_args()
    raw = Path('inputs/MX1_UPD.original.bin').read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((args.build / 'build-report.json').read_text())
    report = verify(original, (args.build / 'app_main.mainline.bin').read_bytes(), build)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups': len(report['groups'])}))


if __name__ == '__main__':
    main()
