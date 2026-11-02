#!/usr/bin/env python3
"""Execute the candidate's BD control, clock and sample-state machine.

The actual linked extension and original clock function bodies execute. Their
unrelated native parameter/event helpers are explicitly stubbed only in clock
tests. Numerical rendering and publication code have no stubs. Hardware clock,
interrupt priority, DSP exchange timing and physical audio are not modeled.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from elftools.elf.elffile import ELFFile
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
    UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
    UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
)

from container_tool import COMPONENT_BY_NAME, ORIGINAL_SHA256, component_unpacked, sha256
from arm_machine import Machine, RETURN

RUNNING = 0x600B4834
PORTS = 0x20013000
SCRATCH_VOICE = 0x20014000
VOICE_BYTES = 32
STEP_BYTES = 11 * 16 * 4
NOISE_BIT = 1 << 16
BD_BITS = (1 << 11) - 1
DEFAULT_STEP = 53 << 16
CLOCK_ENTRIES = {
    "mx1_internal_clock_start": 0x6000A7DC,
    "mx1_internal_clock_stop": 0x6000A810,
    "mx1_internal_clock_step": 0x6000A894,
}
SAVED_REGS = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
              UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)

# Original callees outside the transport/step body being compared. The test
# records calls and supplies deterministic parameter masks or a neutral return;
# it does not claim to emulate their event queue, BFX voices or timer hardware.
NATIVE_STUBS = {
    0x6000C754: "native transaction constructor",
    0x6000C7A0: "native parameter append",
    0x6000C7C8: "native repeated parameter append",
    0x6000C794: "native transaction completion",
    0x6000A366: "native transport notification helper",
    0x6005A198: "native stop/clock helper",
    0x6005B3D8: "native parameter bank selector",
    0x6005A172: "native step-mask reader",
    0x60033238: "native beat-effect trigger",
}


def checked(ok, reason):
    if not ok:
        raise AssertionError(reason)


def symbols_from(elf: Path) -> dict:
    with elf.open("rb") as f:
        e = ELFFile(f)
        symbols = {s.name: s["st_value"] for s in
                   e.get_section_by_name(".symtab").iter_symbols() if s.name}
    return symbols


class CoreMachine(Machine):
    def __init__(self, image: bytes, symbols: dict):
        super().__init__(image)
        from routing_mpu_verify import protect_code
        protect_code(self)
        self.symbols = symbols
        self.stub_native = False
        self.native_mask = 0
        self.native_calls = []
        self.measuring = False
        self.instructions = 0
        self.uc.hook_add(UC_HOOK_CODE, self.instruction)
        self.write(PORTS, b"\xA5" * 48)

    def instruction(self, u, address, size, user):
        if self.measuring:
            self.instructions += 1
        if self.stub_native and address in NATIVE_STUBS:
            args = tuple(u.reg_read(r) for r in
                         (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
            self.native_calls.append((address, args))
            value = self.native_mask if address == 0x6005A172 else 0
            u.reg_write(UC_ARM_REG_R0, value)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))

    def invoke(self, name, *args, measured=False):
        self.measuring = measured
        self.instructions = 0
        try:
            # Exercise the exact candidate's installed far jumps whenever a
            # transport/step callback is requested. Trampoline comparison below
            # still enters its explicit original-body helper independently.
            entry = CLOCK_ENTRIES.get(name, self.symbols[name])
            result = self.call(entry, *[v & 0xFFFFFFFF for v in args],
                               count=1000000)[0]
        finally:
            self.measuring = False
        return result, self.instructions

    def word(self, address):
        return struct.unpack("<I", self.read(address, 4))[0]

    def put(self, address, value):
        self.write(address, struct.pack("<I", value & 0xFFFFFFFF))

    def global_word(self, name):
        return self.word(self.symbols[name])

    def set_global(self, name, value):
        self.put(self.symbols[name], value)

    def voice(self, strip=0):
        return self.read(self.symbols["voices"] + strip * VOICE_BYTES, VOICE_BYTES)

    def port(self, index):
        return self.word(PORTS + index * 4)

    def pattern(self, strip, step, pitch=0, decay=53, enabled=True):
        self.put(self.symbols["mx1_bd_steps"] + (strip * 16 + step) * 4,
                 int(enabled) | ((pitch & 255) << 8) | (decay << 16))

    def render(self, frames=1, rate=48000):
        result = []
        for _ in range(frames):
            self.invoke("mx1_internal_render", rate, PORTS)
            result.append(self.read(PORTS, 48))
        return result

    def start_direct(self):
        self.write(RUNNING, b"\x01")
        self.invoke("mx1_internal_transport_reset")
        self.invoke("mx1_internal_step")


def verify(original: bytes, patched: bytes, build: dict, elf_path: Path) -> dict:
    checked(sha256(original) == build["original_app_sha256"], "original identity mismatch")
    checked(sha256(patched) == build["patched_app_sha256"], "candidate identity mismatch")
    symbols = symbols_from(elf_path)
    groups = []

    def machine(image=patched):
        return CoreMachine(image, symbols)

    def passed(name, **evidence):
        groups.append(dict(name=name, status="pass", **evidence))

    # The actual word-width writes are the UI/audio publication contract. The
    # frame reader never modifies these words, and one UI task is their writer.
    m = machine()
    base = symbols["mx1_bd_steps"]
    checked(base % 4 == 0, "step publication words are unaligned")
    checked(m.read(base, STEP_BYTES) == struct.pack("<I", DEFAULT_STEP) * 176,
            "unexpected startup step defaults")
    writes = []
    hook = m.uc.hook_add(UC_HOOK_MEM_WRITE,
        lambda _u, _a, address, size, value, _d: writes.append((address, size, value)),
        begin=base, end=base + STEP_BYTES - 1)
    for strip in range(11):
        for step in range(16):
            offset = (strip * 16 + step) * 4
            before = m.read(base, STEP_BYTES)
            writes.clear()
            m.invoke("mx1_bd_step_toggle", strip, step)
            m.invoke("mx1_bd_step_adjust", strip, step, 0, 0x7FFFFFFF)
            m.invoke("mx1_bd_step_adjust", strip, step, 1, 0x80000000)
            expected = bytearray(before)
            struct.pack_into("<I", expected, offset, (52 << 16) | (1 << 8) | 1)
            checked(m.read(base, STEP_BYTES) == expected, "step edit affected another step")
            checked(writes == [(base + offset, 4, DEFAULT_STEP | 1),
                               (base + offset, 4, DEFAULT_STEP | 0x101),
                               (base + offset, 4, (52 << 16) | 0x101)],
                    "step publication was not exactly one aligned word per edit")
            checked(m.invoke("mx1_bd_step_get", strip, step)[0] == (52 << 16) | 0x101,
                    "step getter packing mismatch")
    m.uc.hook_del(hook)
    for _ in range(80): m.invoke("mx1_bd_step_adjust", 0, 0, 0, 1)
    checked((m.word(base) >> 8) & 255 == 24, "positive pitch clamp failed")
    for _ in range(80): m.invoke("mx1_bd_step_adjust", 0, 0, 0, -1)
    checked((m.word(base) >> 8) & 255 == (-24 & 255), "negative pitch clamp failed")
    for _ in range(120): m.invoke("mx1_bd_step_adjust", 0, 0, 1, 1)
    checked((m.word(base) >> 16) & 255 == 100, "positive decay clamp failed")
    for _ in range(120): m.invoke("mx1_bd_step_adjust", 0, 0, 1, -1)
    checked((m.word(base) >> 16) & 255 == 0 and m.word(base) & 1,
            "decay clamp altered enabled flag")
    before = m.read(base, STEP_BYTES)
    for strip, step, parameter, delta in ((11,0,0,1), (0,16,0,1), (0,0,2,1),
                                         (0xFFFFFFFF,0,0,1), (0,0,0,0)):
        m.invoke("mx1_bd_step_adjust", strip, step, parameter, delta)
    for strip, step in ((11,0), (0,16), (0xFFFFFFFF,0xFFFFFFFF)):
        m.invoke("mx1_bd_step_toggle", strip, step)
        checked(m.invoke("mx1_bd_step_get", strip, step)[0] == 0,
                "invalid getter did not return zero")
    checked(before == m.read(base, STEP_BYTES), "invalid step edit changed pattern")
    passed("All 176 per-step words publish atomically and retain step/channel isolation",
           editable_steps=176, observed_publication_width=4, parameters=["semitones", "decay"],
           limits={"pitch": [-24,24], "decay": [0,100]}, invalid_inputs_unchanged=True)

    # Real stock step bodies run with documented parameter/event boundaries.
    # Vary the native loop length and the callback's index; the BD counter must
    # still traverse exactly sixteen steps independent of those arguments.
    phases = []
    for length in (1, 2, 3, 4, 7, 8, 16):
        m = machine()
        m.stub_native = True
        m.write(RUNNING, b"\x01")
        m.put(RUNNING + 12, length - 1)
        m.invoke("mx1_internal_transport_reset")
        observed = []
        for index in range(48):
            m.invoke("mx1_internal_clock_step", 0x20011000, index % length)
            observed.append(m.invoke("mx1_bd_current_step")[0])
        checked(observed == [i % 16 for i in range(48)], "BD loop followed native length")
        phases.append({"native_length": length, "callbacks": 48, "bd_cycles": 3})
        old = m.global_word("mx1_bd_clock")
        m.write(RUNNING, b"\x00")
        m.invoke("mx1_internal_step")
        checked(m.global_word("mx1_bd_clock") == old, "clock advanced while stopped")
        checked(m.invoke("mx1_bd_current_step")[0] == 0xFFFFFFFF, "stopped playhead visible")
        m.write(RUNNING, b"\x01")
        m.invoke("mx1_internal_transport_reset")
        checked(m.invoke("mx1_bd_current_step")[0] == 0xFFFFFFFF, "reset playhead visible")
    passed("Independent sixteen-step counter survives seven native loop lengths",
           cases=phases, original_step_body_executes=True,
           native_stubs={hex(k): v for k,v in NATIVE_STUBS.items()})

    # Trigger two strips with different words and compare their captured
    # engine coefficients to direct compiled-engine calls. Editing a step while
    # a note rings must not mutate the voice already playing that note.
    a, b = machine(), machine()
    for m in (a,b):
        m.invoke("mx1_internal_routes", (1 << 0) | (1 << 10))
        m.pattern(0, 0, -12, 25)
        m.pattern(10, 0, 12, 75)
        m.start_direct()
        m.render()
    checked(a.voice(0) != a.voice(10), "BD voices unexpectedly shared state")
    for strip, pitch, decay in ((0,-12,25), (10,12,75)):
        a.write(SCRATCH_VOICE, bytes(VOICE_BYTES))
        a.invoke("mxkick_trigger", SCRATCH_VOICE, 48000, pitch, decay)
        a.invoke("mxkick_next", SCRATCH_VOICE)
        checked(a.read(SCRATCH_VOICE, VOICE_BYTES) == a.voice(strip), "trigger snapshot differs")
    a.invoke("mx1_bd_step_adjust", 0, 0, 0, 1)
    a.invoke("mx1_bd_step_adjust", 0, 0, 1, 1)
    a.invoke("mx1_bd_step_toggle", 10, 0)
    checked(a.render(256) == b.render(256), "stored step edit altered a ringing note")
    checked(a.voice(0) == b.voice(0) and a.voice(10) == b.voice(10), "voice snapshot mutated")
    # Sixteen callback advances return to the same step number with a new
    # serial; that strike must still be distinguished from the previous one.
    old_clock = a.global_word("mx1_bd_clock")
    for _ in range(16): a.invoke("mx1_internal_step")
    checked((a.global_word("mx1_bd_clock") & 15) == (old_clock & 15)
            and a.global_word("mx1_bd_clock") != old_clock, "clock serial aliased")
    a.render()
    checked(struct.unpack_from("<I", a.voice(), 28)[0] == 31,
            "same-number new step did not retrigger")
    a.render()
    checked(struct.unpack_from("<I", a.voice(), 28)[0] == 30,
            "unchanged clock retriggered twice")
    passed("Per-strip trigger snapshots preserve ringing notes through later step edits",
           distinct_strips=[0,10], comparison_frames=256,
           same_step_next_cycle_retriggers=True, repeated_frame_does_not_retrigger=True)

    m = machine()
    m.stub_native = True
    m.invoke("mx1_internal_routes", NOISE_BIT | 1)
    m.pattern(0,0,0,100)
    generation = m.global_word("transport_generation")
    m.invoke("mx1_internal_clock_start")
    checked(m.global_word("transport_generation") == generation + 1,
            "installed START hook failed to publish a new reset generation")
    m.invoke("mx1_internal_clock_start")
    checked(m.global_word("transport_generation") == generation + 1,
            "repeated START reset an already running sequence")
    m.invoke("mx1_internal_step")
    m.render(128)
    checked(m.port(1) != 0, "kick did not start before stop test")
    # This was a concrete race in the initial draft: a complete stop/start
    # and a disabled first step between samples must kill the old tail.
    m.pattern(0,0,0,100,False)
    generation = m.global_word("transport_generation")
    m.invoke("mx1_internal_clock_stop")
    checked(m.global_word("transport_generation") == generation + 1 and
            not (m.global_word("mx1_bd_clock") & 0x80000000),
            "installed STOP hook failed to invalidate the previous step")
    m.invoke("mx1_internal_clock_start")
    m.invoke("mx1_internal_step")
    m.render()
    checked(m.voice() == bytes(VOICE_BYTES) and m.port(1) == 0,
            "stop/start between frames retained previous voice")
    checked(m.port(0) != 0, "continuous noise incorrectly followed transport")
    m.pattern(0,0,0,53)
    m.invoke("mx1_internal_clock_stop")
    m.invoke("mx1_internal_clock_start")
    checked(m.invoke("mx1_bd_current_step")[0] == 0xFFFFFFFF, "start exposed stale playhead")
    m.render(4)
    checked(m.port(1) == 0, "restart sounded before first clock step")
    m.invoke("mx1_internal_step")
    m.render(64)
    checked(m.port(1) != 0, "first restarted strike failed")
    m.invoke("mx1_internal_clock_stop")
    m.render()
    checked(m.port(1) == 0 and m.voice() == bytes(VOICE_BYTES), "stop failed to silence")
    noise_frames = m.render(16)
    checked(len({frame[:4] for frame in noise_frames}) > 1, "noise stopped with transport")
    passed("Stop/restart clears voices even when both occur between sample callbacks",
           compiled_stock_start_stop_bodies=True, independent_reset_generation=True,
           installed_candidate_entries={name:hex(at) for name,at in CLOCK_ENTRIES.items()},
           disabled_first_step_silent=True, noise_continues_when_stopped=True)

    m = machine()
    m.invoke("mx1_internal_routes", 0xFFFFFFFF)
    checked(m.global_word("mx1_internal_active_mask") == NOISE_BIT | BD_BITS,
            "route mask admitted reserved bits")
    m.pattern(0,0,0,100)
    m.start_direct()
    m.render(64)
    checked(m.port(1) != 0, "rate test did not start")
    for rate in (96000, 44100, 48000):
        m.render(rate=rate)
        checked(m.port(1) == 0 and m.voice() == bytes(VOICE_BYTES), "rate change kept old tail")
        m.invoke("mx1_internal_transport_reset")
        m.invoke("mx1_internal_step")
        m.render(64, rate=rate)
        checked(m.port(1) != 0, "kick failed at supported rate")
    m.render(rate=12345)
    checked(m.read(PORTS,48) == bytes(48), "unsupported sample rate was not silent")
    m.render(rate=48000)
    checked(m.port(1) == 0, "return from invalid rate replayed stale strike")
    checked(m.port(0) != 0, "noise failed to resume at valid rate")
    m.invoke("mx1_internal_transport_reset")
    m.invoke("mx1_internal_step")
    m.render(64)
    m.invoke("mx1_internal_routes", 0)
    m.render()
    checked(m.read(PORTS,48) == bytes(48), "route removal left a generator sample")
    checked(m.read(symbols["voices"],VOICE_BYTES*11) == bytes(VOICE_BYTES*11),
            "route removal retained voice state")
    m.invoke("mx1_internal_step")
    m.render(4)
    m.invoke("mx1_internal_routes", 1)
    m.render(4)
    checked(m.port(1) == 0, "enabling BD mid-step replayed a stale strike")
    passed("Rate and routing transitions reset owned voices and clear all twelve ports",
           rates=[44100,48000,96000], invalid_rate=12345,
           removed_sources_silent=True, no_stale_trigger_on_route_enable=True)

    # Exercise the compiled inlined Q15->binary32 path by asking a voice's
    # convex crossfade to emit a known signed-16 sample on its first call.
    # This avoids replacing/exporting the private conversion helper.
    m = machine()
    m.invoke("mx1_internal_routes",1)
    m.start_direct()
    m.render()
    values = set(range(-32768,32768,127)) | {0,-32768,32767,-1,1}
    for bit in range(16):
        for offset in (-1,0,1):
            for sign in (-1,1):
                value = sign*((1<<bit)+offset)
                if -32768 <= value <= 32767: values.add(value)
    for sample in sorted(values):
        voice = struct.pack("<6IhhI", 0,1230329,0,1,0x7FFFFFFF,1,0,sample,32)
        m.write(symbols["voices"],voice)
        m.render()
        expected = struct.unpack("<I",struct.pack("<f",sample/32768.0))[0]
        checked(m.port(1) == expected, "Q15-to-float conversion lost exactness")
    passed("Actual compiled Q15 conversion is exact at signs, normalization boundaries and dense samples",
           actual_compiled_samples=len(values), signed_range=[-32768,32767],
           expected="IEEE binary32 of signed sample / 32768", numerical_converter_stub=False)

    # Compare the displaced original prologues directly, not a recompiled
    # approximation. Equal initial register/stack values make nested argument
    # addresses comparable without normalizing away an ABI error.
    trampoline_cases = []
    routines = (("start",0x6000A7DC,"mx1_internal_start_original"),
                ("stop",0x6000A810,"mx1_internal_stop_original"),
                ("step",0x6000A894,"mx1_internal_step_original"))
    for name, address, trampoline in routines:
        variants = [(run,0,0,0) for run in (0,1)] if name != "step" else [
            (1,step,mask,chain) for step in (0,7,15)
            for mask in (0,0xFFFF) for chain in (0,1)]
        for run, step, mask, chain in variants:
            ref, new = machine(original), machine()
            for t in (ref,new):
                t.stub_native=True;t.native_mask=mask
                t.write(RUNNING,bytes([run]));t.put(RUNNING+12,7)
                t.write(0x604DF820+0xE0,bytes([chain]))
                for i in range(16): t.write(0x604DF820+0xE2+i*2,struct.pack("<h",i+100))
                t.write(0x604DF820+0x102,struct.pack("<h",3))
                for i,reg in enumerate(SAVED_REGS): t.uc.reg_write(reg,0xA5000000+i*0x101)
            ref.call(address,0x20011000,step)
            new.invoke(trampoline,0x20011000,step)
            checked(ref.native_calls == new.native_calls, "clock trampoline changed native calls")
            checked(ref.read(RUNNING,64) == new.read(RUNNING,64), "clock trampoline changed transport state")
            checked(ref.read(0x604DF820,0x200) == new.read(0x604DF820,0x200),
                    "clock trampoline changed native parameter state")
            for i,reg in enumerate(SAVED_REGS):
                checked(ref.uc.reg_read(reg) == new.uc.reg_read(reg) == 0xA5000000+i*0x101,
                        "clock trampoline clobbered a callee-saved register")
            trampoline_cases.append({"routine":name,"running":run,"native_step":step,
                                     "mask":mask,"chain":chain,"native_calls":len(ref.native_calls)})
    passed("Original transport/step trampolines preserve native calls, state, stack and callee-saved registers",
           cases=trampoline_cases, original_component="app_main",
           original_offsets=["0xa7dc","0xa810","0xa894"],
           original_runtime=["0x6000a7dc","0x6000a810","0x6000a894"],
           explicit_stubs={hex(k):v for k,v in NATIVE_STUBS.items()})

    return {"status":"pass", "hardware_access":False,
            "original_app_sha256":sha256(original),"patched_app_sha256":sha256(patched),
            "candidate_container_sha256":build["container_sha256"],
            "extension_sha256":build["extension_sha256"],"groups":groups,
            "limits":["Actual ARM instructions with explicit native transaction/BFX/timer-helper stubs in clock tests",
                      "Control-word publication is aligned; hardware scheduling and interrupt priority are not validated",
                      "No physical clock, DSP exchange arithmetic, audio, real-time cycle margin, installation or recovery validation"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("firmware",type=Path)
    parser.add_argument("--build",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    raw=args.firmware.read_bytes()
    checked(sha256(raw)==ORIGINAL_SHA256,"original firmware identity mismatch")
    original=component_unpacked(raw,COMPONENT_BY_NAME["app_main"])
    build=json.loads((args.build/"build-report.json").read_text())
    patched=(args.build/"app_main.mainline.bin").read_bytes()
    report=verify(original,patched,build,args.build/"mainline.elf")
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"groups":[g["name"] for g in report["groups"]]},indent=2))


if __name__=="__main__": main()
