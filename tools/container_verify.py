#!/usr/bin/env python3
"""Verify container code against the original Roland ARM decompressor.

Run with Python containing Unicorn: container_verify.py MX1_UPD.BIN --output report.json
This is isolated instruction emulation of one real firmware routine, not an
MX-1 hardware emulator. Wall time and instruction budget are not device cycles.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from container_tool import (
    BOOT_BASE, COMPONENTS, COMPONENT_BY_NAME, ORIGINAL_SHA256, FormatError,
    component_payload, component_unpacked, inspect_image, lzss_decode,
    lzss_encode_literals, repack_image, sha256,
)


def run_original_decoder(image: bytes, packed: bytes, output_size: int) -> bytes:
    """Call exact supplied boot-USB bytes at 0x0100052e under Cortex-M emulation."""
    import unicorn
    from unicorn.arm_const import (
        UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
        UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    )

    if sha256(image) != ORIGINAL_SHA256:
        raise FormatError("Decoder fixture must come from the exact supplied original")
    code = image[0x8030:0x9070]
    emulator = unicorn.Uc(unicorn.UC_ARCH_ARM,
                           unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
    emulator.mem_map(BOOT_BASE, 0x40000)
    emulator.mem_write(BOOT_BASE, code)
    source = 0x70000000
    target = 0x60000000
    sentinel = 0x0103FFF0
    # The actual routine fetches one additional literal/token before deciding
    # output is full. Real component slots have 0xff padding; model it here.
    input_bytes = packed + b"\xFF" * 0x1000
    emulator.mem_map(source, (len(input_bytes) + 0xFFF) & ~0xFFF)
    emulator.mem_write(source, input_bytes)
    emulator.mem_map(target, max(0x1000, (output_size + 0xFFF) & ~0xFFF))
    for register, value in (
        (UC_ARM_REG_SP, 0x0103F000), (UC_ARM_REG_LR, sentinel | 1),
        (UC_ARM_REG_R0, source), (UC_ARM_REG_R1, target),
        (UC_ARM_REG_R2, output_size),
    ):
        emulator.reg_write(register, value)
    emulator.emu_start(0x0100052F, sentinel, count=100_000_000)
    if emulator.reg_read(UC_ARM_REG_PC) != sentinel:
        raise AssertionError("Firmware decoder did not return within instruction budget")
    if emulator.reg_read(UC_ARM_REG_R0) != output_size:
        raise AssertionError("Firmware decoder returned an unexpected byte count")
    return bytes(emulator.mem_read(target, output_size))


def verify(image: bytes) -> dict:
    started = time.monotonic()
    checks = []
    metadata = inspect_image(image)
    if not metadata["is_supplied_original"]:
        raise FormatError("Verification fixture is not the supplied original firmware")
    checks.append({"name": "original hash and four stored-byte checksums", "passed": True})
    expected = {component.name: component_unpacked(image, component)
                for component in COMPONENTS}
    original_images = []
    for component in COMPONENTS:
        if not component.compressed:
            continue
        result = run_original_decoder(image, component_payload(image, component),
                                      len(expected[component.name]))
        if result != expected[component.name]:
            raise AssertionError(f"{component.name}: Python and firmware decoders differ")
        original_images.append({"name": component.name, "bytes": len(result),
                                "sha256": sha256(result)})
    checks.append({"name": "three original LZSS images match actual firmware decoder",
                   "passed": True, "images": original_images})

    rebuilt, report = repack_image(image, expected)
    if rebuilt != image or not report["byte_identical_to_original"]:
        raise AssertionError("No-op unpack/repack was not byte-identical")
    checks.append({"name": "full original extraction and no-op rebuild is byte-identical",
                   "passed": True, "sha256": sha256(rebuilt)})

    synthetic_results = []
    for name in ("app_main", "app_usb"):
        altered = bytearray(expected[name])
        # Synthetic codec fixture only. Never written to a firmware file and
        # deliberately unrelated to any proposed working feature patch.
        altered[0x123] ^= 0x80
        altered = bytes(altered)
        packed_image, patch_report = repack_image(image, {name: altered})
        component = COMPONENT_BY_NAME[name]
        firmware_result = run_original_decoder(
            image, component_payload(packed_image, component), len(altered))
        if firmware_result != altered:
            raise AssertionError(f"{name}: actual firmware rejected literal-only codec")
        if packed_image[:0x10000] != image[:0x10000] or packed_image[0x400000:] != image[0x400000:]:
            raise AssertionError("Boot images or trailer changed")
        for other in COMPONENTS:
            if other.name != name and packed_image[other.offset:other.slot_end] != image[other.offset:other.slot_end]:
                raise AssertionError(f"Unrelated {other.name} component changed")
        synthetic_results.append({
            "component": name,
            "stored_bytes": len(component_payload(packed_image, component)),
            "remaining_slot_bytes": component.slot_end - component.offset - 64 - len(component_payload(packed_image, component)),
            "actual_firmware_decoder_matches": True,
        })
    checks.append({"name": "literal-only repack with synthetic mutation; actual firmware decoder matches; untouched regions preserved",
                   "passed": True, "fixtures": synthetic_results,
                   "note": "Synthetic mutated images are not saved or offered for flashing"})

    resized = expected["app_usb"] + bytes(range(32))
    try:
        repack_image(image, {"app_usb": resized})
        raise AssertionError("Decoded application resize was silently allowed")
    except FormatError:
        pass
    resized_image, _ = repack_image(image, {"app_usb": resized}, allow_resize=True)
    actual_resized = run_original_decoder(image,
        component_payload(resized_image, COMPONENT_BY_NAME["app_usb"]), len(resized))
    if actual_resized != resized:
        raise AssertionError("Original decoder did not accept explicitly resized application")
    checks.append({"name": "decoded size change requires explicit opt-in and original decoder accepts resized codec fixture",
                   "passed": True, "added_bytes": 32,
                   "note": "Codec-only append fixture; runtime scatter-loader correctness remains caller responsibility"})

    corrupted = bytearray(image)
    corrupted[0x80040] ^= 1
    try:
        inspect_image(bytes(corrupted))
        raise AssertionError("Checksum corruption was accepted")
    except FormatError:
        pass
    checks.append({"name": "corrupted compressed byte is rejected by checksum validation", "passed": True})

    malformed = ((b"", 1), (b"\x01", 1), (b"\x00\x00", 3),
                 (b"\x00\xEE\xF0", 3), (b"\x01A\x00", 1),
                 (b"\x00\x00\x00", 2))
    for stream, length in malformed:
        try:
            lzss_decode(stream, length)
            raise AssertionError(f"Malformed stream accepted: {stream.hex()}")
        except FormatError:
            pass
    checks.append({"name": "truncated, oversized, trailing-data and uninitialized-ring streams rejected",
                   "passed": True, "fixtures": len(malformed)})

    # An unchanged updater is preserved and fits. Literal-only replacement of
    # this densely packed slot must fail before an image can be emitted.
    oversized_updater = bytearray(expected["updater"])
    oversized_updater[0] ^= 1
    try:
        repack_image(image, {"updater": bytes(oversized_updater)})
        raise AssertionError("Updater slot overflow was accepted")
    except FormatError:
        pass
    checks.append({"name": "encoded component slot overflow rejected", "passed": True})

    return {
        "status": "passed",
        "input_sha256": sha256(image),
        "check_groups": len(checks),
        "checks": checks,
        "host_wall_seconds": round(time.monotonic() - started, 3),
        "emulation_scope": "Unmodified Roland boot-USB LZSS decoder only",
        "hardware_emulated": False,
        "silicon_cycle_measurement": False,
        "flash_acceptance_or_audio_functionality_tested": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.input.read_bytes())
    rendered = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
