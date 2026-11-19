#!/usr/bin/env python3
"""optics.py -- the law in optics: light through a Fibonacci dielectric multilayer (Companion Part 224).

A stack of layers A and B in the Fibonacci order S_(k+1) = S_k S_(k-1) carries light by the product of the layers'
transfer matrices M = [[cos d, (i/n) sin d], [i n sin d, cos d]], d the optical phase of a layer, n its index;
in air the transmittance is T = 4 / |m11 + m12 + m21 + m22|^2.

  O1 quarter-wave-cycle   at the quarter-wave frequency (d = pi/2 in both layers) the transmittance of the stacks is
                          periodic in the generation with period six, exact in Gaussian rationals, for two pairs of indices
  O2 optical-invariant    the half-traces of the stacks obey the trace map, and its Fricke-Vogt invariant is
                          I = (1/4)(nA/nB - nB/nA)^2 sin^2 dA sin^2 dB, exact at the quarter wave and at two Pythagorean phases
  O3 localization         at a frequency inside a gap the transmittance of the stack of 1597 layers falls below 10^-12,
                          while at the quarter wave it returns to its six values: the light is localized or critical
  O4 period-24-mod-9      the trace map f(x, y, z) = (2xy - z, x, y) is a bijection of the 729 triples modulo 9 with
                          orbits of lengths 1, 2, 3, 4, 6, 8, 12 and 24, f^24 = 1, and it keeps the Fricke-Vogt cubic
                          modulo 9: the quasicrystal written on Omega42's states has the period of the law

    python3 tools/optics.py --selftest
    python3 tools/optics.py --stack nA nB k      the quarter-wave transmittance of the stacks up to generation k
Standard library only; exact (Fraction, Gaussian rationals) for O1, O2 and O4, floating point for O3.
"""
import sys, math, cmath
from fractions import Fraction as F
from collections import Counter
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
class G:
    """a Gaussian rational a + bi"""
    __slots__ = ('a', 'b')
    def __init__(s, a, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): return G(s.a + o.a, s.b + o.b)
    def __mul__(s, o): return G(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def n2(s): return s.a * s.a + s.b * s.b
    def __eq__(s, o): return s.a == o.a and s.b == o.b
def mm(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
def qw_layer(n): return [[G(0), G(0, F(1) / n)], [G(0, n), G(0)]]          # d = pi/2: cos 0, sin 1
def trans(M): s = M[0][0] + M[0][1] + M[1][0] + M[1][1]; return F(4) / s.n2()
def stacks(LA, LB, k, mul=mm):
    S = [LB, LA]                                                            # S_0 = B, S_1 = A
    while len(S) < k + 1: S.append(mul(S[-1], S[-2]))
    return S
# O1
ok1 = True; shown = []
for nA, nB in ((F(2), F(3, 2)), (F(23, 10), F(146, 100))):
    T = [trans(m) for m in stacks(qw_layer(nA), qw_layer(nB), 24)]
    ok1 = ok1 and all(T[k] == T[k + 6] for k in range(len(T) - 6)) and len(set(T[:6])) >= 4
    shown.append((str(nA), str(nB), [str(t) for t in T[:6]]))
P('quarter-wave-cycle', ok1, 'at the quarter-wave frequency the transmittance T_k of the Fibonacci stacks repeats with period six in the generation k, exact for k = 0 to 24:', shown[0],
  '(indices 2 and 3/2) and the same for the indices 2.3 and 1.46 of TiO2 and SiO2: the six-cycle of the trace map (MF-130) seen in light')
# O2: exact half-traces at phases with rational cosine and sine: the quarter wave and Pythagorean phases
def layer(n, c, s): return [[G(c), G(0, s / n)], [G(0, n * s), G(c)]]
ok2 = True; vals = []
for (cA, sA), (cB, sB) in (((F(0), F(1)), (F(0), F(1))), ((F(3, 5), F(4, 5)), (F(5, 13), F(12, 13))), ((F(8, 17), F(15, 17)), (F(0), F(1)))):   # Pythagorean phases: exact cos and sin
    for nA, nB in ((F(2), F(3, 2)), (F(5, 2), F(4, 3))):
        S = stacks(layer(nA, cA, sA), layer(nB, cB, sB), 10)
        x = [(m[0][0] + m[1][1]) for m in S]
        assert all(v.b == 0 for v in x)
        x = [v.a / 2 for v in x]
        for k in range(2, 10): ok2 = ok2 and x[k + 1] == 2 * x[k] * x[k - 1] - x[k - 2]
        I = [x[k + 1] ** 2 + x[k] ** 2 + x[k - 1] ** 2 - 2 * x[k + 1] * x[k] * x[k - 1] - 1 for k in range(1, 10)]
        want = (nA / nB - nB / nA) ** 2 * sA ** 2 * sB ** 2 / 4
        ok2 = ok2 and all(i == want for i in I)
        vals.append(str(want))
P('optical-invariant', ok2, 'the half-traces of the stacks obey the trace map and keep the Fricke-Vogt invariant I = (1/4)(nA/nB - nB/nA)^2 sin^2 dA sin^2 dB, exact for three pairs of phases (the quarter wave and two Pythagorean phases) and two pairs of indices:', vals,
  '| the index contrast and the phases set the surface on which the light\'s trace orbit moves')
# O3
def stack_float(nA, nB, dA, dB, k):
    def lay(n, d): return [[complex(math.cos(d)), 1j * math.sin(d) / n], [1j * n * math.sin(d), complex(math.cos(d))]]
    def m2(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
    S = [lay(nB, dB), lay(nA, dA)]
    while len(S) < k + 1: S.append(m2(S[-1], S[-2]))
    return [4 / abs(m[0][0] + m[0][1] + m[1][0] + m[1][1]) ** 2 for m in S]
nA, nB = 2.3, 1.46
# a gap frequency: search the phase w (dA = dB = w) where T at generation 16 (1597 layers) is smallest, between 0.3 and 0.45 of pi
cands = [(stack_float(nA, nB, w * math.pi, w * math.pi, 16)[16], w) for w in [0.30 + 0.0025 * j for j in range(61)]]
Tmin, wmin = min(cands)
Tq = stack_float(nA, nB, math.pi / 2, math.pi / 2, 16)
ok3 = Tmin < 1e-12 and abs(Tq[16] - Tq[10]) < 1e-9 and Tq[16] > 0.2
P('localization', ok3, 'through a TiO2 / SiO2 Fibonacci stack of 1597 layers (generation 16): at the phase %.4f pi, in a gap, the transmittance is %.2g, below 10^-12, the light localized;' % (wmin, Tmin),
  'at the quarter wave it is %.6f, the value six generations earlier: the light at the center of the spectrum is critical, carried by the six-cycle' % Tq[16])
# O4
m = 9
f = lambda t: ((2 * t[0] * t[1] - t[2]) % m, t[0], t[1])
S9 = [(a, b, c) for a in range(m) for b in range(m) for c in range(m)]
seen = set(); cyc = Counter()
for t in S9:
    if t in seen: continue
    n = 0; u = t
    while u not in seen: seen.add(u); u = f(u); n += 1
    cyc[n] += 1
Icub = lambda t: (t[0] ** 2 + t[1] ** 2 + t[2] ** 2 - 2 * t[0] * t[1] * t[2] - 1) % m
def fpow(t, n):
    for _ in range(n): t = f(t)
    return t
ok4 = len({f(t) for t in S9}) == 729 and sorted(cyc) == [1, 2, 3, 4, 6, 8, 12, 24] and all(fpow(t, 24) == t for t in S9) and all(Icub(f(t)) == Icub(t) for t in S9)
P('period-24-mod-9', ok4, 'the trace map f(x, y, z) = (2xy - z, x, y) is a bijection of the 729 triples modulo 9; its orbits:', ', '.join('%d of length %d' % (cyc[k], k) for k in sorted(cyc)),
  '; f^24 = 1 and the Fricke-Vogt cubic is kept modulo 9: the quasicrystal\'s dynamics on Omega42\'s modulus has the period 24 of the law')
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('OPTICS SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if len(a) == 4 and a[0] == '--stack':
        for k, t in enumerate(trans(m) for m in stacks(qw_layer(F(a[1])), qw_layer(F(a[2])), int(a[3]))): print('generation %d: T = %s = %.6f' % (k, t, float(t)))
        sys.exit(0)
    print(__doc__); sys.exit(2)
