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

DATA_START = 0x01017264
DATA_LIMIT = 0x01018000
ENTRY = 0x60664000
LIMIT = 0x60666000
ORIGINAL_HEAP_START = 0x606634d0
HEAP_END = 0x62000000


def inject(original, blob, code_length):
    """Append packed state/code, use two empty copies and reserve SDRAM code."""
    data_length = len(blob) - code_length
    if (code_length <= 0 or code_length % 4 or ENTRY + code_length > LIMIT or
            data_length <= 0 or data_length % 4 or DATA_START + data_length > DATA_LIMIT):
        raise FormatError('main extension exceeds reviewed state/code bounds or has invalid load size')
    try:
        operations = recover(original)['operations']
    except ValueError as exc:
        raise FormatError('Invalid original startup map') from exc
    if operations[4] != {'call': 0x60000032, 'kind': 'copy', 'destination': 0x01020000,
                          'length': 0, 'source': 0x600dffb4}:
        raise FormatError('Unexpected original empty startup copy')
    if operations[8] != {'call': 0x60000056, 'kind': 'copy', 'destination': 0x40008000,
                          'length': 0, 'source': 0x600e0448}:
        raise FormatError('Unexpected original empty SDRAM code copy')
    for op in operations:
        for start, end in ((DATA_START, DATA_START + data_length), (ENTRY, LIMIT)):
            if op['length'] and op['destination'] < end and op['destination'] + op['length'] > start:
                raise FormatError('Mainline reservation overlaps original startup memory')
    if operations[-1]['destination'] + operations[-1]['length'] != ORIGINAL_HEAP_START:
        raise FormatError('Original static SDRAM boundary changed')
    if struct.unpack_from('<2I', original, 0xd768) != (HEAP_END, ORIGINAL_HEAP_START):
        raise FormatError('Original SDRAM heap bounds changed')
    for offset, expected in ((0xdfac0, (1, 0, 0x8000, 0x01020000)),
                             (0xdfad0, (2, 0, 0x1000, 0x01013e18))):
        if struct.unpack_from('<4I', original, offset) != expected:
            raise FormatError('Original allocator reservation changed')
    cut = len(original)
    modified = bytearray(original + blob)
    changes = []
    for offset, old, new in ((0x10c, 0x01020000, DATA_START),
                            (0x110, 0, data_length), (0x114, 0x600dffb4, 0x60000000 + cut),
                            (0x134, 0x40008000, ENTRY), (0x138, 0, code_length),
                            (0x13c, 0x600e0448, 0x60000000 + cut + data_length)):
        exact_patch(modified, offset, struct.pack('<I', old), struct.pack('<I', new), changes,
                    'Original empty startup copies initialize SRAM state and reserved SDRAM code')
    heap_changes = []
    exact_patch(modified, 0xd76c, struct.pack('<I', ORIGINAL_HEAP_START),
                struct.pack('<I', LIMIT), heap_changes,
                'Reserve mainline code before stock SDRAM heap; initializer derives reduced capacity')
    return modified, {'insert_offset': cut, 'insert_length': len(blob), 'runtime_address': DATA_START,
                     'data_length': data_length, 'code_address': ENTRY, 'code_length': code_length,
                     'code_load_offset': data_length, 'copy_operation_index': 4,
                     'code_copy_operation_index': 8, 'startup_updates': changes,
                     'heap_update': heap_changes[0],
                     'heap_reservation': {'original_start': ORIGINAL_HEAP_START,
                         'start': LIMIT, 'end_exclusive': HEAP_END,
                         'reserved_bytes': LIMIT - ORIGINAL_HEAP_START,
                         'remaining_bytes': HEAP_END - LIMIT}}
