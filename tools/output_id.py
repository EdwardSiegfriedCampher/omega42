#!/usr/bin/env python3
"""output_id.py -- the NAVIGATION OUTPUT ID (Core Part 8.1): the SHA-256 of a finished output, computed over
every line above the OUTPUT ID line and the Navigator Signature, with line endings normalized to LF and trailing
whitespace removed. A Striker or peer re-computes it to confirm that the output they hold is the one the Navigator
issued. The arithmetic of navigation is untouched (canonical_reference.py is frozen).

Usage:
    python3 tools/output_id.py OUTPUT.txt            # prints the OUTPUT ID of the text above the signature
    python3 tools/output_id.py --verify OUTPUT.txt   # checks an OUTPUT ID line already present
    python3 tools/output_id.py --selftest
"""
import hashlib, re, sys
SIG = re.compile(r'^\s*(OUTPUT ID:|CAS-YY = -1/2)')

def body(text):
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    out = []
    for l in lines:
        if SIG.match(l): break
        out.append(l.rstrip())
    while out and not out[-1]: out.pop()
    return '\n'.join(out) + '\n'

def output_id(text):
    return hashlib.sha256(body(text).encode('utf-8')).hexdigest()

def verify(text):
    m = re.search(r'^\s*OUTPUT ID:\s*([0-9a-f]{64})', text, re.M)
    return bool(m) and m.group(1) == output_id(text)

def selftest():
    t = 'Navigation text\nline two  \n\nCAS-YY = -1/2 | Omega = 1/7\n'
    i = output_id(t)
    ok = [i == output_id('Navigation text\r\nline two\r\n'),
          verify('Navigation text\nline two\nOUTPUT ID: %s\nCAS-YY = -1/2\n' % i),
          not verify('Navigation text altered\nOUTPUT ID: %s\n' % i)]
    print('OUTPUT ID SELFTEST: %s (%d/3)' % ('PASS' if all(ok) else 'FAIL', sum(ok))); return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--verify':
        ok = verify(open(a[1], encoding='utf-8').read()); print('OUTPUT ID: %s' % ('VERIFIED' if ok else 'MISMATCH OR ABSENT')); sys.exit(0 if ok else 1)
    print('OUTPUT ID: %s' % output_id(open(a[0], encoding='utf-8').read()))
