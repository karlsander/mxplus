#!/usr/bin/env python3
"""Audit original MX-1 DSP serial-I/O setup using original ARM instructions.

This is evidence about the written register values, not an audio or hardware
emulator. Three MMIO readiness responses and the AK4115 serial-control helper
are explicitly modeled. Physical connector-to-slot order is not inferred here.
"""
import argparse
import json
import struct
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MEM_READ
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_SP

from container_tool import COMPONENT_BY_NAME, component_unpacked, sha256
from memory_map import recover


ORIGINAL_SHA256 = '26f195d7325adf5534a476d1fb24170decd08586ca059cffa6020a8055cbf84e'
MAIN_SHA256 = '256ab535bc55c3e3dbe7c6b609d28da710192f0676e7f4cbbd5ec260ab364a2b'
DSP_INIT = 0x0100a282
DIGITAL_INIT = 0x60001404
DSP_CONTEXT = 0x20000b24
DIGITAL_CONTEXT = 0x20030000
STOP = 0x00001000
EXPECTED_SERIAL = {
    0x40100508: 0x88003006,
    0x40100510: 0x88003004,
    0x40100518: 0x88003002,
    0x40100520: 0x88003000,
    0x40100528: 0x98003016,
    0x40100530: 0x98003014,
    0x40100538: 0x98003012,
    0x40100540: 0x88223010,
    0x40100548: 0x8822300e,
    0x40100550: 0x8822300c,
    0x40100558: 0x8822300a,
}


def u32(value):
    return struct.pack('<I', value & 0xffffffff)


class AuditMachine:
    def __init__(self, image, *, digital=False):
        self.uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        self.uc.mem_map(0x60000000, 0x800000)
        self.uc.mem_write(0x60000000, image)
        self.uc.mem_map(0x01000000, 0x30000)
        self.uc.mem_map(0x20000000, 0x40000)
        self.uc.mem_map(0x40000000, 0x200000)
        self.uc.mem_map(STOP, 0x1000)
        # Apply the map recovered from the actual application startup. This
        # deliberately does not call BSP startup or claim a complete machine.
        for op in recover(image)['operations']:
            if op['kind'] == 'copy' and op['length']:
                offset = op['source'] - 0x60000000
                self.uc.mem_write(op['destination'], image[offset:offset + op['length']])
        self.digital = digital
        self.instructions = 0
        self.writes = []
        self.read_counts = {}
        self.serial_control_calls = []
        self.uc.hook_add(UC_HOOK_CODE, self._code)
        self.uc.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, self._memory,
                         begin=0x40000000, end=0x401fffff)

    def _memory(self, uc, access, address, size, value, user):
        if access != UC_MEM_READ:
            self.writes.append((address, size, value))
            return
        self.read_counts[address] = self.read_counts.get(address, 0) + 1
        # These values allow the original initialization's wait loops to
        # finish. They are assumptions and do not establish physical readiness.
        if address == 0x4002dff4:
            uc.mem_write(address, u32(1))
        elif address == 0x40100048:
            uc.mem_write(address, u32(self.read_counts[address]))
        elif address == 0x4010000c:
            uc.mem_write(address, u32(0))

    def _code(self, uc, address, size, user):
        if address == STOP:
            uc.emu_stop()
            return
        self.instructions += 1
        if address == 0x010097e4:
            raise AssertionError('Original firmware assertion reached')
        if self.digital and address in (0x600030aa, 0x600012dc):
            args = [uc.reg_read(reg) for reg in
                    (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
            self.serial_control_calls.append({'function': hex(address), 'arguments': args})
            uc.reg_write(UC_ARM_REG_R0, 0)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def call(self, address, first, second):
        self.uc.reg_write(UC_ARM_REG_SP, 0x2003f000)
        self.uc.reg_write(UC_ARM_REG_LR, STOP | 1)
        self.uc.reg_write(UC_ARM_REG_R0, first)
        self.uc.reg_write(UC_ARM_REG_R1, second)
        self.uc.emu_start(address | 1, 0, timeout=2_000_000, count=20000)
        assert self.uc.reg_read(UC_ARM_REG_PC) == STOP, 'Initializer did not return'
        assert self.uc.reg_read(UC_ARM_REG_SP) == 0x2003f000

    def register(self, address):
        return struct.unpack('<I', self.uc.mem_read(address, 4))[0]


def audit(image):
    assert sha256(image) == MAIN_SHA256, 'Unsupported decoded main application'
    initialization = []
    for rate, selector, clock in ((44100, 0x20, 0xa312220c),
                                  (48000, 0x30, 0xa412220c),
                                  (96000, 0x31, 0xa412220c)):
        machine = AuditMachine(image)
        machine.call(DSP_INIT, DSP_CONTEXT, rate)
        assert machine.register(DSP_CONTEXT) == rate
        assert machine.register(0x40100044) == selector
        assert machine.register(0x40100040) == clock
        for address, expected in EXPECTED_SERIAL.items():
            assert machine.register(address) == expected, (hex(address), rate)
            assert machine.register(address + 4) == 0x20
        assert machine.register(0x40100504) == 0x20
        # Digital slot zero is selected by the AK4115 manager, independently.
        assert not any(a == 0x40100500 for a, _, _ in machine.writes)
        initialization.append({
            'rate': rate, 'original_instructions': machine.instructions,
            'dsp_rate_selector': hex(selector), 'clock_control': hex(clock),
            'serial_config': {hex(a): hex(machine.register(a)) for a in EXPECTED_SERIAL},
            'register_writes': [{'address': hex(a), 'size': size, 'value': hex(value)}
                                for a, size, value in machine.writes],
        })

    digital_cases = []
    for rate in (44100, 48000, 96000):
        for mode, expected in ((0, 0x88113008), (1, 0x98113018)):
            machine = AuditMachine(image, digital=True)
            machine.uc.mem_write(DIGITAL_CONTEXT + 0x28, u32(mode))
            machine.call(DIGITAL_INIT, DIGITAL_CONTEXT, rate)
            writes = [(a, size, value) for a, size, value in machine.writes
                      if a == 0x40100500]
            assert writes == [(0x40100500, 4, expected)]
            assert len(machine.serial_control_calls) == 15
            digital_cases.append({
                'rate': rate, 'mode': mode, 'serial_config': hex(expected),
                'original_instructions': machine.instructions,
                'stubbed_calls': machine.serial_control_calls,
            })

    return {
        'status': 'pass', 'component': 'main', 'main_sha256': sha256(image),
        'scope': 'Original instruction writes only; physical signal flow not emulated',
        'entry_points': {
            'dsp_initialization': {'runtime': '0x0100a282', 'decoded_offset': '0x000dab0e'},
            'ak4115_initialization': {'runtime': '0x60001404', 'decoded_offset': '0x00001404'},
        },
        'modeled_hardware': {
            '0x4002dff4': 'Ready (1) on each read',
            '0x40100048': 'Incrementing count on reads',
            '0x4010000c': 'Reset complete (0) when read',
        },
        'stubbed_helpers_in_digital_cases': {
            '0x600030aa': 'Digital mode GPIO/control selection',
            '0x600012dc': 'AK4115 serial register write helper',
        },
        'dsp_initialization': initialization,
        'digital_mode_selection': digital_cases,
        'limitations': [
            'No physical audio, ADC/DAC clocks, serial bus, PLL lock or DSP execution is modeled.',
            'The low slot fields are recorded as raw values; physical analog/return lane order requires separate evidence.',
            'DSP program source-operand behavior and per-channel routing are outside this audit.',
            'Instruction counts are not CPU cycles or processing-headroom measurements.',
        ],
    }


def audit_event_dispatch(image):
    """Execute the real DSP event-loop boundary with an empty parameter queue.

    The RTOS wait is supplied one event, then execution stops on the next
    wait. The parameter queue reports empty. The dispatcher, callback body,
    boot-mode getter and callback epilogue run as original instructions.
    """
    machine = AuditMachine(image)
    uc = machine.uc
    task = 0x20030000
    uc.mem_write(task + 8, u32(0x123))
    uc.mem_write(task + 0x0c, u32(8))
    uc.mem_write(task + 0x20, u32(0x60024baf))
    events = []

    def dispatch_hook(engine, address, size, user):
        if address == 0x01003310:
            arguments = [engine.reg_read(r) for r in
                         (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2)]
            assert arguments == [0x123, 8, 1]
            events.append('wait')
            if events.count('wait') == 2:
                engine.emu_stop()
                return
            engine.mem_write(engine.reg_read(UC_ARM_REG_R3), u32(8))
            engine.reg_write(UC_ARM_REG_R0, 0)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
        elif address == 0x60024bae:
            events.append('original_parameter_handler')
        elif address == 0x6000bd6c:
            events.append('modeled_empty_parameter_queue')
            engine.reg_write(UC_ARM_REG_R0, 0)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))
        elif address == 0x60024c52:
            events.append('original_handler_epilogue')

    uc.hook_add(UC_HOOK_CODE, dispatch_hook)
    uc.reg_write(UC_ARM_REG_SP, 0x2003f000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    uc.reg_write(UC_ARM_REG_R0, task)
    uc.emu_start(0x0100e221, 0, timeout=2_000_000, count=10000)
    assert events == ['wait', 'original_parameter_handler',
                      'modeled_empty_parameter_queue', 'original_handler_epilogue', 'wait']
    assert uc.reg_read(UC_ARM_REG_PC) == 0x01003310
    # The permanent dispatcher owns its eight-byte frame. Its callback must
    # have fully released its own frame before the next wait begins.
    assert uc.reg_read(UC_ARM_REG_SP) == 0x2003eff8
    assert machine.writes == [], 'Empty parameter dispatch unexpectedly touched MMIO'
    assert image[0x24c52:0x24c58] == bytes.fromhex('07b0bde8f083')

    post = AuditMachine(image)
    post.uc.mem_write(task + 8, u32(0x123))
    posted = []

    def post_hook(engine, address, size, user):
        if address == 0x010032f2:
            posted.append([engine.reg_read(UC_ARM_REG_R0), engine.reg_read(UC_ARM_REG_R1)])
            engine.reg_write(UC_ARM_REG_R0, 0)
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    post.uc.hook_add(UC_HOOK_CODE, post_hook)
    post.call(0x0100e266, task, 8)
    assert posted == [[0x123, 8]]

    flag = AuditMachine(image)
    flag_object, wait_object, returned_flags = 0x20030000, 0x20030100, 0x20030200
    flag.uc.mem_write(flag_object + 0x1d, b'\x01')
    flag.uc.mem_write(flag_object + 0x20, u32(8))
    flag.uc.mem_write(wait_object + 0x34, u32(8))
    flag.uc.mem_write(wait_object + 0x38, b'\x01')
    flag.uc.mem_write(wait_object + 0x3c, u32(returned_flags))
    flag.call(0x010073b8, flag_object, wait_object)
    assert flag.uc.reg_read(UC_ARM_REG_R0) == 1
    assert flag.register(returned_flags) == 8
    assert flag.register(flag_object + 0x20) == 0
    flag.call(0x010073b8, flag_object, wait_object)
    assert flag.uc.reg_read(UC_ARM_REG_R0) == 0

    dsp_record = struct.unpack_from('<9I', image, 0x751c8)
    panel_record = struct.unpack_from('<9I', image, 0x75234)
    assert dsp_record[2:4] == (0x60024a45, 11)
    assert panel_record[2:4] == (0x6000f3bd, 15)
    return {
        'status': 'pass',
        'task_records': {
            'dsp': {'runtime': '0x600751c8', 'entry': '0x60024a45', 'priority': 11},
            'panel': {'runtime': '0x60075234', 'entry': '0x6000f3bd', 'priority': 15},
        },
        'original_dispatcher': '0x0100e220',
        'original_handler': '0x60024bae',
        'original_epilogue': {'runtime': '0x60024c52', 'decoded_offset': '0x00024c52',
                              'bytes': '07b0bde8f083'},
        'event': 8, 'dispatch_trace': events,
        'empty_handler_mmio_writes': 0,
        'event_post_helper': '0x0100e266', 'observed_flag_post_arguments': posted[0],
        'flag_match_helper': '0x010073b8',
        'auto_clear_check': 'First match returned 8 and cleared pending flags; second did not match.',
        'modeled': [
            'RTOS wait supplied one event 8; stopped on the subsequent wait.',
            'Parameter queue pop at 0x6000bd6c returned empty.',
            'Flag posting at 0x010032f2 recorded arguments and returned success.',
            'Flag matching used initialized synthetic flag/wait records.',
        ],
        'not_tested': ['RTOS scheduling, interrupt timing or concurrent execution.'],
    }


def audit_pc_import(image):
    """Compare stock test-program PC and serial-source import instructions.

    The original program uploader executes; DMA transport is a byte-copy
    model. The proprietary DSP instructions are inspected, not emulated.
    """
    assert struct.unpack_from('<III', image, 0xcb780) == (0, 0xa32, 0x600cad4c)
    machine = AuditMachine(image)
    uc = machine.uc
    command = 0
    transfers = []
    boundary_writes = []

    def write_hook(engine, access, address, size, value, user):
        nonlocal command
        if address == 0x40100900:
            command = value
        elif address == 0x40100904:
            assert command >> 28 == 2
            destination = 0x40100000 + (command & 0xfffff)
            assert 0x40150000 <= destination < 0x40158000
            engine.mem_write(destination, u32(value))
            boundary_writes.append({'destination': hex(destination), 'value': hex(value)})

    def upload_hook(engine, address, size, user):
        if address in (0x0100a90e, 0x0100a9e8):
            assert engine.reg_read(UC_ARM_REG_R1) == 0
            offset = engine.reg_read(UC_ARM_REG_R2) * 4
            length = engine.reg_read(UC_ARM_REG_R3)
            source = machine.register(engine.reg_read(UC_ARM_REG_SP))
            assert offset + length <= 0x8000
            destination = 0x40150000 + offset
            engine.mem_write(destination, bytes(engine.mem_read(source, length)))
            transfers.append({'source': hex(source), 'destination': hex(destination),
                              'length': length})
            engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.hook_add(UC_HOOK_CODE, upload_hook)
    uc.reg_write(UC_ARM_REG_R2, 0)
    uc.reg_write(UC_ARM_REG_R3, 0x600cb780)
    machine.call(0x0100bfe2, DSP_CONTEXT, 0)
    program = bytes(uc.mem_read(0x40150000, 0x8000))
    logical = b''.join(struct.pack('>I', v) for v in struct.unpack('<8192I', program))

    def words(address, expected):
        actual = list(struct.unpack_from('>' + 'H' * len(expected), logical, address))
        assert actual == expected, (hex(address), actual, expected)
        return {'logical_byte_offset': hex(address),
                'halfwords': ' '.join(f'{v:04x}' for v in actual)}

    pc = [words(0x20, [0x1e05, 0x0fe0, 0x1fe2, 0xa000, 0x0033])]
    for channel in range(1, 18):
        pc.append(words(0x2a + (channel - 1) * 18,
                        [0x7809, 0x0fe0, 0x8fe2, 0x1fe4, 0x9fe6,
                         0xa000 + channel, 0x001f + channel,
                         0x0033 + 2 * channel, 0xa011 + channel]))
    pc.append(words(0x15c, [0x1e05, 0x8fe0, 0x9fe2, 0x0031, 0xa023]))
    native_sources = list(range(0x6000, 0x6006)) + list(range(0x6008, 0x6012)) + [0x6006, 0x6007]
    native_buffers = list(range(0x000c, 0x0012)) + list(range(0x0014, 0x001e)) + [0x0012, 0x0013]
    native = [words(0x16a, [0x0c03, 0x0fe0, 0x6000])]
    for channel in range(1, 18):
        native.append(words(0x170 + (channel - 1) * 10,
                            [0x1e05, 0x0fe0, 0x8fe2,
                             native_sources[channel], native_buffers[channel - 1]]))
    native.append(words(0x21a, [0x0c03, 0x8fe0, 0x0013]))
    assert transfers == [{'source': '0x600cad4c', 'destination': '0x40150000', 'length': 2608}]
    assert boundary_writes == [{'destination': '0x40150a30', 'value': '0x0'}]
    return {
        'status': 'pass',
        'program_descriptor': {'runtime': '0x600cb780', 'decoded_offset': '0x000cb780',
                               'source': '0x600cad4c', 'length': 0xa32},
        'descriptor_parent': '0x600779cc',
        'uploader_entry': '0x0100bfe2',
        'program_memory_sha256': sha256(program),
        'modeled_dma': transfers, 'original_boundary_writes': boundary_writes,
        'pc_import_instructions': pc, 'serial_import_instructions': native,
        'finding': 'Both 18-lane import chains use 0fe0 reads and ordinary 8feX stores; '
                   'the PC import does not require the normal program\'s 1040/44c7/BEDA block.',
        'interpretation': 'Original matching import encodings support compatible a000..a011 '
                          'and 6000..6011 sample operands. This is firmware-derived evidence, '
                          'not a proprietary DSP arithmetic emulation.',
        'limitations': ['Bulk DMA and command-window storage are modeled.',
                        'No proprietary DSP instruction execution or physical audio is tested.'],
    }


def audit_input_gates(image):
    """Check native unity gates and the distinct connection-selector writes."""
    initial = AuditMachine(image)
    # The normal input object selects DSP0. No peripheral or arithmetic
    # function is replaced in this initializer execution.
    initial.uc.mem_write(0x605146c8, u32(0))
    initial.call(0x600251f2, 0x605146c8, 0)
    assert len(initial.writes) == 52
    for index in range(1, 14):
        assert initial.register(0x4014c000 + index * 16) == 0x80000000
        assert initial.register(0x4014c004 + index * 16) == 0x3f800000

    cases = []
    callbacks = (0x60027b44, 0x60027b7c, 0x60027bf8, 0x60027c20, 0x60027c48)
    for index, callback in enumerate(callbacks):
        for mode in (0, 2):
            for connected in (0, 1):
                machine = AuditMachine(image)
                machine.uc.mem_write(0x605146c8, u32(0))
                getters = []

                def getter_hook(engine, address, size, user):
                    if address == 0x6001a896:
                        assert engine.reg_read(UC_ARM_REG_R0) == 0x600b5390
                        parameter = engine.reg_read(UC_ARM_REG_R1)
                        assert parameter in (0x19, 0x0c)
                        getters.append(parameter)
                        engine.reg_write(UC_ARM_REG_R0, mode if parameter == 0x19 else 0)
                        engine.reg_write(UC_ARM_REG_PC, engine.reg_read(UC_ARM_REG_LR))

                machine.uc.hook_add(UC_HOOK_CODE, getter_hook)
                machine.call(callback, 0, connected)
                selector = 0x1de + index * 0x34
                value = 0x3f800000 if mode == 2 or not connected else 0
                assert machine.writes == [
                    (0x40100900, 4, 0x40050000 + selector), (0x40100904, 4, value),
                    (0x40100900, 4, 0x40050000 + selector + 0x1a), (0x40100904, 4, value),
                ]
                cases.append({'callback': hex(callback), 'mode': mode,
                              'connected': connected, 'parameter_reads': getters,
                              'selector_offsets': [hex(selector), hex(selector + 0x1a)],
                              'written_value': hex(value), 'native_coefficient_writes': 0})
    return {
        'status': 'pass',
        'native_initializer': {'runtime': '0x600251f2', 'decoded_offset': '0x000251f2',
                               'coefficient_indices': list(range(1, 14)),
                               'initial_value': '0x3f800000', 'mmio_writes': 52},
        'connection_callbacks': cases,
        'modeled': ['Normal input object explicitly selects DSP0.',
                    'Connection cases replace system-parameter getter 0x6001a896: '
                    'mode is 0 or 2; digital direction is input (0).'],
        'finding': 'These original connection callbacks change two embedded PC selectors only; '
                   'they do not update the native input coefficient gates.',
        'limitations': ['Driver connection state, external clocking, and physical audio are not emulated.',
                        'This does not prove that no other firmware path can change a native gate.'],
    }


def verify_image(image):
    """Return every independent audit for the exact decoded main image."""
    assert sha256(image) == MAIN_SHA256, 'Unsupported decoded main application'
    result = audit(image)
    result['dsp_task_dispatch'] = audit_event_dispatch(image)
    result['pc_operand_format'] = audit_pc_import(image)
    result['native_input_gates'] = audit_input_gates(image)
    return result


def verify(original):
    """Return reusable evidence for an exact original update container."""
    assert sha256(original) == ORIGINAL_SHA256, 'Unsupported original firmware'
    image = component_unpacked(original, COMPONENT_BY_NAME['app_main'])
    result = verify_image(image)
    result['original_container_sha256'] = sha256(original)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, default=Path('inputs/MX1_UPD.original.bin'))
    parser.add_argument('--output', type=Path, default=Path('analysis/routing-hardware-audit.json'))
    args = parser.parse_args()
    original = args.original.read_bytes()
    result = verify(original)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'dsp_rate_cases': 3,
                      'digital_mode_rate_cases': 6, 'report': str(args.output)}))


if __name__ == '__main__':
    main()
