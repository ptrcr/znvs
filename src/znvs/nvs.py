
from .sector import Sector


class Nvs:
    """Class responsible for iterating over NVS."""

    def __init__(self, data: bytes, sector_size: int):
        """
        Constructs NVS.
        
        :param bytes data: NVS data
        :param int sector_size: Size of single NVS sector
        """
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
