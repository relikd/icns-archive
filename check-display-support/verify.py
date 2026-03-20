#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from lib import DATA_TYPES, ICNS_TYPES
from PIL import Image


def px_diff(pxR, pxG, pxB):  # type: (list[int], list[int], list[int]) -> int
    r = sum(abs(x-y) for x, y in zip(pxR, [255, 0, 0]))
    g = sum(abs(x-y) for x, y in zip(pxG, [0, 255, 0]))
    b = sum(abs(x-y) for x, y in zip(pxB, [0, 0, 255]))
    return r + g + b


def test_file(fname):  # type: (str) -> int
    if not os.path.exists(fname):
        return -2
    if os.path.getsize(fname) == 0:
        return -1
    im = Image.open(fname, mode='r').convert('RGB')
    data = im.getdata()
    r, R, g, G, b, B = data[0], data[1], data[2], data[3], data[4], data[5]
    # assert first 6px are two-px tuples with 3 distinct values RRGGBB
    if r != R or g != G or b != B or r == g or r == b or g == b:
        return 9001
    # assert pixels mostly match R G B
    rgb_diff = px_diff(r, g, b)
    bgr_diff = px_diff(b, g, r)
    if rgb_diff > 200 and bgr_diff > 200:
        return 9002
    # else, deep compare all px (first 6px should repeat indefinitely)
    expected = [r, R, g, G, b, B]
    for i, x in enumerate(data):
        if x != expected[i % 6]:
            return 9003
    if bgr_diff < rgb_diff:
        return 1020  # 1020 because thats the diff for a px-perfect flip
    return rgb_diff


def test_folder(indir):  # type: (str) -> dict[str, list[int]]
    ''' Return `{size"-"key: [err-count per type]}` '''
    rv = {}  # type: dict[str, list[int]]
    for typ in DATA_TYPES:
        base = '%s/%s/' % (indir, typ)
        for s, keys in ICNS_TYPES.items():
            for key in keys:
                fname = '%d-%s.icns.png' % (s, key)
                err = test_file(base + fname)
                rv.setdefault('%d-%s' % (s, key), []).append(err)
    return rv


def printable(num):  # type: (int) -> str
    if num == 0:
        return '✅'  # ok
    if num > 9000:
        return '❌'  # too many errors
    if num == 1020:
        return '🔄'  # colors flipped, BGR instead of RGB
    if num == -1:
        return '🚫'  # input file empty (qlmanage error)
    if num == -2:
        return '  '  # input file never existed (argb+mask)
    return '⚠️'  # just a few px mismatch


def printResults(data):  # type: (dict[str, list[int]]) -> None
    print(' key | size | ' + ' | '.join(x.ljust(5) for x in DATA_TYPES))
    print(':---:|:----:|' + '|'.join(':-----:' for x in DATA_TYPES))
    for k in sorted('%9s' % x for x in data):
        sz, key = k.strip().split('-')
        print('%s | %s |  ' % (key, sz.ljust(4)) + '   |  '.join(
            printable(x) for x in data[k.strip()]))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <dir>' % os.path.basename(sys.argv[0]),
              file=sys.stderr)
        exit(0)

    indir = os.path.join(sys.argv[1], 'icns')
    if not os.path.isdir(os.path.join(indir, 'jp2')):
        print('ERROR: %s/jp2/ does not exist' % indir, file=sys.stderr)
        exit(1)

    printResults(test_folder(indir))
