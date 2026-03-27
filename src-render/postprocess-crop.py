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
    xy = [DS_STORE_RECT[0] - 50, ih - 150]
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


def cut_whitespace(im):  # type: (Image) -> Image
    ''' Remove empty whitespace at the bottom / right '''
    needle = im.getpixel((0, 0))
    w, h = im.size
    # 5px grid sampling bottom-up
    for y in range(h - 10, 0, -5):
        for x in range(5, w, 5):
            if im.getpixel((x, y)) != needle:
                im = im.crop((0, 0, w, min(y + 15, h)))
                break
        else:
            continue
        break
    # right-to-left sampling
    w, h = im.size
    for x in range(w - 10, 0, -5):
        for y in range(5, h, 5):
            if im.getpixel((x, y)) != needle:
                return im.crop((0, 0, min(x + 20, w), h))
    return im


def auto_crop(infile, rect):  # type: (str, tuple[int, int, int, int]) -> Image
    ''' Use output of `detect_rect()` as second param '''
    im = Image.open(infile, mode='r').crop(rect)
    name = os.path.basename(infile)
    if name.startswith('512-') or name.startswith('1024-'):
        return im.crop((0, 0, 600, im.size[1]))
    if name.startswith('128') or name.startswith('256'):
        return im.crop((0, 0, 600, 340))
    if name.startswith('0-'):
        return im.crop((0, 0, im.size[0], 540))
    # else: edge cases
    return cut_whitespace(im)


def auto_crop_dir(indir, rect):  # type: (str, tuple[int,int,int,int]) -> int
    rv = 0
    for base, dirs, files in os.walk(indir):
        for fn in files:
            name, ext = fn.split('.', 1)
            if ext == 'png':  # and name + '.crop.png' not in files:
                pth = os.path.join(base, name)
                auto_crop(pth + '.png', rect).save(pth + '.crop.png')
                rv += 1
    return rv


def m_crop_dir(indir, rect):  # type: (str, list[int]) -> int
    rv = 0
    for base, dirs, files in os.walk(indir):
        for fn in files:
            name, ext = fn.split('.', 1)
            if ext in ['png', 'tiff']:
                pth = os.path.join(base, name)
                Image.open(pth + '.' + ext).crop(rect).save(pth + '.crop.png')
                rv += 1
    return rv


if __name__ == '__main__':
    if len(sys.argv) not in [2, 6] or not os.path.exists(sys.argv[1]):
        print('usage: %s <dir> [<left> <top> <right> <bottom>]' %
              os.path.basename(sys.argv[0]), file=sys.stderr)
        exit(0)

    root = sys.argv[1]

    if len(sys.argv) == 2:
        for fn in [
            os.path.join(root, 'app', 'png', '256.png'),
            os.path.join(root, 'app', 'alpha-bits.png')
        ]:
            if os.path.isfile(fn):
                c = auto_crop_dir(os.path.join(root, 'app'), detect_rect(fn))
                print('cropped %s images' % c)
                exit(0)
        print('ERROR: Could not detect directory structure', file=sys.stderr)
        exit(1)
    else:
        c = m_crop_dir(root, [int(x) for x in sys.argv[2:6]])
        print('cropped %s images' % c)
