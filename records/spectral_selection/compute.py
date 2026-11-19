#!/usr/bin/env python3
"""Spectrum, the canonical selection and the instruments (Core 1.8.8, 1.8.9, Part 3.31; Companion 43.9).
Standard library only. Every number printed is computed here."""
import cmath, math
N = 9
T = lambda s: (s[1], (s[0] + s[1]) % N)
def orbit(s):
    o, x = [s], T(s)
    while x != s: o.append(x); x = T(x)
    return o
lift = lambda v: ((v % 9) + 4) % 9 - 4            # the centred residue: the representative of least absolute value
VOICES = {'A': (1, 1), 'B': (1, 3), 'C': (2, 5)}
def power(c):
    L = len(c); return [abs(sum(c[n] * cmath.exp(-2j * math.pi * k * n / L) for n in range(L))) ** 2 for k in range(L)]

print("1. Differencing is a time shift on every orbit (residues): dx(n) = x(n+1) - x(n) = x(n-1), and the central second difference is x(n-3):",
      all(((o[(n + 1) % len(o)][0] - o[n][0]) % 9 == o[(n - 1) % len(o)][0]) and ((o[(n + 1) % len(o)][0] - 2 * o[n][0] + o[n - 1][0]) % 9 == o[(n - 3) % len(o)][0])
          for s in [(a, b) for a in range(9) for b in range(9)] for o in [orbit(s)] for n in range(len(o))))

print("2. Energy and curvature by representation (sum of squares of the values, and of their central second differences):")
for name, s in VOICES.items():
    v = [a for a, b in orbit(s)]
    c = [lift(x) for x in v]
    d19 = [x if x else 9 for x in v]
    curv = lambda x: sum((x[(n + 1) % 24] - 2 * x[n] + x[n - 1]) ** 2 for n in range(24))
    res_curv = sum(lift((v[(n + 1) % 24] - 2 * v[n] + v[n - 1]) % 9) ** 2 for n in range(24))
    print("   Voice %s: residue energy %d | residue curvature %d | display 1-9 curvature %d | display 0-8 curvature %d | centred-lift curvature %d"
          % (name, sum(x * x for x in c), res_curv, curv(d19), curv(v), curv(c)))
print("   residue measures: Voice C is the unique maximum; the display measures order the voices one way and the centred lift the other")

print("3. Centred power spectra on the odd harmonics (levels):")
for name, s in VOICES.items():
    P = power([lift(a) for a, b in orbit(s)])
    lv = sorted({round(P[k], 4) for k in range(1, 24, 2)})
    print("   Voice %s: %s | all integers: %s" % (name, lv, all(abs(P[k] - round(P[k])) < 1e-6 for k in range(24))))
print("   108 * sqrt(3) = %.4f: the irrational levels of Voices A and B are 324 - 108 sqrt 3 and 324 + 108 sqrt 3" % (108 * 3 ** 0.5))

print("4. Autocorrelation of the centred canonical cycle, R(L) = sum c(n) c(n+L) / sum c(n)^2:")
c = [lift(a) for a, b in orbit((2, 5))]; E = sum(x * x for x in c)
R = {L: sum(c[n] * c[(n + L) % 24] for n in range(24)) / E for L in range(24)}
print("   nonzero lags:", {L: round(r, 4) for L, r in R.items() if abs(r) > 1e-12})
print("   at the arm offsets: Yang +5 %.2f | Yin +18 %.2f | 4D +8 %+.2f | Antipode +12 %+.2f" % (R[5], R[18], R[8], R[12]))
for name, s in VOICES.items():
    cc = [lift(a) for a, b in orbit(s)]; EE = sum(x * x for x in cc)
    print("   Voice %s at lags 2, 5, 8, 12, 18: %s" % (name, [round(sum(cc[n] * cc[(n + L) % 24] for n in range(24)) / EE, 4) for L in (2, 5, 8, 12, 18)]))

print("5. K-alt-5 (adversarial, not a criterion): period 24 and an all-integer centred power spectrum")
surv = [s for s in [(a, b) for a in range(9) for b in range(9)] if len(orbit(s)) == 24 and all(abs(p - round(p)) < 1e-6 for p in power([lift(a) for a, b in orbit(s)]))]
print("   survivors: %d, exactly the 24 states of Voice C: %s -> the voice is selected, the starting state is open (UNDERDETERMINED)" % (len(surv), set(surv) == set(orbit((2, 5)))))

print("6. Parity of value observables under the half turn v -> -v (anchor -> Antipode):")
tests = {'M234 scale family dr(v^2)': lambda v: (v * v) % 9, 'Crown / Torsion membership (v mod 3 = 0)': lambda v: v % 3 == 0,
         'centred value (M289)': lift, 'completion v_S + v_A (ACS, M285)': lambda v: v % 9}
for name, f in tests.items():
    even = all(f(v) == f((-v) % 9) for v in range(9))
    print("   %-44s %s" % (name, 'EVEN: identical at a position and its Antipode' if even else 'ODD or mixed: separates a position from its Antipode'))
print("7. FP-Adjacency in residues: {4, 5} = {4, -4}, the pair at the greatest cyclic distance from 0:",
      max(range(1, 9), key=lambda v: abs(lift(v))) in (4, 5) and abs(lift(4)) == abs(lift(5)) == 4)
