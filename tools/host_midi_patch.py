"""USB-application integration for the sole mainline builder; not a build target."""
import struct
import subprocess
import sys
from elftools.elf.elffile import ELFFile
from container_tool import FormatError, sha256
from firmware_patch import exact_patch
from memory_map import recover

# (decoded offset, runtime address, exact displaced instructions, export).
HOOKS = [
    (0xa1e2,0x6000a1e2,'2de9f04f87b004460d46','mx1_host_config'),
    (0x9160,0x60009160,'2de9f0470446c27b','mx1_host_tx_open'),
    (0x90fa,0x600090fa,'2de9f047314d0446c27b','mx1_host_rx_open'),
    (0x340b0,0x010091bc,'70b50079374900eb8000','mx1_host_tx_close'),
    (0x33f60,0x0100906c,'70b500798b4900eb8000','mx1_host_rx_close'),
    (0x342ae,0x010093ba,'584a70b50b4600eb8001','mx1_host_enqueue'),
    (0x34188,0x01009294,'00f06ff8','mx1_host_tx_poll'),
    (0x33ff8,0x01009104,'00f0f3f8','mx1_host_rx_poll'),
]

def integrate(original,root,out,env,jump):
    exports=[h[3] for h in HOOKS]+['mx1_host_select','mx1_host_receive','mx1_host_done']
    sources=[root/'patches/usb_host_midi.c',root/'patches/usb_host_midi.S']
    elf=out/'usb-host.elf'
    command=[sys.executable,'-m','ziglang','build-exe','-target','thumb-freestanding-eabi',
             '-mcpu','cortex_m3','-O','ReleaseSmall','-fno-strip','-fno-compiler-rt','-fno-lto',
             '-fno-stack-protector','-fentry=mx1_host_config','--script',str(root/'patches/mainline.ld'),'-femit-bin='+str(elf)]
    for name in exports: command+=['--force_undefined',name]
    command+=['-cflags','-ffreestanding','-fno-builtin','-fno-unwind-tables','-fno-asynchronous-unwind-tables',
              '-Wall','-Wextra','-Werror','--']+[str(p) for p in sources]
    subprocess.run(command,env=env,check=True)
    if elf.stat().st_size > 1024 * 1024:
        raise FormatError('Unexpected sparse/oversized USB ELF layout')
    with elf.open('rb') as f:
        ef=ELFFile(f)
        sections=[s.name for s in ef.iter_sections() if s['sh_flags']&2 and s['sh_size']]
        if sections!=['.host_text','.host_state']: raise FormatError('Unexpected host ELF sections: '+str(sections))
        code=ef.get_section_by_name('.host_text'); state=ef.get_section_by_name('.host_state')
        if (code['sh_addr']!=0x0100bee4 or code['sh_type']!='SHT_PROGBITS' or code['sh_flags']&7!=6 or
            not 0<code['sh_size']<=0x111c or code['sh_size']%4 or
            state['sh_addr']!=0x01017868 or state['sh_type']!='SHT_NOBITS' or state['sh_flags']&7!=3 or
            not 0<state['sh_size']<=0x798): raise FormatError('Invalid USB memory placement')
        if any(s['sh_type'] in ('SHT_REL','SHT_RELA') for s in ef.iter_sections()): raise FormatError('Host relocations remain')
        blob=code.data(); size=state['sh_size']; tab=ef.get_section_by_name('.symtab')
        symbols={}
        for name in exports:
            match=tab.get_symbol_by_name(name)
            if len(match or [])!=1: raise FormatError('Missing host export '+name)
            s=match[0]
            if s['st_info']['type']!='STT_FUNC' or not 0x0100bee4<=(s['st_value']&~1)<0x0100bee4+len(blob): raise FormatError('Invalid export '+name)
            symbols[name]=s['st_value']
    m=recover(original); hot=m['operations'][0]
    if hot!={'call':0x6000000e,'kind':'copy','destination':0x01000300,'length':0xbbe4,'source':0x6002b1f4}: raise FormatError('USB startup map changed')
    if m['operations'][3]!={'call':0x60000028,'kind':'zero','destination':0x01010060,'length':0x7808}: raise FormatError('USB BSS map changed')
    # These allocator bases are independent of main-processor memory.
    table=original[0x2820c:0x28278]
    if table!=bytes.fromhex('0080004000100000009000400010000000a000400010000000500440001000000060044000100000007004400010000000d000010010000000e000010010000000f0000100100000020000000300000000000000010000000100000001000200020003000400040005000000'): raise FormatError('USB allocator table changed')
    if original[0x34964:0x34984] != struct.pack('<8I',1,0,0x8000,0x01020000,2,0,0x1000,0x010142c4):
        raise FormatError('USB RTOS pool map changed')
    cut=0x36dd8; patched=bytearray(original[:cut]+blob+original[cut:]); changes=[]
    def patch(off,old,new,label, runtime=None):
        exact_patch(patched,off,old,new,changes,label)
        changes[-1]['component']='app_usb'
        if runtime is not None: changes[-1]['runtime_address']=runtime
    patch(0xe8,struct.pack('<I',0xbbe4),struct.pack('<I',0xbbe4+len(blob)),'Extend USB executable startup copy')
    for off in (0x100,0x114,0x128,0x13c,0x150):
        old=struct.unpack_from('<I',original,off)[0]
        if old<0x60036dd8: raise FormatError('Unexpected USB initialized source')
        patch(off,struct.pack('<I',old),struct.pack('<I',old+len(blob)),'Relocate USB initialized-data source')
    patch(0x108,struct.pack('<I',0x7808),struct.pack('<I',0x7808+size),'Reserve and zero host MIDI state')
    for off,runtime,old,name in HOOKS:
        expected=bytes.fromhex(old)
        if len(expected)==4:
            delta=(symbols[name]&~1)-(runtime+4)
            if delta&1 or not -(1<<24)<=delta<(1<<24): raise FormatError('Host BL range')
            v=delta&0x1ffffff; sign=v>>24; j1=1^((v>>23)&1)^sign; j2=1^((v>>22)&1)^sign
            data=struct.pack('<HH',0xf000|(sign<<10)|((v>>12)&0x3ff),0xd000|(j1<<13)|(j2<<11)|((v>>1)&0x7ff))
        else: data=jump(runtime,symbols[name])
        if len(data)<len(expected): data+=bytes.fromhex('00bf')*((len(expected)-len(data))//2)
        patch(off,expected,data,name,runtime)
    for off,old,name in [(0x7848,0x60007bf9,'mx1_host_select'),(0x7844,0x01008257,'mx1_host_receive')]:
        patch(off,struct.pack('<I',old),struct.pack('<I',symbols[name]),name)
    report={'original_app_sha256':sha256(original),'patched_app_sha256':sha256(patched),
            'extension_sha256':sha256(blob),'symbols':symbols,'patches':changes,
            'code_start':0x0100bee4,'code_bytes':len(blob),'code_limit':0x0100d000,
            'state_start':0x01017868,'state_bytes':size,'state_limit':0x01018000,
            'insert_offset':cut,'allocator_table_offset':0x2820c,'allocator_table_hex':table.hex(),
            'sources':{str(p.relative_to(root)):sha256(p.read_bytes()) for p in [*sources,root/'patches/mainline.ld',root/'tools/host_midi_patch.py']}}
    (out/'usb-host.load.bin').write_bytes(blob)
    (out/'app_usb.mainline.bin').write_bytes(patched)
    return bytes(patched), report
