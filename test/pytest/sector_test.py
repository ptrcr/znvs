import os
import unittest

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from sample_descriptor import SampleDescriptor
from znvs.entry import Entry
from znvs.nvs import Nvs
from znvs.sector import Sector, SectorBuilder


class TestSector(unittest.TestCase):
    def test_sector_iterator(self):
        descriptor = SampleDescriptor.load("sample_00")

        sector_0 = descriptor.dump[:0x400]
        for (expected, actual) in list(zip(descriptor.items, Sector(sector_0))):
            self.assertEqual(expected, actual.get_entry(), f"\n{expected=}\n{actual.data=}")

    def test_ate_iterator_sector_not_closed(self):
        sector = Sector(bytes.fromhex("1122334455667788990011223344556677889900FFFFFFFFCDAB00001400FFD2FFFF00000000FF5CFFFFFFFFFFFFFFFF"))
        entries = [Entry(0xABCD, bytes.fromhex("1122334455667788990011223344556677889900"))]  # just one entry

        for expected, actual in zip(entries, sector):
            self.assertEqual(expected.id, actual.data_id)
            self.assertEqual(expected.value, actual.data)

        self.assertFalse(sector.is_closed)

    def test_closed_sector_iteration(self):
        sector = Sector(bytes.fromhex("AABBCCFF112233445566FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFCDAB04000600FF29020000000300FFB3FFFF00000000FF5CFFFF20000000FF38"))
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("112233445566"))]

        for expected, actual in zip(entries, sector):
            self.assertEqual(expected.id, actual.data_id)
            self.assertEqual(expected.value, actual.data)

        self.assertTrue(sector.is_closed)

    def test_sector_encoder(self):
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("112233445566"))]
        builder = SectorBuilder(64)
        for entry in entries:
            self.assertTrue(builder.add(entry))

        encoded = builder.get_bytes()
        self.assertEqual(bytes.fromhex(
            "AABBCCFF112233445566FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFCDAB04000600FF29020000000300FFB3FFFF00000000FF5CFFFFFFFFFFFFFFFF"), encoded)

        for expected, actual in zip(entries, builder.get()):
            self.assertEqual(expected.id, actual.data_id)
            self.assertEqual(expected.value, actual.data)

        # Close sector
        builder.close()
        encoded = builder.get_bytes()
        self.assertEqual(bytes.fromhex(
            "AABBCCFF112233445566FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFCDAB04000600FF29020000000300FFB3FFFF00000000FF5CFFFF20000000FF38"), encoded)
        self.assertTrue(builder.get().is_closed)

    def test_sector_encoder_not_enough_space(self):
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("112233445566"))]
        builder = SectorBuilder(40)
        self.assertTrue(builder.add(entries.pop(0)))
        self.assertFalse(builder.add(entries.pop(0)))

        self.assertEqual(bytes.fromhex(
            "AABBCCFFFFFFFFFFFFFFFFFFFFFFFFFF020000000300FFB3FFFF00000000FF5CFFFFFFFFFFFFFFFF"), builder.get_bytes())

    def test_require_two_entries(self):
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("1122334455667788990011223344556677889900"))]
        sector_size = 48

        builder = SectorBuilder(sector_size)
        self.assertTrue(builder.add(entries[0]))
        self.assertFalse(builder.add(entries[1]))
        builder.close()
        nvs = builder.get_bytes()

        # Prepare new sector and put new sector there, sector shall be closed automatically
        builder = SectorBuilder(sector_size)
        self.assertTrue(builder.add(entries[1]))
        self.assertTrue(builder.get().is_closed)
        nvs = nvs + builder.get_bytes()

        # Validate iterating over obtained sectors give results same as input
        for expected, actual in zip(entries, [e for s in Nvs(nvs, sector_size) for e in s]):
            self.assertEqual(expected.id, actual.data_id)
            self.assertEqual(expected.value, actual.data)
