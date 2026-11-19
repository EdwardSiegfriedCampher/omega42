#!/usr/bin/env python3
"""Evidence run 10 -- moduli supplied by physics: c mod 8 (Gauss-Milgram) and c mod 24 (framing). Standard library only."""
import cmath, math
from fractions import Fraction as Fr
phi = (1 + 5 ** 0.5) / 2

# K1: the Fibonacci theory from its fusion rule
# tau x tau = 1 + tau  =>  d^2 = 1 + d, positive root
d = (1 + math.sqrt(5)) / 2
print("K1 fusion tau x tau = 1 + tau forces the quantum dimension d with d^2 = d + 1: d = %.12f = phi: %s" % (d, abs(d - phi) < 1e-12))
D = math.sqrt(1 + d * d)
for sgn in (1, -1):
    theta = cmath.exp(sgn * 4j * math.pi / 5)
    gm = (1 + d * d * theta) / D
    c8 = (cmath.phase(gm) / (2 * math.pi) * 8) % 8
    print("K1 theta_tau = exp(%+d * 4 pi i / 5): |sum|/D = %.12f, exp(2 pi i c / 8) -> c = %.6f mod 8 (14/5 = 2.8, 26/5 = 5.2)" % (sgn, abs(gm), c8))
# the other spins for which d = phi and |Gauss sum| = 1 holds (consistency of a modular category)
ok = [k for k in range(1, 20) if abs(abs(1 + d * d * cmath.exp(2j * math.pi * k / 20)) / D - 1) < 1e-9]
print("K1 spins theta = exp(2 pi i k/20) with a unit-modulus Gauss sum: k = %s -> theta_tau = exp(+-4 pi i/5) only" % ok)

# K2: Sugawara central charges c = k dim / (k + h_dual) at level 1
alg = {'G2': (14, 4), 'F4': (52, 9), 'E8': (248, 30)}
c = {a: Fr(1 * dim, 1 + h) for a, (dim, h) in alg.items()}
print("K2 central charges at level 1: G2 %s, F4 %s, E8 %s | G2 + F4 = %s = E8: %s" % (c['G2'], c['F4'], c['E8'], c['G2'] + c['F4'], c['G2'] + c['F4'] == c['E8']))
print("K2 modulo 8: G2 %s, F4 %s, E8 %s -> E8_1 is invisible to the anyon data (trivial in the mod-8 layer)" % (c['G2'] % 8, c['F4'] % 8, c['E8'] % 8))

# K3: the mod-24 layer
for n in range(1, 7):
    cc = n * c['E8']
    ph = cc / 24 % 1
    print("K3 %d cop%s of E8_1: c = %s | c mod 8 = %s | framing phase exp(-2 pi i c/24) = exp(-2 pi i %s) | closes: %s"
          % (n, "y" if n == 1 else "ies", cc, cc % 8, ph, ph == 0))
print("K3 Z/24 = Z/8 x Z/3: E8_1 has c = 8 -> (0 mod 8, 2 mod 3): it has returned in the mod-8 layer and not in the mod-3 layer")
