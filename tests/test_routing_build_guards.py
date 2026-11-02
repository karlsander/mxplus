"""Routing patch guards and actual Thumb veneer behavior, without device I/O."""
from pathlib import Path
import struct
import sys
import tempfile
import unittest

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5,
                               UC_ARM_REG_R6, UC_ARM_REG_R7, UC_ARM_REG_R8,
                               UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
                               UC_ARM_REG_R12, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC, UC_ARM_REG_APSR)

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from firmware_patch import inject
from build_firmware import absolute_jump, build, patch_ui, ENTRY, LIMIT
from container_tool import FormatError


class RoutingGuardTests(unittest.TestCase):
    def test_absolute_veneer_preserves_registers_stack_and_flags(self):
        for address in (0x60013354, 0x60013356):
            with self.subTest(address=hex(address)):
                u = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
                u.mem_map(0x60013000, 0x1000)
                u.mem_map(0x0100F000, 0x1000)
                target = 0x0100F700
                u.mem_write(address, absolute_jump(address, target))
                regs = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                        UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
                        UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
                        UC_ARM_REG_R12, UC_ARM_REG_SP, UC_ARM_REG_LR)
                expected = {reg: 0x20000000 + index * 16 for index, reg in enumerate(regs)}
                for reg, value in expected.items():
                    u.reg_write(reg, value)
                u.reg_write(UC_ARM_REG_APSR, 0xA8000000)
                u.emu_start(address | 1, target, count=4)
                self.assertEqual(u.reg_read(UC_ARM_REG_PC), target)
                self.assertEqual({reg: u.reg_read(reg) for reg in regs}, expected)
                self.assertEqual(u.reg_read(UC_ARM_REG_APSR) & 0xF8000000, 0xA8000000)

    def test_ui_hook_rejects_wrong_original_sites_and_double_application(self):
        original = bytearray((ROOT / "analysis/container_app_main.bin").read_bytes())
        symbols = {"mx1_route_ui_event": ENTRY | 1, "mx1_route_ui_display": ENTRY + 0x80 | 1}
        for offset in (0xF5D8, 0x13356):
            with self.subTest(offset=hex(offset)):
                damaged = original.copy()
                damaged[offset] ^= 1
                with self.assertRaisesRegex(FormatError, "original bytes"):
                    patch_ui(damaged, symbols, [])
        image = original.copy()
        changes = []
        patch_ui(image, symbols, changes)
        self.assertEqual(len(changes), 2)
        self.assertEqual(image[0xF5D8:0xF5DC], struct.pack("<I", ENTRY | 1))
        self.assertEqual(image[0x13356:0x13360], absolute_jump(0x60013356, ENTRY + 0x80))
        with self.assertRaisesRegex(FormatError, "original bytes"):
            patch_ui(image, symbols, [])

    def test_extension_respects_exact_reviewed_sram_boundary(self):
        original = (ROOT / "analysis/container_app_main.bin").read_bytes()
        maximum = LIMIT - ENTRY
        image, record = inject(original, bytes(maximum))
        self.assertEqual(record["runtime_address"] + record["insert_length"], LIMIT)
        self.assertEqual(len(image), len(original) + maximum)
        for size in (maximum + 4, 1, maximum - 1):
            with self.subTest(size=size), self.assertRaises(FormatError):
                inject(original, bytes(size))

    def test_wrong_firmware_is_rejected_before_compilation_or_output_creation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            firmware = path / "wrong.bin"
            firmware.write_bytes(b"wrong revision")
            with self.assertRaisesRegex(FormatError, "SHA-256 mismatch"):
                build(firmware, path / "output")
            self.assertFalse((path / "output").exists())


if __name__ == "__main__":
    unittest.main()
