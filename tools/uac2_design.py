#!/usr/bin/env python3
"""Generate a UAC2 descriptor DESIGN and request contract, never a firmware.

This generates separate audio-only and original-modes descriptor prototypes.
No image is modified, no hardware is accessed, and no flashable BIN is written.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from usb_descriptors import parse_configuration


ORIGINAL_VENDOR_MIDI = bytes.fromhex(
    "09 04 03 00 02 ff 03 00 00 "
    "06 24 f1 02 02 02 "
    "07 05 03 02 00 02 00 "
    "07 05 84 02 00 02 00 "
    "09 04 03 01 02 ff 03 00 00 "
    "07 05 03 03 00 02 04 "
    "07 05 85 03 00 02 04"
)


def prototype_configuration(preserve_modes: bool = False) -> bytes:
    # 18 unpositioned channels preserve original 18-channel endpoint framing.
    # One fixed-for-this-session, read-only internal clock, entity ID 0x10.
    ac = bytes.fromhex(
        "09 24 01 00 02 0a 4b 00 00 "
        "08 24 0a 10 01 05 00 00 "
        "11 24 02 01 01 01 00 10 12 00 00 00 00 00 00 00 00 "
        "0c 24 03 02 03 06 00 01 10 00 00 00 "
        "11 24 02 06 03 06 00 10 12 00 00 00 00 00 00 00 00 "
        "0c 24 03 07 01 01 00 06 10 00 00 00"
    )
    assert len(ac) == 75
    body = bytes.fromhex("08 0b 00 03 01 00 20 02 09 04 00 00 00 01 01 20 00") + ac
    for interface, terminal, endpoint, attributes in ((1, 1, 0x0d, 0x05), (2, 7, 0x8e, 0x25)):
        body += bytes((9, 4, interface, 0, 0, 1, 2, 0x20, 0))
        alternates = ((1, 18, 1008), (2, 2, 112)) if preserve_modes else ((1, 18, 1008),)
        for alternate, channels, max_packet in alternates:
            body += bytes((9, 4, interface, alternate, 1, 1, 2, 0x20, 0))
            body += bytes((16, 0x24, 1, terminal, 0, 1, 1, 0, 0, 0, channels, 0, 0, 0, 0, 0))
            body += bytes.fromhex("06 24 02 01 04 18")
            body += bytes((7, 5, endpoint, attributes)) + struct.pack("<H", max_packet) + bytes((1,))
            body += bytes.fromhex("08 25 01 00 00 00 00 00")
    if preserve_modes:
        assert len(ORIGINAL_VENDOR_MIDI) == 52
        body += ORIGINAL_VENDOR_MIDI
    interface_count = 4 if preserve_modes else 3
    return bytes((9, 2)) + struct.pack("<H", 9 + len(body)) + bytes((interface_count, 1, 0, 0xc0, 0)) + body


def design_report(preserve_modes: bool = False) -> dict:
    config = prototype_configuration(preserve_modes=preserve_modes)
    decoded = parse_configuration(config, 0)
    assert len(config) == (355 if preserve_modes else 211) and decoded["warnings"] == []
    report = {
        "schema": "mx1-uac2-original-modes-design-v1" if preserve_modes else "mx1-uac2-audio-only-design-v1",
        "status": "UNINTEGRATED DESIGN: NOT FIRMWARE; NOT A FLASHABLE UPDATE; NOT HARDWARE-VERIFIED",
        "configuration_length": len(config),
        "original_configuration_length": 258,
        "fits_original_descriptor_storage_size": len(config) <= 258,
        "device_descriptor_design_hex": "12 01 00 02 ef 02 01 40 82 05 a3 01 00 01 01 02 00 01",
        "device_qualifier_design_hex": "0a 06 00 02 ef 02 01 40 01 00",
        "device_descriptor_warning": "Reuses Roland VID/PID solely for this private existing-device experiment. Never an allocation for a new commercial device. Driver matching/cache and device qualifier changes require review.",
        "configuration_hex": config.hex(" "),
        "configuration_sha256": hashlib.sha256(config).hexdigest(),
        "decoded_configuration": decoded,
        "design_choices": [
            "High-speed UAC2 only, 18 capture and 18 playback channels; existing interface numbers 0/1/2, streaming alternate 1, endpoint addresses 0x0d/0x8e, 125-us interval and 24-bit samples in four-byte subslots.",
            "One shared clock ID 0x10; current internal sampling rate is selected on the hardware before enumeration. Frequency and validity are read-only. The one advertised range equals that actual current rate.",
            ("Preserves original stereo alternate 2 on IF1/IF2 and all 52 original vendor-MIDI bytes on IF3. IAD groups only IF0..IF2. MIDI remains vendor-specific; this does not provide class-compliant MIDI to iOS."
             if preserve_modes else "No MIDI interface or two-channel alternate is advertised in this first audio probe. This is a test design, not the final feature set."),
            "No mute/volume Feature Unit. Mixer controls remain physical firmware controls; no fake OS controls are advertised.",
            "Input uses implicit feedback. Valid startup requires actual IN audio packets independent of host OUT packet arrival.",
        ],
        "control_request_contract": [
            {"request": "clock frequency GET_CUR", "setup_hex": "a1 01 00 01 00 10 04 00", "response": "4 bytes little-endian uint32 actual current sample rate; truncate to wLength"},
            {"request": "clock frequency GET_RANGE", "setup_hex": "a1 02 00 01 00 10 0e 00", "response": "u16(1), u32(current_rate), u32(current_rate), u32(0); truncate to wLength, including 2-byte header probe"},
            {"request": "clock validity GET_CUR", "setup_hex": "a1 01 00 02 00 10 01 00", "response": "1 byte, 1 only when the internal clock is valid"},
            {"request": "SET_CUR to read-only clock, unknown entity/selector, malformed request", "response": "STALL; do not silently acknowledge or write memory"},
            {"request": "SET_INTERFACE IF1/IF2 alt0/alt1/alt2" if preserve_modes else "SET_INTERFACE IF1/IF2 alt0/alt1", "response": "Preserve original hardware endpoint start/stop and channel-count mapping; establish input-first startup and unplug/reconnect behavior"},
        ],
        "unresolved_integration": [
            "Replace or redirect runtime descriptor setup that currently copies and edits UAC1 format blocks at fixed offsets. In-place storage fit does not make an in-place patch correct.",
            "Connect class-specific setup dispatch to real EP0 response primitives and supply actual clock state.",
            "Provide consistent device and qualifier descriptors, and a truthful full-speed behavior; the original empty full-speed template is not a tested UAC2 fallback.",
            "Prove sample alignment on the wire: 24 significant bits in a four-byte subslot does not itself prove which bit positions the original DMA path uses.",
            "Prove IN transmission starts before OUT data arrives. Apple's implicit-feedback host waits for stable IN timing before sending OUT.",
            ("Verify IF1/IF2 alternate transitions retain 18/2-channel hardware framing. Fixed 18-channel terminal clusters describe the internal mixer; alternate 2 advertises a 2-channel USB stream, whose host mapping and actual firmware routing require validation."
             if preserve_modes else "Check alternate-setting and hardware task coupling to omitted MIDI interface; no assumption of safety from unchanged audio endpoint numbers."),
            "Validate on a descriptor parser, then host stack, then muted-output hardware with an independently verified recovery path. No such physical tests have been performed.",
        ],
    }
    if preserve_modes:
        report["preserved_vendor_midi"] = {"original_main_offset_hex": "0xb4a6a", "length": 52,
                                           "new_configuration_offset": len(config) - 52,
                                           "raw_hex": ORIGINAL_VENDOR_MIDI.hex(" ")}
        report["unresolved_integration"].insert(0, "355 bytes require relocation; do not overwrite the original 258-byte configuration in place.")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--variant", choices=("audio-only", "preserve-modes"), default="audio-only")
    args = parser.parse_args()
    text = json.dumps(design_report(preserve_modes=args.variant == "preserve-modes"), indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
        print(f"Wrote unintegrated descriptor design: {args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
