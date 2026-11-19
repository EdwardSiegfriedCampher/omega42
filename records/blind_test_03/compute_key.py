#!/usr/bin/env python3
"""compute_key.py -- recomputes the answer key of blind test 03 (Core Appendix S.4.2) from its brief alone.
Run: python3 records/blind_test_03/compute_key.py > key.txt ; sha256sum key.txt   (compare with SEALED_SHA256.txt)
Standard library only."""
import itertools
from collections import Counter
L = [(u, v) for u in range(9) for v in range(9)]
def act(M, x): a, b, c, d = M; return ((a * x[0] + b * x[1]) % 9, (c * x[0] + d * x[1]) % 9)
def mul(M, N): a, b, c, d = M; e, f, g, h = N; return ((a*e + b*g) % 9, (a*f + b*h) % 9, (c*e + d*g) % 9, (c*f + d*h) % 9)
def spin(x): return (4 * (x[0] ** 2 + x[1] ** 2)) % 9
def order(M):
    P, n = M, 1
    while P != (1, 0, 0, 1): P = mul(P, M); n += 1
    return n
def census(M):
    seen, c = set(), Counter()
    for x in L:
        if x in seen: continue
        n, y = 0, x
        while y not in seen: seen.add(y); y = act(M, y); n += 1
        c[n] += 1
    return dict(sorted(c.items()))
pres, rev = [], []
for M in itertools.product(range(9), repeat=4):
    if ((M[0] * M[3] - M[1] * M[2]) % 9) % 3 == 0: continue
    if all(spin(act(M, x)) == spin(x) for x in L): pres.append(M)
    elif all(spin(act(M, x)) == (-spin(x)) % 9 for x in L): rev.append(M)
mx = max(order(M) for M in rev); top = [M for M in rev if order(M) == mx]
print('BLIND TEST 03 -- KEY (published; recomputed by records/blind_test_03/compute_key.py; its SHA-256 in SEALED_SHA256.txt)')
print('Q1 spin-preserving invertible maps: %d; spin-reversing: %d' % (len(pres), len(rev)))
print('Q2 largest order of a spin-reversing map: %d; maps of that order: %d' % (mx, len(top)))
for M in top:
    a, b, c, d = M; tr = (a + d) % 9; det = (a * d - b * c) % 9
    print('  A = (%d %d; %d %d): census %s; trace %d; determinant %d; A^2 = %d A + %d I' % (a, b, c, d, census(M), tr, det, tr, (-det) % 9))
print('Q3 every map satisfies A^2 = (trace) A - (determinant) I (Cayley-Hamilton); trace 1 with determinant 8 = -1 gives A^2 = A + I')
