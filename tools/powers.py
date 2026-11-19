#!/usr/bin/env python3
"""powers.py -- the powers of the law and their cycle structure, for mapping by derived symmetry (Core L-510 (Mapping
record); Companion Part 168).

An object that does not carry the whole 24-step law may carry a subgroup of it. For every k dividing 24 this tool gives
the order of T^k, whether it is +I or -I, its cycles on the canonical orbit (gcd(24, k) cycles of 24/gcd(24, k)) and on
the whole surface of 81 states, its fixed states, and the count of equivariant identifications of two free sets of n
orbits of length m (n! m^n), the mapping freedom a correspondence at that level leaves.
    python3 tools/powers.py                 # the table
    python3 tools/powers.py --freedom N M   # n! m^n
    python3 tools/powers.py --selftest
Standard library only.
"""
import math, sys
M = 9
def T(s): return (s[1], (s[0] + s[1]) % M)
def Tk(s, k):
    for _ in range(k): s = T(s)
    return s
def mat(k):
    a, b, c, d = 1, 0, 0, 1
    for _ in range(k): a, b, c, d = b, (a + b) % M, d, (c + d) % M
    return ((a, b), (c, d))
CANON = [(2, 5)]
while True:
    n = T(CANON[-1])
    if n == CANON[0]: break
    CANON.append(n)
def cycles(states, k):
    S, seen, out = set(states), set(), []
    for s in states:
        if s in seen: continue
        c, x = 0, s
        while True:
            seen.add(x); x = Tk(x, k); c += 1
            if x == s: break
        out.append(c)
    return sorted(out)
ALL = [(a, b) for a in range(M) for b in range(M)]
def freedom(n, m): return math.factorial(n) * m ** n
def row(k):
    A = mat(k); I = ((1, 0), (0, 1)); mI = ((8, 0), (0, 8))
    o = next(j for j in range(1, 25) if mat(k * j) == I)
    can = cycles(CANON, k); allc = cycles(ALL, k)
    return dict(k=k, matrix=A, order=o, sign='+I' if A == I else ('-I' if A == mI else ''), canonical=(len(can), can[0]),
                surface={L: allc.count(L) for L in sorted(set(allc))}, fixed=[s for s in ALL if Tk(s, k) == s])
def selftest():
    r = {k: row(k) for k in (1, 2, 3, 4, 6, 8, 12, 24)}
    t = [('the canonical orbit has 24 states from (2, 5)', len(CANON) == 24),
         ('A^6 = [[5, 8], [8, 4]] (mod 9), of order 4', r[6]['matrix'] == ((5, 8), (8, 4)) and r[6]['order'] == 4),
         ('A^12 = -I, A^24 = +I', r[12]['sign'] == '-I' and r[24]['sign'] == '+I'),
         ('T^6 cuts the canonical orbit into 6 cycles of 4', r[6]['canonical'] == (6, 4)),
         ('T^3 cuts it into 3 cycles of 8', r[3]['canonical'] == (3, 8)),
         ('T^6 on the surface: (0, 0) fixed and 20 cycles of 4', r[6]['surface'] == {1: 1, 4: 20}),
         ('T^1 to T^6 and T^12 fix (0, 0) alone', all(r[k]['fixed'] == [(0, 0)] for k in (1, 2, 3, 4, 6, 12))),
         ('T^8 fixes the nine states of the 3-shell', sorted(r[8]['fixed']) == [(a, b) for a in (0, 3, 6) for b in (0, 3, 6)]),
         ('the freedom of 6 orbits of 4 is 2,949,120', freedom(6, 4) == 2949120),
         ('the apothem over the half-base is sqrt(317)/11', abs(math.sqrt(317) / 11 - math.sqrt(1 + (14 / 11) ** 2)) < 1e-12)]
    for n, ok in t: print('%-58s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('POWERS SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if len(a) == 3 and a[0] == '--freedom': print(freedom(int(a[1]), int(a[2]))); sys.exit(0)
    print('  k  A^k (mod 9)        order sign  canonical orbit     surface (length: count)')
    for k in (1, 2, 3, 4, 6, 8, 12, 24):
        r = row(k)
        print('%3d  %-18s %5d %-4s  %2d cycles of %-4d  %s' % (k, r['matrix'], r['order'], r['sign'], r['canonical'][0], r['canonical'][1], r['surface']))
    phi = (1 + 5 ** .5) / 2; ap = math.sqrt(317) / 11
    print('apothem / half-base = sqrt(317)/11 = %.6f; phi = %.6f; difference %.4f percent' % (ap, phi, (ap / phi - 1) * 100))
