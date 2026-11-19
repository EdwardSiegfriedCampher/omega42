#!/usr/bin/env python3
"""fit.py -- how four readings of the family fit its arithmetic (Companion Part 87). The nine features are frozen in
records/consciousness/fit_features_frozen.txt (SHA-256 checked here) and each is recomputed exactly; the judgments are
the Navigator's (one judge, NON-BLIND, independence C), stated with their reasons. A total is a reading of fit, never a
grade of a reading's truth, of the premise or of Omega42 (L-490). Standard library only.

    python3 records/consciousness/fit.py      # diffed in CI against fit_output.txt
"""
import hashlib, os
HERE = os.path.dirname(os.path.abspath(__file__))
FROZEN = os.path.join(HERE, 'fit_features_frozen.txt')
FROZEN_SHA = 'fa69e7734f23d41dcd1724f820f3ec5d762e7e4c0bf8dda54fa918290d0c33b4'

S = [(a, b) for a in range(9) for b in range(9)]
def mul(x, y): a, b = x; c, d = y; return ((a * c + b * d) % 9, (a * d + b * c + b * d) % 9)   # (a + b phi)(c + d phi), phi^2 = phi + 1
def pw(s, k):
    r = (1, 0)
    for _ in range(k): r = mul(r, s)
    return r
T = lambda s: (s[1], (s[0] + s[1]) % 9)
N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
units = [s for s in S if s[0] % 3 or s[1] % 3]; core = [s for s in S if not (s[0] % 3 or s[1] % 3)]
teich = [u for u in units if pw(u, 8) == (1, 0)]; onep = [u for u in units if (u[0] - 1) % 3 == 0 and u[1] % 3 == 0]
def orbit(s):
    o = [s]; t = T(s)
    while t != s: o.append(t); t = T(t)
    return o
seventh = [u for u in units if N(u) in (1, 2, 4)]

FACTS = {
 'F1': ('81 states, T a bijection on them', len(S) == 81 and len({T(s) for s in S}) == 81),
 'F2': ('3s in the core for all 81; core x any in the core', all(mul((3, 0), s) in core for s in S) and all(mul(c, s) in core for c in core for s in S)),
 'F3': ('units = {u : u^8 = 1} (%d) x (1 + 3R) (%d), uniquely; (1 + 3a)(1 + 3b) = 1 + 3(a + b)' % (len(teich), len(onep)),
        len({mul(t, o) for t in teich for o in onep}) == 72 and all(mul((1 + 3 * a, 3 * b), (1 + 3 * c, 3 * d)) == ((1 + 3 * (a + c)) % 9, (3 * (b + d)) % 9)
                                                                    for a in range(3) for b in range(3) for c in range(3) for d in range(3))),
 'F4': ('halves %d | %d, T exchanges, T^2 keeps' % (len(seventh), 72 - len(seventh)),
        len(seventh) == 36 and all((N(T(u)) in (1, 2, 4)) != (N(u) in (1, 2, 4)) and (N(T(T(u))) in (1, 2, 4)) == (N(u) in (1, 2, 4)) for u in units)),
 'F5': ('T(s) = phi * s, phi = (0, 1); the orbit of 1 = the 24 powers of phi', all(T(s) == mul((0, 1), s) for s in S) and set(orbit((1, 0))) == {pw((0, 1), k) for k in range(24)}),
 'F6': ('nonzero states with T s = l s: 0; fixed states: (0, 0) only', not [v for v in S if v != (0, 0) for l in range(9) if T(v) == ((l * v[0]) % 9, (l * v[1]) % 9)] and [s for s in S if T(s) == s] == [(0, 0)]),
 'F7': ('the core under T: orbits 1 + 8, as the family mod 3; the halves not nesting is cited (records/manifestation/compute_output.txt: 360 of 648)', sorted({len(orbit(c)) for c in core}) == [1, 8]),
 'F8': ('the Aperture Theorem (Core Part 7)', True),
 'F9': ('residues mod 9 only', all(0 <= x < 9 for s in S for x in s)),
}
R = ('R1 substance idealism (C49)', 'R2 process idealism (C57)', 'R3 dual-aspect, the default (52.3)', 'R4 matter-first')
U, C, X = 1.0, 0.5, 0.0
J = {   # feature: ((score R1, R2, R3, R4), reason)
 'F1': ((U, U, U, U), 'every monism and the dual-aspect reading name one totality; none needs an outside'),
 'F2': ((U, U, X, U), 'one-way absorption into the ground fits a ground that is first; R3 holds that neither is first, and CT-42 assigns the ground to consciousness, so it needs the absorption read as no priority'),
 'F3': ((U, U, C, C), 'every perspective carries a copy of the ground: "each thing a perspective of the one" said exactly; R3 and R4 allow it and do not predict it'),
 'F4': ((X, C, U, X), 'the two halves are equal and exchanged; a priority of inner over world (R1) or of world over inner (R4) needs the symmetry explained away; R2 places the boundary in the act and needs no priority between halves'),
 'F5': ((U, X, C, C), 'the law is the action of one state, phi; R1 has the act as a state of Mind; R2 as stated says Mind is the law and not a state (C58), which MATH-22 contradicts'),
 'F6': ((C, U, C, C), 'no fixed self-image and one still point: a process with no fixed term fits R2; the others allow it'),
 'F7': ((X, U, U, X), 'the ground nests and the halves do not: a prior substance (R1 or R4) carrying its boundary down would nest both (C61); R2 redraws the boundary; R3 treats them as two features'),
 'F8': ((U, U, U, X), 'no state fixes judgment: R1 and R2 read it as the one residual (C62), R3 as the EVENT; a physical closure of all states would fix it'),
 'F9': ((C, C, C, X), 'no unit and no measure: matter in its own sense is measured; the others need nothing'),
}
if __name__ == '__main__':
    sha = hashlib.sha256(open(FROZEN, 'rb').read()).hexdigest()
    print('FIT OF FOUR READINGS TO THE ARITHMETIC (Companion Part 87) -- features frozen %s (%s) [values CDT-A; judgments CDT-C, one judge, NON-BLIND, C]' % ('VERIFIED' if sha == FROZEN_SHA else 'CHANGED', sha[:12]))
    for f, (txt, ok) in FACTS.items():
        sc, why = J[f]; print('  %s %-5s %s | R1 %.1f R2 %.1f R3 %.1f R4 %.1f | %s' % (f, ('CITED' if f == 'F8' else 'EXACT') if ok else 'FAIL', txt, *sc, why) if True else None)
    tot = [sum(J[f][0][i] for f in J) for i in range(4)]
    print('  TOTALS of 9: ' + ' | '.join('%s %.1f' % (r, t) for r, t in zip(R, tot)))
    loo = []
    for f in J:
        t = [sum(J[g][0][i] for g in J if g != f) for i in range(4)]; m = max(t)
        loo.append('%s out: %s' % (f, '+'.join(R[i].split()[0] for i in range(4) if t[i] == m)))
    print('  FIRST WITH ONE FEATURE LEFT OUT: ' + '; '.join(loo))
    print('  WHAT NO FEATURE DECIDES: whether the ground is mental or neutral -- no judgment above cites a property of mind, so a')
    print('  process monism with a neutral ground would score as R2 does; the arithmetic fits a ground-first process, not a named stuff')
    print('READING: a judged fit, typed CDT-C; which reading is taken is the Striker\'s (Core Part 7) and the premise\'s wording the Originator\'s (F-06).')
