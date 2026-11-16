"""Execute send policy, factory effect initializers and control writers.

Program upload/boundary/readback instructions run. Bulk program DMA is copied;
data-RAM transport, command completion and RTOS waits are explicit boundaries.
The MASTER parameter database replay is skipped, then the real independent
factory callbacks run. This does not execute a physical DSP or measure time.
"""
import struct
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE, UC_MEM_READ
from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
                              UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,
                              UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_SP)
from fx_sends_audit import SendMachine, SLOT_STATE
from routing_hardware_audit import STOP, u32

REGS=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)


class SendsMachine(SendMachine):
    boundaries={0x6000c59e:'MASTER parameter view construction',
                0x600249dc:'MASTER parameter callback lookup (no replay)',
                0x60054c14:'DSP command completion',0x60054c32:'DSP synchronization wait',
                0x6005513c:'Data descriptor clear transport',0x60054bec:'Data descriptor upload transport',
                0x60054c46:'Delay RAM clear transport',0x60054c50:'Delay RAM completion',
                0x6005507e:'Coefficient smoothing completion',
                0x6000f1bc:'Current DSP task boot-mode query',0x6000bd6c:'Empty parameter queue',
                0x600550ba:'DSP1 delay RAM completion',0x600550c4:'DSP0 delay RAM completion'}

    def __init__(self,image,symbols):
        super().__init__(image)
        self.symbols=symbols;self.command=0;self.boundary_calls=[];self.loads=[]
        self.parameters={0x19:0,6:0};self.headphone_mix=64
        self.uc.mem_write(0x20000b24,u32(48000))
        self.uc.hook_add(UC_HOOK_CODE,self.control)
        self.uc.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,self.program_port,
                         begin=0x40100900,end=0x40100907)

    def ret(self,value=0):
        self.uc.reg_write(UC_ARM_REG_R0,value)
        self.uc.reg_write(UC_ARM_REG_PC,self.uc.reg_read(UC_ARM_REG_LR))

    def call(self,address,first,second):
        self.uc.reg_write(UC_ARM_REG_SP,0x2003f000)
        self.uc.reg_write(UC_ARM_REG_LR,STOP|1)
        self.uc.reg_write(UC_ARM_REG_R0,first);self.uc.reg_write(UC_ARM_REG_R1,second)
        self.uc.emu_start(address|1,0,timeout=5_000_000,count=500000)
        assert self.uc.reg_read(UC_ARM_REG_PC)==STOP,hex(self.uc.reg_read(UC_ARM_REG_PC))
        assert self.uc.reg_read(UC_ARM_REG_SP)==0x2003f000

    def control(self,uc,address,size,user):
        args=[uc.reg_read(r) for r in REGS]
        if address==0x60029eec:
            self.loads.append((self.register(SLOT_STATE),args[1]))
        if address in (0x0100a90e,0x0100a9e8):
            source=self.register(uc.reg_read(UC_ARM_REG_SP))
            destination=(0x40150000 if args[1]==0 else 0x40170000)+args[2]*4
            assert args[1] in (0,1) and args[2]*4+args[3]<=0x8000
            uc.mem_write(destination,bytes(uc.mem_read(source,args[3])))
            self.ret();return
        if address==0x6001a896:
            assert args[0]==0x600b5390
            self.ret(self.parameters.get(args[1],0));return
        if address==0x6001a1ce:
            assert args[:3]==[0x60514504,0x20,0]
            self.ret(self.headphone_mix);return
        if address==0x60054bec:
            # Data-descriptor transport model, disjoint from instruction DMA.
            offset,length,source=struct.unpack('<III',uc.mem_read(args[3]+args[2]*12,12))
            assert offset%8==0 and length%8==0 and offset+length<=0x800
            uc.mem_write((0x4014e000 if args[1]==0 else 0x4016e000)+offset,
                         bytes(uc.mem_read(source,length)))
        if address in self.boundaries:
            self.boundary_calls.append((address,args))
            self.ret()

    def program_port(self,uc,access,address,size,value,user):
        if access==UC_MEM_READ:
            if address==0x40100904 and self.command&0xf0000 in (0x50000,0x70000):
                source=0x40100000+(self.command&0xfffff)
                bits=(int.from_bytes(uc.mem_read(source^2,2),'little')<<16 if self.command>>28==0
                      else int.from_bytes(uc.mem_read(source,4),'little'))
                uc.mem_write(address,u32(bits))
        elif address==0x40100900:
            self.command=value
        elif address==0x40100904 and self.command&0xf0000 in (0x50000,0x70000):
            destination=0x40100000+(self.command&0xfffff)
            if self.command>>28==0:
                uc.mem_write(destination^2,struct.pack('<H',value>>16))
            elif self.command>>28==2:
                uc.mem_write(destination,u32(value))
            # Float-immediate conversion belongs to the physical DSP and is
            # recorded, not treated as raw instruction bits in this model.

    def flush(self):
        return self.checked(self.symbols['mx1_sends_flush'],0,0)


def verify(original,patched,build):
    symbols=build['symbols'];m=SendsMachine(patched,symbols)
    state=symbols['mx1_sends_state']
    def configure(mode=0,kind=0,param=64,time=10):
        m.uc.mem_write(state+28,u32(1+mode+(kind<<2)+(param<<5)+(time<<12)))
    cases=0
    for kind in range(8):
        configure(kind=kind)
        before=len(m.loads)
        requests=m.flush()
        assert m.loads[before:]==[(1,1 if kind<4 else 3 if kind==4 else 4)]
        assert m.register(SLOT_STATE)==0
        assert m.register(SLOT_STATE+0x64)==(1 if kind<4 else 3 if kind==4 else 4)
        assert m.register(0x4016c994)==0x3f800000
        dry=0x73 if kind<4 else 0x78 if kind==4 else 0x75
        assert any(r['kind']=='coefficient' and r['core']==1 and r['index']==dry and r['float_bits']==0 for r in requests)
        # Every factory parameter and program write belongs to slot 1. New
        # bus coefficients have their own range; MASTER coefficients stay intact.
        assert all(r['index']>=0x70 for r in requests if r['kind']=='coefficient' and r['core']==1)
        for param,time in ((0,0),(127,127),(17,101)):
            configure(kind=kind,param=param,time=time);n=len(m.loads);m.flush()
            assert len(m.loads)==n,'Parameter edit reloaded/truncated the effect'
            assert m.register(SLOT_STATE)==0
            cases+=1
        n=len(m.loads);m.flush();assert len(m.loads)==n
    internal_program=bytes(m.uc.mem_read(0x40176000,0x2000))
    internal_coefficients=bytes(m.uc.mem_read(0x4016c700,0xf0))
    internal_descriptors=bytes(m.uc.mem_read(0x4016e138,0x108))
    for algorithm in range(20):
        requests=m.checked(0x60029ee4,0,algorithm)
        assert bytes(m.uc.mem_read(0x40176000,0x2000))==internal_program
        assert bytes(m.uc.mem_read(0x4016c700,0xf0))==internal_coefficients
        assert bytes(m.uc.mem_read(0x4016e138,0x108))==internal_descriptors
        assert all(r['index']<0x70 or r['index']==0x9a for r in requests
                   if r['kind']=='coefficient' and r['core']==1)
        assert m.register(0x4016c9a4)==0x3f800000
    # Enter the actual patched dispatcher with an explicitly empty RTOS queue.
    # Both route policy and the complete sends flush run after the original drain.
    before=len(m.loads)
    requests=m.checked(0x60024bae,0,0)
    assert len(m.loads)==before and any(r.get('index')==0x99 for r in requests)
    # Actual per-channel values use the original AUX curve and pre/post setting.
    m.uc.mem_write(state,bytes(range(11))+bytes(range(117,128)))
    for post in (0,1):
        m.parameters[6]=post;m.flush()
        assert m.register(0x4016c964)==(0x3f800000 if post else 0)
        for ch in range(11):
            assert m.register(0x4016c004+(0x80+ch)*16)==m.register(0x60077af4+ch*4)
            assert m.register(0x4016c004+(0x8b+ch)*16)==m.register(0x60077af4+(117+ch)*4)
    for mode in (1,2,2,0):
        configure(mode=mode);m.headphone_mix=91
        requests=m.flush()
        assert m.register(0x4016c974)==(0x3f800000 if mode==1 else 0)
        assert m.register(0x4016c984)==(0x3f800000 if mode==2 else 0)
        if mode in (0,2):
            phones=[r for r in requests if r['kind']=='coefficient' and r['core']==0]
            assert [r['index'] for r in phones]==[0x26,0x27]
            assert phones[0]['float_bits']==(0 if mode==2 else m.register(0x60077ef4+91*4))
    m.parameters[0x19]=2;n=len(m.loads);requests=m.flush()
    assert len(m.loads)==n and m.register(0x4016c994)==0
    assert all(m.register(0x4016c004+i*16)==0 for i in range(0x80,0x96))
    m.parameters[0x19]=0;m.uc.mem_write(SLOT_STATE+0x64,u32(0));m.flush()
    assert len(m.loads)==n+1,'Graph reset did not reload internal instance'
    m.uc.mem_write(0x6051deb8,u32(4));n=len(m.loads);assert m.flush()==[]
    assert len(m.loads)==n and not m.writes
    # Graph-entry trampoline: original stop boundary precedes all new writes;
    # the unchanged remainder of graph construction is a boundary in this case.
    graph=SendsMachine(patched,symbols);phases=[]
    def prefix(uc,address,size,user):
        if address==0x60026792:
            phases.append('original_stop');graph.ret()
        elif address==0x600267bc:
            phases.append('original_continuation')
            sp=uc.reg_read(UC_ARM_REG_SP)
            saved=struct.unpack('<4I',uc.mem_read(sp,16))
            for reg,value in zip((UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_PC),saved):
                uc.reg_write(reg,value)
            uc.reg_write(UC_ARM_REG_SP,sp+16)
    graph.uc.hook_add(UC_HOOK_CODE,prefix)
    graph.uc.mem_write(0x20030000,u32(0x20030100))
    for normal in (False,True):
        graph.uc.mem_write(0x20030104,u32(0x600777c4 if normal else 0x600777ac))
        graph.uc.mem_write(state+36,bytes([1]))
        requests=graph.checked(0x600267b4,0x20030000,0)
        assert phases[-2:]==['original_stop','original_continuation']
        assert graph.uc.mem_read(state+36,1)==bytes(1)
        assert [r['index'] for r in requests]==([0x99,0x9a] if normal else [])
    from routing_audio_extract import reconstruct
    _,programs=reconstruct((0x600ba008,symbols['mx1_sends_programs']),(18,20),image=patched)
    graph.uc.mem_write(0x40170000,programs[1])
    for entry in (0x11ca,0x1aca,0x1b32):
        for mode in (1,0):
            graph.uc.reg_write(UC_ARM_REG_R2,entry);graph.uc.reg_write(UC_ARM_REG_R3,mode)
            graph.checked(0x60026d6c,0,1)
            assert int.from_bytes(graph.uc.mem_read(0x40170000+((entry+2)^2),2),'little')==0xff70|mode
    return dict(name='Compiled ARM send policy, all eight factory variations, live edits, destinations and reset/diagnostic guards',
                status='pass',parameter_cases=cases,loader_calls=len(m.loads),master_algorithm_isolation_cases=20,
                original_effect_load_and_initializers=True,
                graph_prefix_cases=2,original_mute_marker_cases=6,
                graph_prefix_boundaries=['Original graph stop call', 'Original graph continuation after displaced prologue'],
                modeled_boundaries={hex(k):v for k,v in m.boundaries.items()})
