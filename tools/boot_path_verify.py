#!/usr/bin/env python3
"""Trace the original boot selector/loader and routing cold startup offline.

Executes unchanged main-boot instructions from their reset vector. Board setup,
the inter-processor transport and its completion are explicit stub boundaries.
The selector input is supplied, not claimed to be a measured TAP electrical net.
Never accesses a mixer or writes firmware to a device.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS
from elftools.elf.elffile import ELFFile
from unicorn import (Uc, UcError, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS,
                     UC_HOOK_CODE, UC_HOOK_MEM_READ_UNMAPPED)
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1,
    UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP)

from container_tool import (BOOT_BASE, COMPONENT_BY_NAME, ORIGINAL_SHA256,
    component_unpacked, inspect_image, sha256)
from arm_machine import BASE, Machine
from memory_map import recover
from routing_audio_verify import AudioMachine

ROOT = Path(__file__).resolve().parents[1]
FLASH = 0x03000000
SELECTOR = 0x425A0080
RETURN = 0x0FFF0000


def word(value: int) -> bytes:
    return struct.pack('<I', value)


class BootMachine:
    """Only board-facing boundaries are replaced; selector and loader execute."""

    def __init__(self, image: bytes, selector: int, *, applications_mapped=True):
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        flash_size = 0x400000 if applications_mapped else 0x40000
        for address, size in ((BOOT_BASE, 0x40000), (0x02003000, 0x1000), (FLASH, flash_size),
                (BASE, 0x200000), (0x20000000, 0x20000),
                (SELECTOR & ~0xFFF, 0x1000), (RETURN, 0x1000)):
            self.uc.mem_map(address, size)
        self.uc.mem_write(FLASH, image[:flash_size])
        size = struct.unpack_from('<I', image, 0x0C)[0]
        self.uc.mem_write(BOOT_BASE, image[0x30:0x30 + size])
        self.uc.mem_write(SELECTOR, word(selector))
        self.stubs = []
        self.loads = []
        self.transfers = []
        self.faults = []
        self.normal_setup = 0
        self.usb_handoff = None
        boundaries = (0x01000540, 0x0100037E, 0x01001346, 0x0100095E,
                      0x01000970, 0x01001ABC, 0x01001AEA, RETURN + 0x100,
                      0x01000448, 0x010002D8)
        for address in boundaries:
            self.uc.hook_add(UC_HOOK_CODE, self.boundary,
                             begin=address, end=address)
        self.uc.hook_add(UC_HOOK_MEM_READ_UNMAPPED, self.unmapped)

    def ret(self, result=0):
        self.uc.reg_write(UC_ARM_REG_R0, result)
        self.uc.reg_write(UC_ARM_REG_PC, self.uc.reg_read(UC_ARM_REG_LR))

    def unmapped(self, uc, access, address, size, value, user):
        self.faults.append({'address': hex(address), 'size': size})
        return False

    def boundary(self, uc, address, size, user):
        arg0, arg1 = (uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1))
        if address == 0x010002D8:
            # The stock reset-context run raises UC_ERR_EXCEPTION on the BX
            # into SDRAM, before a target code hook fires. Board setup is not
            # modeled. Inspect the final target here and test application
            # startup independently, rather than claiming a continuous boot.
            assert arg0 == BASE | 1
            uc.emu_stop()
            return
        if address == 0x01000448:
            self.loads.append(hex(arg0))
            return  # Execute the complete original loader and LZSS decoder.
        self.stubs.append(hex(address))
        if address == 0x01000540:
            # Board initialization normally provides this ROM-service table.
            uc.mem_write(0x02003018, word(RETURN + 0x101))
        elif address == 0x01000970:
            descriptor = bytes(uc.mem_read(arg1, 0x20))
            length = struct.unpack_from('<I', descriptor, 0x0C)[0]
            source = struct.unpack_from('<I', descriptor, 0x14)[0]
            destination = struct.unpack_from('<I', descriptor, 0x1C)[0]
            data = bytes(uc.mem_read(source, length))
            self.transfers.append({'source': hex(source),
                'destination': hex(destination), 'length': length,
                'sha256': sha256(data)})
            # Model completed peer transfer, not the second processor itself.
            uc.mem_write(0x01010040, word(0))
        elif address == 0x01001ABC:
            self.normal_setup += 1
        elif address == 0x01001AEA:
            header = bytes(uc.mem_read(arg0, 0x40))
            length = struct.unpack_from('<I', header, 0x3C)[0]
            self.usb_handoff = {'header': hex(arg0), 'decoded_bytes': length,
                'sha256': sha256(bytes(uc.mem_read(BASE, length)))}
        self.ret()

    def run(self):
        reset = struct.unpack('<I', bytes(self.uc.mem_read(BOOT_BASE + 4, 4)))[0]
        self.uc.emu_start(reset, RETURN, timeout=30_000_000, count=60_000_000)
        assert self.uc.reg_read(UC_ARM_REG_PC) == 0x010002D8, 'Boot did not reach selected handoff'
        return {'loads': self.loads, 'transfers': self.transfers,
            'normal_peer_setup_calls': self.normal_setup,
            'usb_application_handoff': self.usb_handoff,
            'stub_calls': self.stubs, 'handoff_instruction': '0x010002d8: bx r0',
            'selected_entry': hex(self.uc.reg_read(UC_ARM_REG_R0))}


def audit(original: bytes, candidate: bytes, build: dict, applied_address: int) -> dict:
    assert sha256(original) == ORIGINAL_SHA256
    assert build['input_sha256'] == ORIGINAL_SHA256
    assert sha256(candidate) == build['container_sha256']
    stock_info, candidate_info = inspect_image(original), inspect_image(candidate)
    assert stock_info['update_plan'] == candidate_info['update_plan']
    assert original[:0x80000] == candidate[:0x80000]
    assert original[0x200000:] == candidate[0x200000:]
    for name in ('updater', 'subcpu', 'app_usb'):
        component = COMPONENT_BY_NAME[name]
        assert component_unpacked(original, component) == component_unpacked(candidate, component)
    checks = [{'name': 'Only the main application slot differs; boot/updater/panel/USB/trailer preserved',
               'status': 'pass'}]

    # The reset entry and selector execute, with BOTH application regions
    # physically absent from the emulator's address map. Reads would fault.
    updater = component_unpacked(original, COMPONENT_BY_NAME['updater'])
    cases = []
    for name, image in (('stock', original), ('routing', candidate)):
        machine = BootMachine(image, 0, applications_mapped=False)
        trace = machine.run()
        assert machine.loads == ['0x3010000'] and not machine.faults
        assert machine.normal_setup == 0 and machine.usb_handoff is None
        assert bytes(machine.uc.mem_read(BASE, len(updater))) == updater
        assert len(machine.transfers) == 2
        assert machine.transfers[0]['source'] == '0x3008030'
        assert machine.transfers[0]['destination'] == '0x1000000'
        assert machine.transfers[0]['length'] == 0x1040
        assert machine.transfers[0]['sha256'] == stock_info['boot_images'][1]['sha256']
        assert machine.transfers[1]['length'] == 4
        cases.append({'image': name, 'application_flash': 'unmapped', **trace})
    checks.append({'name': 'Reset selects and decodes updater with both application regions unmapped',
                   'status': 'pass', 'cases': cases,
                   'decoded_updater_sha256': sha256(updater)})

    # Negative control proves the missing application really is inaccessible.
    missing = BootMachine(original, 1, applications_mapped=False)
    try:
        missing.run()
    except UcError:
        assert missing.faults and missing.faults[0]['address'] == '0x320003c'
    else:
        raise AssertionError('Normal branch unexpectedly ran without application flash')
    checks.append({'name': 'Normal-branch negative control faults on missing USB application header',
                   'status': 'pass', 'faults': missing.faults})

    cases = []
    for name, image in (('stock', original), ('routing', candidate)):
        machine = BootMachine(image, 1)
        trace = machine.run()
        main = component_unpacked(image, COMPONENT_BY_NAME['app_main'])
        usb = component_unpacked(image, COMPONENT_BY_NAME['app_usb'])
        assert bytes(machine.uc.mem_read(BASE, len(main))) == main
        assert machine.loads == ['0x3200000', '0x3080000']
        assert machine.usb_handoff['sha256'] == sha256(usb)
        assert machine.normal_setup == 1
        cases.append({'image': name, 'decoded_main_sha256': sha256(main), **trace})
    checks.append({'name': 'Original main-boot loader decodes complete stock and routing applications',
                   'status': 'pass', 'cases': cases})

    # Unlike pre-applying the scatter map, execute the actual application
    # startup over dirty SRAM, then inspect initialized routing data and gaps.
    main = component_unpacked(candidate, COMPONENT_BY_NAME['app_main'])
    assert sha256(main) == build['patched_app_sha256']
    assert sha256(component_unpacked(original, COMPONENT_BY_NAME['app_main'])) == build['original_app_sha256']
    insertion = build['scatter_extension']
    assert sha256(main[insertion['insert_offset']:insertion['insert_offset'] +
                       insertion['insert_length']]) == build['extension_sha256']
    symbols = build['symbols']
    cold_cases = []
    for pattern in (0x55, 0xAA):
        machine = Machine(main, scatter=False)
        machine.write(BOOT_BASE, bytes([pattern]) * 0x18000)
        machine.write(0x01020000, bytes([pattern]) * 0x10000)
        machine.write(0x20000000, bytes([pattern]) * 0x20000)
        machine.uc.reg_write(UC_ARM_REG_SP, 0x2001FFF0)
        machine.uc.emu_start(BASE | 1, BASE + 0x7E, timeout=5_000_000, count=3_000_000)
        assert machine.uc.reg_read(UC_ARM_REG_PC) == BASE + 0x7E
        for index, op in enumerate(recover(main)['operations']):
            if op['length']:
                expected = (main[op['source'] - BASE:op['source'] - BASE + op['length']]
                            if op['kind'] == 'copy' else bytes(op['length']))
                if index == 3:
                    from uac2_design import prototype_configuration
                    expected = bytes(op['length'] - 516) + prototype_configuration(preserve_modes=True) + bytes(161)
                assert machine.read(op['destination'], op['length']) == expected
        state = symbols['mx1_route_state']
        assert machine.read(state, 11) == bytes(11)
        assert machine.read(applied_address, 11) == bytes(11)
        start = build['scatter_extension']['runtime_address']
        end = start + build['scatter_extension']['code_length']
        assert machine.read(end, 0x01010000 - end) == bytes([pattern]) * (0x01010000 - end)
        cold_cases.append({'dirty_byte': hex(pattern), 'routes': 'all Auto',
            'desired_and_applied_state_zero': True,
            'extension_end': hex(end), 'untouched_gap_bytes': 0x01010000 - end})
    checks.append({'name': 'Actual cold startup installs initialized route state without relying on zero SRAM',
                   'status': 'pass', 'cases': cold_cases})

    # Execute the actual RTOS variable-pool initialization, not just a scan for
    # plausible unused SRAM. ICSR=0 supplies thread mode to the original query.
    # Pool names, bases and lengths come from the original initialized records.
    pool_cases = []
    for name, image in (('stock', component_unpacked(original, COMPONENT_BY_NAME['app_main'])),
                        ('routing', main)):
        machine = Machine(image)
        machine.uc.mem_map(0xE000E000, 0x2000)
        records = struct.unpack('<8I', machine.read(0x0100F234, 0x20))
        assert records == (1, 0, 0x8000, 0x01020000, 2, 0, 0x1000, 0x01013E18)
        extension_before = machine.read(0x0100F6A4, 0x95C)
        machine.call(0x01006338, count=500_000)
        assert machine.read(0x0100F6A4, 0x95C) == extension_before
        pools = []
        for control, length, base in ((0x01014E18, 0x8000, 0x01020000),
                                      (0x01014E5C, 0x1000, 0x01013E18)):
            assert struct.unpack('<2I', machine.read(control + 0x1C, 8)) == (length, base)
            assert base >= 0x01010000
            pools.append({'control': hex(control), 'base': hex(base),
                          'length': length, 'end_exclusive': hex(base + length)})
        pool_cases.append({'image': name, 'pools': pools, 'extension_unchanged': True})
    checks.append({'name': 'Actual original RTOS pool initialization preserves extension and excludes its SRAM',
                   'status': 'pass', 'initializer_runtime': '0x01006338',
                   'initializer_decoded_offset': '0xd6bc4',
                   'configuration_runtime': '0x0100f234',
                   'configuration_decoded_offset': '0xdfac0', 'cases': pool_cases,
                   'modeled': 'SCB ICSR reads zero (thread mode); no RTOS initializer function stubbed'})

    # Verify initial event-8 handling is inert in every normal/diagnostic DSP
    # mode and every mixer mode. Repeated drains must not invent routes.
    cases = []
    for dsp_mode in (0, 1, 2, 3, 4, 0xFFFFFFFF):
        for mixer_mode in (0, 1, 2):
            machine = AudioMachine(main, symbols, b'')
            machine.write(0x6051DEB8, word(dsp_mode))
            machine.parameters[0x19] = mixer_mode
            for _ in range(3):
                added, _ = machine.drain()
                assert added == 0
            assert not machine.posts and not machine.commands
            assert machine.read(symbols['mx1_route_state'], 11) == bytes(11)
            cases.append({'dsp_mode': hex(dsp_mode), 'mixer_mode': mixer_mode,
                          'drains': 3, 'programming_writes': 0})
    checks.append({'name': 'First and repeated Auto drains produce no routing DSP writes or event posts',
                   'status': 'pass', 'cases': cases})

    stack_cases = []
    for name, image in (('stock', component_unpacked(original, COMPONENT_BY_NAME['app_main'])),
                        ('routing', main)):
        machine = AudioMachine(image, symbols, b'')
        low = [0x2001FFF0]
        def observe_stack(uc, address, size, user):
            low[0] = min(low[0], uc.reg_read(UC_ARM_REG_SP))
        handle = machine.uc.hook_add(UC_HOOK_CODE, observe_stack)
        machine.drain()
        machine.uc.hook_del(handle)
        stack_cases.append({'image': name, 'observed_stack_bytes': 0x2001FFF0 - low[0]})
    checks.append({'name': 'Original and routing empty-handler stack depth measured under stated stubs',
                   'status': 'pass', 'cases': stack_cases,
                   'limit': 'Does not include task ancestors, interrupts or stack use inside stubbed calls; not a full stack-margin proof'})

    boot = original[0x30:0x30 + struct.unpack_from('<I', original, 0x0C)[0]]
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    disassembly = {}
    for start, end in ((0x2C0, 0x2FC), (0x448, 0x4D6)):
        disassembly[hex(start)] = [f'{i.address:#010x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}'
            for i in decoder.disasm(boot[start:end], BOOT_BASE + start)]
    return {'status': 'pass', 'input_sha256': sha256(original),
        'candidate_sha256': sha256(candidate), 'hardware_access': False,
        'hardware_recovery_verified': False, 'checks': checks,
        'boot_main_selector': {'decoded_offset': '0x2dc', 'runtime': '0x010002dc',
            'input_word': hex(SELECTOR), 'input_zero': 'updater at flash offset 0x10000',
            'input_nonzero': 'normal application at flash offset 0x80000',
            'electrical_TAP_mapping': 'Not measured; updater branch correlated with documented TAP entry'},
        'boot_main_disassembly': disassembly,
        'stubs': {
            '0x01000540': 'Board/ROM-service initialization; install modeled cleanup callback',
            '0x0100037e': 'Board memory-interface setup and delay',
            '0x01001346': 'Peer transport reset/setup',
            '0x0100095e': 'Peer transport ready, returns zero',
            '0x01000970': 'Record transfer descriptor/source bytes; model completion',
            '0x01001abc': 'Normal-branch peer setup, count only',
            '0x01001aea': 'Normal USB-application peer handoff, hash loaded bytes',
            hex(RETURN + 0x100): 'Modeled ROM cleanup callback',
            'Auto drain': 'Existing AudioMachine parameter/queue/RTOS boundaries; actual routing and original drain execute'},
        'limits': [
            'No immutable-ROM execution before the supplied reset vector',
            'No electrical TAP mapping, power, clock, SDRAM, flash or peer-processor behavior measured',
            'Stops immediately before final BX; stock reset-context SDRAM handoff raises a Unicorn CPU exception',
            'Application startup is executed separately, not a continuous boot or updater USB-enumeration test',
            'Does not prove recovery after arbitrary corruption or interrupted programming',
            'No complete application/RTOS/DSP/audio emulation or real-time stack/deadline measurement']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--firmware', type=Path, default=ROOT / 'inputs/MX1_UPD.original.bin')
    parser.add_argument('--build', type=Path, default=ROOT / 'build/mainline')
    parser.add_argument('--output', type=Path, default=ROOT / 'analysis/boot_path_verification.json')
    args = parser.parse_args()
    with (args.build / 'mainline.elf').open('rb') as stream:
        elf = ELFFile(stream)
        text = elf.get_section_by_name('.text')
        build = json.loads((args.build / 'build-report.json').read_text())
        assert sha256(text.data() + elf.get_section_by_name('.usb_data').data()) == build['extension_sha256']
        applied = elf.get_section_by_name('.symtab').get_symbol_by_name('applied')
        assert len(applied) == 1 and applied[0]['st_size'] == 11
        applied_address = applied[0]['st_value']
        assert applied_address == 0x0101726f
        assert build["writable_state"] == {"start": 0x01017264, "size": 540, "end_exclusive": 0x01017480, "startup_zero_length_offset": 0x108}
    report = audit(args.firmware.read_bytes(),
        (args.build / 'MXPLUS_MAINLINE_UNTESTED.bin').read_bytes(),
        build, applied_address)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'],
        'checks': [check['name'] for check in report['checks']],
        'candidate_sha256': report['candidate_sha256'],
        'hardware_recovery_verified': False}, indent=2))


if __name__ == '__main__':
    main()
