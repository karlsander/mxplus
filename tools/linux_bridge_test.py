#!/usr/bin/env python3
"""Host-independent tests of bridge dry-run behavior and routing decisions."""
import contextlib
import io
import json
import unittest
from unittest import mock

import linux_bridge as bridge


class BridgeTests(unittest.TestCase):
    def test_actions_are_read_only_without_apply(self):
        for action in ("plan", "setup", "route", "teardown"):
            output = io.StringIO()
            with contextlib.redirect_stdout(output), \
                    mock.patch.object(bridge, "setup") as setup, \
                    mock.patch.object(bridge, "route") as route, \
                    mock.patch.object(bridge, "teardown") as teardown:
                self.assertEqual(bridge.main([action]), 0)
                json.loads(output.getvalue())
                setup.assert_not_called()
                route.assert_not_called()
                teardown.assert_not_called()

    def test_channel_count_and_direction(self):
        args = bridge.parser().parse_args(["plan", "--channels", "18"])
        plan = bridge.plan(args)
        self.assertEqual(plan["write_fields"]["functions/uac2.bridge/c_chmask"], "0x3ffff")
        self.assertEqual(plan["minimum_audio_payload_bytes_per_125us_per_direction"], 432)
        self.assertEqual(plan["requested_route_latency_us"], 5000)
        to_mx1, from_mx1 = [route["argv"] for route in plan["routes"]]
        self.assertEqual(to_mx1[2], "hw:CARD=UAC2Gadget,DEV=0")
        self.assertEqual(to_mx1[4], "hw:CARD=MX1,DEV=0")
        self.assertEqual(from_mx1[2], "hw:CARD=MX1,DEV=0")
        self.assertEqual(from_mx1[4], "hw:CARD=UAC2Gadget,DEV=0")
        self.assertIn("samplerate", to_mx1)

    def test_setup_apply_requires_truthful_power_selection(self):
        args = bridge.parser().parse_args(["setup", "--apply"])
        with mock.patch.object(bridge.os, "geteuid", return_value=0), \
                mock.patch.object(bridge.Path, "mkdir") as mkdir:
            with self.assertRaisesRegex(RuntimeError, "power-mode"):
                bridge.setup(args)
            mkdir.assert_not_called()

    def test_96khz_multichannel_target_fits_conservative_buffer_budget(self):
        args = bridge.parser().parse_args(["plan", "--channels", "18", "--rate", "96000"])
        frames = bridge.requested_latency(args) * args.rate / 1000000
        self.assertEqual(frames, 240)
        self.assertLess(frames * args.channels * 4, 65536 / 2)

    def test_card_id_rejects_pcm_and_shell_syntax(self):
        for invalid in ("../MX1", "hw:1,0", "MX1;echo", "$(x)", "a\nb"):
            with self.assertRaises(Exception):
                bridge.card_id(invalid)
        self.assertEqual(bridge.card_id("MX1"), "MX1")


if __name__ == "__main__":
    unittest.main()
