"""Original EHCI bulk construction/completion; DMA and allocation are modeled."""
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from arm_machine import Machine

P=lambda *v:struct.pack('<'+'I'*len(v),*(x&0xffffffff for x in v))
H=lambda v:struct.pack('<H',v)

def completion(image, flags, actual, speed=0, token_error=0):
    m=Machine(image)
    dev=0x20014000;ep=0x20015000;driver=0x20016000;hc=0x20017000
    toggles=0x20018000;hub=0x20019000;parent=0x2001a000
    anchor=0x60478000;regs=0x40010000;heap=[0x60470000];alloc=[]
    def boundary(u,a,size,data):
        if a==0x6000b330:
            n=u.reg_read(UC_ARM_REG_R1);align=u.reg_read(UC_ARM_REG_R2)
            result=(heap[0]+align-1)&-align;heap[0]=result+n
            m.write(result,bytes(n));alloc.append((result,n))
        elif a in (0x60014ae4,0x010003b8):result=0
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,boundary)
    m.write(0x6002b0ec,P(driver));m.write(driver+0x40,P(hc))
    m.write(hc+4,P(regs));m.write(hc+0x2c,P(anchor));m.write(hc+0x80,P(toggles))
    m.write(anchor,P(anchor|2));m.write(anchor+0x30,P(anchor,anchor))
    m.write(dev+0x4a,H(1)+H(3));m.write(dev+0x58,H(speed));m.write(dev+0xec,P(hub))
    m.write(hub+4,P(parent,dev));m.write(parent+0x4c,H(2));m.write(parent+0x58,H(0x400))
    m.write(ep+8,bytes([0x81,128,2,0]));m.write(ep+0x10,H(64 if not speed else 512))
    m.write(0x2001ff80,P(0,0x20000000,64,0x6000f593,0x2001b000))
    assert m.call(0x600111ee,dev,ep,flags,0,stack=0x2001ff80)[0]==0
    wrapper=alloc[0][0]
    u32=lambda a:struct.unpack('<I',m.read(a,4))[0]
    private=u32(wrapper+0x44);qh=u32(private);td=u32(u32(private+4))
    assert m.read(wrapper+0x16,2)==bytes([int(bool(flags&0x2000)),flags&1])
    assert u32(private+8)==1 and u32(td+0x20)==64
    assert u32(qh+0x10)==td and u32(td+8)&0x8180==0x8180
    assert u32(regs)&0x20 # actual constructor enabled the modeled async schedule
    assert m.call(0x60011a4e,hc,wrapper)[0]==0xfffffff6 # active = pending
    # Model controller writeback only: clear Active, update remaining bytes,
    # data toggle and optional error. Original completion interprets it.
    m.write(td+8,P(((64-actual)<<16)|0x80008d00|token_error))
    result=m.call(0x60011a4e,hc,wrapper)[0]
    return result,u32(wrapper+0x2c)

def verify(original,patched,h):
    from host_midi_verify import Transport
    rows=[]
    for speed in (0,0x400):
        for n in (0,4,16,60,64):
            before=completion(original,0,n,speed)
            after=completion(original,0x2000,n,speed)
            assert before==((0 if n==64 else 0xfffffff1),n)
            assert after==(0,n)
            rows.append(dict(speed=speed,bytes=n,before=before[0],after=after[0]))
    # Feed the real HCD result to compiled MIDI poll/callback, including a ZLP
    # then single events. It must deliver each message and keep RX armed.
    t=Transport(patched,h);assert t.attach(0,0)[0]==0;t.poll(0)
    for payload in (b'',P(0x643c9009),P(0x003c8008),P(0x643d9009)*15):
        req=t.requests[-1];assert req['flags']==0x2000 and req['timeout']==0xffffffff
        status,n=completion(original,req['flags'],len(payload))
        t.done(req,payload,status=status,length=n);before=len(t.requests);t.poll(0)
        assert len(t.requests)==before+1
    assert t.received==[0x643c9009,0x003c8008]+[0x643d9009]*15
    # The short-packet option does not mask stalls or malformed MIDI lengths.
    for payload,error in ((P(0x643c9009),0x40),(b'\x09\x90',0)):
        t=Transport(patched,h);t.attach(0,0);t.poll(0);req=t.requests[-1]
        status,n=completion(original,req['flags'],len(payload),token_error=error)
        t.done(req,payload,status=status,length=n);t.poll(0)
        assert not t.received and len(t.requests)==1
    return dict(cases=rows,boundary='Original EHCI wrapper, QH/qTD construction, schedule linking, toggle handling and completion run unchanged. Heap/critical sections and controller DMA/status are modeled; this does not validate USB timing or delivery.')
