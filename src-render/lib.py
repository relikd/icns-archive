#!/usr/bin/env python3
import os
import struct  # pack
if False:  # TYPE_CHECKING
    from typing import Iterable  # noqa: F401 # novermin


DATA_TYPES = ['jp2', 'jpf', 'png', 'rgb', 'argb', 'argb+mask', 'argbu', 'rgbu']
ICNS_TYPES = [
    # 24-bit RGB
    (16, 'is32'), (32, 'il32'), (48, 'ih32'), (128, 'it32'),
    (16, 'icp4'), (32, 'icp5'), (48, 'icp6'),
    # ARGB
    (16, 'ic04'), (32, 'ic05'), (18, 'icsb'),
    # PNG, JPG2000
    (36, 'icsB'), (24, 'sb24'), (48, 'SB24'),
    (128, 'ic07'), (256, 'ic08'), (512, 'ic09'), (1024, 'ic10'),
    (32, 'ic11'), (64, 'ic12'), (256, 'ic13'), (512, 'ic14'),
]
SIZES = sorted(set(x for x, _ in ICNS_TYPES))


def makedir(fname):  # type: (str) -> None
    if not os.path.isdir(fname):
        os.makedirs(fname)


def write_icns(fname, fields):  # type: (str, list[tuple[str, bytes]]) -> None
    with open(fname, 'wb') as fp:
        fp.write('icns'.encode())
        fp.write(struct.pack('>I', 8 + sum(8 + len(v) for k, v in fields)))
        for k, v in fields:
            fp.write(k.encode())
            fp.write(struct.pack('>I', 8 + len(v)))
            fp.write(v)


def byte_(byte, copies=1):  # type: (int, int) -> bytes
    ''' Python 2 compatible int-to-bytes conversion '''
    return struct.pack('B', byte) * copies


def bytes_(bytelist):  # type: (Iterable[int]) -> bytes
    ''' Python 2 compatible int-to-bytes conversion '''
    return bytes().join(struct.pack('B', x) for x in bytelist)
