#!/usr/bin/env python3
"""Compile and package an experimental MX-1 USB-B UAC2 extension offline.

Preserves the original boot/update/sub-CPU/host applications. Does not access a
device. The generated candidate is not a statement of physical compatibility.
"""
import argparse
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
from elftools.elf.elffile import ELFFile
from build_host_probe import exact_patch
from container_tool import ORIGINAL_SHA256,COMPONENT_BY_NAME,component_unpacked,repack_image,sha256,FormatError
from memory_map import recover
from uac2_design import prototype_configuration

ROOT=Path(__file__).resolve().parents[1]

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

def build(firmware,out):
    raw=firmware.read_bytes()
    if sha256(raw)!=ORIGINAL_SHA256:raise FormatError('original firmware SHA-256 mismatch')
    out.mkdir(parents=True,exist_ok=True)
    config=prototype_configuration(preserve_modes=True)
    (out/'uac2_configuration.h').write_text('#define MX1_UAC2_CONFIGURATION_BYTES {'+
        ','.join('0x%02x'%b for b in config)+'}\n')
    cache=out/'compiler-cache';cache.mkdir(exist_ok=True)
    env=dict(os.environ,ZIG_GLOBAL_CACHE_DIR=str(cache.resolve()),ZIG_LOCAL_CACHE_DIR=str(cache.resolve()))
    elf=out/'uac2_device_probe.elf'
    cmd=[sys.executable,'-m','ziglang','build-exe','-target','thumb-freestanding-eabi',
         '-mcpu','cortex_m3','-O','ReleaseSmall','-fno-strip','-fno-compiler-rt','-fno-lto',
         '-fno-stack-protector','-fentry=mx1_uac2_initialize','--script',str(ROOT/'patches/uac2_device.ld'),
         '-femit-bin='+str(elf),'-I',str(out),'-cflags','-ffreestanding','-fno-builtin',
         '-fno-unwind-tables','-fno-asynchronous-unwind-tables','--',
         str(ROOT/'patches/uac2_device_probe.c'),str(ROOT/'sources/hardware/uac2_adapter.c')]
    subprocess.run(cmd,check=True,env=env)
    with elf.open('rb') as f:
        ef=ELFFile(f);section=ef.get_section_by_name('.text');blob=section.data()
        symbols={s.name:s.entry['st_value'] for s in ef.get_section_by_name('.symtab').iter_symbols() if s.name.startswith('mx1_')}
        if section['sh_addr']!=0x0100f6a4:raise FormatError('extension load address mismatch')
        if any(s['sh_type']=='SHT_REL' for s in ef.iter_sections()):raise FormatError('unresolved relocation')
    required=('mx1_uac2_initialize','mx1_uac2_configuration','mx1_uac2_class_request','mx1_uac2_set_rate')
    if not all(k in symbols for k in required):raise FormatError('compiler omitted required extension symbols')
    (out/'uac2_device_probe.code.bin').write_bytes(blob)
    original=component_unpacked(raw,COMPONENT_BY_NAME['app_main'])
    modified,scatter=inject(original,blob);changes=[]
    exact_patch(modified,0xd980,bytes.fromhex('10b500f01ff80d48'),
        bytes.fromhex('dff800f0')+struct.pack('<I',symbols['mx1_uac2_initialize']|1),changes,'normal USB initializer hook')
    exact_patch(modified,0xb4afc,struct.pack('<I',0x600b499c),
        struct.pack('<I',symbols['mx1_uac2_configuration']),changes,'HS configuration pointer')
    exact_patch(modified,0xb4984,bytes.fromhex('ff00ff'),bytes.fromhex('ef0201'),changes,'normal device IAD class triplet')
    exact_patch(modified,0xb4996,bytes.fromhex('ff00ff'),bytes.fromhex('ef0201'),changes,'normal qualifier IAD class triplet')
    # Original capture pump clears r12 when there is no OUT data. Keep the
    # existing default of 1 so IN can prime before playback; OUT silence remains.
    exact_patch(modified,0xda292,bytes.fromhex('4ff0000c'),bytes.fromhex('4ff0010c'),changes,'input-first audio priming experiment')
    changes[-1]['runtime_address']=0x01009a06
    rebuilt,container_report=repack_image(raw,{'app_main':bytes(modified)},allow_resize=True)
    (out/'app_main.uac2_probe.bin').write_bytes(modified)
    (out/'MX1_UAC2_DEVICE_PROBE_UNTESTED.bin').write_bytes(rebuilt)
    report={'status':'OFFLINE EXPERIMENT; NOT HARDWARE VALIDATED',
            'input_sha256':sha256(raw),'patched_app_sha256':sha256(modified),'container_sha256':sha256(rebuilt),
            'extension_sha256':sha256(blob),'compiler':'ziglang 0.13.0 Cortex-M3 ReleaseSmall, no LTO',
            'symbols':symbols,'scatter_extension':scatter,'patches':changes,
            'uac2_configuration_length':len(config),'uac2_configuration_sha256':sha256(config),
            'container':container_report,
            'limits':['High-speed USB-B only; normal audio mode only',
                      'Fixed read-only clock reports the existing 44.1/48/96 kHz boot setting',
                      '18-channel alt1 and stereo alt2 retained, four-byte 24-bit PCM',
                      'Original vendor MIDI IF3 retained; no class-compliant MIDI claim',
                      'Full-speed non-audio descriptor remains the stock vendor stub',
                      'Clock-valid response reports supported configured rate, not measured PLL lock',
                      'Capture startup change tested under mocked MMIO only',
                      'Apple/iOS enumeration, FIFO timing and sustained audio unverified']}
    (out/'build-report.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('firmware',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=build(a.firmware,a.output)
    print(json.dumps({k:r[k] for k in ['status','container_sha256','symbols','scatter_extension','patches']},indent=2))
if __name__=='__main__':main()
