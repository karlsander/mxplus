"""Execute original selection/storage and compiled channel surface; no hardware.

RTOS queues/key decoding, SELECT actions, parameter storage, lookup and text
loops execute. Final panel I/O, notifications, periodic scheduling and hardware
are modeled as in mastering_verify. No sends or audio processing are modeled.
"""
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
from arm_machine import Machine
from mastering_verify import MasterMachine, MIX, SYSTEM, SETUP, STATE
from routing_ui_verify import PAGE, BOOT, MODAL, KEYS, CONTEXT, u32
from container_tool import sha256

CSTATE=0x010174d0
KEY_IDS=(0x1b,0x1c,0x1d,0)

class ChannelMachine(MasterMachine):
    def __init__(self,image,symbols):
        self.led_calls=[]
        super().__init__(image,symbols)
        self.set(MIX,0xfb,-1)
        self.transactions.clear()
    def instruction(self,uc,address,size,user):
        args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
        if address in (0x60010516,0x60010538) and 0x29<=args[0]<=0x33:
            self.key_actions.append((address,args[0]))
            return  # Execute unchanged stock SELECT dispatcher and action.
        if address==0x60014a78:
            return  # Execute the patched or original mono helper.
        if address==0x01002ad2:
            color=struct.unpack('<I',self.read(uc.reg_read(UC_ARM_REG_SP),4))[0]
            self.led_calls.append((*args,color))
            self.leds[args[1]]=args[2]
            self.ret(); return  # Final LED driver boundary.
        super().instruction(uc,address,size,user)
    def select(self,strip):
        self.event(2,0x29+strip);self.event(1,0x29+strip)
    def draw(self):
        self.characters.clear()
        self.checked(0x60013356,CONTEXT)
        return ''.join(chr(c[2]) for c in self.characters[-4:])
    def selected(self):
        return self.get(MIX,0xfb)


def lookup_equivalence(original,patched):
    results=[]
    for image in (original,patched):
        m=Machine(image); calls=[]
        def hook(uc,address,size,user):
            if address==0x60054b38:
                calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)))
                uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        m.uc.hook_add(UC_HOOK_CODE,hook)
        values=[m.call(0x6001a40c,0,i)[0] for i in range(141)]
        assert values==list(range(141))
        invalid=(141,142,0x7fff,0x8000,0xffff,0x10000,0xffffffff,0x80000000)
        assert all(m.call(0x6001a40c,0,i)[0]==0 for i in invalid)
        results.append((values,calls))
    assert results[0]==results[1]
    assert original[0x1a654:0x1a658]==patched[0x1a654:0x1a658]==bytes.fromhex('002010bd')
    assert original[0x1a888:0x1a896]==patched[0x1a888:0x1a896]
    refs=Path('analysis/ghidra-main/references.tsv').read_text().splitlines()[1:]
    for row in refs:
        f=row.split('\t')
        try: source,target=int(f[0],16),int(f[1],16)
        except (ValueError,IndexError): continue
        assert not (0x6001a40c<target<0x6001a896 and not 0x6001a40c<=source<0x6001a896), row
    for off in range(0,len(original)-3,2):
        value=struct.unpack_from('<I',original,off)[0]&~1
        if 0x6001a41c<=value<0x6001a654 or 0x6001a658<=value<0x6001a888:
            assert 0x1a40c<=off<0x1a896, ('interior pointer',hex(off),hex(value))
    return dict(name='System lookup matches all 141 IDs and invalid diagnostics; original return and external references preserved',status='pass')


def verify(original,patched,build):
    symbols=build['symbols']; groups=[lookup_equivalence(original,patched)]
    def passed(name,**kw):groups.append(dict(name=name,status='pass',**kw))
    m=ChannelMachine(patched,symbols)
    assert m.selected()==-1
    # Execute actual SELECT presses/releases, not an inferred independent latch.
    for strip in range(11):
        m.select(strip)
        assert m.selected()==strip and m.get(MIX,strip)==1
        for page,key in enumerate(KEY_IDS):
            m.transactions.clear(); before=len(m.original_events)
            m.event(2,key);m.event(3,key);m.event(1,key)
            assert len(m.original_events)==before
            assert m.read(CSTATE+strip,1)==bytes([page])
            assert m.draw()==f'P{page+1}--'
            for delta in (-32768,-1,0,1,32767):m.event(4,1,delta)
            assert len(m.original_events)==before and not m.transactions
            # The stock asynchronous TAP writer must not overwrite page state.
            for led in range(10,14):
                for mode in (0,1,3):
                    m.checked(0x60014a78,led,mode,9)
                    assert m.leds[led]==(led-10==page)
        m.select(strip)
        assert m.selected()==-1 and all(m.get(MIX,i)==0 for i in range(11))
        assert m.draw()!='P4--'
    passed('All 11 stock SELECT toggle paths, four empty pages, signed dial boundaries and asynchronous LED isolation',cases=44)
    # Each channel remembers its page in RAM; no actual mixer/system writes.
    for strip in range(11):
        m.select(strip);m.event(2,KEY_IDS[strip%4]);m.event(1,KEY_IDS[strip%4])
    for strip in range(11):
        m.select(strip);assert m.draw()==f'P{strip%4+1}--'
    passed('Per-channel page memory and switching; no parameter writes from page controls')
    # Held controls cannot leak release or repeat into tempo after deselection.
    for key in KEY_IDS:
        m=ChannelMachine(patched,symbols);m.select(4);m.event(2,key);m.select(4)
        before=len(m.original_events)
        m.event(2,key);m.event(3,key);m.event(1,key)
        assert len(m.original_events)==before
        m.event(2,key);m.event(1,key)
        assert len(m.original_events)==before+2
    passed('Channel-owned duplicate press, release and repeat isolation across deselection')
    m=ChannelMachine(patched,symbols);m.select(4);m.event(2,0x1b)
    m.event(2,0x17);m.tick(2000);assert not m.active()
    m.event(1,0x17);m.event(1,0x1b)
    m.enter();m.exit()
    passed('Held channel-page button blocks mastering entry until released')
    # No-selection pass-through retains all stock tempo/shortcut event packets.
    m=ChannelMachine(patched,symbols)
    for key in KEY_IDS:
        for kind in (2,3,1):m.event(kind,key)
    for delta in (-32768,0,32767):m.event(4,1,delta)
    assert len(m.original_events)==15
    for led in range(0x62):
        m.checked(0x60014a78,led,3,7)
        assert m.led_calls[-1]==(0x60512984,led,3,7,0)
    passed('No-selection tempo packets and all ordinary mono LED calls preserve original ABI')
    m.execute_tempo=True;m.parameters.clear();m.event(4,1,2)
    assert any(a[0]==0x600160ec and a[2:]==(0x1a,2,10) for a in m.parameters)
    m.select(4);m.parameters.clear();m.event(4,1,2)
    assert not any(a[0]==0x600160ec for a in m.parameters)
    for key in range(0x55):
        if key in KEY_IDS or key==0x17 or 0x29<=key<=0x33:continue
        before=len(m.original_events)
        for kind in (2,3,1):m.event(kind,key)
        assert len(m.original_events)==before+3, key
    passed('Only the four tempo buttons are owned; original tempo adjustment requires no selection')
    # Stock-held releases must be cleaned up even if a channel becomes selected.
    for key in KEY_IDS:
        m=ChannelMachine(patched,symbols);m.event(2,key)
        m.set(MIX,0xfb,4);m.set(MIX,4,1)
        m.event(2,key)  # Duplicate down must not steal the stock release.
        m.event(1,key)
        assert not m.read(KEYS+key//8,1)[0]&(1<<(key&7))
        assert m.original_events[-1]==bytes([1,key,0,0]).hex()
    passed('Stock-held keys release normally after selection changes')
    # Main/channel-setting pages own tempo; menus, boot, lock and modal do not.
    for page in range(17):
        m=ChannelMachine(patched,symbols);m.select(4);m.write(PAGE,struct.pack('<H',page))
        before=len(m.original_events);m.event(4,1,1)
        active=5<=page<=10 or page==15
        assert (len(m.original_events)==before)==active
    for guard in (BOOT,MODAL,0x600b537c):
        m=ChannelMachine(patched,symbols);m.select(4);m.write(guard,u32(1))
        before=len(m.original_events);m.event(4,1,1)
        assert len(m.original_events)==before+1
    passed('Normal/channel-setting pages and boot, UI-lock, modal and menu guards')
    # Redraw sees externally applied selections and requests tempo + LED refresh.
    m=ChannelMachine(patched,symbols)
    for strip in (4,7,-1):
        for i in range(11):m.set(MIX,i,i==strip)
        m.set(MIX,0xfb,strip);m.write(CONTEXT,bytes(2))
        m.checked(symbols['mx1_master_redraw'],CONTEXT)
        assert struct.unpack('<H',m.read(CONTEXT,2))[0]&0x500==0x500
    passed('Selection changes through stock parameters refresh right display and LEDs')
    # Mastering takes precedence and does not overwrite the remembered page.
    m=ChannelMachine(patched,symbols);m.select(4);m.event(2,0x1c);m.event(1,0x1c)
    m.enter();saved=m.read(CSTATE,11)
    for key in KEY_IDS:m.event(2,key);m.event(1,key)
    assert m.read(CSTATE,11)==saved
    m.checked(0x60014a78,13,3,9);assert m.leds[13]==3
    m.exit();assert m.draw()=='P2--'
    passed('Mastering priority and channel page restoration')
    # Existing source-routing hold keeps priority; the empty page returns on
    # release without changing its identity. VALUE remains a stock event.
    m=ChannelMachine(patched,symbols);m.select(4)
    m.event(2,0x1c);m.event(1,0x1c);m.event(2,0x29+4)
    m.event(4,1,1);assert m.adjustments[-1]==(4,1)
    m.event(1,0x29+4)
    # Pressing the current SELECT deselects on release, as stock specifies.
    assert m.selected()==-1
    m.select(4);assert m.draw()=='P2--'
    before=len(m.original_events);m.event(4,0,1)
    assert len(m.original_events)==before+1
    passed('Source-routing hold priority, original deselection and VALUE delivery')
    for key in KEY_IDS:
        m=ChannelMachine(patched,symbols);m.select(4);m.event(2,key)
        m.event(2,0x2d);before=len(m.adjustments);m.event(4,1,1)
        assert len(m.adjustments)==before
        m.event(1,key);m.event(4,1,1)
        assert m.adjustments[-1]==(4,1)
        m.event(1,0x2d)
    passed('Channel-owned held keys participate in the source-routing modifier guard')
    # Linked follower SELECTs stay ignored by the stock selection action.
    for leader,follower,setting in ((0,1,3),(2,3,4)):
        m=ChannelMachine(patched,symbols);m.system_values[setting]=1
        m.select(leader);assert m.selected()==leader
        assert m.get(MIX,leader)==m.get(MIX,follower)==1
        m.select(follower);assert m.selected()==leader
        m.event(2,0x1d);m.event(1,0x1d);assert m.draw()=='P3--'
        m.select(leader);assert m.selected()==-1
    # Two physically held SELECTs use original multiple-selection semantics.
    m=ChannelMachine(patched,symbols)
    m.event(2,0x29);m.event(2,0x2d);m.event(1,0x2d);m.event(1,0x29)
    assert m.get(MIX,0)==m.get(MIX,4)==1 and m.selected()==0
    m.event(2,0x1b);m.event(1,0x1b);assert m.draw()=='P1--'
    passed('Original linked and multiple selection retain their current channel')
    return dict(status='pass',candidate_container_sha256=build['container_sha256'],patched_app_sha256=sha256(patched),groups=groups,
        hardware_access=False,limits='Original selection and parameter storage execute; final LEDs, RTOS and audio remain modeled/unexecuted. Physical UI acceptance is pending.')

if __name__=='__main__':
    from container_tool import COMPONENT_BY_NAME,component_unpacked
    original=component_unpacked(Path('inputs/MX1_UPD.original.bin').read_bytes(),COMPONENT_BY_NAME['app_main'])
    result=verify(original,Path('build/mainline/app_main.mainline.bin').read_bytes(),json.loads(Path('build/mainline/build-report.json').read_text()))
    Path('build/mainline/channel-controls-verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
