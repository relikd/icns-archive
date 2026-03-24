#!/usr/bin/env python3
import os
import sys
import struct
import sqlite3
from zipfile import ZipFile
if False:  # TYPE_CHECKING
    from typing import Iterator  # noqa: F401 # novermin

KNOWN_BBINARY = [
    b'ICON', b'ICN#', b'icm#', b'icm4', b'icm8', b'ics#', b'ics4', b'ics8',
    b'is32', b's8mk', b'icl4', b'icl8', b'il32', b'l8mk', b'ich#', b'ich4',
    b'ich8', b'ih32', b'h8mk', b'it32', b't8mk', b'icp4', b'icp5',
]
KNOWN_IMG = [
    b'icp6', b'ic07', b'ic08', b'ic09', b'ic10', b'ic11', b'ic12', b'ic13',
    b'ic14', b'ic04', b'ic05', b'icsb', b'icsB', b'sb24', b'SB24',
]
KNOWN_ICNS = [
    b'tile', b'over', b'open', b'odrp', b'sbpp', b'slct', b'sbtp',
    b'\xff\xda:]', b'\xFD\xD9\x2F\xA8',
]
KNOWN_INFO = [b'TOC ', b'icnV', b'name', b'info']
KNOWN = KNOWN_BBINARY + KNOWN_IMG + KNOWN_INFO + KNOWN_ICNS


class DB:
    def __init__(self, fname):  # type: (str) -> None
        self.con = sqlite3.connect(fname)
        self.cur = self.con.cursor()
        self.create()

    def save(self):  # type: () -> None
        self.con.commit()

    def create(self):  # type: () -> None
        self.cur.executescript('''
            CREATE TABLE IF NOT EXISTS os (
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS files (
                os INT NOT NULL,
                name TEXT NOT NULL,
                fake BOOL NOT NULL,
                FOREIGN KEY (os) REFERENCES os(id)
            );
            CREATE TABLE IF NOT EXISTS entries (
                file INT NOT NULL,
                key TEXT(4) NOT NULL,
                data TEXT(5) NOT NULL,
                FOREIGN KEY (file) REFERENCES files(id)
            );
        ''')

    def exists(self, os_name):  # type: (str) -> bool
        self.cur.execute('SELECT 1 FROM os WHERE name=?', [os_name])
        return self.cur.fetchone() is not None

    def os(self, name):  # type: (str) -> int
        return self.cur.execute(
            'INSERT INTO os(name) VALUES (?)',
            [name]).lastrowid or -1

    def file(self, os_id, name, fake):  # type: (int, str, bool) -> int
        return self.cur.execute(
            'INSERT INTO files(os,name,fake) VALUES (?,?,?)',
            [os_id, name, fake]).lastrowid or -1

    def entry(self, file_id, key, data):  # type: (int, bytes, str) -> int
        return self.cur.execute(
            'INSERT INTO entries(file,key,data) VALUES (?,?,?)',
            [file_id, key, data]).lastrowid or -1


#######################################
#
# Generate analysis database
#
#######################################

def determine_data(key, data):  # type: (bytes, bytes) -> str
    if data[:8] == b'\x89PNG\x0d\x0a\x1a\x0a':
        return 'png'
    if data[:8] == b'\xFF\x4F\xFF\x51\x00\x2F\x00\x00':
        return 'jp2'
    if data[:8] == b'\x00\x00\x00\x0CjP  ':
        return 'jpf'
    if data[:6] == b'bplist':
        return 'plist'
    if data[:4] == b'ARGB':
        return 'argb'

    if key == b'!':  # not part of icns file but the whole file could be wrong
        if data[:4] == b'icns':
            return 'icns'
        if data[:4] == b'MM\x00*' or data[:4] == b'II*\x00':
            return 'tiff'
        if data[:3] == b'\xFF\xD8\xFF':  # JPEG (not supported in icns files)
            return 'jpg'
    if key in KNOWN_BBINARY or key in KNOWN_INFO:
        return 'bin'
    if key in KNOWN_ICNS:
        return 'icns'
    return ''


def mini_parser(data):  # type: (bytes) -> Iterator[tuple[bytes, str]]
    ''' Iterate over icns header fields '''
    off = 0
    while off < len(data):
        key, size = struct.unpack('>4sI', data[off:off + 8])
        sample = data[off + 8:off + 16]
        typ = determine_data(key, sample)
        yield key, typ
        if typ == 'icns':
            for sub in mini_parser(data[off + 8:off + size]):
                yield sub
        off += size


def parse_src_txt(zipfile):  # type: (ZipFile) -> dict[int, str]
    ''' Load `_src.txt` file into memory. Returns `{file-num: src-path}` '''
    rv = {}  # type: dict[int, str]
    with zipfile.open('_src.txt') as fp:
        for line in fp.readlines():
            num, ref = line.decode().split(',', 1)
            rv[int(num)] = ref.strip()
    return rv


def parse_file(data, fname):  # type: (bytes, str) -> dict[bytes, set[str]]
    ''' Parse raw data and extract ICNS keys. Returns `{key: {data-types}}` '''
    rv = {}  # type: dict[bytes, set[str]]
    # ICNS header
    key, size = struct.unpack('>4sI', data[:8])
    if key != b'icns':
        print('ERROR: not an icns file (detected: %s) in %s'
              % (determine_data(b'!', data[:8]), fname), file=sys.stderr)
        return {}
    if size != len(data):
        print('WARN: length mismatch %d != %d in %s'
              % (size, len(data), fname), file=sys.stderr)
    # iter fields
    for key, kind in mini_parser(data[8:size]):
        if key not in KNOWN:
            print('!!!: unexpected key %r in %s' % (key, fname),
                  file=sys.stderr)
        elif not kind:
            print('!!!: unexpected data in key %r in %s' % (key, fname),
                  file=sys.stderr)
        else:
            rv.setdefault(key, set()).add(kind)
    return rv


def parse_zip(db, os_id, zipfile, pth_prefix):
    # type: (DB, int, ZipFile, str) -> None
    ''' Iter over all `.icns` files inside of zip file. '''
    refs = parse_src_txt(zipfile)
    for file in zipfile.filelist:  # already sorted by Makefile `make zip`
        fn = file.filename
        if not fn.endswith('.icns'):
            continue
        fullpath = os.path.join(pth_prefix, fn)
        ref = refs[int(fn.split('.', 1)[0])]  # number of e.g., `42.icns`
        is_fake = '.rsrc/' in ref and '.rsrc/icns/' not in ref
        # create new db entry for a file refernce
        f_id = db.file(os_id, fullpath, is_fake)
        with zipfile.open(fn) as fp:
            data = fp.read()
        for k, fields in parse_file(data, fullpath).items():
            for field in fields:
                # create new db entry per ICNS key
                db.entry(f_id, k, field)


def iter_os_zips(root):  # type: (str) -> Iterator[tuple[str, list[str]]]
    ''' Sorted list of `(os-name, [zip-files])` '''
    # split OS-version by '.' and sort parts by int
    for _, item in sorted(([int(n) for n in x.split()[0].split('.')], x)
                          for x in os.listdir(root) if x[0].isdigit()):
        pth = os.path.join(root, item)
        if os.path.isdir(pth):
            yield item, sorted(os.path.join(pth, x) for x in os.listdir(pth)
                               if x.endswith('.zip'))
        elif pth.endswith('.zip'):
            yield item.removesuffix('.zip'), [pth]


def parse_archive(db, root):  # type: (DB, str) -> None
    for os_name, zip_files in iter_os_zips(root):
        if db.exists(os_name):
            continue
        print('process: ' + os_name)
        # create new db entry for OS grouping
        os_id = db.os(os_name)
        for zipfile in zip_files:
            with ZipFile(zipfile) as zf:
                parse_zip(db, os_id, zf, os.path.relpath(zipfile, root))


#######################################
#
# Evaluate analysis results
#
#######################################

def pretty_key(key):  # type: (bytes) -> str
    try:
        return key.decode()
    except UnicodeDecodeError:
        return key.hex().upper()


def ostype_by_os(db, key):  # type: (DB, bytes) -> dict[int, int]
    return dict((oid, count) for oid, count in db.cur.execute('''
        SELECT os, count(*)
        FROM entries INNER JOIN files on file=files.ROWID
        WHERE key=? -- AND not fake
        GROUP BY os''', [key]))


def distinct_types(db):  # type: (DB) -> dict[bytes, tuple[str, int, int]]
    return dict((k, (d, mn, mx)) for k, d, mn, mx in db.cur.execute('''
        SELECT key, group_concat(DISTINCT data), min(os), max(os)
        FROM entries INNER JOIN files on file = files.ROWID
        GROUP BY key'''))


def evaluate(db, outfile):  # type: (DB, str) -> None
    os_list = [(k, v.split()[0]) for k, v in
               db.cur.execute('SELECT ROWID, name FROM os').fetchall()]

    with open(outfile, 'w') as fp:
        fp.write('''# Icons extracted from macOS disk image – Analysis

## Data format usage

earliest version tested: OS %s
latest version tested: macOS %s

 key   | data     | first OS | last OS
-------|:--------:|:--------:|:-------:
''' % (os_list[0][1] + '  ', os_list[-1][1]))  # 2x space for markdown newline

        types = distinct_types(db)
        for key in KNOWN:
            d, mn, mx = types.get(key, ('', 0, 0))
            fp.write('`%s` | %s | %s | %s\n' % (
                pretty_key(key),
                ', '.join(d.split(',')).ljust(8),
                (os_list[mn-1][1] if mn else '').ljust(8),
                (os_list[mx-1][1] if mx else '').ljust(7),
            ))

        fp.write('''

## OSType usage by OS

How often a key was used across all system icns files.

key   |%s
------%s
''' % ('|'.join(x.ljust(5) for _, x in os_list), '|:---:' * len(os_list)))

        for key in KNOWN:
            fp.write('`%s`' % pretty_key(key))
            counter = ostype_by_os(db, key)
            for os_id, _ in os_list:
                fp.write('|' + str(counter.get(os_id, '')).ljust(5))
            fp.write('\n')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('usage: %s <src-dir> <db-path>' % os.path.basename(sys.argv[0]))
        exit(0)

    _, root, db_path = sys.argv
    testFile = os.path.join(root, '14 Sonoma.zip')
    if not os.path.isfile(testFile):
        print('ERROR: "%s" does not exist' % testFile)
        exit(1)

    db = DB(db_path)
    parse_archive(db, root)
    evaluate(db, os.path.splitext(db_path)[0] + '-report.md')
    db.save()
