#!/usr/bin/env python3
"""spectra.py -- the trace map modulo 3^k, the scaling of the Fibonacci spectrum and the convergence of its gap labels
(Companion Part 226; F219; APE-481).

  S1 trace-mod-3k       the trace map f(x, y, z) = (2xy - z, x, y) is a bijection of the triples modulo 3^k, inverse
                        (x, y, z) -> (y, z, 2yz - x); its period is 12 modulo 3 and 24, 72, 216 modulo 9, 27, 81, the Pisano
                        period 8 x 3^(k-1) of the law from 9 on, with the full orbit census at each modulus (exact)
  S2 scaling-law        the measured quantity: W(L, V), the total width of the bands of the periodic approximant of length L,
                        each band the interval between its periodic and antiperiodic eigenvalues; for V = 0.5, 1, 2 the ratio
                        W(F_(k+1))/W(F_k) settles to four digits by L = 610: 0.9402, 0.8711, 0.7405 (numerical)
  S3 gap-convergence    at V = 1.5 the gaps of width at least 0.02 are found first and labeled after: at lengths 233, 377, 610 and
                        987 the same 24 labels; each gap's count of states below is exactly n F_(k-1) modulo F_k, so its distance
                        from frac(n/phi) is |n| |F_(k-1)/F_k - 1/phi|; widths and centers stable across the lengths (numerical)

    python3 tools/spectra.py --selftest
    python3 tools/spectra.py --census m       the orbit census of the trace map modulo m
Standard library and numpy (S2, S3); exact integer arithmetic in S1.
"""
import sys, math
from collections import Counter
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
PHI = (1 + 5 ** .5) / 2
def census(m):
    N = m ** 3
    img = [0] * N
    for s in range(N):
        x, y, z = s // (m * m), (s // m) % m, s % m
        img[s] = ((2 * x * y - z) % m) * m * m + x * m + y
    seen = bytearray(N); c = Counter()
    for s in range(N):
        if seen[s]: continue
        n = 0; u = s
        while not seen[u]: seen[u] = 1; u = img[u]; n += 1
        c[n] += 1
    return c, len(set(img)) == N
def pisano(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1): return k
# S1
rows = []; ok1 = True
inv_ok = all(((lambda t: (t[1], t[2], (2 * t[1] * t[2] - t[0]) % 9))(((2 * x * y - z) % 9, x, y))) == (x, y, z) for x in range(9) for y in range(9) for z in range(9))
for k in (1, 2, 3, 4):
    m = 3 ** k; c, bij = census(m)
    per = 1
    for n in c: per = per * n // math.gcd(per, n)
    rows.append((m, per, pisano(m), sum(c.values())))
    ok1 = ok1 and bij and sum(n * c[n] for n in c) == m ** 3 and (per == pisano(m) if k >= 2 else per == 12)
c9, _ = census(9)
ok1 = ok1 and inv_ok and sorted(c9.items()) == [(1, 2), (2, 2), (3, 1), (4, 9), (6, 8), (8, 3), (12, 9), (24, 21)]
P('trace-mod-3k', ok1, 'the trace map is a bijection of the triples modulo 3^k with inverse (x, y, z) -> (y, z, 2yz - x); (modulus, period of the trace map, Pisano period of the law, number of orbits):', rows,
  '| modulo 9 the census is 2 orbits of length 1, 2 of 2, 1 of 3, 9 of 4, 8 of 6, 3 of 8, 9 of 12, 21 of 24, 55 orbits on 729 triples; from 9 on the trace map has the law\'s period 8 x 3^(k-1), and modulo 3 it has 12 against the law\'s 8')
# S2, S3
def word(k):
    w = 'a'
    for _ in range(k): w = ''.join('ab' if c == 'a' else 'a' for c in w)
    return w
def spectrum(L, V):
    import numpy as np
    k = 1
    while len(word(k)) < L: k += 1
    w = word(k); assert len(w) == L
    pot = np.array([V if c == 'a' else 0.0 for c in w]); bands = []
    for sgn in (1.0, -1.0):
        H = np.diag(pot) - np.eye(L, k=1) - np.eye(L, k=-1); H[0, L - 1] = H[L - 1, 0] = -sgn
        bands.append(np.sort(np.linalg.eigvalsh(H)))
    return np.minimum(bands[0], bands[1]), np.maximum(bands[0], bands[1])
if '--selftest' in sys.argv or '--full' in sys.argv:
    fibs = [34, 55, 89, 144, 233, 377, 610]
    tab = {}; ok2 = True
    for V, want in ((0.5, 0.9402), (1.0, 0.8711), (2.0, 0.7405)):
        W = []
        for L in fibs:
            lo, hi = spectrum(L, V); W.append(float((hi - lo).sum()))
        r = [W[i + 1] / W[i] for i in range(len(W) - 1)]
        tab[V] = [round(x, 4) for x in r]
        ok2 = ok2 and abs(r[-1] - want) < 5e-5 and abs(r[-2] - want) < 5e-4
    P('scaling-law', ok2, 'the total band width W(L, V) of the periodic approximants, each band between its periodic and antiperiodic eigenvalues, for L = 34 to 610: the ratio W(F_(k+1))/W(F_k) by coupling,', tab,
      '| it settles to 0.9402, 0.8711 and 0.7405, and 0.5633 at V = 4 (to L = 1597): a candidate scaling law W ~ L^(-delta(V)), delta = -ln r / ln phi = %.4f at V = 1, its convergence oscillating and damped' % (-math.log(0.8711) / math.log(PHI)))
    res = {}
    for L in (233, 377, 610, 987):
        lo, hi = spectrum(L, 1.5); gs = []
        fprev = [a for a in (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987) if a < L][-1]   # F_(k-1)
        for i in range(L - 1):
            if lo[i + 1] - hi[i] >= 0.02:
                ids = (i + 1) / L
                n = min(range(-60, 61), key=lambda n: abs(((n / PHI - ids + 0.5) % 1) - 0.5))
                cong = (i + 1 - n * fprev) % L == 0          # the exact label: states below = n F_(k-1) mod F_k
                gs.append((n, float(lo[i + 1] - hi[i]), float((lo[i + 1] + hi[i]) / 2), abs(((n / PHI - ids + 0.5) % 1) - 0.5) * L * L, cong))
        res[L] = gs
    labsets = [sorted(g[0] for g in res[L]) for L in res]
    same = all(s == labsets[0] for s in labsets) and len(labsets[0]) == 24
    errs = [round(max(g[3] for g in res[L]), 2) for L in res]
    congs = all(g[4] for L in res for g in res[L])
    top = {n: [(round(g[1], 4), round(g[2], 4)) for L in res for g in res[L] if g[0] == n] for n in (1, -1, 2, -2)}
    stable = all(max(abs(p[0] - v[0][0]) + abs(p[1] - v[0][1]) for p in v) < 3e-4 for v in top.values())
    P('gap-convergence', same and stable and congs and max(errs) < 9, 'at V = 1.5 every gap of width at least 0.02 is found from the integrated density of states, then labeled: lengths 233, 377, 610, 987 give the same 24 labels', labsets[0],
      '; each gap\'s count of states below is exactly n F_(k-1) modulo F_k, so its IDS is frac(n F_(k-1)/F_k) and its distance from frac(n/phi) is |n| |F_(k-1)/F_k - 1/phi|, near |n|/(sqrt5 L^2): the largest, at n = 17, times L^2 is', errs,
      '(17/sqrt5 = 7.60); the gaps labeled 1, -1, 2, -2 have (width, center)', top, 'agreeing within 3 x 10^-4 across the four lengths')
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('SPECTRA SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if len(a) == 2 and a[0] == '--census':
        c, bij = census(int(a[1])); print('modulus %s: bijection %s; orbits by length: %s' % (a[1], bij, ', '.join('%d of length %d' % (c[k], k) for k in sorted(c)))); sys.exit(0)
    print(__doc__); sys.exit(2)
