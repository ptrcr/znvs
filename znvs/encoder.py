import logging
from .entry import Entry
from .exception import ParameterError
from .nvs import Nvs

logger = logging.getLogger(__name__)


class Encoder:
    '''Class responsible for encoding data to binary NVS image.'''

    def __init__(self, sector_size: int):
        """Crate nvs encoder.

        Arguments:
        sector_size -- size of single NVS sector
        """
        self.sector_size = sector_size

    def dump(self, entries: list[Entry]) -> bytes:
        entries: dict[int, bytes] = {}


        for sector in Nvs(data, self.sector_size):
            for ate in sector:
                entry = ate.get_entry()
                entries[entry.id] = entry.value

        return [Entry(id, data) for id, data in entries.items() if data is not None]
