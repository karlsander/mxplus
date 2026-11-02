#!/usr/bin/env python3
"""Reproduce the bounded review of the frozen 88457445 mainline.

Exit zero means the recorded observations were reproduced, including the
known stereo accounting defect. This is NOT a firmware acceptance gate.
No firmware is built, modified or installed; no hardware is accessed.
"""
import hashlib
import json
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1

from arm_machine import Machine, RETURN
from container_tool import ORIGINAL_SHA256
from routing_storage_verify import StorageMachine, record, SCENE_RECORD, SYSTEM_RECORD

APP_SHA = "595c901fc03dc83851e390554542ae18566e3539f0c46971d7a7c9774f147758"
CANDIDATE_SHA = "88457445ffe1abeca8365198d0c15ed967c6f5b4dac08393da52c575a80660ba"
ORIGINAL_APP_SHA = "256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b"
PUMP = 0x01009840
USBF = 0x40010000
PLAYBACK_STATE = 0x20000420
PACKET_REMAINING = 0x01010050


def word(value):
    return struct.pack("<I", value & 0xffffffff)


def checked_file(path, expected):
    data = (ROOT / path).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected, path
    return data


def finite_packet(image, channels, frames):
    """Supply one finite packet to the actual running playback arm.

    Packet bytes/readiness are explicit stimuli, not a peripheral emulator.
    Capture is inactive. Conversion registers are identity mocks.
    """
    m = Machine(image)
    m.uc.mem_map(0x40100000, 0x20000)
    m.write(USBF + 0x17c, word((2 if channels == 2 else 1) << 16))
    m.write(PLAYBACK_STATE, word(2))
    m.write(0x01010044, b"\x01")
    words = list(range(1, channels * frames + 1))
    reads = []
    history = []

    def read_fifo(uc, access, address, size, value, user):
        if address == USBF + 0x1f4:
            assert size == 4 and words, "Read beyond supplied packet"
            sample = words.pop(0)
            reads.append(sample)
            uc.mem_write(address, word(sample))

    def convert(uc, access, address, size, value, user):
        if address == 0x4004056c:
            uc.mem_write(0x40040574, word(value))

    m.uc.hook_add(UC_HOOK_MEM_READ, read_fifo)
    m.uc.hook_add(UC_HOOK_MEM_WRITE, convert)
    for tick in range(frames):
        m.write(USBF + 0x16c, word(8 if words else 0))
        m.write(USBF + 0xd8, word(channels * frames * 4))
        m.call(PUMP)
        values = struct.unpack("<18I", m.read(0x40101000, 72))
        expected = tuple(range(tick * channels + 1, (tick + 1) * channels + 1))
        assert values == (expected if channels == 18 else (0,) * 16 + expected)
        history.append({
            "tick": tick,
            "remaining_counter": int.from_bytes(m.read(PACKET_REMAINING, 4), "little"),
            "fifo_words_left": len(words),
            "state": int.from_bytes(m.read(PLAYBACK_STATE, 4), "little"),
        })
    assert not words and reads == list(range(1, channels * frames + 1))
    underflows = [h["tick"] for h in history if h["remaining_counter"] > 0x7fffffff]
    if channels == 2:
        assert underflows and all(h["state"] == 2 for h in history)
        assert m.read(0x01010044, 1) == b"\x00", "Next packet is never re-armed"
    else:
        assert not underflows
        assert history[frames - 3]["state"] == 3
        assert history[-1]["state"] == 2
        assert m.read(0x01010044, 1) == b"\x01"
    return {"channels": channels, "frames": frames,
            "packet_bytes": channels * frames * 4,
            "first_counter_underflow_tick": underflows[0] if underflows else None,
            "sample_words_in_order": True, "fifo_overread_observed": False,
            "history": history}


def accelerated_stereo_wrap(image):
    """Seed the counter reached if readiness never resets stereo playback.

    This avoids executing hundreds of millions of ticks. The arithmetic prefix
    is modeled; the resulting callback, including its tail prefetch, executes.
    It is not a claim that real hardware maintains this readiness pattern.
    """
    frames = 6
    initial_bytes = frames * 2 * 4
    trigger_tick = ((initial_bytes - 144) // 8 * pow(9, -1, 2**29)) % (2**29)
    elapsed_ticks = trigger_tick - 1
    remaining = (initial_bytes - elapsed_ticks * 72) & 0xffffffff
    assert remaining == 216 and elapsed_ticks % frames == 1
    available_words = (frames - elapsed_ticks % frames) * 2
    m = Machine(image)
    m.uc.mem_map(0x40100000, 0x20000)
    m.write(USBF + 0x17c, word(2 << 16))
    m.write(USBF + 0x16c, word(8))
    m.write(USBF + 0xd8, word(initial_bytes))
    m.write(PLAYBACK_STATE, word(2))
    m.write(0x01010044, b"\x00")
    m.write(PACKET_REMAINING, word(remaining))
    reads = []

    def read_fifo(uc, access, address, size, value, user):
        if address == USBF + 0x1f4:
            reads.append(address)
            # Out-of-packet reads are counted and return modeled zero. No
            # assertion about a real peripheral's empty-FIFO response follows.
            uc.mem_write(address, word(len(reads) if len(reads) <= available_words else 0))

    def convert(uc, access, address, size, value, user):
        if address == 0x4004056c:
            uc.mem_write(0x40040574, word(value))

    m.uc.hook_add(UC_HOOK_MEM_READ, read_fifo)
    m.uc.hook_add(UC_HOOK_MEM_WRITE, convert)
    m.call(PUMP)
    assert len(reads) == 38 and available_words == 10
    assert m.read(PLAYBACK_STATE, 4) == word(3)
    return {"modeled_prefix_ticks": elapsed_ticks,
            "trigger_tick": trigger_tick,
            "prefix_assumption": "Continuous stereo packets and OUT readiness with no reset/re-arm",
            "counter_seed": remaining, "available_packet_words": available_words,
            "actual_callback_fifo_reads": len(reads),
            "reads_beyond_supplied_packet": len(reads) - available_words,
            "physical_occurrence_verified": False}


class PreemptionMachine(StorageMachine):
    observer = None

    def hook(self, uc, address, size, user):
        # Observe the boundary before a modeled call redirects PC, so the
        # suspended context resumes at the same entry as the recorded trace.
        if self.observer is not None and self.observer(address):
            uc.emu_stop()
            return
        if address in (0x0100ab04, 0x0100baee):
            self.ret()  # DSP programming is separately tested; no numeric DSP here.
        else:
            super().hook(uc, address, size, user)


def refresh_during_edit(image, symbols):
    """Interrupt edit traces, grouping Thumb IT blocks at their outer edges."""
    m = PreemptionMachine(image, symbols)
    routes = [1, 6, 7, 9, 5, 8, 11, 20, 26, 50, 51]
    cases = []
    for strip, delta in ((0, 1), (4, 1), (10, 1), (0, -1), (4, -1), (10, -1)):
        def prepare():
            m.write(SCENE_RECORD, record(routes))
            m.write(SYSTEM_RECORD, record(routes))
            m.write(symbols["mx1_route_state"], bytes(routes))
            m.write(0x0101726f, bytes(11) + b"\x01")  # applied=0, route_ready=1
            m.posts.clear()
            m.uc.reg_write(UC_ARM_REG_SP, 0x2001fff0)
            m.uc.reg_write(UC_ARM_REG_LR, RETURN | 1)
            m.uc.reg_write(UC_ARM_REG_R0, strip)
            m.uc.reg_write(UC_ARM_REG_R1, delta & 0xffffffff)

        prepare()
        trace = []
        m.observer = lambda address: trace.append(address)
        m.call(symbols["mx1_route_adjust"], strip, delta & 0xffffffff)
        m.observer = None
        expected = routes.copy()
        expected[strip] += delta
        expected = record(expected)
        assert m.read(SCENE_RECORD, 16) == expected
        # Unicorn cannot reliably stop/resume inside an IT block (notably
        # conditional POP {pc}). Cover the block's entry and following code,
        # and disclose the internal boundaries we cannot faithfully model.
        cs = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
        it_slots = set()
        for address in trace:
            ins = next(cs.disasm(m.read(address, 4), address))
            if ins.mnemonic.startswith("it"):
                cursor = address + ins.size
                for _ in range(len(ins.mnemonic) - 1):
                    it_slots.add(cursor)
                    cursor += next(cs.disasm(m.read(cursor, 4), cursor)).size
        tested = 0
        for position in range(len(trace)):
            if trace[position] in it_slots:
                continue
            prepare()
            hits = [0]

            def stop(address):
                should_stop = hits[0] == position
                hits[0] += 1
                return should_stop

            m.observer = stop
            m.uc.emu_start(symbols["mx1_route_adjust"], RETURN, count=100000)
            m.observer = None
            assert hits[0] == position + 1, (strip, delta, position, hits[0], hex(m.uc.reg_read(UC_ARM_REG_PC)))
            assert m.uc.reg_read(UC_ARM_REG_PC) == trace[position]
            context = m.uc.context_save()
            resume = m.uc.reg_read(UC_ARM_REG_PC)
            # A distinct DSP stack prevents corrupting the suspended UI frame.
            m.uc.reg_write(UC_ARM_REG_SP, 0x2001bff0)
            m.uc.reg_write(UC_ARM_REG_LR, RETURN | 1)
            m.uc.emu_start(symbols["mx1_route_flush"], RETURN, count=100000)
            assert m.uc.reg_read(UC_ARM_REG_PC) == RETURN
            assert m.uc.reg_read(UC_ARM_REG_SP) == 0x2001bff0
            m.uc.context_restore(context)
            m.uc.emu_start(resume | 1, RETURN, count=100000)
            assert m.uc.reg_read(UC_ARM_REG_PC) == RETURN
            assert m.uc.reg_read(UC_ARM_REG_SP) == 0x2001fff0
            assert m.read(SCENE_RECORD, 16) == expected, (strip, delta, position)
            assert m.read(SYSTEM_RECORD, 16) == expected, (strip, delta, position)
            assert m.read(symbols["mx1_route_state"], 11) == expected[4:15]
            tested += 1
        cases.append({"strip": strip, "delta": delta, "boundaries": tested,
                      "it_internal_boundaries_excluded": len(trace) - tested,
                      "status": "pass"})
    return cases


def instruction_evidence(original):
    m = Machine(original)
    disassembler = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    blocks = []
    for start, end in ((0x01003dfa, 0x01003e1a), (0x010049a8, 0x010049d0),
                       (0x01009860, 0x0100987c), (0x010098da, 0x01009976),
                       (0x010099ec, 0x01009a00)):
        offset = 0xd0b8c + start - 0x01000300
        blocks.append(f"; main app decoded +0x{offset:x}, runtime 0x{start:08x}")
        for ins in disassembler.disasm(m.read(start, end - start), start):
            blocks.append(f"{ins.address:08x}  {ins.bytes.hex():10s} {ins.mnemonic:8s} {ins.op_str}")
    return "\n".join(blocks) + "\n"


def main():
    checked_file("inputs/MX1_UPD.original.bin", ORIGINAL_SHA256)
    checked_file("build/mainline/MXPLUS_MAINLINE_UNTESTED.bin", CANDIDATE_SHA)
    image = checked_file("build/mainline/app_main.mainline.bin", APP_SHA)
    original = checked_file("analysis/container_app_main.bin", ORIGINAL_APP_SHA)
    build = json.loads((ROOT / "build/mainline/build-report.json").read_text())
    assert build["patched_app_sha256"] == APP_SHA
    assert build["container_sha256"] == CANDIDATE_SHA
    packets = [finite_packet(image, channels, frames)
               for channels in (18, 2) for frames in (5, 6, 12)]
    races = refresh_during_edit(image, build["symbols"])
    report = {
        "status": "observations reproduced; known defect remains",
        "hardware_access": False,
        "candidate_sha256": CANDIDATE_SHA,
        "patched_app_sha256": APP_SHA,
        "original_app_sha256": ORIGINAL_APP_SHA,
        "findings": [{
            "id": "USB-STEREO-ACCOUNTING", "priority": "P1",
            "component": "app_main", "decoded_offset": "0xda1d0",
            "runtime_address": "0x01009944", "instruction": "subs r0, #0x48",
            "observation": "Stereo consumes eight bytes but decrements the packet counter by 72; normal next-packet re-arm is not reached.",
            "scope": "Inherited stock pump behavior exposed by the advertised stereo alternate; physical symptom not measured.",
        }],
        "finite_packets": packets,
        "accelerated_stereo_counter_wrap": accelerated_stereo_wrap(image),
        "routing_preemptions": races,
        "boundaries": [
            "Original/candidate Thumb instructions run; Ghidra pseudocode is not executed.",
            "Packet tests start in running playback state2 with a new packet; capture is inactive.",
            "OUT length/readiness and finite FIFO contents are supplied, conversion is identity; no peripheral timing or USB bus emulation.",
            "No FIFO overread or incorrect sample order occurs in these short packet fixtures; the established defect is counter underflow and missing packet re-arm.",
            "A separately accelerated uninterrupted-readiness case seeds the arithmetically derived later counter and reproduces a 38-word read burst against ten remaining packet words; physical occurrence is unverified.",
            "Routing tests execute compiled restore/store/adjust/flush with code write protection and separate UI/DSP stacks.",
            "Routing mode is Mixer; parameter lookup, event delivery, DSP writers, notifications and storage boundaries are modeled.",
            "One complete DSP refresh interrupts each edit at each tested boundary; this is not an exhaustive RTOS or scene-copy race test.",
            "Thumb IT blocks are tested at their outer boundaries; Unicorn cannot faithfully pause at their internal conditional returns.",
            "No physical flash read/program, power-loss recovery, DSP arithmetic, audio quality or deadline margin is established.",
        ],
    }
    destination = Path(__file__).resolve().parent
    (destination / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (destination / "instructions.asm").write_text(instruction_evidence(original))
    print(report["status"])
    print(f"{len(packets)} finite-packet cases; {sum(r['boundaries'] for r in races)} routing preemptions")


if __name__ == "__main__":
    main()
