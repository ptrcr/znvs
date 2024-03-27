
from .ate import Ate
from .exception import ChecksumError
from .util import batched


class Sector:
    def __init__(self, data: bytes):
        self.data = data
        self.ates = [bytes(a) for a in batched(self.data, Ate._SIZE)][::-1]
        self.sector_valid = True

        try:
            # GC done ate
            gc_done = Ate.from_data(self.ates[1], self.data)
            if gc_done is None or not gc_done.is_gc_done:
                self.sector_valid = False
        except ChecksumError as _:
            self.sector_valid = False

    @property
    def is_closed(self):
        try:
            return Ate.from_data(self.data[-Ate._SIZE:], self.data).is_close
        except:
            return False

    def __iter__(self):
        self.idx = 2  # skip close_ate and gc_done ate
        return self

    def __next__(self) -> Ate:
        if not self.sector_valid:
            raise StopIteration

        ate = Ate.from_data(self.ates[self.idx], self.data)
        if ate:
            self.idx += 1
            return ate
        else:
            raise StopIteration
