#!/usr/bin/env python3
"""Compile and inject the narrow MX-1 UAC1 host-enumeration experiment offline.

No device I/O. Build artifacts are research-only until hardware validation.
Run with the Python environment that contains ziglang, capstone, unicorn and
pyelftools. The original update hash and every overwritten byte are checked.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
from elftools.elf.elffile import ELFFile
from container_tool import (ORIGINAL_SHA256,COMPONENT_BY_NAME,component_unpacked,
                            repack_image,sha256,FormatError)
from memory_map import recover

ROOT=Path(__file__).resolve().parents[1]

def scatter_extend(original,blob):
    """Append code to the FIRST SRAM copy, moving only load-image .data sources.

    Runtime addresses of all existing code and data remain unchanged. The final
    SDRAM BSS clear is deliberately unchanged. It occurs after all copies.
    """
    m=recover(original)
    hot=m['operations'][0]
    if hot != {'call':0x6000000e,'kind':'copy','destination':0x01000300,
               'length':0xbbe4,'source':0x6002b1f4}:
        raise FormatError('not the expected USB application scatter layout')
    # Three original USB allocator regions occupy 0x0100d000..0x01010000.
    # Their table is at decoded 0x2820c; do not mistake all of this gap for free RAM.
    if len(blob)%4 or 0x0100bee4+len(blob)>0x0100d000:
        raise FormatError('extension exceeds unused private-SRAM interval')
    insert_at=hot['source']-0x60000000+hot['length']
    patched=bytearray(original[:insert_at]+blob+original[insert_at:])
    struct.pack_into('<I',patched,0xe8,hot['length']+len(blob))
    updates=[{'offset':0xe8,'before':hot['length'],'after':hot['length']+len(blob)}]
    # These source literals are established by the actual startup LDR/BL trace.
    for literal in (0x100,0x114,0x128,0x13c,0x150):
        old=struct.unpack_from('<I',original,literal)[0]
        if old < 0x60000000+insert_at:
            raise FormatError('unexpected initialized-data source before insertion')
        struct.pack_into('<I',patched,literal,old+len(blob))
        updates.append({'offset':literal,'before':old,'after':old+len(blob)})
    recover(patched)  # All copy sources must still fit the new load image.
    return patched,{'insert_offset':insert_at,'runtime_address':0x0100bee4,
                    'insert_length':len(blob),'startup_updates':updates}

def exact_patch(image,offset,expected,replacement,changes,label):
    if image[offset:offset+len(expected)]!=expected or len(expected)!=len(replacement):
        raise FormatError(f'{label}: original bytes do not match')
    image[offset:offset+len(expected)]=replacement
    changes.append({'label':label,'file_offset':offset,'runtime_address':0x60000000+offset,
                    'original':expected.hex(),'replacement':replacement.hex()})

def build(firmware,out):
    raw=firmware.read_bytes()
    if sha256(raw)!=ORIGINAL_SHA256:raise FormatError('original firmware SHA-256 mismatch')
    out.mkdir(parents=True,exist_ok=True)
    elf=out/'uac1_host_probe.elf'
    cache=out/'compiler-cache';cache.mkdir(exist_ok=True)
    env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(cache.resolve()),ZIG_LOCAL_CACHE_DIR=str(cache.resolve()))
    command=[sys.executable,'-m','ziglang','build-exe','-target','thumb-freestanding-eabi',
             '-mcpu','cortex_m3','-O','ReleaseSmall','-fno-strip','-fno-compiler-rt','-fno-lto',
             '--force_undefined','mx1_uac1_policy',
             '--force_undefined','mx1_uac1_configuration',
             '-fno-stack-protector','-fentry=mx1_uac1_classify',
             '--script',str(ROOT/'patches/uac1_host.ld'),'-femit-bin='+str(elf),
             '-cflags','-ffreestanding','-fno-builtin','-fno-unwind-tables',
             '-fno-asynchronous-unwind-tables','--',str(ROOT/'patches/uac1_host_probe.c'),
             str(ROOT/'patches/uac1_trampoline.S')]
    subprocess.run(command,check=True,env=env)
    with elf.open('rb') as f:
        ef=ELFFile(f);text=ef.get_section_by_name('.text');blob=text.data()
        symbols={s.name:s.entry['st_value'] for s in ef.get_section_by_name('.symtab').iter_symbols() if s.name.startswith('mx1_')}
        if text['sh_addr']!=0x0100bee4:raise FormatError('extension link address mismatch')
        if any(s['sh_type']=='SHT_REL' for s in ef.iter_sections()):raise FormatError('unresolved relocations')
    (out/'uac1_host_probe.code.bin').write_bytes(blob)
    original=component_unpacked(raw,COMPONENT_BY_NAME['app_usb'])
    patched,scatter=scatter_extend(original,blob)
    changes=[]
    # At a halfword-aligned entry, PC-relative LDR has PC aligned down to a120.
    # LDR pc,[pc,#4]; NOP; .word target -> literal at a124, resume at a128.
    veneer=bytes.fromhex('dff804f000bf')+struct.pack('<I',symbols['mx1_uac1_classify']|1)
    exact_patch(patched,0xa11e,bytes.fromhex('2de9f04191f805c00026'),veneer,changes,'descriptor classifier hook')
    config_veneer=bytes.fromhex('dff804f000bf')+struct.pack('<I',symbols['mx1_uac1_configuration']|1)
    exact_patch(patched,0xa1e2,bytes.fromhex('2de9f04f87b004460d46'),config_veneer,
                changes,'configuration parser hook with strict-origin markers')
    exact_patch(patched,0x7848,struct.pack('<I',0x60007bf9),
                struct.pack('<I',symbols['mx1_uac1_policy']|1),changes,'selection callback pointer')
    rebuilt,container_report=repack_image(raw,{'app_usb':bytes(patched)},allow_resize=True)
    (out/'app_usb.uac1_probe.bin').write_bytes(patched)
    # An explicit experimental name; never the official automatic-update name.
    image_path=out/'MX1_UAC1_HOST_PROBE_UNTESTED.bin'
    image_path.write_bytes(rebuilt)
    report={'status':'OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED',
            'input_sha256':sha256(raw),'patched_app_sha256':sha256(patched),
            'container_sha256':sha256(rebuilt),'extension_sha256':sha256(blob),
            'compiler':'ziglang 0.13.0 (Clang/LLVM), thumb-freestanding-eabi cortex_m3 ReleaseSmall',
            'symbols':symbols,'scatter_extension':scatter,'patches':changes,
            'container':container_report,
            'limits':['UAC1 AudioStreaming class 1/subclass 2/protocol 0',
                      'High-speed only; bInterval 1 (125 microseconds)',
                      'Separate IN and OUT interfaces, only alt0+alt1',
                      'Fixed single rate 44100/48000/96000; identical in/out',
                      'Stereo PCM, 24 significant bits in 4-byte subframes',
                      'No explicit feedback endpoint, rate SET_CUR, UAC2, packed PCM or generic MIDI',
                      'Enumeration and policy experiment, not proven streaming interoperability']}
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=build(a.firmware,a.output)
    print(json.dumps({k:r[k] for k in ['status','container_sha256','symbols','scatter_extension','patches']},indent=2))
if __name__=='__main__':main()
