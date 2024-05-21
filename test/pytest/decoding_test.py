import os
import unittest

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../src'))  # nopep8
from sample_descriptor import SampleDescriptor
from znvs.decoder import Decoder
from znvs.exception import ChecksumError
from znvs.nvs import Nvs


class TestDecoder(unittest.TestCase):
    def _test_sample_decoding(self, sample_name: str):
        descriptor = SampleDescriptor.load(sample_name)
        decoder = Decoder(descriptor.nvs.sector_size)
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
        decoder = Decoder(descriptor.nvs.sector_size)
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

            for (expected, actual) in list(zip(expected_sectors, Nvs(descriptor.dump, descriptor.nvs.sector_size))):
                self.assertEqual(expected, actual.data, f"\n{expected=}\n{actual.data=}")

    def test_sectors_iterator_02(self):
        # Last sector in flash layout is first nvs sector
        descriptor = SampleDescriptor.load("sample_02")
        first_sector_offset = descriptor.nvs.sector_size * (descriptor.nvs.sectors_num - 1)
        expected_sectors = [descriptor.dump[first_sector_offset:], descriptor.dump[0:descriptor.nvs.sector_size],
                            descriptor.dump[descriptor.nvs.sector_size:first_sector_offset]]

        for (expected, actual) in list(zip(expected_sectors, Nvs(descriptor.dump, descriptor.nvs.sector_size))):
            self.assertEqual(expected, actual.data, f"\n{expected=}\n{actual.data=}")
