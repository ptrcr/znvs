import unittest
from sample_descriptor import SampleDescriptor
import os

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.ate import Ate
from znvs.exception import EncodingError
from znvs.sector import Sector


class TestAte(unittest.TestCase):
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
        item1_data = bytes.fromhex("AABBCCDDEE")
        ate = Ate(24, 2, item1_data, 8)
        self.assertEqual(ate.data, item1_data)
        self.assertEqual(8, ate.aligned_data_size)
        
        ate.to_bytes(sector)
        self.assertEqual(bytes(sector[:-1]), bytes.fromhex("FFFFFFFFFFFFFFFFAABBCCDDEEFFFFFFFFFFFFFFFFFFFFFF020008000500FF"))
        self.assertTrue(Ate._validate_crc(sector[24:]))

    def test_ate_encoder_no_space(self):
        sector = bytearray.fromhex("FF") * 32
        item1_data = bytes.fromhex("AABBCCDDEE")
        ate = Ate(24, 2, item1_data, 20)
        self.assertRaises(EncodingError, ate.to_bytes, sector)

    def test_ate_encode_many_items(self):
        sector = bytearray.fromhex("FF") * 40
        
        item1_id = 2
        item1_data = bytes.fromhex("AABBCCDDEE")
        ate1 = Ate(32, item1_id, item1_data, 0)
        self.assertEqual(ate1.data, item1_data)
        self.assertEqual(8, ate1.aligned_data_size)
        
        item2_id = 3
        item2_data = bytes.fromhex("112233445566778899")
        ate2 = ate1.next(item2_id, item2_data)
        self.assertEqual(ate2.data_offset, ate1.aligned_data_size)
        self.assertEqual(ate2.data, item2_data)
        self.assertEqual(ate2.ate_offset, 24)
        self.assertEqual(12, ate2.aligned_data_size)

        ate1.to_bytes(sector)
        ate2.to_bytes(sector)

        expected_sector = bytes.fromhex("AABBCCDDEEFFFFFF112233445566778899FFFFFFFFFFFFFF030008000900FFF2020000000500FFCE")
        self.assertEqual(expected_sector, bytes(sector))
        self.assertTrue(Ate._validate_crc(sector[ate1.ate_offset:]))
        self.assertTrue(Ate._validate_crc(sector[ate2.ate_offset:ate1.ate_offset]))

        item3_id = 4
        ate3 = ate2.next(item3_id, bytes.fromhex("A1A2"))
        self.assertRaises(EncodingError, ate3.to_bytes, sector)

        # ensure sector data has not been modified
        self.assertEqual(expected_sector, bytes(sector))
