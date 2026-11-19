#!/usr/bin/env python3
"""fibonacci_hamiltonian.py -- the law in the physics of quasicrystals: the Fibonacci Hamiltonian, its trace map,
the Fricke-Vogt invariant and the gap labels in the law's ring Z[phi] (Companion Part 222).

  H1 fib-substitution    the substitution a -> ab, b -> a has matrix [[1,1],[1,0]], the law with coordinates exchanged; word lengths F_k
  H2 trace-map           transfer matrices of the Fibonacci Hamiltonian obey M_(k+1) = M_(k-1) M_k; half-traces x_(k+1) = 2 x_k x_(k-1) - x_(k-2)
  H3 fricke-vogt         I = x_(k+1)^2 + x_k^2 + x_(k-1)^2 - 2 x_(k+1) x_k x_(k-1) - 1 = V^2/4 at every step, for every energy (exact)
  H4 six-cycle           the trace map f(x, y, z) = (2xy - z, x, y) returns every triple with two zero coordinates after six steps (exact)
  H5 gap-labels          on the periodic approximant of length 377, the integrated density of states in each of the widest gaps
                         equals frac(n / phi) for an integer n: the gap labels lie in Z + Z phi, the law's ring (numerical)
  H6 cantor-scaling      the measure of the approximant spectra shrinks with the length; the ratio across three steps of the
                         law tends to a constant (numerical)
  H7 escape              Suto's criterion: half-traces escape for an energy in a gap and stay bounded in the bands (numerical)

    python3 tools/fibonacci_hamiltonian.py --selftest
    python3 tools/fibonacci_hamiltonian.py --gaps V L    the widest gaps and their labels on the approximant of length L
Standard library and numpy; exact (Fraction) for H1 to H4, floating point for H5 and H6.
"""
import sys, math
from fractions import Fraction as F
PHI = (1 + 5 ** .5) / 2
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def word(k):
    w = 'a'
    for _ in range(k): w = ''.join('ab' if c == 'a' else 'a' for c in w)
    return w
# H1
M = [[sum(1 for c in 'ab' if c == x) if y == 'a' else sum(1 for c in 'a' if c == x) for y in 'ab'] for x in 'ab']
lens = [len(word(k)) for k in range(12)]
P('fib-substitution', M == [[1, 1], [1, 0]] and lens == [fib(k + 2) for k in range(12)] and all(word(k + 1) == word(k) + word(k - 1) for k in range(1, 10)),
  'the substitution a -> ab, b -> a has matrix', M, '= S A S with S the coordinate exchange; the word lengths are', lens[:8], '..., F_(k+2), and w_(k+1) = w_k w_(k-1)')
# H2, H3: transfer matrices T(v) = [[E - v, -1], [1, 0]], on-site potential v = V on a, 0 on b
def mm(X, Y): return [[X[0][0] * Y[0][0] + X[0][1] * Y[1][0], X[0][0] * Y[0][1] + X[0][1] * Y[1][1]], [X[1][0] * Y[0][0] + X[1][1] * Y[1][0], X[1][0] * Y[0][1] + X[1][1] * Y[1][1]]]
def transfer(w, E, V):
    R = [[F(1), F(0)], [F(0), F(1)]]
    for c in w: R = mm([[E - (V if c == 'a' else 0), F(-1)], [F(1), F(0)]], R)
    return R
ok2 = ok3 = True; inv = []
for E, V in ((F(1, 3), F(1)), (F(-2, 5), F(3, 2)), (F(0), F(2)), (F(7, 4), F(1, 2))):
    Ms = [transfer(word(k), E, V) for k in range(9)]
    for k in range(1, 8): ok2 = ok2 and Ms[k + 1] == mm(Ms[k - 1], Ms[k])
    x = [(m[0][0] + m[1][1]) / 2 for m in Ms]
    xm1 = E / 2   # x_(-1) = E/2 (the free transfer matrix), the start of the map
    xs = [xm1] + x
    for k in range(2, 9): ok2 = ok2 and xs[k + 1] == 2 * xs[k] * xs[k - 1] - xs[k - 2]
    I = [xs[k + 1] ** 2 + xs[k] ** 2 + xs[k - 1] ** 2 - 2 * xs[k + 1] * xs[k] * xs[k - 1] - 1 for k in range(1, 9)]
    ok3 = ok3 and all(i == V * V / 4 for i in I); inv.append((str(E), str(V), str(I[0])))
P('trace-map', ok2, 'for four exact energies and potentials, the transfer matrices of the words obey M_(k+1) = M_(k-1) M_k, the law of the words carried to SL2,',
  'and their half-traces obey x_(k+1) = 2 x_k x_(k-1) - x_(k-2), the trace map of Kohmoto, Kadanoff and Tang')
P('fricke-vogt', ok3, 'the Fricke-Vogt invariant I = x_(k+1)^2 + x_k^2 + x_(k-1)^2 - 2 x_(k+1) x_k x_(k-1) - 1 equals V^2/4 at every step:', inv,
  '| the trace map keeps a cubic as the law keeps Q')
# H4: the six-cycle of the trace map and Suto's escape criterion
f = lambda t: (2 * t[0] * t[1] - t[2], t[0], t[1])
ok4 = True
for a_ in (F(1), F(5, 2), F(-3, 7)):
    t = (F(0), F(0), a_); orbit = [t]
    for _ in range(6): t = f(t); orbit.append(t)
    ok4 = ok4 and orbit[6] == orbit[0] and len(set(orbit[:6])) == 6
def half_traces(E, V, K):
    xs = [1.0, E / 2, (E - V) / 2]   # x_(-1) = 1, x_0 = E/2 (word b), x_1 = (E - V)/2 (word a)
    while len(xs) < K and abs(xs[-1]) < 1e12: xs.append(2 * xs[-1] * xs[-2] - xs[-3])
    return xs
P('six-cycle', ok4, 'the trace map f(x, y, z) = (2xy - z, x, y) returns every triple with two zero coordinates after exactly six steps (a = 1, 5/2, -3/7), its orbit (0, 0, a) -> (-a, 0, 0) -> (0, -a, 0) -> (0, 0, -a) -> (a, 0, 0) -> (0, a, 0) -> (0, 0, a);',
  'f is the law of the words acting on the character variety of SL2, with the Fricke-Vogt cubic as its invariant')
# H5, H6: numerical
def spectrum(L, V):
    import numpy as np
    w = word(40)[:L] if L > len(word(14)) else None
    k = 1
    while len(word(k)) < L: k += 1
    w = word(k); assert len(w) == L
    pot = np.array([V if c == 'a' else 0.0 for c in w])
    bands = []
    for theta in (0.0, math.pi):   # periodic and antiperiodic boundary: the band edges of the approximant
        H = np.diag(pot) - np.eye(L, k=1) - np.eye(L, k=-1)
        H[0, L - 1] = H[L - 1, 0] = -math.cos(theta)
        bands.append(np.sort(np.linalg.eigvalsh(H)))
    lo = np.minimum(bands[0], bands[1]); hi = np.maximum(bands[0], bands[1])
    return lo, hi
def gaps(L, V, top=10):
    lo, hi = spectrum(L, V)
    g = [(lo[i + 1] - hi[i], (i + 1) / L, hi[i], lo[i + 1]) for i in range(L - 1) if lo[i + 1] > hi[i]]
    g.sort(reverse=True)
    out = []
    for width, ids, a, b in g[:top]:
        n = min(range(-60, 61), key=lambda n: abs(((n / PHI - ids + 0.5) % 1) - 0.5))
        out.append((round(float(width), 4), round(float(ids), 6), n, abs(((n / PHI - ids + 0.5) % 1) - 0.5)))
    return out, sum(hi - lo)
gl, meas377 = gaps(377, 1.0)
ok5 = all(err < 1.5 / 377 and abs(n) <= 12 for _, _, n, err in gl)
P('gap-labels', ok5, 'on the approximant of length 377 with V = 1, each of the 10 widest gaps has integrated density of states within 1.5/377 of frac(n/phi), labels n =',
  [n for _, _, n, _ in gl], '| the gap labels lie in Z + Z phi, the ring the law multiplies')
ms = [gaps(L, 1.0, 1)[1] for L in (34, 144, 610)]
rat = [ms[i + 1] / ms[i] for i in range(2)]
P('cantor-scaling', ms[0] > ms[1] > ms[2] and abs(rat[0] - rat[1]) < 0.1 * rat[0],
  'the total width of the approximant spectra at V = 1 for lengths 34, 144, 610:', [round(float(m), 5) for m in ms], '| ratio across three steps of the law:', [round(float(r), 4) for r in rat],
  '-- the spectrum is a Cantor set of measure zero (Suto), shrinking by a near-constant factor for each power A^3')
lo, hi = spectrum(610, 1.0)
import numpy as np
g = max((lo[i + 1] - hi[i], (hi[i] + lo[i + 1]) / 2) for i in range(609))
esc_gap = max(abs(x) for x in half_traces(g[1], 1.0, 22))
inside = [ (lo[i] + hi[i]) / 2 for i in range(0, 610, 61)]
esc_in = max(max(abs(x) for x in half_traces(E, 1.0, 16)) for E in inside)
P('escape', esc_gap > 1e9 and esc_in < 10, 'Suto\'s criterion seen on the law: for an energy in the widest gap the half-traces escape, max |x_k| passes %.3g by k = 20; for ten energies in the bands of the approximant of length 610 they stay below %.3g through k = 14 (word length 610)' % (esc_gap, esc_in))
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('FIBONACCI HAMILTONIAN SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if len(a) == 3 and a[0] == '--gaps':
        for w, ids, n, err in gaps(int(a[2]), float(a[1]))[0]: print('gap width %.4f  IDS %.6f  label n = %d  (|IDS - frac(n/phi)| = %.2e)' % (w, ids, n, err))
        sys.exit(0)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    print(__doc__); sys.exit(2)
