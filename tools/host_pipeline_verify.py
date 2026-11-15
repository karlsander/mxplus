"""B10 request breadcrumbs. Original core instructions execute; no RTOS/DMA.

Exercise a real original submission rejection and completion, not merely a
stubbed wrapper return. API and HCD boundaries are separate controlled models.
"""
import struct
from unicorn.arm_const import *
from host_midi_core_verify import Core, P, REQ, EP


def verify(original,image,h):
    from host_midi_verify import Transport
    base=h['midi_pipeline_start'];symbols=h['symbols']
    def rows(m,token=5):
        v=struct.unpack('<21I',m.read(base+token*84,84))
        return [list(v[i:i+3]) for i in range(0,21,3)]

    # Non-extension callbacks execute the displaced prologue and original
    # body with identical observable outputs and no diagnostic records.
    a=Core(original);b=Core(image)
    for c in (a,b):
        assert c.submit(-1)==0
        c.complete(-9)
    assert a.sent==b.sent and a.done==b.done and a.freed==b.freed
    assert b.m.read(base,672)==bytes(672)

    class TracedCore(Core):
        def boundary(self,u,address,size,data):
            if address==0x01000876: # original wake flag; no task switch
                u.reg_write(UC_ARM_REG_R0,0)
                u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
            super().boundary(u,address,size,data)
    c=TracedCore(image);c.callback=symbols['mx1_host_done']
    assert c.submit(-1)==0
    v=rows(c.m);assert v[2][0]==v[3][0]==1 and v[2][2]==REQ and v[3][2]==0
    assert v[6][0]==0
    c.complete(-9);v=rows(c.m);assert v[6][0]==1 and v[6][2]==0xfffffff7
    assert c.reserve(5)==[1,2,3,4,5]
    assert c.submit(100)==0xffffffec
    v=rows(c.m);assert v[2][0]==v[3][0]==v[6][0]==2
    assert v[3][2]==v[6][2]==0xffffffec
    # Submission error callback runs before core return. The completed
    # request can be freed by the body: the wrapper must not reread it.
    saved=c.m.read(base,672)
    c.callback=symbols['mx1_host_done']
    c.m.write(REQ+0x20,P(8))
    assert c.m.call(0x6000f81a,REQ)[0]==0xffffffec
    assert c.m.read(base,672)==saved

    class TracedTransport(Transport):
        def __init__(self,*args):
            self.hcd=[]
            super().__init__(*args)
        def stub(self,u,address,size,data):
            if address==0x600111ee:
                regs=[u.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
                self.hcd.append(regs+list(struct.unpack('<5I',self.m.read(u.reg_read(UC_ARM_REG_SP),20))))
                u.reg_write(UC_ARM_REG_R0,0xfffffff3)
                u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
            super().stub(u,address,size,data)
    t=TracedTransport(image,h);assert t.attach(2,1)[0]==0
    t.enqueue(2,[0x7f409009]);t.poll(1)
    request=t.requests[-1];v=rows(t.m)
    assert v[0][0]==v[1][0]==1 and v[0][2]==4 and v[1][2]==0
    t.done(request);assert rows(t.m)[6][0]==1
    t.reject=-12;t.enqueue(2,[0x7f419009]);t.poll(1);v=rows(t.m)
    assert v[0][0]==v[1][0]==2 and v[1][2]==0xfffffff4
    args=[0x20012200,request['ep'],0x2000,123,456,0x20000800,64,0x6000f593,0x2001b000]
    t.m.write(0x2001ff80,P(*args[4:]))
    tags=[0x12340000+i for i in range(8)]
    regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
    for reg,tag in zip(regs,tags):t.m.uc.reg_write(reg,tag)
    assert t.m.call(symbols['mx1_ehci_request'],*args[:4],stack=0x2001ff80)[0]==0xfffffff3
    assert t.hcd==[args] and [t.m.uc.reg_read(r) for r in regs]==tags
    v=rows(t.m);assert v[4][0]==v[5][0]==1 and v[4][2]==request['ep'] and v[5][2]==0xfffffff3
    # A different endpoint must not contaminate our lifetime counters.
    saved=t.m.read(base,672);args[1]=EP
    assert t.m.call(symbols['mx1_ehci_request'],*args[:4],stack=0x2001ff80)[0]==0xfffffff3
    assert t.m.read(base,672)==saved
    return {'status':'pass','stages':7,'live_bytes':672,
            'checks':['original core success/error/completion and unrelated callback parity',
                      'invalid token ignored','API accepted/rejected counters',
                      'HCD register/stack arguments, return and callee-saved registers',
                      'unmatched endpoint ignored'],
            'boundary':'Original core and compiled wrappers execute; allocator, queues, wakes, API and HCD delivery modeled. No RTOS timing or DMA.'}
