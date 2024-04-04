from .ate import Ate
from .nvs import Nvs
from .entry import Entry
from .sector import SectorBuilder
import logging

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
        nvs = b''
        while len(entries) > 0:
            sector = SectorBuilder(self.sector_size)
            consumed: list[Entry] = []
            for entry in entries:
                if sector.add(entry):
                    consumed.append(entry)
                else:
                    # TODO: Close sector
                    # TODO: Validate it is possible to encode such entry in empty sector
                    break

            # Remove entries that were successfully encoded
            for entry in consumed:
                entries.remove(entry)

            nvs = nvs + sector.get_bytes()

        return nvs
