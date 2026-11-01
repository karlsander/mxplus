"""Descriptor-fixture checks, independent of target USB hardware."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import uac2_design as design
from usb_descriptors import parse_configuration


class UAC2DesignTests(unittest.TestCase):
    def test_original_probe_and_preserving_lengths(self):
        for preserve, length, interfaces in ((False, 211, 3), (True, 355, 4)):
            config = design.prototype_configuration(preserve_modes=preserve)
            parsed = parse_configuration(config, 0)
            self.assertEqual(len(config), length)
            self.assertEqual(parsed["total_length"], length)
            self.assertEqual(parsed["interface_count"], interfaces)
            self.assertEqual(parsed["warnings"], [])

    def test_preserved_midi_is_exact_original_bytes(self):
        image = ROOT / "analysis/container_app_main.bin"
        if not image.exists():
            self.skipTest("original decompressed firmware absent")
        original = image.read_bytes()[0xb4a6a:0xb4a9e]
        self.assertEqual(len(original), 52)
        self.assertEqual(design.ORIGINAL_VENDOR_MIDI, original)
        self.assertEqual(design.prototype_configuration(True)[-52:], original)

    def test_audio_alternates_and_endpoint_framing(self):
        parsed = parse_configuration(design.prototype_configuration(True), 0)
        interfaces = [d for d in parsed["descriptors"] if d["descriptor_type"] == 4]
        self.assertEqual([(d["number"], d["alternate_setting"]) for d in interfaces],
                         [(0, 0), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2), (3, 0), (3, 1)])
        streams = [d for d in parsed["descriptors"] if d["name"] == "uac2_as_general"]
        self.assertEqual([(d["parent_interface"], d["parent_alternate_setting"], d["channels"])
                         for d in streams], [(1, 1, 18), (1, 2, 2), (2, 1, 18), (2, 2, 2)])
        endpoints = [d for d in parsed["descriptors"] if d["descriptor_type"] == 5
                     and d["parent_interface"] in (1, 2)]
        self.assertEqual([(d["address"], d["maximum_packet_size_raw"], d["attributes"], d["interval"])
                         for d in endpoints], [("0x0d", 1008, 5, 1), ("0x0d", 112, 5, 1),
                                               ("0x8e", 1008, 37, 1), ("0x8e", 112, 37, 1)])

    def test_iad_excludes_vendor_midi_and_shared_clock_is_read_only(self):
        config = design.prototype_configuration(True)
        # IAD: first interface 0, count 3, audio class, UAC2 protocol.
        self.assertEqual(config[9:17], bytes.fromhex("08 0b 00 03 01 00 20 02"))
        self.assertIn(bytes.fromhex("08 24 0a 10 01 05 00 00"), config)
        self.assertEqual(config.count(bytes.fromhex("08 24 0a")), 1)
        self.assertFalse(design.design_report(True)["fits_original_descriptor_storage_size"])

    def test_all_terminal_clock_and_stream_references_resolve(self):
        parsed = parse_configuration(design.prototype_configuration(True), 0)
        descriptors = parsed["descriptors"]
        terminals = {d["terminal_id"]: d for d in descriptors if "terminal_id" in d}
        clocks = {d["clock_id"]: d for d in descriptors if "clock_id" in d}
        self.assertEqual(set(terminals), {1, 2, 6, 7})
        self.assertEqual(set(clocks), {0x10})
        self.assertFalse(set(terminals) & set(clocks))
        self.assertEqual(terminals[2]["source_id"], 1)
        self.assertEqual(terminals[7]["source_id"], 6)
        for terminal in terminals.values():
            self.assertIn(terminal["clock_source_id"], clocks)
        for descriptor in descriptors:
            if descriptor["name"] == "uac2_as_general":
                terminal = terminals[descriptor["terminal_link"]]
                self.assertEqual(terminal["terminal_type"], "0x0101")
                expected = "uac2_input_terminal" if descriptor["parent_interface"] == 1 else "uac2_output_terminal"
                self.assertEqual(terminal["name"], expected)
        ac = [d for d in descriptors if d.get("parent_interface") == 0 and d["descriptor_type"] == 0x24]
        self.assertEqual(sum(d["length"] for d in ac), ac[0]["total_class_specific_length"])

    def test_highest_rate_packet_capacity_has_one_frame_headroom(self):
        parsed = parse_configuration(design.prototype_configuration(True), 0)
        streams = {(d["parent_interface"], d["parent_alternate_setting"]): d
                   for d in parsed["descriptors"] if d["name"] == "uac2_as_general"}
        for d in parsed["descriptors"]:
            key = (d.get("parent_interface"), d.get("parent_alternate_setting"))
            if d["descriptor_type"] == 5 and key in streams:
                # 96 kHz gives 12 frames per 125-us microframe. Include +1.
                self.assertGreaterEqual(d["maximum_payload_per_transaction"], streams[key]["channels"] * 4 * 13)
                self.assertEqual(d["high_speed_transactions_per_microframe"], 1)


if __name__ == "__main__":
    unittest.main()
