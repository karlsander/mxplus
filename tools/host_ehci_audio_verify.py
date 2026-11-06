"""Original EHCI initialization/worker plus compiled split-ISO extension.

Heap, IRQ/task setup, DMA/MMIO, RTOS delivery and DSP are explicit models.
This does not execute a USB transaction or establish real-time scheduling.
"""
import struct
from unicorn.arm_const import *
from unicorn import UC_HOOK_CODE
from arm_machine import RETURN

P=lambda *v:struct.pack('<'+'I'*len(v),*v)
H=lambda v:struct.pack('<H',v)

def verify(image,h,syms):
    from host_audio_verify import Audio,DEV,EP,DRIVER,HC,REGS,TD,TDSTRIDE,STRIDE
    table=0x4000b000;cap=0x40020000;initial_table=0x60470000

    class Ehci(Audio):
        def __init__(self,port=0):
            self.alloc=[];self.polls=[];self.real_poll=False;self.reset_halt=True
            super().__init__(image,h,syms)
            self.p+=port*STRIDE
            m=self.m
            m.write(HC,bytes(0x600));m.write(REGS,bytes(0x100))
            m.write(DEV+0x4a,H(1)+H(3))
            m.write(0x6002b0ec,P(DRIVER));m.write(DRIVER+0x40,P(HC))
            m.write(HC,P(cap,REGS));m.write(cap+8,P(0x80))
            # Run original ten periodic dummy roots and asynchronous anchor.
            assert m.call(0x60010356,HC,initial_table)[0]==0 and len(self.alloc)==11
            self.call('mx1_ehci_bind',1,DRIVER);m.write(DRIVER+0x40,P(HC))
            assert self.u32(DRIVER+12)==h['symbols']['mx1_ehci_request']
            assert self.u32(DRIVER+8)==h['symbols']['mx1_ehci_reset']
            assert self.u32(DRIVER+0x2c)==h['symbols']['mx1_ehci_event']
            m.call(0x60007faa) # actual replacement table and stock iTD chain
            assert self.u32(REGS+20)==table and self.u32(HC+8)==initial_table
            self.baseline=m.read(table,1024)
            self.original_chain=m.read(0x4000b420,512)
            m.write(REGS,P(0x10039,0x4000,0x33,0,0,table))
            m.write(syms['diagnostics']+44*port+12,P(1))
            m.write(syms['debug_ports']+780*port,P(DEV))
            m.write(syms['debug_ports']+780*port+716,P(1,3,0,1,0x20018000,0x20018100,1,1,0x400,0x424,0x2514,1))
            m.write(DEV+0xec,P(0x20018000));m.write(0x20018004,P(0x20018100,DEV))
            m.write(0x2001814a,H(1)+H(1));m.write(0x20018158,H(0x400))
        def stub(self,u,a,size,data):
            r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
            result=0
            if a==0x6000b330:
                assert r[1:3]==[56,64]
                result=0x60480800+len(self.alloc)*64;self.alloc.append(result)
            elif a in (0x60014ae4,0x010003b8,0x6000a548,0x60015536,0x60015540,0x60008d16,0x60009034):pass
            elif a in (0x600111ee,0x600113ae,0x60011be4):self.stock.append((a,r))
            elif a==0x600107f6:
                self.stock.append((a,r))
                if r[1]==2:
                    if self.reset_halt:self.m.write(REGS+4,P(0x1000))
                    self.m.write(DRIVER+0x40,P(0));self.m.write(HC,b'\xa5'*0xa0)
                    result=0xffffffec # model freed context despite cleanup error
            elif a==0x6000c376:
                if self.real_poll:return
                self.polls.append(r[:3])
            else:return super().stub(u,a,size,data)
            u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        def start(self,frame=2040):
            self.m.write(self.p,P(DEV,EP,0,0,1,1,0,0,1))
            self.m.write(REGS+12,P(frame*8))
            return self.call('mx1_ehci_request',DEV,EP,0,0,0,0,0,syms['start_done'],self.p)
        def state(self,word):return self.u32(syms['ehci']+word*4)
        def advance(self,f):
            self.m.write(REGS+12,P((f&2047)*8))
            self.call('mx1_ehci_event',1,1)
        def complete(self,i,frames=44,status=2):
            t=self.p+TD+i*TDSTRIDE
            self.m.write(t+12,P(0x80000400|((184-frames*4)<<16)|status))
            self.m.write(t+32,struct.pack('<'+'h'*(frames*2),*([1234,-2345]*frames)))
        def poll_done(self):
            controller,callback,token=self.polls[-1]
            self.m.call(callback,controller,0,token)

    q=Ehci();m=q.m;p=q.p
    publication=[]
    def publish(u,a,size,data):
        if q.u32(p+24)==2:
            assert q.state(51)==0xffff, 'Audio task could see a partially built ring'
            publication.append(a)
    hook=m.uc.hook_add(UC_HOOK_CODE,publish)
    assert q.start()==0 and q.u32(p+24)==2 and len(q.events)==1
    m.uc.hook_del(hook);assert publication
    assert q.u32(syms['diagnostics']+4)==0x56
    for i in range(16):
        t=p+TD+i*TDSTRIDE;data=t+32;f=(2044+i)&2047
        assert t%32==0 and q.u32(table+(f&255)*4)==t|4
        assert m.read(t+4,12)==P(0x81010403,0x1c01,0x80b80080)
        assert m.read(t+16,12)==P(data,(data+183)&~4095,1)
        assert q.u32(t)==struct.unpack_from('<I',q.baseline,(f&255)*4)[0]
    # Completion state bit 1 is legal; no packet/descriptor reuse before the
    # old H-frame is two frames past, including FRINDEX and frame-list wrap.
    q.complete(0);q.advance(2045);assert q.u32(p+72)==0
    q.advance(2046);assert q.u32(p+72)==1
    frames_consumed=0
    for ms in range(1,300):
        i=ms%16;frames=45 if ms%10==9 else 44
        q.complete(i,frames);q.advance((2044+ms+2)&2047)
        for quarter in range(4):q.call('mx1_audio_tick',quarter*2)
        if q.polls and q.state(65):q.poll_done()
        frames_consumed+=frames
    assert q.u32(p+72)==300 and q.u32(p+76)==0
    assert q.u32(p+80)==q.u32(p+84)==0
    assert m.read(0x4000b420,512)==q.original_chain
    assert q.state(59)==1234 and q.state(60)==2345 and q.state(61)==300
    assert sum(len(x[2])//2 for x in q.dsp)==sum(45 if ms%10==9 else 44 for ms in range(299))
    # Readout belongs to EHCI pages 5..7; cached raw layout includes live table.
    raw=syms['debug_ports']+308
    assert m.read(raw,12)==P(HC,REGS,table)
    assert q.u32(raw+32*4)==0x81010403 and q.u32(raw+33*4)==0x1c01
    def page(number):
        b=bytearray([0xf0,0x7d,0x44,0x42,1,1,13,2,number,0,0,0,0])
        b.extend([(-sum(b[1:]))&127,0xf7])
        m.write(EP+0x20,P(0x20019000));m.write(0x20019008,P(DEV))
        for i in range(0,len(b),3):
            part=b[i:i+3];word=(4+len(part) if i+3>=len(b) else 4)|sum(x<<(8+j*8) for j,x in enumerate(part))
            assert q.call('mx1_debug_receive',0,EP,word)==1
        wire=bytearray();out=0x2001c000
        for _ in range(10):
            n=q.call('mx1_debug_transmit',0,EP,out)
            if not n:break
            for word in struct.unpack('<'+'I'*n,m.read(out,n*4)):
                wire.extend(word.to_bytes(4,'little')[1:1+(3 if word&15==4 else (word&15)-4)])
        assert wire[-1]==0xf7 and not sum(wire[1:-1])&127
        return [sum(wire[i+j]<<(j*7) for j in range(5)) for i in range(8,len(wire)-2,5)]
    assert page(0)==[2]
    assert page(5)[3:6]==[HC,REGS,table]
    assert len(page(6))==37 and len(page(7))==35
    sequence=q.u32(syms['debug_ports']+304);m.write(syms['debug_ports']+304,P(sequence|1))
    assert page(5)==[2];m.write(syms['debug_ports']+304,P(sequence))
    # Transport-only mode drains accepted PCM and collects peaks without any
    # converter submission. Its timeout stops; it never falls back to audio.
    d=syms['debug_ports'];sd=syms['dsp_diagnostics']
    m.write(d+276,P(3,240000));m.write(syms['debug_ticks'],P(31))
    calls=len(q.dsp);q.call('mx1_audio_tick',0)
    assert len(q.dsp)==calls and q.u32(sd+4)==calls
    assert page(8)[3:6]==[calls,calls,0] and page(8)[10]==3
    snapshot=m.read(sd,144)
    # A page request consumes cached RAM, even if hardware is inaccessible.
    m.uc.mem_unmap(0x40100000,0x10000)
    assert page(8)[2]==q.u32(sd) and m.read(sd,144)==snapshot
    m.uc.mem_map(0x40100000,0x10000)
    m.write(sd,P(q.u32(sd)|1));assert page(8)==[2];m.write(sd,snapshot)
    m.write(syms['debug_ticks'],P(240000));q.call('mx1_audio_tick',0)
    assert len(q.dsp)==calls and q.u32(p+16)==0
    # Restore the test's active state for explicit cancellation below.
    m.write(p+16,P(1));m.write(d+276,P(0));m.write(syms['debug_ticks'],P(1200))
    # Stop leaves current DMA buffers intact, unlinks only our heads and waits
    # for frame progress. The original OHCI wrapper must not inspect EHCI RAM.
    q.call('mx1_ehci_cancel',DEV,EP);saved=m.read(p+TD,16*TDSTRIDE)
    assert q.u32(p+24)==3 and m.read(table,1024)==q.baseline
    q.call('mx1_ohci_event',0,4);assert q.u32(p+24)==3
    stopped=q.u32(p+40);q.advance(stopped+1);assert q.u32(p+20)==1
    q.advance(stopped+2);assert q.u32(p+20)==q.u32(p+24)==0
    assert m.read(p+TD,16*TDSTRIDE)==saved
    if q.state(65):q.poll_done()
    assert q.start(frame=100)==0
    # Full, short, active, malformed and errored DMA outcomes. No status other
    # than inactive/no-error may publish a packet, even if byte count is valid.
    outcomes=[]
    for i,(frames,status,valid) in enumerate([(46,0,1),(40,2,1),(44,0x40,0),(44,0x84,0),(44,4,0),(39,2,0)]):
        before=q.u32(p+72);q.complete(i,frames,status);q.advance(106+i)
        assert q.u32(p+72)-before==valid;outcomes.append([frames,status,valid])
    q.call('mx1_ehci_cancel',DEV,EP);q.advance(q.u32(p+40)+2)
    # New transfer admission must not pass an unbudgeted periodic endpoint to
    # the original driver while our descriptors are still retiring.
    q=Ehci();assert q.start()==0;q.m.write(EP+0x100+10,b'\x03')
    before=len(q.stock)
    assert q.call('mx1_ehci_request',DEV,EP+0x100,0,0,0,0,0,0,0)==0xfffffff3
    assert len(q.stock)==before and q.u32(q.p+24)==3
    assert q.call('mx1_ehci_request',DEV,EP+0x200,0,0,0,0,0,0,0)==0
    assert q.stock[-1][0]==0x600111ee # control/bulk remains stock
    # Frozen frame retains ownership; request polling is bounded to one. The
    # callback after unlink never follows an endpoint/device that was freed.
    q.m.write(syms['debug_ticks'],P(31));q.call('mx1_audio_tick',0)
    assert len(q.polls)==1 and q.state(65)==1
    q.m.write(syms['debug_ticks'],P(63));q.call('mx1_audio_tick',0)
    assert len(q.polls)==1
    q.m.uc.mem_unmap(DEV,0x1000);q.poll_done()
    assert q.u32(q.p+20)==1
    q.advance(q.u32(q.p+40)+2);assert q.u32(q.p+20)==0
    # Changed links are never overwritten, and those DMA objects are retained.
    q=Ehci();assert q.start()==0;entry=table+(2044&255)*4
    q.m.write(entry,P(0x12345678));q.call('mx1_ehci_cancel',DEV,EP);q.advance(2050)
    assert q.u32(entry)==0x12345678 and q.u32(q.p+20)==1 and q.u32(q.p+24)==3
    # A teardown error may follow a freed context. Only a verified halt releases
    # descriptor ownership; otherwise quarantine, never dereference freed HC.
    for halted in (True,False):
        q=Ehci();q.reset_halt=halted;assert q.start()==0
        assert q.call('mx1_ehci_reset',1,2)==0xffffffec
        assert q.u32(q.p+12)==0 and q.u32(q.p+24)==(0 if halted else 4)
        assert q.u32(q.p+20)==(0 if halted else 1)
        q.call('mx1_ehci_event',1,1)
    # Guard the actual running controller, table identity, TT route and absence
    # of existing stock audio. Reject without editing the running periodic list.
    negatives=[]
    for address,value in [(REGS,0x10009),(REGS+4,0x5000),(REGS+20,initial_table),
                          (REGS+16,1),(0x4000bbb0,1),(0x4000b424,0x80000000),
                          (syms['debug_ports']+716+8*4,0),(table,0x60480804)]:
        q=Ehci();q.m.write(address,P(value));before=q.m.read(table,1024)
        assert q.start()==0xfffffffb,(hex(address),value)
        assert q.m.read(table,1024)==before and q.u32(q.p+24)==0
        negatives.append([hex(address),value])
    # Watchdogs expire without a command/IOC and never reset the controller.
    for elapsed,stage in [(240001,0x58),(401,0x5a)]:
        q=Ehci();assert q.start()==0;q.m.write(syms['debug_ticks'],P(elapsed));q.advance(2041)
        assert q.u32(q.p+24)==3 and q.u32(syms['diagnostics']+4)==stage
    # Physical HOST3 uses port index 2, whose existing buffer placement crosses
    # a 4-KiB page. Validate both DMA page words against that actual layout.
    q=Ehci(port=2);assert q.start()==0;crossed=[]
    for i in range(16):
        td=q.p+TD+i*TDSTRIDE;data=td+32
        if data>>12!=(data+183)>>12:
            assert q.u32(td+16)==data and q.u32(td+20)==(data+183)&~4095
            crossed.append(i)
    assert crossed
    # The original converter's busy-gate return is a real instruction path,
    # not a mocked failure. Capture it, keep the DMA alive until worker stop.
    q=Ehci(port=2);assert q.start()==0;q.real_dsp=True
    ctx=0x20005ee0+2*0xa4;gate=0x40101200;sd=syms['dsp_diagnostics']+2*144
    q.m.write(ctx+20,P(gate));q.m.write(gate,P(7))
    q.call('mx1_audio_tick',0)
    assert q.u32(sd+4)==1 and q.u32(sd+8)==0 and q.u32(sd+12)==0xffffffff
    assert q.u32(sd+16)==7 and q.u32(sd+24+11*4)==gate
    assert q.u32(q.p+92)==1 and q.u32(q.p+16)==0 and q.u32(q.p+24)==2
    q.advance(2041);assert q.u32(q.p+24)==3
    q.advance(2043);assert q.u32(q.p+20)==0
    # Original controller-status queue and worker dispatch. No USB-object
    # pointer is enqueued. The callback runs in the worker even without IOC.
    q=Ehci();assert q.start()==0;q.real_poll=True;m=q.m
    sent=[];received=[];freed=[];request=0x20018000
    # Remove only the fixture allocator hook by intercepting at the original
    # allocator's entry before q.stub sees it; a separate machine avoids hook
    # ordering ambiguity and executes the very same compiled callbacks.
    from arm_machine import Machine
    w=Machine(image)
    for a,n in [(0x6002b0e8,8),(DRIVER,68),(HC,0xa0),(REGS,0x100),
                (0x60480800,704),(0x4000b000,0xc00),(h['audio_state_start'],h['audio_state_bytes'])]:
        w.write(a,m.read(a,n))
    def worker_boundary(u,a,size,data):
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        if a==0x6000b330:
            assert r[1:3]==[0x3c,4];result=request
        elif a==0x6000b6c4:sent.append(r[1]);result=0
        elif a==0x6000b724:
            if received:
                u.reg_write(UC_ARM_REG_SP,0x2001ff80);u.reg_write(UC_ARM_REG_PC,RETURN|1);return
            received.append(r);w.write(r[1],P(request));result=0
        elif a==0x6000b388:freed.append(r[1]);result=0
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    w.uc.hook_add(UC_HOOK_CODE,worker_boundary)
    u32=lambda a:struct.unpack('<I',w.read(a,4))[0]
    w.write(u32(0x6000c500),P(1,0,1,2));w.write(u32(0x6000c508),H(2))
    assert w.call(0x6000c376,1,syms['ehci_poll_done'],0x1234)[0]==0
    assert sent==[request] and u32(request)==0x03000021
    assert w.read(request+0x24,8)==P(0x1234,syms['ehci_poll_done'])
    w.call(0x6000bdc8,stack=0x2001ff80)
    assert received and freed==[request] and u32(syms['ehci']+65*4)==0
    return {'status':'pass','original_periodic_dummy_allocations':11,'live_periodic_table':hex(table),
        'driver_context_table_is_not_live_table':True,'stream_packets':300,'outcomes':outcomes,
        'publish_running_after_ring_complete':True,'transport_only_no_converter':True,
        'transport_only_expiry_stops':True,'cached_converter_page':True,'original_busy_gate_failure':True,
        'host3_page_crossing_slots':crossed,
        'admission_negative_cases':negatives,'original_controller_status_queue_and_worker':True,
        'cases':['actual stock frame-list replacement and dummy iTD chain','guarded EHCI bind trampoline',
                 'split endpoint/hub/port/masks and DMA alignment','2048-frame and 256-slot wrap',
                 '44/45-frame stereo PCM and peak telemetry','completion state bit is not an error',
                 'past-frame reuse, frozen-frame retention and unlink grace','one pending worker poll',
                 'callback after device object release','foreign link quarantine',
                 'freed context on reset error; halt check','new periodic endpoint admission refusal',
                 'OHCI isolation','60-second and lost-worker watchdogs'],
        'boundary':'Original table construction/replacement and controller-status queue/worker execute. Heap, IRQ/task setup, DMA/MMIO/clock, stock EHCI completion/teardown and DSP are modeled; no wire or timing claim.'}
