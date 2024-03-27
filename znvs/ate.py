
from __future__ import annotations
import struct
from crc import Calculator, Configuration
from .entry import Entry
from .exception import ChecksumError


class Ate:
    _SIZE = 8
    _CRC_CALCULATOR = Calculator(Configuration(width=8, polynomial=0x07, init_value=0xff))

    def __init__(self, data_id, data, sector_offset):
        self.data_id = data_id
        self.sector_offset = sector_offset
        self.data = data

    def get_entry(self) -> Entry | None:
        '''Returns Entry if Ate is not special kind (close of gc)'''
        if self.is_close or self.is_gc_done:
            return None
        return Entry(self.data_id, self.data)

    @property
    def is_close(self):
        return self.data_id == 0xFFFF and self.data is None and self.sector_offset != 0x00

    @property
    def is_gc_done(self):
        return self.data_id == 0xFFFF and self.data is None and self.sector_offset == 0x00

    @staticmethod
    def _validate_crc(allocation_table_entry: bytes) -> bool:
        return 0 == Ate._CRC_CALCULATOR.checksum(allocation_table_entry)

    @staticmethod
    def from_data(ate_data: bytes, sector_data: bytes) -> Ate | None:
        if ate_data == bytes.fromhex("FFFFFFFFFFFFFFFF"):
            return None

        # Each entry is 8 bytes
        # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
        # |  ID  | OFFS  |  LEN  | - |CRC|
        data_id, data_offset, data_length = struct.unpack_from("<HHH", ate_data)
        if not Ate._validate_crc(ate_data):
            raise ChecksumError("ATE CRC is invalid")
        return Ate(data_id, sector_data[data_offset:data_offset + data_length] if data_length > 0 else None, data_offset)
