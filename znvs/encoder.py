from .nvs import Nvs
from .exception import EncodingError
from .entry import Entry
import logging
from .ate import Ate

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
        sectors = []
        while len(entries) > 0:
            sector = bytearray.fromhex("FF") * self.sector_size
            ate = None
            consumed: list[Entry] = []
            for entry in entries:
                if ate is None:
                    ate = Ate(self.sector_size - Ate._SIZE, entry.id, entry.value, 0)
                else:
                    ate = ate.next(entry.id, entry.value)

                try:
                    ate.to_bytes(sector)
                    consumed.append(entry)
                except EncodingError as _:
                    # No space in sector
                    # TODO: Close sector
                    # TODO: Validate it is possible to encode such entry in empty sector
                    break

            # Remove entries that were successfully encoded
            for entry in consumed:
                entries.remove(entry)

            sectors.append(sector)

        return b''.join(sectors)
