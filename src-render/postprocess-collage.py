#!/usr/bin/env python3
import os
import sys
from lib import DATA_TYPES
from PIL import Image


def compose(indir):  # type: (str) -> list[str]
    rv = []
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
        for prefix, pos in data.items():
            fn = os.path.join(indir, typ, prefix + '.crop.png')
            im.paste(Image.open(fn), pos)
            rv.append(fn)
        im.save(os.path.join(indir, typ + '.collage.png'))
    return rv


def find_eligible(root):  # type: (str) -> list[str]
    ''' Find all "app" folder which contain a "0-sm.crop.png" file '''
    rv = []
    for base, dirs, files in os.walk(root):
        if 'app' in dirs:
            path = os.path.join(base, 'app')
            if os.path.isfile(os.path.join(path, 'png', '0-sm.crop.png')):
                rv.append(path)
    return rv


if __name__ == '__main__':
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print('usage: %s <dir>' %
              os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(0)

    count = 0
    needs_cleanup = []
    for path in find_eligible(sys.argv[1]):
        print('processing %s' % path)
        needs_cleanup.extend(compose(path))
        count += 1

    print('new compositions: %d' % count)

    if needs_cleanup:
        ans = input('Delete original files? [y/N] ')
        if ans.lower() == 'y':
            print('cleanup.')
            for old_f in needs_cleanup:
                os.remove(old_f)
            for old_d in set(os.path.dirname(x) for x in needs_cleanup):
                if not os.listdir(old_d):
                    os.removedirs(old_d)
