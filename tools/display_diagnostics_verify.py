"""Diagnostic callbacks execute as ARM; panel delivery and RTOS remain modeled."""
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_PC, UC_ARM_REG_LR
from arm_machine import Machine
from mastering_verify import MasterMachine, STATE
from routing_ui_verify import KEYS, PAGE, BOOT, MODAL, u32
from container_tool import sha256
from diagnostic_heap_verify import verify as verify_heap

DIAG=0x010174d0

class DiagnosticMachine(MasterMachine):
    def __init__(self,image,symbols):
        self.host_parameters=[]; self.host_capture=False
        super().__init__(image,symbols)
    def instruction(self,uc,address,size,user):
        if self.host_capture and address in (0x6000c754,0x6000c794,0x010097e4):
            self.ret(); return  # Host-status transaction and error-log boundary.
        if self.host_capture and address==0x6000c7a0:
            self.host_parameters.append((uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
            self.ret(); return
        super().instruction(uc,address,size,user)
    def display(self): return ''.join(chr(c[2]) for c in self.characters[-7:])
    def enable(self):
        self.event(2,0x29); self.event(2,0)
        assert self.display()=='bLdd001'
        self.event(1,0); self.event(1,0x29)
    def page(self,index):
        self.write(DIAG+31,bytes([index]))  # Force page for independent value checks.
        self.write(DIAG+34,b'\0')
        self.tick(0)
        return self.display()
    def snapshot(self,offset): return struct.unpack('<4H',self.read(DIAG+offset,8))


def verify(original,patched,build):
    symbols=build['symbols']; groups=[]
    def passed(name,**kw): groups.append(dict(name=name,status='pass',**kw))
    assert symbols['mx1_diag_state']==DIAG
    assert build['diagnostics']['state_bytes']==36
    for offset,name in ((0xf5d8,'mx1_diag_event'),(0xf5dc,'mx1_diag_tick')):
        assert struct.unpack_from('<I',patched,offset)[0]==symbols[name]|1
    # Verify the original reader and notification decoder, not decompiler types.
    assert original[0x34e8:0x3780]==patched[0x34e8:0x3780]
    assert struct.unpack_from('<I',original,0x375c)[0]==0x600b1b3a
    m=DiagnosticMachine(patched,symbols)
    m.host_capture=True
    for port in range(4):
        m.write(0x600b1b3a+port,b'\0')
        for event,expected,status in ((0,1,0),(4,5,1),(5,1,0),(2,3,0),(4,7,1),(1,0,0)):
            m.checked(0x600035c8,0,port,event)
            assert m.read(0x600b1b3a+port,1)==bytes([expected])
            assert m.checked(0x600034e8,port)[0]==status
            assert (0x97+port,status) in m.host_parameters
        m.write(0x600b1b3a+port,b'\x0d')
        assert m.checked(0x600034e8,port)[0]==2
    passed('Original main host notification decoder and MIDI-ready reader establish displayed bits',
           component='app_main', decoded_offset='0x35c8', runtime='0x600035c8',
           flags_runtime='0x600b1b3a', midi_ready_bits='0x05, unless error bits 0x18',
           modeled='Transaction constructor/commit/parameter delivery and error logging')

    m=DiagnosticMachine(patched,symbols);m.enable()
    assert m.read(KEYS,16)==bytes(16)  # SELECT release preserved, entry TAP never reaches stock.
    assert not any(e.startswith('0200') or e.startswith('0100') for e in m.original_events)
    for expected in range(1,22):
        m.event(4,1,1); assert m.read(DIAG+31,1)==bytes([expected])
    m.event(4,1,1);assert m.display()=='bLdd001'
    m.event(4,1,-1);assert m.read(DIAG+31,1)==b'\x15'
    assert m.encoders==[] and m.adjustments==[]
    # No redraw or stock operation for idle ADC background when cached display is current.
    m.tick(0); before=len(m.characters)
    m.event(0xb,0,64);m.tick(0);assert len(m.characters)==before
    m.event(2,0x29);m.event(2,0);m.event(1,0);m.event(1,0x29)
    assert m.read(DIAG+30,1)==b'\0'
    m.event(4,1,1);assert m.encoders
    passed('SELECT 1 plus TAP toggles diagnostic display; TEMPO pages wrap without changing tempo/routes; releases preserved')

    # Enter the diagnostic UI despite each mastering guard; boot mode is excluded.
    for address,data in ((PAGE,struct.pack('<H',12)),(0x600b537c,u32(1)),(MODAL,u32(1))):
        m=DiagnosticMachine(patched,symbols);m.write(address,data);m.enable()
    m=DiagnosticMachine(patched,symbols);m.write(BOOT,u32(1))
    m.event(2,0x29);m.event(2,0);assert m.read(DIAG+30,1)==b'\0'
    passed('Diagnostic entry bypasses mastering page/lock/modal guards but excludes boot/setup')

    for addr,data,mask,first,high in ((BOOT,u32(1),1,0xffff,0),
            (0x600b537c,u32(1),2,0xffff,0),(PAGE,struct.pack('<H',12),4,0xffff,0),
            (MODAL,u32(1),8,0xffff,0),(KEYS+10,b'\x80',16,87,128)):
        m=DiagnosticMachine(patched,symbols);m.write(addr,data);m.event(2,0x17)
        guard,page,key,hi=m.snapshot(0)
        assert (guard,key,hi)==(mask,first,high)
        assert page==(12 if addr==PAGE else 5)
        assert m.read(DIAG+22,2)==b'\0\0' # post-MASTER state
        assert not m.active()
    m=DiagnosticMachine(patched,symbols);m.enable()
    m.event(2,0x17)
    assert m.snapshot(0)==(0,5,0xffff,0)
    assert m.page(1)=='btn0217' and m.page(7)=='MSt0002'
    m.event(2,0);assert m.active()
    assert m.page(1)=='btn0200' and m.page(10)=='tPr0002' and m.page(11)=='tPo0001'
    # Only the actual combo changes mastering state; diagnostic observation adds no transactions.
    m.event(1,0);m.event(1,0x17);m.exit()
    m.event(2,0x17);m.event(4,0,1)
    assert m.page(12)=='CAn0400'
    m.event(1,0x17);m.event(2,0x17);m.write(0x600b537c,u32(1));m.tick(0)
    assert m.page(12)=='CAnFFFE'
    passed('Captured button IDs, every entry guard including key 87, before/after chord state and event/tick cancellation')

    m=DiagnosticMachine(patched,symbols);m.enable()
    for port in range(4):
        m.write(0x600b1b3a+port,bytes([1+port*2]))
        m.write(0x200003fc+port,bytes([port&1]))
        m.write(0x20000401+port,bytes([1-(port&1)]))
        assert m.page(14+port)==f'U{port+1} {1+port*2:04X}'
        assert m.page(18+port)==f'C{port+1} {((port&1)<<8)|(1-(port&1)):04X}'
    m.page(18);m.write(0x200003fc,b'\x01');m.tick(0);assert m.display()=='C1 0101'
    passed('All four live host flag bytes and both per-port clock gates render independently; tick updates changed values')
    # Independently establish each displayed gate by the unchanged original sender.
    assert original[0xd171e:0xd1a0e]==patched[0xd171e:0xd1a0e]
    m=Machine(patched);sent=[]
    def mailbox(uc,address,size,user):
        if address not in (0x60057ebc,0x01009430): return
        if address==0x01009430: sent.append(m.read(uc.reg_read(UC_ARM_REG_R1),4))
        uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,mailbox)
    for port in range(4):
        for gate in (port,port+5):
            m.write(0x200003fc,b'\x01'*10);m.write(0x200003fc+gate,b'\0')
            m.write(0x20017000,u32(0xf80f));sent.clear()
            m.call(0x01000e92,0,0x20017000,0,0x2a800)
            assert sent==[u32(0xf80f|(p<<5)) for p in range(4) if p!=port]
    passed('Original MIDI sender independently rejects each host destination when either displayed clock gate is zero',
           runtime='0x01000e92',decoded_offset='0xd171e',modeled='Cross-core mailbox acceptance')
    # Execute original startup/allocator boundary verification through exhaustion.
    heap=verify_heap(original,patched,build);groups.extend(heap['groups'])
    return dict(status='pass',patched_app_sha256=sha256(patched),candidate_container_sha256=build['container_sha256'],
        groups=groups,hardware_access=False,limits=[
            'Control-task ARM execution; higher panel actions, periodic body, parameter notifications and final panel I/O modeled.',
            'Main host flags are delivered stock notifications, not USB enumeration traces or transfer-completion counters.',
            'No physical display, scheduler timing, peak heap use, USB PHY/DMA or FM-1 acceptance established.'])
