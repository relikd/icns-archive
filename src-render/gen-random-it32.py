#!/usr/bin/env python3
import os
from lib import makedir, write_icns, byte_, bytes_
from zipfile import ZipFile
from random import randint


def generate_random_it32_header(root):  # type: (str) -> None
    print('generating random it32 header')
    makedir(root)
    with ZipFile('assets/raw-files.zip') as Zip:
        with Zip.open('128x128.rgb') as f:
            data = f.read()

    def random_header():  # type: () -> bytes
        return bytes_([randint(0x00, 0xFF) for _ in range(4)])

    for i in range(100):
        write_icns(os.path.join(root, '%d.icns' % i), [
            ('it32', random_header() + data),
            ('t8mk', byte_(0xFF, 16384)),
        ])


if __name__ == '__main__':
    generate_random_it32_header(os.path.join('build', 'random-it32'))
