#!/usr/bin/env python3
"""Build the sole MX-1 mainline routing and USB-B firmware candidate.

Only files are read/written. The exact stock input and every overwritten site
are guarded. USB-host unlocking is excluded. This never flashes a unit.
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

from firmware_patch import inject
from firmware_patch import exact_patch
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
    # Frozen storage contract: four reserved zero-default words in each block,
    # unchanged group lengths/slot counts and stock autosave policy.
    for offset, expected in (
        (0x684f0, struct.pack('<6I', 0x604f39a4, 2, 0x604f3e0c, 1, 0x604f4014, 66)),
        (0x6ed08, struct.pack('<4I', 0, 141, 1, 2)),
        (0x6ed28, struct.pack('<4I', 271, 268, 65, 1)),
        (0x686d8 + 0x10*16, bytes(64)),
        (0x686d8 + 0x182*16, struct.pack('<4I', 0, 0, 0, 0xa0200)*4),
        (0x56990, bytes.fromhex('c7f7f9fe')),
    ):
        if original[offset:offset+len(expected)] != expected:
            raise FormatError(f'Storage contract mismatch at app_main+{offset:#x}')
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "compiler-cache"
    cache.mkdir(exist_ok=True)
    env = dict(os.environ, ZIG_GLOBAL_CACHE_DIR=str(cache.resolve()),
               ZIG_LOCAL_CACHE_DIR=str(cache.resolve()))
    sources = [ROOT / "patches" / p for p in (
        "channel_routing_audio.c", "channel_routing_ui.c", "channel_routing_ui.S", "usb_audio.c")]
    from uac2_design import prototype_configuration
    config = prototype_configuration(preserve_modes=True)
    (out / "uac2_configuration.h").write_text("#define MX1_UAC2_CONFIGURATION_BYTES {" +
        ",".join(hex(b) for b in config) + "}\n")
    sources.append(ROOT / "sources/hardware/uac2_adapter.c")
    elf = out / "mainline.elf"
    command = [sys.executable, "-m", "ziglang", "build-exe", "-target",
               "thumb-freestanding-eabi", "-mcpu", "cortex_m3", "-O", "ReleaseSmall",
               "-fno-strip", "-fno-compiler-rt", "-fno-lto", "-fno-stack-protector",
               "-fentry=mx1_route_ui_event", "--script", str(ROOT / "patches/mainline.ld"),
               "-femit-bin=" + str(elf), "-I", str(ROOT / "patches"), "-I", str(out)]
    required = ("mx1_route_ui_event", "mx1_route_ui_display", "mx1_route_get",
                "mx1_route_adjust", "mx1_route_label", "mx1_route_recall", "mx1_uac2_initialize",
                "mx1_uac2_set_rate", "mx1_uac2_class_request", "mx1_uac2_start", *REQUIRED_SYMBOLS)
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
        if allocated != [".text", ".route_state", ".usb_data", ".usb_state"] or text["sh_type"] != "SHT_PROGBITS":
            raise FormatError("ELF contains allocated bytes outside the injected section")
        state = ef.get_section_by_name(".route_state")
        if (state["sh_type"] != "SHT_NOBITS" or state["sh_addr"] != 0x01017264
                or state["sh_size"] != 24 or state["sh_flags"] & 7 != 3):
            raise FormatError("Unexpected writable routing state reservation")
        usb_data = ef.get_section_by_name(".usb_data")
        usb_state = ef.get_section_by_name(".usb_state")
        if (usb_data["sh_addr"] != 0x0101727c or usb_data["sh_size"] != 356 or
            usb_data["sh_type"] != "SHT_PROGBITS" or usb_data["sh_flags"] & 7 != 3 or usb_data.data() != config + b'\0' or
            usb_state["sh_addr"] != 0x010173e0 or usb_state["sh_size"] != 20 or
            usb_state["sh_type"] != "SHT_NOBITS" or usb_state["sh_flags"] & 7 != 3):
            raise FormatError("Unexpected USB writable sections")
        descriptor_blob = usb_data.data()
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
        for name, address in (("mx1_route_state", 0x01017264), ("applied", 0x0101726f)):
            objects = table.get_symbol_by_name(name) or []
            if (len(objects) != 1 or objects[0]["st_value"] != address
                    or objects[0]["st_size"] != 11
                    or ef.get_section(objects[0]["st_shndx"]).name != ".route_state"):
                raise FormatError("Unexpected routing state object: " + name)
        for name, address, length, section in (
            ("route_ready", 0x0101727a, 1, ".route_state"),
            ("mx1_uac2_rate", 0x010173e0, 4, ".usb_state"),
            ("mx1_uac2_reply", 0x010173e4, 14, ".usb_state"),
            ("mx1_uac2_configuration", 0x0101727c, 355, ".usb_data")):
            objects = table.get_symbol_by_name(name) or []
            if (len(objects) != 1 or objects[0]["st_value"] != address or
                objects[0]["st_size"] != length or
                ef.get_section(objects[0]["st_shndx"]).name != section):
                raise FormatError("Unexpected USB state object: " + name)
        symbols = {s.name: s.entry["st_value"]
                   for s in table.iter_symbols()
                   if s.name.startswith("mx1_")}
    if not all(name in symbols for name in required):
        raise FormatError("Compiler omitted required routing exports")
    modified, scatter = inject(original, blob)
    cut = scatter['insert_offset'] + len(blob)
    modified[cut:cut] = descriptor_blob
    for update in scatter['startup_updates']:
        if update['offset'] == 0xe8: continue
        value = (0x60000000 + cut if update['offset'] == 0x114
                 else update['after'] + len(descriptor_blob))
        struct.pack_into('<I', modified, update['offset'], value)
        update['after'] = value
    scatter['code_length'] = len(blob)
    scatter['insert_length'] += len(descriptor_blob)
    blob += descriptor_blob
    changes: list[dict] = []
    # Original BSS ends exactly at the reserved state start. Extend only its
    # zero count, preserving every existing destination and allocator record.
    from memory_map import recover
    bss = recover(original)["operations"][3]
    if bss != {"call": 0x60000028, "kind": "zero", "destination": 0x01010088,
               "length": 0x71dc}:
        raise FormatError("Unexpected original writable SRAM BSS")
    exact_patch(modified, 0x108, struct.pack("<I", 0x71dc),
                struct.pack("<I", 0x736c), changes,
                "Zero 400-byte mainline writable state reservation after original writable SRAM BSS")
    exact_patch(modified, 0x10c, struct.pack('<I', 0x01020000), struct.pack('<I', 0x0101727c), changes,
                "Repurpose zero-length startup copy for writable USB descriptor")
    exact_patch(modified, 0x110, bytes(4), struct.pack('<I', 356), changes,
                "Initialize 356-byte USB descriptor storage after writable BSS clear")
    exact_patch(modified, 0xd980, bytes.fromhex('10b500f01ff80d48'),
                absolute_jump(0x6000d980, symbols['mx1_uac2_initialize']), changes, "USB-B UAC2 initializer")
    exact_patch(modified, 0xb4afc, struct.pack('<I', 0x600b499c),
                struct.pack('<I', symbols['mx1_uac2_configuration']), changes, "UAC2 configuration pointer")
    for offset in (0xb4984, 0xb4996):
        exact_patch(modified, offset, bytes.fromhex('ff00ff'), bytes.fromhex('ef0201'), changes, "UAC2 device association")
    exact_patch(modified, 0xda292, bytes.fromhex('4ff0000c'), bytes.fromhex('4ff0010c'), changes, "Capture-first priming")
    changes[-1]['runtime_address'] = 0x01009a06
    exact_patch(modified, 0x1e786, bytes.fromhex("3eb50c46002202216846"),
                absolute_jump(0x6001e786, symbols["mx1_route_recall"]), changes,
                "Scene recall routes and normal-boot latest-route restoration")
    patch_ui(modified, symbols, changes)
    audio = patch_audio(modified, symbols, changes)
    for change in changes:
        change["component"] = "app_main"
    rebuilt, container = repack_image(raw, {"app_main": bytes(modified)}, allow_resize=True)
    (out / "mainline.load.bin").write_bytes(blob)
    (out / "app_main.mainline.bin").write_bytes(modified)
    (out / "MXPLUS_MAINLINE_UNTESTED.bin").write_bytes(rebuilt)
    report = {
        "status": "OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED",
        "input_sha256": sha256(raw), "original_app_sha256": sha256(original),
        "patched_app_sha256": sha256(modified), "container_sha256": sha256(rebuilt),
        "extension_sha256": sha256(blob), "symbols": symbols,
        "compiler": "ziglang 0.13.0 Cortex-M3 ReleaseSmall, no LTO",
        "sources": {str(p.relative_to(ROOT)): sha256(p.read_bytes()) for p in [
            *sources, ROOT / "patches/channel_routing.h", ROOT / "patches/mainline.ld",
            Path(__file__).resolve(), ROOT / "tools/routing_audio_patch.py",
            ROOT / "tools/firmware_patch.py", ROOT / "tools/uac2_design.py"]},
        "scatter_extension": scatter, "patches": changes,
        "writable_state": {"start": 0x01017264, "size": 400, "end_exclusive": 0x010173f4, "startup_zero_length_offset": 0x108},
        "audio_routing": audio, "container": container,
        "sram_bytes_remaining": LIMIT - ENTRY - scatter['code_length'],
        "hardware_access": False,
        "limits": [
            "Routing predecessor passed user bench tests; combined USB-B mainline awaits hardware testing",
            "Routing and USB-B audio combined; USB-host application remains stock",
            "Real-time deadline margin and electrical/DMA behavior require hardware measurement",
        ],
    }
    (out / "build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("firmware", nargs="?", type=Path, default=ROOT / "inputs/MX1_UPD.original.bin")
    p.add_argument("--output", type=Path, default=ROOT / "build/mainline")
    a = p.parse_args()
    r = build(a.firmware, a.output)
    print(json.dumps({k: r[k] for k in ("status", "container_sha256", "symbols",
                    "scatter_extension", "patches", "sram_bytes_remaining")}, indent=2))


if __name__ == "__main__":
    main()
