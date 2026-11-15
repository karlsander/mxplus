"""Original EHCI initialization/worker plus compiled split-ISO extension.

Heap, IRQ/task setup, DMA/MMIO, RTOS delivery and DSP are explicit models.
This does not execute a USB transaction or establish real-time scheduling.
"""
import struct
from unicorn.arm_const import *
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from arm_machine import RETURN

P=lambda *v:struct.pack('<'+'I'*len(v),*v)
H=lambda v:struct.pack('<H',v)

def verify(image,h,syms):
    from host_audio_verify import Audio,DEV,EP,DRIVER,HC,REGS,TD,TDSTRIDE,STRIDE
    table=0x4000b000;cap=0x40020000;initial_table=0x60470000
    for name in ('ehci_path','ehci_arm','ehci_unlink'):
        f=h['ehci_sram_helpers'][name]
        assert f['runtime_address']==syms[name]
        assert h['code_start']<=syms[name]&~1<(syms[name]&~1)+f['bytes']<=h['code_start']+h['code_bytes']

    class Ehci(Audio):
        def __init__(self,port=0):
            self.alloc=[];self.polls=[];self.real_poll=False;self.reset_halt=True;self.poll_result=0
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
                self.polls.append(r[:3]);result=self.poll_result
            else:return super().stub(u,a,size,data)
            u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        def start(self,frame=2040,poll_only=0):
            self.m.write(self.p,P(DEV,EP,0,0,1,1,0,0,1))
            self.m.write(REGS+12,P(frame*8))
            return self.call('mx1_ehci_request',DEV,EP,poll_only,0,0,0,0,syms['start_done'],self.p)
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
    def page(number,port=0):
        b=bytearray([0xf0,0x7d,0x44,0x42,1,1,13,2,number,0,0,0,0])
        b.extend([(-sum(b[1:]))&127,0xf7])
        m.write(EP+0x20,P(0x20019000));m.write(0x20019008,P(DEV))
        for i in range(0,len(b),3):
            part=b[i:i+3];word=(4+len(part) if i+3>=len(b) else 4)|sum(x<<(8+j*8) for j,x in enumerate(part))
            assert q.call('mx1_debug_receive',port,EP,word)==1
        wire=bytearray();out=0x2001c000
        for _ in range(10):
            n=q.call('mx1_debug_transmit',port,EP,out)
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
    # B9 explicit probe 9: no ISO IOC, existing worker queue is the primary
    # source of service. Execute ticks/poll callbacks with no event callback;
    # DMA completions and elapsed frame values remain modeled, not timing.
    q=Ehci(port=2);m=q.m;p=q.p
    writes=[]
    m.uc.hook_add(UC_HOOK_MEM_WRITE,lambda u,access,a,n,v,data:writes.append((a,n,v)),
                  begin=REGS,end=REGS+0xff)
    assert q.start(frame=0,poll_only=1)==0
    assert q.u32(syms['async_diagnostic']+532)==1
    db=syms['debug_ports']+2*780
    m.write(db+276,P(3,10000))
    for i in range(16):assert q.u32(p+TD+i*TDSTRIDE+12)==0x00b80080
    for f in range(1,129):
        m.write(REGS+12,P(f*8))
        for i in range(16):
            if q.state(3+i)==f:
                q.complete(i)
                # Hardware retains the originally clear IOC bit.
                t=p+TD+i*TDSTRIDE
                m.write(t+12,P(q.u32(t+12)&0x7fffffff))
        for quarter in range(4):
            q.call('mx1_audio_tick',quarter*2)
            if q.state(65):q.poll_done()
    assert len(q.polls)==32 and q.u32(syms['async_diagnostic']+8)==0
    assert q.u32(syms['async_diagnostic']+12)==32 and not q.dsp
    assert q.u32(p+72)>=120 and q.u32(p+76)==q.u32(p+80)==0
    assert not writes # no controller-register mutation
    assert all(not q.u32(p+TD+i*TDSTRIDE+12)&0x80000000 for i in range(16))
    m.write(p+16,P(0));m.write(REGS+12,P(129*8))
    m.write(syms['debug_ticks'],P(527));q.call('mx1_audio_tick',0);q.poll_done()
    assert q.u32(p+24)==3 and q.u32(p+20)==1
    m.write(REGS+12,P(131*8));m.write(syms['debug_ticks'],P(543))
    q.call('mx1_audio_tick',0);q.poll_done()
    assert q.u32(p+24)==q.u32(p+20)==0 and m.read(table,1024)==q.baseline
    # A subsequent ordinary start restores IOC/fallback policy. The flag
    # belongs to one start, not to a stale manager command or sticky global.
    assert q.start(frame=140)==0 and q.u32(syms['async_diagnostic']+532)==0
    assert m.read(syms['service_timing'],48)==bytes(48)
    assert q.u32(p+TD+12)==0x80b80080
    rejected=Ehci();assert rejected.start(poll_only=2)==0xfffffffb
    # B11: model an audio-task preemption during a long worker service.
    # A second machine executes the compiled audio tick against a copied
    # state at that instruction boundary, without replacing the running
    # worker's registers/stack. This is a scheduling model, not live timing.
    preemptions=[]
    for policy,interval in [(1,16),(0,32)]:
        q=Ehci();m=q.m;assert q.start(frame=0,poll_only=policy)==0
        m.write(syms['debug_ports']+276,P(3,10000))
        for _ in range(interval):q.call('mx1_audio_tick',0)
        assert len(q.polls)==1 and q.state(65)==1
        def during_service(u,a,size,data):
            if a!=(syms['ehci_service']&~1):return
            assert q.state(65)==1 # latch covers service, not just queue wait
            tick=q.u32(syms['debug_ticks'])+64
            m.write(syms['debug_ticks'],P(tick))
            probe=Audio(image,h,syms)
            probe.m.write(h['audio_state_start'],m.read(h['audio_state_start'],h['audio_state_bytes']))
            probe.m.write(syms['debug_ticks'],P(tick-1)) # tick lands on the old modulo deadline
            attempts=[]
            def queue_probe(v,pc,n,ctx):
                if pc==0x6000c376:
                    attempts.append(pc);v.reg_write(UC_ARM_REG_R0,0)
                    v.reg_write(UC_ARM_REG_PC,v.reg_read(UC_ARM_REG_LR))
            probe.m.uc.hook_add(UC_HOOK_CODE,queue_probe)
            probe.call('mx1_audio_tick',0)
            assert not attempts
            preemptions.append({'policy':policy,'modeled_service_ticks':64,'requeued':len(attempts)})
            # Negative control: releasing the latch at the same eligible tick
            # admits a successor, reproducing the preceding callback policy.
            probe.m.write(syms['ehci']+65*4,P(0))
            probe.m.write(syms['debug_ticks'],P(tick-1))
            probe.call('mx1_audio_tick',0);assert len(attempts)==1
            preemptions[-1]['released_latch_requeues']=len(attempts)
        hook=m.uc.hook_add(UC_HOOK_CODE,during_service)
        q.poll_done();m.uc.hook_del(hook)
        finished=q.u32(syms['debug_ticks'])
        assert q.state(65)==0 and q.u32(syms['poll_after'])==finished+interval
        for _ in range(interval-1):q.call('mx1_audio_tick',0)
        assert len(q.polls)==1
        q.call('mx1_audio_tick',0);assert len(q.polls)==2 and q.state(65)==1
    # Rejected enqueue also waits a complete interval; wraparound stays bounded.
    q=Ehci();m=q.m;m.write(syms['debug_ticks'],P(0xfffffff0))
    assert q.start(frame=0,poll_only=1)==0
    m.write(syms['debug_ports']+276,P(3,10000));q.poll_result=0xfffffff4
    for _ in range(15):q.call('mx1_audio_tick',0)
    assert not q.polls
    q.call('mx1_audio_tick',0);assert len(q.polls)==1 and q.state(65)==0
    assert q.u32(syms['poll_after'])==16
    for _ in range(15):q.call('mx1_audio_tick',0)
    assert len(q.polls)==1
    q.call('mx1_audio_tick',0);assert len(q.polls)==2
    # B12 elapsed worker time: model FRINDEX wrap while the worker runs.
    # Tick progression includes preemption; this fixture supplies both clocks.
    q=Ehci();m=q.m;assert q.start(frame=2047,poll_only=1)==0
    timing=syms['service_timing'];clock=[5,10]
    def elapsed_model(u,a,size,data):
        if a==(syms['ehci_snapshot']&~1):
            m.write(REGS+12,P(clock[0]));m.write(syms['debug_ticks'],P(clock[1]))
    hook=m.uc.hook_add(UC_HOOK_CODE,elapsed_model)
    q.call('mx1_ehci_event',1,1)
    assert list(struct.unpack('<12I',m.read(timing,48)))==[2,1,13,13,13,10,10,0,0,16376,5,0]
    clock[:]=[21,8202];q.call('mx1_ehci_event',1,1)
    assert list(struct.unpack('<12I',m.read(timing,48)))==[4,2,13,13,16,8192,8192,0,0,5,21,1]
    m.uc.hook_del(hook)
    row=page(19);assert row==[0,19]+list(struct.unpack('<12I',m.read(timing,48)))
    m.write(syms['debug_ports']+780,P(DEV));assert page(19,port=1)==[2]
    m.uc.mem_unmap(REGS,0x1000)
    assert page(19)==row # cached state only; no MMIO from MIDI
    m.write(timing,P(5));assert page(19)==[2]
    # The original converter's busy-gate return is a real instruction path,
    # not a mocked failure. Capture it, keep the DMA alive until worker stop.
    q=Ehci(port=2);assert q.start()==0;q.real_dsp=True
    ctx=0x20005ee0+2*0xa4;gate=0x40101200;sd=syms['dsp_diagnostics']+2*144
    q.m.write(ctx+20,P(gate));q.m.write(gate,P(7))
    # B7 waits for real input priming before entering that original gate.
    for i in range(8):q.call('mx1_audio_tick',i*2)
    assert q.u32(sd+4)==0 and q.u32(q.p+92)==0
    q.complete(0);q.complete(1);q.advance(2047)
    q.call('mx1_audio_tick',0)
    assert q.u32(sd+4)==1 and q.u32(sd+8)==0 and q.u32(sd+12)==0xffffffff
    assert q.u32(sd+16)==7 and q.u32(sd+24+11*4)==gate
    assert q.u32(q.p+92)==1 and q.u32(q.p+16)==0 and q.u32(q.p+24)==2
    q.advance(0);assert q.u32(q.p+24)==3
    q.advance(2);assert q.u32(q.p+20)==0
    # B8 captures original bulk wrappers and QH/qTDs in worker context. Run
    # original request construction and original indexed-list traversal;
    # allocation, controller DMA and IRQ delivery remain explicit models.
    class AsyncEhci(Ehci):
        def __init__(self):
            self.real_midi=False;self.heap=0x60470000;self.qheap=0x60481800
            self.midi_alloc=[]
            super().__init__()
        def stub(self,u,a,size,data):
            if self.real_midi and a==0x600111ee:return
            if self.real_midi and a==0x6000b330:
                n=u.reg_read(UC_ARM_REG_R1);align=u.reg_read(UC_ARM_REG_R2)
                if n==56 and align==64:
                    result=self.qheap;self.qheap+=64
                else:
                    result=(self.heap+align-1)&-align;self.heap=result+n
                self.m.write(result,bytes(n));self.midi_alloc.append((result,n))
                u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
            return super().stub(u,a,size,data)
    q=AsyncEhci();assert q.start()==0;m=q.m;q.real_midi=True
    m.write(HC+0x80,P(0x60478000)) # original toggle cache
    wrappers=[]
    for i,direction in enumerate((128,0)):
        ep=EP+0x400+i*0x100
        m.write(ep+8,bytes([1|direction,direction,2,0]));m.write(ep+0x10,H(64))
        m.write(0x2001ff80,P(0,0x20000000+i*64,64,0x6000f593,0x2001b000))
        before=len(q.midi_alloc)
        assert m.call(0x600111ee,DEV,ep,0x2000,0,stack=0x2001ff80)[0]==0
        wrappers.append(q.midi_alloc[before][0])
    assert q.u32(HC+0x8c)==2
    ad=syms['async_diagnostic'];first=ad+20;last=first+256
    def capture(tick):
        m.write(syms['debug_ticks'],P(tick));m.write(syms['ehci']+55*4,P(tick))
        q.advance(2041)
    pipeline=h['midi_pipeline_start']
    m.write(pipeline,P(*range(42))) # port zero RX/TX stage triples
    capture(4000)
    assert q.u32(first)==2 and q.u32(first+4)==4000
    assert q.u32(first+24)==0 and q.u32(first+28)==2
    original_first=m.read(first,256)
    for i,w in enumerate(wrappers):
        v=struct.unpack('<26I',m.read(last+48+i*104,104))
        private=q.u32(w+0x44);qh=q.u32(private);td=q.u32(q.u32(private+4))
        assert v[:6]==(w,EP+0x400+i*0x100,qh,td,64,0)
        assert v[6:18]==struct.unpack('<12I',m.read(qh,48))
        assert v[18:21]==struct.unpack('<3I',m.read(td,12))
        assert v[20]&128 and v[21]==1 and v[24]==td and v[25]==v[20]
        # Model DMA completion without calling the original event consumer.
        m.write(td+8,P(0x80008d00))
    m.write(pipeline,P(*range(100,142)))
    capture(4128)
    assert m.read(first,256)==original_first
    assert q.u32(last+48+20*4)==0x80008d00
    assert q.u32(last+48+104+20*4)==0x80008d00
    # Cached page reads neither touch live MMIO nor follow retained pointers.
    # The page() closure below uses q/m variables from this verifier.
    m.write(DEV+0x10,H(0x1209)+H(1));m.write(EP+0x20,P(0x20015100))
    m.write(0x20015108,P(DEV));m.write(syms['debug_ports'],P(DEV))
    for number in (11,12,13,14):
        row=page(number);assert len(row)==40 and row[:2]==[0,number]
        assert row[2:14]==list(struct.unpack('<12I',m.read(first if number<13 else last,48)))
        assert row[14]==wrappers[(number-11)&1]
    for number in (15,16,17,18):
        row=page(number);assert len(row)==26 and row[:2]==[0,number]
        cached=first if number<17 else last
        assert row[2:5]==list(struct.unpack('<3I',m.read(cached,12)))
        start=(0 if number<17 else 100)+21*((number-15)&1)
        assert row[5:]==list(range(start,start+21))
    m.write(syms['debug_ports']+780,P(DEV))
    assert page(11,port=1)==[2] # same identity on another port cannot read owner
    assert page(15,port=1)==[2]
    live_heap=m.read(0x60470000,0x1000)
    m.uc.mem_unmap(0x40010000,0x1000);m.uc.mem_unmap(0x60470000,0x1000)
    assert page(11)[2]==2 and page(14)[2]==q.u32(last)
    assert page(15)[5:]==list(range(21)) and page(18)[5:]==list(range(121,142))
    m.write(last,P(q.u32(last)|1));assert page(13)==[2]
    assert page(17)==[2]
    # Corrupt/bounded-list fixtures must not follow arbitrary addresses.
    m.uc.mem_map(0x40010000,0x1000);m.uc.mem_map(0x60470000,0x1000)
    m.write(0x60470000,live_heap)
    m.write(REGS,P(0x10039,0x4000,0x33,2041*8,0,table))
    m.write(last,P(0));m.write(HC+0x8c,P(17));capture(4256)
    assert q.u32(last+24)==1
    m.write(HC+0x8c,P(2));m.write(wrappers[0]+0x44,P(0xdead0000));capture(4384)
    assert q.u32(last+24)==4 # bad private pointer is never followed
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
        'async_original_bulk_construction_and_cached_pages':True,
        'poll_only_without_iso_ioc_or_controller_writes':True,
        'poll_callback_preemption_model':preemptions,'poll_completion_relative_gap_and_wrap':True,
        'sram_helpers_and_cached_service_timing':True,
        'admission_negative_cases':negatives,'original_controller_status_queue_and_worker':True,
        'cases':['actual stock frame-list replacement and dummy iTD chain','guarded EHCI bind trampoline',
                 'split endpoint/hub/port/masks and DMA alignment','2048-frame and 256-slot wrap',
                 '44/45-frame stereo PCM and peak telemetry','completion state bit is not an error',
                 'past-frame reuse, frozen-frame retention and unlink grace','one pending worker poll',
                 'callback after device object release','foreign link quarantine',
                 'freed context on reset error; halt check','new periodic endpoint admission refusal',
                 'OHCI isolation','60-second and lost-worker watchdogs'],
        'boundary':'Original table construction/replacement and controller-status queue/worker execute. Heap, IRQ/task setup, DMA/MMIO/clock, stock EHCI completion/teardown and DSP are modeled; no wire or timing claim.'}
