
from typing import cast
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

        self.last_ate_offset = cast(Ate, Ate.from_bytes(len(self.data) - Ate._SIZE, self.data)).data_offset if self.is_closed else None

    @property
    def is_closed(self):
        try:
            return Ate.from_bytes(len(self.data) - Ate._SIZE, self.data).is_close
        except:
            return False

    def __iter__(self):
        self.next_ate_offset = len(self.data) - Ate._SIZE * 3  # skip close_ate and gc_done ate
        return self

    def __next__(self) -> Ate:
        if not self.sector_valid:
            raise StopIteration

        # If sector is closed and we already processed last ate, do not even try to decode next ate
        if self.last_ate_offset is not None and self.next_ate_offset < self.last_ate_offset:
            raise StopIteration

        ate = Ate.from_bytes(self.next_ate_offset, self.data)
        if ate:
            self.next_ate_offset -= Ate._SIZE
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

            # Automatically close sector is there is less space than for single ate
            if ate.ate_offset - (ate.data_offset + ate.aligned_data_size) < Ate._SIZE:
                self.close()

            return True
        except EncodingError as _:
            return False

    def close(self):
        Ate(self.sector_size - Ate._SIZE, 0xFFFF, None, self.last_ate.ate_offset).to_bytes(self.data)

    def get(self) -> Sector:
        return Sector(self.data)

    def get_bytes(self) -> bytes:
        return bytes(self.data)
