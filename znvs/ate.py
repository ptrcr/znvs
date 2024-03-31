
from __future__ import annotations
import math
import struct
from crc import Calculator, Configuration
from .entry import Entry
from .exception import ChecksumError, EncodingError, ParameterError


class Ate:
    _SIZE = 8
    _DATA_ALIGNMENT = 4
    _CRC_CALCULATOR = Calculator(Configuration(width=8, polynomial=0x07, init_value=0xff))

    def __init__(self, ate_offset, data_id, data, data_offset):
        if data_offset % Ate._DATA_ALIGNMENT or ate_offset % Ate._DATA_ALIGNMENT:
            raise ParameterError("Offset not aligned")

        self.ate_offset = ate_offset
        self.data_id = data_id
        self.data_offset = data_offset
        self.data = data

    def get_entry(self) -> Entry | None:
        '''Returns Entry if Ate is not special kind (close of gc)'''
        if self.is_close or self.is_gc_done:
            return None
        return Entry(self.data_id, self.data)

    @property
    def is_close(self):
        return self.data_id == 0xFFFF and self.data is None and self.data_offset != 0x00

    @property
    def is_gc_done(self):
        return self.data_id == 0xFFFF and self.data is None and self.data_offset == 0x00

    @property
    def aligned_data_size(self):
        return Ate._DATA_ALIGNMENT * math.ceil(len(self.data)/Ate._DATA_ALIGNMENT)

    def to_bytes(self, sector_data: bytearray):
        if self.data_offset + self.aligned_data_size > self.ate_offset:
            raise EncodingError("Data do not fit into sector")

        if sector_data[self.ate_offset:self.ate_offset + Ate._SIZE] != b'\xFF' * Ate._SIZE or \
                sector_data[self.data_offset:self.data_offset + self.aligned_data_size] != b'\xFF' * self.aligned_data_size:
            raise EncodingError("Data not erased")

        ate = struct.pack("<HHHB", self.data_id, self.data_offset, len(self.data), 0xFF)
        ate += Ate._calc_crc(ate).to_bytes(1, 'little')
        sector_data[self.data_offset:self.data_offset + len(self.data)] = self.data
        sector_data[self.ate_offset:self.ate_offset + Ate._SIZE] = ate

    @staticmethod
    def _calc_crc(allocation_table_entry: bytes) -> int:
        return Ate._CRC_CALCULATOR.checksum(allocation_table_entry)

    @staticmethod
    def _validate_crc(allocation_table_entry: bytes) -> bool:
        return 0 == Ate._calc_crc(allocation_table_entry)

    @staticmethod
    def from_bytes(ate_offset: int, sector_data: bytes) -> Ate | None:
        ate_data = sector_data[ate_offset:ate_offset + Ate._SIZE]
        if ate_data == bytes.fromhex("FFFFFFFFFFFFFFFF"):
            return None

        # Each entry is 8 bytes
        # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
        # |  ID  | OFFS  |  LEN  | - |CRC|
        data_id, data_offset, data_length = struct.unpack_from("<HHH", ate_data)
        if not Ate._validate_crc(ate_data):
            raise ChecksumError("ATE CRC is invalid")
        return Ate(ate_offset, data_id, sector_data[data_offset:data_offset + data_length] if data_length > 0 else None, data_offset)
