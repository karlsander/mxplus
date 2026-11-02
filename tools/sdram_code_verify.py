"""Execute stock SDRAM pool creation/allocation with the code reservation.

Pool creation and the low-level allocator run unchanged. SCB state is supplied
as thread mode; the scheduling decision at 0x01008e02 returns 1 to avoid task
switching. Allocation enters the actual pool primitive, not task wait wrappers.
This verifies memory exclusion, not peak workload usage or SDRAM timing.
"""
import struct
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_PC, UC_ARM_REG_LR
from arm_machine import Machine
from container_tool import sha256

OLD_START, CODE, NEW_START, END = 0x606634d0, 0x60664000, 0x60666000, 0x62000000


def verify(original, patched, build):
    assert sha256(patched) == build['patched_app_sha256']
    assert struct.unpack_from('<2I', original, 0xd768) == (END, OLD_START)
    assert struct.unpack_from('<2I', patched, 0xd768) == (END, NEW_START)
    assert patched[0xd6f4:0xd75e] == original[0xd6f4:0xd75e]
    assert build['scatter_extension']['heap_reservation'] == {
        'original_start': OLD_START, 'start': NEW_START, 'end_exclusive': END,
        'reserved_bytes': NEW_START - OLD_START, 'remaining_bytes': END - NEW_START}
    cases = []
    for label, app, base in (('stock', original, OLD_START), ('candidate', patched, NEW_START)):
        m = Machine(app)
        m.uc.mem_map(0x60800000, 0x1800000)  # Rest of the stock 32-MiB SDRAM pool.
        m.uc.mem_map(0xe000e000, 0x2000)
        descriptors, writes = [], []

        def code(uc, address, size, user):
            if address == 0x010033b8:
                descriptors.append(struct.unpack('<3I', m.read(uc.reg_read(UC_ARM_REG_R0), 12)))
            elif address == 0x01008e02:
                uc.reg_write(UC_ARM_REG_R0, 1)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        m.uc.hook_add(UC_HOOK_CODE, code)
        m.uc.hook_add(UC_HOOK_MEM_WRITE,
            lambda u,a,address,size,value,d: writes.append((address,size)),
            begin=OLD_START, end=END-1)
        m.call(0x01006338, count=500000)  # Original RTOS fixed pool setup.
        before = m.read(OLD_START, NEW_START - OLD_START)
        if label == 'candidate':
            from routing_mpu_verify import protect_code
            protect_code(m)
        ident = m.call(0x6000d6f4)[0]  # Original heap initializer + pool creator.
        assert ident == 3
        assert len(descriptors) == 1
        assert descriptors[0][0] & 0xffff == 1
        assert descriptors[0][1:] == (END-base, base)
        control = 0x01014e18 + (ident-1)*0x44
        assert struct.unpack('<2I', m.read(control+0x1c,8)) == (END-base,base)
        allocations = []
        for size in (16, 4096, 0x100000):
            ptr = m.call(0x01007604, control, size, 0)[0]
            assert base <= ptr and ptr+size <= END
            allocations.append({'address': hex(ptr), 'requested_bytes': size})
        largest = struct.unpack('<I', m.read(control+0x28,4))[0]
        remaining = struct.unpack('<I', m.read(largest+8,4))[0]
        ptr = m.call(0x01007604, control, remaining, 0)[0]
        assert base <= ptr and ptr+remaining <= END
        allocations.append({'address': hex(ptr), 'requested_bytes': remaining})
        assert m.call(0x01007604, control, 16, 0)[0] == 0, 'Exhausted pool did not fail'
        assert writes and all(base <= address and address+size <= END for address,size in writes)
        if label == 'candidate':
            assert m.read(OLD_START, NEW_START-OLD_START) == before
        cases.append({'image': label, 'heap_start': hex(base), 'heap_bytes': END-base,
                      'allocations': allocations, 'exhausted_request_returns_null': True,
                      'lowest_allocator_write': hex(min(a for a,_ in writes)),
                      'reservation_unchanged': label == 'candidate'})
    assert cases[0]['heap_bytes'] - cases[1]['heap_bytes'] == 11056
    return {'status': 'pass', 'candidate_container_sha256': build['container_sha256'],
        'patched_app_sha256': sha256(patched), 'groups': [
            {'name': 'Stock SDRAM heap creation and allocation exclude reserved code through exhaustion',
             'status': 'pass', 'heap_initializer': '0x6000d6f4', 'pool_creator': '0x010033b8',
             'allocation_primitive': '0x01007604', 'heap_base_literal_decoded': '0xd76c',
             'reserved_bytes': 11056, 'cases': cases}],
        'limits': ['SCB reads thread mode; scheduling decision 0x01008e02 is stubbed to return 1.',
                   'Allocations enter the original low-level primitive; task wait/free wrappers are not exercised.',
                   'Does not establish peak heap usage, memory-bus timing, or IRQ deadline margin.']}
