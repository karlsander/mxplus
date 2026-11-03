"""Mainline high-speed USB-MIDI 1.0 function; independently authored.

USB-IF MIDI 1.0 sections 6.1/6.2 and appendix B. The retired audio design in
uac2_design stays frozen. MIDI bulk transport remains the original firmware.
"""
import struct
from uac2_design import prototype_configuration, ORIGINAL_VENDOR_MIDI
from usb_descriptors import parse_configuration


def mainline_configuration():
    old = prototype_configuration(preserve_modes=True)
    assert old.endswith(ORIGINAL_VENDOR_MIDI)
    # Separate UAC1 control collection for MIDI; UAC2 IAD remains IF0..2.
    midi = bytes.fromhex('08 0b 03 02 01 01 00 00 '
                         '09 04 03 00 00 01 01 00 00 '
                         '09 24 01 00 01 09 00 01 04 '
                         '09 04 04 00 02 01 03 00 00')
    jacks = bytearray()
    for base in (1, 5):
        # Embedded IN -> external OUT; external IN -> embedded OUT.
        jacks += bytes((6, 0x24, 2, 1, base, 0))
        jacks += bytes((6, 0x24, 2, 2, base + 1, 0))
        jacks += bytes((9, 0x24, 3, 1, base + 2, 1, base + 1, 1, 0))
        jacks += bytes((9, 0x24, 3, 2, base + 3, 1, base, 1, 0))
    # Normative section 6.1.2.1: header + Jack/Element descriptors only.
    midi += bytes.fromhex('07 24 01 00 01') + struct.pack('<H', 7 + len(jacks)) + jacks
    for endpoint, ids in ((3, (1, 5)), (0x84, (3, 7))):
        midi += bytes((9, 5, endpoint, 2, 0, 2, 0, 0, 0))
        midi += bytes((6, 0x25, 1, 2, *ids))
    config = bytearray(old[:-len(ORIGINAL_VENDOR_MIDI)] + midi)
    struct.pack_into('<H', config, 2, len(config))
    config[4] = 5
    validate_configuration(bytes(config))
    return bytes(config)


def validate_configuration(config):
    """Validate references and cable order, not merely descriptor byte lengths."""
    parsed = parse_configuration(config, 0)
    if parsed['warnings']:
        raise ValueError(parsed['warnings'])
    rows = [bytes.fromhex(d['raw_hex']) for d in parsed['descriptors']]
    interfaces = [d for d in rows if d[1] == 4]
    if config[4] != 5 or {d[2] for d in interfaces} != set(range(5)):
        raise ValueError('Expected five interfaces')
    if [d for d in rows if d[1] == 11] != [
            bytes.fromhex('08 0b 00 03 01 00 20 02'),
            bytes.fromhex('08 0b 03 02 01 01 00 00')]:
        raise ValueError('Audio and MIDI associations must be separate')
    start = rows.index(bytes.fromhex('09 04 03 00 00 01 01 00 00'))
    if rows[start+1] != bytes.fromhex('09 24 01 00 01 09 00 01 04'):
        raise ValueError('MIDI control collection must reference interface 4')
    if rows[start+2] != bytes.fromhex('09 04 04 00 02 01 03 00 00'):
        raise ValueError('Expected MIDIStreaming interface 4 alternate 0')
    header = rows[start+3]
    jacks = rows[start+4:start+12]
    if header[:5] != bytes.fromhex('07 24 01 00 01') or int.from_bytes(header[5:7], 'little') != 7 + sum(map(len,jacks)):
        raise ValueError('Invalid MIDIStreaming class length/version')
    entities = {}
    for jack in jacks:
        if len(jack) not in (6,9) or jack[1] != 0x24 or jack[2] not in (2,3) or jack[3] not in (1,2) or not jack[4] or jack[4] in entities:
            raise ValueError('Invalid or duplicate MIDI jack')
        entities[jack[4]] = jack
    for jack in jacks:
        if jack[2] == 3 and (len(jack) != 9 or jack[5] != 1 or jack[6] not in entities or entities[jack[6]][2] != 2 or jack[7] != 1):
            raise ValueError('Invalid MIDI source jack/pin')
    tail = rows[start+12:]
    if len(tail) != 4:
        raise ValueError('Unexpected MIDI endpoint/alternate count')
    for n,(endpoint,subtype,ids) in enumerate(((3,2,(1,5)),(0x84,3,(3,7)))):
        ep,assoc = tail[n*2:n*2+2]
        if ep != bytes((9,5,endpoint,2,0,2,0,0,0)) or assoc != bytes((6,0x25,1,2,*ids)):
            raise ValueError('Invalid bulk endpoint or cable order')
        if any(entities[i][2:4] != bytes((subtype,1)) for i in ids):
            raise ValueError('Endpoint must associate embedded jacks of matching direction')
    return {'interfaces': [3,4], 'ports_per_direction': 2, 'bulk_endpoints': ['0x03','0x84'],
            'configuration_bytes': len(config), 'midi_class_bytes': int.from_bytes(header[5:7], 'little')}
