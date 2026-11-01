#!/usr/bin/env python3
"""Disassemble chosen main-app runtime bytes with relocated literal annotations."""
import argparse,json,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_ARM,CS_MODE_THUMB,CS_MODE_MCLASS
from capstone.arm import ARM_OP_MEM,ARM_REG_PC

ROOT=Path(__file__).resolve().parents[2]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('address',type=lambda v:int(v,16))
    parser.add_argument('length',type=lambda v:int(v,0))
    args=parser.parse_args()
    blob=(ROOT/'analysis/container_app_main.bin').read_bytes()
    mapping=json.loads((ROOT/'analysis/map-main.json').read_text())
    def read(address,length):
        if 0x60000000<=address<=0x60000000+len(blob)-length:
            return blob[address-0x60000000:address-0x60000000+length]
        for op in mapping['operations']:
            if op['kind']=='copy' and op['destination']<=address<=op['destination']+op['length']-length:
                off=op['source']-0x60000000+address-op['destination']
                return blob[off:off+length]
        raise ValueError(f'unmapped {address:08x}')
    md=Cs(CS_ARCH_ARM,CS_MODE_THUMB|CS_MODE_MCLASS);md.detail=True
    for ins in md.disasm(read(args.address,args.length),args.address):
        annotation=''
        for op in ins.operands:
            if op.type==ARM_OP_MEM and op.mem.base==ARM_REG_PC:
                address=((ins.address+4)&~3)+op.mem.disp
                try:
                    value=struct.unpack('<I',read(address,4))[0]
                    annotation=f' ; [{address:08x}]=0x{value:08x}'
                except ValueError:
                    pass
        print(f'{ins.address:08x}  {ins.bytes.hex():10s} {ins.mnemonic:8s} {ins.op_str}{annotation}')

if __name__=='__main__':main()
