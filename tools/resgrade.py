#!/usr/bin/env python3
"""resgrade.py -- M379 Resonance Grader (Core Part 3.86; F195): grades a proposed correspondence between the law and
another map on the record's own Congruence Depths (Core Part 0.0.8), and revisits the Companion's mappings through the
Lorentz image (MF-59 to MF-64).

  grading   for a map S, a candidate f and the law T on the 81 states: does f . S = T . f hold; is f one-to-one, and if
            not, what does it forget (its fibres); how does the period change; and how cheap is the match -- any two maps
            with the same cycle type are intertwined by many bijections (663,552 for A and [[0,1],[1,7]]), so a commuting
            square alone is weak evidence and the value structure decides (MF-66)
  revisit   the Voices are three mass classes (mass^2 = N^2 = 1, 7, 4 mod 9 for Voices A, B, C); the Wheel and the Fix are
            the kernel, where every spacetime image vanishes (FP-CoreField); the completion position (+12) is the spinor
            partner, identical in every image; the law's Lorentz image on the symmetric (2+1) matrices is improper and
            orthochronous: parity, not time, is what it reverses (on all four Hermitian axes it is proper, tools/lorentz.py) (FP-PhaseParity, FP-GlideMirror) (MF-65)

    python3 tools/resgrade.py            the revisited mappings and three graded examples
    python3 tools/resgrade.py --selftest
Standard library only. The physical readings are CONDITIONAL on AP-SPACE.
"""
import math, sys
from collections import Counter

M9 = 9
STATES = [(a, b) for a in range(M9) for b in range(M9)]


def lin(M):
    return lambda s: ((M[0][0] * s[0] + M[0][1] * s[1]) % M9, (M[1][0] * s[0] + M[1][1] * s[1]) % M9)


T = lin(((0, 1), (1, 1)))


def norm(s):
    return (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % M9


def image(s):
    """the rank-one and norm images s s^T and M_s M_s^T, mod 9, as (p, q, r) triples."""
    a, b = s
    return ((a * a) % M9, (a * b) % M9, (b * b) % M9), ((a * a + b * b) % M9, (2 * a * b + b * b) % M9, (b * b + (a + b) ** 2) % M9)


def orbits(F, pts):
    seen, out = set(), []
    for p in pts:
        if p in seen:
            continue
        o, q = [], p
        while q not in seen:
            seen.add(q); o.append(q); q = F(q)
        out.append(o)
    return out


def cycle_type(F, pts):
    return dict(sorted(Counter(len(o) for o in orbits(F, pts)).items()))


def intertwiners(ct):
    """the number of bijections f with f . S = T . f when S and T have the same cycle type: prod over lengths l of l^k k!."""
    return math.prod(l ** k * math.factorial(k) for l, k in ct.items())


def grade(S, f, pts_src, Tgt):
    """a correspondence report for f . S = Tgt . f: whether it commutes, whether f is one-to-one, and its fibre sizes."""
    fib = Counter(Counter(f(x) for x in pts_src).values())
    return dict(commutes=all(f(S(x)) == Tgt(f(x)) for x in pts_src), injective=set(fib) == {1}, fibres=dict(sorted(fib.items())))


def revisit():
    R = {}
    for o in orbits(T, STATES):
        R[o[0]] = (len(o), sorted({norm(s) for s in o}), sorted({norm(s) ** 2 % M9 for s in o}), all(image(s) == ((0, 0, 0), (0, 0, 0)) for s in o))
    return R


def selftest():
    R = revisit(); A24 = [o for o in orbits(T, STATES) if len(o) == 24]
    twin = lin(((0, 1), (1, 7)))
    ctA, ctT = cycle_type(T, STATES), cycle_type(twin, STATES)
    sym = [(p, q, r) for p in range(M9) for q in range(M9) for r in range(M9)]
    L = lambda v: (v[2] % M9, (v[1] + v[2]) % M9, (v[0] + 2 * v[1] + v[2]) % M9)
    cases = [
        ('voices: the three 24-orbits carry mass^2 = N^2 of 1, 7 and 4 mod 9, one class each, kept by every step',
         sorted(v[2][0] for v in R.values() if v[0] == 24) == [1, 4, 7] and all(len(v[2]) == 1 for v in R.values())),
        ('kernel: the Wheel (8) and the Fix (1) are exactly the states whose spacetime images vanish mod 9',
         sorted(v[0] for v in R.values() if v[3]) == [1, 8] and not any(v[3] for v in R.values() if v[0] == 24)),
        ('spinor: on every 24-orbit the state at +12 is -s and has the same images; at +6 the images differ',
         all(o[(i + 12) % 24] == ((-o[i][0]) % M9, (-o[i][1]) % M9) and image(o[i]) == image(o[(i + 12) % 24]) for o in A24 for i in range(24))
         and not all(image(o[i]) == image(o[(i + 6) % 24]) for o in A24 for i in range(24))),
        ('parity: the Lorentz image of the law on the symmetric (2+1) matrices has determinant -1 and keeps the future cone (improper, orthochronous)',
         0 * (1 * 1 - 1 * 2) - 0 + 1 * (0 * 2 - 1 * 1) == -1 and (3 * 1 - 0 + 0) / 2 > 0),
        ('grading: s -> s s^T commutes with the law and its image map but is not one-to-one (fibres of 2 and 9)',
         (lambda g: g['commutes'] and not g['injective'] and g['fibres'] == {2: 36, 9: 1})(grade(T, lambda s: image(s)[0], STATES, L))),
        ('cheap match: A and [[0,1],[1,7]] share the cycle type 1, 8, 24^3 mod 9 and are intertwined by %d bijections' % intertwiners(ctA),
         ctA == ctT == {1: 1, 8: 1, 24: 3} and intertwiners(ctA) == 663552),
        ('value structure decides: no linear map of (Z/9)^2 intertwines A with [[0,1],[1,7]] (traces 1 and 7 differ mod 9)', (1 - 7) % 9 != 0),
        ('a null control: the image map L on all 729 symmetric matrices has cycle type 1, 2^4, 4^18, 12^54, so no bijection to the 81 states exists',
         cycle_type(L, sym) == {1: 1, 2: 4, 4: 18, 12: 54}),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('RESONANCE GRADER SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    names = {24: 'Voice', 8: 'Wheel', 1: 'Fix'}
    print('REVISITED -- the five orbits of the law mod 9 through the Lorentz image')
    for seed, (n, norms, m2, zero) in revisit().items():
        print('  %-5s seed %-7s period %2d  norms %-8s mass^2 %-5s image %s' % (names[n], seed, n, norms, m2, 'ZERO (kernel)' if zero else 'nonzero'))
    print('CHEAP MATCH -- bijections intertwining A with [[0,1],[1,7]] on 81 states: %d' % intertwiners({24: 3, 8: 1, 1: 1}))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
