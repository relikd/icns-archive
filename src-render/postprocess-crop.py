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


def detect_rect(infile, x=0, y=0):
    # type: (str, int, int) -> tuple[int, int, int, int]
    ''' Find Finder window content area '''
    im = Image.open(infile, mode='r')
    iw, ih = im.size
    # OS <= 10.4 (800x600)
    if x == 0 or y == 0:
        sx, sy = min(iw, DS_STORE_RECT[0]) - 50, ih - 150
    else:
        sx, sy = x, y

    needle = im.getpixel((sx, sy))  # should be white
    left, right, top, bottom = sx, sx, sy, sy
    while right < (iw - 1) and im.getpixel((right + 1, sy)) == needle:
        right += 1
    while bottom < (ih - 1) and im.getpixel((sx, bottom + 1)) == needle:
        bottom += 1
    while left > 0 and im.getpixel((left - 1, bottom)) == needle:
        left -= 1
    while top > 0 and im.getpixel((right, top - 1)) == needle:
        top -= 1
    # macOS 11+ starts with subtle window shadows. No clear boundaries anymore.
    # macOS 26 is an abomination with quadruple shadows overlapping each other.
    # Alternative search. Start at previous position and try going further.
    left += 3
    while left > 0 and im.getpixel((left - 1, sy)) == needle:
        left -= 1
    top += 3
    while top > 0 and im.getpixel((left, top - 1)) == needle:
        top -= 1
    return left, top, right, bottom


def validate_rect(rect):  # type: (tuple[int, int, int, int]) -> bool
    return rect[2] - rect[0] > 150 and rect[3] - rect[1] > 150


def cut_whitespace(im):  # type: (Image.Image) -> Image.Image
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


def auto_crop(infile, rect):
    # type: (str, tuple[int, int, int, int]) -> Image.Image
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


def find_all_autocrop(root):  # type: (str) -> list[str]
    rv = []
    for base, dirs, files in os.walk(root):
        if os.path.basename(base) != 'app':
            continue
        for fn in [
            os.path.join(base, 'png', '256.png'),
            os.path.join(base, 'alpha-bits.png'),
            os.path.join(base, 'alpha-bits.tiff'),
        ]:
            if not os.path.isfile(fn):
                continue
            print('processing %s' % base)
            rect = detect_rect(fn)
            if not validate_rect(rect):
                print('ERROR: invalid crop %s %s' % (
                    rect, fn.removeprefix(root)))
                continue
            eligible = find_eligible(base)
            for fn in eligible:
                auto_crop(fn, rect).save(os.path.splitext(fn)[0] + '.crop.png')
            rv.extend(eligible)
    return rv


#######################
# manual cropping
#######################

def m_crop_dir(indir, rect):  # type: (str,tuple[int,int,int,int]) -> list[str]
    rv = []
    for fn in find_eligible(indir):
        Image.open(fn).crop(rect).save(os.path.splitext(fn)[0] + '.crop.png')
        rv.append(fn)
    return rv


def m_auto_crop_dir(indir, x, y):  # type: (str, int, int) -> list[str]
    rv = []
    for fn in find_eligible(indir):
        rect = detect_rect(fn, x, y)
        if not validate_rect(rect):
            print('ERROR: invalid crop %s %s' % (rect, fn.removeprefix(indir)))
            continue
        cut_whitespace(Image.open(fn).crop(rect)).save(
            os.path.splitext(fn)[0] + '.crop.png')
        rv.append(fn)
    return rv


def find_eligible(indir):  # type: (str) -> list[str]
    ''' Find all png files which haven't been cropped yet '''
    rv = []
    for base, dirs, files in os.walk(indir):
        for fn in files:
            ext = fn.split('.', 1)[1]  # can be "crop.png" or "collage.png"
            if ext in ['png', 'tiff']:
                rv.append(os.path.join(base, fn))
    return rv


if __name__ == '__main__':
    if len(sys.argv) not in [2, 4, 6] or not os.path.exists(sys.argv[1]):
        scpt = os.path.basename(sys.argv[0])
        print('usage: %s <dir>' % scpt)
        print('       %s <dir> <start-x> <start-y>' % scpt)
        print('       %s <dir> <left> <top> <right> <bottom>' % scpt)
        exit(0)

    root = sys.argv[1]

    if len(sys.argv) == 2:
        needs_cleanup = find_all_autocrop(root)
    elif len(sys.argv) == 4:
        x, y = [int(x) for x in sys.argv[2:]]
        needs_cleanup = m_auto_crop_dir(root, x, y)
    else:
        a, b, c, d = [int(x) for x in sys.argv[2:]]
        needs_cleanup = m_crop_dir(root, (a, b, c, d))

    print('cropped images: %d' % len(needs_cleanup))

    if needs_cleanup:
        ans = input('Delete original files? [y/N] ')
        if ans.lower() == 'y':
            print('cleanup.')
            for old in needs_cleanup:
                os.remove(old)
