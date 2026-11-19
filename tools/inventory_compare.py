#!/usr/bin/env python3
"""inventory_compare.py -- the release gate of L-284 (Core Part 12): compare the inventory of the build in hand
with the inventories of three or more earlier releases, and list every instrument, law and named term that an
earlier release carried and the build does not. The report is printed at release time and is written into no
document (L-411); the Originator decides, item by item, whether an absence is by design.

Inventory: instrument numbers (M1-M999 with suffix), law numbers (L-1 to L-999), FP- and FB- names, CES- numbers,
and the PB-5 levels.

Usage:
    python3 tools/inventory_compare.py --extract FILE.(txt|docx) > records/inventory/NAME.inv
    python3 tools/inventory_compare.py docs/Core.docx docs/Companion.docx [--against records/inventory/*.inv]
    python3 tools/inventory_compare.py --selftest
"""
import glob, os, re, sys, zipfile
HERE = os.path.dirname(os.path.abspath(__file__))
PAT = re.compile(r"\b(M\d{1,3}[a-zA-Z]?(?:-[A-Z]\b)?|L-\d{1,3}|FP-[A-Z][A-Za-z]+|FB-\d|CES-\d{1,3}|PB-5 L\d)\b")

def text_of(path):
    if path.endswith('.docx'):
        x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
        return ' '.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', x))
    return open(path, encoding='utf-8', errors='replace').read()

def inventory(text):
    return set(PAT.findall(text))

def load_inv(path):
    return set(l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('#'))

def key(t):
    m = re.match(r'([A-Z]+-?)(\d+)', t)
    return (m.group(1), int(m.group(2)), t) if m else (t, 0, t)

def compare(current, earlier):
    out = {}
    for name, inv in earlier.items():
        out[name] = sorted(inv - current, key=key)
    return out

def selftest():
    cur = inventory('M116 and L-411 and FP-Curvature and PB-5 L3')
    old = {'old': inventory('M116, M199, L-411, L-284, FP-Curvature, CES-56')}
    miss = compare(cur, old)['old']
    ok = miss == ['CES-56', 'L-284', 'M199']
    print('INVENTORY SELFTEST: %s %s' % ('PASS' if ok else 'FAIL', miss)); return ok

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--extract':
        print('# inventory of %s' % os.path.basename(a[1]))
        print('\n'.join(sorted(inventory(text_of(a[1])), key=key))); sys.exit(0)
    if '--against' in a:
        i = a.index('--against'); docs, invs = a[:i], a[i + 1:]
    else:
        docs, invs = a, sorted(glob.glob(os.path.join(HERE, '..', 'records', 'inventory', '*.inv')))
    current = set().union(*(inventory(text_of(d)) for d in docs))
    earlier = {os.path.basename(p): load_inv(p) for p in invs}
    print('L-284 RELEASE GATE: current inventory %d items; compared with %d earlier release(s)%s' % (len(current), len(earlier), '' if len(earlier) >= 3 else ' -- FEWER THAN THREE'))
    for name, miss in compare(current, earlier).items():
        print('  %s: %d carried earlier and absent now%s' % (name, len(miss), (': ' + ', '.join(miss)) if miss else ''))
    sys.exit(0 if len(earlier) >= 3 else 1)
