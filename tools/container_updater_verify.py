#!/usr/bin/env python3
"""Execute original updater parsing/checksum/write-loop code with file/flash stubs.

No USB or physical flash access occurs. File operations and flash I/O are modeled
in memory; arithmetic, comparisons, checksums and loop bounds run as the original
ARM instructions. This verifies the software path, not a safe recovery procedure.
"""
from __future__ import annotations

import argparse
import json
import struct
import time
from pathlib import Path

import unicorn
from unicorn.arm_const import (
    UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC,
    UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
)

from container_tool import (COMPONENTS, COMPONENT_BY_NAME, ORIGINAL_SHA256,
                            FormatError, component_unpacked, repack_image, sha256)
from memory_map import recover


class UpdaterHarness:
    ARENA = 0x70000000
    INFO = ARENA + 0x1000
    BUFFER = ARENA + 0x10000
    SENTINEL = ARENA + 0xFF000
    STACK = 0x0103E000
    FLASH = 0x03000000
    FILE_HANDLE = 1

    def __init__(self, original: bytes, input_file: bytes | None = None,
                 *, corrupt_write: bool = False):
        if sha256(original) != ORIGINAL_SHA256:
            raise FormatError("Original updater fixture hash mismatch")
        self.input_file = original if input_file is None else input_file
        self.original = original
        self.cursor = 0
        self.errors: list[int] = []
        self.writes: list[tuple[int, int]] = []
        self.progress: list[tuple[int, int]] = []
        self.corrupt_write = corrupt_write
        self.emulator = unicorn.Uc(unicorn.UC_ARCH_ARM,
                                   unicorn.UC_MODE_THUMB | unicorn.UC_MODE_MCLASS)
        emu = self.emulator
        for start, size in ((0x01000000, 0x40000), (self.FLASH, 0x400000),
                            (0x20000000, 0x100000), (0x60000000, 0x800000),
                            (self.ARENA, 0x100000)):
            emu.mem_map(start, size)
        app = component_unpacked(original, COMPONENT_BY_NAME["updater"])
        emu.mem_write(0x60000000, app)
        mapping = recover(app)
        for operation in mapping["operations"]:
            length = operation["length"]
            if not length:
                continue
            if operation["kind"] == "copy":
                source = operation["source"] - 0x60000000
                data = app[source:source + length]
            else:
                data = b"\0" * length
            emu.mem_write(operation["destination"], data)
        emu.mem_write(self.FLASH, original[:0x400000])
        emu.mem_write(self.ARENA, b"MX1_UPD.BIN\0")
        # The writer's filename buffer; value comes from literal at 0x60005990.
        emu.mem_write(0x6002D554, b"MX1_UPD.BIN\0")
        self.stub_addresses = {
            0x60003278: "flash_bus_mode",
            0x60003478: "flash_read",
            0x60006D04: "file_stat",
            0x60006C88: "file_open",
            0x60006CF6: "file_seek",
            0x60006CE8: "file_read",
            0x60006C78: "file_close",
            0x60005186: "error_notification",
            0x6000519C: "write_progress",
            0x600051B6: "checksum_notification",
            0x600051FA: "flash_erase_program_sector",
        }
        # Address-filtered hooks avoid a Python callback for every instruction.
        for address in self.stub_addresses:
            emu.hook_add(unicorn.UC_HOOK_CODE, self._stub, begin=address, end=address)

    def _arguments(self) -> tuple[int, int, int, int]:
        return tuple(self.emulator.reg_read(reg) for reg in
                     (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))

    def _return(self, value: int = 0) -> None:
        self.emulator.reg_write(UC_ARM_REG_R0, value & 0xFFFFFFFF)
        self.emulator.reg_write(UC_ARM_REG_PC, self.emulator.reg_read(UC_ARM_REG_LR))

    def _stub(self, emulator, address, size, user_data):
        name = self.stub_addresses[address]
        a, b, c, d = self._arguments()
        if name in ("flash_bus_mode", "file_close", "checksum_notification"):
            self._return()
        elif name == "flash_read":
            if a + b > 0x400000:
                raise AssertionError("Firmware checksum attempted an out-of-range flash read")
            emulator.mem_write(c, bytes(emulator.mem_read(self.FLASH + a, b)))
            self._return()
        elif name == "file_stat":
            emulator.mem_write(b, struct.pack("<5I", len(self.input_file), 0, 0, 0, 0))
            self._return()
        elif name == "file_open":
            self.cursor = 0
            self._return(self.FILE_HANDLE)
        elif name == "file_seek":
            offset = b if b < 0x80000000 else b - 0x100000000
            base = 0 if c == 0 else self.cursor if c == 1 else len(self.input_file) if c == 2 else None
            if base is None or base + offset < 0:
                self._return(0xFFFFFFFF)
            else:
                self.cursor = base + offset
                self._return()
        elif name == "file_read":
            requested = b * c
            data = self.input_file[self.cursor:self.cursor + requested]
            if data:
                emulator.mem_write(a, data)
            self.cursor += len(data)
            self._return(len(data) // b if b else 0)
        elif name == "error_notification":
            self.errors.append(a)
            self._return()
        elif name == "write_progress":
            self.progress.append((a, b))
            self._return()
        elif name == "flash_erase_program_sector":
            flash_offset = a * c
            if flash_offset + c > 0x400000:
                raise AssertionError("Out-of-range simulated flash write")
            data = bytes(emulator.mem_read(b, c))
            if self.corrupt_write:
                data = bytes([data[0] ^ 1]) + data[1:]
            emulator.mem_write(self.FLASH + flash_offset, data)
            self.writes.append((flash_offset, c))
            self._return()
        else:
            raise AssertionError(name)

    def call(self, address: int, *args: int) -> int:
        emu = self.emulator
        emu.reg_write(UC_ARM_REG_SP, self.STACK)
        emu.reg_write(UC_ARM_REG_LR, self.SENTINEL | 1)
        for register, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                                   (*args[:4], 0, 0, 0, 0)):
            emu.reg_write(register, value)
        for index, value in enumerate(args[4:]):
            emu.mem_write(self.STACK + index * 4, struct.pack("<I", value))
        emu.emu_start(address | 1, self.SENTINEL, count=200_000_000)
        if emu.reg_read(UC_ARM_REG_PC) != self.SENTINEL:
            raise AssertionError(f"Firmware function {address:#x} failed to return")
        return emu.reg_read(UC_ARM_REG_R0)

    def parse_trailer(self) -> tuple[int, tuple[int, int, int]]:
        result = self.call(0x600056D0, self.INFO, self.ARENA)
        return result, struct.unpack("<3I", self.emulator.mem_read(self.INFO, 12))

    def check_component(self, component_name: str) -> tuple[int, int]:
        component = COMPONENT_BY_NAME[component_name]
        labels = {"updater": 0x60022A8C, "subcpu": 0x60022A9D,
                  "app_main": 0x60022AAE, "app_usb": 0x60022ABF}
        self.emulator.mem_write(self.INFO, b"\0" * 4)
        result = self.call(0x60005232, component.offset, labels[component_name],
                           self.INFO, self.BUFFER, 4096)
        return result, struct.unpack("<I", self.emulator.mem_read(self.INFO, 4))[0]


def verify(original: bytes) -> dict:
    start = time.monotonic()
    checks = []
    harness = UpdaterHarness(original)
    result, info = harness.parse_trailer()
    if result != 0 or info != (64, 767, 4096):
        raise AssertionError("Actual updater trailer parser did not match inferred fields")
    checks.append({"name": "actual trailer parser accepts original and returns start/end/block size",
                   "passed": True, "fields": list(info)})

    for offset, changed in ((0x40000C, 0x41), (0x400008, 0)):
        invalid = bytearray(original)
        if offset == 0x400008:
            invalid[offset:offset + 4] = b"\0" * 4
        else:
            invalid[offset] = changed
        bad = UpdaterHarness(original, bytes(invalid))
        result, _ = bad.parse_trailer()
        if result != 0xFFFFFFFF or bad.errors != [3]:
            raise AssertionError("Invalid trailer was not rejected by actual code")
    checks.append({"name": "actual parser rejects wrong payload size and zero block size",
                   "passed": True})

    result = harness.call(0x60005458, harness.FILE_HANDLE, 0x40000, 0x300000)
    if result != 2:
        raise AssertionError("Starting SUB-CPU tag not accepted")
    invalid_tag = bytearray(original)
    invalid_tag[0x40000] ^= 1
    bad = UpdaterHarness(original, bytes(invalid_tag))
    if bad.call(0x60005458, bad.FILE_HANDLE, 0x40000, 0x300000) != 5:
        raise AssertionError("Wrong starting tag not rejected")
    checks.append({"name": "actual pre-write tag check accepts original and rejects changed SUB-CPU tag",
                   "passed": True, "accepted_component_code": 2})

    sums = []
    for component in COMPONENTS:
        result, checksum = harness.check_component(component.name)
        if result != 1:
            raise AssertionError(f"Original {component.name} failed actual checksum routine")
        expected = struct.unpack_from("<I", original, component.offset + 0x34)[0]
        if checksum != expected:
            raise AssertionError("Actual checksum differs from header")
        sums.append({"component": component.name, "checksum": checksum})
    checks.append({"name": "actual flash checksum routine validates all four original components",
                   "passed": True, "checksums": sums})

    decoded = bytearray(component_unpacked(original, COMPONENT_BY_NAME["app_usb"]))
    decoded[0x123] ^= 0x80  # Codec/write-plan fixture, never a working firmware build.
    synthetic, _ = repack_image(original, {"app_usb": bytes(decoded)})
    writer = UpdaterHarness(original, synthetic)
    result = writer.call(0x60005584, 64, 767, 4096, writer.BUFFER, 4096)
    if result != 1 or writer.errors:
        raise AssertionError("Actual writer loop failed against in-memory I/O")
    expected_writes = [(index * 4096, 4096) for index in range(64, 768)]
    if writer.writes != expected_writes:
        raise AssertionError("Actual flash write bounds differ from trailer interpretation")
    flashed = bytes(writer.emulator.mem_read(writer.FLASH, 0x400000))
    expected_flash = original[:0x40000] + synthetic[0x40000:0x300000] + original[0x300000:0x400000]
    if flashed != expected_flash:
        raise AssertionError("Simulated flashed content differs or protected region was changed")
    for component in COMPONENTS:
        if writer.check_component(component.name)[0] != 1:
            raise AssertionError(f"Repacked {component.name} failed original post-write checksum")
    checks.append({"name": "actual block writer and readback comparison process synthetic repack; all post-write checksums pass",
                   "passed": True, "blocks_written": len(writer.writes),
                   "first_flash_offset": writer.writes[0][0],
                   "flash_end_exclusive": writer.writes[-1][0] + 4096,
                   "preserved_ranges": [[0, 0x40000], [0x300000, 0x400000]],
                   "scope": "Flash erase/program and file I/O are stubs; original loop, arithmetic and memcmp execute"})

    corrupted_address = writer.FLASH + 0x200040
    writer.emulator.mem_write(corrupted_address,
        bytes([bytes(writer.emulator.mem_read(corrupted_address, 1))[0] ^ 1]))
    if writer.check_component("app_usb")[0] != 0:
        raise AssertionError("Actual checksum routine accepted corrupted programmed byte")
    checks.append({"name": "actual post-write checksum rejects one corrupted stored byte", "passed": True})

    bad_write = UpdaterHarness(original, synthetic, corrupt_write=True)
    result = bad_write.call(0x60005584, 64, 767, 4096, bad_write.BUFFER, 4096)
    if result != 0 or bad_write.errors != [7] or len(bad_write.writes) != 1:
        raise AssertionError("Actual readback failure did not stop the write loop")
    checks.append({"name": "actual readback comparison stops on first simulated sector mismatch",
                   "passed": True, "error_code": 7})

    return {
        "status": "passed", "input_sha256": sha256(original),
        "check_groups": len(checks), "checks": checks,
        "host_wall_seconds": round(time.monotonic() - start, 3),
        "unmodified_original_functions_executed": [
            "0x600056d0 trailer parser", "0x60005458 component-tag gate",
            "0x60005232 stored-byte checksum", "0x60005584 sector write loop",
            "0x600051d0 readback comparison", "0x6002173c memcmp"],
        "stubbed_environment": ["File stat/open/seek/read/close", "Flash read",
                                 "Flash erase/program", "Bus-mode changes", "UI notifications"],
        "not_verified": ["Real flash controller behavior", "Power-loss recovery",
                         "Boot ROM and full boot", "Sub-CPU programming",
                         "USB/audio behavior", "Physical device acceptance"],
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
