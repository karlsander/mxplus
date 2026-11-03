#!/usr/bin/env python3
"""Execute original USB-B MIDI instructions with explicit finite FIFO models.

No hardware access. RTOS event delivery, IRQ masks and FIFO readiness/counters
are modeled; the MIDI packetizer, word transfer and cable dispatch run unchanged.
"""
import json
import struct
from pathlib import Path
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_PC, UC_ARM_REG_LR, UC_ARM_REG_SP
from arm_machine import Machine, BASE
from container_tool import sha256
from memory_map import recover
from usb_midi_descriptors import mainline_configuration, validate_configuration


def u32(value):
    return struct.pack('<I',value)


EVENTS = [
    ('note_on','90 3c 64','09 90 3c 64'),
    ('note_off','80 3c 00','08 80 3c 00'),
    ('poly_pressure','a0 3c 40','0a a0 3c 40'),
    ('cc','b0 07 64','0b b0 07 64'),
    ('program','c0 05','0c c0 05 00'),
    ('pressure','d0 40','0d d0 40 00'),
    ('bend','e0 00 40','0e e0 00 40'),
    ('quarter_frame','f1 10','02 f1 10 00'),
    ('song_position','f2 01 02','03 f2 01 02'),
    ('song_select','f3 01','02 f3 01 00'),
    ('tune','f6','05 f6 00 00'),
    ('clock','f8','0f f8 00 00'),
    ('start','fa','0f fa 00 00'),
    ('continue','fb','0f fb 00 00'),
    ('stop','fc','0f fc 00 00'),
    ('active_sensing_filtered_by_stock_packetizer','fe',''),
    ('reset','ff','0f ff 00 00'),
    ('sysex_end_1','f0 41 01 f7','04 f0 41 01 05 f7 00 00'),
    ('sysex_end_2','f0 f7','06 f0 f7 00'),
    ('sysex_end_3','f0 41 f7','07 f0 41 f7'),
    ('sysex_multiframe','f0 41 01 02 03 04 05 06 f7','04 f0 41 01 04 02 03 04 07 05 06 f7'),
]


def cable_events(cable):
    for name,raw,packet in EVENTS:
        expected=bytearray.fromhex(packet)
        for n in range(0,len(expected),4): expected[n] |= cable << 4
        yield name,bytes.fromhex(raw),bytes(expected)


def rx_fifo(image, packets):
    m=Machine(image)
    words=[packets[n:n+4] for n in range(0,len(packets),4)]
    consumed=[]; delivered=[]; waits=[]; selected=[]
    def code(uc,a,size,user):
        if a==0x01003310:  # RTOS wait: one finite packet, then suspend task.
            if waits:
                uc.emu_stop();return
            waits.append(1)
            m.write(uc.reg_read(UC_ARM_REG_R3),u32(1))
            uc.reg_write(UC_ARM_REG_R0,0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a==0x01002580:  # Consumer/listener boundary, no application semantics mocked as success.
            assert uc.reg_read(UC_ARM_REG_R0)==0x600b1b68
            delivered.append(m.read(uc.reg_read(UC_ARM_REG_R1),4))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def read(uc,access,a,size,value,user):
        if a==0x40010088:
            m.write(a,u32(len(consumed)*4 if selected else len(packets)))
        elif a==0x400101cc:
            assert len(consumed)<len(words),'FIFO overread'
            value=words[len(consumed)];consumed.append(value);m.write(a,value)
    def write(uc,access,a,size,value,user):
        if a==0x40010088 and value & 0x8000: selected.append(True)
    m.uc.hook_add(UC_HOOK_CODE,code)
    m.uc.hook_add(UC_HOOK_MEM_READ,read)
    m.uc.hook_add(UC_HOOK_MEM_WRITE,write)
    m.uc.reg_write(UC_ARM_REG_SP,0x2001fff0)
    m.uc.emu_start(0x01000399,0,count=100000,timeout=1_000_000)
    assert m.uc.reg_read(UC_ARM_REG_PC)==0x01003310
    assert b''.join(consumed)==packets and delivered==words
    return len(delivered)


def tx_fifo(image, packets, audio_alternates=(0,0), single=False):
    m=Machine(image);written=[]
    state=0x2001e000; data=0x2001d000
    m.write(state,b'\1'+bytes(3)+u32(0x200040ac)*2+bytes(4))
    m.write(data,packets)
    # Original audio reads identify IF1/IF2 fields in this same register.
    # IF3 (now MIDI AC) and IF4 (MIDI streaming) both stay at alternate zero.
    m.write(0x4001017c,u32((audio_alternates[0]<<16)|(audio_alternates[1]<<12)))
    m.write(0x40010124,u32(4))  # Original bulk IN FIFO readiness bit.
    # Original extracts word capacity from bits 21..31 of this table word.
    m.write(0x40010210,u32(128<<21))
    def code(uc,a,size,user):
        if a in (0x0100e6b0,0x0100e6d0): # IRQ masking/unmasking only
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    def write(uc,access,a,size,value,user):
        if a==0x40010190:
            assert size==4;written.append(u32(value))
    m.uc.hook_add(UC_HOOK_CODE,code);m.uc.hook_add(UC_HOOK_MEM_WRITE,write)
    if single:
        for n in range(0,len(packets),4):
            rc,_=m.call(0x01000566,state,data+n)
            assert rc==1
    else:
        rc,_=m.call(0x010006c4,state,data,len(packets)//4)
        assert rc==(1 if packets else 0)
    assert b''.join(written)==packets
    return len(written)


def cable_dispatch(image, packets):
    m=Machine(image); pending=[packets[i:i+4] for i in range(0,len(packets),4)];seen=[]
    def code(uc,a,size,user):
        if a==0x01001ff0:
            if pending:
                m.write(uc.reg_read(UC_ARM_REG_R1),pending.pop(0)); rc=1
            else: rc=0
            uc.reg_write(UC_ARM_REG_R0,rc);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        elif a==0x010025fe:
            seen.append((uc.reg_read(UC_ARM_REG_R0),m.read(uc.reg_read(UC_ARM_REG_R1),4).hex()))
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    m.uc.hook_add(UC_HOOK_CODE,code)
    m.call(0x010017c2)
    expected=[]
    for n in range(0,len(packets),4):
        p=packets[n:n+4];c=p[0]>>4
        assert c in (0,1)
        expected.append(((0x2000671c,0x20006938)[c],p.hex()))
    assert seen==expected
    return seen


def verify(original,patched,build):
    groups=[]
    def passed(name,**kw):groups.append({'name':name,'status':'pass',**kw})
    # Explicit runtime-to-decoded mapping, compare actual bytes after scatter.
    routines=[(0x01000398,0x9a),(0x01000566,0x11c),(0x010006c4,0x1a2),
              (0x01001394,0x140),(0x010017c2,0x7e),(0x0100e670,0x14)]
    old,new=Machine(original),Machine(patched)
    records=[]
    for a,n in routines:
        op=next(o for o in recover(original)['operations'] if o['kind']=='copy' and o['destination']<=a<a+n<=o['destination']+o['length'])
        offset=op['source']-BASE+a-op['destination']
        assert old.read(a,n)==new.read(a,n)==original[offset:offset+n]
        records.append({'component':'app_main','decoded_offset':hex(offset),'runtime':hex(a),'bytes':n,'sha256':sha256(old.read(a,n))})
    passed('Original MIDI routines remain byte-identical after startup relocation',routines=records)
    samples=[]
    for image in (original,patched):
        m=Machine(image)
        for cable in (0,1):
            for name,raw,expected in cable_events(cable):
                m.write(0x2001c000,raw)
                m.write(0x2001d000,bytes([0xa5])*256)
                rc,_=m.call(0x01001394,0x2001c000,len(raw),0x2001d000,cable)
                assert rc==len(expected)//4,(name,rc)
                assert m.read(0x2001d000,len(expected))==expected,(name,m.read(0x2001d000,len(expected)).hex(),expected.hex())
                assert m.read(0x2001d000+len(expected),4)==bytes([0xa5])*4
                if image is patched:samples.append({'name':name,'cable':cable,'midi_hex':raw.hex(),'usb_hex':expected.hex()})
    passed('Original packetizer emits USB-MIDI 1.0 CIN/cable records',cases=samples)
    stream=b''.join(p for cable in (0,1) for _,_,p in cable_events(cable))
    transfers=[]
    for size in (0,4,8,64,508,512):
        packet=(stream*((size//len(stream))+1))[:size]
        for label,image in (('stock',original),('candidate',patched)):
            transfers.append({'image':label,'bytes':size,'rx_words':rx_fifo(image,packet),'tx_words':tx_fifo(image,packet)})
    passed('Finite bulk FIFO words pass unchanged in both directions',cases=transfers)
    modes=[]
    for out_alt in (0,1,2):
        for in_alt in (0,1,2):
            for image in (original,patched):
                for single in (False,True):
                    assert tx_fifo(image,stream,(out_alt,in_alt),single)==len(stream)//4
            modes.append([out_alt,in_alt])
    passed('Single and batch bulk sends remain independent of audio alternates',audio_alternates=modes,
           midi_alternates='IF3/IF4 both zero; removed vendor interrupt alternate is never selected')
    assert cable_dispatch(original,stream)==cable_dispatch(patched,stream)
    passed('Original USB-B cable dispatcher selects the existing two destinations',cable_0='0x2000671c (source ID 1)',cable_1='0x20006938 (source ID 2)',records=len(stream)//4)
    passed('Separate USB-MIDI descriptor graph has two connected cable pairs',**validate_configuration(mainline_configuration()))
    return {'status':'pass','original_app_sha256':sha256(original),'patched_app_sha256':sha256(patched),
            'candidate_container_sha256':build['container_sha256'],'groups':groups,'hardware_access':False,
            'stubs':['RTOS event wait delivers one packet then suspends','RX listener records words at 01002580; downstream queue pop supplies those records at 01001ff0',
                     'Routing consumer 010025fe records destination and event; musical/clock settings are not exercised',
                     '0100e6b0/0100e6d0 interrupt masks stubbed; finite FIFO counters and bulk IN readiness supplied'],
            'limits':['No USB host enumeration, physical FIFO/DMA, timing, sustained duplex or reconnect validation',
                      'Transfer fixtures are valid complete four-byte packets; malformed host traffic and full queue recovery are not certified',
                      'Raw-byte packetizer tested with complete messages; transport carries prepacketized records',
                      'High-speed only; unchanged full-speed vendor configuration has no MIDI endpoints']}


if __name__=='__main__':
    original=Path('analysis/container_app_main.bin').read_bytes()
    patched=Path('build/mainline/app_main.mainline.bin').read_bytes()
    build=json.loads(Path('build/mainline/build-report.json').read_text())
    report=verify(original,patched,build)
    Path('build/mainline/midi-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'groups':[g['name'] for g in report['groups']]}))
