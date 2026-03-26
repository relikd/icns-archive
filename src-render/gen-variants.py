#!/bin/sh
# Wrapper launches whichever Python is available (min: 2.5 or 3.0)
''':'
for name in python python3; do
    type "$name" > /dev/null 2>&1 && exec "$name" "$0" "$@"
done
exit 1
':'''
import os
import sys
import shutil  # copy
from lib import ICNS_TYPES, DATA_TYPES, makedir, write_icns, byte_, bytes_
from zipfile import ZipFile


def make_app_wrapper(path):  # type: (str) -> None
    base = path.replace('icns', 'app') + '/Contents'
    makedir(base + '/MacOS')
    makedir(base + '/Resources')
    with open(base + '/Info.plist', 'w') as fp:
        fp.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>b</string>
    <key>CFBundleIconFile</key>
    <string>i</string>
</dict>
</plist>''')
    with open(base + '/PkgInfo', 'w') as fp:
        fp.write('APPL????\n')
    if not os.path.islink(base + '/MacOS/b'):
        os.symlink('/bin/sh', base + '/MacOS/b')
    shutil.copy(path, base + '/Resources/i.icns')
    print('.', end='')


def mask_for_size(size, typ):  # type: (int, str) -> list[tuple[str, bytes]]
    if typ in ['rgb', 'rgbu', 'argb+mask']:
        if size == 16:
            return [('s8mk', byte_(0xFF, 16 * 16))]
        if size == 32:
            return [('l8mk', byte_(0xFF, 32 * 32))]
        if size == 48:
            return [('h8mk', byte_(0xFF, 48 * 48))]
        if size == 128:
            return [('t8mk', byte_(0xFF, 128 * 128))]
    return []


def generate_variants(root):  # type: (str) -> None
    base = os.path.join(root, 'variants', 'icns')
    for ext in DATA_TYPES:
        makedir(os.path.join(base, ext))
    try:
        Zip = ZipFile('assets/raw-files.zip')
        print('generate variants: ', end='')
        for s, key in ICNS_TYPES:
            for ext in DATA_TYPES:
                if ext == 'argb+mask' and s not in [16, 32, 48, 128]:
                    continue
                raw = Zip.read('%dx%d.%s' % (s, s, ext.split('+')[0]))
                if key == 'it32' and ext in ['rgb', 'rgbu']:
                    data = byte_(0x00, 4) + raw
                else:
                    data = raw
                fn = os.path.join(base, ext, '%d-%s.icns' % (s, key))
                mask = mask_for_size(s, ext)
                write_icns(fn, [(key, data)] + mask)
                make_app_wrapper(fn)
        print(' done.')
    finally:
        Zip.close()


def generate_edge_cases(root):  # type: (str) -> None
    base = os.path.join(root, 'edge-cases', 'icns')
    for sub in ['compression', 'compression-w-fix', 'alpha-precedence',
                'alpha-bits', 'retina']:
        makedir(os.path.join(base, sub))

    try:
        Zip = ZipFile('assets/raw-edge-cases.zip')
        print('generate edge-cases: ', end='')

        # Test ARGB blue channel issue
        #
        # last byte of compression is ignored even if it is repeating

        for key, sz, ext in [
            ('is32', 16, 'rgb'), ('il32', 32, 'rgb'),
            ('ih32', 48, 'rgb'), ('it32', 128, 'rgb'),
            ('icp6', 48, 'argb'), ('ic04', 16, 'argb'),
            ('ic05', 32, 'argb'), ('icsb', 18, 'argb'),
            ('icp4', 16, 'argb'), ('icp5', 32, 'argb'),
        ]:
            fname = '%s-%s.icns' % (ext, key)
            data = Zip.read('solid-blue-%d.%s' % (sz, ext))
            if key == 'it32':
                data = byte_(0x00, 4) + data
            # with plain compression
            fn = os.path.join(base, 'compression', fname)
            write_icns(fn, [(key, data)] + mask_for_size(sz, ext))
            make_app_wrapper(fn)
            # with null-byte "fix"
            fn = os.path.join(base, 'compression-w-fix', fname)
            write_icns(fn, [(key, data + byte_(0))] + mask_for_size(sz, ext))
            make_app_wrapper(fn)

        # Test alpha mask mixing
        #
        #                  .––.        .––.
        # image with alpha | /  + mask  \ | => which wins?
        #                  |/            \|

        mask_keys = {16: 's8mk', 32: 'l8mk', 48: 'h8mk', 128: 't8mk'}
        for sz, key in [
            (16, 'icp4'), (32, 'icp5'), (48, 'icp6'),
            (16, 'ic04'), (32, 'ic05'),
            (48, 'SB24'), (128, 'ic07'), (32, 'ic11'),
        ]:
            mask = Zip.read('half-mask-%d.a' % (sz))
            pth = os.path.join(base, 'alpha-precedence')
            for ext in ['argb', 'png', 'jpf']:
                print('.', end='')
                data = Zip.read('half-green-%d.%s' % (sz, ext))
                fn = os.path.join(pth, '%s-%s.icns' % (ext, key))
                write_icns(fn, [(key, data), (mask_keys[sz], mask)])
                make_app_wrapper(fn)

        # Test RGB + 8-bit icon
        #
        # because of wiki issue that says "il32+icl8 ignores transparency"

        bit_icons = {16: 'ics8', 32: 'icl8', 48: 'ich8'}
        for sz, key in [(16, 'is32'), (32, 'il32'), (48, 'ih32')]:
            mask = Zip.read('half-mask-%d.a' % (sz))
            data = Zip.read('solid-red-%d.rgb' % (sz))
            if key == 'it32':
                data = byte_(0x00, 4) + data
            content = [(key, data), (bit_icons[sz], byte_(0xFF, sz * sz))]

            fn = os.path.join(base, 'alpha-bits', 'rgb-%s-nomask.icns' % (key))
            write_icns(fn, content)
            make_app_wrapper(fn)

            fn = os.path.join(base, 'alpha-bits', 'rgb-%s-mask.icns' % (key))
            write_icns(fn, content + [(mask_keys[sz], mask)])
            make_app_wrapper(fn)

        # Test Retina combinations
        #
        # Will unrenderable @2x icons render if the @1x is attached?

        try:
            ZipRaw = ZipFile('assets/raw-files.zip')
            for sz, key1, ext1, key2, _ in [
                (16, 'is32', 'rgb', 'ic11', 'png'),
                (16, 'icp4', 'rgb', 'ic11', 'png'),
                (16, 'ic04', 'argb', 'ic11', 'png'),

                (32, 'il32', 'rgb', 'ic12', 'png'),
                (32, 'icp5', 'rgb', 'ic12', 'png'),
                (32, 'ic05', 'argb', 'ic12', 'png'),

                (18, 'icsb', 'argb', 'icsB', 'png'),
                (24, 'sb24', 'png', 'SB24', 'png'),
                (128, 'ic07', 'png', 'ic13', 'png'),
                (128, 'it32', 'rgb', 'ic13', 'png'),
                (256, 'ic08', 'png', 'ic14', 'png'),
                (512, 'ic09', 'png', 'ic10', 'png'),
            ]:
                data1 = Zip.read('solid-red-%d.%s' % (sz, ext1))
                data2 = ZipRaw.read('%dx%d.png' % (sz * 2, sz * 2))
                if key1 == 'it32':
                    data1 = byte_(0x00, 4) + data1
                fn = os.path.join(base, 'retina', '%s-%s.icns' % (key1, key2))
                write_icns(fn, [
                    (key1, data1), (key2, data2)] + mask_for_size(sz, ext1))
                make_app_wrapper(fn)
        finally:
            ZipRaw.close()

        print(' done.')
    finally:
        Zip.close()


def generate_color_palette(root):  # type: (str) -> None
    fn = os.path.join(root, 'color-palette')
    print('generate color palette.')
    write_icns(fn + '-8.icns', [
        ('ics8', bytes_(range(256)))])
    write_icns(fn + '-4.icns', [
        ('ics4', bytes_(i + (i << 4) for i in range(16) for _ in range(8)))])
    write_icns(fn + '-2.icns', [
        ('ics#', bytes_([0] * 16 + [255] * 16 + [15] * 32))])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: %s <out-dir>' %
              os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(0)

    root = sys.argv[1]
    if os.path.exists(root):
        print('<out-dir> already exists', file=sys.stderr)
        exit(1)

    makedir(root)
    generate_color_palette(root)
    generate_variants(root)
    generate_edge_cases(root)
