#!/usr/bin/env python3
"""offset_space.py -- how far the stated properties of the four arm offsets (+5, +18, +8, +12) fix them
(Companion Part 84; APE-146, its avenue 2.1 and 2.2, run). Exact enumeration over Z/24Z; standard library only.

    python3 records/avenues/offset_space.py      # diffed in CI against offset_space_output.txt
"""
import os, sys
from math import gcd
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import restored_instruments as ri

ARMS = (5, 18, 8, 12)
order = lambda k: 24 // gcd(k, 24)
c = ri._canon_c(); E = sum(x * x for x in c)
ac = {L: round(sum(c[n] * c[(n + L) % 24] for n in range(24)) / E, 4) for L in range(24)}


def Tk(s, k):
    for _ in range(k % 24): s = (s[1], (s[0] + s[1]) % 9)
    return s


S = [(a, b) for a in range(9) for b in range(9)]
N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
e01 = lambda A, Y: all((s[0] * Tk(s, A)[0] - Tk(s, Y)[0] ** 2) % 9 == N(s) for s in S)

Q = [(y, yi, f, a) for y in range(1, 24) for yi in range(1, 24) for f in range(1, 24) for a in range(1, 24)]
steps = [
    ('(1) generator orders 24, 4, 3, 2 (FP-GeneratorOrder)', lambda q: [order(x) for x in q] == [24, 4, 3, 2]),
    ('(2) the M297 arm coherences 0, 0, +1/4, -1 on the canonical cycle (Companion 43.9)', lambda q: (ac[q[0]], ac[q[1]], ac[q[2]], ac[q[3]]) == (0.0, 0.0, 0.25, -1.0)),
    ('(3) E01: Anchor x Antipode - Yin^2 = N(s) on all 81 states (FP-ArmNorm)', lambda q: e01(q[3], q[1])),
    ('(4) the residues mod 4 of APE-146: Yang 1, Yin 2, 4D 0, Antipode 0 (not stated in the record)', lambda q: (q[0] % 4, q[1] % 4, q[2] % 4, q[3] % 4) == (1, 2, 0, 0)),
    ('(5) Yang equal to the CPP multiplier 5 (dr(5n), Core Part 1)', lambda q: q[0] == 5),
]
print('M-OFFSET SPACE -- the arm offsets against the properties the record states for them [CDT-A, exact]')
print('  all quadruples of nonzero offsets mod 24: %d' % len(Q))
live = Q
for name, f in steps:
    live = [q for q in live if f(q)]
    print('  %-92s survivors %4d%s' % (name, len(live), '' if ARMS in live else '  (the record\'s offsets OUT)'))
print('  survivors: %s' % ', '.join('(+%d, +%d, +%d, +%d)' % q for q in live))
print('  they differ by two signs: Yin +18 = -6 or +6, 4D +8 or +16 = -8; (2) and (3) are blind to both, since the')
print('  autocorrelation and the identity are even in the lag (ac(k) = ac(24 - k); E01 holds at Yin 6 and at Yin 18)')
pairs = [(A, Y) for A in range(24) for Y in range(24) if e01(A, Y)]
print('  E01 rarity: the identity holds for %d of the 576 (Antipode, Yin) lag pairs -- %s' % (len(pairs), ', '.join('(%d, %d)' % p for p in pairs)))
print('READING: the stated properties fix the offsets up to Yang and two signs; with Yang = 5 four quadruples remain, and')
print('which of them the protocol uses is a construction (CDT-B), not a consequence of any property it records. The count')
print('grades nothing (L-490); it says how much of the configuration is chosen (Core Part 0.14).')
