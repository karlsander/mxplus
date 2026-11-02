"""Original scene copies and autosave scheduling with modeled flash/RTOS edges."""
import struct
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
from arm_machine import Machine, RETURN
from routing_audio_verify import REGS
from routing_mpu_verify import protect_code

MIX = 0x604f4014
SYSTEM = 0x604f39a4
MIX_SIZE, SYSTEM_SIZE = 1072, 564
SCENE_RECORD = MIX + 0x1cc
SYSTEM_RECORD = SYSTEM + 0x40
MAGIC = b'MXR1'

def record(routes): return MAGIC + bytes(routes) + b'\0'
def u32(v): return struct.pack('<I', v)

class StorageMachine(Machine):
    def __init__(self, image, symbols):
        super().__init__(image)
        protect_code(self)
        self.symbols = symbols
        self.writes = []
        self.posts = []
        self.registrations = []
        self.now = 10000
        self.uc.hook_add(UC_HOOK_CODE, self.hook)
    def call(self, address, *args, **kwargs):
        before = tuple(self.uc.reg_read(r) for r in REGS)
        result = super().call(address, *args, **kwargs)
        assert tuple(self.uc.reg_read(r) for r in REGS) == before, 'Callee-saved register changed'
        return result
    def ret(self, value=0):
        self.uc.reg_write(UC_ARM_REG_R0, value)
        self.uc.reg_write(UC_ARM_REG_PC, self.uc.reg_read(UC_ARM_REG_LR))
    def hook(self, uc, address, size, user):
        args = tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address in (0x6005664c, 0x600596d8, 0x6005a034, 0x6000d3e2, 0x6000becc, 0x6001a896, RETURN+0x100):
            self.ret()  # Singletons, notifications, DSP event, mode, mutex.
        elif address == 0x0100e266:
            self.posts.append(args[:2])
            self.ret()
        elif address == 0x6000e1c2:
            sp = uc.reg_read(UC_ARM_REG_SP)
            length = struct.unpack('<I', self.read(sp, 4))[0]
            self.writes.append((args[2], args[3], self.read(args[3], length)))
            self.ret()  # Observe request; physical programming is not executed.
        elif address == 0x6000e216:
            stack = struct.unpack('<4I', self.read(uc.reg_read(UC_ARM_REG_SP), 16))
            self.registrations.append((*args, *stack))
            self.ret()  # Observe original group registration.
        elif address == 0x6000e240:
            self.ret()  # Storage backend header setup.
        elif address in (0x60054f02, 0x010037e8):
            self.write(args[0], struct.pack('<2I', 0, self.now))
            self.ret()
        elif address == 0x60056994:
            uc.reg_write(UC_ARM_REG_PC, RETURN)  # Stop after original boot BL.
    def copy_group(self, group, destination_slot, source_slot):
        context = 0x20018000
        self.call(0x6000c158, context, group, destination_slot)
        return self.call(0x6000c182, context, group, source_slot, 0)[0]
    def routes(self):
        return bytes(self.call(self.symbols['mx1_route_get'], i)[0] for i in range(11))
    def boot(self):
        self.copy_group(0, 0, 1)  # Stock system restore, real group-copy code.
        self.call(0x60056990, 0, 0)  # Unchanged normal-startup call to scene 0.
        assert self.posts[-1] == (0x6051dea8, 8)


def verify(original, patched, build):
    symbols = build['symbols']
    m = StorageMachine(patched, symbols)
    # Execute original registration: group 0 auto-saves 141 words, group 2
    # explicitly saves 65 slots of 268 words. No storage sizes/flags change.
    m.call(0x6000c8e0, 0)
    regs = {r[2]: r for r in m.registrations}
    assert regs[0][3:6] == (1, SYSTEM + SYSTEM_SIZE, SYSTEM_SIZE)
    assert regs[2][3:6] == (0, MIX + MIX_SIZE, MIX_SIZE * 65)
    old = StorageMachine(original, {})
    old.call(0x6000c8e0, 0)
    assert old.registrations == m.registrations

    # All 64 user slots round-trip via original save, copy and recall code.
    m.boot()
    routes = bytes([1, 6, 7, 9, 5, 8, 11, 20, 26, 50, 52])
    baseline = bytes((i * 17 + 3) & 255 for i in range(MIX_SIZE))
    for slot in range(1, 65):
        m.write(MIX, baseline)
        m.write(SCENE_RECORD, record(routes))
        m.call(0x6001e734, 0, slot + 1)
        group, ptr, payload = m.writes[-1]
        expected = bytearray(baseline)
        expected[0x1cc:0x1dc] = record(routes)
        assert group == 2 and ptr == MIX + (slot + 1)*MIX_SIZE
        assert payload == bytes(expected)
        m.write(MIX, bytes(MIX_SIZE))
        posts = len(m.posts)
        m.call(0x6001e786, 0, slot)
        assert len(m.posts) == posts+1 and m.posts[-1] == (0x6051dea8, 8)
        assert m.routes() == routes
        assert m.read(MIX, MIX_SIZE) == expected
        assert m.read(SYSTEM_RECORD, 16) == record(routes)
    # Cold restart loads last routes even if startup scene contains different
    # routes, and leaves every other startup-scene setting unchanged.
    cold = StorageMachine(patched, symbols)
    m.copy_group(0, 1, 0)  # Snapshot the system bytes; autosave path tested below.
    saved = m.read(SYSTEM + SYSTEM_SIZE, SYSTEM_SIZE)
    cold.write(SYSTEM + SYSTEM_SIZE, saved)
    cold.write(MIX + MIX_SIZE, baseline)
    cold.boot()
    assert cold.routes() == routes
    assert cold.read(MIX, 0x1cc) == baseline[:0x1cc]
    assert cold.read(MIX+0x1dc, MIX_SIZE-0x1dc) == baseline[0x1dc:]
    # Latest edits reach both system copies; snapshots are not overwritten.
    before = cold.read(MIX + MIX_SIZE, MIX_SIZE*65)
    cold.call(symbols['mx1_route_adjust'], 10, 0xffffffff)
    assert cold.routes()[10] == 51
    assert cold.read(SYSTEM_RECORD, 16) == record(cold.routes())
    assert cold.read(SYSTEM_RECORD + SYSTEM_SIZE, 16) == record(routes), 'Autosave shadow must stay dirty until stock timer observes it'
    assert cold.read(MIX + MIX_SIZE, MIX_SIZE*65) == before
    # Model higher-priority DSP refresh of the route cache during a UI save.
    race = StorageMachine(patched, symbols)
    race.boot()
    refreshes = []
    pending = []
    def refresh(uc, access, address, size, value, user):
        if not refreshes: pending.append(address)
    def interrupt(uc, address, size, user):
        if pending and not refreshes:
            refreshes.append(pending[0])
            uc.emu_stop()
    code_hook = race.uc.hook_add(UC_HOOK_CODE, interrupt)
    hook = race.uc.hook_add(UC_HOOK_MEM_WRITE, refresh, begin=SCENE_RECORD+4, end=SCENE_RECORD+14)
    race.uc.reg_write(UC_ARM_REG_SP, 0x2001fff0)
    race.uc.reg_write(UC_ARM_REG_LR, RETURN|1)
    race.uc.reg_write(UC_ARM_REG_R0, 10)
    race.uc.reg_write(UC_ARM_REG_R1, 1)
    race.uc.emu_start(symbols['mx1_route_adjust'], RETURN, count=100000)
    assert refreshes and race.uc.reg_read(UC_ARM_REG_PC) != RETURN
    resume = race.uc.reg_read(UC_ARM_REG_PC)
    race.write(symbols['mx1_route_state'], bytes(11))
    race.uc.hook_del(hook)
    race.uc.hook_del(code_hook)
    race.uc.emu_start(resume|1, RETURN, count=100000)
    assert race.uc.reg_read(UC_ARM_REG_PC) == RETURN and race.uc.reg_read(UC_ARM_REG_SP) == 0x2001fff0
    assert refreshes and race.routes() == bytes(10)+b'\x01'
    assert race.read(SYSTEM_RECORD+14, 1) == b'\x01'
    # Legacy scenes, invalid versions and every bad source byte fail to Auto.
    for raw in (bytes(16), b'\xff'*16, b'MXR2'+bytes(12)):
        cold.write(SCENE_RECORD, raw)
        assert cold.routes() == bytes(11)
    for strip in range(11):
        for value in range(53, 256):
            data = bytearray(record(routes)); data[4+strip] = value
            cold.write(SCENE_RECORD, data)
            assert cold.call(symbols["mx1_route_get"], strip)[0] == 0
    for strip in range(4):
        data = bytearray(record(routes)); data[4+strip] = 5
        cold.write(SCENE_RECORD, data)
        assert cold.routes()[strip] == 0

    # Original autosave comparison and deadline arithmetic. One registered
    # system block is modeled; bytes/length/mode match original registration.
    auto = StorageMachine(patched, symbols)
    obj, node, vtable = 0x20014000, 0x20014100, 0x20016000
    auto.write(obj, u32(vtable)+u32(node))
    auto.write(vtable+0x20, u32(RETURN+0x101)*2)
    auto.write(node+0x1c, u32(SYSTEM+SYSTEM_SIZE)+u32(SYSTEM_SIZE))
    auto.write(node+0x2c, u32(SYSTEM)+b'\x01')
    auto.write(node+0x50, u32(node)*2)
    auto.write(SYSTEM_RECORD, record(routes))
    auto.call(0x6000e0f0, obj, 0, 0)
    assert auto.read(SYSTEM_RECORD+SYSTEM_SIZE, 16) == record(routes)
    assert struct.unpack('<2I', auto.read(node+0x48, 8)) == (11500, 0)
    auto.now = 11000
    auto.call(0x6000e058, obj, 0, 0, 0)
    assert auto.read(node+0x40, 1) == b'\0'
    # Further edits postpone the stock deadline; unchanged bytes do not.
    auto.write(SYSTEM_RECORD+4, b'\x02')
    auto.call(0x6000e0f0, obj, 0, 0)
    assert struct.unpack('<2I', auto.read(node+0x48, 8)) == (12500, 0)
    auto.now = 12000
    auto.call(0x6000e0f0, obj, 0, 0)
    assert struct.unpack('<2I', auto.read(node+0x48, 8)) == (12500, 0)
    auto.now = 12501
    auto.call(0x6000e058, obj, 0, 0, 0)
    assert auto.read(node+0x40, 1) == b'\x01'
    from container_tool import sha256
    return {'status':'pass', 'patched_app_sha256': sha256(patched), 'groups': [
        {'name':'Original storage registration remains identical; existing reserved fields only', 'status':'pass'},
        {'name':'All 64 scene saves/recalls retain routes and all unrelated scene bytes', 'status':'pass'},
        {'name':'Cold restart restores last routes independently of startup scene; edits preserve snapshots', 'status':'pass'},
        {'name':'UI retains its selected source across a modeled DSP cache refresh', 'status':'pass'},
        {'name':'Legacy, unknown-version, out-of-range and invalid mono records fall back to Auto', 'status':'pass'},
        {'name':'Stock autosave observes route bytes and coalesces edits with unchanged 1500-tick delay', 'status':'pass'}],
        'boundaries': ['Original scene copy/save/recall and autosave comparison/deadline ARM instructions execute',
                       'Storage requests are captured; flash erase/program and power-loss durability are not emulated',
                       'Storage nodes, time, singleton access, notifications and mutex calls are modeled',
                       'Restart fixtures supply the saved settings bytes; physical flash reload is untested',
                       'Text backup omits reserved fields; it does not export custom routes']}
