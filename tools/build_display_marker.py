#!/usr/bin/env python3
"""Build a stock-based, two-byte main-application display diagnostic offline."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_host_probe import exact_patch
from container_tool import (COMPONENT_BY_NAME, ORIGINAL_SHA256, FormatError,
                            component_unpacked, repack_image, sha256)
from memory_map import recover

ROOT = Path(__file__).resolve().parents[1]
OFFSET = 0xD3098
RUNTIME = 0x0100280C
BEFORE = bytes.fromhex('1c46')  # mov r4,r3: preserve incoming character
AFTER = bytes.fromhex('3824')   # movs r4,#0x38: ASCII '8'
FILENAME = 'MX1_DISPLAY_MARKER_UNTESTED.bin'


def build(firmware: Path, output: Path) -> dict:
    raw = firmware.read_bytes()
    if sha256(raw) != ORIGINAL_SHA256:
        raise FormatError('Original firmware SHA-256 mismatch')
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    mapping = recover(original)
    hot = mapping['operations'][0]
    if hot != {'call': 0x6000000E, 'kind': 'copy', 'destination': 0x01000300,
               'length': 0xF3A4, 'source': 0x600D0B8C}:
        raise FormatError('Unexpected main startup map')
    if hot['destination'] + OFFSET - (hot['source'] - 0x60000000) != RUNTIME:
        raise FormatError('Display instruction relocation mismatch')
    modified = bytearray(original)
    changes = []
    exact_patch(modified, OFFSET, BEFORE, AFTER, changes,
                "Shared display character becomes ASCII 8 before original font lookup")
    changes[0].update(component='app_main', runtime_address=RUNTIME)
    if {k: v for k, v in recover(modified).items() if k != 'sha256'} != {
            k: v for k, v in mapping.items() if k != 'sha256'}:
        raise FormatError('Display marker changed startup layout')
    candidate, container = repack_image(raw, {'app_main': bytes(modified)})
    output.mkdir(parents=True, exist_ok=True)
    (output / FILENAME).write_bytes(candidate)
    (output / 'app_main.display_marker.bin').write_bytes(modified)
    report = {'status': 'OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED',
        'input_sha256': sha256(raw), 'original_app_sha256': sha256(original),
        'patched_app_sha256': sha256(modified), 'container_sha256': sha256(candidate),
        'patches': changes, 'container': container,
        'sources': {'tools/build_display_marker.py': sha256(Path(__file__).read_bytes())},
        'extension_bytes': 0, 'new_runtime_memory_bytes': 0,
        'startup_mapping_changed': False, 'application_size_changed': False,
        'abi': 'Same instruction width/register destination; MOVS flags are overwritten by the original CMP before use',
        'expected_display': 'Normal text/number character writes become 8: VALUE 888 and TEMPO 8888',
        'hardware_access': False,
        'limits': ['Stock routing and USB; no routing extension included',
                   'Main application only; separate updater display stays original',
                   'Normal menus/values become unreadable; diagnostic only',
                   'Raw segment writes can bypass the character routine',
                   'Physical display, boot and recovery remain unverified for this candidate']}
    (output / 'build-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', nargs='?', type=Path, default=ROOT / 'inputs/MX1_UPD.original.bin')
    parser.add_argument('--output', type=Path, default=ROOT / 'build/display-marker')
    args = parser.parse_args()
    report = build(args.firmware, args.output)
    print(json.dumps({k: report[k] for k in ('status', 'container_sha256', 'patches',
                                           'new_runtime_memory_bytes')}, indent=2))


if __name__ == '__main__':
    main()
