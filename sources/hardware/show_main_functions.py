#!/usr/bin/env python3
"""Select Ghidra main-app functions and resolve named literal-pool words."""
import argparse,json,re,struct
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('addresses',nargs='+')
    args=p.parse_args()
    b=(ROOT/'analysis/container_app_main.bin').read_bytes()
    mapping=json.loads((ROOT/'analysis/map-main.json').read_text())
    text=(ROOT/'analysis/ghidra-main/decompiled.c').read_text()
    def word(address):
        if 0x60000000 <= address < 0x60000000+len(b)-3:
            return struct.unpack_from('<I',b,address-0x60000000)[0]
        for op in mapping['operations']:
            if op['kind']=='copy' and op['destination']<=address<op['destination']+op['length']-3:
                return struct.unpack_from('<I',b,op['source']-0x60000000+address-op['destination'])[0]
        return None
    for address in args.addresses:
        address=address.lower().removeprefix('0x').zfill(8)
        match=re.search(r'/\* Address '+address+r';.*?(?=/\* Address |\Z)',text,re.S)
        if not match:
            print('NOT FOUND',address);continue
        body=match.group()
        print(body)
        for literal in sorted(set(int(a,16) for a in re.findall(r'DAT_([0-9a-f]{8})',body))):
            value=word(literal)
            if value is not None:
                print(f'DAT_{literal:08x} = 0x{value:08x}')
if __name__=='__main__':main()
