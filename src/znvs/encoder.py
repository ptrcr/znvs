from .exception import EncodingError
from .entry import Entry
from .sector import SectorBuilder
import logging

logger = logging.getLogger(__name__)


class Encoder:
    """Class responsible for encoding data to binary NVS image."""

    def __init__(self, sector_size: int):
        """Crate nvs encoder.

        Arguments:
        :param int sector_size: Size of single NVS sector
        """
        self.sector_size = sector_size

    def dump(self, entries: dict[int, bytes], force_close: bool = False) -> bytes:
        """
        Serializes NVS entries to bytes.
        
        :param list[Entry] entries: List of Entries to be put into NVS
        :param bool force_close: Forcibly closes every sector, even if not full
        :return: NVS with serialized Entries
        :raises EncodingError: if Entry cannot be fit into sector
        """
        nvs = b''
        while len(entries) > 0:
            sector = SectorBuilder(self.sector_size)
            consumed: list[int] = []
            for id, value in entries.items():
                if sector.add(Entry(id, value)):
                    consumed.append(id)
                else:
                    # If sector is empty and entry could not be added it means it cannot fit into any sector
                    if sum(1 for _ in sector.get()) == 0:
                        raise EncodingError(f"Entry {id=} cannot fit into sector of {self.sector_size=}")
                    sector.close()
                    break

            # Remove entries that were successfully encoded
            for id in consumed:
                entries.pop(id)

            if force_close:
                sector.close()

            nvs = nvs + sector.get_bytes()

        return nvs
