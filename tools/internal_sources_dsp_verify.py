#!/usr/bin/env python3
"""Check the actual integer source engine; no firmware MMIO or hardware I/O.

Host numerical sweeps and actual Cortex-M3 instructions are compared. Counts
are executed instructions, not cycles or a measured MX-1 real-time budget.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import wave

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "patches/internal_sources_dsp.c"
HEADER = ROOT / "patches/internal_sources_dsp.h"
CODE = 0x01000000
RAM = 0x20000000
VOICE = RAM
PCM = RAM + 0x100
STOP = CODE + 0xFFF0


class Voice(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "phase", "step", "bend", "bend_drop", "envelope", "envelope_drop")]
    _fields_ += [("last", ctypes.c_int16), ("previous", ctypes.c_int16),
                ("crossfade", ctypes.c_uint32)]


def checked(condition: bool, reason: str) -> None:
    if not condition:
        raise AssertionError(reason)


def compile_engines(directory: Path) -> tuple[ctypes.CDLL, Path, dict]:
    # These loops are test helpers only; the candidate links the engine itself.
    wrapper = directory / "wrapper.c"
    wrapper.write_text('''#include "internal_sources_dsp.h"
void kick_fill(mxkick_voice *v, short *out, unsigned n) {
    for (unsigned i=0; i<n; ++i) out[i]=mxkick_next(v);
}
void noise_fill(unsigned *v, short *out, unsigned n) {
    for (unsigned i=0; i<n; ++i) out[i]=mxnoise_next(v);
}
''')
    library = directory / "engine.so"
    subprocess.run(["gcc", "-std=c11", "-O2", "-shared", "-fPIC",
                    "-Wall", "-Wextra", "-Werror", "-fsanitize=undefined",
                    "-fno-sanitize-recover=undefined", "-I", str(HEADER.parent),
                    str(SOURCE), str(wrapper), "-o", str(library)], check=True)
    host = ctypes.CDLL(str(library))
    vp = ctypes.POINTER(Voice)
    host.mxkick_trigger.argtypes = [vp, ctypes.c_uint32, ctypes.c_int32, ctypes.c_uint32]
    host.mxkick_trigger.restype = ctypes.c_int
    host.mxkick_reset.argtypes = [vp]
    host.mxkick_next.argtypes = [vp]
    host.mxkick_next.restype = ctypes.c_int16
    host.mxnoise_next.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
    host.mxnoise_next.restype = ctypes.c_int16
    host.kick_fill.argtypes = [vp, ctypes.POINTER(ctypes.c_int16), ctypes.c_uint32]
    host.noise_fill.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_int16), ctypes.c_uint32]

    script = directory / "engine.ld"
    script.write_text('''ENTRY(mxkick_trigger)
SECTIONS {
  . = 0x01000000;
  .text : { *(.text*) *(.rodata*) . = ALIGN(4); }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.eh_frame*) }
}
''')
    elf = directory / "engine.elf"
    cache = directory / "zigcache"
    cache.mkdir()
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(cache), ZIG_LOCAL_CACHE_DIR=str(cache))
    command = [sys.executable, "-m", "ziglang", "build-exe", "-target",
               "thumb-freestanding-eabi", "-mcpu", "cortex_m3", "-O", "ReleaseSmall",
               "-fno-strip", "-fno-compiler-rt", "-fno-lto", "-fno-stack-protector",
               "-fentry=mxkick_trigger", "--script", str(script), "-femit-bin=" + str(elf),
               "-I", str(HEADER.parent)]
    for name in ("mxkick_trigger", "mxkick_reset", "mxkick_next", "mxnoise_next",
                 "kick_fill", "noise_fill"):
        command += ["--force_undefined", name]
    command += ["-cflags", "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "--",
                str(SOURCE), str(wrapper)]
    subprocess.run(command, env=env, check=True)
    with elf.open("rb") as f:
        e = ELFFile(f)
        symbols = e.get_section_by_name(".symtab")
        checked(not any(s.name and s["st_shndx"] == "SHN_UNDEF"
                        for s in symbols.iter_symbols()), "undefined ARM symbol")
        sizes = {s.name: s["st_size"] for s in symbols.iter_symbols()
                 if s["st_info"]["type"] == "STT_FUNC"}
        metadata = {"compiler_target": "Cortex-M3 Thumb, ReleaseSmall, ziglang 0.13.0",
                    "voice_bytes": ctypes.sizeof(Voice),
                    "function_bytes": sizes,
                    "engine_functions_and_tables_bytes":
                    sum(s["st_size"] for s in symbols.iter_symbols()
                        if s.name not in ("kick_fill", "noise_fill")
                        and s["st_info"]["type"] in ("STT_FUNC", "STT_OBJECT"))}
    return host, elf, metadata


class ArmEngine:
    def __init__(self, elf: Path):
        self.u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        self.u.mem_map(CODE, 0x10000)
        self.u.mem_map(RAM, 0x10000)
        with elf.open("rb") as f:
            e = ELFFile(f)
            for section in e.iter_sections():
                if section["sh_flags"] & 2 and section["sh_size"]:
                    self.u.mem_write(section["sh_addr"], section.data())
            self.symbols = {s.name: s["st_value"] for s in
                            e.get_section_by_name(".symtab").iter_symbols()}

    def call(self, name: str, *args: int, measured: bool = False) -> tuple[int, int]:
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3), args):
            self.u.reg_write(reg, value & 0xFFFFFFFF)
        self.u.reg_write(UC_ARM_REG_SP, RAM + 0xFFF0)
        self.u.reg_write(UC_ARM_REG_LR, STOP | 1)
        count = 0

        def instruction(_u, _address, _size, _data):
            nonlocal count
            count += 1

        hook = self.u.hook_add(UC_HOOK_CODE, instruction) if measured else None
        if measured:
            # Unicorn's already translated blocks can predate a newly added
            # code hook. Invalidate them so every measured instruction counts.
            self.u.ctl_remove_cache(CODE, CODE + 0x10000)
        self.u.emu_start(self.symbols[name] | 1, STOP, count=2000000)
        if hook is not None:
            self.u.hook_del(hook)
            self.u.ctl_remove_cache(CODE, CODE + 0x10000)
        checked(self.u.reg_read(UC_ARM_REG_PC) == STOP, "ARM instruction exhaustion")
        checked(self.u.reg_read(UC_ARM_REG_SP) == RAM + 0xFFF0, "ARM stack imbalance")
        return self.u.reg_read(UC_ARM_REG_R0), count


def render(host, voice: Voice, frames: int) -> bytes:
    data = (ctypes.c_int16 * frames)()
    host.kick_fill(ctypes.byref(voice), data, frames)
    return bytes(data)


def verify(directory: Path, preview: Path | None = None) -> dict:
    host, elf, build = compile_engines(directory)
    arm = ArmEngine(elf)
    report = {"status": "passed", "hardware_access": False,
              "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "header_sha256": hashlib.sha256(HEADER.read_bytes()).hexdigest(),
              "build": build,
              "limits": "Numerical PCM and executed ARM instructions only; no DSP exchange, audio clock, physical sound or cycle measurements."}
    max_cents = 0.0
    decays = []
    for rate in (44100, 48000, 96000):
        for semitone in range(-24, 25):
            v = Voice()
            checked(host.mxkick_trigger(ctypes.byref(v), rate, semitone, 53) == 1,
                    "supported pitch/rate rejected")
            actual = v.step * rate / 2**32
            desired = 55 * 2**(semitone / 12)
            cents = abs(1200 * math.log2(actual / desired))
            checked(cents < 0.01, "pitch error exceeds .01 cents")
            max_cents = max(max_cents, cents)
        for decay in (0, 25, 53, 75, 100):
            for semitone in (-24, -12, 0, 12, 24):
                v = Voice()
                host.mxkick_trigger(ctypes.byref(v), rate, semitone, decay)
                ms = 30 + (decay**3 * 1470 + 500000) // 1000000
                pcm = render(host, v, rate * ms // 1000)
                samples = struct.unpack("<" + "h" * (len(pcm) // 2), pcm)
                peak = max(map(abs, samples))
                checked(1000 < peak <= 16384, "kick peak outside bounded musical range")
                db = 20 * math.log10(v.envelope / 0x7FFFFFFF)
                checked(-60.8 < db < -59.5, "T60 envelope mismatch")
                render(host, v, rate * 3)
                checked(v.envelope == 0 and host.mxkick_next(ctypes.byref(v)) == 0,
                        "finite kick failed to become exact silence")
                decays.append({"rate": rate, "semitone": semitone, "decay": decay,
                               "t60_ms": ms, "envelope_db_at_t60": round(db, 4), "peak": peak})
    report["pitch"] = {"cases": 147, "maximum_cents_error": max_cents,
                       "reference_hz": 55, "semitones": [-24, 24]}
    report["envelope_cases"] = decays

    # Reject wrong rates before writing anything; clamp controls coherently.
    v = Voice()
    host.mxkick_trigger(ctypes.byref(v), 48000, 0, 53)
    render(host, v, 123)
    before = bytes(v)
    checked(not host.mxkick_trigger(ctypes.byref(v), 32000, 0, 53), "bad rate accepted")
    checked(bytes(v) == before, "bad rate mutated voice")
    for pitch, decay, expected_pitch, expected_decay in ((-999, 999, -24, 100), (999, 0, 24, 0)):
        a, b = Voice(), Voice()
        host.mxkick_trigger(ctypes.byref(a), 48000, pitch, decay)
        host.mxkick_trigger(ctypes.byref(b), 48000, expected_pitch, expected_decay)
        checked(bytes(a) == bytes(b), "control clamp mismatch")
    host.mxkick_reset(ctypes.byref(v))
    checked(bytes(v) == bytes(ctypes.sizeof(v)), "reset failed to clear voice")

    # Repeated triggers must preserve the last sample and remain amplitude
    # bounded even when each new strike interrupts a crossfade already running.
    v = Voice()
    trigger_cases = 0
    for gap in (1, 2, 4, 16, 31, 32, 64, 257):
        for hit in range(32):
            previous = v.last
            host.mxkick_trigger(ctypes.byref(v), 48000, (hit % 49) - 24, 100)
            checked(host.mxkick_next(ctypes.byref(v)) == previous,
                    "retrigger created an immediate sample discontinuity")
            pcm = render(host, v, gap)
            checked(max(map(abs, struct.unpack("<" + "h" * gap, pcm))) <= 16384,
                    "retrigger exceeded amplitude bound")
            trigger_cases += 1
    report["retrigger"] = {"cases": trigger_cases, "crossfade_samples": 32,
                           "first_sample_equals_previous": True, "bounded": True}

    # Uniform white pseudo-noise: deterministic xorshift32, independent of
    # kick state, one sample per call. Statistical checks catch signedness,
    # stale-sample and severe correlation regressions, not physical audio.
    seed = ctypes.c_uint32(1)
    count = 1000000
    data = (ctypes.c_int16 * count)()
    host.noise_fill(ctypes.byref(seed), data, count)
    values = list(data)
    mean = sum(values) / count
    square = sum(x*x for x in values)
    rms = math.sqrt(square / count)
    rho = sum(a*b for a, b in zip(values, values[1:])) / square
    checked(min(values) == -8192 and max(values) == 8191, "noise range mismatch")
    checked(abs(mean) < 20 and 4700 < rms < 4760 and abs(rho) < .005,
            "noise uniformity/correlation check failed")
    report["noise"] = {"samples": count, "seed": 1, "mean": mean,
                       "rms": rms, "lag1_correlation": rho,
                       "pcm_sha256": hashlib.sha256(bytes(data)).hexdigest()}

    # A real compiled Thumb block must produce exactly the host PCM and state;
    # no numerical conversions, PRNG or synthesis calls are stubbed here.
    vectors = []
    for rate in (44100, 48000, 96000):
        for pitch, decay in ((-24, 0), (0, 53), (24, 100)):
            v = Voice()
            arm.u.mem_write(VOICE, bytes(ctypes.sizeof(v)))
            host.mxkick_trigger(ctypes.byref(v), rate, pitch, decay)
            arm.call("mxkick_trigger", VOICE, rate, pitch, decay)
            checked(bytes(arm.u.mem_read(VOICE, ctypes.sizeof(v))) == bytes(v), "ARM trigger differs")
            pcm = render(host, v, 4096)
            arm.call("kick_fill", VOICE, PCM, 4096)
            checked(bytes(arm.u.mem_read(PCM, len(pcm))) == pcm, "ARM kick PCM differs")
            checked(bytes(arm.u.mem_read(VOICE, ctypes.sizeof(v))) == bytes(v), "ARM kick state differs")
            vectors.append({"rate": rate, "semitone": pitch, "decay": decay,
                            "frames": 4096, "pcm_sha256": hashlib.sha256(pcm).hexdigest()})
    for seed_value in (0, 1, 0x80000000, 0xFFFFFFFF):
        seed = ctypes.c_uint32(seed_value)
        data = (ctypes.c_int16 * 4096)()
        host.noise_fill(ctypes.byref(seed), data, 4096)
        arm.u.mem_write(VOICE, struct.pack("<I", seed_value))
        arm.call("noise_fill", VOICE, PCM, 4096)
        checked(bytes(arm.u.mem_read(PCM, 8192)) == bytes(data), "ARM noise PCM differs")
        checked(struct.unpack("<I", arm.u.mem_read(VOICE, 4))[0] == seed.value,
                "ARM noise state differs")
    report["actual_thumb"] = {"kick_vectors": vectors, "noise_vectors": 4,
                              "host_pcm_and_state_identical": True, "stubs": []}

    instruction_counts = {}
    arm.u.mem_write(VOICE, bytes(ctypes.sizeof(Voice)))
    for label, setup in (("silent", None), ("onset", (48000, 0, 53)),
                         ("onset_low_pitch", (48000, -24, 53)),
                         ("onset_high_pitch", (48000, 24, 53))):
        if setup:
            arm.call("mxkick_trigger", VOICE, *setup)
        instruction_counts[label] = arm.call("mxkick_next", VOICE, measured=True)[1]
    arm.call("mxkick_trigger", VOICE, 48000, 0, 100)
    arm.call("kick_fill", VOICE, PCM, 64)
    instruction_counts["active_pitch_sweep"] = arm.call("mxkick_next", VOICE, measured=True)[1]
    arm.call("kick_fill", VOICE, PCM, 12000)
    instruction_counts["active_settled_pitch"] = arm.call("mxkick_next", VOICE, measured=True)[1]
    instruction_counts["reset"] = arm.call("mxkick_reset", VOICE, measured=True)[1]
    arm.u.mem_write(VOICE, struct.pack("<I", 1))
    instruction_counts["noise"] = arm.call("mxnoise_next", VOICE, measured=True)[1]
    arm.u.mem_write(VOICE, struct.pack("<I", 0))
    instruction_counts["noise_zero_seed_recovery"] = arm.call("mxnoise_next", VOICE, measured=True)[1]
    report["executed_instruction_counts"] = instruction_counts
    report["executed_instruction_counts_scope"] = "One engine call including function entry/return, excluding caller, IRQ, routing, conversion and DSP writes; not cycles."

    if preview:
        preview.parent.mkdir(parents=True, exist_ok=True)
        pcm = bytearray()
        v = Voice()
        for pitch, decay in ((0, 20), (0, 53), (0, 85), (-12, 53), (12, 53)):
            host.mxkick_trigger(ctypes.byref(v), 48000, pitch, decay)
            pcm += render(host, v, 48000)
        with wave.open(str(preview), "wb") as wav:
            wav.setparams((1, 2, 48000, 0, "NONE", "not compressed"))
            wav.writeframes(pcm)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--preview-wav", type=Path,
                        help="Optional numerical preview, never a mixer recording")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="mxplus-sources-") as temporary:
        report = verify(Path(temporary), args.preview_wav)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    print("Internal source engine passed: 147 pitches, 75 envelopes, 256 retriggers, "
          "1M noise samples, 13 actual-Thumb PCM vectors.")
    print("Executed instructions (not cycles): " + json.dumps(report["executed_instruction_counts"]))


if __name__ == "__main__":
    main()
