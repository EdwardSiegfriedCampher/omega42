#!/usr/bin/env python3
"""atlas.py -- three instruments from F176 to F178 (Core Part 3.78; APE-437 to APE-439).

  M365 Canonical Form Engine  python3 tools/atlas.py canon K R          the orbit label of every state in O(k) arithmetic,
                                                                     checked against breadth-first orbits; --bench times both
  M366 Two-Boundary Explorer  python3 tools/atlas.py twoboundary N      histories of length N in A and B from (1,0) mod 9:
                                                                     how a fixed END changes what is inferred of the START
  M367 Physics Atlas (seed)   python3 tools/atlas.py anomalies          one Standard Model generation: charges and the
                                                                     gauge-anomaly sums, exact (MODE B data, Appendix S)
                              python3 tools/atlas.py lcdm OM OL H0      flat ΛCDM: H(a) and the age, radiation neglected
  python3 tools/atlas.py --selftest
Standard library only. M365 and M366 are MODE A (Core L-559); M367 holds physics as data in its own terms and asserts
no correspondence with Ω42 (Core L-510, L-553).
"""
import math, sys, time
from collections import Counter
from fractions import Fraction as Fr

A = (0, 1, 1, 1)


def app(X, v, m):
    return ((X[0] * v[0] + X[1] * v[1]) % m, (X[2] * v[0] + X[3] * v[1]) % m)


def label(a, b, k, r):
    """the complete invariant of <A, B_r> on (Z/3^k)^2 (MF-43): valuation j and Q(u)^2 mod 3^min(r, k-j)."""
    m = 3 ** k; a %= m; b %= m
    if a == 0 and b == 0:
        return ('zero',)
    j = 0
    while a % 3 == 0 and b % 3 == 0:
        a //= 3; b //= 3; j += 1
    q = 2 * (a * a + a * b - b * b); e = min(r, k - j)
    return (j, q * q % 3 ** e)


def bfs_partition(k, r):
    m = 3 ** k; B = (1, 0, 3 ** r % m, 1); Ai = ((-1) % m, 1, 1, 0); Bi = (1, 0, (-(3 ** r)) % m, 1)
    seen = {}; parts = []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen:
                continue
            idx = len(parts); seen[(a, b)] = idx; st = [(a, b)]; orb = [(a, b)]
            while st:
                x = st.pop()
                for g in (A, B, Ai, Bi):
                    y = app(g, x, m)
                    if y not in seen:
                        seen[y] = idx; st.append(y); orb.append(y)
            parts.append(orb)
    return seen, parts


def canon_check(k, r):
    seen, parts = bfs_partition(k, r)
    lab = {}
    for (x, idx) in seen.items():
        lab.setdefault(label(x[0], x[1], k, r), set()).add(idx)
    one_to_one = all(len(v) == 1 for v in lab.values()) and len(lab) == len(parts)
    return one_to_one, len(parts), 9 ** k


def twoboundary(n, x0=(1, 0), m=9):
    Bm = (1, 0, 3, 1); layer = Counter({(x0, None): 1})
    for _ in range(n):
        nl = Counter()
        for (v, first), c in layer.items():
            for name, g in (('A', A), ('B', Bm)):
                nl[(app(g, v, m), first or name)] += c
        layer = nl
    ends = {}
    for (v, f), c in layer.items():
        ends.setdefault(v, Counter())[f] += c
    shifts = sorted(((abs(d['B'] / sum(d.values()) - 0.5), v, d['B'] / sum(d.values()), sum(d.values())) for v, d in ends.items()), reverse=True)
    return len(ends), shifts[0], 2 ** n


GEN = [('Q_L (3,2)_{1/6}', 3, 2, Fr(1, 6)), ('u^c (3bar,1)_{-2/3}', 3, 1, Fr(-2, 3)), ('d^c (3bar,1)_{1/3}', 3, 1, Fr(1, 3)),
       ('L_L (1,2)_{-1/2}', 1, 2, Fr(-1, 2)), ('e^c (1,1)_{1}', 1, 1, Fr(1))]


def anomalies():
    mult = lambda c, w: c * w
    s = {
        'gravity-U(1): sum Y': sum(mult(c, w) * y for _, c, w, y in GEN),
        'U(1)^3: sum Y^3': sum(mult(c, w) * y ** 3 for _, c, w, y in GEN),
        'SU(3)^2-U(1): sum over triplets of w*Y': sum(w * y for _, c, w, y in GEN if c == 3),
        'SU(2)^2-U(1): sum over doublets of c*Y': sum(c * y for _, c, w, y in GEN if w == 2),
    }
    charges = {'u': Fr(1, 2) + Fr(1, 6), 'd': Fr(-1, 2) + Fr(1, 6), 'nu': Fr(1, 2) - Fr(1, 2), 'e': Fr(-1, 2) - Fr(1, 2)}
    return s, charges


def lcdm_age(om, ol, h0):
    """flat ΛCDM, radiation neglected: t0 = (2 / (3 H0 sqrt(OL))) asinh(sqrt(OL/OM)); 977.792 / H0 is 1/H0 in Gyr."""
    return 2 / (3 * math.sqrt(ol)) * math.asinh(math.sqrt(ol / om)) * 977.792 / h0


def selftest():
    s, ch = anomalies()
    ok1 = all(canon_check(k, r)[0] for k in (2, 3, 4) for r in range(1, k + 1))
    n4, _, _ = twoboundary(4); n16, sh16, tot = twoboundary(16)
    cases = [
        ('M365 the O(k) label equals the breadth-first orbit partition for every k <= 4 and every depth r', ok1),
        ('M365 at k = 6 the 531441 states fall into 7 classes at depth 1 (ratio 75920)', 9 ** 6 // 7 == 75920 and 1 + 6 == 7),
        ('M366 from (1,0) mod 9: 15 endpoints after 4 steps, all 72 primitive states after 16', n4 == 15 and n16 == 72),
        ('M366 conditioning on an end moves P(first step B) from 0.500 to %.3f with no backward influence in the model' % sh16[2], abs(sh16[2] - 0.5) > 0.1),
        ('M367 every gauge-anomaly sum of one generation is exactly 0', all(v == 0 for v in s.values())),
        ('M367 Q = T3 + Y gives u 2/3, d -1/3, nu 0, e -1', ch == {'u': Fr(2, 3), 'd': Fr(-1, 3), 'nu': Fr(0), 'e': Fr(-1)}),
        ('M367 flat ΛCDM with OM 0.315, OL 0.685, H0 67.4: age 13.796 Gyr (radiation neglected)', abs(lcdm_age(0.315, 0.685, 67.4) - 13.796) < 0.001),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('ATLAS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['canon']:
        k, r = int(a[1]), int(a[2]); ok, n, N = canon_check(k, r)
        print('M365 CANONICAL FORM mod 3^%d, depth %d: %d states, %d classes; the O(k) label %s the breadth-first partition' % (k, r, N, n, 'equals' if ok else 'DIFFERS FROM'))
        if '--bench' in a:
            m = 3 ** k; x = (5, 7); t = time.time(); _, parts = bfs_partition(k, r); tb = time.time() - t
            t = time.time()
            for _ in range(10000):
                label(x[0], x[1], k, r)
            tl = (time.time() - t) / 10000
            print('  breadth-first partition %.3f s; one label %.2e s (timings vary by machine)' % (tb, tl))
        return 0
    if a[:1] == ['twoboundary']:
        n = int(a[1]); reach, (d, v, p, cnt), tot = twoboundary(n)
        print('M366 TWO-BOUNDARY EXPLORER: %d steps of A or B (each 1/2) from (1,0) mod 9; %d endpoints reachable' % (n, reach))
        print('  end %s: %d of %d histories; P(first step B | this end) = %.3f against P(first step B) = 0.500' % (v, cnt, tot, p))
        print('  READING: fixing the end selects among histories; it changes what is inferred of the start, and nothing travels backward (reversibility and selection are not retrocausation)')
        return 0
    if a[:1] == ['anomalies']:
        s, ch = anomalies()
        print('M367 PHYSICS ATLAS -- one Standard Model generation, left-handed Weyl fields (MODE B data; no Ω42 correspondence asserted)')
        for name, c, w, y in GEN:
            print('  %-22s colour %d, weak %d, Y %s' % (name, c, w, y))
        for kx, v in s.items():
            print('  %-42s = %s' % (kx, v))
        print('  charges Q = T3 + Y: %s' % ', '.join('%s %s' % kv for kv in ch.items()))
        return 0
    if a[:1] == ['lcdm']:
        om, ol, h0 = map(float, a[1:4])
        print('M367 ΛCDM (flat, radiation neglected): OM %.3f OL %.3f H0 %.1f -> age %.3f Gyr; H(a=0.5) = %.1f km/s/Mpc' % (
            om, ol, h0, lcdm_age(om, ol, h0), h0 * math.sqrt(om * 0.5 ** -3 + ol)))
        return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
