import logging
import struct
from crc import Calculator, Configuration
from .entry import Entry
from .exception import ParameterError, ChecksumError
from .util import batched

logger = logging.getLogger(__name__)


class Ate:
    _ATE_SIZE = 8
    _CRC_CALCULATOR = Calculator(Configuration(width=8, polynomial=0x07, init_value=0xff))

    def __init__(self, ate_data, sector):
        self.sector = sector
        self.data_id, self.data_offset, self.data_length = struct.unpack_from("<HHH", ate_data)
        self.valid = Ate._validate_crc(ate_data)

    def data(self):
        return self.sector[self.data_offset:self.data_offset + self.data_length]

    @property
    def is_close(self):
        return self.valid and self.data_id == 0xFFFF and self.data_length == 0

    @staticmethod
    def _validate_crc(allocation_table_entry: bytes) -> bool:
        return 0 == Ate._CRC_CALCULATOR.checksum(allocation_table_entry)


class Sector:
    def __init__(self, data):
        self.data = data

    @property
    def is_closed(self):
        return Ate(self.data[-Ate._ATE_SIZE:], self.data).is_close


class Sectors:
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
                last_idx = idx if last_idx is None else last_idx

        # sort sectors
        self.sectors = self.sectors[first_idx:] + self.sectors[:first_idx]

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx < len(self.sectors):
            self.idx += 1
            return self.sectors[self.idx - 1]
        raise StopIteration


class AteIterator:
    _ATE_SIZE = 8

    def __iter__(self, sectors):
        self.sectors = sectors
        for sector in self.sectors:
            for ate_data in reversed(batched(self, sector, Ate._ATE_SIZE)):
                ate = Ate(ate_data, sector)

    @staticmethod
    def _deserialize_ate(data, metadata_offset) -> Entry | None:
        try:
            # Each entry is 8 bytes
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # |   ID  | OFFS  |  LEN  | - |CRC|
            nvs_id, offset, length = struct.unpack_from("<HHH", data, metadata_offset)
            if nvs_id != 0xFFFF:
                if not Decoder._validate_crc(data[metadata_offset: metadata_offset + Decoder._METADATA_ENTRY_SIZE]):
                    raise ChecksumError(f"NVS contains entry ({nvs_id=}) which has invalid checksum")
                return Entry(nvs_id, data[offset:offset + length])
        except struct.error as exc:
            logger.error(exc)

        return None


class Decoder:
    '''Class responsible for decoding binary NVS.'''

    _METADATA_ENTRY_SIZE = 8
    _CRC_CALCULATOR = Calculator(Configuration(width=8, polynomial=0x07, init_value=0xff))

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

        for sector in Sectors(data, self.sector_size):
            metadata_offset = self.sector_size - 3 * Decoder._METADATA_ENTRY_SIZE
            entry = Decoder._deserialize_entry(sector.data, metadata_offset)
            while entry:
                entries[entry.id] = entry.value
                metadata_offset -= Decoder._METADATA_ENTRY_SIZE
                entry = Decoder._deserialize_entry(sector.data, metadata_offset)

        return [Entry(id, data) for id, data in entries.items() if data is not None]

    @staticmethod
    def _validate_crc(allocation_table_entry: bytes) -> bool:
        return 0 == Decoder._CRC_CALCULATOR.checksum(allocation_table_entry)

    @staticmethod
    def _deserialize_entry(data, metadata_offset) -> Entry | None:
        try:
            # Each entry is 8 bytes
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # |   ID  | OFFS  |  LEN  | - |CRC|
            nvs_id, offset, length = struct.unpack_from("<HHH", data, metadata_offset)
            if nvs_id != 0xFFFF:
                if not Decoder._validate_crc(data[metadata_offset: metadata_offset + Decoder._METADATA_ENTRY_SIZE]):
                    raise ChecksumError(f"NVS contains entry ({nvs_id=}) which has invalid checksum")
                return Entry(nvs_id, data[offset:offset + length] if length > 0 else None)
        except struct.error as exc:
            logger.error(exc)

        return None
