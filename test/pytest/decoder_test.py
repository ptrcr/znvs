import unittest
from sample_descriptor import SampleDescriptor
import os
from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.decoder import Decoder, Sector, SectorIterator, Ate, AteIterator
from znvs.exception import ChecksumError
from znvs.util import batched


class TestDecoder(unittest.TestCase):
    def _test_sample_decoding(self, sample_name: str):
        descriptor = SampleDescriptor.load(sample_name)
        decoder = Decoder(descriptor.nvs.sector_size * descriptor.nvs.sectors_num, descriptor.nvs.sector_size)
        result = decoder.load(descriptor.dump)
        self.assertEqual(sorted(descriptor.items), sorted(result))

    def test_simple_sample_decoding(self):
        self._test_sample_decoding("sample_00")

    def test_sample_decoding_two_consecutive_sectors_occupied(self):
        self._test_sample_decoding("sample_01")

    def test_sample_decoding_first_nvs_sector_not_at_the_beginning(self):
        self._test_sample_decoding("sample_02")

    def test_sample_decoding_deleted_item(self):
        self._test_sample_decoding("sample_03")

    def test_crc_validation(self):
        descriptor = SampleDescriptor.load("sample_00")
        decoder = Decoder(descriptor.nvs.sector_size * descriptor.nvs.sectors_num, descriptor.nvs.sector_size)
        # Modify one bit at the second entry
        modified = bytearray(descriptor.dump)
        modified[0x3EB] ^= 0x01
        self.assertRaises(ChecksumError, decoder.load, bytes(modified))

    def test_sectors_iterator_00_01(self):
        # First sector in flash layout is first nvs sector
        for sample in ["sample_00", "sample_01"]:
            descriptor = SampleDescriptor.load(sample)
            expected_sectors = [descriptor.dump[0:descriptor.nvs.sector_size],
                                descriptor.dump[descriptor.nvs.sector_size:2 * descriptor.nvs.sector_size],
                                descriptor.dump[descriptor.nvs.sector_size*2:]]

            for (expected, actual) in list(zip(expected_sectors, SectorIterator(descriptor.dump, descriptor.nvs.sector_size))):
                self.assertEqual(expected, actual.data, f"\n{expected=}\n{actual.data=}")

    def test_sectors_iterator_02(self):
        # Last sector in flash layout is first nvs sector
        descriptor = SampleDescriptor.load("sample_02")
        first_sector_offset = descriptor.nvs.sector_size * (descriptor.nvs.sectors_num - 1)
        expected_sectors = [descriptor.dump[first_sector_offset:], descriptor.dump[0:descriptor.nvs.sector_size],
                            descriptor.dump[descriptor.nvs.sector_size:first_sector_offset]]

        for (expected, actual) in list(zip(expected_sectors, SectorIterator(descriptor.dump, descriptor.nvs.sector_size))):
            self.assertEqual(expected, actual.data, f"\n{expected=}\n{actual.data=}")

    def test_ate_decoder(self):
        descriptor = SampleDescriptor.load("sample_00")
        sector = descriptor.dump[:0x400]

        gc_ate = Ate.from_data(sector[0x400-16:-8], sector)
        self.assertTrue(gc_ate.is_gc_done)

        data_ate = Ate.from_data(sector[0x400-24:-16], sector)
        self.assertEqual(descriptor.items[0].id, data_ate.data_id)
        self.assertEqual(descriptor.items[0].value, data_ate.data)

    def test_ate_decoder_close_ate(self):
        descriptor = SampleDescriptor.load("sample_02")
        sector = descriptor.dump[0x800:]

        done_ate = Ate.from_data(sector[0x400-8:], sector)
        self.assertTrue(done_ate.is_close)

    def test_ate_iterator(self):
        descriptor = SampleDescriptor.load("sample_00")
        
        sector_0 = descriptor.dump[:0x400]
        for (expected, actual) in list(zip(descriptor.items, AteIterator(Sector(sector_0)))):
            self.assertEqual(expected, actual.get_entry(), f"\n{expected=}\n{actual.data=}")
