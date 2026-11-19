#!/usr/bin/env python3
"""space_prob.py -- the third space direction and the probability rule (Core L-544 (9), (10); Companion Part 173).

H-42. Modulo 9 the golden ratio is a Gaussian integer: phi -> 5 + i is an isomorphism of Z[phi]/9 onto Z[i]/9 that
carries the norm a^2 + ab - b^2 to x^2 + y^2; phi^6 = 5 + 8 phi is a square root of -1, the quarter-turn of the law. In the
3-adic limit the same holds at every depth (a square root of -1 lifts in Z_3[phi]). So the residues and the limit already
hold i: the Hermitian 2 x 2 matrices over Z[phi]/9 form a 3 + 1 space over Z/9 with interval t^2 - z^2 - x^2 - y^2, and
X -> A X A^T keeps it, carrying the y-direction to its negative. Only over the reals is i absent from Z[phi].
H-43. On the 81 states the invariant probability measures are the mixtures of the five orbit-uniform measures; for a
state psi of l2(81) the sector weights p_O = sum over O of |psi_x|^2 are kept by U_T, and the time average of |psi_x|^2
over one period is its orbit average; the uniform measure gives 8/27, 8/27, 8/27, 8/81 and 1/81.
    python3 tools/space_prob.py              # the values
    python3 tools/space_prob.py --selftest
Standard library only.
"""
import cmath, itertools, random, sys
from fractions import Fraction as F
M = 9
def mphi(u, v, m=M): a, b = u; c, d = v; return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)
def mi(u, v, m=M): a, b = u; c, d = v; return ((a * c - b * d) % m, (a * d + b * c) % m)
def iota(u, m=M): return ((u[0] + 5 * u[1]) % m, u[1] % m)
ELS = [(a, b) for a in range(M) for b in range(M)]
def T(s): return (s[1], (s[0] + s[1]) % M)
def orbits():
    seen, out = set(), []
    for s in ELS:
        if s in seen: continue
        o, x = [], s
        while x not in seen: seen.add(x); o.append(x); x = T(x)
        out.append(o)
    return sorted(out, key=len, reverse=True)
def sqrt_minus_one(k):
    m = 3 ** k
    return [(x, y) for x in range(m) for y in range(m) if mphi((x, y), (x, y), m) == (m - 1, 0)][:2] if k <= 4 else None
def herm(t, z, x, y): return [[((t + z) % M, 0), (x, (-y) % M)], [(x, y), ((t - z) % M, 0)]]
def cm(X, Y): return [[tuple(sum(v) % M for v in zip(*[mi(X[i][k], Y[k][j]) for k in range(2)])) for j in range(2)] for i in range(2)]
AH = [[(0, 0), (1, 0)], [(1, 0), (1, 0)]]
def coords(X): return ((X[0][0][0] + X[1][1][0]) * 5 % M, (X[0][0][0] - X[1][1][0]) * 5 % M, X[1][0][0], X[1][0][1])
def iv(c): return (c[0] ** 2 - c[1] ** 2 - c[2] ** 2 - c[3] ** 2) % M
def lorentz_ok():
    for c in itertools.product(range(M), repeat=4):
        Y = cm(cm(AH, herm(*c)), AH)
        if Y[0][0][1] or Y[1][1][1] or iv(coords(Y)) != iv(c): return False
    return coords(cm(cm(AH, herm(0, 0, 0, 1)), AH)) == (0, 0, 0, 8)
def sector_weights(psi, O):
    return [sum(abs(psi[x]) ** 2 for x in o) for o in O]
def values():
    O = orbits(); p6 = (1, 0)
    for _ in range(6): p6 = mphi(p6, (0, 1))
    rnd = random.Random(42); psi = {x: complex(rnd.gauss(0, 1), rnd.gauss(0, 1)) for x in ELS}
    n = sum(abs(v) ** 2 for v in psi.values()) ** 0.5; psi = {x: v / n for x, v in psi.items()}
    w0 = sector_weights(psi, O); psi1 = {T(x): v for x, v in psi.items()}; w1 = sector_weights(psi1, O)
    x0 = O[0][0]; avg = sum(abs(psi[y]) ** 2 for y in O[0]) / 24
    tav, ph = 0, dict(psi)
    for _ in range(24): tav += abs(ph[x0]) ** 2; ph = {T(x): v for x, v in ph.items()}
    return {'phi -> 5 + i is a ring isomorphism mod 9': all(iota(mphi(u, v)) == mi(iota(u), iota(v)) for u in ELS for v in ELS) and len({iota(u) for u in ELS}) == 81,
            'the norm a^2 + ab - b^2 goes to x^2 + y^2': all((u[0] ** 2 + u[0] * u[1] - u[1] ** 2) % M == (iota(u)[0] ** 2 + iota(u)[1] ** 2) % M for u in ELS),
            'phi^6 and its square': (p6, mphi(p6, p6)),
            'square roots of -1 in Z_3[phi]/3^k, k = 1 to 4': [bool(sqrt_minus_one(k)) for k in range(1, 5)],
            'A X A^T keeps the 3 + 1 interval over Z/9 and sends y to -y': lorentz_ok(),
            'orbit lengths': [len(o) for o in O],
            'uniform sector weights': [str(F(len(o), 81)) for o in O],
            'sector weights kept by one step (max change)': max(abs(a - b) for a, b in zip(w0, w1)),
            'time average equals orbit average (difference)': abs(tav / 24 - avg)}
def selftest():
    v = values()
    t = [('phi -> 5 + i, a ring isomorphism of Z[phi]/9 onto Z[i]/9', v['phi -> 5 + i is a ring isomorphism mod 9']),
         ('the norm goes to x^2 + y^2', v['the norm a^2 + ab - b^2 goes to x^2 + y^2']),
         ('phi^6 = 5 + 8 phi squares to -1', v['phi^6 and its square'] == ((5, 8), (8, 0))),
         ('-1 has a square root in Z_3[phi] mod 3, 9, 27, 81', all(v['square roots of -1 in Z_3[phi]/3^k, k = 1 to 4'])),
         ('the 3 + 1 interval is kept, y goes to -y', v['A X A^T keeps the 3 + 1 interval over Z/9 and sends y to -y']),
         ('uniform weights 8/27, 8/27, 8/27, 8/81, 1/81', v['uniform sector weights'] == ['8/27', '8/27', '8/27', '8/81', '1/81']),
         ('sector weights are kept by the law', v['sector weights kept by one step (max change)'] < 1e-12),
         ('time average = orbit average', v['time average equals orbit average (difference)'] < 1e-12)]
    for n, ok in t: print('%-58s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('SPACE AND PROBABILITY SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    for k, x in values().items(): print('%s: %s' % (k, x))
