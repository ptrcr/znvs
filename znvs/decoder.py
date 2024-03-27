import logging
from .entry import Entry
from .exception import ParameterError
from .nvs import Nvs

logger = logging.getLogger(__name__)


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
