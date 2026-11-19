#!/usr/bin/env python3
"""waves.py -- the Omega42 Wave Dynamics Engine: one transfer-matrix engine for electrons, light and sound in Fibonacci
structures, the topological pump whose charge is the gap label, and the reach and limit of the classification modulo 9
(Companion Part 225; F218; APE-480).

Every system is a pair of unimodular letter matrices (M_a, M_b), multiplied in the Fibonacci order S_(k+1) = S_k S_(k-1),
the law of the words; the half-traces obey the trace map and keep the Fricke-Vogt invariant I.

  W1 offdiagonal-invariant  electrons with Fibonacci hoppings t_a, t_b: bond matrices [[E/t, -1/t], [t, 0]], unimodular;
                            I = (1/4)(t_a/t_b - t_b/t_a)^2 at every step and for every energy (exact)
  W2 acoustic-duality       a layer carries sound by [[cos, i Z sin], [i sin / Z, cos]], the optical layer with n = 1/Z, and
                            M(1/n) = J M(n) J with J the exchange: the transmittance of every stack is the same for n and 1/n,
                            so light and sound through the same Fibonacci order obey one law, index for impedance (exact)
  W3 shared-six-cycle       light and sound at the quarter wave and electrons with Fibonacci hoppings at E = 0 all start on
                            the six-cycle (0, 0, a) of the trace map; the diagonal model at E = 0 does not (exact)
  W4 pump-charge            the topological pump: sliding the phason of the Fibonacci potential once around its cycle pumps,
                            across each of the six widest gaps, a charge equal to minus the gap label n (numerical)
  W6 one-automorphism       the substitution is one automorphism of the free group: its abelianization is the law (letter counts),
                            its action on SL2 characters is the trace map with the Fricke cubic (transfer matrices) (exact)
  W5 mod9-equivariance      reduction modulo 9 commutes with the trace map, so every integer orbit carries a residue orbit of
                            period dividing 24; the residue does not decide boundedness: (1, 1, 1) is fixed and (1, 1, 10),
                            with the same residue, escapes (exact)

    python3 tools/waves.py --selftest
    python3 tools/waves.py --pump V      the pumped charge across the widest gaps for potential V
Standard library and numpy (W4 only); exact Fraction arithmetic in W1 to W3 and W5.
"""
import sys, math, itertools
from fractions import Fraction as F
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
def mm(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
def words(Ma, Mb, k, mul=mm):
    S = [Mb, Ma]
    while len(S) < k + 1: S.append(mul(S[-1], S[-2]))
    return S
def half_traces(S, tr=lambda m: (m[0][0] + m[1][1]) / 2): return [tr(m) for m in S]
def fv(x, k): return x[k + 1] ** 2 + x[k] ** 2 + x[k - 1] ** 2 - 2 * x[k + 1] * x[k] * x[k - 1] - 1
# W1
ok1 = True; vals = []
for ta, tb, E in ((F(1), F(2), F(1, 3)), (F(3, 2), F(1), F(-5, 7)), (F(1), F(1, 3), F(0)), (F(2, 5), F(7, 4), F(9, 2))):
    x = half_traces(words([[E / ta, -1 / ta], [ta, 0]], [[E / tb, -1 / tb], [tb, 0]], 12))
    want = (ta / tb - tb / ta) ** 2 / 4
    ok1 = ok1 and all(x[k + 1] == 2 * x[k] * x[k - 1] - x[k - 2] for k in range(2, 12)) and all(fv(x, k) == want for k in range(1, 12))
    vals.append('t = %s, %s, E = %s: I = %s' % (ta, tb, E, want))
P('offdiagonal-invariant', ok1, 'electrons on a chain whose hoppings t_a, t_b follow the Fibonacci word: the bond matrices [[E/t, -1/t], [t, 0]] are unimodular, their products obey the trace map, and',
  'I = (1/4)(t_a/t_b - t_b/t_a)^2 at every step, the same at every energy:', vals)
# W2: Gaussian rationals
class G:
    __slots__ = ('a', 'b')
    def __init__(s, a, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): return G(s.a + o.a, s.b + o.b)
    def __mul__(s, o): return G(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def n2(s): return s.a * s.a + s.b * s.b
    def __eq__(s, o): return s.a == o.a and s.b == o.b
def optical(n, c, s): return [[G(c), G(0, s / n)], [G(0, n * s), G(c)]]
def acoustic(Z, c, s): return [[G(c), G(0, Z * s)], [G(0, s / Z), G(c)]]
def T(M): t = M[0][0] + M[0][1] + M[1][0] + M[1][1]; return F(4) / t.n2()
J = [[G(0), G(1)], [G(1), G(0)]]
ok2 = True; six = None
for (cA, sA), (cB, sB) in (((F(0), F(1)), (F(0), F(1))), ((F(3, 5), F(4, 5)), (F(5, 13), F(12, 13)))):
    for ZA, ZB in ((F(46, 10), F(32, 10)), (F(3), F(5, 4))):           # impedances relative to the surroundings
        Sa = words(acoustic(ZA, cA, sA), acoustic(ZB, cB, sB), 14)
        So = words(optical(ZA, cA, sA), optical(ZB, cB, sB), 14)
        Sinv = words(optical(1 / ZA, cA, sA), optical(1 / ZB, cB, sB), 14)
        ok2 = ok2 and all(T(a) == T(o) == T(i) for a, o, i in zip(Sa, So, Sinv)) and mm(mm(J, optical(ZA, cA, sA)), J) == optical(1 / ZA, cA, sA)
        if cA == 0 and ZA == F(46, 10): six = [str(T(m)) for m in Sa[:7]]
P('acoustic-duality', ok2, 'sound through a layer of impedance Z is carried by [[cos, i Z sin], [i sin/Z, cos]], the optical layer of index n = 1/Z, and M(1/n) = J M(n) J: every Fibonacci stack transmits sound and light identically, index for impedance, exact for 15 generations;',
  'at the quarter wave the acoustic transmittance with impedance ratios 4.6 and 3.2 repeats with period six:', six)
# W3
def six_start(x): return x[0] == 0 and x[1] == 0
xo = half_traces(words(optical(F(2), F(0), F(1)), optical(F(3, 2), F(0), F(1)), 8), tr=lambda m: (m[0][0] + m[1][1]).a / 2)
xa = half_traces(words(acoustic(F(46, 10), F(0), F(1)), acoustic(F(32, 10), F(0), F(1)), 8), tr=lambda m: (m[0][0] + m[1][1]).a / 2)
xe = half_traces(words([[F(0), F(-1)], [F(1), F(0)]], [[F(0), F(-1, 3)], [F(3), F(0)]], 8))
V = F(1); xd = half_traces(words([[F(0) - V, F(-1)], [F(1), F(0)]], [[F(0), F(-1)], [F(1), F(0)]], 8))
per6 = lambda x: all(x[k] == x[k + 6] for k in range(len(x) - 6))
P('shared-six-cycle', six_start(xo) and six_start(xa) and six_start(xe) and per6(xo) and per6(xa) and per6(xe) and not per6(xd),
  'light and sound at the quarter wave and electrons with Fibonacci hoppings at E = 0 start their trace orbits at (0, 0, a) and repeat with period six: light', [str(v) for v in xo[:6]], ', sound', [str(v) for v in xa[:6]], ', electrons', [str(v) for v in xe[:6]],
  '; the on-site model at E = 0, V = 1 does not, its orbit', [str(v) for v in xd[:6]], 'growing: the shared cycle belongs to the models whose letter matrices are traceless at the frequency')
# W4
def pump(V, L=89, p=55, betas=(2.0, 5.0), N=600, top=6):
    import numpy as np
    def chain(th, beta):
        j = np.arange(L); b = p / L
        return V * np.tanh(beta * (np.cos(2 * np.pi * b * j + 2 * np.pi * th) - np.cos(np.pi * b))) / np.tanh(beta)
    def pol(th, nf, beta):
        H = np.diag(chain(th, beta)) - np.eye(L, k=1) - np.eye(L, k=-1); H[0, L - 1] = H[L - 1, 0] = -1
        w, v = np.linalg.eigh(H); Phi = v[:, :nf]
        U = np.exp(2j * np.pi * np.arange(L) / L)
        return np.angle(np.linalg.det(Phi.conj().T @ (U[:, None] * Phi))) / (2 * np.pi), w
    res = []
    for beta in betas:
        _, w = pol(0.0, 1, beta)
        gaps = sorted([(w[i + 1] - w[i], i + 1) for i in range(L - 1)], reverse=True)[:top]
        for g, nf in gaps:
            ids = nf / L; lab = min(range(-20, 21), key=lambda n: abs(((n * p / L - ids + 0.5) % 1) - 0.5))
            tot = 0.0; prev, _ = pol(0.0, nf, beta); big = 0
            for k in range(1, N + 1):
                cur, _ = pol(k / N, nf, beta); d = cur - prev; d -= round(d); tot += d; prev = cur; big = max(big, abs(d))
            res.append((beta, round(float(g), 3), nf, lab, round(tot, 6), big))
    return res
pr = pump(1.5)
ok4 = all(abs(tot + lab) < 1e-6 and big < 0.05 for _, _, _, lab, tot, big in pr) and len({lab for _, _, _, lab, _, _ in pr}) == 6
P('pump-charge', ok4, 'the topological pump on the Fibonacci chain (89 sites, V = 1.5, the smooth family of Kraus that tends to the Fibonacci potential as beta grows): one cycle of the phason pumps, across each of the six widest gaps, a charge equal to minus its label,',
  sorted({(lab, int(round(tot))) for _, _, _, lab, tot, _ in pr}), 'as (label, charge), the same at beta = 2 and beta = 5, every step of the Berry phase below 0.05: the gap label of MF-131 is a Chern number')
# W5
m = 9
f = lambda t: (2 * t[0] * t[1] - t[2], t[0], t[1])
fm = lambda t: ((2 * t[0] * t[1] - t[2]) % m, t[0] % m, t[1] % m)
eq = all(tuple(c % m for c in f(t)) == fm(tuple(c % m for c in t)) for t in itertools.product(range(-12, 13), repeat=3))
a = (1, 1, 1); b = (1, 1, 10)
oa = [a]; ob = [b]
for _ in range(12): oa.append(f(oa[-1])); ob.append(f(ob[-1]))
P('mod9-equivariance', eq and all(t == a for t in oa) and max(abs(c) for c in ob[-1]) > 10 ** 6 and tuple(c % 9 for c in a) == tuple(c % 9 for c in b),
  'reduction modulo 9 commutes with the trace map on the 15,625 integer triples with entries -12 to 12, so every integer orbit carries a residue orbit of period dividing 24 (MF-148);',
  'the residue labels an orbit and does not decide its fate: (1, 1, 1) is a fixed point, and (1, 1, 10), of the same residue, escapes, past 10^%d after 12 steps' % (len(str(max(abs(c) for c in ob[-1]))) - 1))
# W6: one automorphism of the free group, two shadows
import random
rng = random.Random(7)
def rnd_sl2():
    while True:
        a, b, c = (F(rng.randint(-5, 5), rng.randint(1, 4)) for _ in range(3))
        if a != 0: return [[a, b], [c, (1 + b * c) / a]]
trm = lambda X: X[0][0] + X[1][1]
ok6 = True
for _ in range(50):
    X, Y = rnd_sl2(), rnd_sl2()
    x, y, z = trm(X), trm(Y), trm(mm(X, Y))
    Xs, Ys = mm(X, Y), X                                     # sigma: a -> ab, b -> a
    xs, ys, zs = trm(Xs), trm(Ys), trm(mm(Xs, Ys))
    ok6 = ok6 and (xs, ys, zs) == (z, x, x * z - y) and x * x + y * y + z * z - x * y * z == xs * xs + ys * ys + zs * zs - xs * ys * zs
ab = [[1, 1], [1, 0]]                                         # letter counts of sigma(a) = ab, sigma(b) = a
P('one-automorphism', ok6 and ab == [[sum(1 for c in 'ab' if c == 'a'), sum(1 for c in 'a' if c == 'a')], [sum(1 for c in 'ab' if c == 'b'), sum(1 for c in 'a' if c == 'b')]],
  'the substitution sigma: a -> ab, b -> a is one automorphism of the free group on two letters with two shadows: on letter counts, its abelianization, the matrix [[1,1],[1,0]], the law with coordinates exchanged;',
  'on SL2 characters, (tr X, tr Y, tr XY) -> (tr XY, tr X, tr X tr XY - tr Y), the trace map, keeping the Fricke cubic x^2 + y^2 + z^2 - xyz, exact on 50 random pairs of rational SL2 matrices: the incidence matrix and the transfer matrices are the same automorphism seen in two representations')
if __name__ == '__main__':
    a_ = sys.argv[1:]
    if a_ == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('WAVES SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a_ == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if len(a_) == 2 and a_[0] == '--pump':
        for beta, g, nf, lab, tot, big in pump(float(a_[1])): print('beta %.1f: gap width %.3f, states below %d, label %d, pumped charge %.6f' % (beta, g, nf, lab, tot))
        sys.exit(0)
    print(__doc__); sys.exit(2)
