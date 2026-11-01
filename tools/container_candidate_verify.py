#!/usr/bin/env python3
"""Verify an actual candidate with the original decoder and updater instructions.

Offline only. USB I/O, physical flash programming, full boot and audio are not
modeled. See container_updater_verify.py for precisely scoped environment stubs.
"""
import argparse
import json
import struct
from pathlib import Path

from container_tool import (COMPONENTS, ORIGINAL_SHA256, component_payload,
                            component_unpacked, inspect_image, sha256)
from container_verify import run_original_decoder
from container_updater_verify import UpdaterHarness


def verify(original, candidate):
    if sha256(original) != ORIGINAL_SHA256:
        raise ValueError("Unexpected original firmware")
    source_info = inspect_image(original)
    candidate_info = inspect_image(candidate)
    plan = candidate_info["update_plan"]
    assert plan == source_info["update_plan"], "Candidate changed update plan"
    first, end, size = plan["flash_start"], plan["flash_end_exclusive"], plan["block_size"]
    assert candidate[:first] == original[:first], "Candidate changed protected lower region"
    assert candidate[end:] == original[end:], "Candidate changed protected upper region/trailer"
    changed = []
    for component in COMPONENTS:
        before = component_unpacked(original, component)
        after = component_unpacked(candidate, component)
        if before == after:
            continue
        if component.compressed:
            actual = run_original_decoder(original, component_payload(candidate, component), len(after))
            assert actual == after, "Original decoder disagrees on candidate component"
        changed.append({"component": component.name, "original_decoded_bytes": len(before),
                        "candidate_decoded_bytes": len(after),
                        "candidate_decoded_sha256": sha256(after),
                        "original_decoder_matches": component.compressed})
    harness = UpdaterHarness(original, candidate)
    rc, fields = harness.parse_trailer()
    assert rc == 0 and fields == (plan["start_block"], plan["end_block_inclusive"], size)
    tag_result = harness.call(0x60005458, harness.FILE_HANDLE, first, end)
    assert tag_result != 5, "Original pre-write component-label gate rejects candidate"
    rc = harness.call(0x60005584, fields[0], fields[1], size, harness.BUFFER, size)
    assert rc == 1 and not harness.errors, "Original writer loop rejected candidate"
    expected_writes = [(block * size, size) for block in range(fields[0], fields[1] + 1)]
    assert harness.writes == expected_writes, "Unexpected flash write plan"
    flashed = bytes(harness.emulator.mem_read(harness.FLASH, 0x400000))
    assert flashed == original[:first] + candidate[first:end] + original[end:0x400000]
    checksums = []
    for component in COMPONENTS:
        rc, value = harness.check_component(component.name)
        expected = struct.unpack_from("<I", candidate, component.offset + 0x34)[0]
        assert rc == 1 and value == expected, f"Post-write checksum failed: {component.name}"
        checksums.append({"component": component.name, "checksum": value, "passed": True})
    return {
        "status": "passed", "original_sha256": sha256(original),
        "candidate_sha256": sha256(candidate), "candidate_bytes": len(candidate),
        "changed_decoded_components": changed,
        "original_trailer_parser_accepts": True,
        "original_component_label_gate_result": tag_result,
        "original_sector_write_and_readback_loop_accepts": True,
        "blocks_written_in_memory": len(harness.writes),
        "write_start": first, "write_end_exclusive": end,
        "all_bytes_outside_update_range_preserved": True,
        "original_post_write_checksum_results": checksums,
        "scope": "Original ARM routines executed; file/flash I/O and UI notifications explicitly stubbed",
        "hardware_flash_or_audio_functionality_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("candidate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.original.read_bytes(), args.candidate.read_bytes())
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
