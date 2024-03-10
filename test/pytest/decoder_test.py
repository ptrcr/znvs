import unittest
from sample_descriptor import SampleDescriptor
import os
from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.decoder import Decoder
from znvs.exception import ChecksumError


class TestDecoder(unittest.TestCase):
    def test_sample_decoding(self):
        descriptor = SampleDescriptor.load("sample_00")
        decoder = Decoder(descriptor.nvs.sector_size * descriptor.nvs.sectors_num, descriptor.nvs.sector_size)
        result = decoder.load(descriptor.dump)
        self.assertEqual(sorted(descriptor.items), sorted(result))

    def test_crc_validation(self):
        descriptor = SampleDescriptor.load("sample_00")
        decoder = Decoder(descriptor.nvs.sector_size * descriptor.nvs.sectors_num, descriptor.nvs.sector_size)
        # Modify one bit at the second entry
        modified = bytearray(descriptor.dump)
        modified[0x3EB] ^= 0x01
        self.assertRaises(ChecksumError, decoder.load, bytes(modified))
