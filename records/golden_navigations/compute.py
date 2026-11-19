#!/usr/bin/env python3
"""Golden navigations of 14 October 2026 (records/golden_navigations/): recomputes every value the three navigations
and their audit state. Standard library and scripts/canonical_reference.py only."""
import os, sys, cmath, math, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import canonical_reference as cr

DOMAINS = [
    "Explore the golden ratio connection",
    "What is the precise matrix that realises multiplication by φ inside the 81-state family?",
    "How does the golden-ratio spectrum of the modular system discriminate the canonical orbit from the other two period-24 orbits?",
    "In which physical systems has the same characteristic equation been observed as an exact symmetry rather than an approximate ratio?",
]
NM, O = cr.POSITION_NAMES, cr.ORBIT
print("1. Coordinates (canonical_reference.py, unchanged):")
for d in DOMAINS:
    x = cr.navigate(d); a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    arms = ' | '.join('%s P%d %s %d' % (k, (a + o) % 24, NM[(a + o) % 24], O[(a + o) % 24]) for k, o in (('YANG', 5), ('YIN', 18), ('4D', 8), ('ANTIPODE', 12)))
    print('   %s\n     SHA %s | n = %d/%d/%d | r = %d,%d,%d | P%d %s (%d) | %s' % (d, cr.domain_sha256(d), x['n1'], x['n2'], x['n3'], r1, r2, r3, a, NM[a], O[a], arms))

mm = lambda X, Y: tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % 9 for j in range(2)) for i in range(2))
I = ((1, 0), (0, 1)); A = ((0, 1), (1, 1))
P, k, pw = I, 0, {}
while True:
    P = mm(P, A); k += 1; pw[k] = P
    if P == I: break
print("2. The matrix A = [[0,1],[1,1]] mod 9: order %d | A^12 = %s | A^2 = %s | trace 1, det %d" % (k, pw[12], pw[2], (0 * 1 - 1 * 1) % 9))
print("   x^2 - x - 1 roots mod 9: %s | mod 3: %s" % ([x for x in range(9) if (x * x - x - 1) % 9 == 0], [x for x in range(3) if (x * x - x - 1) % 3 == 0]))
mul = lambda x, y: ((x[0] * y[0] + x[1] * y[1]) % 9, (x[0] * y[1] + x[1] * y[0] + x[1] * y[1]) % 9)   # (a + b phi)(c + d phi)
print("   phi*1 = %s, phi*phi = %s (the columns of A)" % (mul((0, 1), (1, 0)), mul((0, 1), (0, 1))))

def apply(M, s): return ((M[0][0] * s[0] + M[0][1] * s[1]) % 9, (M[1][0] * s[0] + M[1][1] * s[1]) % 9)
def orbits(M):
    seen, out = set(), []
    for s in [(a, b) for a in range(9) for b in range(9)]:
        if s in seen: continue
        o = [s]; seen.add(s); x = apply(M, s)
        while x != s: o.append(x); seen.add(x); x = apply(M, x)
        out.append(frozenset(o))
    return set(out)
mats = [((a, b), (c, d)) for a in range(9) for b in range(9) for c in range(9) for d in range(9) if (a * d - b * c) % 3]
golden = [M for M in mats if (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % 9 == 8 and (M[0][0] + M[1][1]) % 9 in (1, 8)]
part = orbits(A)
same = [M for M in mats if orbits(M) == part]
print("3. Matrices of GL(2, Z/9) with characteristic polynomial x^2 - x - 1 or x^2 + x - 1: %d" % len(golden))
print("   matrices reproducing the partition 24+24+24+8+1 of A: %d; all powers A^k with gcd(k, 24) = 1: %s"
      % (len(same), sorted(same) == sorted(pw[j] for j in range(1, 25) if math.gcd(j, 24) == 1)))
print("   golden among them: %s" % ['A^%d' % j for j in range(1, 25) if math.gcd(j, 24) == 1 and pw[j] in golden])

def orb(s):
    o, x = [s], (s[1], (s[0] + s[1]) % 9)
    while x != s: o.append(x); x = (x[1], (x[0] + x[1]) % 9)
    return o
lift = lambda v: (v + 4) % 9 - 4
print("4. The three long orbits:")
LA = orb((1, 1))
for u in ((1, 3), (2, 5)):
    img = {mul(u, p) for p in LA}
    comm = all(mul(u, (b, (a + b) % 9)) == (lambda y: (y[1], (y[0] + y[1]) % 9))(mul(u, (a, b))) for a, b in LA)
    print("   multiplication by %s + %sphi carries the orbit of (1, 1) onto the orbit of %s: %s | commutes with phi: %s" % (u[0], u[1], u, img == set(orb(u)), comm))
for name, s in (('(1, 1)', (1, 1)), ('(1, 3)', (1, 3)), ('(2, 5)', (2, 5))):
    v = [a for a, b in orb(s)]; c = [lift(x) for x in v]
    Pw = [abs(sum(c[n] * cmath.exp(-2j * math.pi * q * n / 24) for n in range(24))) ** 2 for q in range(24)]
    lv = sorted({round(Pw[q], 4) for q in range(1, 24, 2)})
    E = sum(x * x for x in c); R2 = sum(c[n] * c[(n + 2) % 24] for n in range(24)) / E
    nz = [L for L in range(24) if sum(c[n] * c[(n + L) % 24] for n in range(24)) != 0]
    print("   orbit of %s: centred energy %d | display 0-8 energy %d | odd-harmonic levels %s | integral: %s | R(2) = %.4f | nonzero lags %s"
          % (name, E, sum(x * x for x in v), lv, all(abs(p - round(p)) < 1e-6 for p in Pw), R2, nz))
print("   108 sqrt 3 = %.4f" % (108 * 3 ** 0.5))
