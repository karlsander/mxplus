#!/usr/bin/env python3
"""Bounded, read-only USB descriptor inspection for decompressed MX-1 images.

No third-party modules are needed. Offsets always refer to the supplied image,
not the compressed updater. The address base is supplied by the caller and does
not prove that a descriptor is served unchanged at runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path


def u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 2], "little")


def u24(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset + 3], "little")


def metadata(data: bytes, offset: int, base: int) -> dict:
    return {
        "offset": offset,
        "offset_hex": f"0x{offset:x}",
        "address_with_supplied_base": f"0x{base + offset:08x}",
        "length": len(data),
        "descriptor_type": data[1],
        "raw_hex": data.hex(" "),
    }


def descriptor_fields(raw: bytes, interface: dict | None = None) -> dict:
    """Decode only fields whose descriptor length/layout is established."""
    kind = raw[1]
    length = len(raw)
    fields = {}
    if kind == 1 and length == 18:
        fields = dict(
            name="device", bcdUSB=f"0x{u16(raw, 2):04x}",
            device_class=raw[4], device_subclass=raw[5], device_protocol=raw[6],
            ep0_max_packet_size=raw[7], vendor_id=f"0x{u16(raw, 8):04x}",
            product_id=f"0x{u16(raw, 10):04x}", bcdDevice=f"0x{u16(raw, 12):04x}",
            manufacturer_string_index=raw[14], product_string_index=raw[15],
            serial_string_index=raw[16], number_of_configurations=raw[17],
        )
    elif kind in (2, 7) and length >= 9:
        fields = dict(
            name="configuration" if kind == 2 else "other_speed_configuration",
            total_length=u16(raw, 2), interface_count=raw[4],
            configuration_value=raw[5], configuration_string_index=raw[6],
            attributes=raw[7], self_powered=bool(raw[7] & 0x40),
            remote_wakeup=bool(raw[7] & 0x20), max_power_usb2_mA=raw[8] * 2,
        )
    elif kind == 4 and length >= 9:
        fields = dict(
            name="interface", number=raw[2], alternate_setting=raw[3],
            endpoint_count=raw[4], interface_class=raw[5],
            interface_subclass=raw[6], interface_protocol=raw[7],
            string_index=raw[8],
        )
    elif kind == 5 and length >= 7:
        attributes = raw[3]
        maximum = u16(raw, 4)
        fields = dict(
            name="endpoint", address=f"0x{raw[2]:02x}",
            direction="IN" if raw[2] & 0x80 else "OUT", number=raw[2] & 0xf,
            attributes=attributes,
            transfer_type=["control", "isochronous", "bulk", "interrupt"][attributes & 3],
            synchronization_type=["none", "asynchronous", "adaptive", "synchronous"][(attributes >> 2) & 3],
            usage_type=["data", "feedback", "implicit_feedback_data", "reserved"][(attributes >> 4) & 3],
            maximum_packet_size_raw=maximum, maximum_payload_per_transaction=maximum & 0x7ff,
            high_speed_transactions_per_microframe=1 + ((maximum >> 11) & 3),
            interval=raw[6],
        )
        if (attributes & 3) in (1, 3) and 1 <= raw[6] <= 16:
            fields["high_speed_service_interval_us_if_applicable"] = 125 * (1 << (raw[6] - 1))
        if length >= 9:
            fields.update(refresh=raw[7], synchronization_address=f"0x{raw[8]:02x}")
    elif kind == 6 and length == 10:
        fields = dict(
            name="device_qualifier", bcdUSB=f"0x{u16(raw, 2):04x}",
            device_class=raw[4], device_subclass=raw[5], device_protocol=raw[6],
            ep0_max_packet_size=raw[7], number_of_configurations=raw[8], reserved=raw[9],
        )
    elif kind == 11 and length >= 8:
        fields = dict(
            name="interface_association", first_interface=raw[2], interface_count=raw[3],
            function_class=raw[4], function_subclass=raw[5],
            function_protocol=raw[6], string_index=raw[7],
        )
    elif kind == 0x24 and length >= 3:
        fields = dict(name="class_specific_interface", subtype=raw[2])
        subclass = (interface or {}).get("interface_subclass")
        protocol = (interface or {}).get("interface_protocol")
        if subclass == 2 and protocol in (0, 1, 2):
            # Roland's vendor 0/1/2 formats have the UAC1 AS descriptor layout.
            if raw[2] == 1 and length == 7:
                fields.update(name="uac1_layout_as_general", terminal_link=raw[3],
                              delay=raw[4], format_tag=u16(raw, 5))
            elif raw[2] == 2 and length >= 8 and raw[3] == 1:
                fields.update(name="uac1_layout_format_type_i", format_type=raw[3],
                              channels=raw[4], subframe_bytes=raw[5],
                              valid_bits=raw[6], frequency_type=raw[7])
                count = raw[7]
                expected = 14 if count == 0 else 8 + 3 * count
                if length < expected:
                    fields["malformed"] = "sample-rate list extends past descriptor"
                elif count:
                    fields["sample_rates_hz"] = [u24(raw, 8 + 3 * i) for i in range(count)]
                else:
                    fields["sample_rate_range_hz"] = [u24(raw, 8), u24(raw, 11)]
        elif subclass == 2 and protocol == 0x20:
            if raw[2] == 1 and length >= 16:
                fields.update(name="uac2_as_general", terminal_link=raw[3],
                              controls=raw[4], format_type=raw[5],
                              formats=int.from_bytes(raw[6:10], "little"), channels=raw[10],
                              channel_config=int.from_bytes(raw[11:15], "little"), channel_names=raw[15])
            elif raw[2] == 2 and length >= 6 and raw[3] == 1:
                fields.update(name="uac2_format_type_i", format_type=raw[3],
                              subslot_bytes=raw[4], valid_bits=raw[5])
        elif subclass == 1 and protocol == 0x20:
            if raw[2] == 1 and length >= 9:
                fields.update(name="uac2_ac_header", bcdADC=f"0x{u16(raw, 3):04x}",
                              category=raw[5], total_class_specific_length=u16(raw, 6), controls=raw[8])
            elif raw[2] == 0x0a and length >= 8:
                fields.update(name="uac2_clock_source", clock_id=raw[3], attributes=raw[4],
                              controls=raw[5], associated_terminal=raw[6], string_index=raw[7])
            elif raw[2] == 2 and length >= 17:
                fields.update(name="uac2_input_terminal", terminal_id=raw[3], terminal_type=f"0x{u16(raw, 4):04x}",
                              associated_terminal=raw[6], clock_source_id=raw[7], channels=raw[8],
                              channel_config=int.from_bytes(raw[9:13], "little"), channel_names=raw[13],
                              controls=u16(raw, 14), string_index=raw[16])
            elif raw[2] == 3 and length >= 12:
                fields.update(name="uac2_output_terminal", terminal_id=raw[3], terminal_type=f"0x{u16(raw, 4):04x}",
                              associated_terminal=raw[6], source_id=raw[7], clock_source_id=raw[8],
                              controls=u16(raw, 9), string_index=raw[11])
        if raw[2] == 0xf1:
            fields.update(name="roland_vendor_class_specific", opaque=True,
                          note="Preserved bytes; no unsupported control/MIDI semantics inferred.")
    elif kind == 0x25 and length >= 3:
        fields = dict(name="class_specific_endpoint", subtype=raw[2])
        subclass = (interface or {}).get("interface_subclass")
        protocol = (interface or {}).get("interface_protocol")
        if subclass == 2 and protocol in (0, 1, 2) and raw[2] == 1 and length >= 7:
            fields.update(name="uac1_layout_endpoint_general", attributes=raw[3],
                          sampling_frequency_control=bool(raw[3] & 1),
                          pitch_control=bool(raw[3] & 2), lock_delay_units=raw[4],
                          lock_delay=u16(raw, 5))
        elif subclass == 2 and protocol == 0x20 and raw[2] == 1 and length >= 8:
            fields.update(name="uac2_endpoint_general", attributes=raw[3], controls=raw[4],
                          lock_delay_units=raw[5], lock_delay=u16(raw, 6))
    if not fields:
        fields = dict(name="unknown_or_unsupported_layout")
    return fields


def parse_configuration(data: bytes, offset: int, base: int = 0) -> dict:
    if offset < 0 or offset + 9 > len(data):
        raise ValueError("configuration header outside input")
    if data[offset] != 9 or data[offset + 1] not in (2, 7):
        raise ValueError("not a configuration header")
    total = u16(data, offset + 2)
    if total < 9 or offset + total > len(data):
        raise ValueError("configuration length outside input")
    result = metadata(data[offset:offset + 9], offset, base)
    result.update(descriptor_fields(data[offset:offset + 9]))
    result["raw_configuration_hex"] = data[offset:offset + total].hex(" ")
    result["descriptors"] = []
    result["warnings"] = []
    pos, stop, current = offset + 9, offset + total, None
    interface_keys, seen_interfaces = set(), set()
    actual_endpoints = 0

    def check_endpoint_count() -> None:
        if current is not None and actual_endpoints != current["endpoint_count"]:
            result["warnings"].append(
                f"interface {current['number']} alternate {current['alternate_setting']} "
                f"declares {current['endpoint_count']} endpoints, contains {actual_endpoints}")

    while pos < stop:
        if pos + 2 > stop:
            raise ValueError(f"truncated descriptor header at 0x{pos:x}")
        length = data[pos]
        if length < 2 or pos + length > stop:
            raise ValueError(f"invalid descriptor length {length} at 0x{pos:x}")
        raw = data[pos:pos + length]
        item = metadata(raw, pos, base)
        fields = descriptor_fields(raw, current)
        item.update(fields)
        if raw[1] == 4:
            if length < 9:
                raise ValueError(f"short interface descriptor at 0x{pos:x}")
            check_endpoint_count()
            current, actual_endpoints = fields, 0
            key = (current["number"], current["alternate_setting"])
            if key in interface_keys:
                result["warnings"].append(f"duplicate interface/alternate {key}")
            interface_keys.add(key)
            seen_interfaces.add(current["number"])
        elif raw[1] == 5:
            if length < 7:
                raise ValueError(f"short endpoint descriptor at 0x{pos:x}")
            actual_endpoints += 1
            if current is None:
                result["warnings"].append(f"endpoint without interface at 0x{pos:x}")
        if current is not None:
            item["parent_interface"] = current["number"]
            item["parent_alternate_setting"] = current["alternate_setting"]
        result["descriptors"].append(item)
        pos += length
    check_endpoint_count()
    if len(seen_interfaces) != result["interface_count"]:
        result["warnings"].append("unique interface count does not match configuration header")
    for number in seen_interfaces:
        if (number, 0) not in interface_keys:
            result["warnings"].append(f"interface {number} has no zero alternate setting")
    return result


def scan_image(data: bytes, base: int = 0x60000000) -> dict:
    report = {
        "schema": "mx1-usb-descriptor-report-v1", "image_size": len(data),
        "image_sha256": hashlib.sha256(data).hexdigest(), "supplied_base": f"0x{base:x}",
        "limitations": [
            "Static templates can be copied and modified by startup code; this is not a live USB capture.",
            "Address values assume the supplied image base; pointer scans report literal data, not proven xrefs.",
            "A valid descriptor chain does not establish USB class compliance or successful audio streaming.",
            "No conversion or firmware patch is performed. Class-byte edits cannot create missing AC entities, clock requests, or synchronization behavior.",
        ],
        "devices": [], "qualifiers": [], "configurations": [], "strings_near_descriptors": [],
    }
    for offset in range(max(0, len(data) - 1)):
        size, kind = data[offset:offset + 2]
        if size < 2 or offset + size > len(data):
            continue
        raw = data[offset:offset + size]
        if kind == 1 and size == 18 and raw[7] in (8, 16, 32, 64) and 1 <= raw[17] <= 8:
            if u16(raw, 2) not in (0x0100, 0x0110, 0x0200, 0x0210, 0x0300, 0x0310, 0x0320):
                continue
            item = metadata(raw, offset, base)
            item.update(descriptor_fields(raw))
            report["devices"].append(item)
        elif kind == 6 and size == 10 and raw[7] in (8, 16, 32, 64) and raw[9] == 0 and 1 <= raw[8] <= 8:
            if u16(raw, 2) != 0x0200:
                continue
            item = metadata(raw, offset, base)
            item.update(descriptor_fields(raw))
            report["qualifiers"].append(item)
        elif kind in (2, 7) and size == 9 and raw[7] & 0x80 and 1 <= raw[4] <= 32 and raw[5] > 0:
            try:
                config = parse_configuration(data, offset, base)
            except ValueError:
                continue
            if any(d["descriptor_type"] == 4 for d in config["descriptors"]):
                report["configurations"].append(config)

    # Limit string scan to adjacent regions to avoid treating arbitrary code as UTF-16.
    ranges = [(c["offset"] - 512, c["offset"] + c["total_length"] + 1024)
              for c in report["configurations"]]
    for offset in range(max(0, len(data) - 1)):
        if not any(lo <= offset < hi for lo, hi in ranges):
            continue
        size, kind = data[offset:offset + 2]
        if kind != 3 or size < 4 or size % 2 or offset + size > len(data):
            continue
        raw = data[offset:offset + size]
        if raw == b"\x04\x03\x09\x04":
            fields = dict(name="possible_language_string", language_ids=["0x0409"])
        else:
            try:
                value = raw[2:].decode("utf-16-le")
            except UnicodeDecodeError:
                continue
            if not all(32 <= ord(ch) < 127 for ch in value):
                continue
            fields = dict(name="possible_string", text=value)
        item = metadata(raw, offset, base)
        item.update(fields)
        report["strings_near_descriptors"].append(item)
    objects = [obj for key in ("devices", "qualifiers", "configurations", "strings_near_descriptors")
               for obj in report[key]]
    wanted = {base + obj["offset"]: obj for obj in objects}
    for obj in objects:
        obj["aligned_literal_pointer_offsets"] = []
    for offset in range(0, len(data) - 3, 4):
        value, = struct.unpack_from("<I", data, offset)
        if value in wanted:
            wanted[value]["aligned_literal_pointer_offsets"].append(f"0x{offset:x}")
    report["mx1_findings"] = summarize_mx1(report)
    return report


def summarize_mx1(report: dict) -> dict:
    matching = [d for d in report["devices"]
                if d["vendor_id"] == "0x0582" and d["product_id"] == "0x01a3"]
    if not matching:
        return {"identified": False}
    streams = []
    for config in report["configurations"]:
        current = None
        for item in config["descriptors"]:
            if item["name"] == "interface":
                current = {"configuration_offset": config["offset_hex"], "interface": item["number"],
                           "alternate_setting": item["alternate_setting"], "class": item["interface_class"],
                           "subclass": item["interface_subclass"], "protocol": item["interface_protocol"]}
            elif current and item["name"] == "uac1_layout_format_type_i":
                current.update({k: item[k] for k in ("channels", "subframe_bytes", "valid_bits", "sample_rates_hz") if k in item})
            elif current and item["name"] == "endpoint" and item["transfer_type"] == "isochronous":
                stream = dict(current)
                stream.update({k: item[k] for k in ("address", "direction", "synchronization_type", "usage_type", "interval", "maximum_payload_per_transaction")})
                stream["endpoint_offset"] = item["offset_hex"]
                streams.append(stream)
    return {
        "identified": True, "streams": streams,
        "static_template_only": True,
        "class_compliance_obstacles": [
            "Device and interfaces use vendor-specific class codes.",
            "Interface 0 has no standard AudioControl header or terminal graph in this template.",
            "The stream format blocks have UAC1 layout; 125-us high-speed polling is not Apple's compliant ADC1 design.",
            "Playback uses asynchronous OUT plus an implicit-feedback IN data endpoint; startup sequencing must be measured.",
            "A UAC2 conversion requires new AudioControl/clock/terminal/AS descriptors and matching request handlers.",
            "The MIDI vendor descriptors need an independently implemented standard USB MIDI descriptor graph.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="decompressed main application binary")
    parser.add_argument("--base", type=lambda value: int(value, 0), default=0x60000000)
    parser.add_argument("--output", type=Path, help="write complete JSON report here; otherwise stdout")
    args = parser.parse_args()
    report = scan_image(args.image.read_bytes(), args.base)
    report["input_path"] = str(args.image)
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
        print(f"Wrote {args.output}: {len(report['devices'])} device descriptor(s), "
              f"{len(report['configurations'])} configuration(s), "
              f"{len(report['mx1_findings'].get('streams', []))} MX-1 stream alternates")
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
