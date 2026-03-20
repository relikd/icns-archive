#!/usr/bin/env python3
import os
import struct  # pack

SIZES = [16, 18, 24, 32, 36, 48, 64, 128, 256, 512, 1024]
DATA_TYPES = ['jp2', 'jpf', 'png', 'rgb', 'argb', 'argb+mask', 'argbu', 'rgbu']
ICNS_TYPES = {
    16: ['is32', 'icp4', 'ic04'],
    18: ['icsb'],
    24: ['sb24'],
    32: ['il32', 'icp5', 'ic11', 'ic05'],
    36: ['icsB'],
    48: ['ih32', 'icp6', 'SB24'],
    64: ['ic12'],
    128: ['it32', 'ic07'],
    256: ['ic08', 'ic13'],
    512: ['ic09', 'ic14'],
    1024: ['ic10'],
}


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


def bytes_(bytelist):  # type: (list[int]) -> bytes
    ''' Python 2 compatible int-to-bytes conversion '''
    return bytes().join(struct.pack('B', x) for x in bytelist)
