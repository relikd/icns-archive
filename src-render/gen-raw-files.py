#!/usr/bin/env python3
from lib import SIZES, makedir, byte_, bytes_
from analyze import test_file, Enum
from PIL import Image


#########################
# rgb + argb
#########################

def pack(data):  # type: (list[int]) -> bytes
    ''' Duplicate from icnsutil.PackBytes '''
    ret = []  # type: list[int]
    buf = []  # type: list[int]
    i = 0

    def flush_buf():  # type: () -> None
        # write out non-repeating bytes
        if len(buf) > 0:
            ret.append(len(buf) - 1)
            ret.extend(buf)
            # buf.clear()
            while buf:
                buf.pop()

    end = len(data)
    while i < end:
        arr = data[i:i + 3]
        x = arr[0]
        if len(arr) == 3 and x == arr[1] and x == arr[2]:
            flush_buf()
            # repeating
            c = 3
            while (i + c) < end and data[i + c] == x:
                c += 1
            i += c
            while c > 130:  # max number of copies encodable in compression
                ret.append(0xFF)
                ret.append(x)
                c -= 130
            if c > 2:
                ret.append(c + 0x7D)  # 0x80 - 3
                ret.append(x)
            else:
                i -= c
        else:
            buf.append(x)
            if len(buf) > 127:
                flush_buf()
            i += 1
    flush_buf()
    return bytes_(ret)


def compressed_data(w, h, argb):  # type: (int, int, bool) -> bytes
    sz = w * h
    pattern = [0, 0, 0, 0, 255, 255] * (sz // 6 + 2)
    r = pack(pattern[4:sz + 4])
    g = pack(pattern[2:sz + 2])
    b = pack(pattern[:sz])
    if argb:
        return 'ARGB'.encode() + pack([255] * sz) + r + g + b
    return r + g + b


def uncompressed_data(w, h, argb):  # type: (int, int, bool) -> bytes
    sz = w * h
    pattern = bytes_([0, 0, 0, 0, 0xFF, 0xFF]) * (sz // 6 + 2)
    r = pattern[4:sz + 4]
    g = pattern[2:sz + 2]
    b = pattern[:sz]
    if argb:
        return 'ARGB'.encode() + byte_(0xFF, sz) + r + g + b
    return r + g + b


#########################
# png + jpf
#########################

def px(i):  # type: (int) -> tuple[int, int, int]
    t = i % 6
    if t < 2:
        return (255, 0, 0)
    if t < 4:
        return (0, 255, 0)
    return (0, 0, 255)


#########################
# main
#########################

def generate():  # type: () -> None
    makedir('out-raw-files')
    for s in SIZES:
        fname = 'out-raw-files/%dx%d' % (s, s)
        print('generate ' + fname.split('/')[1])
        # ARGB
        with open(fname + '.argb', 'wb') as fp:
            fp.write(compressed_data(s, s, argb=True))
        with open(fname + '.argbu', 'wb') as fp:
            fp.write(uncompressed_data(s, s, argb=True))
        # RGB
        with open(fname + '.rgb', 'wb') as fp:
            fp.write(compressed_data(s, s, argb=False))
        with open(fname + '.rgbu', 'wb') as fp:
            fp.write(uncompressed_data(s, s, argb=False))
        # PNG
        im = Image.new('RGB', (s, s))
        im.putdata([px(i) for i in range(s*s)])
        im.save(fname + '.png')
        assert test_file(fname + '.png') == Enum.PERFECT
        # JPEG2000
        im.save(fname + '.jpf')
        assert test_file(fname + '.jpf') == Enum.PERFECT


if __name__ == '__main__':
    generate()
