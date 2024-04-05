import unittest
import os

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.entry import Entry
from znvs.sector import SectorBuilder


class TestSector(unittest.TestCase):
    def test_sector_encoder(self):
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("112233445566"))]
        builder = SectorBuilder(64)
        for entry in entries:
            self.assertTrue(builder.add(entry))

        encoded = builder.get_bytes()
        print(encoded.hex())
        self.assertEqual(bytes.fromhex(
            "AABBCCFF112233445566FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFCDAB04000600FF29020000000300FFB3FFFF00000000FF5CFFFFFFFFFFFFFFFF"), encoded)

        for expected, actual in zip(entries, builder.get()):
            self.assertEqual(expected.id, actual.data_id)
            self.assertEqual(expected.value, actual.data)

    def test_sector_encoder_not_enough_space(self):
        entries = [Entry(2, bytes.fromhex("AABBCC")), Entry(0xABCD, bytes.fromhex("112233445566"))]
        builder = SectorBuilder(40)
        self.assertTrue(builder.add(entries.pop(0)))
        self.assertFalse(builder.add(entries.pop(0)))

        self.assertEqual(bytes.fromhex(
            "AABBCCFFFFFFFFFFFFFFFFFFFFFFFFFF020000000300FFB3FFFF00000000FF5CFFFFFFFFFFFFFFFF"), builder.get_bytes())
