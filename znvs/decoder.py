from __future__ import annotations
import logging
import struct
from crc import Calculator, Configuration
from .entry import Entry
from .exception import ParameterError, ChecksumError, DecodingError
from .util import batched

logger = logging.getLogger(__name__)


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


class Sector:
    def __init__(self, data: bytes):
        self.data = data
        self.ates = [bytes(a) for a in batched(self.data, Ate._SIZE)][::-1]
        self.sector_valid = True

        try:
            # GC done ate
            gc_done = Ate.from_data(self.ates[1], self.data)
            if gc_done is None or not gc_done.is_gc_done:
                self.sector_valid = False
        except ChecksumError as _:
            self.sector_valid = False

    @property
    def is_closed(self):
        try:
            return Ate.from_data(self.data[-Ate._SIZE:], self.data).is_close
        except:
            return False

    def __iter__(self):
        self.idx = 2  # skip close_ate and gc_done ate
        return self

    def __next__(self) -> Ate:
        if not self.sector_valid:
            raise StopIteration

        ate = Ate.from_data(self.ates[self.idx], self.data)
        if ate:
            self.idx += 1
            return ate
        else:
            raise StopIteration


class Nvs:
    def __init__(self, data: bytes, sector_size: int):
        self.sectors = [Sector(data[i:i + sector_size]) for i in range(0, len(data), sector_size)]
        first_idx = None
        last_idx = None
        for idx in range(len(self.sectors)):
            if self.sectors[idx].is_closed:
                if last_idx is not None:
                    first_idx = idx
                    break
                elif first_idx is None:
                    first_idx = idx
            else:
                if last_idx is None:
                    last_idx = idx

        # sort sectors
        self.sectors = self.sectors[first_idx:] + self.sectors[:first_idx]

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self) -> Sector:
        if self.idx < len(self.sectors):
            self.idx += 1
            return self.sectors[self.idx - 1]
        raise StopIteration


class Decoder:
    '''Class responsible for decoding binary NVS.'''

    def __init__(self, nvs_size: int, sector_size: int):
        """Crate nvs decoder.

        Arguments:
        nvs_size -- size of whole NVS
        sector_size -- size of single NVS sector
        """
        if not nvs_size % sector_size == 0:
            raise ParameterError("NVS size must be a multiplicity of sector_size.")
        self.nvs_size = nvs_size
        self.sector_size = sector_size

    def load(self, data: bytes) -> list[Entry]:
        if len(data) != self.nvs_size:
            raise ParameterError("Provided data does not match NVS layout configuration.")

        entries: dict[int, bytes] = {}

        for sector in Nvs(data, self.sector_size):
            for ate in sector:
                entry = ate.get_entry()
                entries[entry.id] = entry.value

        return [Entry(id, data) for id, data in entries.items() if data is not None]
