#!/usr/bin/env python3
import os
import sys
from lib import DATA_TYPES
from PIL import Image


def compose(indir):  # type: (str) -> None
    w, _ = Image.open(os.path.join(indir, 'png', '0-sm.crop.png')).size
    _, h = Image.open(os.path.join(indir, 'png', '1024-ic10.crop.png')).size
    for typ in DATA_TYPES:
        if typ == 'argb+mask':
            size = (max(w, 600), 540//3*2 + 340)
            data = {
                '0-sm': (0, 0),
                '128': (0, 540//3*2),
            }
        else:
            size = (3 * 600, 2*340 + h)
            data = {
                '0-sm': (0, 0),
                '128': (1200, 0),
                '256': (1200, 340),
                '512-ic09': (0, 2*340),
                '512-ic14': (600, 2*340),
                '1024-ic10': (1200, 2*340),
            }

        im = Image.new('RGB', size, color=(255, 255, 255))
        for k, v in data.items():
            im.paste(Image.open(os.path.join(indir, typ, k + '.crop.png')), v)
        im.save(os.path.join(indir, typ + '.collage.png'))


if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print('usage: %s <dir>' %
              os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(0)

    root = sys.argv[1].rstrip('/')
    if os.path.basename(root) != 'app' or \
            not os.path.isdir(os.path.join(root, 'jp2')):
        print('ERROR: Not an app dir')
        exit(1)

    compose(root)
