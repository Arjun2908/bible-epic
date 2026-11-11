#!/usr/bin/env python3
"""Berean Standard Bible lookup built from the public-domain USFM files (usfm-bible/examples.bsb).
  bsb.py build                 -> writes bsb/bsb.json
  bsb.py show 1SA 17 4-11      -> prints verses
  import: from bsb import verse, verses, check(text, 'BOOK', ch, v) """
import sys, os, re, json, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bsb')
SRC_REPO = 'https://github.com/usfm-bible/examples.bsb'
JS = os.path.join(ROOT, 'bsb.json')

def clean(t):
    t = re.sub(r'\\f .*?\\f\*', '', t)            # footnotes
    t = re.sub(r'\\x .*?\\x\*', '', t)            # cross references
    t = re.sub(r'\\w ([^|\\]*)\|[^\\]*\\w\*', r'\1', t)
    t = re.sub(r'\\\+?nd ([^\\]*)\\\+?nd\*', lambda m: m.group(1).upper(), t)   # divine name: the source marks it as small caps (\nd Lord\nd*); the BSB prints LORD / GOD
    t = re.sub(r'\\[a-z0-9]+\*', '', t)           # closing char markers
    t = re.sub(r'\\[a-z0-9]+ ?', '', t)           # remaining markers
    t = t.replace('\u02bc', '\u2019')             # modifier apostrophe -> typographic apostrophe
    return re.sub(r'\s+', ' ', t).strip()

def build():
    import subprocess
    os.makedirs(ROOT, exist_ok=True)
    if not os.path.isdir(os.path.join(ROOT, 'src1')):
        subprocess.run(['git', 'clone', '-q', '--depth', '1', SRC_REPO, os.path.join(ROOT, 'src1')], check=True)
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'src1', '*.usfm'))):
        book = os.path.basename(f)[2:5]; out[book] = {}
        ch, v = None, None
        for line in open(f, encoding='utf-8-sig'):
            line = line.rstrip('\n')
            if line.startswith('\\id'): continue
            m = re.match(r'\\c (\d+)', line)
            if m: ch = m.group(1); out[book][ch] = {}; v = None; continue
            if re.match(r'\\(s\d?|ms\d?|mr|r|d|sp|qa|cl|cd|h|toc\d|mt\d?|rem|ide|usfm|b)\b', line) and not line.startswith('\\v'):
                if line.startswith('\\d ') and ch: out[book][ch].setdefault('title', clean(line[3:]))
                continue
            m = re.match(r'\\v (\d+)(?:-\d+)? (.*)', line)
            if m:
                v = m.group(1); out[book][ch][v] = m.group(2); continue
            # continuation: poetry / paragraph lines that carry verse text
            m2 = re.match(r'\\(?:p|m|q\d?|pi\d?|li\d?|pc|qr|qc|mi|nb|pmo|pm|pmc|pmr)\b ?(.*)', line)
            if m2 and ch:
                rest = m2.group(1)
                mv = re.match(r'\\v (\d+)(?:-\d+)? (.*)', rest)
                if mv: v = mv.group(1); out[book][ch][v] = mv.group(2)
                elif rest and v: out[book][ch][v] += ' ' + rest
        for c in out[book]:
            for k in out[book][c]: out[book][c][k] = clean(out[book][c][k])
    json.dump(out, open(JS, 'w', encoding='utf-8'), ensure_ascii=False)
    n = sum(len([k for k in c if k != 'title']) for b in out.values() for c in b.values())
    print('books', len(out), 'verses', n)

_DB = None
def db():
    global _DB
    if _DB is None: _DB = json.load(open(JS, encoding='utf-8'))
    return _DB
def verse(book, ch, v): return db()[book][str(ch)][str(v)]
def verses(book, ch, a, b): return ' '.join(verse(book, ch, i) for i in range(a, b + 1))
def norm(s): return re.sub(r'\s+', ' ', s.replace('\u201c', '"').replace('\u201d', '"').replace('\u2018', "'").replace('\u2019', "'")).strip()
def check(text, book, ch, a, b=None):
    """True if `text` appears verbatim (quotes normalised) inside the given verse range."""
    return norm(text) in norm(verses(book, ch, a, b or a))

if __name__ == '__main__':
    if sys.argv[1] == 'build': build()
    elif sys.argv[1] == 'show':
        book, ch, rng = sys.argv[2], sys.argv[3], sys.argv[4]
        a, b = (rng.split('-') + [rng])[:2] if '-' in rng else (rng, rng)
        for i in range(int(a), int(b) + 1): print(i, verse(book, ch, i))
