"""Instruction-level bind/setup regression; USB control completion is modeled.

Original manager record construction, interface callbacks, setup, SET_INTERFACE
completion, MIDI-open dispatcher, request packing and task open handlers run.
Descriptor/list lookup, RTOS delivery, endpoint lookup and USB I/O are modeled.
"""
import struct
from pathlib import Path
from unicorn.arm_const import *
from unicorn import UC_HOOK_CODE
from arm_machine import Machine
from host_midi_verify import Transport, configuration, P, H, BUF, DEVICE

EVENT=0x20013000
PARENT=0x20018000
CONFIG_NODE=0x20018100
DRIVER=0x20018200
DETACH=0x0fff0200
NOTIFY=0x0fff0300
CONTROL_RETURN=0x0fff0400

class Setup(Transport):
    def __init__(self,image,report,cfg,port=2,vid=0x1209,enable_audio=False):
        self.enable_audio=enable_audio
        self.events=[];self.opens=[];self.controls=[];self.binds=[];self.notices=[]
        self.control_error=0;self.queue_error=False;self.endpoint_error=False
        self.nodes=[];self.endpoints={};self.iteration=0;self.port=port
        super().__init__(image,report)
        m=self.m
        self.record=0x604518e4+port*0x200
        m.write(BUF,cfg)
        m.write(DEVICE+8,bytes.fromhex('1201000200000040')+H(vid)+H(1)+H(0x390)+bytes(4))
        m.write(DEVICE+0x58,H(0x400 if vid==0x582 else 0))
        m.write(DEVICE+0x24,P(1));m.write(DEVICE+0xec,P(PARENT))
        m.write(PARENT+4+([2,3,0,1].index(port)+1)*4,P(DEVICE))
        m.write(0x4000b400,P(self.s['mx1_host_select']))
        m.write(0x4000b404,P(NOTIFY|1))
        # Locate stock flag handles via the original literal; model created tasks.
        flags=struct.unpack('<I',m.read(0x600091c4,4))[0]
        m.write(flags+8,H(1)+H(2))
        m.write(DRIVER+12,P(DETACH|1))
        node=0;at=9
        while at<len(cfg):
            d=cfg[at:at+cfg[at]];at+=len(d)
            if d[1]==4:
                node=0x20015000+len(self.nodes)*0x100;self.nodes.append(node)
                m.write(node+8,P(DEVICE)+P(DRIVER))
                m.write(node+0x13,bytes([d[2],d[3],int(d[3]==0)]))
            elif d[1]==5:
                ep=0x20019000+len(self.endpoints)*0x100
                m.write(ep+8,bytes([d[2],d[2]&128,d[3]&3,d[3]&0x30]))
                m.write(ep+0xc,bytes([d[3]&0xc]))
                m.write(ep+0xe,H(d[6]));m.write(ep+0x10,d[4:6]);m.write(ep+0x20,P(node))
                self.endpoints[node,d[2]&128]=ep
    def stub(self,u,a,size,data):
        m=self.m
        # This historical regression isolates MIDI setup; the combined audio
        # setup, controls and rebind are executed in host_audio_verify.py.
        if not self.enable_audio and a==(self.s.get('mx1_audio_setup',0)&~1):
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR));return
        addresses=(0x60009d2c,0x60009f58,0x60007e10,0x60009558,
                   0x6000eb3e,0x6000a904,0x6000ac30,0x6000acb8,
                   0x6000ee16,DETACH,NOTIFY,CONTROL_RETURN,0x60008e5a,0x60008e92,0x600096c6)
        if a not in addresses:return super().stub(u,a,size,data)
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        result=0
        if a==0x60009d2c:result=BUF
        elif a==0x60007e10:self.events.append(m.read(r[0],12));result=1
        elif a==NOTIFY:self.notices.append(r[:2])
        elif a==0x60009558:
            stack=struct.unpack('<4I',m.read(u.reg_read(UC_ARM_REG_SP),16))
            self.controls.append(r+list(stack))
            if self.control_error:result=self.control_error
            elif r[1]==1 and r[2]==11:
                # Model successful wire request, then run the REAL completion
                # in this call frame. Stock completion ignores the alternate
                # helper's result and returns wire status to the waiting task.
                self.control_return=u.reg_read(UC_ARM_REG_LR)
                u.reg_write(UC_ARM_REG_LR,CONTROL_RETURN|1)
                u.reg_write(UC_ARM_REG_R1,stack[0]);u.reg_write(UC_ARM_REG_R2,r[3])
                u.reg_write(UC_ARM_REG_PC,0x6000ef39);return
        elif a==CONTROL_RETURN:
            u.reg_write(UC_ARM_REG_LR,self.control_return)
        elif a==0x6000eb3e:result=CONFIG_NODE
        elif a==0x6000a904:result=len(self.nodes)
        elif a==0x6000ac30:self.iteration=0;result=self.nodes[0]
        elif a==0x6000acb8:
            self.iteration+=1
            result=self.nodes[self.iteration] if self.iteration<len(self.nodes) else 0
        elif a in (0x6000ee16,DETACH):
            self.binds.append([a,r[0]])
            result=DRIVER if a==0x6000ee16 else 0
        elif a in (0x60008e5a,0x60008e92):
            if not self.queue_error:self.opens.append((int(a==0x60008e92),m.read(r[0],12)))
            result=int(not self.queue_error)
        elif a==0x600096c6:
            assert r[1]==0 and r[3] in (1,2,3)
            target=struct.unpack('<3I',m.read(u.reg_read(UC_ARM_REG_SP),12))[2]
            ep=self.endpoints.get((r[0],r[2]),0)
            m.write(target,P(0 if self.endpoint_error else ep))
            result=0xffffffff if self.endpoint_error else 0
        u.reg_write(UC_ARM_REG_R0,result);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    def bind_initial(self):
        for node in self.nodes:
            if self.m.read(node+0x14,1)!=b'\0':continue
            self.m.write(EVENT,bytes(4)+P(node)+bytes(4))
            self.checked(0x60008426,EVENT,0,0,0)
        assert [e[0] for e in self.events]==[2,4],self.events
        assert self.m.read(self.record+0xe,1)==b'\xff'
    def setup(self,original=False):
        self.m.write(EVENT,bytes([4])+bytes(3)+P(DEVICE)+bytes(4))
        callback=0x6000865d if original else struct.unpack('<I',self.m.read(0x60028288,4))[0]
        self.checked(callback,EVENT,0,0,0)
    def drain(self):
        for tx,event in self.opens:
            self.m.write(EVENT,event)
            assert event[0] in (0,1)
            address=((0x010091bc if tx else 0x0100906c) if event[0] else
                     (0x01009154 if tx else 0x0100900a))
            self.checked(address,EVENT,0,0,0)
        self.opens.clear()
    def state(self):return struct.unpack('<H',self.m.read(self.record,2))[0]


def verify_setup(patched,report,main):
    h=report['host_midi']
    fixture=Path(__file__).resolve().parents[1]/'evidence/fm1-host-midi-20261103'
    fm1=bytes.fromhex((fixture/'configuration.hex').read_text())
    # Before/after differ ONLY in the setup callback for this reproducer.
    before=Setup(patched,h,fm1);before.bind_initial();before.setup(original=True)
    assert before.controls==[[DEVICE,1,11,0,2,0,0,0]]
    assert before.state()==1 and not before.opens and not before.binds
    before.poll(1);assert not before.requests
    cases=[]
    for port in range(4):
        t=Setup(patched,h,fm1,port);t.bind_initial();t.setup()
        assert t.controls==before.controls and not t.binds
        assert t.state()==5 and [tx for tx,_ in t.opens]==[0,1]
        assert t.notices==[[port,0],[port,4]],t.notices
        # A repeated setup or late interface bind must not open twice.
        opens=list(t.opens);t.setup();assert t.opens==opens
        midi=t.nodes[-1];t.m.write(EVENT,bytes(4)+P(midi)+bytes(4))
        t.checked(0x60008426,EVENT,0,0,0);assert [e[0] for e in t.events]==[2,4]
        t.drain();t.enqueue(port,[0xfa0f,0xf80f,0xfc0f]);t.poll(1)
        assert t.requests[-1]['data']=='0ffa00000ff800000ffc0000'
        t.poll(0);rx=t.requests[-1];assert rx['token']==port*2
        t.done(rx,P(0xf80f)+P(0xfa0f)+P(0x643c9009));t.poll(0)
        assert t.received==[0x643c9009|(port<<5)]
        cases.append({'port':port,'state':t.state(),'notifications':t.notices,
                      'tx':t.requests[0]['data']})
    # Genuine MIDI-only interface0, absent AC/AS; original classifier executes.
    directions=[]
    for direction in ('both','in','out'):
        c=configuration(direction=direction);c=bytearray(c[:9]+c[27:])
        c[2:4]=H(len(c));c[4]=1;c[11]=0
        t=Setup(patched,h,c);t.bind_initial()
        assert t.m.read(t.record+0x71,3)==b'\xff\xff\0'
        assert t.m.read(t.record+0x24,1)==b'\x03'
        t.setup();assert t.state()==5
        assert [tx for tx,_ in t.opens]==({'both':[0,1],'in':[0],'out':[1]}[direction])
        t.drain();t.poll(0);t.enqueue(t.port,[0xf80f]);t.poll(1)
        assert len(t.requests)==(2 if direction=='both' else 1)
        directions.append(direction)
    # No opens after control failure, queue rejection or inactive interface.
    t=Setup(patched,h,fm1);t.bind_initial();t.control_error=-1;t.setup()
    assert t.state()==1 and t.m.read(t.record+4,4)==P(0x13) and not t.opens
    t=Setup(patched,h,fm1);t.bind_initial();t.queue_error=True;t.setup()
    assert t.state()==1 and not t.opens and t.notices[-1]==[0xffffffff,100]
    t=Setup(patched,h,fm1);t.bind_initial();t.m.write(t.nodes[-1]+0x15,b'\0');t.setup()
    assert t.state()==1 and not t.opens and t.m.read(t.record+4,4)==bytes(4)
    # Failed endpoint lookup is handled by the original task; no transfer starts.
    t=Setup(patched,h,fm1);t.bind_initial();t.setup();t.endpoint_error=True;t.drain()
    t.enqueue(t.port,[0xf80f]);t.poll(1);t.poll(0);assert not t.requests
    # Disconnect through the original manager and close-request packers, then
    # rebind/setup on the same port while the old RX DMA completion is pending.
    t=Setup(patched,h,fm1);t.bind_initial();t.setup();t.drain();t.poll(0)
    pending=t.requests[-1]
    t.m.write(EVENT,bytes([3])+bytes(3)+P(DEVICE)+bytes(4))
    t.checked(0x600083cc,EVENT,0,0,0)
    assert t.state()==0 and t.m.read(t.record+8,4)==bytes(4)
    assert [e[0] for _,e in t.opens]==[1,1]
    t.drain();assert t.cancels==[pending['ep']]
    t.events.clear();t.bind_initial();t.setup();t.drain();t.poll(0)
    assert len(t.requests)==1  # old buffer still owned
    t.done(pending,P(0x643c9009));t.poll(0)
    assert not t.received and len(t.requests)==2
    t.done(t.requests[-1],P(0x643e9009));t.poll(0)
    assert t.received==[0x643e9009|(t.port<<5)] and t.state()==5
    # Roland's original alt1 switch/rebind sequence remains identical.
    stock=main[0xb499c:0xb499c+0x102];roland=[]
    for old in (True,False):
        t=Setup(patched,h,stock,vid=0x582);t.bind_initial();t.setup(original=old)
        roland.append((t.controls,t.binds,t.state(),t.opens,t.notices))
    assert roland[0]==roland[1] and roland[0][1],roland
    return dict(before_state=before.state(),before_midi_opens=0,ports=cases,
                midi_interface_zero=directions,roland_original_sequence_equal=True,
                manager_disconnect_reconnect_with_pending_rx=True,
                original_control_wait=verify_control_wait(patched),
                boundary='Successful control I/O, descriptor/list/endpoint lookup and RTOS delivery are modeled; original completion and handlers execute')


def verify_control_wait(image):
    """Original control API waits for completion; only RTOS primitives modeled."""
    observed=[]
    for status in (0,-7):
        m=Machine(image);order=[];request=[0]
        global_base=struct.unpack('<I',m.read(0x60009624,4))[0]
        m.write(global_base+0x14,P(1))
        def stub(u,a,size,data):
            if a not in (0x6000b7ec,0x6000b6c4,0x6000b8e6,0x6000b88a):return
            order.append(a)
            if a==0x6000b6c4:
                request[0]=u.reg_read(UC_ARM_REG_R1)
                assert m.read(request[0]+0x10,8)==bytes.fromhex('010b000002000000')
                m.write(request[0]+8,P(0xdeadbeef))
            elif a==0x6000b8e6:
                assert request[0] and u.reg_read(UC_ARM_REG_R0)==7
                m.write(request[0]+8,P(status))
            u.reg_write(UC_ARM_REG_R0,7 if a==0x6000b7ec else 0)
            u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
        m.uc.hook_add(UC_HOOK_CODE,stub)
        m.write(0x2001fff0,P(2)+bytes(12))
        assert m.call(0x60009558,DEVICE,1,11,0)[0]==status&0xffffffff
        assert order==[0x6000b7ec,0x6000b6c4,0x6000b8e6,0x6000b88a]
        observed.append(status)
    return observed
