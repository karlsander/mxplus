#!/usr/bin/env python3
"""Reproducible MX-1 1.05 update-container inspection and experimental repacking.

This tool does not communicate with hardware. Its checksum and LZSS support is
verified against the supplied firmware; it does not certify a patched image for
flashing. Unknown boot-header fields and the update plan are preserved exactly.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path

ORIGINAL_SHA256 = "26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e"
IMAGE_SIZE = 0x400010
FLASH_SIZE = 0x400000
HEADER_SIZE = 0x40
BOOT_HEADER_SIZE = 0x30
BOOT_BASE = 0x01000000
RING_SIZE = 4096
RING_START = 4096 - 18


class FormatError(ValueError):
    """A precondition for this particular firmware format was not met."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


@dataclass(frozen=True)
class Component:
    name: str
    offset: int
    slot_end: int
    tag: bytes
    compressed: bool


COMPONENTS = (
    Component("updater", 0x10000, 0x40000, b"PX-11:Updater   ", True),
    Component("subcpu", 0x40000, 0x80000, b"PX-11:SUB-CPU   ", False),
    Component("app_main", 0x80000, 0x200000, b"PX-11:Appli     ", True),
    # The trailer ends writes at 0x300000. The remaining MiB is not part of the
    # application's writable slot even though the distributed image is erased.
    Component("app_usb", 0x200000, 0x300000, b"PX-11:Appli     ", True),
)
COMPONENT_BY_NAME = {component.name: component for component in COMPONENTS}


def lzss_decode(data: bytes, expected_size: int) -> bytes:
    """Decode Roland's zero-initialized Okumura-style LZSS stream.

    Unlike a permissive file carver, reject truncated/overlong streams and any
    reference to the last 18 initial ring bytes before they have been written.
    The firmware initializes only ring[0:4078]; those other bytes are undefined.
    """
    if expected_size < 0 or expected_size > 32 * 1024 * 1024:
        raise FormatError("Implausible decoded size")
    ring = bytearray(RING_SIZE)
    defined = bytearray(b"\x01" * RING_START + b"\x00" * 18)
    cursor = RING_START
    output = bytearray()
    source = 0

    def emit(value: int) -> None:
        nonlocal cursor
        if len(output) >= expected_size:
            raise FormatError("LZSS token exceeds declared decoded length")
        output.append(value)
        ring[cursor] = value
        defined[cursor] = 1
        cursor = (cursor + 1) & (RING_SIZE - 1)

    while len(output) < expected_size:
        if source >= len(data):
            raise FormatError("LZSS stream ended before its flag byte")
        flags = data[source]
        source += 1
        for bit in range(8):
            if len(output) == expected_size:
                break
            if flags & (1 << bit):
                if source >= len(data):
                    raise FormatError("Truncated LZSS literal")
                emit(data[source])
                source += 1
            else:
                if source + 2 > len(data):
                    raise FormatError("Truncated LZSS back-reference")
                first, second = data[source:source + 2]
                source += 2
                position = first | ((second & 0xF0) << 4)
                length = (second & 0x0F) + 3
                for index in range(length):
                    address = (position + index) & (RING_SIZE - 1)
                    if not defined[address]:
                        raise FormatError("LZSS reads uninitialized ring bytes")
                    emit(ring[address])
    if source != len(data):
        raise FormatError(f"LZSS has {len(data) - source} unconsumed bytes")
    return bytes(output)


def lzss_encode_literals(data: bytes) -> bytes:
    """Emit valid LZSS using literals only; intentionally simple and auditable.

    Main and USB application slots have enough space for this encoding. The
    original updater does not; an attempt to replace it is rejected on size.
    Unchanged components retain the exact original compressed bytes.
    """
    output = bytearray()
    for offset in range(0, len(data), 8):
        group = data[offset:offset + 8]
        output.append((1 << len(group)) - 1)
        output.extend(group)
    return bytes(output)


def component_payload(image: bytes, component: Component) -> bytes:
    offset = component.offset
    payload_offset = u32(image, offset + 0x2C)
    size = u32(image, offset + 0x30)
    if payload_offset != HEADER_SIZE:
        raise FormatError(f"{component.name}: unexpected payload offset")
    if offset + payload_offset + size > component.slot_end:
        raise FormatError(f"{component.name}: payload exceeds assigned slot")
    return image[offset + payload_offset:offset + payload_offset + size]


def component_unpacked(image: bytes, component: Component) -> bytes:
    payload = component_payload(image, component)
    decoded_size = u32(image, component.offset + 0x3C)
    if component.compressed:
        return lzss_decode(payload, decoded_size)
    if decoded_size != len(payload):
        raise FormatError(f"{component.name}: raw component length mismatch")
    return payload


def inspect_image(image: bytes, *, decode: bool = True) -> dict:
    if len(image) != IMAGE_SIZE:
        raise FormatError(f"Expected {IMAGE_SIZE} bytes, found {len(image)}")
    digest = sha256(image)
    start_block, end_block, block_size, payload_size = struct.unpack_from("<4I", image, FLASH_SIZE)
    if payload_size != len(image) - 16:
        raise FormatError("Trailer payload size does not equal file size minus 16")
    if block_size == 0 or end_block < start_block:
        raise FormatError("Invalid update block range")
    update_start = start_block * block_size
    update_end = (end_block + 1) * block_size
    if update_end > payload_size:
        raise FormatError("Update block range exceeds payload")
    result = {
        "sha256": digest,
        "size": len(image),
        "is_supplied_original": digest == ORIGINAL_SHA256,
        "format_scope": "Observed Roland MX-1 firmware 1.051132 layout only",
        "boot_base": BOOT_BASE,
        "boot_images": [],
        "components": [],
        "trailer_offset": FLASH_SIZE,
        "trailer_hex": image[FLASH_SIZE:].hex(),
        "trailer_words_le": list(struct.unpack_from("<4I", image, FLASH_SIZE)),
        "update_plan": {
            "start_block": start_block, "end_block_inclusive": end_block,
            "block_size": block_size, "payload_size": payload_size,
            "flash_start": update_start, "flash_end_exclusive": update_end,
            "evidence": "Original updater 0x600056d0 reads trailer; 0x60005584 writes inclusive block range",
        },
        "unproven_fields": [
            "ESC91 boot header fields other than signature and payload length",
            "Boot-ROM behavior and acceptance checks outside traced updater path",
        ],
    }
    for name, offset, slot_end in (("boot_main", 0, 0x8000),
                                  ("boot_usb", 0x8000, 0x10000)):
        if image[offset:offset + 12] != b"ESC91.000\x00\x00\x00":
            raise FormatError(f"{name}: signature mismatch")
        size = u32(image, offset + 12)
        start = offset + BOOT_HEADER_SIZE
        if not 0 < size <= slot_end - start:
            raise FormatError(f"{name}: invalid boot payload length")
        payload = image[start:start + size]
        result["boot_images"].append({
            "name": name, "header_offset": offset, "payload_offset": start,
            "payload_size": size, "load_address": BOOT_BASE,
            "initial_sp": u32(payload, 0), "reset_vector": u32(payload, 4),
            "sha256": sha256(payload), "header_hex": image[offset:start].hex(),
        })
    for component in COMPONENTS:
        offset = component.offset
        if image[offset:offset + 16] != component.tag:
            raise FormatError(f"{component.name}: signature mismatch")
        payload = component_payload(image, component)
        checksum = u32(image, offset + 0x34)
        computed = sum(payload) & 0xFFFFFFFF
        if checksum != computed:
            raise FormatError(f"{component.name}: stored-byte checksum mismatch "
                              f"({checksum:#x} != {computed:#x})")
        row = {
            "name": component.name, "header_offset": offset,
            "payload_offset": offset + HEADER_SIZE,
            "slot_end": component.slot_end,
            "slot_capacity": component.slot_end - offset - HEADER_SIZE,
            "label": image[offset:offset + 16].decode("ascii").rstrip(),
            "build_timestamp": image[offset + 16:offset + 32].decode("ascii"),
            "version": image[offset + 32:offset + 40].decode("ascii"),
            "entry_address_field": u32(image, offset + 0x28),
            "load_address": u32(image, offset + 0x38),
            "stored_size": len(payload), "checksum": checksum,
            "checksum_algorithm": "sum of stored payload bytes modulo 2^32",
            "checksum_valid": True,
            "compression": "lzss-zero-init-4096-18" if component.compressed else "none",
            "decoded_size": u32(image, offset + 0x3C),
            "stored_sha256": sha256(payload),
            "padding_is_ff": all(value == 0xFF for value in
                image[offset + HEADER_SIZE + len(payload):component.slot_end]),
        }
        if decode:
            unpacked = component_unpacked(image, component)
            row["decoded_sha256"] = sha256(unpacked)
        result["components"].append(row)
    return result


def extract_image(image: bytes, directory: Path) -> dict:
    manifest = inspect_image(image)
    directory.mkdir(parents=True, exist_ok=True)
    for row in manifest["boot_images"]:
        start = row["payload_offset"]
        (directory / f"{row['name']}.bin").write_bytes(image[start:start + row["payload_size"]])
    for component in COMPONENTS:
        (directory / f"{component.name}.stored.bin").write_bytes(component_payload(image, component))
        (directory / f"{component.name}.bin").write_bytes(component_unpacked(image, component))
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def repack_image(original: bytes, replacements: dict[str, bytes], *,
                 allow_resize: bool = False) -> tuple[bytes, dict]:
    """Replace decoded application payloads, preserving every other component.

    Only the exact supplied original is accepted as a base. By default, decoded
    length changes are rejected. Explicit allow_resize permits main/USB changes
    only; callers must also repair and validate the runtime scatter mapping.
    """
    original_manifest = inspect_image(original)
    if not original_manifest["is_supplied_original"]:
        raise FormatError("Repacking requires the exact supplied original firmware as base")
    unknown = replacements.keys() - COMPONENT_BY_NAME.keys()
    if unknown:
        raise FormatError("Unknown replacement component(s): " + ", ".join(sorted(unknown)))
    image = bytearray(original)
    changes = []
    for component in COMPONENTS:
        if component.name not in replacements:
            continue
        replacement = replacements[component.name]
        previous = component_unpacked(original, component)
        if replacement == previous:
            continue
        if len(replacement) != len(previous):
            if not allow_resize or component.name not in ("app_main", "app_usb"):
                raise FormatError(f"{component.name}: decoded size change requires explicit application allow_resize")
            if not 0 < len(replacement) <= 8 * 1024 * 1024:
                raise FormatError(f"{component.name}: invalid resized application length")
        encoded = lzss_encode_literals(replacement) if component.compressed else replacement
        capacity = component.slot_end - component.offset - HEADER_SIZE
        if len(encoded) > capacity:
            raise FormatError(f"{component.name}: encoded size {len(encoded)} exceeds {capacity}-byte slot")
        start = component.offset + HEADER_SIZE
        end = start + len(encoded)
        # This image has erased padding throughout every defined slot.
        if not all(value == 0xFF for value in original[
                start + len(component_payload(original, component)):component.slot_end]):
            raise FormatError(f"{component.name}: unexpected non-erased slot padding")
        image[start:component.slot_end] = encoded + b"\xFF" * (component.slot_end - end)
        struct.pack_into("<I", image, component.offset + 0x30, len(encoded))
        struct.pack_into("<I", image, component.offset + 0x34, sum(encoded) & 0xFFFFFFFF)
        struct.pack_into("<I", image, component.offset + 0x3C, len(replacement))
        changes.append({
            "name": component.name,
            "decoded_bytes_changed": sum(a != b for a, b in zip(previous, replacement)) + abs(len(previous) - len(replacement)),
            "old_decoded_size": len(previous),
            "new_decoded_size": len(replacement),
            "decoded_size_change_explicitly_allowed": allow_resize,
            "old_decoded_sha256": sha256(previous),
            "new_decoded_sha256": sha256(replacement),
            "old_stored_size": len(component_payload(original, component)),
            "new_stored_size": len(encoded),
            "encoding": "literal-only LZSS" if component.compressed else "raw",
        })
    result = bytes(image)
    manifest = inspect_image(result)
    for name, expected in replacements.items():
        if component_unpacked(result, COMPONENT_BY_NAME[name]) != expected:
            raise AssertionError(f"{name}: internal repack round-trip failed")
    return result, {
        "base_sha256": sha256(original),
        "output_sha256": sha256(result),
        "byte_identical_to_original": result == original,
        "changes": changes,
        "boot_images_and_trailer_unchanged": (
            result[:0x10000] == original[:0x10000]
            and result[FLASH_SIZE:] == original[FLASH_SIZE:]),
        "all_bytes_outside_update_range_unchanged": (
            result[:original_manifest["update_plan"]["flash_start"]] ==
                original[:original_manifest["update_plan"]["flash_start"]]
            and result[original_manifest["update_plan"]["flash_end_exclusive"]:] ==
                original[original_manifest["update_plan"]["flash_end_exclusive"]:]),
        "container_validation": manifest,
        "hardware_validation": "not performed; research output only",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect_parser = commands.add_parser("inspect", help="Validate checksums and show JSON metadata")
    inspect_parser.add_argument("input", type=Path)
    inspect_parser.add_argument("--output", type=Path)
    extract_parser = commands.add_parser("extract", help="Extract boot and application images")
    extract_parser.add_argument("input", type=Path)
    extract_parser.add_argument("directory", type=Path)
    repack_parser = commands.add_parser("repack", help="Build an offline experimental image")
    repack_parser.add_argument("input", type=Path)
    repack_parser.add_argument("output", type=Path)
    repack_parser.add_argument("--replace", action="append", default=[], metavar="NAME=DECODED_FILE")
    repack_parser.add_argument("--allow-resize", action="store_true",
                              help="Permit application size changes; caller must validate scatter-loader changes")
    args = parser.parse_args()
    try:
        image = args.input.read_bytes()
        if args.command == "inspect":
            report = inspect_image(image)
            if args.output:
                args.output.write_text(json.dumps(report, indent=2) + "\n")
        elif args.command == "extract":
            report = extract_image(image, args.directory)
        else:
            replacements = {}
            for replacement in args.replace:
                name, separator, filename = replacement.partition("=")
                if not separator or name in replacements:
                    raise FormatError("Each replacement must be unique NAME=DECODED_FILE")
                replacements[name] = Path(filename).read_bytes()
            output, report = repack_image(image, replacements, allow_resize=args.allow_resize)
            if args.output.resolve() == args.input.resolve():
                raise FormatError("Output must not overwrite the original firmware")
            args.output.write_bytes(output)
            args.output.with_suffix(args.output.suffix + ".json").write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
    except (FormatError, OSError, UnicodeError) as exc:
        parser.exit(1, f"error: {exc}\n")


if __name__ == "__main__":
    main()
