"""Host MIDI ARM regression checks. Hardware transfers/RTOS delivery are modeled.

Original startup, descriptor ABI/selection, MIDI ring dispatch and stock USB
request/completion instructions execute. These are not USB timing measurements.
"""
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE, UC_PROT_READ, UC_PROT_EXEC
from unicorn.arm_const import *
from arm_machine import Machine, BASE
from memory_map import recover
from container_tool import sha256
from usb_midi_verify import EVENTS

P=lambda x:struct.pack('<I',x & 0xffffffff)
H=lambda x:struct.pack('<H',x)
BUF=0x20010000; RECORD=0x20012000; DEVICE=0x20014000; INFO=0x20015000; OUT=0x20016000

def configuration(packet=64, direction='both', composite=False):
    ac=bytes.fromhex('09 04 00 00 00 01 01 00 00 09 24 01 00 01 09 00 01 01')
    jacks=bytes.fromhex('06 24 02 01 01 00 06 24 02 02 02 00 09 24 03 01 03 01 02 01 00 09 24 03 02 04 01 01 01 00')
    eps=b''
    for ep,jack in ((1,1),(0x81,3)):
        if direction=='out' and ep&128 or direction=='in' and not ep&128:continue
        eps+=bytes([9,5,ep,2])+H(packet)+bytes(3)+bytes([5,0x25,1,1,jack])
    ms=bytes([9,4,1,0,len(eps)//14,1,3,0,0])+bytes([7,0x24,1,0,1])+H(37)+jacks+eps
    extra=bytes.fromhex('09 04 02 00 00 01 02 00 00') if composite else b''
    body=ac+ms+extra
    return bytes([9,2])+H(9+len(body))+bytes([3 if composite else 2,1,0,0x80,50])+body

def pipeline(image,cfg,vid=0x1234,speed=0,policy=0x60007bf8):
    m=Machine(image);m.write(BUF,cfg);m.write(RECORD,bytes(0x400));m.write(DEVICE,bytes(0x100))
    m.write(DEVICE+0x10,H(vid)+H(0x5678)+H(0x100));m.write(DEVICE+0x58,H(speed))
    m.write(RECORD+0x66,H(vid))
    rc,_=m.call(0x6000a1e2,RECORD+0x64,BUF)
    if rc:return rc,None
    m.call(0x60008580,INFO,OUT,DEVICE,RECORD)
    m.call(policy,INFO,OUT)
    return rc, (m.read(RECORD,0x200),m.read(OUT,18))

def verify_descriptor_lengths(patched,report):
    policy=report['host_midi']['symbols']['mx1_host_select']
    fixture=Path(__file__).resolve().parents[1]/'evidence/fm1-host-midi-20261103'
    cfg=bytes.fromhex((fixture/'configuration.hex').read_text())
    device=bytes.fromhex((fixture/'device.hex').read_text())
    assert sha256(cfg)=='9d0d30219e1228a7809ef0abe08bda1068a4a0de5487737445d4f06f7e9162b0'
    assert sha256(device)=='3d15b0b23702b6dae0db3a850dc1229d31700f62416a9b4521bd302e7cc7d40a'
    vid=struct.unpack_from('<H',device,8)[0]
    selected=struct.pack('<9H',0,0,0,0,0,0,1,0,0)
    rc,result=pipeline(patched,cfg,vid=vid,policy=policy)
    assert rc==0 and result[1]==selected
    # FM-1 has audio streaming before MIDI. Only MIDI interface 2 is selected;
    # audio remains disabled even though an audio alternate is advertised.
    assert result[0][0x64+0xe4]==2
    headers=[];at=9
    while at<len(cfg):
        if cfg[at:at+5]==bytes([7,0x24,1,0,1]):headers.append(at)
        at+=cfg[at]
    assert len(headers)==1
    header=headers[0];accepted=[]
    # Every length near this exact descriptor must fail except the two
    # documented counts. Include truncation into each descriptor boundary.
    for length in range(len(cfg)+2):
        c=bytearray(cfg);c[header+5:header+7]=H(length)
        rc,res=pipeline(patched,c,vid=vid,policy=policy)
        if not rc:
            assert res[1]==selected
            accepted.append(length)
    assert accepted==[37,65],accepted
    for length in range(9,len(cfg)):
        c=bytearray(cfg[:length]);c[2:4]=H(length)
        assert pipeline(patched,c,vid=vid,policy=policy)[0]!=0,length
    cases=[]
    # Count the actual span, not a hardcoded 65: one-way endpoints, 7-byte
    # standard endpoints and a following unrelated interface are covered.
    for direction in ('both','in','out'):
      for epbytes in (7,9):
        c=configuration(direction=direction,composite=True)
        parts=[];at=9
        while at<len(c):
            d=c[at:at+c[at]];at+=len(d)
            if d[1]==5 and epbytes==7:d=bytes([7])+d[1:7]
            parts.append(d)
        c=c[:9]+b''.join(parts);c=bytearray(c);c[2:4]=H(len(c))
        total=37+(epbytes+5)*(2 if direction=='both' else 1)
        for length in (37,total,total-1,total+1,total+9):
            c[41:43]=H(length)
            rc,res=pipeline(patched,c,policy=policy)
            assert (rc==0)==(length in (37,total)),(direction,epbytes,length,rc)
            if not rc:assert res[1]==selected
        cases.append([direction,epbytes,total])
    return dict(fm1_configuration_sha256=sha256(cfg),accepted_fm1_lengths=accepted,
                length_cases=len(cfg)+2,truncated_cases=len(cfg)-9,endpoint_cases=cases,
                source='FM-1 monitor built descriptor, not a live USB capture')

class Transport:
    def __init__(self,image,report):
        self.m=Machine(image);self.m.uc.mem_protect(0x01001000,0xf000,UC_PROT_READ|UC_PROT_EXEC);self.s=report['symbols'];self.requests=[];self.received=[];self.cancels=[];self.wakes=[];self.reject=0
        self.m.uc.hook_add(UC_HOOK_CODE,self.stub)
    def stub(self,u,a,size,data):
        m=self.m
        if a not in (0x60009464,0x01000876,0x01008256,0x60009716):return
        r=[u.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
        if a==0x60009464:
            stack=struct.unpack('<3I',m.read(u.reg_read(UC_ARM_REG_SP),12))
            self.requests.append({'ep':r[0],'buffer':r[1],'size':r[2],'callback':r[3],
                                  'token':stack[0],'timeout':stack[1],'flags':stack[2],
                                  'data':m.read(r[1],r[2]).hex()})
        elif a==0x01008256:self.received.append(r[0])
        elif a==0x60009716:self.cancels.append(r[0])
        elif a==0x01000876:self.wakes.append(r[:2])
        u.reg_write(UC_ARM_REG_R0,self.reject if a==0x60009464 else 0)
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    def checked(self,address,*args):
        regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
        tags=[0x12340000+i for i in range(8)]
        for reg,tag in zip(regs,tags):self.m.uc.reg_write(reg,tag)
        rc=self.m.call(address,*args)[0]
        assert [self.m.uc.reg_read(r) for r in regs]==tags,hex(address)
        return rc
    def call(self,name,*args):return self.checked(self.s[name],*args)
    def attach(self,port,tx,speed=0,packet=64,vid=0x1234):
        # Distinct endpoint per generation/direction; records in stock table.
        ep=0x20010000+port*0x100+tx*0x50; interface=0x20011000+port*0x100
        dev=0x20012000+port*0x100;rec=0x4000bf20+tx*0x50+port*0x14
        self.m.write(ep,bytes(0x50));self.m.write(interface,bytes(0x40));self.m.write(dev,bytes(0x100));self.m.write(rec,bytes(0x14))
        self.m.write(ep+8,bytes([1,0 if tx else 128,2,0]));self.m.write(ep+0x10,H(packet))
        self.m.write(ep+0x20,P(interface));self.m.write(interface+8,P(dev));self.m.write(dev+0x10,H(vid));self.m.write(dev+0x58,H(speed))
        self.m.write(rec+4,P(ep));self.m.write(rec+12,bytes([port,0,1,2]))
        rc=self.checked(0x60009160 if tx else 0x600090fa,rec)
        return rc,ep
    def enqueue(self,port,words):
        # Run the unchanged original cross-core consumer's queue insertion and
        # patched original drain, including cable->physical-port translation.
        self.m.write(0x4000bc0a,H(1))
        for word in words:
            tagged=word | port<<5
            assert self.m.call(0x010092bc,tagged)[0]==1
    def poll(self,tx):self.call('mx1_host_tx_poll' if tx else 'mx1_host_rx_poll')
    def done(self,request,data=b'',status=0,length=None):
        if data:self.m.write(request['buffer'],data)
        n=(len(data) if request['token']&1==0 else request['size']) if length is None else length
        self.m.write(0x2001d000,P(status)+P(n))
        self.checked(request['callback'],0,request['ep'],0x2001d000,request['token'])
    def close(self,port,tx):
        self.m.write(0x2001c000,bytes(4)+bytes([port])+bytes(7))
        self.checked(0x010091bc if tx else 0x0100906c,0x2001c000)


def verify(original,patched,main,report):
    groups=[]
    def passed(name,**kw):groups.append(dict(name=name,status='pass',**kw))
    h=report['host_midi'];s=h['symbols']
    assert sha256(patched)==h['patched_app_sha256']
    from host_midi_ehci_verify import verify as verify_ehci
    passed('Original EHCI short-packet completion and continued MIDI reception',**verify_ehci(original,patched,h))
    # Execute original reset copy/zero loops from dirty memory, not Python scatter.
    machines=[]
    for image in (original,patched):
        m=Machine(image,scatter=False)
        m.write(0x01017868,b'\xa5'*h['state_bytes'])
        m.write(h['audio_state_start'],b'\xa5'*h['audio_state_bytes'])
        m.uc.reg_write(UC_ARM_REG_SP,0x2001fff0)
        m.uc.emu_start(BASE|1,BASE+0x7e,count=2000000,timeout=2000000)
        assert m.uc.reg_read(UC_ARM_REG_PC)==BASE+0x7e
        machines.append(m)
    assert machines[1].read(h['state_start'],h['state_bytes'])==bytes(h['state_bytes'])
    assert machines[1].read(h['audio_state_start'],h['audio_state_bytes'])==bytes(h['audio_state_bytes'])
    assert machines[1].read(h['audio_code_start'],h['audio_code_bytes'])==patched[h['audio_source']-BASE:]
    assert machines[1].read(h['code_start'],h['code_bytes'])==patched[h['insert_offset']:h['insert_offset']+h['code_bytes']]
    for op in recover(original)['operations']:
        if op['kind']=='copy' and op['length'] and op['destination']!=0x01000300:
            assert machines[0].read(op['destination'],op['length'])==machines[1].read(op['destination'],op['length'])
    passed('Original USB startup copies code, zeroes state, preserves existing initialized data',code_bytes=h['code_bytes'],state_bytes=h['state_bytes'])
    # Execute USB MPU setup and pool initialization with a dirty reservation.
    m=Machine(patched);m.uc.mem_map(0xe000e000,0x2000);regions={};selected=[0]
    def mpu_write(u,access,a,size,value,data):
        if a==0xe000ed98:selected[0]=value
        elif a==0xe000ed9c:regions.setdefault(selected[0],{})['base']=value
        elif a==0xe000eda0:regions[selected[0]]['attributes']=value
    def mpu_stub(u,a,size,data):
        if a==0x010006f0:u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_MEM_WRITE,mpu_write,begin=0xe000ed98,end=0xe000eda0)
    m.uc.hook_add(UC_HOOK_CODE,mpu_stub);m.call(0x60003760)
    assert regions[1]['base']==0x01000000 and regions[1]['attributes']==0x06000021
    assert regions[2]['base']==0x01010000 and regions[2]['attributes']==0x1300001d
    # Original SDRAM MPU region permits execution and writes across the
    # reserved [607f0000,60800000) range. No MPU protection is relaxed.
    assert regions[6]=={'base':0x60000000,'attributes':0x03000035}
    m.write(h['state_start'],b'\xa5'*h['state_bytes'])
    m.call(0x01001b9c,count=500000)
    assert m.read(h['state_start'],h['state_bytes'])==b'\xa5'*h['state_bytes']
    passed('Original USB MPU permissions and RTOS pools exclude the extension state',regions=regions,
           general_pool=['0x010142c4','0x010152c4'],stack_pool=['0x01020000','0x01028000'])
    # Poll hooks are at external call sites: preserve the original TX loop's
    # backward branch into its own prologue. Decode both generated BL targets.
    from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB)
    for offset,address,name in ((0x34188,0x01009294,'mx1_host_tx_poll'),(0x33ff8,0x01009104,'mx1_host_rx_poll')):
        ins=list(md.disasm(patched[offset:offset+4],address))
        assert len(ins)==1 and ins[0].mnemonic=='bl' and int(ins[0].op_str[1:],16)==s[name]&~1
    assert patched[0x3426a:0x342ae]==original[0x3426a:0x342ae]
    passed('Original TX loop remains intact; task call sites target the new poll wrappers')
    samples=[]
    for speed,packet in [(0,8),(0,16),(0,32),(0,64),(0x400,512)]:
      for direction in ('both','in','out'):
       for composite in (False,True):
        cfg=configuration(packet,direction,composite)
        rc,new=pipeline(patched,cfg,speed=speed,policy=s['mx1_host_select'])
        assert rc==0 and struct.unpack('<9H',new[1])==(0,0,0,0,0,0,1,0,0),(speed,direction,rc,new)
        assert pipeline(original,cfg,speed=speed)[1][1]==bytes(18)
        samples.append([speed,packet,direction,composite])
    # Real embedded stock Roland descriptor fixture, exact original parser/selector behavior.
    cfg=main[0xb499c:0xb499c+0x102]
    assert pipeline(original,cfg,0x582,0x400)==pipeline(patched,cfg,0x582,0x400,s['mx1_host_select'])
    passed('Standard MIDI-only/composite descriptors through original ABI; Roland unchanged',cases=samples)
    passed('FM-1 descriptor and both bounded MIDI header length conventions',
           **verify_descriptor_lengths(patched,report))
    from host_midi_setup_verify import verify_setup
    passed('Original bind/setup/completion opens alternate-zero MIDI without a rebind',
           **verify_setup(patched,report,main))
    cfg=configuration();malformed=[]
    for n in range(9,len(cfg)):
        c=bytearray(cfg[:n]);c[2:4]=H(n);malformed.append(bytes(c))
    for offset,value in [(18,0),(27,8),(29,8),(30,1),(31,3),(34,0x20),(36,6),(39,2),(41,0),(47,0),(59,1),(75,0),(76,3),(77,3),(80,1),(85,2),(86,3),(89,1),(99,2)]:
        c=bytearray(cfg);c[offset]=value;malformed.append(bytes(c))
    rejected=0
    for c in malformed:
        rc,res=pipeline(patched,c,policy=s['mx1_host_select'])
        assert rc or res[1]==bytes(18), c.hex()
        rejected+=1
    # Explicit malformed cases with stable descriptor offsets.
    explicit=[b'\x09\x02\x00\x00'+bytes(5),cfg[:9]+b'\0'+cfg[10:]]
    for c in explicit:assert pipeline(patched,c,policy=s['mx1_host_select'])[0]!=0
    passed('Malformed/truncated descriptor chains remain unselected',rejected_cases=rejected)
    transmitted=[]
    for speed,packet in [(0,64),(0x400,512)]:
        t=Transport(patched,h)
        for port in range(4):assert t.attach(port,1,speed,packet)[0]==0
        for port in range(4):t.enqueue(port,[0x643c9009,0x0000f80f,0x0000fa0f,0x0000fc0f])
        t.poll(1);assert len(t.requests)==4
        for req in t.requests:
            assert req['size']==16 and req['data']=='0ff800000ffa00000ffc000009903c64',req
            assert req['flags']==0 and req['timeout']==100
            transmitted.append(req)
            t.done(req)
        t.poll(1);assert len(t.requests)==4
    passed('Original TX ring dispatches all four ports; sync precedes queued channel data',requests=transmitted)
    t=Transport(patched,h)
    for port in range(4):assert t.attach(port,0)[0]==0
    t.poll(0);assert len(t.requests)==4
    words=[0x00643c90<<8|9,0x0000f80f,0x0000fa0f,0x0000fb0f,0x0000fc0f,0x0001f203,0x0001f102,0x0007b00b]
    # Above note is 32-bit after masking.
    for req in list(t.requests):t.done(req,b''.join(P(w) for w in words))
    t.poll(0)
    assert len(t.received)==8,t.received
    for p in range(4):assert t.received[p*2:p*2+2]==[((words[0]&0xffffffff)|(p<<5)),words[-1]|(p<<5)]
    passed('RX uses stock port/cable numbering and blocks clock/transport/SPP/MTC on every port',received=[hex(x) for x in t.received])
    # Cancellation and immediate reconnect cannot reuse buffers or deliver old input.
    t=Transport(patched,h);assert t.attach(0,0)[0]==0;t.poll(0);old=t.requests[0]
    t.close(0,0);assert t.cancels==[old['ep']]
    assert t.attach(0,0)[0]==0;t.poll(0);assert len(t.requests)==1
    t.done(old,P(0x643c9009));t.poll(0)
    assert not t.received and len(t.requests)==2
    passed('Reconnect retains DMA ownership until old completion; stale RX is discarded')
    # Failure/short writes are terminal until reconnect; stalled port does not block others.
    for failure in ('submit','completion','short','overflow'):
        t=Transport(patched,h)
        for port in (0,1):assert t.attach(port,1)[0]==0
        if failure=='overflow':t.enqueue(0,[0x0000f80f]*33)
        else:t.enqueue(0,[0x0000f80f])
        if failure=='submit':t.reject=0xfffffff5
        t.poll(1);t.reject=0
        if failure=='completion':t.done(t.requests[0],status=-7)
        if failure=='short':t.done(t.requests[0],length=0)
        t.enqueue(1,[0x0000f80f]);t.poll(1)
        assert t.requests[-1]['token']==3
        before=len(t.requests);t.enqueue(0,[0x0000f80f]);t.poll(1);assert len(t.requests)==before
    passed('Submission/completion/short-write/overflow failures isolate the affected output')
    # Original asynchronous USB API request packing and completion ABI. The
    # heap allocator/mailbox/free are stubbed; original struct construction,
    # completion dispatch and endpoint bookkeeping execute unchanged.
    m=Machine(patched); req=0x2001a000; ep=0x2001b000; interface=0x2001c000; completion=0x2001d000
    g=struct.unpack('<I',m.read(0x60009624,4))[0]
    m.write(g+0x14,P(1)); m.write(g+0xc,P(7)); m.write(g+4,P(9))
    m.write(ep+0x20,P(interface)); events=[]; callback=0x0fff0100
    def api_stub(u,a,size,data):
        if a not in (0x6000b330,0x6000b6c4,0x6000b388,callback):return
        if a==callback:
            events.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),
                           m.read(u.reg_read(UC_ARM_REG_R2),8).hex(),u.reg_read(UC_ARM_REG_R3)))
        u.reg_write(UC_ARM_REG_R0,req if a==0x6000b330 else 0)
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,api_stub)
    for flags in (0,0x2000):
        m.write(0x2001fff0,P(3)+P(100)+P(flags))
        assert m.call(0x60009464,ep,0x20000800,64,callback|1)[0]==0
        assert struct.unpack('<7I',m.read(req+0xc,28))==(interface,ep,0x20000800,64,callback|1,3,100)
        assert m.read(req+0x28,2)==H(flags)
    for status in (0,-7,-9):
        m.write(ep+0x14,P(req));m.write(ep+0x18,P(0));m.write(ep+8,b'\x01\x00\x02')
        m.write(completion+8,P(status)+P(interface)+P(ep)+P(64))
        m.call(0x6000f60a,completion,0,0,0)
        assert events[-1]==(interface,ep,(P(status)+P(64)).hex(),3),events
        assert m.read(ep+0x14,4)==bytes(4)
    passed('Original USB request builder and completion dispatcher establish callback ABI',completion_cases=events)
    # Main-processor sender remains unchanged. Run its clock fanout for enabled
    # host destinations; model only the cross-core mailbox accepting each word.
    m=Machine(main);sent=[];m.write(0x200003fc,b'\x01'*10)
    def main_stub(u,a,size,data):
        if a not in (0x60057ebc,0x01009430):return
        if a==0x01009430:sent.append(m.read(u.reg_read(UC_ARM_REG_R1),4))
        u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,main_stub)
    for word in (0xf80f,0xfa0f,0xfb0f,0xfc0f):
        m.write(BUF,P(word));m.call(0x01000e92,0,BUF,0,0x2a800)
    assert sent==[P(w|(p<<5)) for w in (0xf80f,0xfa0f,0xfb0f,0xfc0f) for p in range(4)]
    passed('Original main MIDI sender fans Clock/Start/Continue/Stop to all enabled host ports',
           runtime='0x01000e92',decoded_offset='0xd171e',enabled_host_mask='0x2a800',words=[w.hex() for w in sent])
    # Notes, controllers and complete multi-packet SysEx traverse unchanged.
    t=Transport(patched,h);assert t.attach(0,0)[0]==0;t.poll(0)
    payload=b''.join(bytes.fromhex(packet) for name,raw,packet in EVENTS
        if not name.startswith(('clock','start','continue','stop','song_position','quarter_frame')))
    expected=[int.from_bytes(payload[n:n+4],'little') for n in range(0,len(payload),4)]
    # Feed finite endpoint packets, not an oversized simulated USB transaction.
    for off in range(0,len(payload),64):
        req=t.requests[-1];t.done(req,payload[off:off+64]);t.poll(0)
    assert t.received==expected
    passed('Notes, controllers and SysEx survive RX unchanged',events=len(expected))
    # Background message overflow must not suppress the priority clock lane.
    t=Transport(patched,h);t.attach(0,1);t.enqueue(0,[0x643c9009]*33+[0xf80f]);t.poll(1)
    assert t.requests[-1]['data']=='0ff80000'
    passed('Background queue overload leaves sync output running')
    return {'status':'pass','patched_app_sha256':sha256(patched),'groups':groups,'hardware_access':False,
            'limits':['Asynchronous USB submission/cancel and RTOS flag delivery are stubbed; no USB controller or PHY is simulated',
                      'Synthetic descriptors and FM-1 built-image descriptors; no physical USB capture or device validation',
                      'No latency/jitter, electrical, disconnect timing or full firmware scheduling claim']}

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1];b=root/'build/mainline';r=json.loads((b/'build-report.json').read_text())
    report=verify((root/'analysis/container_app_usb.bin').read_bytes(),(b/'app_usb.mainline.bin').read_bytes(),
                  (root/'analysis/container_app_main.bin').read_bytes(),r)
    (b/'host-midi-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
