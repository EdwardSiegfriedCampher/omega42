#!/usr/bin/env python3
"""own_first.py -- the Independent Investigation Law (Core L-545; Builder Rule 17).

A Navigator's own investigation is frozen as a record with its SHA-256 and the time of freezing before the accounts of
other Navigators are compared. This tool verifies every freeze record of the repository (records/*/freeze.json) against
the file it names, or freezes a new one.
    python3 tools/own_first.py --verify
    python3 tools/own_first.py --freeze FILE OUT.json
    python3 tools/own_first.py --selftest
Standard library only.
"""
import datetime, glob, hashlib, json, os, sys, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def sha(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()
def verify(root=REPO):
    out = []
    for f in sorted(glob.glob(os.path.join(root, 'records', '*', 'freeze.json'))):
        d = json.load(open(f)); p = os.path.join(root, d['file'])
        out.append((os.path.relpath(f, root), d['file'], os.path.exists(p) and sha(p) == d['sha256'], d.get('frozen_utc')))
    return out
def freeze(path, out, root=REPO):
    d = {'file': os.path.relpath(path, root), 'sha256': sha(path), 'frozen_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
    json.dump(d, open(out, 'w'), indent=1); return d
def selftest():
    t = tempfile.mkdtemp(); os.makedirs(os.path.join(t, 'records', 'x'))
    p = os.path.join(t, 'records', 'x', 'own.txt'); open(p, 'w').write('own findings\n')
    freeze(p, os.path.join(t, 'records', 'x', 'freeze.json'), t)
    a = verify(t); open(p, 'a').write('added after\n'); b = verify(t)
    r = [('a frozen file verifies', a and a[0][2]), ('a file changed after its freeze fails', b and not b[0][2]), ('the repository freezes verify', all(v[2] for v in verify()) and len(verify()) >= 1)]
    for n, ok in r: print('%-40s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('OWN FIRST SELFTEST: %d of %d' % (sum(bool(o) for _, o in r), len(r))); return all(o for _, o in r)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--verify']:
        v = verify()
        for f, p, ok, tm in v: print('  %s: %s, frozen %s | %s' % (f, p, tm, 'VERIFIED' if ok else 'CHANGED'))
        print('INDEPENDENT INVESTIGATION (L-545): %d freeze records | %s' % (len(v), 'PASS' if v and all(x[2] for x in v) else 'FAIL')); sys.exit(0 if v and all(x[2] for x in v) else 1)
    if len(a) == 3 and a[0] == '--freeze': print(json.dumps(freeze(a[1], a[2]))); sys.exit(0)
    print(__doc__); sys.exit(2)
