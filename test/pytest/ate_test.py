import unittest
from sample_descriptor import SampleDescriptor
import os

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.ate import Ate
from znvs.sector import Sector


class TestDecoder(unittest.TestCase):
    def test_ate_decoder(self):
        descriptor = SampleDescriptor.load("sample_00")
        sector = descriptor.dump[:0x400]

        gc_ate = Ate.from_bytes(0x400-16, sector)
        self.assertTrue(gc_ate.is_gc_done)

        data_ate = Ate.from_bytes(0x400-24, sector)
        self.assertEqual(descriptor.items[0].id, data_ate.data_id)
        self.assertEqual(descriptor.items[0].value, data_ate.data)

    def test_ate_decoder_close_ate(self):
        descriptor = SampleDescriptor.load("sample_02")
        sector = descriptor.dump[0x800:]

        done_ate = Ate.from_bytes(0x400-8, sector)
        self.assertTrue(done_ate.is_close)

    def test_ate_iterator(self):
        descriptor = SampleDescriptor.load("sample_00")

        sector_0 = descriptor.dump[:0x400]
        for (expected, actual) in list(zip(descriptor.items, iter(Sector(sector_0)))):
            self.assertEqual(expected, actual.get_entry(), f"\n{expected=}\n{actual.data=}")

    def test_ate_encoder(self):
        sector = bytearray.fromhex("FF") * 32
        ate = Ate(24, 2, bytes.fromhex("AABBCCDDEE"), 8)
        ate.to_bytes(sector)
        self.assertEqual(bytes(sector[:-1]), bytes.fromhex("FFFFFFFFFFFFFFFFAABBCCDDEEFFFFFFFFFFFFFFFFFFFFFF020008000500FF"))
        Ate._validate_crc(sector[24:])
