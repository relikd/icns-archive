#!/bin/sh
# Wrapper launches whichever Python is available (min: 2.5 or 3.0)
''':'
for name in python python3; do
    type "$name" > /dev/null 2>&1 && exec "$name" "$0" "$@"
done
exit 1
':'''
import os  # makedirs
import shutil  # copy
from lib import ICNS_TYPES, DATA_TYPES, makedir, write_icns, byte_
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


def generate_variants():  # type: () -> None
    for ext in DATA_TYPES:
        makedir(os.path.join('out-variants', 'icns', ext))
    try:
        Zip = ZipFile('assets/raw-files.zip')
        for s, keys in ICNS_TYPES.items():
            print('generate icns for %dx%d' % (s, s))
            for ext in DATA_TYPES:
                if ext == 'argb+mask' and s not in [16, 32, 48, 128]:
                    continue
                raw = Zip.read('%dx%d.%s' % (s, s, ext.split('+')[0]))
                for key in keys:
                    if key == 'it32' and ext in ['rgb', 'rgbu']:
                        data = byte_(0x00, 4) + raw
                    else:
                        data = raw
                    fn = 'out-variants/icns/%s/%d-%s.icns' % (ext, s, key)
                    mask = mask_for_size(s, ext)
                    write_icns(fn, [(key, data)] + mask)
                    make_app_wrapper(fn)
    finally:
        Zip.close()


if __name__ == '__main__':
    generate_variants()
