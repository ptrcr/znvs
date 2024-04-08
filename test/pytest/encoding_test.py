import os
import unittest

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from sample_descriptor import SampleDescriptor
from znvs.decoder import Decoder
from znvs.encoder import Encoder


class TestEncoder(unittest.TestCase):
    def test_simple_sample_decode_encode(self):
        descriptor = SampleDescriptor.load("sample_00")
        decoder = Decoder(descriptor.nvs.sector_size)
        decoded = decoder.load(descriptor.dump)
        encoded = Encoder(descriptor.nvs.sector_size).dump(decoded)
        self.assertEqual(encoded + b'\xFF' * (len(descriptor.dump) - len(encoded)), descriptor.dump)
