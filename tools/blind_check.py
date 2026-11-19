#!/usr/bin/env python3
"""blind_check.py -- independent checker for blind test 02 (records/blind_test_02/scoring_rule.txt, level L3).
Given a 2x2 matrix over Z/9 (a b c d), it recomputes: invertibility, whether it preserves or reverses every spin
h(x) = 4(a^2 + b^2)/9 mod 1, its order, its cycle census on the 81 labels, trace, determinant and the quadratic
identity A^2 = sA + tI. Written separately from the pilot code. Standard library only.
Usage: python3 tools/blind_check.py a b c d    |    --selftest"""
import sys
from collections import Counter
def act(M, x): a, b, c, d = M; return ((a * x[0] + b * x[1]) % 9, (c * x[0] + d * x[1]) % 9)
def mul(M, N):
    a, b, c, d = M; e, f, g, h = N
    return ((a * e + b * g) % 9, (a * f + b * h) % 9, (c * e + d * g) % 9, (c * f + d * h) % 9)
def spin(x): return (4 * (x[0] ** 2 + x[1] ** 2)) % 9
def check(M):
    a, b, c, d = M; det = (a * d - b * c) % 9
    if det % 3 == 0: return {'invertible': False}
    labels = [(u, v) for u in range(9) for v in range(9)]
    pres = all(spin(act(M, x)) == spin(x) for x in labels)
    rev = all(spin(act(M, x)) == (-spin(x)) % 9 for x in labels)
    P, n = M, 1
    while P != (1, 0, 0, 1): P = mul(P, M); n += 1
    seen, cen = set(), Counter()
    for x in labels:
        if x in seen: continue
        L, y = 0, x
        while y not in seen: seen.add(y); y = act(M, y); L += 1
        cen[L] += 1
    tr = (a + d) % 9; t = (-det) % 9
    A2 = mul(M, M); ident = A2 == ((tr * a + t) % 9, tr * b % 9, tr * c % 9, (tr * d + t) % 9)
    return {'invertible': True, 'preserves': pres, 'reverses': rev, 'order': n, 'census': dict(sorted(cen.items())),
            'trace': tr, 'det': det, 'identity': 'A^2 = %dA + %dI' % (tr, t), 'identity_holds': ident}
if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest':
        r = check((1, 4, 5, 1))
        ok = r['reverses'] and r['order'] == 24 and r['census'] == {1: 1, 8: 1, 24: 3} and r['trace'] == 2 and r['identity_holds']
        print('BLIND CHECK SELFTEST: %s %s' % ('PASS' if ok else 'FAIL', r)); sys.exit(0 if ok else 1)
    print(check(tuple(int(x) % 9 for x in a)))
