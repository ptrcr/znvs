from __future__ import annotations
from collections import namedtuple
import os
import yaml

from site import addsitedir  # nopep8
addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))  # nopep8
from znvs.entry import Entry  # nopep8


class SampleDescriptor:
    SAMPLES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../golden_samples')
    Nvs = namedtuple("Nvs", "sector_size sectors_num")
    
    def __init__(self, nvs: dict, content: list[dict], dump: str):
        self.nvs = SampleDescriptor.Nvs(**nvs)
        self.items = [Entry(item["item"]["id"], bytes.fromhex(item["item"]["hex_value"])) for item in content]
        with open(os.path.join(SampleDescriptor.SAMPLES_DIR, dump), 'rb') as dump_file:
            self.dump = dump_file.read()

    @staticmethod
    def load(name: str) -> SampleDescriptor:
        with open(os.path.join(SampleDescriptor.SAMPLES_DIR, name + ".yml")) as yml_file:
            return SampleDescriptor(**yaml.load(yml_file.read(), yaml.SafeLoader))
