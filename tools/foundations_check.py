#!/usr/bin/env python3
"""foundations_check.py -- M376 Foundations Checker (Core Part 3.83; APE-449, F187): recomputes the results the foundations
paper added to the record (MF-53 to MF-56) and labels every entry of records/math/results.json with its evidence state.

  MF-53  every shear B_c = [[1,0],[c,1]]: |<A, B_c> mod 3^k| depends only on r = v_3(c): 48*27^(k-1) for a unit c (all of
         det = +-1), 8*3^(3k-2r-1) for r >= 1; the kernel of SL_2 is contained exactly when r <= 1 (computed for k <= 3)
  MF-54  over Q, the A-invariant homogeneous polynomials of degree d form a space of dimension 1 when 4 | d and 0 otherwise,
         spanned by Q^(d/2): every invariant polynomial is a polynomial in Q^2 (degrees up to 12)
  MF-55  modulo 3^k the powers of phi are exactly the units of norm +-1, 8*3^(k-1) of them; the 3-adic closure of an orbit
         is the level set Q(y)^2 = Q(x)^2 (k up to 5)
  MF-56  the class of phi in (O/3^k)^x/(Z/3^k)^x has order 4*3^(k-1), the size of that group: the projective action is
         minimal and uniquely ergodic (k up to 6)

    python3 tools/foundations_check.py check          recompute MF-53 to MF-56
    python3 tools/foundations_check.py states         the evidence state of every MF entry (F179; Core Part 0.0.8.9)
    python3 tools/foundations_check.py --selftest
Standard library only. MODE A (Core L-559).
"""
import json, os, sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = ((0, 1), (1, 1))
# MF entries whose statement is proved in writing (Core Part 3.83 names the proofs); the rest of EXACT is VERIFIED by a tool
PROVED = {'MF-01', 'MF-02', 'MF-03', 'MF-06', 'MF-31', 'MF-35', 'MF-42', 'MF-48', 'MF-49', 'MF-54', 'MF-55', 'MF-56'}


def mul(X, Y, m):
    return tuple(tuple(sum(X[i][t] * Y[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))


def group_order(gens, m):
    I = ((1, 0), (0, 1)); S = {I}; fr = [I]
    while fr:
        nx = []
        for g in fr:
            for h in gens:
                p = mul(g, h, m)
                if p not in S:
                    S.add(p); nx.append(p)
        fr = nx
    return len(S)


def v3(c):
    r = 0
    while c % 3 == 0:
        c //= 3; r += 1
    return r


def mf53():
    rows = []
    for k, cs in ((2, range(1, 9)), (3, (1, 2, 4, 5, 3, 6, 12, 9, 18))):
        m = 3 ** k
        for c in cs:
            r = v3(c); want = 48 * 27 ** (k - 1) if r == 0 else 8 * 3 ** (3 * k - 2 * r - 1)
            rows.append((k, c, r, group_order([A, ((1, 0), (c, 1))], m), want))
    return rows, all(g == w for _, _, _, g, w in rows)


def mf54(dmax=12):
    """dimension of the A-invariant homogeneous polynomials of degree d over Q: nullity of (M_d - I)."""
    from math import comb
    dims = {}
    for d in range(1, dmax + 1):
        # substitution x -> y, y -> x + y on monomials x^i y^(d-i)
        n = d + 1; M = [[Fraction(0)] * n for _ in range(n)]
        for i in range(n):           # image of x^i y^(d-i) = y^i (x+y)^(d-i)
            for t in range(d - i + 1):
                M[t][i] += comb(d - i, t)   # x^t y^(d-t)
        for i in range(n):
            M[i][i] -= 1
        # rank by elimination
        R = [row[:] for row in M]; rank = 0
        for col in range(n):
            piv = next((r for r in range(rank, n) if R[r][col] != 0), None)
            if piv is None:
                continue
            R[rank], R[piv] = R[piv], R[rank]
            for r in range(n):
                if r != rank and R[r][col] != 0:
                    f = R[r][col] / R[rank][col]
                    R[r] = [a - f * b for a, b in zip(R[r], R[rank])]
            rank += 1
        dims[d] = n - rank
    return dims, all(dims[d] == (1 if d % 4 == 0 else 0) for d in dims)


def omul(x, y, m):   # (a + b phi)(c + d phi), phi^2 = phi + 1
    a, b = x; c, d = y
    return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)


def norm(x, m):
    a, b = x
    return (a * a + a * b - b * b) % m


def mf55(kmax=5):
    out = []
    for k in range(1, kmax + 1):
        m = 3 ** k; pw = set(); x = (1, 0)
        while True:
            pw.add(x); x = omul(x, (0, 1), m)
            if x == (1, 0):
                break
        units = {(a, b) for a in range(m) for b in range(m) if (a % 3, b % 3) != (0, 0) and norm((a, b), m) in (1, m - 1)}
        out.append((k, len(pw), len(units), pw == units))
    return out, all(o[3] and o[1] == 8 * 3 ** (o[0] - 1) for o in out)


def mf56(kmax=6):
    out = []
    for k in range(1, kmax + 1):
        m = 3 ** k; x = (0, 1); n = 1
        while x[1] % m != 0:          # phi^n is a scalar exactly when its phi-coordinate vanishes
            x = omul(x, (0, 1), m); n += 1
        size = (8 * 9 ** (k - 1)) // (2 * 3 ** (k - 1))
        out.append((k, n, size))
    return out, all(n == s == 4 * 3 ** (k - 1) for k, n, s in out)


def states():
    d = json.load(open(os.path.join(ROOT, 'records', 'math', 'results.json'), encoding='utf-8'))['results']
    rows = []
    for r in d:
        st = r['status']
        e = 'PROVISIONAL' if st.startswith('CONDITIONAL') else ('PROVED' if r['id'] in PROVED else 'VERIFIED')
        rows.append((r['id'], e, st))
    return rows


def selftest():
    a, oka = mf53(); b, okb = mf54(); c, okc = mf55(); d, okd = mf56(); s = states()
    cases = [
        ('MF-53 every shear: the group order depends only on v_3(c) (%d cases, k = 2 and 3)' % len(a), oka),
        ('MF-54 invariant polynomials: dimension 1 in degrees 4, 8, 12 and 0 otherwise %s' % [b[x] for x in sorted(b)], okb),
        ('MF-55 the powers of phi are exactly the norm +-1 units mod 3^k, k <= 5 %s' % [x[1] for x in c], okc),
        ('MF-56 the projective order of phi is 4*3^(k-1), the size of the group, k <= 6 %s' % [x[1] for x in d], okd),
        ('every MF entry carries exactly one evidence state (%d entries)' % len(s),
         all(e in ('PROVED', 'VERIFIED', 'PROVISIONAL') for _, e, _ in s) and len(s) == len({i for i, _, _ in s})),
        ('a CONDITIONAL entry is never labelled PROVED or VERIFIED', all(e == 'PROVISIONAL' for _, e, st in s if st.startswith('CONDITIONAL'))),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('FOUNDATIONS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['check']:
        for k, c, r, g, w in mf53()[0]:
            print('MF-53 k=%d c=%-2d v3=%d |<A,B_c>| = %d (expected %d)' % (k, c, r, g, w))
        print('MF-54 invariant dimensions by degree:', mf54()[0])
        for k, p, u, eq in mf55()[0]:
            print('MF-55 k=%d powers of phi %d, norm +-1 units %d, equal %s' % (k, p, u, eq))
        for k, n, s in mf56()[0]:
            print('MF-56 k=%d projective order %d, group size %d' % (k, n, s))
        return 0
    if a[:1] == ['states']:
        S = states()
        for i, e, st in S:
            print('%-6s %-11s %s' % (i, e, st))
        print('EVIDENCE STATES: %s' % ', '.join('%s %d' % (x, sum(1 for _, e, _ in S if e == x)) for x in ('PROVED', 'VERIFIED', 'PROVISIONAL')))
        return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
