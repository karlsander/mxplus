#!/usr/bin/env python3
"""Recover the MX-1 applications' scatter-loading map from startup instructions.

The compressed application's load address is NOT every function's runtime
address. Both cores copy Thumb code into private SRAM before entering C++.
This script resolves literal loads and calls in the startup stub, not a guessed
list of addresses. Capstone is an independent check of the original instructions.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_MCLASS

BASE = 0x60000000

def recover(data):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS)
    registers = {}
    operations = []
    instructions = []
    entry = None
    for ins in md.disasm(data[:0x80], BASE):
        instructions.append(f'{ins.address:08x}: {ins.bytes.hex():10s} {ins.mnemonic} {ins.op_str}')
        if ins.mnemonic == 'ldr' and '[pc,' in ins.op_str:
            word = int.from_bytes(ins.bytes, 'little')
            if word & 0xf800 != 0x4800:
                raise ValueError('unexpected startup literal instruction')
            register = (word >> 8) & 7
            pool = ((ins.address + 4) & ~3) + (word & 255) * 4
            registers[register] = struct.unpack_from('<I', data, pool-BASE)[0]
        elif ins.mnemonic == 'bl':
            target = int(ins.op_str.removeprefix('#'), 16)
            if target not in (BASE+0x80, BASE+0x9e):
                raise ValueError(f'unknown startup operation {target:x}')
            operation = {'call': ins.address, 'kind': 'copy' if target == BASE+0x80 else 'zero',
                         'destination': registers[0], 'length': registers[1]}
            if operation['kind'] == 'copy':
                operation['source'] = registers[2]
                off = registers[2]-BASE
                if not 0 <= off <= len(data) or off+registers[1] > len(data):
                    raise ValueError('copy exceeds supplied decompressed image')
            operations.append(operation)
        elif ins.mnemonic == 'bx' and ins.op_str == 'r0':
            entry = registers[0]
    if len(operations) != 13 or entry is None or not entry & 1:
        raise ValueError('unrecognized startup layout')
    hot = operations[0]
    return {'sha256':hashlib.sha256(data).hexdigest(), 'load_base':BASE,
            'file_size':len(data), 'runtime_entry':entry,
            'resident_code_end':hot['source'], 'operations':operations,
            'startup_disassembly':instructions}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('image',type=Path)
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args()
    result=recover(a.image.read_bytes())
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    lines=[f"entry\t{result['runtime_entry']:x}\t0\t0",
           f"resident_end\t{result['resident_code_end']:x}\t0\t0"]
    for op in result['operations']:
        if op['length']:
            lines.append(f"{op['kind']}\t{op['destination']:x}\t{op['length']:x}\t{op.get('source',0):x}")
    a.output.with_suffix('.tsv').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='startup_disassembly'},indent=2))

if __name__=='__main__':main()
