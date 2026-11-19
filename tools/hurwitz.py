#!/usr/bin/env python3
"""hurwitz.py -- M380 The Forty-Two Reading (Core Part 3.87): what the new mathematics says about the number 42.

  triangle  the law acts on the hyperbolic plane (MF-62), whose discrete symmetry groups have triangles with angles
            pi/p, pi/q, pi/r and area pi(1 - 1/p - 1/q - 1/r); the largest sum of three unit fractions below 1 is
            1/2 + 1/3 + 1/7 = 41/42, so the (2, 3, 7) reflection triangle has the least area of any, pi/42; its rotation
            subgroup, the least cocompact Fuchsian group, has pi/21; A has determinant -1, so the law sits in the reflection
            setting, where pi/42 is the minimum (MF-67)
  record    its three angles are the record's three constants: CAS-YY = -1/2, the prime 3, Omega = 1/7; and
            1/2 + 1/3 + 1/7 + 1/42 = 1
  seven     modulo 7 the cusp of the modular group closes: the translation and the shear B have order 7, and <A, B>
            generates every matrix of determinant +-1, projectively PGL2(F7) of order 336 = 8 x 42, the full symmetry of
            the Klein quartic; its rotations, PSL2(F7) of order 168 = 4 x 42, reach the Hurwitz bound 84(g - 1) (MF-68)
  lift      the 7 is the law's own: A^8 = I + 3M with M = [[4, 7], [7, 11]], so F_8 = 21 = 3 x 7 and 42 = 2 F_pi(3) = 2 x 3 x 7,
            one factorization with the least triangle; the formula 2 F_pi(p) gives 4, 1974, 635622 at p = 2, 7, 13 (MF-69)
  generate  B^2 A^2 = [[1, 1], [0, 1]] modulo 7, so <A^2, B> = SL2(F7) and <A, B> = every determinant +-1 (F197); the same
            full group appears at every prime tested except 3, where B = I and <A, B> collapses to <A> of order 8: the
            generation is generic, the prime 3 is the exception that makes the shear a depth operator (MF-71)
  check     modulo 7 the order of A is 16, of the twin [[0,1],[1,7]] 2, of the Pell matrix 6: a second prime separates the
            impostors that every 3-adic statistic confused, and the handshake now carries it (MF-72); PGL2(F7) has no
            element of order 24 (its largest projective order is 8), so the 24 positions cannot be the 24 heptagons of
            the Klein quartic in any way the law respects (MF-72)
  frieze    the 42 triangulations of a heptagon are the 42 positive quiddity cycles of length 7, words in SL2(Z) whose product
            is -I -- the same -I as the law's half period (Conway and Coxeter) (MF-70)

    python3 tools/hurwitz.py            the reading
    python3 tools/hurwitz.py --selftest
Standard library only. The arithmetic is EXACT; reading the constants as angles is CDT-B.
"""
import sys
from fractions import Fraction as Fr


def mm(X, Y, m):
    return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))


def generate(gens, m):
    I = ((1, 0), (0, 1)); S = {I}; fr = [I]
    while fr:
        nf = []
        for g in fr:
            for h in gens:
                p = mm(g, h, m)
                if p not in S:
                    S.add(p); nf.append(p)
        fr = nf
    return S


def proj_order(X, m):
    n, Y = 1, X
    while Y not in (((1, 0), (0, 1)), ((m - 1, 0), (0, m - 1))):
        Y = mm(Y, X, m); n += 1
    return n


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def pisano(p):
    a, b, n = 0, 1, 0
    while True:
        a, b, n = b, (a + b) % p, n + 1
        if (a, b) == (0, 1):
            return n


def quiddity(n=7, top=6):
    from itertools import product
    c = 0
    for q in product(range(1, top), repeat=n):
        if sum(q) != 3 * n - 6:
            continue
        P = ((1, 0), (0, 1))
        for a in q:
            P = tuple(tuple(sum(P[i][k] * ((a, -1), (1, 0))[k][j] for k in range(2)) for j in range(2)) for i in range(2))
        c += P == ((-1, 0), (0, -1))
    return c


def order_mod(X, m):
    n, Y = 1, X
    while Y != ((1, 0), (0, 1)):
        Y = mm(Y, X, m); n += 1
    return n


def best_triangle(limit=60):
    return max((Fr(1, p) + Fr(1, q) + Fr(1, r), (p, q, r)) for p in range(2, limit) for q in range(p, limit) for r in range(q, limit)
               if Fr(1, p) + Fr(1, q) + Fr(1, r) < 1)


A = ((0, 1), (1, 1)); B = ((1, 0), (3, 1)); S7 = ((0, 6), (1, 0)); T7 = ((1, 1), (0, 1))


def selftest():
    G = generate([A, B], 7); PSL = generate([S7, T7], 7)
    cases = [
        ('triangle: the largest sum of three unit fractions below 1 is 1/2 + 1/3 + 1/7 = 41/42 (all p <= q <= r < 60)', best_triangle() == (Fr(41, 42), (2, 3, 7))),
        ('triangle: the (2, 3, 7) reflection triangle has area pi/42 and its rotation group pi/21; the modular (2, 3, infinity) area is pi/6', 1 - Fr(1, 2) - Fr(1, 3) - Fr(1, 7) == Fr(1, 42) and 1 - Fr(1, 2) - Fr(1, 3) == Fr(1, 6)),
        ('record: 1/2 + 1/3 + 1/7 + 1/42 = 1', Fr(1, 2) + Fr(1, 3) + Fr(1, 7) + Fr(1, 42) == 1),
        ('seven: the translation and the shear B have order 7 modulo 7; S and ST have orders 2 and 3', [proj_order(x, 7) for x in (T7, B, S7, mm(S7, T7, 7))] == [7, 7, 2, 3]),
        ('seven: PSL2(F7) has order 168 = 4 x 42 = 84(g - 1) at g = 3', len(PSL) // 2 == 168 == 84 * 2),
        ('seven: <A, B> mod 7 is every matrix of determinant +-1, projectively of order 336 = 8 x 42', len(G) == 672 and {(g[0][0] * g[1][1] - g[0][1] * g[1][0]) % 7 for g in G} == {1, 6}),
        ('lift: A^8 = I + 3M with M = [[4, 7], [7, 11]]; F_8 = 21 = 3 x 7; 2 F_pi(3) = 42 = 2 x 3 x 7',
         (fib(7), fib(8), fib(9)) == (13, 21, 34) and ((13 - 1) // 3, 21 // 3, (34 - 1) // 3) == (4, 7, 11) and 2 * fib(pisano(3)) == 42 == 2 * 3 * 7),
        ('lift: 2 F_pi(p) is not special in general -- 4, 1974, 635622 at p = 2, 7, 13', [2 * fib(pisano(p)) for p in (2, 7, 13)] == [4, 1974, 635622]),
        ('frieze: the positive quiddity cycles of length 7 with product -I number 42, the Catalan number C_5', quiddity() == 42 == 252 // 6),
        ('generate: B^2 A^2 = [[1, 1], [0, 1]] mod 7 and <A^2, B> = SL2(F7), of order 336', mm(mm(B, B, 7), mm(A, A, 7), 7) == ((1, 1), (0, 1)) and len(generate([mm(A, A, 7), B], 7)) == 336),
        ('generate: <A, B> is every determinant +-1 at p = 2, 5, 7, 11, 13 and collapses to order 8 at p = 3',
         all(len(generate([A, B], q)) == (6 if q == 2 else 2 * q * (q * q - 1)) for q in (2, 5, 7, 11, 13)) and len(generate([A, B], 3)) == 8),
        ('check: modulo 7 the orders of A, the twin and the Pell matrix are 16, 2 and 6', [order_mod(M, 7) for M in (A, ((0, 1), (1, 7)), ((0, 1), (1, 2)))] == [16, 2, 6]),
        ('check: the largest projective order in PGL2(F7) is 8, so no element cycles 24 faces', max(proj_order(g, 7) for g in generate([A, B], 7)) == 8),
        ('seven: 7 is inert like 3 (7 = 2 mod 5); A has projective order 8 modulo 7 and 4 modulo 3', proj_order(A, 7) == 8 and proj_order(A, 3) == 4 and 7 % 5 == 2),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('FORTY-TWO READING SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    s, t = best_triangle()
    print('THE LEAST HYPERBOLIC TRIANGLE: angles pi/%d, pi/%d, pi/%d; 1/2 + 1/3 + 1/7 = %s; area pi/42' % (t + (s,)))
    print('THE RECORD: CAS-YY = -1/2, the prime 3, Omega = 1/7 -- and 1/2 + 1/3 + 1/7 + 1/42 = 1')
    print('MODULO 7: |<A, B>| = %d, projectively 336 = 8 x 42; PSL2(F7) = 168 = 4 x 42 = 84 x 2' % len(generate([A, B], 7)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
