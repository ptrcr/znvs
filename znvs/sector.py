
from .ate import Ate
from .exception import ChecksumError


class Sector:
    def __init__(self, data: bytes):
        self.data = data
        self.sector_valid = True

        try:
            # GC done ate
            gc_done = Ate.from_bytes(len(self.data) - Ate._SIZE*2, self.data)
            if gc_done is None or not gc_done.is_gc_done:
                self.sector_valid = False
        except ChecksumError as _:
            self.sector_valid = False

    @property
    def is_closed(self):
        try:
            return Ate.from_bytes(len(self.data) - Ate._SIZE, self.data).is_close
        except:
            return False

    def __iter__(self):
        self.idx = 2  # skip close_ate and gc_done ate
        return self

    def __next__(self) -> Ate:
        if not self.sector_valid:
            raise StopIteration

        ate = Ate.from_bytes(len(self.data) - Ate._SIZE * (self.idx + 1), self.data)
        if ate:
            self.idx += 1
            return ate
        else:
            raise StopIteration


class SectorBuilder:
    def __init__(self, sector_size):
        self.sector_size = sector_size
        sector_data = b'\xff' * self.sector_size
