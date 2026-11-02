#!/usr/bin/env python3
"""Verify the original USB driver's early registration and binding filter.

Executes original binder/list/probe instructions. RTOS lock/unlock and probe
queue delivery are stubbed; USB enumeration and actual streaming are not modeled.
"""
import argparse
import json
import struct
from pathlib import Path

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_LR, UC_ARM_REG_PC
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine


def binding_case(image, device_class, interface_class, *, control_mask=None):
    machine = Machine(image)
    driver, linked_list, interface, device = 0x20017000, 0x20017100, 0x20017200, 0x20017300
    registration = bytearray(image[0x2B0AC:0x2B0BC])
    if control_mask is not None:
        registration[5] = 0xFF
        registration[6] = control_mask
    machine.write(driver, b"\0" * 8 + registration + b"\0" * 4)
    machine.write(linked_list, struct.pack("<3I", driver, driver, 1))
    machine.write(0x6002B178, struct.pack("<I", linked_list))
    machine.write(interface, b"\0" * 0x40)
    machine.write(interface + 8, struct.pack("<I", device))
    machine.write(interface + 0x10, bytes([interface_class, 2, 0, 1, 0, 1]))
    machine.write(device, b"\0" * 0x100)
    machine.write(device + 0x0C, bytes([device_class]))
    machine.write(device + 0x10, struct.pack("<HH", 0x1234, 0x5678))
    events = []

    def stub(emu, address, size, user_data):
        if address == 0x60007E10:
            pointer = emu.reg_read(UC_ARM_REG_R0)
            events.append(machine.read(pointer, 12).hex())
        emu.reg_write(UC_ARM_REG_R0, 0)
        emu.reg_write(UC_ARM_REG_PC, emu.reg_read(UC_ARM_REG_LR))

    for address in (0x60014AE4, 0x010003B8, 0x60007E10):
        machine.uc.hook_add(UC_HOOK_CODE, stub, begin=address, end=address)
    result, _ = machine.call(0x6000EE16, interface)
    attached = struct.unpack("<I", machine.read(interface + 0x0C, 4))[0]
    return {"device_class": device_class, "interface_class": interface_class,
            "vendor_id": 0x1234, "product_id": 0x5678,
            "mask": registration[6], "result": result,
            "driver_attached": attached == driver + 8,
            "probe_events": len(events)}


def verify(original):
    if sha256(original) != ORIGINAL_SHA256:
        raise ValueError("Unexpected original firmware")
    image = component_unpacked(original, COMPONENT_BY_NAME["app_usb"])
    record = image[0x2B0AC:0x2B0BC]
    assert record == bytes.fromhex("00000000000000007d83006091830060")
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    registration_code = [f"{i.address:08x}: {i.bytes.hex():10s} {i.mnemonic} {i.op_str}"
                         for i in md.disasm(image[0x8958:0x8982], 0x60008958)]
    instructions = list(md.disasm(image[0x8974:0x897A], 0x60008974))
    assert instructions[0].mnemonic == "ldr" and instructions[1].op_str == "#0x600093f8"
    assert struct.unpack_from("<I", image, 0x8B80)[0] == 0x6002B0AC
    cases = []
    for device_class, interface_class in ((0, 1), (1, 1), (0xEF, 1), (0xFF, 0xFF), (0, 8)):
        result = binding_case(image, device_class, interface_class)
        assert result["result"] == 0 and result["driver_attached"] and result["probe_events"] == 1
        cases.append(result)
    negative = binding_case(image, 0, 1, control_mask=8)
    assert negative["result"] == 0xFFFFFFFF and not negative["driver_attached"] and negative["probe_events"] == 0
    return {
        "status": "passed", "input_sha256": sha256(original),
        "registration_record_address": "0x6002b0ac", "registration_record_hex": record.hex(),
        "match_flags": {"VID": False, "PID": False, "device_class": False, "interface_class": False},
        "probe_callback": "0x6000837d", "remove_callback": "0x60008391",
        "registration_task": "0x60008958", "registration_call": "0x60008976",
        "registration_disassembly": registration_code,
        "original_binder_cases": cases,
        "negative_control_with_artificial_interface_class_filter": negative,
        "conclusion": "Original audio driver registration is wildcard; no earlier vendor/class registration patch is needed",
        "limitations": "Probe queue delivery and RTOS critical sections are stubbed; downstream selection, hardware USB and streaming are not tested here",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = verify(args.input.read_bytes())
    text = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
