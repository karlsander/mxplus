"""Actual stock parameter transactions and compiled mastering UI, offline only."""
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_SP
from arm_machine import Machine
from routing_ui_verify import UIMachine, PACKET, PAGE, MODAL, u32, signed
from container_tool import sha256

SYSTEM = 0x600b5390
MASTER, MIX, SETUP = 0x600b53b8, 0x600b53ac, 0x60514504
ADC = 0x605129b4
STATE = 0x01017444
ASSIGN = {6:4,7:3,8:7,9:6,10:10,11:9,12:14,13:13,
          14:29,15:28,16:33,17:32,18:37,19:36,20:42,21:41,
          22:46,23:45,24:50,25:49,26:56,27:57}
SWITCHES = {0x29:(0,0x34),0x34:(2,0x3f),0x37:(12,0x42),
            0x2d:(27,0x38),0x30:(40,0x3b),0x33:(17,0x3e),
            0x3e:(19,0x49),0x49:(58,0x54)}
LABELS = {0:'EQ ',2:'Lty',3:'Lgn',4:'LFr',6:'LMg',7:'LMf',9:'HMg',10:'HMf',
          12:'Hty',13:'Hgn',14:'HFr',17:'LCt',19:'Enh',27:'EXP',28:'ELt',29:'ELr',
          32:'EMt',33:'EMr',36:'EHt',37:'EHr',40:'CMP',41:'CLt',42:'CLr',45:'CMt',
          46:'CMr',49:'CHt',50:'CHr',56:'Mid',57:'Sid',58:'LIM'}


class MasterMachine(UIMachine):
    def __init__(self,image,symbols):
        self.clock=10000; self.tick_calls=0; self.redraw_calls=0
        self.leds={}; self.notices=[]; self.real_redraw=False
        self.saves=[]; self.loads=[]; self.transactions=[]
        super().__init__(image,symbols)
        # Normal operating state after stock 0x6001649c clears the UI lock.
        self.write(0x600b537c,u32(0))
        locale = self.checked(0x6005ce38,0,0)[0]
        self.write(0x6064c0cc,u32(locale+1))  # Same ctype pointer as stock 0x6000020e..0x60000214.
        # Model the object constructors by installing the original vtables.
        for ctx,vt in ((SYSTEM,0x600a9970),(MASTER,0x600a9174),(MIX,0x600a8804),(SETUP,0x600a9488)):
            self.write(ctx,u32(vt))
        self.set(SYSTEM,1,0)
        for i in range(28): self.write(ADC+i*8,struct.pack('<H',64))
        for i in range(11):
            self.set(MIX,0x58+i,64); self.set(MIX,0x63+i,64)
            self.set(SETUP,0x2d+i,-1); self.set(SETUP,0x38+i,-1)
        for i in range(5): self.set(SETUP,0x1e+i,64)
        self.set(MIX,0xe2,64)
        for i in range(65):
            default=struct.unpack_from('<I',image,0x686d8+(0x476+i)*16+8)[0]
            self.set(MASTER,i,default)
        self.parameters.clear(); self.notices.clear()

    def instruction(self,uc,address,size,user):
        args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
        if address == 0x600161f6:
            self.transactions.append(args)
            return
        if address == 0x6001a896 and args[1]==1:
            return  # Actual selected-slot getter; other system controls modeled by base.
        if address in (0x6005664c,0x600596d8):
            self.ret()  # Storage singleton boundary; copied slot data remains actual.
        elif address == 0x6000e1c2:
            size=struct.unpack('<I',self.read(uc.reg_read(UC_ARM_REG_SP),4))[0]
            self.saves.append((args[1],args[2],args[3],self.read(args[3],size)))
            self.ret()  # Final nonvolatile storage submission, not hardware writing.
        elif address == 0x6001fb4c:
            self.loads.append(args[1]); return
        elif address == 0x6001a1ce:
            return  # Execute the actual stock getter/clamping setter.
        if address in (0x6000becc,0x6005a034,0x60057ebc,0x010093d6,0x60012340):
            self.ret()  # Mutex, singleton, outgoing parameter/MIDI notifications.
        elif address in (0x6000d400,0x6000d3e2):
            self.notices.append((address,args)); self.ret()
        elif address == 0x010037e8:
            self.write(args[0],struct.pack('<II',0,self.clock&0xffffffff)); self.ret()
        elif address == 0x60010b76:
            self.tick_calls+=1; self.ret()  # Registered stock periodic boundary.
        elif address == self.symbols.get('mx1_master_redraw_original') and not self.real_redraw:
            self.redraw_calls+=1; self.ret()
        elif address == 0x60014a78:
            self.leds[args[0]]=args[1]; self.ret()
        elif address == 0x60014a18:
            self.leds.clear(); self.ret()
        elif address == 0x60054b38:
            raise AssertionError('Stock diagnostic called: '+str(args))
        else:
            super().instruction(uc,address,size,user)

    def set(self,ctx,id,value):
        return self.checked(0x600161f6,ctx,id,value&0xffffffff,0)
    def get(self,ctx,id):
        entry={SYSTEM:0x6001a896,MASTER:0x6001fa48,MIX:0x6001e65e,SETUP:0x6001a1ce}[ctx]
        return signed(self.checked(entry,ctx,id,0)[0])
    def event(self,kind,id,value=0):
        self.write(PACKET,struct.pack('<BBh',kind,id,value))
        # Test the actual registered entry, not a disconnected helper.
        entry=struct.unpack('<I',self.read(0x6000f5d8,4))[0]
        return self.checked(entry,PACKET)
    def tick(self,delta):
        self.clock=(self.clock+delta)&0xffffffff
        entry=struct.unpack('<I',self.read(0x6000f5dc,4))[0]
        return self.checked(entry)
    def active(self): return self.read(STATE+135,1)==b'\x01'
    def enter(self):
        self.event(2,0x17); self.tick(1199); assert not self.active()
        self.tick(1); assert self.active(); self.event(1,0x17)
    def exit(self):
        self.event(2,0x17); assert not self.active(); self.event(1,0x17)


def extract_parameters(original):
    machine=Machine(original)
    result=[]
    display_base=struct.unpack_from('<I',original,0xd194)[0]-0x60000000
    assert display_base == 0x70c04
    for i in range(65):
        parameter_id=machine.call(0x6001f866,0,i)[0]
        assert parameter_id==0x476+i
        offset=0x748c0+i*28
        name=original[offset:].split(b'\0',1)[0].decode('ascii')
        # The named export record embeds the same parameter ID in its header.
        assert struct.unpack_from('<H',original,offset-2)[0]==parameter_id
        lo,hi,default,flags=struct.unpack_from('<4I',original,0x686d8+parameter_id*16)
        fmt=struct.unpack_from('<I',original,display_base+parameter_id*8+4)[0]-0x60000000
        display=original[fmt:].split(b'\0',1)[0].decode('ascii')
        result.append({'n':i+1,'id':hex(parameter_id),'name':name,
            'name_decoded_offset':hex(offset),'name_runtime':hex(0x60000000+offset),
            'stored_range':[lo,hi],'descriptor_default':default,
            'display_format':display,'display_decoded_offset':hex(fmt)})
    return result


def verify_lookup(original,patched):
    results=[]
    for image in (original,patched):
        m=Machine(image); calls=[]
        def hook(uc,address,size,user):
            if address==0x60054b38:
                calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
                from unicorn.arm_const import UC_ARM_REG_LR
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        m.uc.hook_add(UC_HOOK_CODE,hook)
        values=[m.call(0x6001dbd6,0,i)[0] for i in range(0x107)]
        assert values==[i+(0x10f if i<0x73 else 0x114) for i in range(0x107)]
        for i in (0x107,0x7fff,0x8000,0xffff,0xffffffff,0x80000000):
            assert m.call(0x6001dbd6,0,i)[0]==0
        results.append((values,calls))
    assert results[0]==results[1]
    assert original[0x1de08:0x1de0c]==patched[0x1de08:0x1de0c]
    assert original[0x1e5ec:0x1e65e]==patched[0x1e5ec:0x1e65e]
    # Reviewed external references: neighboring initializer reads the literal;
    # two other functions branch to the shared pop. Neither is overwritten.
    refs=Path('analysis/ghidra-main/references.tsv').read_text().splitlines()[1:]
    external=[]
    for row in refs:
        f=row.split('\t')
        try: source,target=int(f[0],16),int(f[1],16)
        except (ValueError,IndexError):continue
        if 0x6001dbd6<target<0x6001e65e and not 0x6001dbd6<=source<0x6001e65e:
            external.append((source,target))
    assert external==[(0x6001dbca,0x6001de08),(0x6001e80a,0x6001e5ec),(0x6001e97c,0x6001e5ec)]
    # Scan literal words as well, rather than relying only on Ghidra xrefs.
    for off in range(0,len(original)-3,2):
        value=struct.unpack_from('<I',original,off)[0]&~1
        if 0x6001dbf4<=value<0x6001de08 or 0x6001de0c<=value<0x6001e5ec:
            assert 0x1dbd6<=off<0x1e65e, ('unexpected interior pointer',hex(off),hex(value))


def verify_hold_traffic(patched,symbols):
    # Physical control packets share this callback with ADC samples and other
    # panel notifications. The clock/periodic boundary remains modeled here.
    m=MasterMachine(patched,symbols)
    m.event(2,0x17)
    for step in range(12):
        m.event(0xb,6,64+(step&1))
        m.event(0x1d,0,0)
        m.tick(100)
        assert m.active()==(step==11), 'Background panel traffic cancelled mastering hold'
    assert '02170000' not in m.original_events, 'Background traffic synthesized a stock MASTERING press'
    assert m.original_events.count('1d000000')==12
    m.event(1,0x17)
    assert m.active()
    m.exit()

    # Background traffic must not turn a short tap into an editor entry or
    # swallow the original bypass action on release.
    m=MasterMachine(patched,symbols)
    m.event(2,0x17);m.event(0xb,6,65);m.tick(300);m.event(1,0x17)
    assert not m.active()
    assert m.original_events[-2:]==['02170000','01170000']

    # Other buttons and either encoder event still cancel the hold and replay
    # the deferred MASTERING press before the stock modified gesture.
    for kind,control in ((2,0x29),(4,0),(4,1),(5,0)):
        m=MasterMachine(patched,symbols)
        m.event(2,0x17);m.event(0xb,6,65);m.event(kind,control,1)
        assert m.original_events[1:3]==['02170000',struct.pack('<BBh',kind,control,1).hex()]
        m.tick(2000)
        assert not m.active()


def verify(original,patched,build):
    verify_lookup(original,patched)
    parameters=extract_parameters(original)
    symbols=build['symbols']
    verify_hold_traffic(patched,symbols)
    m=MasterMachine(patched,symbols)
    # Short tap passes the exact stock down/up pair; long hold has no key
    # actions and does not change master bypass or load another preset.
    m.event(2,0x17);m.tick(300);m.event(1,0x17)
    assert [p[:4] for p in m.original_events[-2:]]==['0217','0117']
    m.key_actions.clear();m.original_events.clear();m.enter()
    assert not m.key_actions and not m.original_events
    assert m.leds[6]==3
    # Eight SELECT/BFX/MFX controls toggle only their assigned parameter.
    # Auto-repeat, duplicate down and release cannot toggle a second time.
    for key,(index,led) in SWITCHES.items():
        before=[m.get(MASTER,i) for i in range(65)]
        m.event(2,key)
        expected=before[:];expected[index]=int(not before[index])
        assert [m.get(MASTER,i) for i in range(65)]==expected
        assert m.leds[led]==expected[index]
        assert ''.join(chr(c[2]) for c in m.characters[-7:-4])==LABELS[index]
        m.event(3,key);m.event(2,key);m.event(1,key)
        assert [m.get(MASTER,i) for i in range(65)]==expected
        m.event(2,key);m.event(1,key)
        assert m.get(MASTER,index)==before[index]
        assert m.leds[led]==before[index]
    # All 22 knobs/faders reach both stored endpoints without mixer changes.
    unmapped={i:m.get(MASTER,i) for i in range(65) if i not in ASSIGN.values()}
    mixer=m.read(0x604f4014,1072)
    for adc,index in ASSIGN.items():
        m.event(0xb,adc,0);m.event(0xb,adc,127);m.event(0xb,adc,0)
        assert m.get(MASTER,index)==0,(adc,index)
        m.event(0xb,adc,127)
        assert m.get(MASTER,index)==parameters[index]['stored_range'][1]
        assert ''.join(chr(c[2]) for c in m.characters[-7:-4])==LABELS[index]
    assert m.read(0x604f4014,1072)==mixer
    assert all(m.get(MASTER,i)==v for i,v in unmapped.items())
    assert m.notices, 'Original transaction notifications did not run'
    # All other buttons/encoders and unused analogue controls are consumed.
    eq=[m.get(MASTER,i) for i in range(65)]
    for id in range(0x55):
        if id in SWITCHES or id==0x17 or 1<=id<=10:continue
        m.event(2,id);m.event(3,id);m.event(1,id)
    for kind in (4,5):
        for id in (0,1):m.event(kind,id,1)
    for adc in set(range(28))-ASSIGN.keys():m.event(0xb,adc,100)
    assert eq==[m.get(MASTER,i) for i in range(65)]
    assert m.read(0x604f4014,1072)==mixer
    assert not m.original_events
    # Button held across exit: release must not invoke scene/store actions.
    m.event(2,0x19);m.exit();m.event(1,0x19);assert not m.original_events
    # Original slot copies and save preparation run unchanged. Storage worker
    # submission is captured, so this establishes RAM retention and correct
    # save payloads, not flash completion or power-cycle survival.
    m=MasterMachine(patched,symbols);m.enter()
    assert m.leds[0x19]==1 and all(m.leds[0x19+i]==0 for i in range(1,10))
    expected=[]
    for slot in range(10):
        m.event(2,slot+1);m.event(1,slot+1)
        assert m.get(SYSTEM,1)==slot and m.get(SETUP,0x24)==0
        assert m.leds[0x19+slot]==1
        assert all(m.leds[0x19+i]==0 for i in range(10) if i!=slot)
        for i in range(65): m.set(MASTER,i,(slot+i)%(parameters[i]['stored_range'][1]+1))
        expected.append([m.get(MASTER,i) for i in range(65)])
    for slot in range(10):
        m.event(2,slot+1);m.event(1,slot+1)
        assert [m.get(MASTER,i) for i in range(65)]==expected[slot]
        assert struct.unpack('<I',m.read(STATE+4,4))[0]==0
        assert all(m.leds[0x29+i]==3 for i in range(11))
        loads=len(m.loads); saves=len(m.saves)
        m.event(2,slot+1);m.event(3,slot+1);m.event(2,slot+1);m.event(1,slot+1)
        assert len(m.loads)==loads and len(m.saves)==saves
    m.exit()
    assert len(m.saves)==20
    assert all(area==0 and group==6 and len(data)==260 for area,group,ptr,data in m.saves)
    assert list(struct.unpack('<65I',m.saves[-1][3]))==expected[9]
    assert [t[2] for t in m.transactions if t[0]==SETUP and t[1]==0x24]==[1,0]*19
    # A displaced control must catch the NEW slot value before editing it.
    m=MasterMachine(patched,symbols);m.enter()
    m.event(0xb,7,0);m.event(0xb,7,127)
    m.event(2,2);m.event(1,2)  # untouched slot contains zero in this fixture
    m.event(0xb,7,120);assert m.get(MASTER,3)==0
    m.event(0xb,7,0);m.event(0xb,7,127);assert m.get(MASTER,3)==24
    # Forced pickup with stock global Jump AND Pass; logical levels are held
    # until crossing, then the unchanged stock fader function applies the move.
    for mode in (0,1):
        for adc in range(7,28,2):
            m=MasterMachine(patched,symbols);m.system_values[5]=mode
            m.enter();m.event(0xb,adc,127);m.exit()
            strip=(adc-7)//2
            m.event(0xb,adc,100);assert m.get(MIX,0x58+strip)==64
            m.event(0xb,adc,63);assert m.get(MIX,0x58+strip)==63
            m.event(0xb,adc,20);assert m.get(MIX,0x58+strip)==20
    # Tone knobs also return through their unchanged stock handlers. A target
    # changed externally during the edit must be picked up at its new value.
    m=MasterMachine(patched,symbols);m.enter();m.event(0xb,6,127)
    m.set(MIX,0x63,40);m.exit()
    m.event(0xb,6,50);assert m.get(MIX,0x63)==40
    m.event(0xb,6,39);assert m.get(MIX,0x63)==39
    # Entering mastering uses pickup for every fader/knob, including ratios.
    for adc,index in ASSIGN.items():
        m=MasterMachine(patched,symbols)
        maximum=parameters[index]['stored_range'][1]
        m.set(MASTER,index,maximum);m.write(ADC+adc*8,struct.pack('<H',0));m.enter()
        m.event(0xb,adc,0);assert m.get(MASTER,index)==maximum
        m.event(0xb,adc,127);m.event(0xb,adc,0);assert m.get(MASTER,index)==0
    # Unsigned timer wrap, guarded pages/modal states, and held modifiers.
    m=MasterMachine(patched,symbols);m.clock=0xffffff00;m.enter();m.exit()
    for page in (0,1,12,14,16):
        m=MasterMachine(patched,symbols);m.write(PAGE,struct.pack('<H',page))
        m.event(2,0x17);m.tick(2000);assert not m.active();m.event(1,0x17)
        assert len(m.original_events)==2
    m=MasterMachine(patched,symbols);m.event(2,0x17);m.event(4,1,1);m.tick(2000)
    assert not m.active() and m.original_events[:2]==['02170000','04010100']
    m.event(1,0x17)
    m=MasterMachine(patched,symbols);m.enter();m.write(MODAL,u32(1));m.tick(1)
    assert not m.active()
    m=MasterMachine(patched,symbols);m.write(0x600b537c,u32(1))
    m.event(2,0x17);m.tick(2000);assert not m.active()
    # Exercise the displaced full-redraw prologue, both branch outcomes, with
    # an empty dirty mask and the fader-only dirty mask.
    m=MasterMachine(patched,symbols);m.real_redraw=True
    for dirty in (0,8):
        m.write(0x605141cc,struct.pack('<H',dirty))
        m.checked(0x6001484a,0x605141cc)
        assert m.read(0x605141cc,2)==bytes(2)
    # Original renderer reports the displaced fader using the existing blink
    # encoding in both global modes. Physical LED timing remains untested.
    for mode in (0,1):
        m=MasterMachine(patched,symbols);m.system_values[5]=mode
        m.enter();m.event(0xb,7,127);m.exit();m.checked(0x60014488)
        assert m.leds[0x29]==3
    return {'status':'pass','patched_app_sha256':sha256(patched),'parameters':parameters,
        'groups':[{'name':name,'status':'pass'} for name in (
          'Reclaimed stock mixer lookup agrees for all 263 valid IDs and invalid boundaries; external literal/shared returns preserved',
          'All 65 mastering names and ranges linked to actual original index instructions',
          'Long hold, short tap, exit and stock modifier gestures; guards and timer wrap',
          'Mastering hold survives continuous ADC samples and unrelated panel notifications; short taps retain the stock action',
          'All 22 assigned controls and eight switches execute stock transactions, correct display/LED selection, and preserve unmapped parameters',
          'Ten step-pad slots use original copy/save preparation; all 65 values survive slot round trips; pickup resets and same-slot presses are inert',
          'Entire edit surface isolated; held-button releases cannot leak after exit',
          'Mastering entry pickup and forced mixer-return pickup in Jump and Pass modes; stock fader blink encoding')],
        'boundaries':['Original parameter lookup, getters, clamping setters, group storage and formatter execute unchanged except compressed mixer ID lookup',
          'Original fader handlers and blink renderer execute; physical ADC/LED protocol and timing are not modeled',
          'Object vtables and parameter defaults are initialized fixtures; RTOS time, periodic callback body, mutex, notifications, MIDI send, storage singleton/submission and final panel I/O are stubbed',
          'No hardware, audio measurements or physical save/restart acceptance; no new sample callback, MPU region or heap reservation']}

if __name__=='__main__':
    original=Path('analysis/container_app_main.bin').read_bytes()
    patched=Path('build/mainline/app_main.mainline.bin').read_bytes()
    build=json.loads(Path('build/mainline/build-report.json').read_text())
    report=verify(original,patched,build)
    Path('build/mainline/mastering-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='parameters'},indent=2))
