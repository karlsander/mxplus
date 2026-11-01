#!/usr/bin/env python3
"""Build the independent, untested MX-1 channel-routing firmware experiment.

Only files are read/written. The exact stock input and every overwritten site
are guarded. This does not combine the earlier USB experiments or flash a unit.
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

from build_device_probe import inject
from build_host_probe import exact_patch
from container_tool import (COMPONENT_BY_NAME, ORIGINAL_SHA256, FormatError,
                            component_unpacked, repack_image, sha256)

ROOT = Path(__file__).resolve().parents[1]
ENTRY = 0x0100F6A4
LIMIT = 0x01010000


def absolute_jump(address: int, target: int) -> bytes:
    """Flag/register-preserving Thumb veneer with a word-aligned literal."""
    if address & 1:
        raise FormatError("Patch instruction address must be even")
    prefix = b"\x00\xbf" if address & 2 else b""
    return prefix + bytes.fromhex("dff800f0") + struct.pack("<I", target | 1)


def patch_ui(image: bytearray, symbols: dict, changes: list) -> None:
    exact_patch(image, 0xF5D8, struct.pack("<I", 0x60010B49),
                struct.pack("<I", symbols["mx1_route_ui_event"] | 1), changes,
                "Panel event callback: hold SELECT and turn TEMPO")
    exact_patch(image, 0x13356, bytes.fromhex("feb50446c54804f07cff"),
                absolute_jump(0x60013356, symbols["mx1_route_ui_display"]), changes,
                "Tempo display overlay with relocated original prologue")


def build(firmware: Path, out: Path) -> dict:
    raw = firmware.read_bytes()
    if sha256(raw) != ORIGINAL_SHA256:
        raise FormatError("Original firmware SHA-256 mismatch")
    # Import after identity validation; --help and bad-input rejection need no
    # generated routing data or compiler installation.
    from routing_audio_patch import REQUIRED_SYMBOLS, patch_audio
    original = component_unpacked(raw, COMPONENT_BY_NAME["app_main"])
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "compiler-cache"
    cache.mkdir(exist_ok=True)
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(cache.resolve()),
               ZIG_LOCAL_CACHE_DIR=str(cache.resolve()))
    sources = [ROOT / "patches" / p for p in (
        "channel_routing_audio.c", "channel_routing_ui.c", "channel_routing_ui.S")]
    elf = out / "channel_routing.elf"
    command = [sys.executable, "-m", "ziglang", "build-exe", "-target",
               "thumb-freestanding-eabi", "-mcpu", "cortex_m3", "-O", "ReleaseSmall",
               "-fno-strip", "-fno-compiler-rt", "-fno-lto", "-fno-stack-protector",
               "-fentry=mx1_route_ui_event", "--script", str(ROOT / "patches/channel_routing.ld"),
               "-femit-bin=" + str(elf), "-I", str(ROOT / "patches")]
    required = ("mx1_route_ui_event", "mx1_route_ui_display", "mx1_route_get",
                "mx1_route_adjust", "mx1_route_label", *REQUIRED_SYMBOLS)
    for name in required:
        command += ["--force_undefined", name]
    command += ["-cflags", "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "--"]
    command += [str(p) for p in sources]
    subprocess.run(command, check=True, env=env)
    with elf.open("rb") as f:
        ef = ELFFile(f)
        text = ef.get_section_by_name(".text")
        if text is None or text["sh_addr"] != ENTRY:
            raise FormatError("Routing extension link address mismatch")
        blob = text.data()
        if not blob or len(blob) % 4 or ENTRY + len(blob) > LIMIT:
            raise FormatError("Routing extension exceeds reviewed SRAM interval")
        if any(s["sh_type"] in ("SHT_REL", "SHT_RELA") for s in ef.iter_sections()):
            raise FormatError("Unresolved extension relocation")
        allocated = [s.name for s in ef.iter_sections()
                     if s["sh_flags"] & 2 and s["sh_size"]]
        if allocated != [".text"] or text["sh_type"] != "SHT_PROGBITS":
            raise FormatError("ELF contains allocated bytes outside the injected section")
        table = ef.get_section_by_name(".symtab")
        for name in required:
            matches = table.get_symbol_by_name(name) or []
            if len(matches) != 1:
                raise FormatError("Missing or ambiguous routing export: " + name)
            symbol = matches[0]
            if (symbol["st_info"]["type"] != "STT_FUNC" or
                not isinstance(symbol["st_shndx"], int) or
                ef.get_section(symbol["st_shndx"]).name != ".text" or
                not ENTRY <= (symbol["st_value"] & ~1) < ENTRY + len(blob)):
                raise FormatError("Routing function lies outside injected section: " + name)
        symbols = {s.name: s.entry["st_value"]
                   for s in table.iter_symbols()
                   if s.name.startswith("mx1_")}
    if not all(name in symbols for name in required):
        raise FormatError("Compiler omitted required routing exports")
    modified, scatter = inject(original, blob)
    changes: list[dict] = []
    patch_ui(modified, symbols, changes)
    audio = patch_audio(modified, symbols, changes)
    for change in changes:
        change["component"] = "app_main"
    rebuilt, container = repack_image(raw, {"app_main": bytes(modified)}, allow_resize=True)
    (out / "channel_routing.code.bin").write_bytes(blob)
    (out / "app_main.routing.bin").write_bytes(modified)
    (out / "MX1_CHANNEL_ROUTING_UNTESTED.bin").write_bytes(rebuilt)
    report = {
        "status": "OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED",
        "input_sha256": sha256(raw), "original_app_sha256": sha256(original),
        "patched_app_sha256": sha256(modified), "container_sha256": sha256(rebuilt),
        "extension_sha256": sha256(blob), "symbols": symbols,
        "compiler": "ziglang 0.13.0 Cortex-M3 ReleaseSmall, no LTO",
        "sources": {str(p.relative_to(ROOT)): sha256(p.read_bytes()) for p in [
            *sources, ROOT / "patches/channel_routing.h", ROOT / "patches/channel_routing.ld",
            Path(__file__).resolve(), ROOT / "tools/routing_audio_patch.py"]},
        "scatter_extension": scatter, "patches": changes,
        "audio_routing": audio, "container": container,
        "sram_bytes_remaining": LIMIT - ENTRY - len(blob),
        "hardware_access": False,
        "limits": [
            "No physical MX-1 flashing, recovery, audio or UI validation",
            "Standalone main-application experiment; no UAC1-host or UAC2-device changes",
            "Real-time deadline margin and electrical/DMA behavior require hardware measurement",
        ],
    }
    (out / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("firmware", type=Path)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    r = build(a.firmware, a.output)
    print(json.dumps({k: r[k] for k in ("status", "container_sha256", "symbols",
                    "scatter_extension", "patches", "sram_bytes_remaining")}, indent=2))


if __name__ == "__main__":
    main()
