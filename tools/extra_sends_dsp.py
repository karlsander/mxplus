#!/usr/bin/env python3
"""Small, independently written ESC2 send kernels for the mainline builder.

Only A arithmetic and FE transfers are emitted, using packet templates present
in the frozen MX-1. Numerical/parallel-operation semantics are cross-referenced
to enorrmann/roland-plugout-reveng, instruction_set_reference.md sections 6/10,
commit 34a25b46b63d807e3b42407914258ac46d369515. No upstream code is imported.
This module does not build a firmware variant or access a device.
"""
from __future__ import annotations

import struct

# Coefficients belong to DSP1. Original normal/effect programs stop at C07F.
ALT_GAIN = 0xC080
FX_GAIN = 0xC08B
POST = 0xC096
SEND_R = 0xC097
PHONES = 0xC098
RETURN = 0xC099
MASTER_VALID = 0xC09A
# Same-frame temporaries beyond both original normal programs' bank-1 uses.
FX_INPUT = 0x20B0
ALT_OUTPUT = 0x20B2
MIXER_ENTRY = 0x2000
OUTPUT_ENTRY = 0x2800


def arithmetic(destination, operation, x, y, immediate=False):
    if not (0 <= destination < 8 and 0 <= operation < 8 and 0 <= x < 8 and 0 <= y < 16):
        raise ValueError('Unsupported A operand')
    return destination << 12 | operation << 9 | x << 6 | (0x10 if immediate else 0) | y


class Kernel:
    """Emit the seven simple templates observed in the original mixer.

All operations and stores read the registers as they were at packet entry.
Loads become available in the following packet. A register may have one writer
per packet. Bank 5 has at most one access, coefficients at most two reads.
"""
    templates = {(1, 0): 0x0900, (2, 0): 0x1500, (0, 1): 0x0C00,
                 (0, 2): 0x1E00, (1, 1): 0x1800, (2, 1): 0x2E00,
                 (1, 2): 0x3400, (2, 2): 0x5F00}

    def __init__(self):
        self.packets = []

    def emit(self, ops=(), transfers=(), literal=None):
        ops, transfers = tuple(ops), tuple(transfers)
        header = self.templates[(len(ops), len(transfers))]
        writes = [op >> 12 for op in ops]
        writes += [register for register, _ in transfers if register < 8]
        if len(writes) != len(set(writes)):
            raise ValueError('Parallel register write conflict')
        if sum(address >> 13 == 5 for _, address in transfers) > 1:
            raise ValueError('Multiple bank-5 accesses')
        if any(register >= 8 and address >> 13 == 6 for register, address in transfers):
            raise ValueError('DSP write to coefficient bank')
        if literal is not None and (transfers or len(ops) != 1):
            raise ValueError('Only standalone immediate arithmetic is emitted')
        body = list(ops)
        body.extend(register << 12 | 0xFE0 | index * 2
                    for index, (register, _) in enumerate(transfers))
        body.extend(address for _, address in transfers)
        if literal is not None:
            body.append(literal)
        self.packets.append((header | (len(body) + 1), *body))

    def constant(self, register, raw16):
        self.emit((arithmetic(register, 0, 1, 0, True),), literal=raw16)

    def load(self, register, address):
        self.emit(transfers=((register, address),))

    def store(self, register, address):
        self.emit(transfers=((register + 8, address),))

    def encode(self):
        return b''.join(struct.pack('>' + 'H' * len(p), *p) for p in self.packets)


def mixer():
    """Two independent sums from the stock post-BEAT-FX, pre-pan strip taps.

The alternate bus retains stereo until its destination mixdown. Internal FX
uses the channel pan, like the existing AUX. In PRE mode the stock AUX ignores
mute and fader; in POST mode both apply. Reading the original DSP coefficients
preserves the selected fader curve and its actual coefficient value.
"""
    k = Kernel()
    k.packets.append((0x0A02, 0xFF70))
    for r in (2, 3, 4, 5):
        k.constant(r, 0)
    for channel in range(11):
        source = 0xA128 + (channel if channel < 4 else channel * 2 - 4)
        k.emit(transfers=((0, source), (6, 0xC038 + channel)))
        if channel < 4:
            k.emit((arithmetic(1, 0, 1, 0),), ((7, 0xC022 + channel),))
        else:
            k.emit(transfers=((1, source + 1), (7, 0xC022 + channel)))
        # f = 1 + post * (fader * mute - 1).
        k.emit((arithmetic(6, 2, 6, 7),), ((7, POST),))
        k.emit((arithmetic(6, 0, 7, 0, True),), literal=0xB000)
        k.emit((arithmetic(6, 2, 6, 7),))
        k.emit((arithmetic(6, 0, 6, 0, True),), literal=0x3000)
        k.emit((arithmetic(0, 2, 0, 6), arithmetic(1, 2, 1, 6)),
               ((7, ALT_GAIN + channel),))
        k.emit((arithmetic(4, 3, 0, 7), arithmetic(5, 3, 1, 7)),
               ((6, 0xC001 + channel), (7, 0xC00C + channel)))
        k.emit((arithmetic(0, 2, 0, 6), arithmetic(1, 2, 1, 7)),
               ((7, FX_GAIN + channel),))
        k.emit((arithmetic(2, 3, 0, 7), arithmetic(3, 3, 1, 7)))
    k.emit(transfers=((10, FX_INPUT), (11, FX_INPUT + 1)))
    k.emit(transfers=((12, ALT_OUTPUT), (13, ALT_OUTPUT + 1)))
    # Original mixer return, including its required trailing packet.
    k.packets.extend(((0x0A02, 0xFF70), (0x0B02, 0x00F8), (0x0001,)))
    if MIXER_ENTRY + len(k.encode()) > OUTPUT_ENTRY:
        raise ValueError('Send mixer overlaps output kernel')
    return k


def interpolate(k, first, second, coefficient, destination):
    """Destination = first + coefficient * (second - first)."""
    k.load(0, first)
    k.emit(transfers=((1, second), (7, coefficient)))
    k.emit((arithmetic(1, 7, 0, 1),))
    k.emit((arithmetic(0, 3, 1, 7),))
    k.store(0, destination)


def output():
    """Mix the dedicated MASTER slot and wet return before stock metering.

The internal return never becomes a MASTER FX input. SEND R averages the two
normal AUX channels onto L and the two alternate channels onto R. PHONES mode
replaces the CUE source; the ARM policy fixes headphone MIX at its CUE endpoint.
"""
    k = Kernel()
    k.packets.append((0x0A02, 0xFF70))
    # Replace the stock slot crossfade with a dedicated MASTER slot (slot 0).
    # An explicit validity gate bypasses it while its program is being loaded.
    k.constant(0, 0)
    k.store(0, 0xA146)
    for side in (0, 1):
        k.emit(transfers=((0, 0x2006 + side), (1, 0x2000 + side)))
        k.emit(transfers=((7, 0xC051), (6, MASTER_VALID)))
        k.emit((arithmetic(7, 2, 7, 6), arithmetic(1, 7, 0, 1)),
               ((8, 0x4001 + side),))
        k.emit((arithmetic(0, 3, 1, 7),), ((1, 0x2004 + side),))
        k.emit((arithmetic(0, 6, 0, 1),), ((1, 0x2002 + side), (7, RETURN)))
        k.emit((arithmetic(0, 3, 1, 7),))
        k.store(0, 0xA13A + side)
    # Both mono values must be formed before either original AUX side changes.
    for first, second, destination in ((0xA13C, 0xA13D, 0x20B4),
                                       (ALT_OUTPUT, ALT_OUTPUT + 1, 0x20B5)):
        k.load(0, first)
        k.load(1, second)
        k.emit((arithmetic(0, 6, 0, 1),))
        k.emit((arithmetic(0, 2, 0, 0, True),), literal=0x2800)
        k.store(0, destination)
    for side in (0, 1):
        interpolate(k, 0xA13C + side, 0x20B4 + side, SEND_R, 0xA13C + side)
        interpolate(k, 0xA13E + side, ALT_OUTPUT + side, PHONES, 0xA13E + side)
    # Resume the exact original metering block; its epilogue returns to root.
    k.packets.extend(((0x0A02, 0xFF70), (0x0B03, 0x0080, 0x1B32 // 2), (0x0001,)))
    if OUTPUT_ENTRY + len(k.encode()) > 0x4000:
        raise ValueError('Output kernel overlaps MASTER FX slot')
    return k
