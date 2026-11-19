#!/usr/bin/env python3
"""einstein.py -- M378 Relativistic Kinematics (Core Part 3.85): what the Lorentz action of A (M344) does, in Einstein's
own quantities, computed exactly.

  light     every Fibonacci state (F_n, F_n+1) becomes a light ray s s^T of energy F_2n+1 / 2, and its components form the
            Pythagorean triple (2 F_n F_n+1)^2 + (F_n-1 F_n+2)^2 = F_2n+1^2 (MF-59)
  matter    a unit rest mass boosted by A^n has energy L_2n / 2 (its gamma), speed sqrt5 F_2n / L_2n, and its mass kept,
            because L^2 - 5 F^2 = 4 (MF-60); one step is speed sqrt5/3, Doppler factor phi^2, rapidity 2 ln phi
  sky       the ratios F_n+1 / F_n converging to phi are relativistic aberration: repeated boosts draw every light ray toward
            the forward direction, the golden ray
  shear     B fixes the light ray e2 e2^T: a null rotation, an element of the photon's little group (MF-61)
  geometry  A is real, so it acts on 2+1 Minkowski space, whose unit mass shell is the hyperbolic plane; a hyperbolic
            element of GL2(Z) translates by 2 ln rho (rho its spectral radius), so least hyperbolic growth (Core L-558, P2)
            and least translation are one statement: A is the shortest glide reflection (2 ln phi) and A^2 (trace 3) the
            shortest closed geodesic of the modular surface (4 ln phi) (MF-62)
  orbit     the Fibonacci light rays are one Lorentz orbit: each Pythagorean triple is the boost of the one before; in
            coordinates X = [[t+x, y], [y, t-x]] the action is t' = (3t - x + 2y)/2, x' = (-t - x - 2y)/2, y' = t - x + y
  prime 3   modulo 3^k the same boost has finite order 8*3^(k-1): at an inert prime a boost closes into a cycle (MF-28)
  mass      the norm map s -> M_s M_s^T (M_s = a I + b A) intertwines the law with the Lorentz action and its interval is
            N(s)^2 = Q(s)^2/4: Omega42's invariant is the invariant mass; by Cassini every Fibonacci state has unit mass (MF-63)
  spin      both maps send s and -s to the same image (81 states to 37 matrices mod 9), and the image returns in half the
            period (cycle type 1, 2^4, 4^18, 12^54 against 24, 24, 24, 8, 1): the half-period negation of the law is the
            sign of a spinor, which a full turn reverses and two turns restore (MF-64)

    python3 tools/einstein.py            the tables
    python3 tools/einstein.py --selftest
Exact arithmetic (Fraction) where it can be; standard library only. The physical reading is CONDITIONAL on AP-SPACE.
"""
import math, sys
from fractions import Fraction as Fr

F = [0, 1]; L = [2, 1]
for _ in range(90):
    F.append(F[-1] + F[-2]); L.append(L[-1] + L[-2])
PHI = (1 + 5 ** .5) / 2
A = ((0, 1), (1, 1)); B = ((1, 0), (3, 1))


def mm(X, Y):
    return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)) for i in range(2))


def tr(X):
    return tuple(tuple(X[j][i] for j in range(2)) for i in range(2))


def event(X):
    """real symmetric [[t+z, x], [x, t-z]] -> (t, x, z)."""
    return Fr(X[0][0] + X[1][1], 2), Fr(X[0][1]), Fr(X[0][0] - X[1][1], 2)


def light(n):
    a, b = F[n], F[n + 1]
    return event(((a * a, a * b), (a * b, b * b)))


def matter(n):
    P = ((1, 0), (0, 1))
    for _ in range(n):
        P = mm(A, P)
    return event(mm(P, tr(P)))


def order_mod(m):
    P, n = tuple(tuple(x % m for x in r) for r in A), 1
    while P != ((1, 0), (0, 1)):
        P = tuple(tuple(x % m for x in r) for r in mm(P, A)); n += 1
    return n


def coords_ok():
    for t in range(-4, 5):
        for x in range(-4, 5):
            for y in range(-4, 5):
                Y = mm(mm(A, ((t + x, y), (y, t - x))), tr(A))
                if (Fr(Y[0][0] + Y[1][1], 2), Fr(Y[0][0] - Y[1][1], 2), Y[0][1]) != (Fr(3 * t - x + 2 * y, 2), Fr(-t - x - 2 * y, 2), t - x + y):
                    return False
    return True


def norm(a, b):
    return a * a + a * b - b * b


def norm_map(a, b, m=None):
    M = ((a, b), (b, a + b)); X = mm(M, tr(M))
    return tuple(tuple(x % m for x in r) for r in X) if m else X


def sym_cycle_type(m=9):
    from collections import Counter
    L = lambda v: (v[2] % m, (v[1] + v[2]) % m, (v[0] + 2 * v[1] + v[2]) % m)
    seen, ct = set(), Counter()
    for v in ((p, q, r) for p in range(m) for q in range(m) for r in range(m)):
        if v in seen:
            continue
        n, w = 0, v
        while True:
            seen.add(w); w = L(w); n += 1
            if w == v:
                break
        ct[n] += 1
    return dict(sorted(ct.items()))


def selftest():
    b = 5 ** .5 / 3
    cases = [
        ('light: (F_n, F_n+1) is a null ray of energy F_2n+1/2 with the Pythagorean triple, n < 40',
         all((lambda t, x, z: t * t - x * x - z * z == 0 and t == Fr(F[2 * n + 1], 2) and (2 * F[n] * F[n + 1]) ** 2 + (F[n - 1] * F[n + 2]) ** 2 == F[2 * n + 1] ** 2)(*light(n)) for n in range(1, 40))),
        ('matter: A^n boosts a unit rest mass to energy L_2n/2 with its mass kept, n < 30',
         all((lambda t, x, z: t == Fr(L[2 * n], 2) and t * t - x * x - z * z == 1)(*matter(n)) for n in range(1, 30))),
        ('matter: the speed after n steps is sqrt5 F_2n / L_2n (L^2 - 5F^2 = 4), n < 30',
         all(abs(math.sqrt(float(matter(n)[0]) ** 2 - 1) / float(matter(n)[0]) - 5 ** .5 * F[2 * n] / L[2 * n]) < 1e-12 for n in range(1, 30))),
        ('Einstein addition: sqrt5/3 with itself is 3 sqrt5/7', abs(2 * b / (1 + b * b) - 3 * 5 ** .5 / 7) < 1e-12),
        ('Doppler factor at sqrt5/3 is phi^2; rapidity arccosh(3/2) = 2 ln phi',
         abs(math.sqrt((1 + b) / (1 - b)) - PHI ** 2) < 1e-12 and abs(math.acosh(1.5) - 2 * math.log(PHI)) < 1e-12),
        ('sky: F_n+1/F_n converges to phi, the forward ray (error below 1e-11 at n = 29)', abs(F[30] / F[29] - PHI) < 1e-11),
        ('shear: B fixes the light ray e2 e2^T and has trace 2 (a null rotation)', mm(mm(B, ((0, 0), (0, 1))), tr(B)) == ((0, 0), (0, 1)) and B[0][0] + B[1][1] == 2),
        ('geometry: A^2 has trace 3 and translation length 2 arccosh(3/2) = 4 ln phi, the least for hyperbolic elements of SL2(Z)',
         mm(A, A)[0][0] + mm(A, A)[1][1] == 3 and abs(2 * math.acosh(1.5) - 4 * math.log(PHI)) < 1e-12),
        ('prime 3: the boost has order 8, 24, 72 modulo 3, 9, 27', [order_mod(3 ** k) for k in (1, 2, 3)] == [8, 24, 72]),
        ('glide: A (det -1, trace 1) translates by 2 arcsinh(1/2) = 2 ln phi, the least of any hyperbolic element of GL2(Z)',
         abs(2 * math.asinh(0.5) - 2 * math.log(PHI)) < 1e-12 and 2 * math.log(PHI) < 2 * math.log((3 + 5 ** .5) / 2)),
        ('orbit: the Fibonacci light rays form one Lorentz orbit, X_n+1 = A X_n A^T, n < 40',
         all(mm(mm(A, ((F[n] ** 2, F[n] * F[n + 1]), (F[n] * F[n + 1], F[n + 1] ** 2))), tr(A)) == ((F[n + 1] ** 2, F[n + 1] * F[n + 2]), (F[n + 1] * F[n + 2], F[n + 2] ** 2)) for n in range(40))),
        ('mass: the norm map has interval N(s)^2 and intertwines, X_As = A X_s A^T, for |a|, |b| <= 15',
         all((lambda X: X[0][0] * X[1][1] - X[0][1] * X[1][0])(norm_map(a, b)) == norm(a, b) ** 2 and norm_map(b, a + b) == mm(mm(A, norm_map(a, b)), tr(A)) for a in range(-15, 16) for b in range(-15, 16))),
        ('mass: Cassini -- every Fibonacci state has norm +-1, a unit mass, n < 60', all(abs(norm(F[n], F[n + 1])) == 1 for n in range(60))),
        ('spin: mod 9 the image of the 81 states has 37 points, and the action on symmetric matrices has cycle type 1, 2^4, 4^18, 12^54',
         len({norm_map(a, b, 9) for a in range(9) for b in range(9)}) == 37 and sym_cycle_type(9) == {1: 1, 2: 4, 4: 18, 12: 54}),
        ('coordinates: t\' = (3t - x + 2y)/2, x\' = (-t - x - 2y)/2, y\' = t - x + y for X = [[t+x, y], [y, t-x]] (F193)', coords_ok()),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('RELATIVISTIC KINEMATICS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    print('LIGHT -- the Fibonacci state (F_n, F_n+1) as a light ray (t, x, z), t = F_2n+1/2')
    for n in range(1, 9):
        t, x, z = light(n); print('  n=%-2d state (%d, %d)  ->  t=%s x=%s z=%s   triple %d^2 + %d^2 = %d^2' % (n, F[n], F[n + 1], t, x, z, 2 * F[n] * F[n + 1], F[n - 1] * F[n + 2], F[2 * n + 1]))
    print('MATTER -- a unit rest mass after n steps of A: gamma = L_2n/2, speed = sqrt5 F_2n/L_2n')
    for n in range(1, 7):
        t, x, z = matter(n); print('  n=%d  gamma=%s  speed=%.9f c  (sqrt5*%d/%d)' % (n, t, 5 ** .5 * F[2 * n] / L[2 * n], F[2 * n], L[2 * n]))
    print('ONE STEP -- speed sqrt5/3 = %.6f c, Doppler factor phi^2 = %.6f, rapidity 2 ln phi = %.6f' % (5 ** .5 / 3, PHI ** 2, 2 * math.log(PHI)))
    print('MODULAR SURFACE -- A^2 translates by 4 ln phi = %.6f, the shortest closed geodesic' % (4 * math.log(PHI)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
