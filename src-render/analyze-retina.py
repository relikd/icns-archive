#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from analyze import test_file, sorted_os, printable
from PIL import Image


def print_icns_support():  # type: () -> None
    root = '../collection-edge-cases'
    all_os = sorted_os(os.listdir(root))[4:]
    keys = [
        '16-ic04-ic11', '32-ic05-ic12', '16-icp4-ic11', '32-icp5-ic12',
        '16-is32-ic11', '18-icsb-icsB', '24-sb24-SB24', '32-il32-ic12',
        '128-ic07-ic13', '128-it32-ic13', '256-ic08-ic14', '512-ic09-ic10',
    ]

    print('## icns @2x')
    print()
    print(' Combo   |' + '|'.join(x.ljust(5) for x in all_os))
    print('---------|' + '|'.join('-----' for _ in range(len(all_os))))
    for k in keys:
        print('%s' % '+'.join(k.split('-')[1:]), end='')
        for ver in all_os:
            pth = os.path.join(root, ver, 'icns', 'retina@2x', k + '.icns.png')
            print('| %s  ' % printable(test_file(pth)), end='')
        print()

    print()
    print()
    print('## icns @1x')
    print()
    print(' Combo   |' + '|'.join(x.ljust(5) for x in all_os))
    print('---------|' + '|'.join('-----' for _ in range(len(all_os))))
    for k in keys:
        print('%s' % '+'.join(k.split('-')[1:]), end='')
        for ver in all_os:
            pth = os.path.join(root, ver, 'icns', 'retina', k + '.icns.png')
            try:
                for px in Image.open(pth, mode='r').convert('RGB').getdata():
                    if sum(abs(x-y) for x, y in zip(px, [255, 0, 0])) > 20:
                        print('| ❌  ', end='')
                        break
                else:
                    print('| ✅  ', end='')
            except Exception:
                print('| 🚫  ', end='')
                continue
        print()


if __name__ == '__main__':
    print_icns_support()
