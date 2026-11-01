#!/usr/bin/env python3
"""Execute original and injected MX-1 ARM routines; no hardware emulation claim.

Verifies startup scatter copies, classifier hook/trampoline, complete original
configuration parsing, original policy-input construction, and selection.
USB controllers, audio DMA, DSP clocks, streaming and UI are not emulated here.
"""
import argparse
import json
import struct
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UcError
from unicorn.arm_const import (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,
                              UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
                              UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11,
                              UC_ARM_REG_SP,UC_ARM_REG_LR,UC_ARM_REG_PC)
from container_tool import COMPONENT_BY_NAME,component_unpacked,sha256
from memory_map import recover

BASE=0x60000000
RETURN=0x0fff0000
BUF=0x20010000
OUT=0x20012000
PORT=0x20014000
DEVICE=0x20015000
INFO=0x20016000

class Machine:
    def __init__(self,image,scatter=True):
        self.image=image
        self.uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
        for address,size in [(BASE,0x800000),(0x01000000,0x30000),(0x20000000,0x20000),
                             (0x40000000,0x50000),(RETURN,0x1000)]:
            self.uc.mem_map(address,size)
        self.uc.mem_write(BASE,image)
        if scatter:
            for op in recover(image)['operations']:
                if not op['length']:continue
                content=(image[op['source']-BASE:op['source']-BASE+op['length']]
                         if op['kind']=='copy' else bytes(op['length']))
                self.uc.mem_write(op['destination'],content)
    def read(self,address,size):return bytes(self.uc.mem_read(address,size))
    def write(self,address,content):self.uc.mem_write(address,bytes(content))
    def call(self,address,*args,count=100000,measure=False):
        u=self.uc
        u.reg_write(UC_ARM_REG_SP,0x2001fff0);u.reg_write(UC_ARM_REG_LR,RETURN|1)
        for reg,val in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,val)
        instructions=[0]
        handle=None
        if measure:
            def on_instruction(*_):instructions[0]+=1
            handle=u.hook_add(UC_HOOK_CODE,on_instruction)
        try:u.emu_start(address|1,RETURN,timeout=1_000_000,count=count)
        finally:
            if handle is not None:u.hook_del(handle)
        if u.reg_read(UC_ARM_REG_PC)!=RETURN:raise AssertionError(f'function did not return, pc={u.reg_read(UC_ARM_REG_PC):x}')
        if u.reg_read(UC_ARM_REG_SP)!=0x2001fff0:raise AssertionError('stack pointer not restored')
        return u.reg_read(UC_ARM_REG_R0),instructions[0]
    def classify(self,interface,end=None):
        self.write(BUF,interface)
        self.write(OUT,bytes([0xa5])*32)
        ret,count=self.call(0x6000a11e,OUT,BUF,BUF+(len(interface) if end is None else end),measure=True)
        if self.read(OUT+18,14)!=bytes([0xa5])*14:raise AssertionError('classifier wrote beyond 18-byte record')
        return self.read(OUT,18),count
    def pipeline(self,configuration,policy_address,vid=0x1234,high_speed=True):
        self.write(BUF,configuration);self.write(PORT,bytes(0x400));self.write(DEVICE,bytes(0x100))
        self.write(DEVICE+0x10,struct.pack('<HHH',vid,0x5678,0x100))
        self.write(DEVICE+0x58,struct.pack('<H',0x400 if high_speed else 0x200))
        rc,_=self.call(0x6000a1e2,PORT+0x64,BUF)
        if rc:raise AssertionError(f'original config parser failed {rc:x}')
        # This original routine transfers the parsed records into the actual
        # policy ABI and zeroes the 18-byte selection output.
        self.call(0x60008580,INFO,OUT,DEVICE,PORT)
        _,n=self.call(policy_address,INFO,OUT,measure=True)
        return {'selection':list(struct.unpack('<9H',self.read(OUT,18))),
                'in_alternates':self.read(PORT+0x6e,1)[0],
                'out_alternates':self.read(PORT+0x6f,1)[0],
                'policy_instructions':n,'info_hex':self.read(INFO,0x7c).hex()}

def stream(number,direction,rate=48000,**changes):
    """Synthetic UAC1 HS interval-1 research fixture, not a physical device dump."""
    v=dict(cls=1,protocol=0,subframe=4,bits=24,channels=2,interval=1,alt=1,
           rate_count=1,format_tag=1,endpoints=1,maxpacket=112,feedback=False,
           endpoint=None,attributes=None)
    v.update(changes)
    itf0=bytes([9,4,number,0,0,v['cls'],2,v['protocol'],0])
    itf1=bytes([9,4,number,v['alt'],v['endpoints'],v['cls'],2,v['protocol'],0])
    general=bytes([7,0x24,1,1,1,v['format_tag']&255,v['format_tag']>>8])
    format=bytes([11,0x24,2,1,v['channels'],v['subframe'],v['bits'],v['rate_count']])+rate.to_bytes(3,'little')
    if v['rate_count']==2:format=bytes([14])+format[1:]+(96000).to_bytes(3,'little')
    endpoint=v['endpoint'] if v['endpoint'] is not None else (0x81 if direction else 1)
    attributes=v['attributes'] if v['attributes'] is not None else (0x25 if direction else 5)
    ep=bytes([9,5,endpoint,attributes])+struct.pack('<H',v['maxpacket'])+bytes([v['interval'],0,0])
    if v['feedback']:ep+=bytes([7,5,0x82,0x11,4,0,1])
    return itf0+itf1+general+format+ep

def configuration(rate=48000,**changes):
    # The classifier ignores AudioControl; the test deliberately isolates the
    # AS path and does not claim this synthetic configuration is USB certified.
    ac=bytes([9,4,0,0,0,1,1,0,0])
    contents=ac+stream(1,False,rate,**changes)+stream(2,True,rate,**changes)
    return bytes([9,2])+struct.pack('<H',9+len(contents))+bytes([3,1,0,0xc0,0])+contents

def interfaces(config):
    pos=0
    while pos<len(config):
        n=config[pos]
        if n<2 or pos+n>len(config):raise ValueError('bad test descriptor')
        if config[pos+1]==4:yield pos
        pos+=n

def verify(original,patched,main_image,build_report):
    results=[]
    def passed(name,**details):results.append(dict(name=name,status='pass',**details))
    policy=build_report['symbols']['mx1_uac1_policy']
    a,b=Machine(original),Machine(patched)
    # Execute both full startup stubs, including their original memory clears.
    startups=[]
    for image in (original,patched):
        m=Machine(image,scatter=False)
        m.uc.reg_write(UC_ARM_REG_SP,0x2001fff0)
        m.uc.emu_start(BASE|1,BASE+0x7e,timeout=2_000_000,count=2_000_000)
        assert m.uc.reg_read(UC_ARM_REG_PC)==BASE+0x7e
        for op in recover(image)['operations']:
            if op['kind']=='copy' and op['length']:
                assert m.read(op['destination'],op['length'])==image[op['source']-BASE:op['source']-BASE+op['length']]
        startups.append(m)
    for op in recover(original)['operations']:
        if op['kind']=='copy' and op['destination']!=0x01000300 and op['length']:
            assert startups[0].read(op['destination'],op['length'])==startups[1].read(op['destination'],op['length'])
    passed('Original ARM startup loads extension and preserves all existing initialized data',
           extension_bytes=build_report['scatter_extension']['insert_length'])
    # Actual descriptor fixture from the firmware: every Roland audio/MIDI alt.
    config=main_image[0xb499c:0xb499c+0x102]
    comparisons=[]
    for off in interfaces(config):
        ra,na=a.classify(config[off:]);rb,nb=b.classify(config[off:])
        assert ra==rb,(off,ra.hex(),rb.hex())
        comparisons.append({'offset':off,'original_instructions':na,'patched_instructions':nb})
    passed('Original Roland descriptor classifier behavior preserved through trampoline',
           interfaces=len(comparisons),instruction_counts=comparisons)
    # End-to-end original parser -> original ABI builder -> policy hook.
    samples=[]
    for rate in (44100,48000,96000):
        cfg=configuration(rate)
        old=a.pipeline(cfg,0x60007bf9)
        new=b.pipeline(cfg,policy)
        assert old['selection']==[0]*9 and old['in_alternates']==old['out_alternates']==0
        assert new['selection']==[1,1,0,1,1,0,0,0,0],new
        assert new['in_alternates']==new['out_alternates']==2
        samples.append({'rate':rate,'original':old,'modified':new})
    passed('Synthetic generic UAC1 profile reaches selection using original parser and ABI builder',cases=samples)
    rejects=[]
    for label,kw in [('packed24',{'subframe':3}),('16bit',{'subframe':2,'bits':16}),
                     ('32significantbits',{'bits':32}),('mono',{'channels':1}),
                     ('44channels',{'channels':44}),('UAC2',{'protocol':0x20}),
                     ('interval4',{'interval':4}),('multi_rate',{'rate_count':2}),
                     ('continuous_rate',{'rate_count':0}),('float_pcm',{'format_tag':3}),
                     ('explicit_feedback',{'feedback':True,'endpoints':2}),
                     ('tiny_packet',{'maxpacket':1}),('high_bandwidth',{'maxpacket':0x880}),
                     ('endpoint_zero',{'endpoint':0}),('reserved_endpoint_address',{'endpoint':0x71}),
                     ('reserved_endpoint_usage',{'attributes':0x35}),
                     ('adaptive_endpoint',{'attributes':9}),
                     ('alt5',{'alt':5})]:
        r=b.pipeline(configuration(**kw),policy)
        assert r['selection']==[0]*9,(label,r)
        rejects.append(label)
    r=b.pipeline(configuration(rate=88200),policy);assert r['selection']==[0]*9
    rejects.append('unsupported88200')
    r=b.pipeline(configuration(),policy,high_speed=False);assert r['selection']==[0]*9
    rejects.append('full_speed')
    passed('Unsupported formats, rates, endpoint layouts and speeds stay rejected',cases=rejects)
    # Different IN/OUT sample rate cannot accidentally select a stream.
    contents=stream(1,False,48000)+stream(2,True,96000)
    mismatch=bytes([9,2])+struct.pack('<H',len(contents)+9)+bytes([2,1,0,0xc0,0])+contents
    assert b.pipeline(mismatch,policy)['selection']==[0]*9
    passed('Mismatched IN and OUT rates rejected')
    contents=stream(1,False,cls=0xff,protocol=2,bits=32,interval=4)+stream(2,True,cls=0xff,protocol=1,bits=32,interval=4)
    vendor=bytes([9,2])+struct.pack('<H',len(contents)+9)+bytes([2,1,0,0xc0,0])+contents
    assert b.pipeline(vendor,policy)['selection']==[0]*9
    passed('Non-Roland vendor descriptors cannot bypass strict generic-profile validation')
    # The stock parser indexes streams by alternate number, not by interface:
    # later interfaces can overwrite the same alt1 slot. Both alt0 and alt1
    # must therefore originate from a validated standard pair.
    malformed_layouts={
        'later_vendor_overwrites_standard_alt1':
            stream(1,False)[9:]+stream(2,True)[9:]+
            stream(3,False,cls=0xff,protocol=2,bits=32,interval=4)[9:]+
            stream(4,True,cls=0xff,protocol=1,bits=32,interval=4)[9:],
        'duplicate_standard_alt1_without_alt0':
            stream(1,False)[9:]+stream(2,True)[9:]+
            stream(3,False)[9:]+stream(4,True)[9:],
        'earlier_vendor_followed_by_standard_alt1_without_alt0':
            stream(1,False,cls=0xff,protocol=2,bits=32,interval=4)[9:]+
            stream(2,True,cls=0xff,protocol=1,bits=32,interval=4)[9:]+
            stream(3,False)[9:]+stream(4,True)[9:],
    }
    for label,contents in malformed_layouts.items():
        cfg=bytes([9,2])+struct.pack('<H',len(contents)+9)+bytes([4,1,0,0xc0,0])+contents
        result=b.pipeline(cfg,policy)
        assert result['selection']==[0]*9,(label,result)
    passed('Origin markers require both standard alt0 and alt1 and track later overwrites',
           cases=list(malformed_layouts))
    # Exercise actual policy equivalence on a real MX-1 descriptor tree.
    old=a.pipeline(config,0x60007bf9,vid=0x0582)
    new=b.pipeline(config,policy,vid=0x0582)
    assert old['selection']==new['selection']
    assert old['in_alternates']==new['in_alternates'] and old['out_alternates']==new['out_alternates']
    passed('Original Roland full parser and policy output unchanged',selection=old['selection'])
    # Bounded malformed-descriptor paths in the NEW classifier only. The old
    # surrounding Roland configuration parser is not asserted to be hardened.
    bads=[b'',b'\x09',bytes([9,4,1,1,1,1,2,0,0])+b'\0\x24',
          bytes([9,4,1,1,1,1,2,0,0])+b'\xff\x24',
          stream(1,False)[9:-1]]
    for fixture in bads:
        rec,_=b.classify(fixture);assert rec[0]==0
    passed('New classifier rejects truncated and zero-length descriptor chains',cases=len(bads))
    # Sentinel values exercise all AAPCS callee-saved registers, including r9.
    # Machine.call additionally checks restored SP and the actual return PC.
    saved_regs=(UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6,UC_ARM_REG_R7,
                UC_ARM_REG_R8,UC_ARM_REG_R9,UC_ARM_REG_R10,UC_ARM_REG_R11)
    sentinels=[0x13450000+i*0x100 for i in range(len(saved_regs))]
    abi_cases=[]
    def check_preserved(label,invoke):
        for reg,value in zip(saved_regs,sentinels):b.uc.reg_write(reg,value)
        invoke()
        assert [b.uc.reg_read(reg) for reg in saved_regs]==sentinels,label
        abi_cases.append(label)
    for label,fixture in [('standard_alt1',stream(1,False)[9:]),
                          ('standard_alt0',stream(1,False)),
                          ('unsupported_format',stream(1,False,bits=16)),
                          ('vendor_class_trampoline',stream(1,False,cls=0xff,protocol=2))]:
        check_preserved(label,lambda fixture=fixture:b.classify(fixture))
    b.write(BUF,configuration())
    check_preserved('configuration_parser_trampoline',
                    lambda:b.call(0x6000a1e2,PORT+0x64,BUF))
    for vid in (0x1234,0x0582):
        b.pipeline(configuration() if vid==0x1234 else config,policy,vid=vid)
        check_preserved(f'policy_vid_{vid:04x}',lambda:b.call(policy,INFO,OUT))
    passed('New hooks preserve AAPCS r4-r11, stack pointer and return address',cases=abi_cases)
    return {'status':'pass','groups':results,'original_app_sha256':sha256(original),
            'patched_app_sha256':sha256(patched),
            'scope':'Original ARM startup/parser/policy plus compiled extension executed in Unicorn; no USB bus, DSP, DMA or physical device.',
            'instruction_measurement':'Executed instruction counts only; not cycle counts or real-time performance predictions.'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware',type=Path);p.add_argument('--build',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();raw=a.firmware.read_bytes()
    r=verify(component_unpacked(raw,COMPONENT_BY_NAME['app_usb']),
             (a.build/'app_usb.uac1_probe.bin').read_bytes(),
             component_unpacked(raw,COMPONENT_BY_NAME['app_main']),
             json.loads((a.build/'build-report.json').read_text()))
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'groups':[x['name'] for x in r['groups']]},indent=2))
if __name__=='__main__':main()
