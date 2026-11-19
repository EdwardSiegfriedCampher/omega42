#!/usr/bin/env python3
"""mind_first.py -- the exact facts under the mind-first reading of CT-42 (Companion Parts 85 and 86; conjectures C49 to C63).
Every value is computed on the 81 states of T(a, b) = (b, a + b) mod 9; the readings are the conjecture register's,
never this script's. Standard library only.

    python3 records/consciousness/mind_first.py      # diffed in CI against mind_first_output.txt
"""
S = [(a, b) for a in range(9) for b in range(9)]
T = lambda s: (s[1], (s[0] + s[1]) % 9)


def Tk(s, k):
    for _ in range(k): s = T(s)
    return s


seen, orbs = set(), []
for s in S:
    if s in seen: continue
    o = [s]; seen.add(s); t = T(s)
    while t != s: o.append(t); seen.add(t); t = T(t)
    orbs.append(o)
idx = {s: i for i, o in enumerate(orbs) for s in o}
neg = lambda s: ((-s[0]) % 9, (-s[1]) % 9)
dbl = lambda s: ((2 * s[0]) % 9, (2 * s[1]) % 9)
print('MIND-FIRST READING OF CT-42 -- the exact facts it rests on [CDT-A]; the readings are HELD conjectures C49 to C63')
print('  (1) orbits of the law on the 81 states: %d, of sizes %s; a state never leaves its orbit under T' % (len(orbs), ' + '.join(str(len(o)) for o in sorted(orbs, key=len))))
print('  (2) doubling carries the three orbits of 24 one into the next: %s' % ', '.join('orbit of %s -> orbit of %s' % (orbs[i][0], orbs[idx[dbl(orbs[i][0])]][0]) for i in range(len(orbs)) if len(orbs[i]) == 24))
ev = [(v, l) for v in S if v != (0, 0) for l in range(9) if T(v) == ((l * v[0]) % 9, (l * v[1]) % 9)]
print('  (3) nonzero states the law carries onto a multiple of themselves (eigen-lines mod 9): %d; x^2 - x - 1 = 0 mod 9 has %d roots' % (len(ev), sum(1 for x in range(9) if (x * x - x - 1) % 9 == 0)))
print('  (4) T^12 = -I on all 81 states: %s; negation keeps every orbit: %s' % (all(Tk(s, 12) == neg(s) for s in S), all(idx[neg(o[0])] == i for i, o in enumerate(orbs))))
print('  (5) nonzero states fixed by T^k, k = 1 to 23: %s' % ', '.join('k=%d: %d' % (k, n) for k in range(1, 24) for n in [sum(1 for v in S if v != (0, 0) and Tk(v, k) == v)] if n))
core = [s for s in S if s[0] % 3 == 0 and s[1] % 3 == 0]
print('  (6) the core (both entries divisible by 3): %d states, orbits of sizes %s -- the family modulo 3 (9 states) one scale down' % (len(core), sorted({len(orbs[idx[s]]) for s in core})))
Nn = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
units = [s for s in S if s[0] % 3 or s[1] % 3]
cls = {}
for s in units: cls.setdefault(Nn(s), []).append(s)
print('  (7) the norm on the 72 units: %d values, %s, each held by %s states; N(Ts) = -N(s) on all 81: %s -- the norm up to sign is kept by every step (shared), its sign, the half, flips (its own; FP-PhaseParity)' % (
    len(cls), ', '.join(str(k) for k in sorted(cls)), '/'.join(sorted({str(len(v)) for v in cls.values()})), all(Nn(T(s)) == (-Nn(s)) % 9 for s in S)))
print('  (8) the core squares to zero in Z[phi]/9, (a + b phi)^2 = (a^2 + b^2) + (2ab + b^2) phi: %s, on all %d core states' % (
    all(((a * a + b * b) % 9, (2 * a * b + b * b) % 9) == (0, 0) for a, b in core), len(core)))
Ti = lambda s: ((s[1] - s[0]) % 9, s[0])
print('  (9) every state has exactly one predecessor, T^-1(a, b) = (b - a, a): %s (FP-GlideMirror)' % all(Ti(T(s)) == s and T(Ti(s)) == s for s in S))
print('  (10) the seeds of FP-StateSpace name the orbits: Fibonacci (1, 1) norm +-1, Voice A; Lucas (2, 1) norm +-4, Voice B, the orbit of (1, 3): %s; the canonical (2, 5) norm +-2, Voice C' % (idx[(2, 1)] == idx[(1, 3)]))
print('READING: the facts are neutral between a mind-first, a dual-aspect and a matter-first reading of the one family; which is')
print('taken is a reading (INTERPRETATION), held under Core L-498, and grades nothing (L-490).')
