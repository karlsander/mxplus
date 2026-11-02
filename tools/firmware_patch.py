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
ENTRY = 0x01018000
LIMIT = 0x0101c000


def inject(original, blob, code_length):
    """Append the mainline load image and guard the original empty copy slot."""
    if (code_length <= 0 or code_length % 4 or ENTRY + code_length > LIMIT or
            len(blob) != ENTRY - DATA_START + code_length):
        raise FormatError('main extension exceeds reviewed SRAM bounds or has invalid load size')
    operations = recover(original)['operations']
    if operations[4] != {'call': 0x60000032, 'kind': 'copy', 'destination': 0x01020000,
                          'length': 0, 'source': 0x600dffb4}:
        raise FormatError('Unexpected original empty startup copy')
    for op in operations:
        if op['length'] and op['destination'] < LIMIT and op['destination'] + op['length'] > DATA_START:
            raise FormatError('Mainline reservation overlaps original startup memory')
    for offset, expected in ((0xdfac0, (1, 0, 0x8000, 0x01020000)),
                             (0xdfad0, (2, 0, 0x1000, 0x01013e18))):
        if struct.unpack_from('<4I', original, offset) != expected:
            raise FormatError('Original allocator reservation changed')
    cut = len(original)
    modified = bytearray(original + blob)
    changes = []
    for offset, old, new in ((0x10c, 0x01020000, DATA_START),
                            (0x110, 0, len(blob)), (0x114, 0x600dffb4, 0x60000000 + cut)):
        exact_patch(modified, offset, struct.pack('<I', old), struct.pack('<I', new), changes,
                    'Original empty startup copy initializes mainline writable state and read-only code')
    return modified, {'insert_offset': cut, 'insert_length': len(blob), 'runtime_address': DATA_START,
                     'code_address': ENTRY, 'code_length': code_length, 'copy_operation_index': 4,
                     'startup_updates': changes}
