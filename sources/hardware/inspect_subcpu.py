#!/usr/bin/env python3
"""Reproduce the panel-MCU evidence from this exact user-supplied MX-1 image.

This is inspection only; it never writes to the input or a device.  The optional
Capstone disassembly is of explicit routines, not a claim that every byte is code.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

FIRMWARE_SHA256 = "26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e"
OFFSET, SIZE, BASE = 0x40040, 0x4014, 0x08000000
IRQ_NAMES = {
    0: "WWDG", 1: "PVD", 2: "TAMPER", 3: "RTC", 4: "FLASH", 5: "RCC",
    **{i + 6: f"EXTI{i}" for i in range(5)},
    **{i + 10: f"DMA1_Channel{i}" for i in range(1, 8)},
    18: "ADC1", 23: "EXTI9_5", 24: "TIM1_BRK_TIM15", 25: "TIM1_UP_TIM16",
    26: "TIM1_TRG_COM_TIM17", 27: "TIM1_CC", 28: "TIM2", 29: "TIM3", 30: "TIM4",
    31: "I2C1_EV", 32: "I2C1_ER", 33: "I2C2_EV", 34: "I2C2_ER",
    35: "SPI1", 36: "SPI2", 37: "USART1", 38: "USART2", 39: "USART3",
    40: "EXTI15_10", 41: "RTC_Alarm", 42: "CEC", 54: "TIM6_DAC", 55: "TIM7",
}
PERIPHERALS = {
    0x40010800: "GPIOA", 0x40010c00: "GPIOB", 0x40011000: "GPIOC",
    0x40011400: "GPIOD", 0x40011800: "GPIOE", 0x40012400: "ADC1",
    0x40012c00: "TIM1", 0x40013800: "USART1", 0x40021000: "RCC",
}


def analyze(image):
    digest = hashlib.sha256(image).hexdigest()
    if digest != FIRMWARE_SHA256:
        raise ValueError("Firmware SHA-256 differs: do not reuse these fixed offsets")
    sub = image[OFFSET:OFFSET + SIZE]
    words = struct.unpack_from("<72I", sub)
    if words[:2] != (0x200015b0, 0x08000315):
        raise ValueError("Unexpected SUB-CPU vectors")
    vectors = []
    for irq in range(56):
        value = words[16 + irq]
        reserved = irq not in IRQ_NAMES
        if reserved != (value == 0):
            raise ValueError(f"Vector {irq} does not match STM32F100xB layout")
        vectors.append({"irq": irq, "vector_offset": f"0x{4*(16+irq):x}",
                        "stm32f100_role": IRQ_NAMES.get(irq, "reserved"),
                        "handler": f"0x{value:08x}",
                        "custom_handler": value not in (0, 0x0800032f)})
    pool_locations = []
    for off in range(0, len(sub)-3, 4):
        value = struct.unpack_from("<I", sub, off)[0]
        if value in PERIPHERALS:
            pool_locations.append({"image_offset": f"0x{off:x}",
                                   "address": f"0x{value:08x}",
                                   "role": PERIPHERALS[value]})
    return {
        "input_sha256": digest, "subcpu_sha256": hashlib.sha256(sub).hexdigest(),
        "input_offset": hex(OFFSET), "size_bytes": SIZE, "load_address": hex(BASE),
        "initial_sp": hex(words[0]), "reset_vector": hex(words[1]),
        "vector_layout": "matches ST STM32F100xB low/medium-density value-line template",
        "vectors": vectors, "peripheral_literal_locations": pool_locations,
        "observed_scatter_records": [
            {"source": hex(a), "destination": hex(b), "length": c, "copy_routine": hex(d)}
            for a,b,c,d in struct.iter_unpack("<4I", sub[0x3f34:0x3f54])
        ],
        "evidence_limits": [
            "Vector/peripheral agreement is strong identification, not a PCB marking inspection.",
            "Literal occurrence alone is not proof of execution; see startup call chain and decompilation.",
            "STM32F100V8 or VB package hypothesis also depends on live GPIOE/PD pin usage.",
        ],
    }, sub


def disassemble(sub):
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
    from capstone.arm import ARM_OP_MEM, ARM_REG_PC
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    md.detail = True
    output = []
    for name, start, end in [
        ("Reset_Handler",0x314,0x31c), ("GPIO_init",0x884,0xa1e),
        ("clock_enable",0xc18,0xc64), ("SystemInit",0xc64,0xd26),
        ("USART1_init",0x1354,0x13c4), ("main_startup",0x2934,0x2976),
    ]:
        output.append(f"\n; {name} 0x{BASE+start:08x}")
        for ins in md.disasm(sub[start:end], BASE+start):
            extra = ""
            if (ins.mnemonic.startswith("ldr") and len(ins.operands)>1 and
                ins.operands[1].type == ARM_OP_MEM and ins.operands[1].mem.base == ARM_REG_PC):
                pool = ((ins.address+4)&~3)+ins.operands[1].mem.disp
                if BASE <= pool < BASE+len(sub)-3:
                    value=struct.unpack_from("<I",sub,pool-BASE)[0]
                    extra=f" ; [0x{pool:08x}] = 0x{value:08x}"
            output.append(f"{ins.address:08x}: {ins.bytes.hex():12s} {ins.mnemonic:8s} {ins.op_str}{extra}")
    return "\n".join(output)+"\n"


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("firmware",type=Path)
    p.add_argument("output",type=Path)
    p.add_argument("--disassemble", action="store_true", help="also emit selected Capstone evidence")
    a=p.parse_args()
    evidence,sub=analyze(a.firmware.read_bytes())
    a.output.mkdir(parents=True,exist_ok=True)
    (a.output/"subcpu_evidence.json").write_text(json.dumps(evidence,indent=2)+"\n")
    (a.output/"subcpu.bin").write_bytes(sub)
    if a.disassemble:
        (a.output/"subcpu_selected.asm").write_text(disassemble(sub))
    print(json.dumps({"subcpu_sha256":evidence["subcpu_sha256"],"size_bytes":SIZE,
                      "irq_layout_verified":True,"output":str(a.output)}))


if __name__ == "__main__":
    main()
