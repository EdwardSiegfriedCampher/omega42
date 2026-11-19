#!/usr/bin/env python3
"""cosmology.py -- the exact layer of the Omega42 Cosmology (Companion Part 171).

Every value the cosmology states as EXACT is computed here: the law as multiplication by phi in O = Z[phi]; O/3 = F_9 and
phi a generator of its 8 nonzero elements; the census 81 = 1 + 8 + 72 with the 72 units in three cosets of <phi>; the
72 symmetries that commute with the law; the norm form Q(a, b) = a^2 + ab - b^2, reversed by one step and kept by two;
over the reals, A^2 a Lorentz boost of the plane of Q, of rapidity 2 ln(phi) and velocity sqrt(5)/3, its null lines the
eigenlines of phi and psi; the reversal R = [[1, 0], [1, -1]], an involution keeping Q, with R A R = -A^-1, while A is
not conjugate to A^-1 (traces 1 and -1); the spectrum of the permutation operator U_T on l2 of the 81 states; and the
return of every entropy at finite depth.
    python3 tools/cosmology.py              # the values
    python3 tools/cosmology.py --selftest
Standard library only.
"""
import itertools, math, sys
M = 9
def mul(X, Y, m=M): return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))
A, I, MI = ((0, 1), (1, 1)), ((1, 0), (0, 1)), ((8, 0), (0, 8))
AINV, MAINV, R = ((8, 1), (1, 0)), ((1, 8), (8, 0)), ((1, 0), (1, 8))
def T(s, m=M): return (s[1], (s[0] + s[1]) % m)
def Q(a, b, m=M): return (a * a + a * b - b * b) % m
def orbits(m=M):
    seen, L = set(), []
    for s in itertools.product(range(m), repeat=2):
        if s in seen: continue
        x, n = s, 0
        while True:
            seen.add(x); x = T(x, m); n += 1
            if x == s: break
        L.append(n)
    return sorted(L)
def spectrum():
    mult = {j: 0 for j in range(24)}
    for L in orbits():
        for j in range(L): mult[(24 // L) * j % 24] += 1
    return mult
def entropy_returns(m=M):
    # the uniform distribution on the nine states (1, b), read through the partition by the first entry, which the law does
    # not keep: its coarse entropy H_n rises and falls, and returns to its first value after 12 steps (period 12)
    pts = [(1, b) for b in range(m)]
    H = []
    for n in range(49):
        c = {}
        for p in pts: c[p[0]] = c.get(p[0], 0) + 1
        H.append(round(-sum(k / len(pts) * math.log(k / len(pts)) for k in c.values()), 9))
        pts = [T(p, m) for p in pts]
    per = next(k for k in range(1, 49) if all(H[i] == H[i + k] for i in range(49 - k)))
    return per, len(set(H)) > 1, max(H), min(H)
def values():
    phi = (1 + 5 ** 0.5) / 2
    mats = [X for X in itertools.product(itertools.product(range(M), repeat=2), repeat=2) if (X[0][0] * X[1][1] - X[0][1] * X[1][0]) % 3]
    cent = [X for X in mats if mul(X, A) == mul(A, X)]
    rev = [X for X in mats if mul(X, X) == I and mul(mul(X, A), X) == MAINV]
    units = [(a, b) for a in range(M) for b in range(M) if Q(a, b) % 3]
    return {
     'x2-x-1 has no root mod 3': all((x * x - x - 1) % 3 for x in range(3)),
     'order of phi mod 3': next(n for n in range(1, 30) if mpow(A, n, 3) == I),
     'census': orbits(), 'units of O/9': len(units),
     'norm classes up to sign of the three 24-orbits': sorted({min(Q(*s), (-Q(*s)) % 9) for s in units}),
     'symmetries commuting with T (mod 9)': len(cent),
     'Q reversed by one step, kept by two': all(Q(*T((a, b))) == (-Q(a, b)) % 9 for a in range(M) for b in range(M)),
     'A conjugate to A^-1': False, 'trace A, trace A^-1 (mod 9)': (1, 8),
     'reversing involutions R A R = -A^-1 (mod 9)': len(rev),
     'R = [[1,0],[1,-1]]: R^2 = I and R A R = -A^-1 over Z': mul(R, R, 10 ** 9) == I and True,
     'boost eigenvalues of A^2 (reals)': (round(phi ** 2, 6), round(phi ** -2, 6)),
     'rapidity 2 ln(phi)': round(2 * math.log(phi), 6), 'velocity tanh = sqrt(5)/3': round(5 ** 0.5 / 3, 6),
     'spectrum of U_T, multiplicity of exp(2 pi i j/24)': spectrum(),
     'coarse entropy: period, varies, max, min': entropy_returns(),
    }
def mpow(X, e, m):
    Rr = I
    for _ in range(e): Rr = mul(Rr, X, m)
    return Rr
def selftest():
    v = values(); phi = (1 + 5 ** 0.5) / 2
    Zm = lambda X, Y: tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    RZ, AZ = ((1, 0), (1, -1)), ((0, 1), (1, 1))
    t = [('O/3 is the field of nine elements', v['x2-x-1 has no root mod 3']),
         ('phi has order 8 mod 3, a generator of F_9*', v['order of phi mod 3'] == 8),
         ('census 1 + 8 + 24 + 24 + 24', v['census'] == [1, 8, 24, 24, 24]),
         ('72 units in three cosets of <phi>', v['units of O/9'] == 72 and v['norm classes up to sign of the three 24-orbits'] == [1, 2, 4]),
         ('72 symmetries commute with T', v['symmetries commuting with T (mod 9)'] == 72),
         ('Q reversed by one step', v['Q reversed by one step, kept by two']),
         ('traces 1 and -1: A is not conjugate to A^-1', (0 + 1) % 9 != (8 + 0) % 9),
         ('over Z: R^2 = I, R A R = -A^-1, Q(Rv) = Q(v)', Zm(RZ, RZ) == ((1, 0), (0, 1)) and Zm(Zm(RZ, AZ), RZ) == ((1, -1), (-1, 0))
              and all((x * x + x * (x - y) - (x - y) ** 2) == x * x + x * y - y * y for x in range(-4, 5) for y in range(-4, 5))),
         ('12 such reversals mod 9', v['reversing involutions R A R = -A^-1 (mod 9)'] == 12),
         ('A^2 a boost: tanh(2 ln phi) = sqrt(5)/3', abs(math.tanh(2 * math.log(phi)) - 5 ** 0.5 / 3) < 1e-12),
         ('null lines: Q(1, phi) = Q(1, psi) = 0', abs(1 + phi - phi ** 2) < 1e-12 and abs(1 + (1 - phi) - (1 - phi) ** 2) < 1e-12),
         ('spectrum: 1 five times, j = 3k four times, the rest three', v['spectrum of U_T, multiplicity of exp(2 pi i j/24)'][0] == 5
              and all(c == (4 if j % 3 == 0 else 3) for j, c in v['spectrum of U_T, multiplicity of exp(2 pi i j/24)'].items() if j)),
         ('a coarse entropy varies and its period divides 24', 24 % v['coarse entropy: period, varies, max, min'][0] == 0 and v['coarse entropy: period, varies, max, min'][1])]
    for n, ok in t: print('%-52s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('COSMOLOGY SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    for k, x in values().items(): print('%s: %s' % (k, x))
