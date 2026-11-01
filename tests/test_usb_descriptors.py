"""Bounds and actual-image evidence tests; no USB hardware is accessed."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("usb_descriptors", ROOT / "tools/usb_descriptors.py")
USB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(USB)


class USBDescriptorTests(unittest.TestCase):
    def test_empty_and_short_input(self):
        for data in (b"", b"\x12", b"\x12\x01", bytes(range(256))):
            report = USB.scan_image(data)
            self.assertEqual(report["devices"], [])

    def test_reject_configuration_lengths(self):
        valid = bytes.fromhex("09 02 12 00 01 01 00 80 00 09 04 00 00 00 ff ff 00 00")
        self.assertEqual(USB.parse_configuration(valid, 0)["warnings"], [])
        for changed in (valid[:-1], valid[:9] + b"\x00" + valid[10:],
                        valid[:9] + b"\x14" + valid[10:]):
            with self.assertRaises(ValueError):
                USB.parse_configuration(changed, 0)

    def test_reject_truncated_rate_list(self):
        fields = USB.descriptor_fields(bytes.fromhex("0b 24 02 01 02 04 18 02 00 77 01"),
                                       {"interface_subclass": 2, "interface_protocol": 2})
        self.assertIn("malformed", fields)
        self.assertNotIn("sample_rates_hz", fields)

    def test_endpoint_usage_and_period(self):
        fields = USB.descriptor_fields(bytes.fromhex("07 05 8e 25 f0 03 01"))
        self.assertEqual(fields["usage_type"], "implicit_feedback_data")
        self.assertEqual(fields["synchronization_type"], "asynchronous")
        self.assertEqual(fields["maximum_payload_per_transaction"], 1008)
        self.assertEqual(fields["high_speed_service_interval_us_if_applicable"], 125)

    def test_exact_mx1_evidence(self):
        path = ROOT / "analysis/container_app_main.bin"
        if not path.exists():
            self.skipTest("decompressed original firmware not present")
        image = path.read_bytes()
        report = USB.scan_image(image)
        device = next(d for d in report["devices"] if d["product_id"] == "0x01a3")
        self.assertEqual(device["offset"], 0xb4980)
        self.assertEqual(device["device_class"], 255)
        self.assertEqual(device["aligned_literal_pointer_offsets"], ["0xb4af8"])
        config = next(c for c in report["configurations"] if c["offset"] == 0xb499c)
        self.assertEqual(config["total_length"], 258)
        self.assertEqual(config["warnings"], [])
        self.assertEqual(bytes.fromhex(config["raw_configuration_hex"]), image[0xb499c:0xb4a9e])
        self.assertEqual([(s["direction"], s["alternate_setting"], s["channels"])
                          for s in report["mx1_findings"]["streams"]],
                         [("OUT", 1, 18), ("OUT", 2, 2), ("IN", 1, 18), ("IN", 2, 2)])


if __name__ == "__main__":
    unittest.main()
