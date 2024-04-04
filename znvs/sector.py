
from .ate import Ate
from .exception import ChecksumError, EncodingError
from .entry import Entry


class Sector:
    def __init__(self, data: bytes):
        self.data = data
        self.sector_valid = True

        try:
            # GC done ate
            gc_done = Ate.from_bytes(len(self.data) - Ate._SIZE * 2, self.data)
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
        self.data = bytearray.fromhex("FF") * self.sector_size

        # gc done ate
        self.last_ate = Ate(self.sector_size - Ate._SIZE * 2, 0xFFFF, None, 0)
        self.last_ate.to_bytes(self.data)

    def add(self, entry: Entry) -> bool:
        ate = self.last_ate.next(entry.id, entry.value)
        try:
            ate.to_bytes(self.data)
            self.last_ate = ate
            return True
        except EncodingError as _:
            # TODO: close ate
            return False

    def get(self) -> Sector:
        return Sector(self.data)

    def get_bytes(self) -> bytes:
        return bytes(self.data)
