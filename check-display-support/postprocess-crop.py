#!/usr/bin/env python3
'''
This script only works if the Finder window has clearly defined edges.
The white backround content must be surrounded by a non-white border.

The frame detection works as follows:
1) load "png/256.png"
2) start with a point (*) guaranteed to be in frame
3) save color as reference lookup
4) go down until color changes (that is the [B]ottom of the frame)
5) repeat process to find [L]eft, [T]op, and [R]ight border

╭───────────────────────────────────────────────────╮
│⊙⊙⊙                                                │
├────────┬──────────────────────────────────────────┤
│        │T--------------------------------------->R│
│        │|                                         │
│        │|                                         │
│        │|                               *         │
│        │|                               |         │
│        │L<------------------------------B         │
╰────────┴──────────────────────────────────────────╯

NOTE:

- Starting macOS 12, the Finder title-bar is transparent unless you hover
over the title-bar. When you start the render script, place your cursor
somewhere near the window title (but avoid cursor and tooltip shadows).

- Starting macOS 26, it is impossible to get a clean window screenshot because
everything is transparently overlapping each other and has shadows (shadows
are really bad for this detection method). --> you must crop manually.
'''
import os
import sys
from PIL import Image

DS_STORE_RECT = (940, 689)  # window size is defined in DS_Store file


def detect_rect(infile):  # type: (str) -> tuple[int, int, int, int]
    ''' Find Finder window content area '''
    x = Image.open(infile, mode='r')
    iw, ih = x.size
    xy = [DS_STORE_RECT[0] - 50, ih - 100]
    needle = x.getpixel(xy)  # should be white
    while xy[1] < ih and x.getpixel(xy) == needle:
        xy[1] += 1
    xy[1] -= 1
    while xy[0] > 0 and x.getpixel(xy) == needle:
        xy[0] -= 1
    xy[0] += 1
    left, bottom = xy
    while xy[1] > 0 and x.getpixel(xy) == needle:
        xy[1] -= 1
    xy[1] += 1
    while xy[0] < iw and x.getpixel(xy) == needle:
        xy[0] += 1
    xy[0] -= 1
    right, top = xy
    return left, top, right, bottom


def auto_crop(infile, rect):  # type: (str, tuple[int, int, int, int]) -> Image
    ''' Use output of `detect_rect()` as second param '''
    x = Image.open(infile, mode='r').crop(rect)
    name = os.path.basename(infile)
    if name.startswith('512-') or name.startswith('1024-'):
        return x.crop((0, 0, 600, x.size[1]))
    if name.startswith('128') or name.startswith('256'):
        return x.crop((0, 0, 600, 340))
    if name.startswith('0-'):
        return x.crop((0, 0, x.size[0], 540))
    return x


def auto_crop_dir(indir):  # type: (str) -> None
    indir = os.path.join(indir, 'app')
    if not os.path.isdir(os.path.join(indir, 'jp2')):
        print('ERROR: %s/jp2/ does not exist' % indir, file=sys.stderr)
        exit(1)

    clip = detect_rect(os.path.join(indir, 'png', '256.png'))
    for base, dirs, files in os.walk(indir):
        for fn in files:
            name, ext = fn.split('.', 1)
            if ext == 'png':  # and name + '.crop.png' not in files:
                pth = os.path.join(base, name)
                auto_crop(pth + '.png', clip).save(pth + '.crop.png')


def m_crop_dir(indir, rect):  # type: (str, list[int]) -> None
    for base, dirs, files in os.walk(indir):
        for fn in files:
            name, ext = fn.split('.', 1)
            if ext == 'png':  # and name + '.crop.png' not in files:
                pth = os.path.join(base, name)
                Image.open(pth + '.png').crop(rect).save(pth + '.crop.png')


if __name__ == '__main__':
    if len(sys.argv) not in [2, 6] or not os.path.exists(sys.argv[1]):
        print('usage: %s <dir> [<left> <top> <right> <bottom>]' %
              os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(0)

    if len(sys.argv) == 2:
        auto_crop_dir(sys.argv[1])
    else:
        m_crop_dir(sys.argv[1], [int(x) for x in sys.argv[2:6]])
