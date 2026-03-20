#!/bin/sh
# Wrapper launches whichever Python is available (min: 2.6 or 3.0)
''':'
for name in python python3; do
    type "$name" > /dev/null 2>&1 && exec "$name" "$0" "$@"
done
exit 1
':'''

import os
import sys
import struct
if False:  # TYPE_CHECKING
    from typing import BinaryIO, Iterator  # noqa: F401 # novermin


ICON_KEYS = [
    'icns',
    'ICON',  # 32x32 mono
    'ics#', 'ics4', 'ics8',  # 16x16
    'icm#', 'icm4', 'icm8',  # 16x12
    'ICN#', 'icl4', 'icl8',  # 32x32
    'ich#', 'ich4', 'ich8',  # 48x48
]


def findType(fp, needle):  # type: (BinaryIO, bytes) -> tuple[int, int]
    type_count = struct.unpack('>H', fp.read(2))[0]
    for _ in range(type_count + 1):  # plus one
        typ, count, offset = struct.unpack('>4sHH', fp.read(8))
        if typ == needle:
            return offset, count + 1  # plus one
    return 0, 0


def iterIcns(fp, key):  # type: (BinaryIO, bytes) -> Iterator[tuple[str,bytes]]
    fp.seek(0)
    data_offset, map_offset = struct.unpack('>II', fp.read(8))

    # start of map
    fp.seek(map_offset + 24)
    type_off, name_off = struct.unpack('>HH', fp.read(4))

    # start of types
    fp.seek(map_offset + type_off)
    res_off, res_count = findType(fp, key)

    # start of resource list
    res_off += map_offset + type_off
    for i in range(res_count):
        fp.seek(res_off + i * 12)
        r_id, n_off, d_off = struct.unpack('>HHI', fp.read(8))
        d_off = d_off & 0x00FFFFFF  # first byte are bitflags

        # read name
        if n_off == 0xFFFF:
            name = str(i)
        else:
            fp.seek(map_offset + name_off + n_off)
            n_len = struct.unpack('>B', fp.read(1))[0]
            name = fp.read(n_len).decode('mac_roman')

        # data
        fp.seek(data_offset + d_off)
        d_len = struct.unpack('>I', fp.read(4))[0]
        data = fp.read(d_len)

        yield name, data


def export(fname, icnsOnly=True):  # type: (str, bool) -> int
    count = 0
    try:
        with open(fname + '/..namedfork/rsrc', 'rb') as fpr:
            for key in ['icns'] if icnsOnly else ICON_KEYS:
                dirname = fname + '.rsrc/' + key
                for name, data in iterIcns(fpr, key.encode()):
                    if count == 0:
                        print(fname)
                    count += 1
                    if not os.path.exists(dirname):
                        os.makedirs(dirname)
                    with open(dirname + '/' + name + '.icns', 'wb') as fpw:
                        if key != 'icns':
                            fpw.write('icns'.encode())
                            fpw.write(struct.pack('>I', len(data) + 16))
                            fpw.write(key.encode())
                            fpw.write(struct.pack('>I', len(data) + 8))
                        fpw.write(data)
            if count > 0:
                print('  %d icons' % count)
    except Exception:
        pass
    return count


if __name__ == '__main__':
    allKeys = '-a' in sys.argv
    args = [x for x in sys.argv if x != '-a']

    if len(args) != 2:
        print('usage: %s [-a] <file or dir>' % os.path.basename(args[0]))
        print('  -a: include icon fields which are not stored in icns wrapper')
        exit(0)

    if not os.path.exists(args[1]):
        print('ERROR: Argument <file or dir> must exist')
        exit(1)

    total = 0
    if os.path.isfile(args[1]):
        total += export(args[1], not allKeys)
    else:
        for base, _, files in os.walk(sys.argv[1]):
            for f in files:
                total += export(os.path.join(base, f), not allKeys)
    print('done. %d icons' % total)
