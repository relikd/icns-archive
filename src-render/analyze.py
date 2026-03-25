#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
from lib import DATA_TYPES, ICNS_TYPES
from PIL import Image

ICNS_TYPES_SET = set(x for _, x in ICNS_TYPES)


#######################################
#
# Verify pixel correctness
#
#######################################

class Enum:
    NEVER = 1  # input file never existed (argb+mask)
    ERROR = 2  # qlmanage error. could not produce preview
    WRONG = 4  # pixel colors dont match at all
    MAN_WRONG = 8  # manually set wrong
    FLIPPED = 16  # colors flipped, BGR instead of RGB
    MAN_GOOD = 32  # manually set good
    GOOD = 64  # nearly perfect match. There is a slight color shift
    PERFECT = 128  # pixel-perfect match


def px_diff(pxR, pxG, pxB):  # type: (list[int], list[int], list[int]) -> int
    r = sum(abs(x-y) for x, y in zip(pxR, [255, 0, 0]))
    g = sum(abs(x-y) for x, y in zip(pxG, [0, 255, 0]))
    b = sum(abs(x-y) for x, y in zip(pxB, [0, 0, 255]))
    return r + g + b


def test_file(fname):  # type: (str) -> int
    if not os.path.exists(fname):
        return Enum.NEVER
    if os.path.getsize(fname) == 0:
        return Enum.ERROR
    im = Image.open(fname, mode='r').convert('RGB')
    data = im.getdata()
    r, R, g, G, b, B = data[0], data[1], data[2], data[3], data[4], data[5]
    # assert first 6px are two-px tuples with 3 distinct values RRGGBB
    if r != R or g != G or b != B or r == g or r == b or g == b:
        return Enum.WRONG
    # assert pixels mostly match R G B
    rgb_diff = px_diff(r, g, b)
    bgr_diff = px_diff(b, g, r)
    if rgb_diff > 200 and bgr_diff > 200:
        return Enum.WRONG
    # else, deep compare all px (first 6px should repeat indefinitely)
    expected = [r, R, g, G, b, B]
    for i, x in enumerate(data):
        if x != expected[i % 6]:
            return Enum.WRONG
    if bgr_diff < rgb_diff:
        return Enum.FLIPPED
    return Enum.PERFECT if rgb_diff == 0 else Enum.GOOD


#######################################
#
# DB creation
#
#######################################

class DB:
    def __init__(self, fname):  # type: (str) -> None
        self.con = sqlite3.connect(fname)
        self.cur = self.con.cursor()
        self.create()

    def save(self):  # type: () -> None
        self.con.commit()

    def create(self):  # type: () -> None
        self.cur.executescript('''
            CREATE TABLE IF NOT EXISTS tbl (
                os TEXT(6) NOT NULL,
                typ TEXT(9) NOT NULL,
                size INT NOT NULL,
                key TEXT(4) NOT NULL,
                icns INT DEFAULT 0,
                app INT DEFAULT 0
            );
        ''')

    def all_os(self):  # type: () -> list[str]
        return [x[0] for x in db.cur.execute('SELECT DISTINCT os FROM tbl')]

    def add(self, os_ver):  # type: (str) -> None
        self.cur.executemany(
            'INSERT INTO tbl (os, typ, size, key) VALUES (?, ?, ?, ?)',
            [(os_ver, t, s, k) for t in DATA_TYPES for s, k in ICNS_TYPES])

    def remaining_icns(self):  # type: () -> list[tuple[str,str,int,str]]
        return list(self.cur.execute(
            'SELECT os, typ, size, key FROM tbl WHERE icns=0 ORDER BY ROWID'))

    def remaining_manually(self):  # type: () -> list[tuple[str,str,bool,bool]]
        return list(self.cur.execute('''
            SELECT os, typ, icns==0, app==0 FROM tbl
            WHERE icns=0 OR app=0 GROUP BY os, typ ORDER BY ROWID
        '''))

    def pre_populate(self, os_list):  # type: (DB, list[str]) -> None
        ''' Create exhaustive type table with empty values '''
        done = set(self.all_os())
        for os_name in os_list:
            if os_name not in done:
                self.add(os_name)
        self.save()

    def populate_automatically(self, root):  # type: (DB, str) -> None
        '''Populate (still) empty values with automatically testable results'''
        for os_ver, typ, size, key in self.remaining_icns():
            par = os.path.join(root, os_ver, 'icns', typ)
            if not os.path.isdir(par):
                continue  # 10.5 and earlier cant generate qlmanage thumbnails
            fn = os.path.join(par, '%d-%s.icns.png' % (size, key))
            # update existing
            self.cur.execute(
                'UPDATE tbl SET icns=? WHERE os=? AND typ=? AND key=?',
                [test_file(fn), os_ver, typ, key])
        self.save()

    def populate_manually(self, root):  # type: (DB, str) -> None
        '''Populate (still) empty values with manual input'''
        print('Manual check. Enter all keys which display properly.')
        print('(separated by space)')
        for os_ver, typ, needs_icns, needs_app in self.remaining_manually():
            if needs_icns:
                self._ask(os_ver, 'icns', typ)
            if needs_app:
                self._ask(os_ver, 'app', typ)
        print('done.')

    def _ask(self, os_ver, grp, typ):  # type: (str, str, str) -> None
        ans = input('%s  %s  %s: ' % (os_ver, grp, typ))
        good = set(ans.split())
        bad = ICNS_TYPES_SET - good
        unknown_keys = good - ICNS_TYPES_SET
        if unknown_keys:
            print('ERROR: unknown keys %s. try again.' % (unknown_keys))
            self._ask(os_ver, grp, typ)
            return

        # compute reply variants
        for reply, keys in [(Enum.MAN_GOOD, good), (Enum.MAN_WRONG, bad)]:
            for key in keys:
                self.cur.execute(
                    'UPDATE tbl SET %s=? WHERE os=? AND typ=? AND key=?' % grp,
                    [reply, os_ver, typ, key])
        self.save()

    def cleanup(self):  # type: () -> None
        # remove entries which weren't tested
        self.cur.executescript('''
            DELETE FROM tbl
            WHERE typ='argb+mask' AND size NOT IN (16, 32, 48, 128);

            DELETE FROM tbl
            WHERE os='10.4' AND key NOT IN (
                'ic07', 'ic08', 'ic09', 'ic10', 'icp4', 'icp5', 'icp6', 'ih32',
                'il32', 'is32', 'it32');

            DELETE FROM tbl
            WHERE os IN ('9.2', '10.0', '10.1', '10.2', '10.3')
                AND key NOT IN ('ih32', 'il32', 'is32', 'it32');
        ''')
        self.save()

    def select(self, os_ver, typ, key):  # type: (str,str,str)->tuple[int,int]
        return self.cur.execute('''
            SELECT icns, app FROM tbl WHERE os=? AND typ=? AND key=?
        ''', (os_ver, typ, key)).fetchone() or (Enum.NEVER, Enum.NEVER)

    def good_fields(self, group):  # type: (str) -> list[tuple[str, str, str]]
        ''' Return `(key, typ, os-list)` where icns and/or app are good. '''
        fields = (group.split('+')[0], group.split('+')[-1])
        return self.cur.execute('''
            SELECT key, typ, group_concat(DISTINCT os) FROM tbl
            WHERE %s>=? AND %s>=? GROUP BY key, typ
        ''' % fields, [Enum.MAN_GOOD, Enum.MAN_GOOD]).fetchall()

    def new_keys(self, group):  # type: (str) -> dict[str, dict[str, set[str]]]
        ''' Return `{(os, typ): key-set}`. '''
        fields = (group.split('+')[0], group.split('+')[-1])
        return dict(
            (o, dict(
                (t, set(k.split(',')))
                for t, k in self.cur.execute('''
                    SELECT typ, group_concat(DISTINCT key) FROM tbl
                    WHERE os=? AND %s>=? AND %s>=? GROUP BY typ
                ''' % fields, [o, Enum.MAN_GOOD, Enum.MAN_GOOD])))
            for o in self.all_os())


#######################################
#
# Print output
#
#######################################

def printable(num):  # type: (int) -> str
    if num in [Enum.PERFECT, Enum.GOOD, Enum.MAN_GOOD]:
        return '✅'
    if num in [Enum.WRONG, Enum.MAN_WRONG]:
        return '❌'
    if num == Enum.FLIPPED:
        return '🔄'
    if num == Enum.ERROR:
        return '🚫'
    if num == Enum.NEVER:
        return '  '
    return '⚠️'  # should never happen


def matches_expectation(icns, app):  # type: (int, int) -> bool
    return icns == app or \
        (app == Enum.MAN_GOOD and icns >= Enum.MAN_GOOD) or \
        (app == Enum.MAN_WRONG and icns <= Enum.MAN_WRONG)


def tbl_head(columns, width, center=False):  # type:(list[str],int,bool) -> str
    ch = ':' if center else '-'
    pretty = [x.ljust(width) for x in columns]
    return ' key | size | ' + ' | '.join(x for x in pretty) + \
        '\n:---:|:----:|' + '|'.join(ch + '-' * len(x) + ch for x in pretty)


def desc_timeline(min_os, max_os):  # type: (str, str) -> str
    return '''
earliest version tested: OS %(min)s%(nl)s
latest version tested: macOS %(max)s

Shows the first OS version which renders the icon correctly.%(nl)s
=> full correctness: `icns+app`%(nl)s
=> partial correctness: either `icns` or `app`
''' % {'nl': '  ', 'min': min_os, 'max': max_os}


def tbl_timeline_tldr(db, group, os_list):  # type: (DB, str, list[str]) -> str
    ''' Quick overview timeline (mixed types) '''
    columns = ['jp2', 'jpf', 'png', 'rgb', 'argb', 'argb+mask']
    updates = db.new_keys(group)
    known = dict((x, set('')) for x in columns)

    txt = ' OS   | new keys\n------|----------'
    for os_ver in os_list:
        new_keys = set()
        for typ in columns:
            this_keys = set(updates[os_ver].get(typ, []))
            new_keys |= this_keys - known[typ]
            known[typ] |= this_keys
        if new_keys:
            txt += '\n%s | %s' % (os_ver.ljust(5), ', '.join(sorted(new_keys)))
    return txt + '\n'


def tbl_timeline_full(db, group):  # type: (DB, str) -> str
    ''' Detailed timeline with version usage '''
    columns = ['jp2', 'jpf', 'png', 'rgb', 'argb', 'argb+mask']
    usage = db.good_fields(group)

    txt = tbl_head(columns, 5)
    for sz, key in ICNS_TYPES:
        txt += '\n%s | %4d ' % (key, sz)
        for typ in columns:
            os_range = next((sorted_os(o.split(','))
                            for k, t, o in usage
                            if k == key and t == typ), None)
            if os_range is None:
                txt += '|       '
            else:
                txt += '| %s ' % os_range[0].ljust(5)
    return txt + '\n'


def desc_detailed():  # type: () -> str
    return '''
Legend:%(nl)s
✅ The image renders correctly.%(nl)s
🔄 The color order is flipped. BGR instead of RGB.%(nl)s
❌ Does not render correct image.%(nl)s
🚫 Could not render / rendering error / no output.

### How to read the results

This is a combined table. Showing results of both, icns and app rendering.
If a cell contains only one emoji, the result is valid for both. If the cell is
split up, the first emoji applies to icns rendering and the second emoji to app
rendering (it is the same icns file, just put inside an app bundle).

❌/✅ means the icon cannot be rendered in a plain `icns` file but renders fine
when used inside an `.app` bundle (the very same icns file!). Likewise, ✅/❌
renders standalone icns files fine but fails when bundled in an app.

Empty cells were not tested at all. E.g., for `argb+mask` only sizes 16, 32,
48, and 128 are relevant because no other mask-sizes exist. Early OS versions
skip some keys because generating a preview gets progressively harder the older
it gets. Though I did preview all keys in 10.3 and 10.4 (even if the cells are
empty) and they are indeed non-rendering.
''' % {'nl': '  '}  # markdown new line


def tbl_os_detailed(db, os_ver):  # type: (DB, str) -> str
    columns = ['jp2', 'jpf', 'png', 'rgb', 'argb', 'argb+mask']

    txt = tbl_head(columns, 5, center=True)
    omitted = []
    for sz, key in ICNS_TYPES:
        pairs = [db.select(os_ver, typ, key) for typ in columns]

        # skip keys/lines with no test result
        if all(x == (Enum.NEVER, Enum.NEVER) for x in pairs):
            omitted.append(key)
            continue

        txt += '\n%s | %4d ' % (key, sz)
        for icns, app in pairs:
            txt += '| ' + printable(icns)
            if matches_expectation(icns, app):
                txt += '    '
            else:
                txt += '/' + printable(app) + ' '
    if omitted:
        txt += '\n\n*omitted*: ' + ', '.join(omitted)
    return txt + '\n'


def write_markdown(db, outfile):  # type: (DB, str) -> None
    os_list = sorted_os(db.all_os())
    with open(outfile, 'w') as fp:
        fp.write('''# Rendering of .icns and .app icons in macOS – Analysis

Table of contents:
- [Detailed render results](#detailed-render-results)
- [Newly introduced keys](#newly-introduced-keys)
''')
        fp.write('\n\n## Detailed render results\n')
        fp.write(desc_detailed())

        for os_ver in os_list:
            fp.write('\n\n### macOS %s' % os_ver)
            fp.write('\n\n' + tbl_os_detailed(db, os_ver))

        fp.write('\n\n## Newly introduced keys\n')
        fp.write(desc_timeline(os_list[0], os_list[-1]))

        for group in ['icns+app', 'icns', 'app']:
            fp.write('\n\n## Render success: %s' % group)
            fp.write('\n\n' + tbl_timeline_tldr(db, group, os_list))
            fp.write('\n\n' + tbl_timeline_full(db, group))


#######################################
#
# Main entry
#
#######################################

def sorted_os(in_list):  # type: (list[str]) -> list[str]
    ''' Sort by OS version number. '''
    return sorted(filter(lambda x: x[0].isdigit(), in_list),
                  key=lambda x: [int(n) for n in x.split()[0].split('.')])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s <src-dir> <db-path>' % os.path.basename(sys.argv[0]))
        exit(0)

    _, root, db_path = sys.argv
    if not os.path.isdir(os.path.join(root, '10.15')):
        print('ERROR: "%s" does not contain OS versions' % root)
        exit(1)

    db = DB(db_path)
    db.pre_populate(sorted_os(os.listdir(root)))
    db.populate_automatically(root)
    db.populate_manually(root)
    db.cleanup()
    write_markdown(db, os.path.splitext(db_path)[0] + '-report.md')
