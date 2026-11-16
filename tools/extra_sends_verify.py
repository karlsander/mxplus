"""Offline numerical and original-uploader checks for the independent sends.

The numerical model implements only the A/FE subset emitted by these kernels.
It models RAW32 truncation and parallel reads, not delay RAM, DMA or deadlines.
The original ARM uploader runs unchanged; only its bulk DMA is a byte copy.
"""
import json
import math
from pathlib import Path
import random
import struct

from container_tool import sha256
from esc2_disassemble import logical_image, decode, binding_tail
from extra_sends_dsp import mixer, output
from routing_audio_extract import reconstruct


def quantize(value):
    sign=-1 if value<0 else 1
    for exponent in range(4):
        scale=2.0**(32-4*exponent)
        mantissa=int(abs(value)*scale)
        if mantissa<0x20000000:
            return sign*mantissa/scale
    return sign*0x1fffffff/scale


def immediate(raw):
    return (-1 if raw&0x8000 else 1)*(raw&0x1fff)*2.0**(16-32+4*((raw>>13)&3))


def execute(program, memory):
    """Decode bytes independently of the emitter, with packet-entry registers."""
    templates={0x0900:(1,0),0x1500:(2,0),0x0c00:(0,1),0x1e00:(0,2),
               0x1800:(1,1),0x2e00:(2,1),0x3400:(1,2),0x5f00:(2,2)}
    regs=[0.0]*8
    for packet in decode(program,0):
        words=packet.words
        if words[0] in (0x0a02,0x0b02,0x0b03,1):
            continue # Mode markers and externally checked return/jump framing.
        arithmetic, transfers=templates[words[0]&~31]
        old=regs[:]
        for word in words[1:1+arithmetic]:
            d=word>>12;op=(word>>9)&7;x=(word>>6)&7;y=word&15
            rhs=immediate(words[-1]) if word&0x30 else old[y&7]*(-1 if y&8 else 1)
            if op==0:
                value=rhs if x==1 else old[d]+rhs
                assert x in (1,6,7)
            elif op==2: value=old[x]*rhs
            elif op==3: value=old[d]+old[x]*rhs
            elif op==6: value=old[x]+rhs
            elif op==7: value=rhs-old[x]
            else: raise AssertionError(hex(word))
            regs[d]=quantize(value)
        literals=1+arithmetic+transfers
        for word in words[1+arithmetic:literals]:
            assert word&0xfe0==0xfe0 and (word&31)%2==0
            register=word>>12;address=words[literals+(word&31)//2]
            if register<8: regs[register]=memory.get(address,0.0)
            else: memory[address]=old[register-8]
    return memory


def numerical():
    rng=random.Random(0x4d5831)
    cases=0
    for post in (0,1):
        for mode in range(3):
            for valid in (0,1):
                for enabled in (0,1):
                    for _ in range(20):
                        m={0xc096:post,0xc097:int(mode==1),0xc098:int(mode==2),
                           0xc099:enabled,0xc09a:valid,0xc051:rng.random()}
                        alt=[0.,0.]; fx=[0.,0.]
                        for ch in range(11):
                            source=0xa128+(ch if ch<4 else ch*2-4)
                            l=rng.uniform(-.3,.3);r=l if ch<4 else rng.uniform(-.3,.3)
                            fader=rng.random();mute=rng.choice((0,1))
                            gain_a=rng.choice((0.,1.,rng.random()))
                            gain_f=rng.choice((0.,1.,rng.random()))
                            pan=[rng.random(),rng.random()]
                            m.update({source:l,0xc038+ch:fader,0xc022+ch:mute,
                                      0xc080+ch:gain_a,0xc08b+ch:gain_f,
                                      0xc001+ch:pan[0],0xc00c+ch:pan[1]})
                            if ch>=4:m[source+1]=r
                            factor=fader*mute if post else 1
                            for side,sample in enumerate((l,r)):
                                alt[side]+=sample*factor*gain_a
                                fx[side]+=sample*factor*pan[side]*gain_f
                        execute(mixer().encode(),m)
                        for side in (0,1):
                            assert math.isclose(m[0x20b0+side],fx[side],abs_tol=2e-6)
                            assert math.isclose(m[0x20b2+side],alt[side],abs_tol=2e-6)
                        values={a:rng.uniform(-1,1) for a in (*range(0x2000,0x2008),*range(0xa13a,0xa140))}
                        m.update(values);before=dict(m)
                        execute(output().encode(),m)
                        for side in (0,1):
                            dry=before[0x2006+side];master=before[0x2000+side]
                            expected=before[0x2004+side]+dry+(master-dry)*before[0xc051]*valid+before[0x2002+side]*enabled
                            assert math.isclose(m[0xa13a+side],expected,abs_tol=3e-6)
                            assert m[0x4001+side]==dry
                            aux=(sum(before[0xa13c+i] for i in (0,1)) if side==0 else sum(alt))/2 if mode==1 else before[0xa13c+side]
                            phones=alt[side] if mode==2 else before[0xa13e+side]
                            assert math.isclose(m[0xa13c+side],aux,abs_tol=3e-6)
                            assert math.isclose(m[0xa13e+side],phones,abs_tol=3e-6)
                            # Internal return cannot feed back into either send
                            # sum, MASTER input, or any strip input/state.
                            assert m[0x20b0+side]==before[0x20b0+side]
                            assert m[0x2006+side]==before[0x2006+side]
                        cases+=1
    return dict(name='Numerical send mixing, pre/post mute/fader, pan isolation, destinations and wet-return placement',status='pass',cases=cases)


def verify(original,patched,build):
    from extra_sends_arm_verify import verify as arm_verify
    groups=[numerical(), arm_verify(original,patched,build)]
    table=build['symbols']['mx1_sends_programs']
    _,old=reconstruct()
    report,new=reconstruct((0x600ba008,table),(18,20),image=patched)
    assert old[0]==new[0], 'DSP0 normal graph changed'
    logical=logical_image(new[1]);baseline=logical_image(old[1])
    expected=bytearray(baseline)
    for at,before,after in ((0x1ac4,'0b0200f80001','0b0300801000'),
                            (0x1ace,'3e070fe01fe27fe420002002c050','0b03008014000001000100010001')):
        assert expected[at:at+len(bytes.fromhex(before))]==bytes.fromhex(before)
        expected[at:at+len(bytes.fromhex(before))]=bytes.fromhex(after)
    for at,kernel in ((0x2000,mixer()),(0x2800,output())):
        data=kernel.encode()
        assert not any(expected[at:at+len(data)])
        expected[at:at+len(data)]=data
    assert logical==expected
    groups.append(dict(name='Original ARM uploader installs both kernels and only two guarded normal-graph branches',status='pass',chunks=38,modeled=report['modeled']))
    cases=0
    for algorithm in range(20):
        for slot in (0,1):
            table=(0xcaaac,0xcab4c)[slot]
            descriptor=struct.unpack_from('<I',original,table+algorithm*4)[0]
            off,length,_=struct.unpack_from('<III',original,descriptor-0x60000000)
            _,a=reconstruct((0x600ba008,descriptor),(0,1))
            _,b=reconstruct((0x600ba008,descriptor),(0,1),image=patched)
            x=logical_image(a[1]);y=logical_image(b[1]);want=bytearray(x)
            if slot==1 and algorithm in (1,3,4):
                refs=[]
                for p in decode(x[off:off+length],off):
                    for i,j in binding_tail(p):
                        if p.words[j] in (0x2006,0x2007):
                            assert p.words[i]>>12<8
                            refs.append(p.offset+j*2)
                            struct.pack_into('>H',want,p.offset+j*2,0x20b0+p.words[j]-0x2006)
                assert len(refs)==(6 if algorithm==1 else 2)
                assert y[off+length-26:off+length-16]==bytes.fromhex('1e050fe01fe201000101')
            assert y==want,(algorithm,slot)
            cases+=1
    groups.append(dict(name='All MASTER programs unchanged; only three internal algorithms receive independent input operands',status='pass',upload_cases=cases))
    descriptors=[]
    for algorithm in range(20):
        for slot,table in enumerate((0xcaafc,0xcab9c)):
            pointer=struct.unpack_from('<I',original,table+algorithm*4)[0]-0x60000000
            offset,length,source=struct.unpack_from('<III',original,pointer)
            assert offset==(32 if slot==0 else 312)
            assert offset+length<=(312 if slot==0 else 576)
            data=original[source-0x60000000:source-0x60000000+length]
            assert patched[source-0x60000000:source-0x60000000+length]==data
            bases=[a&0x7fffffff for a,b in struct.iter_unpack('<II',data) if a]
            assert all((0x491500<=a<0x637300 if slot==0 else 0x637300<=a<=0x7fffff) for a in bases)
            descriptors.append(dict(algorithm=algorithm,slot=slot,first_entry=offset//8,
                                    entries=length//8,encoded_bases=[hex(a) for a in bases]))
    groups.append(dict(name='Original delay descriptors use disjoint slot entries and encoded address bands; payloads preserved',
                       status='pass',cases=40,descriptors=descriptors,
                       limit='Encoded address bands are static evidence, not complete execution of dynamic delay addresses or physical RAM.'))
    return dict(status='pass',candidate_container_sha256=build['container_sha256'],patched_app_sha256=sha256(patched),groups=groups,hardware_access=False,
                limits=['Numerical A/FE model covers the new kernels, not complete factory effect algorithms or delay RAM.',
                        'Uploader DMA and command-register storage are modeled; physical timing and audio are untested.'])


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    original=(root/'analysis/container_app_main.bin').read_bytes()
    candidate=root/'build/mainline'
    report=verify(original,(candidate/'app_main.mainline.bin').read_bytes(),json.loads((candidate/'build-report.json').read_text()))
    (candidate/'extra-sends-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
