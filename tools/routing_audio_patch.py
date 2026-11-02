"""Exact patch contract and independent DSP input-operand evidence."""
from __future__ import annotations

import struct

from firmware_patch import exact_patch
from container_tool import FormatError

REQUIRED_SYMBOLS = ("mx1_route_dispatch", "mx1_route_flush")
SITES = (0x328, 0x33A, 0x34C, 0x360, 0x376, 0x38A,
         0x3AC, 0x3C2, 0x3E2, 0x3F8, 0x418, 0x42E,
         0x44E, 0x464, 0x484, 0x49A, 0x4AC, 0x4BC)
STOCK = (0x6000, 0x6001, 0x6002, 0x6003, 0x6004, 0x6005,
         0x6008, 0x6009, 0x600A, 0x600B, 0x600C, 0x600D,
         0x600E, 0x600F, 0x6010, 0x6011, 0x2010, 0x2011)
SELECTORS = tuple(0x1DE + pair * 0x34 + side * 0x1A
                  for pair in range(5) for side in range(2))


def source_offset(logical: int) -> int:
    """Normal graph chunk at DSP 0x31a, ROM 0x600b88e8.

    The first source word has unused upper halfword. Original uploader executes
    a boundary merge, then whole-word DMA. Logical high-halfword-first order
    differs from the ARM's little-endian memory address order.
    """
    return 0xB88E8 + ((logical - 0x318) ^ 2)


def patch_audio(image: bytearray, symbols: dict, changes: list) -> dict:
    evidence = []
    for logical, operand in zip(SITES + (0x4CE, 0x4E0), STOCK + (0x6006, 0x6007)):
        offset = source_offset(logical)
        expected = struct.pack("<H", operand)
        if image[offset:offset + 2] != expected:
            raise FormatError(f"DSP input-source guard mismatch at app_main+{offset:#x}")
        evidence.append({"component": "app_main", "decoded_offset": offset,
                         "rom_runtime": 0x60000000 + offset,
                         "dsp_core": 0, "dsp_logical_offset": logical,
                         "original_operand": operand, "expected_bytes": expected.hex()})
    for logical in SELECTORS:
        offset = 0xB8700 + ((logical - 0x134) ^ 2)
        if image[offset:offset + 2] != b"\0\0":
            raise FormatError(f"DSP computer-selector guard mismatch at app_main+{offset:#x}")
    # Entire original 10-byte entry: push {r4-r9,lr}; sub sp,#28;
    # bl 0x6000f1bc. The extension trampoline executes equivalent originals.
    replacement = b"\x00\xbf" + bytes.fromhex("dff800f0") + struct.pack(
        "<I", symbols["mx1_route_dispatch"] | 1)
    exact_patch(image, 0x24BAE, bytes.fromhex("2de9f04387b0eaf702fb"), replacement,
                changes, "DSP parameter-event-8 drain, then queued routing update")
    changes[-1]["runtime_address"] = 0x60024BAE
    return {
        "destination_strips": 11, "source_choices_with_auto": 53,
        "mono_strips_skip_stereo_pair_choices": True,
        "dsp_operand_guards": evidence,
        "dsp_computer_selector_offsets": list(SELECTORS),
        "audio_sample_cpu_copy": False,
        "task_event": {"task": 0x6051DEA8, "event": 8,
                       "original_handler": 0x60024BAE, "post": 0x0100E266},
        "mode_policy": "Mixer/Control Surface only; External Mixer restores stock; diagnostics excluded",
        "persistence": "Scene reserved fields; latest routes through stock system autosave; see docs/ROUTING_STORAGE.md",
        "return_policy": "Copies raw Return; original Return bus and AUX controls remain unchanged",
        "limits": ["DSP execution and physical audio not emulated",
                   "Stereo pair writes are sequential, not frame-atomic; no click-free guarantee",
                   "Original DSP programming-port handshake/timing retained, not hardware measured",
                   "Routed analog inputs retain their physical ADC gain before destination DSP gain"],
    }
