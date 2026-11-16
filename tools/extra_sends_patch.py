"""Guarded integration of the two sends into the sole mainline builder."""
import struct

from container_tool import FormatError, sha256
from firmware_patch import exact_patch
from extra_sends_dsp import mixer, output, MIXER_ENTRY, OUTPUT_ENTRY

CODE_START = 0x60664000
HEAP_START = 0x60666000
STATE_START = 0x010174E0


def words(data):
    return ','.join(hex(x[0]) for x in struct.iter_unpack('<I', data))


def cpu_program(logical, start=0):
    padded = bytes(start & 2) + logical
    padded += bytes(-len(padded) % 4)
    return b''.join(padded[i:i+4][::-1] for i in range(0, len(padded), 4))


def header(original):
    """Only new program bytes and the extended normal-program table are emitted.

    Existing program sources remain at their stock locations. Both kernels are
    uploaded inside the stock normal-graph stop/load/start transaction.
    """
    result = []
    for name, kernel in (('mix', mixer()), ('out', output())):
        result.append('static const unsigned sends_' + name + '[] = {' +
                      words(cpu_program(kernel.encode())) + '};')
    rows = []
    for i in range(18):
        row = struct.unpack_from('<III', original, 0xbbed0 + 12*i)
        rows.append('{' + ','.join(hex(x) for x in row) + '}')
    for name, entry, kernel in (('mix', MIXER_ENTRY, mixer()), ('out', OUTPUT_ENTRY, output())):
        rows.append('{%s,%s,(unsigned)sends_%s}' % (hex(entry), len(kernel.encode()), name))
    result.append('const unsigned mx1_sends_programs[20][3] = {' + ','.join(rows) + '};')
    return '\n'.join(result) + '\n'


def integrate(image, original, symbols, changes, jump):
    def program_patch(source, start, position, expected, replacement, label):
        # The original uploader pads an unaligned first halfword into the LOW
        # half of the first CPU word. Preserve neighboring halfwords verbatim.
        relative = position - start + (start & 2)
        base = relative & ~3
        end = (relative + len(expected) + 3) & ~3
        source_offset = source - 0x60000000 + base
        before = original[source_offset:source_offset + end-base]
        logical = bytearray(b''.join(before[i:i+4][::-1] for i in range(0, len(before), 4)))
        at = relative - base
        if logical[at:at+len(expected)] != expected or len(expected) != len(replacement):
            raise FormatError('DSP guard mismatch: ' + label)
        logical[at:at+len(expected)] = replacement
        after = b''.join(logical[i:i+4][::-1] for i in range(0, len(logical), 4))
        exact_patch(image, source_offset, before, after, changes, label)
        changes[-1].update(dsp_core=1, logical_program_offset=position,
                           logical_original=expected.hex(), logical_replacement=replacement.hex())

    program_patch(0x600bb448, 0x11ca, 0x1ac4,
                  bytes.fromhex('0b0200f80001'), bytes.fromhex('0b0300801000'),
                  'Extend the original mixer with independent send sums')
    program_patch(0x600bbd4c, 0x1aca, 0x1ace,
                  bytes.fromhex('3e070fe01fe27fe420002002c050'),
                  bytes.fromhex('0b0300801400') + bytes.fromhex('0001')*4,
                  'Dedicated MASTER slot and internal wet return; preserve original mute marker')
    sites = {1: ((0x6032,0x2006),(0x6048,0x2007),(0x61ac,0x2006),
                 (0x61ae,0x2007),(0x62a6,0x2007),(0x62a8,0x2006)),
             3: ((0x6046,0x2006),(0x6048,0x2007)),
             4: ((0x601e,0x2006),(0x6020,0x2007))}
    # Aggregate adjacent operands into one guarded CPU word patch.
    for algorithm, refs in sites.items():
        descriptor = struct.unpack_from('<I', original, 0xcab4c+algorithm*4)[0]
        start, length, source = struct.unpack_from('<III', original, descriptor-0x60000000)
        assert start == 0x6000
        positions = {}
        for position, value in refs:
            positions.setdefault(position & ~3, []).append((position,value))
        for base, operands in positions.items():
            before = original[source-0x60000000+base-start:source-0x60000000+base-start+4][::-1]
            after = bytearray(before)
            for position, value in operands:
                assert struct.unpack_from('>H', before, position-base)[0] == value
                struct.pack_into('>H', after, position-base, 0x20b0+value-0x2006)
            program_patch(source, start, base, before, after,
                          f'Internal algorithm {algorithm}: independent input taps')
    for offset in (0x2abfe, 0x2acce, 0x2b150):
        exact_patch(image, offset, bytes.fromhex('401c'), bytes.fromhex('0020'), changes,
                    'Reserve slot zero for normal, COMBI and direct MASTER type selection')
    exact_patch(image, 0x29ee4, bytes.fromhex('2de9f04389b00d46'),
                jump(0x60029ee4, symbols['mx1_sends_load']), changes,
                'Bypass MASTER return during original in-place effect loading')
    exact_patch(image, 0x267b4, bytes.fromhex('70b50446fff7ebff'),
                jump(0x600267b4, symbols['mx1_sends_graph']), changes,
                'Invalidate effect returns before every original graph reload')
    exact_patch(image, 0x777c4, struct.pack('<II',18,0x600bbed0),
                struct.pack('<II',20,symbols['mx1_sends_programs']), changes,
                'Normal DSP1 graph includes both extra-send kernels')
    return {'normal_program_count':20,
            'kernels': [{'entry':entry,'bytes':len(k.encode()),'sha256':sha256(k.encode())}
                        for entry,k in ((MIXER_ENTRY,mixer()),(OUTPUT_ENTRY,output()))],
            'master_slot':0,'internal_slot':1,'additional_delay_buffers':0,
            'coefficient_indices':[0x80,0x9a],'same_frame_data_words':[0x20b0,0x20b5]}
