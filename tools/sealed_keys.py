#!/usr/bin/env python3
"""sealed_keys.py -- the state of every sealed key (Core Appendix R.4; Companion Part 183).
A key sealed by its hash is in one of four states. SEALED: the key is present and matches its hash (the test is open or
closed, and its key can be checked). KEY LOST: the key is absent and records/<test>/KEY_LOST.txt records how, where it was
searched for and what the test's status is. HELD: the key is absent from this build and records/<test>/KEY_HELD.txt names who holds it. FAIL: the key is absent with no such record, or present and not matching.
    python3 tools/sealed_keys.py --check TEST    # one test, e.g. blind_test_02
    python3 tools/sealed_keys.py --all
    python3 tools/sealed_keys.py --selftest
Standard library only."""
import hashlib, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS = ['blind_test_01', 'blind_test_02', 'blind_test_03', 'm267_pilot_01']
def state(t):
    d = os.path.join(REPO, 'records', t); s = os.path.join(d, 'SEALED_SHA256.txt')
    if not os.path.exists(s): return 'FAIL', 'no SEALED_SHA256.txt'
    h, name = open(s).read().split()[:2]; k = os.path.join(d, name.lstrip('*'))
    if os.path.exists(k):
        ok = hashlib.sha256(open(k, 'rb').read()).hexdigest() == h
        return ('SEALED', 'the key matches its sealed hash') if ok else ('FAIL', 'the key does not match its sealed hash')
    if os.path.exists(os.path.join(d, 'KEY_LOST.txt')): return 'KEY LOST', 'absent, recorded in KEY_LOST.txt; the sealed hash stands'
    if os.path.exists(os.path.join(d, 'KEY_HELD.txt')): return 'HELD', 'absent from this build, held as KEY_HELD.txt names; the sealed hash stands'
    return 'FAIL', 'the key is absent and no KEY_LOST.txt records why'
if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--check']:
        st, why = state(a[1]); print('SEALED KEY %s: %s (%s)' % (a[1], st, why)); sys.exit(0 if st != 'FAIL' else 1)
    if a == ['--all'] or a == ['--selftest']:
        R = [(t,) + state(t) for t in TESTS]
        for t, st, why in R: print('%-15s %-9s %s' % (t, st, why))
        ok = all(st != 'FAIL' for _, st, _ in R)
        if a == ['--selftest']: print('SEALED KEYS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
        sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
