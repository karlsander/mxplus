#!/usr/bin/env python3
"""Boundary/ordering checks for the partial decoder; no DSP math model."""
import struct
import unittest

from esc2_disassemble import Packet, binding_tail, decode, flow_target, logical_image


def words(*values):
    return struct.pack('>' + 'H' * len(values), *values)


class DecoderTests(unittest.TestCase):
    def test_word_order_from_original_boundary_uploader(self):
        # CPU low halfword comes after the high halfword in logical DSP order.
        self.assertEqual(logical_image(bytes.fromhex('030c0100e00f01a0')),
                         words(1, 0x0c03, 0xa001, 0x0fe0))
        with self.assertRaises(ValueError):
            logical_image(b'\x00\x01')

    def test_factory_copy_packet_and_literal_zero(self):
        packet = words(0x1e05, 0x0fe0, 0x8fe2, 0x6001, 0)
        parsed = decode(packet, 0x170)
        self.assertEqual(parsed, [Packet(0x170, (0x1e05, 0x0fe0, 0x8fe2, 0x6001, 0))])
        self.assertEqual(binding_tail(parsed[0]), [(1, 3), (2, 4)])
        self.assertEqual(parsed[0].encode(), packet)

    def test_reject_truncation_without_resynchronizing(self):
        packet = words(0x1e05, 0x0fe0, 0x8fe2, 0x6001, 0)
        for length in range(1, len(packet)):
            with self.subTest(length=length), self.assertRaises(ValueError):
                decode(packet[:length], 0x170)
        for invalid in (words(0, 1), words(0x20), words(0x1f, 1, 1)):
            with self.assertRaises(ValueError):
                decode(invalid, 0x100)

    def test_special_words_require_explicit_chunk_context(self):
        data = words(0, 1, 0x0a02, 0xff71, 0)
        with self.assertRaises(ValueError):
            decode(data, 0)
        with self.assertRaises(ValueError):
            decode(data, 0, gate=True)
        parsed = decode(data, 0, gate=True, trailer=True)
        self.assertEqual([p.kind for p in parsed], ['gate_words', 'packet', 'terminal_word'])
        self.assertEqual(b''.join(p.encode() for p in parsed), data)
        with self.assertRaises(ValueError):
            decode(data, 2, gate=True, trailer=True)
        with self.assertRaises(ValueError):
            decode(words(1), 0, trailer=True)

    def test_flow_inference_is_header_specific(self):
        self.assertEqual(flow_target(decode(words(0x0b03, 0x18a0, 0x2000), 0x36)[0]), 0x4000)
        self.assertIsNone(flow_target(decode(words(0x0c03, 0x0fe0, 0x2000), 0x36)[0]))

    def test_impossible_bindings_remain_raw(self):
        self.assertEqual(binding_tail(Packet(0, (0x0c03, 0x0ffe, 0xa001))), [])
        self.assertEqual(binding_tail(Packet(0, (0x0c03, 0x0fe1, 0xa001))), [])


class ParameterRegistryTests(unittest.TestCase):
    def test_dummy_record_does_not_hide_last_oscillator_controls(self):
        from fx_sends_audit import (ROOT, ORIGINAL_SHA256, MAIN_SHA256, digest,
                                   callback_registry, component_unpacked, COMPONENT_BY_NAME)
        stock = (ROOT / 'inputs/MX1_UPD.original.bin').read_bytes()
        self.assertEqual(digest(stock), ORIGINAL_SHA256)
        blob = component_unpacked(stock, COMPONENT_BY_NAME['app_main'])
        self.assertEqual(digest(blob), MAIN_SHA256)
        records = callback_registry(blob)
        self.assertNotIn(0x45a, records)
        self.assertEqual(records[0x45b], (0x6002c01c, 0xb7118))
        self.assertEqual(records[0x45c], (0x6002c058, 0xb7124))
        self.assertEqual(sum(i in records for i in range(0x453, 0x45d)), 9)


if __name__ == '__main__':
    unittest.main()
