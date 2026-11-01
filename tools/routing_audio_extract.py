#!/usr/bin/env python3
"""Reconstruct ESC2 instruction memories through the original ARM uploader.

This executes original Thumb descriptor arithmetic and boundary writes. DMA is
an explicit byte-copy model, not an emulation of ESC2 DSP arithmetic or timing.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
)

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b"
RETURN = 0x0100F680


def reconstruct(tables=(0x600BA008, 0x600BBED0), counts=(18, 18)) -> tuple[dict, list[bytes]]:
    blob = (ROOT / "analysis/container_app_main.bin").read_bytes()
    assert hashlib.sha256(blob).hexdigest() == EXPECTED
    mapping = json.loads((ROOT / "analysis/map-main.json").read_text())
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for base, size in ((0x01000000, 0x30000), (0x20000000, 0x20000),
                       (0x40100000, 0x80000), (0x60000000, 0x700000)):
        uc.mem_map(base, size)
    uc.mem_write(0x60000000, blob)
    for op in mapping["operations"]:
        if op["kind"] == "copy" and op["length"]:
            offset = op["source"] - 0x60000000
            uc.mem_write(op["destination"], blob[offset:offset + op["length"]])
    command = 0
    trace = []

    def word(address):
        return struct.unpack("<I", uc.mem_read(address, 4))[0]

    def write_hook(engine, access, address, size, value, user):
        nonlocal command
        if address == 0x40100900:
            command = value
        elif address == 0x40100904:
            assert (command >> 28) == 2, hex(command)
            destination = 0x40100000 + (command & 0xFFFFF)
            assert destination % 4 == 0
            engine.mem_write(destination, struct.pack("<I", value))
            trace.append({"type": "original_boundary_write", "destination": destination,
                          "value": value})

    def code_hook(engine, address, size, user):
        # Original uploader has already selected the destination and trimmed
        # partial edge words. Only its bulk DMA transport is modeled.
        if address in (0x0100A90E, 0x0100A9E8):
            core = engine.reg_read(UC_ARM_REG_R1)
            offset = engine.reg_read(UC_ARM_REG_R2) * 4
            length = engine.reg_read(UC_ARM_REG_R3)
            source = word(engine.reg_read(UC_ARM_REG_SP))
            assert core in (0, 1)
            destination = (0x40150000 if core == 0 else 0x40170000) + offset
            assert offset + length <= 0x8000
            engine.mem_write(destination, bytes(engine.mem_read(source, length)))
            trace.append({"type": "modeled_dma", "source": source,
                          "destination": destination, "length": length})
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.hook_add(UC_HOOK_CODE, code_hook)
    chunks = []
    for core, table in enumerate(tables):
        for index in range(counts[core]):
            offset, length, source = struct.unpack("<III", uc.mem_read(table + index * 12, 12))
            chunks.append({"core": core, "index": index, "program_offset": offset,
                           "length": length, "source": source})
            for reg, value in ((UC_ARM_REG_R0, 0x20000B24), (UC_ARM_REG_R1, core),
                               (UC_ARM_REG_R2, index), (UC_ARM_REG_R3, table),
                               (UC_ARM_REG_SP, 0x2001FF00), (UC_ARM_REG_LR, RETURN | 1)):
                uc.reg_write(reg, value)
            uc.emu_start(0x0100BFE3, RETURN, count=10000)
            assert uc.reg_read(UC_ARM_REG_PC) == RETURN
            assert uc.reg_read(UC_ARM_REG_SP) == 0x2001FF00
    images = [bytes(uc.mem_read(base, 0x8000)) for base in (0x40150000, 0x40170000)]
    report = {
        "source_sha256": EXPECTED,
        "executed": ["0x0100bfe2 descriptor wrapper", "0x0100ab32 uploader",
                     "0x0100ab04 original boundary-write helper"],
        "modeled": ["bulk DMA byte copying", "DSP programming-command storage semantics"],
        "not_tested": ["DSP instruction execution", "DMA or DSP timing", "physical audio"],
        "chunks": chunks, "transport_trace": trace,
        "instruction_memory_sha256": [hashlib.sha256(x).hexdigest() for x in images],
    }
    return report, images


def main():
    report, images = reconstruct()
    out = ROOT / "analysis/routing-audio"
    out.mkdir(parents=True, exist_ok=True)
    (out / "program-upload.json").write_text(json.dumps(report, indent=2) + "\n")
    for core, image in enumerate(images):
        (out / f"dsp{core}-program.bin").write_bytes(image)
        # ESC2 program halfwords address the high half of each CPU-visible
        # little-endian word first; boundary uploads establish this ordering.
        logical = b"".join(struct.pack(">I", value) for value in struct.unpack("<8192I", image))
        (out / f"dsp{core}-program-halfwords.txt").write_text("".join(
            f"{offset:04x}: " + " ".join(f"{v:04x}" for v in struct.unpack_from(">8H", logical, offset)) + "\n"
            for offset in range(0, len(logical), 16)))
    print(json.dumps({"original_upload_chunks": len(report["chunks"]),
                      "instruction_memory_sha256": report["instruction_memory_sha256"]}))


if __name__ == "__main__":
    main()
