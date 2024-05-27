# znvs
Tools for manipulating [Zephyr Non-Volatile Storage](https://docs.zephyrproject.org/latest/services/storage/nvs/nvs.html).

## Requirements

* Python3

## Usage

### Preparing NVS

```python
from znvs.encoder import Encoder

example_data = {10: bytes.fromhex('1122334455'),
                20: bytes.fromhex('A5A5A5A5')}
nvs_sector_size = 1024
nvs = Encoder(nvs_sector_size).dump(example_data)
print(nvs)
```

Output:
```
00000000: 11 22 33 44 55 FF FF FF  A5 A5 A5 A5 FF FF FF FF  ."3DU...........
00000010: FF FF FF FF FF FF FF FF  FF FF FF FF FF FF FF FF  ................
00000020: 14 00 08 00 04 00 FF A3  0A 00 00 00 05 00 FF 24  ...............$
00000030: FF FF 00 00 00 00 FF 5C  FF FF FF FF FF FF FF FF  .......\........
```

### Parsing NVS content

```python
from znvs.decoder import Decoder

with open("../test/golden_samples/sample_00.bin", 'rb') as nvs_dump:
    binary_content = nvs_dump.read()
    content = Decoder(0x400).load(binary_content)
    for key, value in content.items():
        print(f"{key}:\n{hexdump(value, 'return')}")
```

Output:
```
1:
00000000: 11 22 33 44 55 66 77 88                           ."3DUfw.
2:
00000000: A5 A5 A5 A5 A5 A5 5A 5A  5A 5A 5A 5A              ......ZZZZZZ
3:
00000000: 00 01 02 03 04 05 06 07  08 09 0A 0B 0C 0D 0E 0F  ................
00000010: 10 11 12 13 14 15 16 17  18 19 1A 1B 1C 1D 1E 1F  ................
00000020: 20 21 22 23 24 25 26 27  28 29 2A 2B 2C 2D 2E 2F   !"#$%&'()*+,-./
00000030: 30 31 32 33 34 35 36 37  38 39 3A 3B 3C 3D 3E 3F  0123456789:;<=>?
00000040: 40 41 42 43 44 45 46 47  48 49 4A 4B 4C 4D 4E 4F  @ABCDEFGHIJKLMNO
00000050: 50 51 52 53 54 55 56 57  58 59 5A 5B 5C 5D 5E 5F  PQRSTUVWXYZ[\]^_
00000060: 60 61 62 63 64 65 66 67  68 69 6A 6B 6C 6D 6E 6F  `abcdefghijklmno
00000070: 70 71 72 73 74 75 76 77  78 79 7A 7B 7C 7D 7E 7F  pqrstuvwxyz{|}~.
```
