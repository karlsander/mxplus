"""Guarded main-application patch and scatter helpers."""
import struct
from container_tool import FormatError
from memory_map import recover

def exact_patch(image,offset,expected,replacement,changes,label):
    if image[offset:offset+len(expected)]!=expected or len(expected)!=len(replacement):
        raise FormatError(f'{label}: original bytes do not match')
    image[offset:offset+len(expected)]=replacement
    changes.append({'label':label,'file_offset':offset,'runtime_address':0x60000000+offset,
                    'original':expected.hex(),'replacement':replacement.hex()})

def inject(original,blob):
    m=recover(original);hot=m['operations'][0]
    if hot!={'call':0x6000000e,'kind':'copy','destination':0x01000300,'length':0xf3a4,'source':0x600d0b8c}:
        raise FormatError('unexpected main application scatter layout')
    if len(blob)%4 or 0x0100f6a4+len(blob)>0x01010000:raise FormatError('main extension exceeds private SRAM gap')
    cut=0xdff30
    result=bytearray(original[:cut]+blob+original[cut:])
    struct.pack_into('<I',result,0xe8,hot['length']+len(blob))
    updates=[{'offset':0xe8,'before':hot['length'],'after':hot['length']+len(blob)}]
    for p in (0x100,0x114,0x128,0x13c,0x150):
        old=struct.unpack_from('<I',original,p)[0]
        if old<0x60000000+cut:raise FormatError('unexpected main initialized-data source')
        struct.pack_into('<I',result,p,old+len(blob))
        updates.append({'offset':p,'before':old,'after':old+len(blob)})
    recover(result)
    return result,{'insert_offset':cut,'runtime_address':0x0100f6a4,
                   'insert_length':len(blob),'startup_updates':updates}
