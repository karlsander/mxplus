"""Execute the FM-1 extension and original OHCI helpers in ARM emulation.

USB DMA, RTOS delivery and DSP hardware are modeled, not timed or validated.
No USB device is opened by this verifier. See each hook's explicit boundary.
"""
import json
import struct
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from arm_machine import Machine, RETURN
from memory_map import recover
from container_tool import sha256
from host_midi_setup_verify import Setup, EVENT

ROOT=Path(__file__).resolve().parents[1]
P=lambda *v:struct.pack('<'+'I'*len(v),*v)
H=lambda v:struct.pack('<H',v)
DEV=0x20014000; EP=0x20015000; DRIVER=0x20013000
HC=0x60460000; REGS=0x40010000; HCCA=0x20011000; ANCHOR=0x20010800
STRIDE=5664; ED=96; TD=160; TDSTRIDE=224

class CombinedSetup(Setup):
    def __init__(self,*args,**kwargs):
        self.audio_requests=[];self.initialized=[];self.audio_control_error=0
        super().__init__(*args,**kwargs,enable_audio=True)
    def stub(self,u,a,size,data):
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        result=0
        if a==0x6000c276:
            stack=struct.unpack('<6I',self.m.read(u.reg_read(UC_ARM_REG_SP),24))
            self.audio_requests.append(r+list(stack))
        elif a==0x600079ee:self.initialized.append(r[:3])
        elif a==0x60009558 and r[1]==0x22 and self.audio_control_error:
            result=self.audio_control_error
        else:return super().stub(u,a,size,data)
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))

def verify_endpoint_constructor(image,c):
    # Build the actual stock endpoint record, including the direction bit in
    # ep[8]. A hand-built fixture formerly masked that bit and hid a rejection.
    m=Machine(image);interface=0x20012000;allocation=0x20017000;descriptor=0x20010000
    start=c.index(bytes.fromhex('090401010101020000'));d=c[start:]
    m.write(descriptor,d)
    def boundary(u,a,size,data):
        if a==0x6000b330:
            assert u.reg_read(UC_ARM_REG_R1)==0x5c
            result=allocation
        elif a in (0x60014ae4,0x010003b8):result=0 # critical-section entry/exit
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,boundary)
    m.call(0x6000e040,interface+0x18,interface,descriptor,len(d))
    record=m.read(allocation+0xc+8,10)
    assert record==bytes.fromhex('8480010004000100b800')
    return record

def verify_controller_indices(original):
    # Run original initialization/binding, modeling only IRQ priority setup.
    # USB speed alone does not select a driver: HOST3 reported index 1.
    m=Machine(original)
    def boundary(u,a,size,data):
        if a==0x010027e6:
            u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,boundary)
    assert m.call(0x60009f78)[0]==0
    rows=[]
    for i,a in enumerate(struct.unpack('<2I',m.read(0x6002b0e8,8))):
        values=struct.unpack('<17I',m.read(a,68))
        assert values[0]==i
        assert values[3]==(0x600132d7 if i==0 else 0x600111ef)
        rows.append({'index':i,'driver':'OHCI' if i==0 else 'EHCI','request':hex(values[3])})
    return {'drivers':rows,'boundary':'Original initialization and binding execute; IRQ priority helper modeled'}

def verify_setup(image,h,c,endpoint_record):
    t=CombinedSetup(image,h,c);t.bind_initial();t.setup()
    assert t.state()==5 and len(t.opens)==2 and not t.audio_requests
    assert [x[:4] for x in t.controls]==[[DEV,1,11,0],[DEV,0x22,1,0x100],[DEV,1,11,1]]
    # Run the real manager bind handler through the patched callback after
    # modeled RTOS delivery of the alternate-one rebind.
    active=t.nodes[2];t.m.write(EVENT,P(0,active,0))
    assert t.m.read(t.endpoints[active,128]+8,10)==endpoint_record
    t.checked(h['symbols']['mx1_audio_bind'],EVENT,0,0,0)
    assert t.initialized==[[2,1,44100]] and len(t.audio_requests)==1
    request=t.audio_requests[0]
    assert request[:7]==[DEV,t.endpoints[active,128],0,0,0,0,0]
    p=h['audio_ports']+2*STRIDE
    assert request[8:]==[p,0] and t.m.read(p+16,8)==P(1,1)
    # A duplicate rebind/setup must not create another transport or reset DSP.
    t.checked(h['symbols']['mx1_audio_bind'],EVENT,0,0,0);t.setup()
    assert len(t.audio_requests)==1 and len(t.initialized)==1
    # Successful transport completion is delivered as stock event5. The actual
    # status updater emits audio readiness alongside already working MIDI.
    t.m.write(p+24,P(2));t.m.write(EVENT,P(5,DEV,0))
    t.checked(h['symbols']['mx1_audio_ready'],EVENT,0,0,0)
    assert t.state()==7 and t.notices[-1]==[2,2]
    # Failure to set the endpoint frequency leaves MIDI operational.
    f=CombinedSetup(image,h,c);f.bind_initial();f.audio_control_error=-1;f.setup()
    assert f.state()==5 and len(f.opens)==2 and not f.audio_requests
    return {'requests':[[*x[:6], 'rate bytes' if x[1]==0x22 else x[6], x[7]] for x in t.controls],
            'midi_and_audio_state':t.state(),'dsp_initialize':t.initialized,
            'boundary':'wire controls, DSP initialization and RTOS queue submission modeled; original alternate switching and manager binding execute'}

class Audio:
    def __init__(self,image,h,elf):
        self.m=Machine(image); self.h=h; self.s=h['symbols']; self.p=h['audio_ports']
        self.events=[];self.dsp=[];self.normal=[];self.stock=[]
        self.real_done=False;self.real_dsp=False;self.real_tick=False
        self.callbacks=elf
        m=self.m
        m.write(DEV+0x10,H(0x1209)+H(1)); m.write(DEV+0x4a,H(0)+H(3))
        m.write(EP+8,bytes([0x84,128,1,0,4]));m.write(EP+0xe,H(1)+H(184))
        m.write(0x6002b0e8,P(DRIVER));m.write(DRIVER+0x40,P(HC))
        m.write(HC+8,P(REGS,HCCA));m.write(REGS+4,P(0x80));m.write(REGS+0x34,P(0x2edf2edf))
        m.write(HC+0x28,P(HC+0x28,HC+0x28,HC+0x28,ANCHOR+12))
        for i in range(63):m.write(HC+i*20+0x3a,bytes([255 if not i else (i-1)//2]))
        m.uc.hook_add(UC_HOOK_CODE,self.stub)
    def u32(self,a):return struct.unpack('<I',self.m.read(a,4))[0]
    def stub(self,u,a,size,data):
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        result=0
        if a==0x60007e10:self.events.append(self.m.read(r[0],12))
        elif a==0x010088dc:
            if self.real_dsp:return
            b=struct.unpack('<12I',self.m.read(r[1],48)); n=b[5]//4
            self.dsp.append((r[0],b,struct.unpack('<'+'i'*n,self.m.read(b[3],n*4))))
        elif a==(self.callbacks['host_audio_tick_original']&~1):
            if self.real_tick:return
        elif a==(self.callbacks['host_ohci_done_original']&~1):
            if self.real_done:return
            t=r[0]; chain=[]
            while t:chain.append(t);t=self.u32(t+8)
            self.normal.append(chain)
        elif a in (0x600132d6,0x600136ac,0x60013962,0x600127b6):
            self.stock.append((a,r));result=0
        elif a==0x6000c31e:pass
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    def call(self,name,*args):
        # All exports use AAPCS, including stack arguments. Check callee-saved
        # registers in addition to Machine's stack/return assertions.
        regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
              UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
        for i,r in enumerate(regs):self.m.uc.reg_write(r,0x12340000+i)
        if len(args)>4:self.m.write(0x2001ff80,P(*args[4:]))
        result=self.m.call(self.s[name],*args[:4],count=300000,stack=0x2001ff80)[0]
        assert [self.m.uc.reg_read(r) for r in regs]==list(range(0x12340000,0x12340008)),name
        return result
    def start(self,port=0,frame=100):
        p=self.p+port*STRIDE
        dev=DEV+port*0x100;ep=EP+port*0x100
        if port:
            self.m.write(dev,self.m.read(DEV,0x80));self.m.write(ep,self.m.read(EP,0x20))
        self.m.write(p,P(dev,ep,0,0,1,1,0,0))
        self.m.write(REGS+0x3c,P(frame))
        result=self.call('mx1_ohci_request',dev,ep,0,0,0,0,0,self.callbacks['start_done'],p)
        return p,result
    def done(self,p,i,frames=44,cc=9,packet=None):
        t=p+TD+i*TDSTRIDE
        control=self.u32(t)&0xffff
        self.m.write(t,P(control));self.m.write(t+8,P(0));self.m.write(t+16,H((cc<<12)|(frames*4)))
        if packet is None:packet=[(-32768 if i%2 else 32767),-1234]*frames
        self.m.write(t+32,struct.pack('<'+'h'*len(packet),*packet))
        self.m.write(p+ED+8,P(p+TD+((i+1)%17)*TDSTRIDE))
        self.m.write(REGS+0x3c,P(control))
        self.call('mx1_ohci_done',t)

def verify_converter_boundary(image,h,syms):
    """Execute the original initializer, task and converter input routines.

    Model only DSP reset/command/result, integer-to-float MMIO and RTOS notify.
    This checks the packet ABI and memory extents, not DSP interpolation.
    """
    q=Audio(image,h,syms);m=q.m;p,_=q.start()
    m.uc.mem_map(0x40140000,0x1000) # modeled DSP scratch, not ordinary RAM
    context=0x20005ee0;smooth=0x010157f8;scratch=0x40140c00
    m.write(context,P(0,0,0,0,0,0x20016000))
    m.write(0x6002b094,P(1,0,scratch))
    integer_writes=[];commands=[];notifications=[]
    def boundary(u,a,size,data):
        result=0
        if a==0x60007b2a:pass # DSP reset only; original init math executes.
        elif a==0x01008a82:
            commands.append([u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)])
        elif a==0x01008a90:result=0x41c00000 # modeled 24 output frames
        elif a==0x010020cc:notifications.append(u.reg_read(UC_ARM_REG_R0))
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    def mmio(u,access,a,size,value,data):
        if a==0x40040548:
            signed=value if value<0x80000000 else value-0x100000000
            integer_writes.append(signed)
            # Distinct finite values expose channel/order errors without
            # claiming the physical converter's scale or timing.
            m.write(a+12,struct.pack('<f',float(signed)))
    m.uc.hook_add(UC_HOOK_CODE,boundary)
    m.uc.hook_add(UC_HOOK_MEM_WRITE,mmio)
    m.call(0x600079ee,0,1,44100,count=300000)
    assert q.u32(smooth)==1 and q.u32(smooth+0x60)==100
    assert q.u32(context+8)==struct.unpack('<I',struct.pack('<f',44100/96000))[0]
    # Keep the first short run inside the initialized drift-estimation epoch;
    # actual counter MMIO and adaptive DSP response remain outside this test.
    m.write(context+0x28,P(1000))
    q.real_dsp=True;q.real_tick=True
    # The original EHCI audio task must stay inactive for this OHCI stream.
    assert m.read(0x4000bbb0,2)==b'\0\0'
    expected=[]
    for ms in range(11):
        frames=45 if ms==10 else 44
        packet=[32767,-32768]*frames
        q.done(p,ms,frames,packet=packet)
        for phase in range(4):q.call('mx1_audio_tick',phase*2)
        expected.extend([32767*512,-32768*512]*frames)
    # First four calls supply silence while priming; one packet stays queued.
    assert integer_writes==[0]*88+expected[:-90]
    assert len(commands)==44 and len(notifications)==44*4
    assert q.u32(p+92)==0 and q.u32(context+0x28)==956
    assert q.u32(smooth+0x60)==(100+44+440)%256
    # Neither the original input converter nor its silent OUT buffer writes
    # beyond the custom port. Guard the following port with nonzero bytes.
    guard=b'\xa5'*STRIDE;m.write(p+STRIDE,guard)
    # Disable its claim/wanted words so the extension never consumes the guard.
    m.write(p+STRIDE+16,P(0,0));guard=m.read(p+STRIDE,STRIDE)
    for phase in range(4):q.call('mx1_audio_tick',phase*2)
    assert m.read(p+STRIDE,STRIDE)==guard
    return {'original_initializer':True,'original_audio_task':True,
            'original_converter_input':True,'calls':48,
            'boundary':'DSP reset/command/result, integer conversion MMIO and RTOS notify modeled; drift epoch seeded; no interpolation or timing claim'}

def verify_worker_and_tree(image,h,syms):
    """Replace the former hand-built tree/direct request call at this boundary.

    Original dummy ED construction, HCCA permutation, request allocation/packing
    and worker dispatch execute. Heap allocation and RTOS queue operations are
    modeled; walking HCCA in Python is not a model of actual USB DMA/timing.
    """
    q=Audio(image,h,syms);m=q.m;allocations=[];request=0x20018000
    sent=[];received=[];freed=[]
    def boundary(u,a,size,data):
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        if a==0x6000b330:
            assert r[1]==0x3c
            result=0x60470000+len(allocations)*64 if len(allocations)<31 else request
            allocations.append(result)
        elif a==0x6000b6c4:sent.append(r[1]);result=0
        elif a==0x6000b724:
            if received:
                # Stop the infinite task when it waits for its next request.
                u.reg_write(UC_ARM_REG_SP,0x2001ff80);u.reg_write(UC_ARM_REG_PC,RETURN|1);return
            received.append(r);m.write(r[1],P(request));result=0
        elif a==0x6000b388:freed.append(r[1]);result=0
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,boundary)
    assert m.call(0x60012274,HC)[0]==0 and len(allocations)==31
    q.call('mx1_ohci_bind',0,DRIVER);m.write(DRIVER+0x40,P(HC))
    m.write(q.u32(0x6000c500),P(1,0,1,2))
    m.write(q.p,P(DEV,EP,0,0,1,1,0,0))
    m.write(REGS+0x3c,P(100))
    m.write(0x2001ff80,P(0,0,0,syms['start_done'],q.p,0))
    assert m.call(0x6000c276,DEV,EP,0,0,stack=0x2001ff80)[0]==0
    assert sent==[request]
    m.call(0x6000bdc8,stack=0x2001ff80)
    assert len(received)==1 and freed==[request] and len(q.events)==1
    assert q.u32(q.p+24)==2
    for slot in range(32):
        ptr=q.u32(HCCA+slot*4);chain=[]
        while ptr:
            assert ptr not in chain
            chain.append(ptr);ptr=q.u32(ptr+12)
        assert len(chain)==6 and chain[-1]==q.p+ED
    return {'hcca_slots_reaching_audio_ed':32,'original_dummy_ed_allocations':31,
            'original_queue_and_worker':True,
            'boundary':'heap allocation and RTOS queue delivery modeled; actual controller traversal and USB transactions untested'}

def verify_monitor(image,h,syms,c):
    t=CombinedSetup(image,h,c);t.bind_initial();t.setup()
    port=t.port;p=h['audio_ports']+port*STRIDE
    ep=t.endpoints[t.nodes[-1],0];out=0x2001c000
    def monitor(words=()):
        t.m.write(out,P(*words)+b'\xa5'*(64-4*len(words)))
        n=t.checked(syms['mx1_audio_monitor'],port,ep,out,len(words))
        assert n<=16 and t.m.read(out+n*4,64-n*4)==b'\xa5'*(64-n*4)
        return list(struct.unpack('<'+'I'*n,t.m.read(out,n*4)))
    def payload(words):
        assert [w&15 for w in words]==[4,4,4,4,7]
        return b''.join(w.to_bytes(4,'little')[1:] for w in words)
    first=payload(monitor());assert first[:6]==bytes.fromhex('f07d4d030000')
    assert not monitor() # no repeated reports merely for MIDI clock/polling
    clock=0xf80f;note=0x643c9009
    assert monitor([clock])==[clock]
    refreshed=monitor([note]);assert refreshed[0]==note and payload(refreshed[1:])==first
    # No diagnostic insertion while user SysEx spans transfers, including an
    # intervening realtime packet. Deferred report follows the user's F7.
    t.m.write(p+24,P(2))
    begin=0x017df004;body=0x04030204;end=0x00f70506
    assert monitor([begin,body])==[begin,body]
    assert monitor([clock])==[clock]
    assert not monitor()
    ended=monitor([end]);assert ended[0]==end and payload(ended[1:])[6]==2
    # Preserve a full musical transfer; the pending note-triggered report is
    # delivered later, never by dropping notes or exceeding the 64-byte buffer.
    assert monitor([note]*16)==[note]*16
    assert len(monitor())==5 and not monitor()
    # Never send the old device's report to a replacement endpoint.
    t.m.write(ep+0x20,P(0x2001b000));t.m.write(0x2001b008,P(DEV+0x100))
    assert monitor([note])==[note]
    # The real lower-driver rejection callback retains the specific reason.
    q=Audio(image,h,syms);q.m.write(REGS+4,P(0))
    pp,rc=q.start();assert rc==0xfffffffb
    diag=syms['diagnostics']
    assert q.u32(diag+4)==0x49 and q.u32(diag+8)==5
    # Exercise the real TX poll integration as well as the formatter above.
    live=CombinedSetup(image,h,c);live.bind_initial();live.setup();live.drain()
    live.enqueue(live.port,[note]);live.poll(1)
    wire=bytes.fromhex(live.requests[-1]['data'])
    assert len(wire)==24 and wire[:4]==P(note)
    assert payload(struct.unpack('<5I',wire[4:]))==first
    return {'format':'F0 7D 4D stage controller error phase control flags cc packets malformed frame_lo frame_hi F7',
            'initial_waiting_rebind_payload':first.hex(),
            'cases':['state change and note-on trigger','no poll/clock flood','user SysEx continuity',
                     'full musical transfer retained','replacement device isolation','specific controller-start rejection'],
            'boundary':'USB MIDI submission modeled; FM-1 display/protocol acceptance still requires hardware'}


def verify_debug_bridge(image,h,syms,c):
    # Actual compiled ARM protocol, RX/TX wrappers and audio mode selection.
    # USB delivery/RTOS scheduling/DSP hardware are the explicit boundaries.
    def frame(op,values=(),seq=12,target=1):
        b=bytearray([0xf0,0x7d,0x44,0x42,1,target,seq,op])
        for v in values:b.extend((v>>(j*7))&127 for j in range(5))
        b.extend([(-sum(b[1:]))&127,0xf7]);return bytes(b)
    def packets(b):
        return [(4+len(b[i:i+3]) if i+3>=len(b) else 4) |
                sum(v<<(8+8*j) for j,v in enumerate(b[i:i+3])) for i in range(0,len(b),3)]
    def decode(words):
        b=b''.join(w.to_bytes(4,'little')[1:1+(3 if w&15==4 else (w&15)-4)] for w in words)
        assert b[:6]==bytes.fromhex('f07d44420101') and b[-1]==0xf7 and not sum(b[1:-1])&127
        assert (len(b)-10)%5==0
        return b[6],b[7],[sum(b[i+j]<<(7*j) for j in range(5)) for i in range(8,len(b)-2,5)]
    t=CombinedSetup(image,h,c);t.bind_initial();t.setup();port=t.port
    ep=t.endpoints[t.nodes[-1],128];tx=t.endpoints[t.nodes[-1],0];out=0x2001c000
    def receive(b):
        for w in packets(b): assert t.checked(syms['mx1_debug_receive'],port,ep,w)==1
    def transmit():
        words=[]
        for _ in range(10):
            t.m.write(out,b'\xa5'*64)
            n=t.checked(syms['mx1_debug_transmit'],port,tx,out)
            assert n<=16 and t.m.read(out+n*4,64-n*4)==b'\xa5'*(64-n*4)
            if not n:return words
            words.extend(struct.unpack('<'+'I'*n,t.m.read(out,n*4)))
        raise AssertionError('unbounded reply')
    wakes=len(t.wakes);receive(frame(1));assert t.wakes[wakes:]==[[2,1]]
    seq,op,v=decode(transmit());assert (seq,op,v[:4])==(12,65,[0,0xb3,port,3])
    receive(frame(2,[0]));assert decode(transmit())[2]==[2] # no controller snapshot yet
    receive(frame(3,[2]));assert decode(transmit())[2]==[2] # no converter without owned transport
    receive(frame(99));assert decode(transmit())[2]==[1]
    bad=bytearray(frame(1));bad[-2]^=1;receive(bad);assert not transmit()
    receive(frame(1,target=0));assert not transmit()
    # Retry after an incomplete or oversized private frame resynchronizes on
    # its F0. Oversized payload is consumed through F7, never stock MIDI data.
    assert t.checked(syms['mx1_debug_receive'],port,ep,packets(frame(1))[0])==1
    receive(frame(1));assert decode(transmit())[1]==65
    for w in [packets(frame(1))[0]]+[0x01010104]*20+[0xf705]:
        assert t.checked(syms['mx1_debug_receive'],port,ep,w)==1
    assert not transmit()
    receive(frame(1));assert decode(transmit())[1]==65
    # A new command never overwrites a response waiting to be transmitted.
    receive(frame(1,seq=21));receive(frame(1,seq=22));assert decode(transmit())[0]==21
    receive(frame(1));assert decode(transmit())[2][-4]==1
    # Keep the stock user SysEx intact before starting a debug response.
    t.m.write(out,P(0x017df004));t.checked(syms['mx1_audio_monitor'],port,tx,out,1)
    receive(frame(1));assert not transmit()
    t.m.write(out,P(0xf705));t.checked(syms['mx1_audio_monitor'],port,tx,out,1)
    assert decode(transmit())[1]==65
    # Musical messages still flow, and a different device cannot read this state.
    assert t.checked(syms['mx1_debug_receive'],port,ep,0x643c9009)==0
    saved=t.m.read(ep+0x20,4);t.m.write(ep+0x20,P(0x2001b000));t.m.write(0x2001b008,P(DEV+0x100))
    assert t.checked(syms['mx1_debug_receive'],port,ep,packets(frame(1))[0])==0
    t.m.write(ep+0x20,saved)
    # Entire RX callback/poll path consumes the private command before stock MIDI.
    live=CombinedSetup(image,h,c);live.bind_initial();live.setup();live.drain();live.poll(0)
    rx=[r for r in live.requests if not r['token']&1][-1]
    live.done(rx,P(*packets(frame(1))));live.poll(0);assert not live.received
    live.enqueue(live.port,[0x643c9009]);wire=[]
    for _ in range(8):
        start=len(live.requests);live.poll(1)
        sends=[r for r in live.requests[start:] if r['token']&1]
        for r in sends: wire.extend(struct.unpack('<'+'I'*(r['size']//4),bytes.fromhex(r['data'])));live.done(r)
    # All response packets precede the queued note; no channel status splits SysEx.
    note=wire.index(0x643c9009);assert decode(wire[:note])[1]==65
    # Active endpoint: fresh snapshots only in the worker, read pages from RAM.
    q=Audio(image,h,syms);p,rc=q.start();assert rc==0
    q.m.write(syms['debug_ports'],P(DEV));q.m.write(EP+0x20,P(0x20018000));q.m.write(0x20018008,P(DEV))
    def request(op,values=()):
        for w in packets(frame(op,values)):assert q.call('mx1_debug_receive',0,EP,w)==1
        words=[]
        for _ in range(10):
            n=q.call('mx1_debug_transmit',0,EP,out)
            if not n:break
            words.extend(struct.unpack('<'+'I'*n,q.m.read(out,n*4)))
        return decode(words)[2] if words else None
    raw=request(2,[0]);assert raw[:3]==[0,0,2] and raw[3:6]==[HC,p+ED,p+TD]
    assert raw[6+1]==0x8c # raw HcControl, not compressed monitor bits
    assert len(request(2,[1]))==37 and len(request(2,[2]))==35
    queued=[]
    def queue(u,a,size,data):
        if a!=0x6000c276:return
        regs=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        queued.append(regs+list(struct.unpack('<6I',q.m.read(u.reg_read(UC_ARM_REG_SP),24))))
        u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    q.m.uc.hook_add(UC_HOOK_CODE,queue)
    assert request(4) is None and len(queued)==1
    q.m.write(REGS+0x3c,P(777));assert q.call('mx1_ohci_request',*queued[-1][:9])==0
    n=q.call('mx1_debug_transmit',0,EP,out)
    assert decode(struct.unpack('<'+'I'*n,q.m.read(out,n*4)))[2]==[0,4]
    assert request(2,[0])[6+10]==777
    # Three modes: stock consumption, mute, locally generated converter input.
    assert request(3,[2])==[0,2]
    for i in range(40):q.call('mx1_audio_tick',i%4*2)
    assert sum(b[1][5]//8 for b in q.dsp)==441 and any(any(x for x in b[2]) for b in q.dsp)
    assert max(abs(x) for b in q.dsp for x in b[2])<=2048*65536
    assert request(3,[1])==[0,1];q.call('mx1_audio_tick',0);assert not any(q.dsp[-1][2])
    assert request(3,[3])==[1]
    q.m.write(syms['debug_ticks'],P(240100));q.call('mx1_audio_tick',0)
    assert request(1)[26]==0 # watchdog restores normal mode
    # The measured HOST3 connection uses controller 1 (EHCI). Do not hand the
    # OHCI-only callback to that driver, initialize DSP or select AS alt1 at boot.
    t=CombinedSetup(image,h,c);t.m.write(DEV+0x4a,H(1)+H(3))
    parent=0x2001a000;t.m.write(0x20018004,P(parent))
    t.m.write(parent+0x4a,H(1)+H(2));t.m.write(parent+0x58,H(0x400))
    t.m.write(parent+0x10,H(0x1234)+H(0x5678))
    t.bind_initial();t.setup();ep=t.endpoints[t.nodes[-1],128];tx=t.endpoints[t.nodes[-1],0]
    assert t.state()==5 and not t.audio_requests and not t.initialized
    assert [x[1:5] for x in t.controls]==[[1,11,0,2]]
    receive(frame(1));v=decode(transmit())[2];assert v[1:7]==[0xb3,port,0x48,5,1,0]
    receive(frame(2,[3]));topology=decode(transmit())[2]
    assert topology==[0,3,1,3,0,0,0x20018000,parent,1,2,0x400,0x1234,0x5678,1]
    t.drain();t.poll(0)
    receive(frame(2,[4]));midi=decode(transmit())[2]
    assert len(midi)==26 and midi[2:5]==[ep,1,0] and midi[8:10]==[1,0]
    # Private controls are accepted in RX but only run on manager delivery.
    for step in (1,2,3,4):
        before=len(t.controls);receive(frame(5,[step]));assert decode(transmit())[2]==[0,step]
        assert len(t.controls)==before
        queued=t.events[-1];assert queued==P(5,DEV,0x3242444d)
        receive(frame(5,[step]));assert decode(transmit())[2]==[2]
        t.m.write(EVENT,queued);t.checked(syms['mx1_audio_ready'],EVENT)
        receive(frame(1));v=decode(transmit())[2];assert v[-3:]==[0,step,0],v
        if step==2:
            # Stock probe callback posts event0 to the manager. It does NOT
            # execute the bind handler on the USB core task. Check the real
            # callback before modeled delivery; do not claim self-deadlock.
            t.checked(0x6000837c,t.nodes[2],0,0,0)
            assert t.events[-1][0]==0 and t.events[-1][4:8]==P(t.nodes[2])
            t.m.write(EVENT,t.events[-1]);t.checked(syms['mx1_audio_bind'],EVENT)
        assert not t.audio_requests and not t.initialized
    assert [x[1:6] for x in t.controls[1:]]==[[0x22,1,0x100,0x84,3],[1,11,1,1,0],[1,11,0,1,0]]
    # A control failure is visible in status, while MIDI/other readouts remain.
    t.audio_control_error=-7;receive(frame(5,[1]));transmit()
    t.m.write(EVENT,t.events[-1]);t.checked(syms['mx1_audio_ready'],EVENT)
    receive(frame(1));v=decode(transmit())[2];assert v[-3:]==[0,1,0xfffffff9]
    assert t.state()==5
    # Idle TX is flag-driven. The audio-task cadence must wake it without
    # a command, claimed audio endpoint, clock routing or queued music.
    def tick_boundary(u,a,size,data):
        if a==(syms['host_audio_tick_original']&~1):
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    t.m.uc.hook_add(UC_HOOK_CODE,tick_boundary)
    wakes=len(t.wakes)
    t.m.write(syms['debug_ticks'],P(4094));t.checked(syms['mx1_audio_tick'],0)
    assert len(t.wakes)==wakes
    t.checked(syms['mx1_audio_tick'],2);assert t.wakes[wakes:]==[[2,1]]
    n=t.checked(syms['mx1_debug_transmit'],port,tx,out)
    assert n==15
    heartbeat=decode(struct.unpack('<15I',t.m.read(out,60)))
    assert heartbeat[:2]==(0,0x7e) and heartbeat[2][:4]==[0,0xb3,0x39,1]
    assert not t.checked(syms['mx1_debug_transmit'],port,tx,out)
    # User SysEx defers a due heartbeat, then the end marker releases it.
    t.m.write(out,P(0x017df004));t.checked(syms['mx1_audio_monitor'],port,tx,out,1)
    t.m.write(syms['debug_ticks'],P(8191));t.checked(syms['mx1_audio_tick'],0)
    assert not t.checked(syms['mx1_debug_transmit'],port,tx,out)
    t.m.write(out,P(0xf705));t.checked(syms['mx1_audio_monitor'],port,tx,out,1)
    assert t.checked(syms['mx1_debug_transmit'],port,tx,out)==15
    return {'status':'pass','cases':['structured replies across multiple transfers','malformed checksum/target rejection',
        'pending reply retention','user SysEx continuity','replacement device isolation','actual RX and TX poll integration',
        'worker-owned register snapshots and bounded pages','normal/mute/test-tone converter modes','mode timeout',
        'EHCI baseline avoids OHCI request and DSP submission','cached topology and MIDI software status',
        'manager-only single-step controls/lookup and failure results','original bind callback queues manager event',
        'reply publication wakes original TX task flag','idle audio cadence wakes TX without claimed audio','one-transfer telemetry defers behind user SysEx'],
        'boundary':'USB delivery, RTOS queue dispatch and DSP hardware modeled; actual compiled ARM code executes'}

def verify(image,report,elf_path):
    h=report['host_midi']
    with elf_path.open('rb') as f:
        elf=ELFFile(f);tab=elf.get_section_by_name('.symtab')
        syms={s.name:s['st_value'] for s in tab.iter_symbols()}
        assert tab.get_symbol_by_name('mx1_audio_ports')[0]['st_size']==4*STRIDE
        assert syms['mx1_audio_ports']==0x607f4000
        assert syms['diagnostics']==syms['mx1_audio_ports']+4*STRIDE
    operations=recover(image)['operations']
    original=(ROOT/'analysis/container_app_usb.bin').read_bytes()
    controllers=verify_controller_indices(original)
    hot=image[h['insert_offset']:h['insert_offset']+h['code_bytes']]
    audio=image[h['audio_source']-0x60000000:]
    expected=bytearray(original[:h['insert_offset']]+hot+original[h['insert_offset']:]+audio)
    for change in h['patches']:
        off=change['file_offset'];before=bytes.fromhex(change['original']);after=bytes.fromhex(change['replacement'])
        assert expected[off:off+len(before)]==before,change
        expected[off:off+len(before)]=after
    assert expected==image, 'USB changes outside guarded patches and extensions'
    assert operations[1]['destination']==h['audio_state_start'] and operations[1]['length']==h['audio_state_bytes']
    assert operations[4]['destination']==h['audio_code_start'] and operations[4]['length']==h['audio_code_bytes']
    assert operations[5]['destination']==0x01020000 and operations[5]['length']==0x8000
    assert struct.unpack_from('<II',image,0x3750)==(0x607f0000,0x604b1178)
    heap=Machine(image);heaps=[]
    def heap_call(u,a,size,data):
        if a==0x0100093c:
            heaps.append(struct.unpack('<3I',heap.read(u.reg_read(UC_ARM_REG_R0),12)))
            u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    heap.uc.hook_add(UC_HOOK_CODE,heap_call);heap.call(0x600036dc)
    assert heaps[0][1:]==(0x607f0000-0x604b1178,0x604b1178)
    t=Audio(image,h,syms);c=bytes.fromhex((ROOT/'evidence/fm1-host-midi-20261103/configuration.hex').read_text())
    endpoint_record=verify_endpoint_constructor(image,c)
    setup=verify_setup(image,h,c,endpoint_record)
    t.m.write(0x20010001,c);assert t.call('mx1_audio_profile',0x20010001)==1
    malformed=0
    for length in range(9,len(c)):
        b=bytearray(c[:length]);b[2:4]=H(length);t.m.write(0x20010001,b)
        # A complete AS can precede missing MIDI: main config validation owns
        # the complete interface set. Profile alone still rejects split AS.
        if length<100:assert not t.call('mx1_audio_profile',0x20010001)
        malformed+=1
    for offset in (70,72,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93):
        b=bytearray(c);b[offset]^=0x10;t.m.write(0x20010001,b)
        assert not t.call('mx1_audio_profile',0x20010001),offset
        malformed+=1
    # Execute relocated OHCI initialization prologue and original body.
    t.call('mx1_ohci_bind',0,DRIVER)
    assert t.u32(DRIVER+12)==h['symbols']['mx1_ohci_request']
    assert t.u32(DRIVER+16)==h['symbols']['mx1_ohci_cancel']
    t.m.write(DRIVER+0x40,P(HC))
    p,result=t.start(frame=65530);assert result==0
    assert t.u32(p+24)==2 and len(t.events)==1
    assert t.u32(ANCHOR+12)==p+ED
    assert t.u32(HC+0x28)==p+ED+24 and t.u32(HC+0x2c)==p+ED+24
    assert t.u32(p+ED)&0xffff==3|(4<<7)|0x9000
    assert t.u32(p+ED+4)==p+TD+16*TDSTRIDE
    assert t.u32(p+ED+8)==p+TD
    for i in range(16):
        td=p+TD+i*TDSTRIDE;ptr=td+32
        assert td%32==0 and t.u32(td)==0xe0000000|((65533+i)&65535)
        assert t.u32(td+4)==ptr&~4095 and t.u32(td+12)==ptr+183
        assert struct.unpack('<H',t.m.read(td+16,2))[0]==0xe000|(ptr&4095)
    # Full-speed short packets, 44/45-frame alternation, integer sign and
    # interleaving; the original DSP MMIO call is an explicit capture stub.
    t.done(p,0,44);t.done(p,1,45)
    for i in range(8):t.call('mx1_audio_tick',(i*2)&7)
    assert [x[1][5]//8 for x in t.dsp]==[11]*7+[12]
    flat=[v for _,_,samples in t.dsp for v in samples]
    assert flat==[32767*65536,-1234*65536]*44+[-32768*65536,-1234*65536]*45
    assert t.u32(p+56)==2 and t.u32(p+72)==2
    # Bad completion cannot publish samples; a later DMA slot is still armed.
    t.done(p,2,44,cc=1);assert t.u32(p+76)==1 and t.u32(p+52)==2
    # Mixed hardware done list: newest standard -> ISO -> older standard.
    normal1=0x20017000;normal2=0x20017100;td=p+TD+3*TDSTRIDE
    t.m.write(normal1+8,P(td));t.m.write(td+8,P(normal2));t.m.write(normal2+8,P(0))
    t.m.write(td,P(0));t.m.write(td+16,H(0x9000|176))
    t.call('mx1_ohci_done',normal1|1)
    assert t.normal==[[normal1,normal2]] and t.u32(p+72)==3
    # Stop removes both hardware/software links without freeing/reusing DMA.
    t.m.write(REGS+0x3c,P(4));assert not t.call('mx1_ohci_cancel',DEV,EP)
    assert t.u32(p+24)==3 and t.u32(p+20)==1
    assert t.u32(ANCHOR+12)==0 and t.u32(HC+0x28)==HC+0x28
    assert t.u32(HC+0x2c)==HC+0x28
    t.m.write(REGS+0x3c,P(5));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==1
    t.m.write(REGS+0x3c,P(6));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==0 and t.u32(p+24)==0
    assert t.start(frame=20)[1]==0
    # A halted periodic visit or a pending writeback must retain DMA ownership.
    t.call('mx1_ohci_cancel',DEV,EP);t.m.write(REGS+0x3c,P(23))
    t.m.write(HCCA+0x84,P(p+TD));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==1
    t.m.write(HCCA+0x84,P(0));t.m.write(REGS+0x30,P(p+TD));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==1
    t.m.write(REGS+0x30,P(0));t.m.write(REGS+0x1c,P(p+ED));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==1
    t.m.write(REGS+0x1c,P(0));t.call('mx1_ohci_event',0,4);assert t.u32(p+20)==0
    # Three static EDs coexist in the original periodic root. Removing the
    # middle entry must update both software links and the hardware chain.
    multi=Audio(image,h,syms);ports=[]
    for port in range(3):
        pp,result=multi.start(port);assert result==0;ports.append(pp)
    first,middle,last=ports
    assert multi.u32(first+ED+12)==middle+ED and multi.u32(middle+ED+12)==last+ED
    multi.call('mx1_ohci_cancel',DEV+0x100,EP+0x100)
    assert multi.u32(first+ED+12)==last+ED
    assert multi.u32(first+ED+24)==last+ED+24 and multi.u32(last+ED+28)==first+ED+24
    # Manager close only publishes stop; completion performs the actual
    # unlink. Successful controller destroy releases all static ownership.
    rec=0x20017000;multi.m.write(rec+8,P(DEV));multi.m.write(rec+2,H(0))
    multi.call('mx1_audio_close',rec)
    assert multi.u32(first+16)==0 and multi.u32(first+24)==2
    multi.done(first,0);assert multi.u32(first+24)==3
    multi.call('mx1_ohci_reset',0,2)
    for pp in ports:assert multi.u32(pp+12)==multi.u32(pp+20)==multi.u32(pp+24)==0
    assert multi.u32(ANCHOR+12)==0 and multi.u32(HC+0x28)==HC+0x28
    # Execute the displaced prologue and REAL original general done handler.
    # General TDs deliberately carry the original dummy marker (no request);
    # no allocator or callbacks are stubbed in this path.
    t.real_done=True
    t.m.write(normal1+8,P(p+TD));t.m.write(p+TD+8,P(normal2));t.m.write(normal2+8,P(0))
    t.m.write(normal1+16,b'\x0f\0');t.m.write(normal2+16,b'\x0f\0')
    assert not t.call('mx1_ohci_done',normal1)
    assert t.u32(normal2+8)==normal1 and t.u32(normal1+8)==0
    # Actual consumed packet counts track an independent source clock rather
    # than a fixed 44.1-kHz consumer assumption. This does not model the DSP's
    # interpolation or prove audible drift correction.
    pacing=[]
    for rate in (44080,44100,44118):
        q=Audio(image,h,syms);p,_=q.start();total=0
        for ms in range(200):
            frames=((ms+1)*rate)//1000-(ms*rate)//1000
            q.done(p,ms%17,frames)
            for phase in range(4):q.call('mx1_audio_tick',phase*2)
        consumed=sum(x[1][5]//8 for x in q.dsp)
        assert consumed==44+(199*rate)//1000,(rate,consumed)
        assert q.u32(p+80)==q.u32(p+84)==0
        assert q.u32(p+52)-q.u32(p+56)==1
        pacing.append({'source_frames_per_second':rate,'consumed_frames_in_200ms':consumed,'queued_packets':1})
    converter=verify_converter_boundary(image,h,syms)
    worker=verify_worker_and_tree(image,h,syms)
    monitor=verify_monitor(image,h,syms,c)
    debug=verify_debug_bridge(image,h,syms,c)
    return {'status':'pass','patched_app_sha256':sha256(image),'hardware_access':False,
            'limits':'instruction checks only; USB/DSP/RTOS boundaries modeled','setup':setup,'pacing':pacing,
            'converter_boundary':converter,'controller_indices':controllers,
            'worker_and_tree':worker,'fm1_monitor':monitor,'debug_bridge':debug,
            'stock_endpoint_record_hex':endpoint_record.hex(),
            'profile_negative_cases':malformed,'heap_reservation_bytes':65536,
            'iso_descriptors_per_port':17,'audio_state_bytes':h['audio_state_bytes'],
            'cases':['guarded complete USB patch accounting','startup placement','original heap creation',
                     'original endpoint constructor preserves direction bit',
                     'OHCI binding ABI','periodic insertion and bandwidth',
                     'ITD alignment/page boundaries/frame wrap','short PCM16 packets',
                     'stereo sign and scaling','250-us packet distribution',
                     'errored packet rejection','mixed general/ISO done list',
                     'unlink/quiescence/reopen','DMA retirement barriers',
                     'multiple periodic EDs and middle unlink','manager stop intent and controller teardown',
                     'original general-TD handler ABI','source-clock packet pacing']}

if __name__=='__main__':
    report=json.loads((ROOT/'build/mainline/build-report.json').read_text())
    result=verify((ROOT/'build/mainline/app_usb.mainline.bin').read_bytes(),report,ROOT/'build/mainline/usb-host.elf')
    output=ROOT/'build/mainline/host-audio-verification.json';output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
