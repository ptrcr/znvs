from .exception import ParameterError
from .nvs import Nvs


class Decoder:
    """Class responsible for decoding binary NVS."""

    def __init__(self, sector_size: int):
        """Crate nvs decoder.

        :param int sector_size: Size of single NVS sector
        """
        self.sector_size = sector_size

    def load(self, data: bytes) -> dict[int, bytes]:
        """
        Loads NVS from bytes.
        
        :param bytes data: NVS data.
        """
        if not len(data) % self.sector_size == 0:
            raise ParameterError("NVS size must be a multiplicity of sector_size.")

        entries: dict[int, bytes] = {}

        for sector in Nvs(data, self.sector_size):
            for ate in sector:
                entry = ate.get_entry()
                entries[entry.id] = entry.value


        return {id: data for id, data in entries.items() if data is not None}
