#!/usr/bin/env python3
"""levels.py -- the level ladder of the family and the experiential spectrum placement (Companion Part 89).
(1) LEVELS: at every scale 3^n the states of Z[phi]/3^n fall into levels by their 3-adic valuation; each level is the
whole unit set of a coarser scale (FP-CoreRecursion). (2) SPECTRUM: the frozen placement test of
records/consciousness/spectrum_frozen.txt (SHA-256 checked). Exact values; readings typed in the conjecture register.
Standard library and the tools.   python3 records/consciousness/levels.py   # diffed in CI against levels_output.txt
"""
import hashlib, os, sys
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.join(HERE, '..', '..')
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'scripts')]
import consciousness as cs
FROZEN = os.path.join(HERE, 'spectrum_frozen.txt'); FROZEN_SHA = '7e282c44f830f634763fa706da2ffddcfd114995b8e6babdd0c2d6a4a621cd11'


def ladder(n):
    m = 3 ** n; out = {}
    for a in range(m):
        for b in range(m):
            if (a, b) == (0, 0): k = n
            else:
                k, x, y = 0, a, b
                while x % 3 == 0 and y % 3 == 0: x //= 3; y //= 3; k += 1
            out.setdefault(k, [0, (a, b)]); out[k][0] += 1
    rows = []
    for k in sorted(out):
        s = out[k][1]; t = (s[1], (s[0] + s[1]) % m); p = 1
        while t != s: t = (t[1], (t[0] + t[1]) % m); p += 1
        rows.append((k, out[k][0], p))
    return rows


N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
half = lambda s: None if not (s[0] % 3 or s[1] % 3) else ('SEVENTH' if N(s) in (1, 2, 4) else 'MANIFEST')
anti = lambda s: ((-s[0]) % 9, (-s[1]) % 9)


def chance(states):
    """P(opposite halves) and P(antipodes) for two states drawn independently from the given list."""
    n = len(states)
    opp = sum(1 for x in states for y in states if half(x) and half(y) and half(x) != half(y)) / n ** 2
    ant = sum(1 for x in states for y in states if y == anti(x) and x != (0, 0)) / n ** 2
    return opp, ant


def tail(p, k, n): return sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


if __name__ == '__main__':
    print('LEVELS OF THE FAMILY (Companion Part 89) -- level = 3-adic valuation of the state at scale 3^n [CDT-A]')
    for n in (1, 2, 3, 4):
        print('  mod %-3d %s' % (3 ** n, ' | '.join('level %d: %d states, period %d' % r for r in ladder(n))))
    print('  rule: at mod 3^n, level k (k < n) holds 8 x 9^(n-1-k) states of period 8 x 3^(n-1-k); level n is the still point;')
    print('  level k at mod 3^n is the unit set of mod 3^(n-k), carried by 3^k (FP-CoreRecursion)')
    sha = hashlib.sha256(open(FROZEN, 'rb').read()).hexdigest()
    print('EXPERIENTIAL SPECTRUM PLACEMENT -- frozen %s (%s)' % ('VERIFIED' if sha == FROZEN_SHA else 'CHANGED', sha[:12]))
    pairs = [[c.strip() for c in l.split('|')][1:] for l in open(FROZEN, encoding='utf-8') if l.startswith('PAIR')]
    S81 = [(a, b) for a in range(9) for b in range(9)]; R1 = [(1, b) for b in range(9)]
    pu = chance(S81); pc = chance(R1)
    h1 = h2 = 0
    for x, y in pairs:
        sx, sy = cs.state('What is %s?' % x), cs.state('What is %s?' % y)
        o = bool(half(sx) and half(sy) and half(sx) != half(sy)); a = sy == anti(sx); h1 += o; h2 += a
        print('  %-9s %s %-8s | %-13s %s %-8s | opposite halves %-3s | antipodes %s' % (x, sx, half(sx), y, sy, half(sy), 'YES' if o else 'NO', 'YES' if a else 'NO'))
    print('  P1 opposite halves: %d of 4 | chance per pair %.4f uniform, %.4f given r1 = 1 (E13) | P(>= %d of 4) %.4f uniform, %.4f given r1' % (
        h1, pu[0], pc[0], h1, tail(pu[0], h1, 4), tail(pc[0], h1, 4)))
    print('  P2 antipodes:      %d of 4 | chance per pair %.4f uniform, %.4f given r1 = 1 (E13) | P(>= %d of 4) %.4f uniform, %.4f given r1' % (
        h2, pu[1], pc[1], h2, tail(pu[1], h2, 4), tail(pc[1], h2, 4)))
    print('READING: the ladder is exact; the placement test is a placement, entered whichever way it falls (L-498); it measures where')
    print('words fall, not what an emotion is (R_C), and it grades nothing (L-490).')
