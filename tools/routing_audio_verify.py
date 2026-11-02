#!/usr/bin/env python3
"""Execute the compiled route control and original DSP programming helpers.

This tests emitted ARM instructions and their command/operand effects. It does
NOT emulate ESC2 arithmetic, float-port conversion, sample timing, or audio.
The token-routing oracle below tests address selection and independence only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import struct

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
    UC_ARM_REG_R3, UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
    UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11,
    UC_ARM_REG_LR, UC_ARM_REG_PC)

from container_tool import ORIGINAL_SHA256, COMPONENT_BY_NAME, component_unpacked, sha256
from arm_machine import Machine
from routing_audio_extract import reconstruct
from routing_audio_patch import SITES, STOCK, SELECTORS, source_offset

REGS = (UC_ARM_REG_R4, UC_ARM_REG_R5, UC_ARM_REG_R6, UC_ARM_REG_R7,
        UC_ARM_REG_R8, UC_ARM_REG_R9, UC_ARM_REG_R10, UC_ARM_REG_R11)


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


def choices():
    """Independent product map, not extracted from extension machine code."""
    result = [(0, 0, 'Auto')]
    result.extend((0x6000 + i, 0x6000 + i, f'An{i+1} ') for i in range(4))
    result.extend([(0x6004, 0x6005, 'A56 '), (0x6004, 0x6004, 'An5 '),
                   (0x6005, 0x6005, 'An6 '), (0x6008, 0x6009, 'dIG '),
                   (0x6008, 0x6008, 'dI L'), (0x6009, 0x6009, 'dI R')])
    for port in range(1, 5):
        left = 0x6008 + port * 2
        result.extend([(left, left + 1, f'US{port} '),
                       (left, left, f'U{port} L'), (left+1, left+1, f'U{port} R')])
    result.extend([(0x6006, 0x6007, 'rtn '), (0x6006, 0x6006, 'rt L'),
                   (0x6007, 0x6007, 'rt R')])
    for pair in range(1, 10):
        left = 0xa000 + 2 * (pair - 1)
        result.extend([(left, left+1, f'PC{pair} '), (left, left, f'P{pair} L'),
                       (left+1, left+1, f'P{pair} R')])
    assert len(result) == 53
    return result


CHOICES = choices()


class AudioMachine(Machine):
    def __init__(self, image, symbols, program):
        super().__init__(image)
        from routing_mpu_verify import protect_code
        protect_code(self)
        self.symbols = symbols
        self.uc.mem_map(0x40100000, 0x80000)
        self.write(0x40150000, program)
        self.parameters = {0x19: 0, 0x0c: 0, **{i: 1 for i in range(0x92, 0x97)}}
        self.commands = []
        self.posts = []
        self.queue_polls = 0
        self.queue_messages = []
        self.parameter_fixture = False
        self.original_entry = 0
        self.pending_command = None
        self.selectors = {offset: 0 for offset in SELECTORS}
        self.executed_writers = set()
        self.uc.hook_add(UC_HOOK_CODE, self.instruction)
        self.uc.hook_add(UC_HOOK_MEM_WRITE, self.memory, begin=0x40100000, end=0x4017ffff)

    def ret(self, result=0):
        self.uc.reg_write(UC_ARM_REG_R0, result)
        self.uc.reg_write(UC_ARM_REG_PC, self.uc.reg_read(UC_ARM_REG_LR))

    def instruction(self, uc, address, size, user):
        args = tuple(uc.reg_read(r) for r in
                     (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x6001a896:
            assert args[0] == 0x600b5390 and args[2] == 0
            self.ret(self.parameters.get(args[1], 0))
        elif address == 0x0100e266:
            assert args[:2] == (0x6051dea8, 8)
            self.posts.append(args[:2])
            self.ret()
        elif address == 0x6000f1bc:
            self.original_entry += 1
            self.ret()  # Current task boot-mode query, normal program fixture.
        elif address == 0x6000bd6c:
            self.queue_polls += 1
            assert args[0] == 0x6051e248
            if self.queue_messages:
                self.write(args[1], self.queue_messages.pop(0))
                self.ret(1)
            else:
                self.ret()  # Empty queue; original loop/exit still execute.
        elif address == 0x6000c59e and self.parameter_fixture:
            self.ret(args[0])  # Parameter-accessor construction is modeled.
        elif address == 0x6000c5d4 and self.parameter_fixture:
            self.write(args[2], u32(self.parameters.get(args[1], 0)))
            self.ret(1)
        elif address in (0x0100ab04, 0x0100baee):
            self.executed_writers.add(address)

    def memory(self, uc, access, address, size, value, user):
        assert size == 4
        if address == 0x40100900:
            assert self.pending_command is None, 'Programming command overwritten before data'
            self.pending_command = value
        elif address == 0x40100904:
            assert self.pending_command is not None
            command, self.pending_command = self.pending_command, None
            core = (command & 0xf0000) >> 16
            offset = command & 0xffff
            assert core == 5, hex(command)
            assert command & 0xb0000000 == 0, 'Unexpected width or operation'
            floating = bool(command & 0x40000000)
            self.commands.append((offset, value, floating))
            if floating:
                assert offset in SELECTORS and value in (0, 0x3f800000)
                # Record the requested float value. ESC2's hardware float-to-
                # immediate conversion is NOT modeled or claimed verified.
                self.selectors[offset] = int(value != 0)
            else:
                assert offset in SITES and not value & 0xffff
                operand = value >> 16
                cpu_halfword = 0x40150000 + (offset ^ 2)
                self.write(cpu_halfword, struct.pack('<H', operand))
        else:
            raise AssertionError(f'Unexpected DSP MMIO write {address:#x}')

    def checked(self, address, *args):
        values = [0x45670000 + i * 0x101 for i in range(len(REGS))]
        for register, value in zip(REGS, values):
            self.uc.reg_write(register, value)
        result = self.call(address, *args, measure=True)
        assert [self.uc.reg_read(register) for register in REGS] == values
        assert self.pending_command is None
        return result

    def route(self, strip, source):
        for _ in range(54):
            current, _ = self.checked(self.symbols['mx1_route_get'], strip)
            if current == source:
                return
            count = len(self.commands)
            self.checked(self.symbols['mx1_route_adjust'], strip,
                         1 if current < source else 0xffffffff)
            assert len(self.commands) == count, 'UI path wrote DSP MMIO'
        raise AssertionError('Desired choice not reachable')

    def drain(self):
        before = len(self.commands)
        polls = self.queue_polls
        queued = len(self.queue_messages)
        result = self.checked(0x60024bae)
        assert self.queue_polls == polls + queued + 1
        return len(self.commands) - before, result[1]

    def operands(self):
        return tuple(struct.unpack('<H', self.read(0x40150000 + (p ^ 2), 2))[0] for p in SITES)

    def expected(self):
        result = list(STOCK)
        if self.parameters[0x19] != 2:
            desired = self.read(self.symbols['mx1_route_state'], 11)
            for strip, source in enumerate(desired):
                if source:
                    lane = strip if strip < 4 else strip * 2 - 4
                    count = 1 if strip < 4 else 2
                    result[lane:lane + count] = CHOICES[source][:count]
        return tuple(result)


def verify(original: bytes, patched: bytes, build: dict) -> dict:
    assert sha256(original) == build['original_app_sha256']
    assert sha256(patched) == build['patched_app_sha256']
    groups = []
    def passed(name, **details):
        groups.append(dict(name=name, status='pass', **details))
    upload, programs = reconstruct()
    assert upload['source_sha256'] == sha256(original)
    for offset, value in zip(SITES + (0x4ce, 0x4e0), STOCK + (0x6006, 0x6007)):
        assert struct.unpack_from('<H', original, source_offset(offset))[0] == value
        assert struct.unpack_from('<H', programs[0], offset ^ 2)[0] == value
    passed('Original ARM DSP uploader reconstructs all 36 normal-program chunks and guarded source operands',
           executed=upload['executed'], modeled=upload['modeled'],
           program_hashes=upload['instruction_memory_sha256'])

    # The separate original factory program is evidence about the source-bank
    # read representation; it is NOT inserted into the candidate. It imports
    # native serial and raw CPU playback through the same move bindings into
    # ordinary DSP RAM. Thus the normal prefix's extra arithmetic is not a
    # mandatory format converter between a000 and the ordinary audio domain.
    factory_upload, factory = reconstruct((0x600cb780,), (1,))
    def words(offset, count):
        return tuple(struct.unpack_from('<H', factory[0], (offset + 2*i) ^ 2)[0]
                     for i in range(count))
    assert words(0x20, 5) == (0x1e05, 0x0fe0, 0x1fe2, 0xa000, 0x0033)
    for channel in range(1, 18):
        offset = 0x2a + (channel - 1) * 0x12
        instruction = words(offset, 9)
        assert instruction[:5] == (0x7809, 0x0fe0, 0x8fe2, 0x1fe4, 0x9fe6)
        assert instruction[5:] == (0xa000 + channel, 0x1f + channel,
                                    0x33 + 2*channel, 0xa011 + channel)
    assert words(0x15c, 5) == (0x1e05, 0x8fe0, 0x9fe2, 0x0031, 0xa023)
    assert words(0x16a, 3) == (0x0c03, 0x0fe0, 0x6000)
    raw_order = (0x6001, 0x6002, 0x6003, 0x6004, 0x6005, 0x6008,
                 0x6009, 0x600a, 0x600b, 0x600c, 0x600d, 0x600e,
                 0x600f, 0x6010, 0x6011, 0x6006, 0x6007)
    previous_destinations = (0xc, 0xd, 0xe, 0xf, 0x10, 0x11, 0x14, 0x15,
                             0x16, 0x17, 0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x12)
    for index, (source, previous_destination) in enumerate(zip(raw_order, previous_destinations)):
        assert words(0x170 + index*10, 5) == (0x1e05, 0x0fe0, 0x8fe2, source, previous_destination)
    assert words(0x21a, 3) == (0x0c03, 0x8fe0, 0x13)
    passed('Original factory DSP graph uses identical direct-copy read bindings for raw PC and serial inputs',
           component='app_main', decoded_descriptor_offset=0xcb780,
           descriptor_runtime='0x600cb780', program_source_runtime='0x600cad4c',
           program_sha256=factory_upload['instruction_memory_sha256'][0],
           raw_pc_import_range=['0x20', '0x166'], serial_import_range=['0x16a', '0x220'],
           common_read_binding='0x0fe0', common_write_binding='0x8fe2',
           inference='Both raw source banks are consumed as compatible ordinary DSP audio operands',
           limitation='This is guarded original-program evidence, not execution of ESC2 arithmetic')

    machine = AudioMachine(patched, build['symbols'], programs[0])
    assert machine.read(build['symbols']['mx1_route_state'], 11) == bytes(11)
    assert machine.drain()[0] == 0
    assert machine.operands() == STOCK
    passed('AUTO boot, original empty parameter drain, no DSP programming writes, AAPCS preserved')

    visits = 0
    maximum_commands = maximum_instructions = 0
    for strip in range(11):
        permitted = [i for i, choice in enumerate(CHOICES)
                     if strip >= 4 or choice[0] == choice[1]]
        for source in permitted[1:] + [0]:
            machine.route(strip, source)
            label, _ = machine.checked(build['symbols']['mx1_route_label'], strip)
            assert machine.read(label, 4).decode() == CHOICES[source][2]
            writes, instructions = machine.drain()
            assert machine.operands() == machine.expected()
            maximum_commands = max(maximum_commands, writes)
            maximum_instructions = max(maximum_instructions, instructions)
            visits += 1
        # Repeated outward turns clamp at both ends without a redundant post.
        for endpoint, delta in ((0, 0xffffffff), (52, 1)):
            machine.route(strip, endpoint)
            posts = len(machine.posts)
            for _ in range(3):
                machine.checked(build['symbols']['mx1_route_adjust'], strip, delta)
                assert machine.checked(build['symbols']['mx1_route_get'], strip)[0] == endpoint
            assert len(machine.posts) == posts
            # Turning inward immediately leaves the endpoint, including mono skips.
            machine.checked(build['symbols']['mx1_route_adjust'], strip,
                            1 if endpoint == 0 else 0xffffffff)
            assert machine.checked(build['symbols']['mx1_route_get'], strip)[0] == (1 if endpoint == 0 else 51)
        machine.route(strip, 0)
        machine.drain()
    passed('Every permitted source on every destination executes actual compiled menu and original DSP writers',
           source_choices=53, strips=11, source_destination_visits=visits,
           mono_stereo_pairs_skipped=True, four_character_labels=True,
           endpoints_clamp_without_event_posts=True, inward_turn_resumes=True,
           largest_single_route_drain_commands=maximum_commands,
           largest_single_route_drain_instructions=maximum_instructions)

    # User's explicit fallback, including a simultaneous host stream that must
    # not contaminate the destination. All sources are symbolic tokens here.
    machine.route(4, 6)  # Analog 5 -> original 5/6, duplicated to its L and R.
    machine.route(7, 7)  # Analog 6 -> USB2, duplicated to its L and R.
    machine.parameters[0x94] = 0
    machine.selectors[0x246] = machine.selectors[0x260] = 1  # Original unplug policy.
    machine.drain()
    op = machine.operands()
    assert op[4:6] == (0x6004, 0x6004) and op[10:12] == (0x6005, 0x6005)
    assert machine.selectors[0x246] == machine.selectors[0x260] == 0
    passed('Analog 5/6 split produces independent original-5/6 and USB2 input reads; own PC summand suppressed',
           original_strip_label='An5 ', usb2_label='An6 ', usb2_connected=False)

    # Interdependent route changes must read raw PC slots, not the gated
    # 2000..2011 scratch buffer that a different destination can suppress.
    machine.route(0, 42)  # PC6 left, shared raw playback a00a.
    machine.route(6, 42)  # Same source duplicated to USB1.
    machine.route(10, 25) # Raw Return right on COMPUTER strip.
    machine.drain()
    op = machine.operands()
    assert op[0] == 0xa00a and op[8:10] == (0xa00a, 0xa00a)
    assert op[16:18] == (0x6007, 0x6007)
    assert struct.unpack('<H', machine.read(0x40150000 + (0x4ce ^ 2), 2))[0] == 0x6006
    assert struct.unpack('<H', machine.read(0x40150000 + (0x4e0 ^ 2), 2))[0] == 0x6007
    passed('Duplicate raw PC source survives other destination PC suppression; Return copy preserves original Return reads',
           model_boundary='Address/token independence, not ESC2 numeric sample execution')

    desired = machine.read(build['symbols']['mx1_route_state'], 11)
    machine.parameters[0x19] = 2
    assert machine.checked(build['symbols']['mx1_route_label'], 7)[0] != 0
    ptr = machine.checked(build['symbols']['mx1_route_label'], 7)[0]
    assert machine.read(ptr, 4) == b'modE'
    posts = len(machine.posts)
    machine.checked(build['symbols']['mx1_route_adjust'], 7, 1)
    assert machine.read(build['symbols']['mx1_route_state'], 11) == desired
    assert len(machine.posts) == posts
    machine.drain()
    assert machine.operands() == STOCK
    assert machine.selectors[0x246] == machine.selectors[0x260] == 1
    machine.parameters[0x19] = 1
    machine.drain()
    assert machine.operands() == machine.expected()
    passed('External Mixer restores stock operands and connection policy, blocks UI edits, resumes saved routes in Control Surface')

    # A sample-rate reset reloads the original DSP program but preserves ARM
    # route state. Its stock group notifications subsequently drain event 8.
    machine.write(0x40150000, programs[0])
    machine.drain()
    assert machine.operands() == machine.expected()
    passed('Queued parameter drain reasserts selected sources after full DSP program reload')

    queued = AudioMachine(patched, build['symbols'], programs[0])
    queued.route(7, 7)
    queued.drain()
    queued.parameters[0x94] = 0
    queued.parameter_fixture = True
    # The actual original callback lookup runs against a deliberately narrow
    # fixture table: only global CONNECT USB IN2 AUDIO has a registered handler.
    # Original group metadata, lookup, callback, softfloat conversion and DSP
    # write instructions all execute. Only queue delivery/storage are modeled.
    queued.write(0x6051ab84, struct.pack('<III', 0x20018000, 0, 0x500))
    queued.write(0x20018000, bytes(0x500*4))
    queued.write(0x20018000 + 4*0x94, u32(0x60027bf9))
    queued.queue_messages.append(bytes([0, 1, 0, 0]))
    queued.commands.clear()
    queued.drain()
    usb2 = [entry for entry in queued.commands if entry[0] in (0x246, 0x260) and entry[2]]
    assert usb2 == [(0x246, 0x3f800000, True), (0x260, 0x3f800000, True),
                    (0x246, 0, True), (0x260, 0, True)], usb2
    assert queued.operands()[10:12] == (0x6005, 0x6005)
    passed('Original queued connection callback runs first; routing flush then overrides its unwanted PC summand',
           queue_message='type0/group1', callback='0x60027bf8',
           observed_selector_requests=usb2,
           modeled='Parameter accessor and queue contents; real callback lookup/table fixture and callback execute')

    for mode in range(4, 12):
        machine.write(0x6051deb8, u32(mode))
        count = len(machine.commands)
        machine.checked(build['symbols']['mx1_route_adjust'], 0, 1)
        machine.drain()
        assert len(machine.commands) == count
    machine.write(0x6051deb8, u32(0))
    for strip in (11, 0xffffffff):
        assert machine.checked(build['symbols']['mx1_route_get'], strip)[0] == 0
        ptr = machine.checked(build['symbols']['mx1_route_label'], strip)[0]
        assert machine.read(ptr, 4) == b'----'
        count = len(machine.posts)
        machine.checked(build['symbols']['mx1_route_adjust'], strip, 1)
        assert len(machine.posts) == count
    passed('Diagnostic programs, invalid strip IDs and invalid display accesses are excluded')

    callback_cases = 0
    for mode in (0, 1, 2):
        for connected in (0, 1):
            for digital_output in (0, 1):
                stock = AudioMachine(original, build['symbols'], programs[0])
                stock.parameters.update({0x19: mode, 0x0c: digital_output,
                                         **{i: connected for i in range(0x92, 0x97)}})
                for callback in (0x60027b44, 0x60027b7c, 0x60027bf8, 0x60027c20, 0x60027c48):
                    stock.checked(callback, 0, connected)
                    callback_cases += 1
                machine.parameters.update({0x19: 0, 0x0c: digital_output,
                                           **{i: connected for i in range(0x92, 0x97)}})
                for strip in range(5, 10):
                    machine.route(strip, 7)
                machine.drain()
                if mode != 2:
                    for strip in range(5, 10):
                        machine.route(strip, 0)
                machine.parameters[0x19] = mode
                machine.commands.clear()
                machine.drain()
                restored = [entry for entry in machine.commands if entry[2]]
                assert restored == stock.commands, (mode, connected, digital_output, restored, stock.commands)
                assert all(machine.selectors[p] == stock.selectors[p] for p in SELECTORS)
    assert machine.executed_writers == {0x0100ab04, 0x0100baee}
    passed('AUTO restoration matches original DIGITAL direction and all five native connection truth tables',
           original_writers=[hex(x) for x in sorted(machine.executed_writers)],
           original_callbacks_executed=callback_cases, modes=[0, 1, 2])

    return {
        'status': 'pass', 'groups': groups, 'patched_app_sha256': sha256(patched),
        'source_choices': [{'id': i, 'left_operand': l, 'right_operand': r, 'label': label}
                           for i, (l, r, label) in enumerate(CHOICES)],
        'executed': ['Compiled routing APIs and dispatch trampoline',
                     'Original parameter queue-loop control and epilogue',
                     'Original raw/float DSP command helpers 0x0100ab04 and 0x0100baee',
                     'Original program uploader and its partial-word merges'],
        'modeled': ['Parameter-store lookup results', 'Queue contents/accessor construction and task mode query',
                    'RTOS post recorded here; actual RTOS wrapper tested separately',
                    'DSP program halfword storage; float immediate requests recorded without conversion',
                    'Source operands treated as symbolic tokens, not numerical audio'],
        'not_tested': ['ESC2 arithmetic/float format interpretation', 'Real DSP frame/command timing',
                       'Physical input/output channel order', 'Click-free route changes',
                       'Physical panel or audio operation'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('firmware', type=Path)
    parser.add_argument('--build', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raw = args.firmware.read_bytes()
    assert sha256(raw) == ORIGINAL_SHA256, 'Original firmware identity mismatch'
    original = component_unpacked(raw, COMPONENT_BY_NAME['app_main'])
    build = json.loads((args.build / 'build-report.json').read_text())
    patched = (args.build / 'app_main.mainline.bin').read_bytes()
    report = verify(original, patched, build)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'groups': len(report['groups'])}))


if __name__ == '__main__':
    main()
