import itertools
import logging
import struct
from .entry import Entry
from .exception import ValidationError
from .util import batched

logger = logging.getLogger(__name__)


class Decoder:
    '''Class responsible for decoding binary NVS.'''

    METADATA_ENTRY_SIZE = 8

    def __init__(self, nvs_size: int, sector_size: int):
        """Crate nvs decoder.

        Arguments:
        nvs_size -- size of whole NVS
        sector_size -- size of single NVS sector
        """
        if not nvs_size % sector_size == 0:
            raise ValidationError("NVS size must be a multiplicity of sector_size.")
        self.nvs_size = nvs_size
        self.sector_size = sector_size

    def safe_load(self, data: bytes):
        pass

    def load(self, data: bytes) -> list[Entry]:
        if len(data) != self.nvs_size * self.sector_size:
            raise ValidationError("Provided data does not match NVS layout configuration.")

        metadata_offset = self.sector_size - 3 * Decoder.METADATA_ENTRY_SIZE
        entries: dict[int, bytes] = {}

        # TODO: Use proper sectors order
        for sector in batched(data, self.sector_size):
            entry = Decoder._deserialize_entry(data, metadata_offset)
            while entry:
                entries[entry.id] = entry.data
                metadata_offset -= Decoder.METADATA_ENTRY_SIZE
                entry = Decoder._deserialize_entry(data, metadata_offset)

        return [Entry(id, data) for id, data in entries.items()]

    @staticmethod
    def _validate_crc():
        pass

    @staticmethod
    def _deserialize_entry(data, metadata_offset) -> Entry | None:
        try:
            # Each entry is 8 bytes
            # 0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7
            # |   ID  | OFFS  |  LEN  | - |CRC|
            nvs_id, offset, length = struct.unpack_from("<HHH", data, metadata_offset)
            if nvs_id != 0xFFFF:
                return Entry(nvs_id, data[offset:offset + length])
        except struct.error as exc:
            logger.error(exc)

        return None
