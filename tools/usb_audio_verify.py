#!/usr/bin/env python3
"""Execute an MX-1 UAC2 candidate's ARM initializer and control dispatch.

Original descriptor/registration/control code and the compiled extension run
in Unicorn. RTOS task creation, low-level hardware start, and EP0 reply FIFO
delivery are stubbed; no physical USB or complete USB peripheral is emulated.
"""
import argparse
import json
import struct
from pathlib import Path

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP)

from container_tool import COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine, BASE
from memory_map import recover

SETUP = 0x606293fc
STATE = 0x600d09c0
APP_CALLBACK = 0x605251bc
LOW_CALLBACK = 0x60629b2c
EP0_CONTROL = 0x40010100
USBF = 0x40010000


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


class DeviceMachine(Machine):
    def __init__(self, image, handler=None, failures=None):
        super().__init__(image)
        from routing_mpu_verify import protect_code
        protect_code(self)
        self.handler = handler & ~1 if handler else None
        self.failures = failures or {}
        self.calls = []
        self.replies = []
        self.stalls = []
        self.descriptor_writes = []
        self.visits = []
        self.uc.hook_add(UC_HOOK_CODE, self._instruction)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self._write)

    def _instruction(self, uc, address, size, user):
        args = tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
        if address in (0x6003b764, 0x6003b7cc, 0x6003b7f4,
                       0x6003b786, 0x6003b3ae, 0x6003cae4):
            self.calls.append((address, args))
        if address in (0x01004834, 0x01004646, 0x6003b664, self.handler):
            self.visits.append(address)
        if address == 0x01003e1a:
            self.stalls.append(args[0])
            # Execute the original stall register writes, do not stub them.
        if address == 0x010046ba:
            pointer, length, flags = args
            self.replies.append({'pointer': pointer, 'length': length,
                                 'flags': flags, 'data': self.read(pointer, length)})
        if address in self.failures or address in (0x6003b3ae, 0x6003cae4, 0x010046ba):
            uc.reg_write(UC_ARM_REG_R0, self.failures.get(address, 0) & 0xffffffff)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _write(self, uc, access, address, size, value, user):
        if 0x40010200 <= address < 0x40010280:
            self.descriptor_writes.append((address, size, value))

    def setup(self, request, direct_class=False):
        self.replies.clear()
        self.stalls.clear()
        self.visits.clear()
        self.write(SETUP, request)
        self.write(STATE, b'\x02')  # Setup packet already read from hardware.
        self.write(EP0_CONTROL, u32(0))
        result, count = self.call(0x01004646 if direct_class else 0x01004834,
                                  measure=True)
        return result, count


def request(type_, code, value, index, length):
    return struct.pack('<BBHHH', type_, code, value, index, length)


def expect_reply(machine, expected):
    assert not machine.stalls
    assert len(machine.replies) == 1
    reply = machine.replies[0]
    assert reply['data'] == expected, (reply['data'].hex(), expected.hex())
    assert reply['flags'] == 0


def expect_stall(machine):
    assert not machine.replies
    assert machine.stalls == [0]
    assert machine.read(STATE, 1) == b'\x01'
    assert machine.read(SETUP, 8) == bytes(8)
    assert struct.unpack('<I', machine.read(EP0_CONTROL, 4))[0] & 4


def verify(original, patched, build):
    groups = []
    def passed(name, **details):
        groups.append({'name': name, 'status': 'pass', **details})

    assert sha256(patched) == build['patched_app_sha256']
    handler = build['symbols']['mx1_uac2_class_request']
    configuration = build['symbols']['mx1_uac2_configuration']
    rate_address = build['symbols']['mx1_uac2_rate']

    # Execute the actual startup copy/clear instructions before entering BSP.
    started = []
    for image in (original, patched):
        machine = Machine(image, scatter=False)
        machine.uc.reg_write(UC_ARM_REG_SP, 0x2001fff0)
        machine.uc.emu_start(BASE | 1, BASE + 0x7e, timeout=2_000_000, count=2_000_000)
        assert machine.uc.reg_read(UC_ARM_REG_PC) == BASE + 0x7e
        for op in recover(image)['operations']:
            if op['kind'] == 'copy' and op['length']:
                expected = image[op['source'] - BASE:op['source'] - BASE + op['length']]
                assert machine.read(op['destination'], op['length']) == expected
        started.append(machine)
    for op in recover(original)['operations']:
        if op['kind'] == 'copy' and op['destination'] != 0x01000300 and op['length']:
            assert started[0].read(op['destination'], op['length']) == started[1].read(op['destination'], op['length'])
    passed('Actual startup copies extension and preserves existing initialized data',
           extension_bytes=build['scatter_extension']['insert_length'])

    initialization = []
    control_cases = 0
    instruction_counts = []
    initialized = {}
    for rate in (44100, 48000, 96000):
        machine = DeviceMachine(patched, handler)
        rc, count = machine.call(0x6000d980, rate, measure=True)
        assert rc == 0
        assert machine.read(APP_CALLBACK, 4) == u32(handler | 1)
        assert machine.read(LOW_CALLBACK, 4) == u32(0x6003b665)
        assert machine.read(rate_address, 4) == u32(rate)
        assert machine.read(0x606293e0, 4) == u32(configuration)
        assert machine.read(0x600b499c, 0x102) == original[0xb499c:0xb4a9e]
        sizes = [struct.unpack('<H', machine.read(configuration + offset, 2))[0]
                 for offset in (0x91, 0xbf, 0xf6, 0x124)]
        assert sizes == [(rate // 8000 + 2) * channels * 4 for channels in (18, 2, 18, 2)]
        calls = [address for address, args in machine.calls]
        assert calls == [0x6003b764, 0x6003b7cc, 0x6003b7f4,
                         0x6003b786, 0x6003b3ae, 0x6003cae4]
        assert machine.calls[2][1] == (0, 1, handler | 1)
        initialization.append({'rate': rate, 'packet_sizes': sizes,
                               'instructions': count})

        frequency = u32(rate)
        range_ = struct.pack('<HIII', 1, rate, rate, 0)
        for code, value, response in ((1, 0x0100, frequency),
                                       (2, 0x0100, range_),
                                       (1, 0x0200, b'\x01')):
            for length in (1, 2, 3, 4, 8, 14, 64, 255, 65535):
                _, n = machine.setup(request(0xa1, code, value, 0x1000, length))
                expect_reply(machine, response[:length])
                assert machine.visits == [0x01004834, 0x01004646, 0x6003b664, handler & ~1]
                instruction_counts.append(n)
                control_cases += 1
        # Direct entry tests the lower-level ABI independently of outer routing.
        machine.setup(request(0xa1, 1, 0x0100, 0x1000, 4), direct_class=True)
        expect_reply(machine, frequency)
        assert machine.visits == [0x01004646, 0x6003b664, handler & ~1]
        control_cases += 1
        initialized[rate] = machine

    passed('Patched initializer veneer, original registration, and live rate descriptors',
           cases=initialization)
    passed('Original request dispatch reaches compiled UAC2 handler with correct replies',
           cases=control_cases, min_instructions=min(instruction_counts),
           max_instructions=max(instruction_counts),
           abi='setup pointer preserved through01004646 and6003b664; callback return ignored')

    machine = initialized[48000]
    negatives = [
        ('zero_length', request(0xa1, 1, 0x0100, 0x1000, 0)),
        ('frequency_write', request(0x21, 1, 0x0100, 0x1000, 4)),
        ('wrong_recipient', request(0xa0, 1, 0x0100, 0x1000, 4)),
        ('wrong_endpoint_recipient', request(0xa2, 1, 0x0100, 0x1000, 4)),
        ('wrong_entity', request(0xa1, 1, 0x0100, 0x1100, 4)),
        ('wrong_interface', request(0xa1, 1, 0x0100, 0x1001, 4)),
        ('wrong_channel', request(0xa1, 1, 0x0101, 0x1000, 4)),
        ('unknown_selector', request(0xa1, 1, 0x0300, 0x1000, 4)),
        ('validity_range', request(0xa1, 2, 0x0200, 0x1000, 1)),
        ('unknown_request', request(0xa1, 3, 0x0100, 0x1000, 4)),
    ]
    for name, packet in negatives:
        machine.setup(packet)
        expect_stall(machine)
    passed('Compiled rejection path executes original EP0 stall routine',
           cases=[name for name, packet in negatives])

    # The old GET_DESCRIPTOR dispatcher must return the replacement pointer,
    # mutate other-speed descriptor types, and honor requested lengths.
    descriptor_cases = []
    for speed in ('high', 'full'):
        machine.write(USBF + 8, u32(0 if speed == 'high' else 0x10000))
        for kind, length in ((1, 18), (2, 9), (2, 1000), (6, 10), (7, 1000)):
            machine.setup(request(0x80, 6, kind << 8, 0, length))
            assert len(machine.replies) == 1 and not machine.stalls
            actual = machine.replies[0]['data']
            if kind == 1:
                assert len(actual) == 18 and actual[4:7] == bytes.fromhex('ef0201')
            elif kind == 6:
                assert len(actual) == 10 and actual[4:7] == bytes.fromhex('ef0201')
            else:
                expect_new = (kind == 2 and speed == 'high') or (kind == 7 and speed == 'full')
                total = 435 if expect_new else 45
                assert len(actual) == min(length, total)
                assert actual[1] == kind
                assert struct.unpack_from('<H', actual, 2)[0] == total
                assert actual[4] == (5 if expect_new else 4)
                if expect_new and len(actual) == total:
                    from usb_midi_descriptors import validate_configuration
                    validate_configuration(actual)
            descriptor_cases.append({'speed': speed, 'descriptor_type': kind,
                                     'requested_length': length, 'returned_length': len(actual)})
    passed('Original GET_DESCRIPTOR and other-speed paths use new live descriptor',
           cases=descriptor_cases,
           full_speed_limit='The unchanged full-speed configuration has no audio endpoints')

    # Compare complete tables; enumerate the four intentional MIDI changes.
    # All audio entries and every other register write must remain identical.
    tables = []
    midi_changes = {
        0x40010208: (0x100018c3, 0x100020c3), # EP3 bulk OUT: IF3 -> IF4
        0x4001020c: (0x100098e3, 0),          # Retire EP3 interrupt alternate
        0x40010210: (0x100018d4, 0x100020d4), # EP4 bulk IN: IF3 -> IF4
        0x40010218: (0x100098f5, 0),          # Retire EP5 interrupt alternate
    }
    for rate in (44100, 48000, 96000):
        for speed in ('high', 'full'):
            old = DeviceMachine(original)
            new = DeviceMachine(patched, handler)
            assert old.call(0x6000d980, rate)[0] == new.call(0x6000d980, rate)[0] == 0
            for m in (old, new):
                m.write(USBF + 8, u32(0 if speed == 'high' else 0x10000))
                m.call(0x6003d026)
            expected = bytearray(old.read(USBF + 0x200, 0x80))
            changes = midi_changes if speed == 'high' else {}
            for address, (before, after) in changes.items():
                assert old.read(address, 4) == u32(before)
                expected[address - USBF - 0x200:address - USBF - 0x200 + 4] = u32(after)
            assert new.read(USBF + 0x200, 0x80) == expected
            assert [w for w in old.descriptor_writes if w[0] not in changes] == [
                w for w in new.descriptor_writes if w[0] not in changes]
            if speed == 'high':
                assert old.read(USBF + 0xfc, 4) == u32(0x04002334)
                assert new.read(USBF + 0xfc, 4) == u32(0x05005334)
            else:
                assert old.descriptor_writes == new.descriptor_writes
                assert old.read(USBF + 0xfc, 4) == new.read(USBF + 0xfc, 4)
            tables.append({'rate': rate, 'speed': speed,
                           'table_sha256': sha256(new.read(USBF + 0x200, 0x80)),
                           'interface_register_hex': new.read(USBF + 0xfc, 4).hex(),
                           'reviewed_midi_changes': {hex(a): [hex(v) for v in pair] for a,pair in changes.items()}})
    passed('Original descriptor walker preserves audio tables and applies only reviewed MIDI changes', cases=tables)

    failure_cases = []
    for label, failures, rate in (
        ('unsupported_rate', {}, 12345),
        ('descriptor_init', {0x6003b764: -9}, 48000),
        ('class_registration', {0x6003b7cc: -10}, 48000),
        ('callback_registration', {0x6003b7f4: -11}, 48000),
        ('task_creation', {0x6003b3ae: -12}, 48000),
        ('hardware_start', {0x6003cae4: -13}, 48000),
    ):
        m = DeviceMachine(patched, handler, failures)
        rc, _ = m.call(0x6000d980, rate)
        assert rc == 0xffffffff
        calls = [hex(a) for a, _ in m.calls]
        if label == 'unsupported_rate':
            assert not calls
        failure_cases.append({'failure': label, 'return': hex(rc), 'calls': calls})
    passed('Initializer returns failure for invalid rates and failed stock stages', cases=failure_cases)

    backup = []
    for image in (original, patched):
        m = DeviceMachine(image, handler)
        rc, _ = m.call(0x6000d8da)
        assert rc == 0
        backup.append((m.read(0x606293dc, 32), m.read(0x605251b8, 0x48)))
    assert backup[0] == backup[1]
    passed('Original backup initializer retains descriptor and callback tables')

    return {
        'status': 'pass',
        'original_app_sha256': sha256(original),
        'patched_app_sha256': sha256(patched),
        'candidate_container_sha256': build['container_sha256'],
        'groups': groups,
        'scope': 'Actual ARM startup/init/descriptor/control code plus compiled C extension executed in Unicorn',
        'stubs': ['6003b3ae RTOS task creation', '6003cae4 low-level hardware startup',
                  '010046ba EP0 response FIFO delivery; pointer/length/data/flags recorded'],
        'not_emulated': ['USB bus tokens and host enumeration', 'FIFO capacity and timing',
                         'DSP clock lock', 'actual sustained audio', 'physical flash programming'],
        'instruction_measurement': 'Executed instructions only; not cycles or timing predictions',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', type=Path)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    original = component_unpacked(args.firmware.read_bytes(), COMPONENT_BY_NAME['app_main'])
    patched = (args.build / 'app_main.mainline.bin').read_bytes()
    build = json.loads((args.build / 'build-report.json').read_text())
    report = verify(original, patched, build)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups': [g['name'] for g in report['groups']]}, indent=2))


if __name__ == '__main__':
    main()
