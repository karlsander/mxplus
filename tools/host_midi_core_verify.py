"""Original USB core/alarm failure path; scheduling and HCD delivery modeled."""
import struct
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import *
from arm_machine import Machine

P=lambda *v:struct.pack('<'+'I'*len(v),*(x&0xffffffff for x in v))
DEV=0x20014000;EP=0x20015000;INTERFACE=0x20016000
REQ=0x20017000;COMPLETION=0x20019000;CALLBACK=0x0fff0100

class Core:
    def __init__(self,image):
        self.m=Machine(image);self.heap=0x60470000
        self.queued=[];self.sent=[];self.done=[];self.freed=[];self.scheduled=[]
        self.preempt=False
        self.m.uc.hook_add(UC_HOOK_CODE,self.boundary)
        m=self.m
        # Execute original five-object alarm pool/list initialization.
        m.call(0x01001262)
        assert self.free()==5
        m.write(0x6002b0dc,P(1));m.write(0x6002b0cc,P(9));m.write(0x6002b0d4,P(7))
        m.write(INTERFACE+8,P(DEV));m.write(EP+8,bytes([1,0,2,0]))
        m.write(EP+0x20,P(INTERFACE))
    def u32(self,a):return struct.unpack('<I',self.m.read(a,4))[0]
    def free(self):return struct.unpack('<H',self.m.read(0x0101573e,2))[0]
    def boundary(self,u,a,size,data):
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        result=0;m=self.m
        if a in (0x0100999c,0x010028d6,0x010045b2,0x010045c0):pass
        elif a==0x010045c6:result=1 # task context; do not switch emulated tasks
        elif a==0x01002138:self.scheduled.append(r[:2]) # no hardware timer wheel
        elif a==0x6000b330:
            result=(self.heap+r[2]-1)&-r[2];self.heap=result+r[1]
            m.write(result,bytes(r[1]))
        elif a==0x6000b388:self.freed.append(r[1]) # not an allocator corruption test
        elif a==0x6000b6c4:self.queued.append(r[1]) # preserve observed FIFO order
        elif a==0x6000c276:
            stack=struct.unpack('<6I',m.read(u.reg_read(UC_ARM_REG_SP),24))
            self.sent.append(r+list(stack)) # lower HCD/worker/USB not executed here
        elif a==CALLBACK:
            self.done.append([r[0],r[1],*struct.unpack('<2i',m.read(r[2],8)),r[3]])
            if self.preempt:
                # Model the woken higher-priority TX task queuing its next
                # request before this callback returns. This ordering is a
                # fixture, not a measured live RTOS trace.
                self.queued.append('next TX')
        elif a==0x6000a904:result=1 # endpoint-list lookup only
        elif a==0x6000ac44:result=EP
        else:return
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    def reserve(self,n):
        return [self.m.call(0x60013fc0,9,0x20018000+i*32)[0] for i in range(n)]
    def submit(self,timeout):
        self.m.write(REQ,bytes(0x30))
        self.m.write(REQ,P(0x02000007))
        self.m.write(REQ+12,P(INTERFACE,EP,0x20000800,60,CALLBACK|1,5,timeout))
        return self.m.call(0x6000f81a,REQ)[0]
    def complete(self,status=0):
        self.m.write(COMPLETION,P(0x02000008,0,status,DEV,EP,60))
        self.m.call(0x6000f60a,COMPLETION,0,0,0)

def verify(original):
    t=Core(original);handles=t.reserve(5)
    assert handles==[1,2,3,4,5] and t.free()==0
    assert t.reserve(1)==[0xffffffec] # original alarm wrapper maps -34 to -20
    assert t.submit(100)==0xffffffec and not t.sent
    assert t.done==[[INTERFACE,EP,-20,0,5]]
    # The no-alarm option is stock behavior, not a masked callback error.
    assert t.submit(-1)==0 and len(t.sent)==1 and t.u32(EP+0x18)==0
    assert t.sent[0][:7]==[DEV,EP,0,0,0,0x20000800,60]
    assert t.u32(EP+0x14)==REQ and t.free()==0
    t.complete();assert t.done[-1]==[INTERFACE,EP,0,60,5]
    assert t.u32(EP+0x14)==0 and t.free()==0
    # Untimed requests retain ordinary error completion semantics.
    for status in (-7,-9):
        assert t.submit(-1)==0
        t.complete(status);assert t.done[-1]==[INTERFACE,EP,status,60,5]
        assert not t.u32(EP+0x14)
    # Four occupied slots plus one timed write. The callback precedes timer
    # stop/queued deletion. Model immediate TX wake, then process next submit
    # ahead of that deletion: the original core produces the observed -20.
    q=Core(original);assert q.reserve(4)==[1,2,3,4]
    assert q.submit(100)==0 and q.free()==0
    timer=q.u32(EP+0x18);assert timer==5
    q.preempt=True;q.complete();q.preempt=False
    assert len(q.queued)==2 and q.queued[0]=='next TX'
    cleanup=q.queued[1]
    assert q.u32(cleanup)==0x02000017 and q.u32(cleanup+20)==timer
    assert q.free()==0 and q.u32(EP+0x18)==0
    assert q.submit(100)==0xffffffec and len(q.sent)==1
    assert q.done[-1]==[INTERFACE,EP,-20,0,5]
    # Execute the original deletion routine, as the core's cleanup event
    # does. The full USB core event loop and priority scheduler are modeled.
    assert q.m.call(0x6001402a,timer)[0]==0 and q.free()==1
    assert q.submit(100)==0 and len(q.sent)==2
    return {
        'alarm_slots':5,'exhausted_timed_result':-20,'exhausted_untimed_result':0,
        'retained_completion_errors':[-7,-9],
        'modeled_preemption_order':['next TX','timer cleanup'],
        'next_timed_before_cleanup':-20,'next_timed_after_cleanup':0,
        'boundary':'Original USB core submission/completion, alarm initialization/create/start/stop/delete and wrapper instructions execute. Heap/free, endpoint list lookup, critical sections, timer wheel, mailbox delivery, HCD and task preemption are modeled. Five slots and the failure path are established; actual live slot occupancy, scheduling order, USB delivery and timing are not.'}
