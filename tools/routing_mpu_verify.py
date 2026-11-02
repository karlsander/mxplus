#!/usr/bin/env python3
"""Execute stock MPU setup and verify the routing writable-state reservation.

Unicorn does not enforce the Cortex-M MPU registers itself. We capture the
original register writes, decode the applicable permissions, and explicitly
protect the full code pages in the routing instruction harnesses. This models
permission denial, not delivery of a real MemManage exception or DSP timing.
"""
import struct
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_PROT_READ, UC_PROT_EXEC
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
from arm_machine import Machine, BASE
from memory_map import recover


def protect_code(machine):
    # Region 1 is read-only throughout this interval; higher-priority RW
    # regions 3/4 affect only 0x01000000..0x010002ff, outside these pages.
    machine.uc.mem_protect(0x01001000, 0xf000, UC_PROT_READ | UC_PROT_EXEC)


def original_mpu(image):
    machine = Machine(image)
    machine.uc.mem_map(0xe000e000, 0x2000)
    regions, selected, enabled = {}, [0], [0]

    def instruction(uc, address, size, user):
        if address == 0x60054ef8:  # Register exception handler; no MPU writes here.
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def write(uc, access, address, size, value, user):
        assert size == 4
        if address == 0xe000ed98:
            selected[0] = value
        elif address == 0xe000ed9c:
            regions.setdefault(selected[0], {})['base'] = value
        elif address == 0xe000eda0:
            regions[selected[0]]['attributes'] = value
        elif address == 0xe000ed94:
            enabled[0] = value
        else:
            raise AssertionError(hex(address))

    machine.uc.hook_add(UC_HOOK_CODE, instruction)
    machine.uc.hook_add(UC_HOOK_MEM_WRITE, write, begin=0xe000ed90, end=0xe000edb8)
    machine.call(0x6000d824)
    assert enabled == [1]
    assert len(regions) == 7
    for region in regions.values():
        attr = region['attributes']
        region['size'] = 1 << (((attr >> 1) & 31) + 1)
        region['access_permission'] = (attr >> 24) & 7
        assert attr & 1 and not (attr & 0xff00), 'Unsupported disabled/subregion map'
    return regions


def permission(regions, address):
    for index in sorted(regions, reverse=True):
        r = regions[index]
        if r['base'] <= address < r['base'] + r['size']:
            return r['access_permission']
    raise AssertionError('Unmapped MPU address')


def verify(original, patched, build):
    regions = original_mpu(original)
    assert original_mpu(patched) == regions, 'Stock MPU setup changed'
    assert regions[1] == {'base': 0x01000000, 'attributes': 0x06000021,
                          'size': 0x20000, 'access_permission': 6}
    assert regions[2] == {'base': 0x01010000, 'attributes': 0x1300001d,
                          'size': 0x8000, 'access_permission': 3}
    assert all(permission(regions, a) == 6 for a in range(0x01001000, 0x01010000))
    state, end = 0x01017264, 0x010173f4
    assert build['writable_state']['start'] == state and build['writable_state']['end_exclusive'] == end
    assert build['symbols']['mx1_route_state'] == state
    assert all(permission(regions, a) == 3 for a in range(state, end))
    for name in ('mx1_uac2_rate', 'mx1_uac2_reply', 'mx1_uac2_configuration'):
        assert state <= build['symbols'][name] < end
        assert permission(regions, build['symbols'][name]) == 3
    old_bss, new_bss = recover(original)['operations'][3], recover(patched)['operations'][3]
    assert old_bss['destination'] + old_bss['length'] == state
    assert new_bss['destination'] + new_bss['length'] == end

    for pattern in (0x55, 0xaa):
        machine = Machine(patched, scatter=False)
        machine.write(0x01000000, bytes([pattern]) * 0x18000)
        machine.write(0x01020000, bytes([pattern]) * 0x10000)
        machine.uc.reg_write(UC_ARM_REG_SP, 0x2001fff0)
        machine.uc.emu_start(BASE | 1, BASE + 0x7e, timeout=5_000_000, count=3_000_000)
        assert machine.uc.reg_read(UC_ARM_REG_PC) == BASE + 0x7e
        assert machine.read(state, 24) == bytes(24)
        assert machine.read(0x010173e0, 20) == bytes(20)
        from uac2_design import prototype_configuration
        assert machine.read(0x0101727c, 356) == prototype_configuration(preserve_modes=True) + b'\0'
        assert machine.read(end, 4) == bytes([pattern]) * 4
        # Exercise original pool initialization over sentinels in the reserve.
        machine.uc.mem_map(0xe000e000, 0x2000)
        assert struct.unpack('<8I', machine.read(0x0100f234, 32)) == (
            1, 0, 0x8000, 0x01020000, 2, 0, 0x1000, 0x01013e18)
        machine.write(state, bytes([pattern]) * 400)
        machine.call(0x01006338, count=500_000)
        assert machine.read(state, 400) == bytes([pattern]) * 400
    return {'status': 'pass', 'mpu_setup': {'decoded_offset': '0xd824', 'runtime': '0x6000d824',
                'regions': regions, 'exception_registration': 'stubbed at 0x60054ef8'},
            'groups': [
                {'name': 'Original MPU makes injected code read-only and new route state read-write', 'status': 'pass',
                 'code_protection': '0x01001000..0x0100ffff enforced in all UI/audio instruction cases',
                 'state_interval': [hex(state), hex(end)]},
                {'name': 'Dirty cold startup clears state; original RTOS pools cannot allocate its reservation', 'status': 'pass',
                 'general_pool': ['0x01013e18', '0x01014e18'], 'stack_pool': ['0x01020000', '0x01028000'],
                 'state_reservation_bytes': 400, 'descriptor_initialized_bytes': 356, 'patterns': [85, 170]}],
            'limits': ['Permission rejection is modeled with Unicorn page protection; no real MemManage exception delivery.',
                       'RTOS initializer ICSR reads use thread-mode zero; no hardware or numerical DSP execution.']}
