import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from usb_midi_descriptors import mainline_configuration,validate_configuration
from uac2_design import prototype_configuration


class MIDIConfigurationTests(unittest.TestCase):
    def test_audio_descriptors_unchanged(self):
        config=mainline_configuration()
        self.assertEqual(config[9:303],prototype_configuration(True)[9:303])
        self.assertEqual(validate_configuration(config)['ports_per_direction'],2)

    def test_reject_broken_graph(self):
        config=mainline_configuration()
        # Control collection; MS total length; OUT jack source/pin; cable lists;
        # duplicate jack ID; wrong jack type; invalid endpoint packet size.
        changes=[(4,4),(328,3),(343,0),(363,99),(364,2),(418,5),(419,1),
                 (410,1),(355,1),(348,2)]
        for offset,value in changes:
            with self.subTest(offset=offset):
                changed=bytearray(config);changed[offset]=value
                with self.assertRaises((ValueError,IndexError)):
                    validate_configuration(bytes(changed))

    def test_reject_truncated_or_zero_length(self):
        config=mainline_configuration()
        for n in (8,302,340,len(config)-1):
            with self.subTest(n=n),self.assertRaises(ValueError):
                validate_configuration(config[:n])
        changed=bytearray(config);changed[329]=0
        with self.assertRaises(ValueError):validate_configuration(bytes(changed))

if __name__=='__main__':unittest.main()
