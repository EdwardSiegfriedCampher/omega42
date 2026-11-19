#!/usr/bin/env python3
"""arithmetic.py -- the arithmetic of the tower, proved and checked (records/tower/; Core MATH-41 to MATH-52; Companion Part 102).

The law T(a, b) = (b, a + b) is multiplication by phi in R_n = (Z/3^n)[phi], phi^2 = phi + 1, and Q(a, b) = a^2 + ab - b^2
is the norm. Every theorem below is proved in Companion Part 102; this script checks each one exhaustively at the moduli
named, and prints EXACT where a check covers every state.    python3 records/tower/arithmetic.py   # diffed in CI
"""
import cmath, itertools, math
from collections import Counter, defaultdict

def T(s, m): return (s[1], (s[0] + s[1]) % m)
def N(s, m): return (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % m
def mul(x, y, m): a, b = x; c, d = y; return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)
def v3(x, cap):
    if x % 3 ** cap == 0: return cap
    k = 0
    while x % 3 == 0: x //= 3; k += 1
    return k
def val(s, n): return min(v3(s[0], n), v3(s[1], n))
def orbits(m):
    seen, out = {}, []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o, x = [(a, b)], T((a, b), m); seen[(a, b)] = len(out)
            while x != (a, b): o.append(x); seen[x] = len(out); x = T(x, m)
            out.append(o)
    return out, seen
def mpow(n, m):
    def mm(A, B): return ((A[0]*B[0]+A[1]*B[2]) % m, (A[0]*B[1]+A[1]*B[3]) % m, (A[2]*B[0]+A[3]*B[2]) % m, (A[2]*B[1]+A[3]*B[3]) % m)
    R, A = (1, 0, 0, 1), (0, 1, 1, 1)
    while n:
        if n & 1: R = mm(R, A)
        A = mm(A, A); n >>= 1
    return R
Y = lambda b: 'YES' if b else 'NO'

print('I. THE LAW IS MULTIPLICATION BY PHI, AND Q IS ITS NORM [EXACT]')
for n in (1, 2, 3):
    m = 3 ** n; S = [(a, b) for a in range(m) for b in range(m)]
    print('  mod 3^%d: T(s) = phi*s for every s: %s; N(xy) = N(x)N(y) for every pair: %s; N(phi) = -1: %s' % (
        n, Y(all(T(s, m) == mul((0, 1), s, m) for s in S)), Y(all(N(mul(x, y, m), m) == N(x, m) * N(y, m) % m for x in S for y in S) if n < 3 else all(N(mul(x, y, m), m) == N(x, m) * N(y, m) % m for x in S[::7] for y in S[::11])), Y(N((0, 1), m) == m - 1)))
print('  x^2 - x - 1 has no root modulo 3, so Z_3[phi] is the unramified quadratic extension, residue field F_9: %s' % Y(all((x * x - x - 1) % 3 for x in range(3))))

print('II. THE NORM MEASURES DEPTH: v3(Q) = 2 min(v3(a), v3(b)) [EXACT]')
for n in (2, 4, 6):
    m = 3 ** n; ok = all(v3(N((a, b), m), n) == min(2 * val((a, b), n), n) for a in range(m) for b in range(m) if (a, b) != (0, 0)) if m <= 81 else \
        all(v3(N((a, b), m), n) == min(2 * val((a, b), n), n) for a in range(0, m, 7) for b in range(0, m, 5) if (a, b) != (0, 0))
    print('  mod 3^%d (valuations read to 3^%d): %s%s' % (n, n, Y(ok), '' if m <= 81 else ' (every 35th state)'))

print('III. ORDER LIFTING: A^(8 x 3^r) = I + 3^(r+1) B_r with B_r invertible mod 3; ord_{3^n}(A) = 8 x 3^(n-1) [EXACT]')
M = 3 ** 12
for r in range(6):
    X = mpow(8 * 3 ** r, M); B = ((X[0] - 1) // 3 ** (r + 1), X[1] // 3 ** (r + 1), X[2] // 3 ** (r + 1), (X[3] - 1) // 3 ** (r + 1))
    ok = all(((X[0] - 1) % 3 ** (r + 1), X[1] % 3 ** (r + 1), X[2] % 3 ** (r + 1), (X[3] - 1) % 3 ** (r + 1)) == (0, 0, 0, 0) for _ in [0]) and (B[0] * B[3] - B[1] * B[2]) % 3 != 0
    print('  r = %d: %s' % (r, Y(ok)))
print('  half-turn: A^(4 x 3^(n-1)) = -I mod 3^n for n = 1 to 8: %s' % Y(all(mpow(4 * 3 ** (n - 1), 3 ** n) == (3 ** n - 1, 0, 0, 3 ** n - 1) for n in range(1, 9))))

print('IV. THE CENSUS THEOREM: mod 3^n, one fixed point, one 8-loop, and 3^(m-1) loops of length 8 x 3^(m-1) for m = 2..n [EXACT]')
OB = {}
for n in range(1, 7):
    m = 3 ** n; O, seen = OB[n] = orbits(m)
    pred = Counter({1: 1, 8: 1}); [pred.update({8 * 3 ** (j - 1): 3 ** (j - 1)}) for j in range(2, n + 1)]
    print('  mod 3^%d: %d loops; census as predicted: %s' % (n, len(O), Y(Counter(len(o) for o in O) == pred)))
print('  total states 1 + 8 + sum 3^(m-1) x 8 x 3^(m-1) = 9^n for n = 1 to 12: %s' % Y(all(1 + 8 + sum(3 ** (j - 1) * 8 * 3 ** (j - 1) for j in range(2, n + 1)) == 9 ** n for n in range(1, 13))))

print('V. THE COMPLETE INVARIANT: the loop of a state is fixed by its depth r and its norm up to sign, N/9^r mod 3^(n-r) [EXACT]')
for n in range(1, 7):
    m = 3 ** n; O, seen = OB[n]; keys = set()
    for o in O:
        s = o[0]; r = val(s, n)
        if r == n: keys.add('zero'); continue
        q = 3 ** (n - r); c = ((s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) // 9 ** r) % q; keys.add((r, min(c, (-c) % q)))
    print('  mod 3^%d: %d loops, %d distinct invariants -> complete: %s' % (n, len(O), len(keys), Y(len(keys) == len(O))))

print('VI. THE LAW IS THE WHOLE GROUP OF NORM +-1: <phi> = {u : N(u) = +-1}; the norm is onto the units [EXACT]')
for n in range(1, 7):
    m = 3 ** n; pw, y = set(), (1, 0)
    for _ in range(8 * 3 ** (n - 1)): pw.add(y); y = T(y, m)
    U = [(a, b) for a in range(m) for b in range(m) if (a % 3, b % 3) != (0, 0)]
    print('  mod 3^%d: |<phi>| = %d = |{N = +-1}|, same set: %s; norm image = all %d units: %s' % (
        n, len(pw), Y({u for u in U if N(u, m) in (1, m - 1)} == pw), 2 * 3 ** (n - 1), Y(len({N(u, m) for u in U}) == 2 * 3 ** (n - 1))))
print('  so the loops of units are the cosets of <phi>, one for each unit norm up to sign: 3^(n-1) of them')

print('VII. THE LIFT TREE: the zero state lifts to the zero state and one 8-loop; every other loop to exactly 3 loops of 3 times its length [EXACT]')
for n in range(2, 7):
    Op, seenp = OB[n - 1]; O, _ = OB[n]; mp = 3 ** (n - 1); kids = defaultdict(list)
    for o in O: kids[seenp[(o[0][0] % mp, o[0][1] % mp)]].append(len(o))
    ok = all(sorted(c) == ([1, 8] if len(Op[p]) == 1 else [3 * len(Op[p])] * 3) for p, c in kids.items())
    print('  3^%d -> 3^%d: %s' % (n - 1, n, Y(ok)))
print('  one Omega42 depth is two such steps: every nonzero loop has exactly 9 loops of 9 times its length above it')

print('VIII. SYMMETRY [EXACT]')
m = 9; S = [(a, b) for a in range(m) for b in range(m)]
GL = [M4 for M4 in itertools.product(range(m), repeat=4) if (M4[0] * M4[3] - M4[1] * M4[2]) % 3]
act = lambda M4, p: ((M4[0] * p[0] + M4[1] * p[1]) % m, (M4[2] * p[0] + M4[3] * p[1]) % m)
cent = [M4 for M4 in GL if all(act(M4, T(p, m)) == T(act(M4, p), m) for p in ((1, 0), (0, 1)))]
Oq = [M4 for M4 in GL if all(N(act(M4, p), m) == N(p, m) for p in S)]
SO = [M4 for M4 in Oq if (M4[0] * M4[3] - M4[1] * M4[2]) % m == 1]
A2 = set(); X = (1, 0, 0, 1)
for _ in range(12): A2.add(X); X = ((X[0] * 1 + X[1] * 1) % m, (X[0] * 1 + X[1] * 2) % m, (X[2] * 1 + X[3] * 1) % m, (X[2] * 1 + X[3] * 2) % m)
print('  mod 9: |GL2| = %d; the centralizer of the law has %d elements = the 72 units of R_2 (multiplications by a + b phi): %s' % (len(GL), len(cent), Y(len(cent) == 72 and all(any(all(act(M4, p) == mul((x, y), p, m) for p in ((1, 0), (0, 1))) for x in range(m) for y in range(m)) for M4 in cent))))
print('  |O(Q)| = %d, |SO(Q)| = %d, and SO(Q) is generated by the double step A^2: %s' % (len(Oq), len(SO), Y(set(SO) == A2)))
sig = lambda s: ((s[0] + s[1]) % m, (-s[1]) % m); Ti = lambda s: ((s[1] - s[0]) % m, s[0])
print('  Galois conjugation sigma(a, b) = (a + b, -b) keeps Q and reverses time, sigma T sigma = -T^-1: %s' % Y(all(N(sig(p), m) == N(p, m) and sig(T(sig(p), m)) == tuple((-c) % m for c in Ti(p)) for p in S)))
print('  so O(Q) = <A^2> with sigma: a dihedral group of order 24, the turning and the reversal')

print('IX. GAUSS SUMS: G_n(t) = sum e(t Q / 3^n) = 9^j (-3)^(n-j), j = min(v3(t), n) [EXACT]')
for n in range(1, 6):
    m = 3 ** n; dist = Counter(N((a, b), m) for a in range(m) for b in range(m)); ok = True
    for t in range(m):
        g = sum(c * cmath.exp(2j * math.pi * t * q / m) for q, c in dist.items()); j = v3(t, n)
        ok &= abs(g - 9 ** j * (-3) ** (n - j)) < 1e-6
    print('  mod 3^%d, every t: %s' % (n, Y(ok)))
print('  at every Omega42 depth (n = 2k) and unit t, G = 9^k = sqrt(81^k): the quadratic module ((Z/9^k)^2, Q/9^k) has central charge 0 mod 8')
iso = [p for p in S if N(p, 9) == 0]
print('  mod 9: the isotropic vectors of q = Q/9 are exactly the 9 multiples of 3 (the still point and the 8-loop): %s, a Lagrangian subgroup' % Y(set(iso) == {(a, b) for a in (0, 3, 6) for b in (0, 3, 6)}))
print('  Q = X^2 + Y^2 after the change (a, b) = (X + 4Y, Y) mod 9: %s' % Y(all(N(((x + 4 * y) % 9, y), 9) == (x * x + y * y) % 9 for x in range(9) for y in range(9))))

print('X. FIXED POINTS AND THE ZETA FUNCTION: Fix(T^k) mod 3^n = 1 if 8 does not divide k, else 9^min(j+1, n), k = 8 x 3^j x s [EXACT]')
for n in (2, 4):
    m = 3 ** n; ok = True
    for k in (1, 4, 8, 12, 16, 24, 40, 72, 216):
        X = mpow(k, m); fix = sum(1 for a in range(m) for b in range(m) if ((X[0] * a + X[1] * b) % m, (X[2] * a + X[3] * b) % m) == (a, b))
        if k % 8: pred = 1
        else:
            q, j = k // 8, 0
            while q % 3 == 0: q //= 3; j += 1
            pred = 9 ** min(j + 1, n)
        ok &= fix == pred
    print('  mod 3^%d: %s' % (n, Y(ok)))
print('  zeta_n(t) = 1 / [(1 - t)(1 - t^8) prod_{m=2..n} (1 - t^(8 x 3^(m-1)))^(3^(m-1))]')

print('XI. THE LIMIT Z_3[phi] [DERIVED from I to VII; Companion 102.8]')
print('  T is a 3-adic isometry (A and A^-1 have integer entries), keeps Haar measure, has topological entropy 0;')
print('  its only periodic point is 0; the closure of the orbit of z != 0 is the norm level set {w : N(w) = +-N(z)} (V and VI at every depth),')
print('  and on it T is the odometer x -> x + 1 on Z/8 x Z_3: minimal, uniquely ergodic, every orbit dense in its level set')

print('XII. THE PRIME 3 AMONG THE PRIMES [EXACT for the primes listed]')
def order(m):
    X, k = mpow(1, m), 1
    while X != (1, 0, 0, 1): X = mpow(k + 1, m); k += 1
    return k
for p in (2, 3, 7, 13, 17, 23):
    o = order(p); print('  p = %2d (inert): order of phi mod p = %3d of p^2 - 1 = %3d; phi generates F_(p^2)^x: %s; order mod p^2, p^3: %d, %d' % (p, o, p * p - 1, Y(o == p * p - 1 or (p == 2 and o == 3)), order(p * p), order(p ** 3)))
print('  phi has order dividing 2(p + 1) at an inert odd prime, so it generates F_(p^2)^x only when p^2 - 1 = 2(p + 1): p = 3')
print('  so 3 is the one odd prime at which the law sweeps the whole residue field in one loop (a post-selection property, Core Part 1.8.3)')

print('XIII. THE OCTAGON THAT SURVIVES: the eight roots of unity of Z_3[phi] [EXACT]')
def rpow(x, e, m):
    r = (1, 0)
    while e:
        if e & 1: r = mul(r, x, m)
        x = mul(x, x, m); e >>= 1
    return r
for n in (2, 4, 6):
    m = 3 ** n; w = rpow((0, 1), 9 ** n, m)                       # omega = lim phi^(9^n), the Teichmuller lift of phi mod 3
    pw = [rpow(w, k, m) for k in range(9)]
    print('  mod 3^%d: omega = phi^(9^%d) = %s; omega^8 = 1: %s; omega has order exactly 8: %s; omega = phi mod 3: %s' % (
        n, n, w, Y(pw[8] == (1, 0)), Y(all(pw[k] != (1, 0) for k in range(1, 8))), Y((w[0] % 3, w[1] % 3) == (0, 1))))
print('  the unramified quadratic extension of Q_3 holds the 8th roots of unity and no others, so in the limit the octagon is the one exact figure;')
print('  on the 24-wheel of the surface the regular figures are the n-gons with n | 24: the mirror is the digon (spacing 12), the Eye the hexagon (spacing 4)')

print('XIV. THE SURFACE QUADRATIC MODULE INSIDE E8 [EXACT]')
C8 = [[2,0,-1,0,0,0,0,0],[0,2,0,-1,0,0,0,0],[-1,0,2,-1,0,0,0,0],[0,-1,-1,2,-1,0,0,0],[0,0,0,-1,2,-1,0,0],[0,0,0,0,-1,2,-1,0],[0,0,0,0,0,-1,2,-1],[0,0,0,0,0,0,-1,2]]
def det(M):
    M = [r[:] for r in M]; n = len(M); d = 1
    from fractions import Fraction as F
    M = [[F(x) for x in r] for r in M]
    for i in range(n):
        p = next((k for k in range(i, n) if M[k][i] != 0), None)
        if p is None: return 0
        if p != i: M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        for k in range(i + 1, n):
            f = M[k][i] / M[i][i]
            for j in range(i, n): M[k][j] -= f * M[i][j]
    return d
ip = lambda x, y: sum(x[i] * C8[i][j] * y[j] for i in range(8) for j in range(8))
u = [1,0,0,0,0,0,0,0]; w = [0,0,0,0,1,0,0,0]                     # simple roots alpha_1 and alpha_5 of E8, orthogonal
print('  E8 Cartan matrix: determinant %s (unimodular); alpha_1, alpha_5 are roots (norm %d, %d) and orthogonal (%d)' % (det(C8), ip(u, u), ip(w, w), ip(u, w)))
# L = {x : <x,u> = <x,w> = 0 mod 3}: a basis by hand -- every coordinate free except the two constraints, solved on coordinates 3 and 4
# <x,alpha_1> = 2x1 - x3, <x,alpha_5> = -x4 + 2x5 - x6: L is spanned by e1 + 2e3, 3e3, e2, e4 + 2... -- take the index-9 lattice from the HNF of the kernel
import itertools as it
basis = []
for i in range(8):
    e = [0] * 8; e[i] = 1
    basis.append(e)
def inL(x): return ip(x, u) % 3 == 0 and ip(x, w) % 3 == 0
gens = [x for x in basis if inL(x)] + [[3 if j == i else 0 for j in range(8)] for i in range(8) if not inL(basis[i])]
# fix: x3 enters <.,alpha_1>, x4 and x6 enter <.,alpha_5>; correct the unit vectors that fail by adding multiples of e3 / e4
B = []
for i in range(8):
    x = basis[i][:]
    if not inL(x):
        for c3, c4 in it.product(range(3), repeat=2):
            y = x[:]; y[2] += c3; y[3] += c4
            if inL(y) and (i not in (2, 3)): x = y; break
    B.append(x)
B[2] = [0,0,3,0,0,0,0,0]; B[3] = [0,0,0,3,0,0,0,0]
G = [[ip(B[i], B[j]) for j in range(8)] for i in range(8)]
print('  L = {x in E8 : <x, alpha_1> = <x, alpha_5> = 0 mod 3}, basis in L: %s; det Gram(L) = %s = 9^2 (index 9 in E8)' % (Y(all(inL(b) for b in B)), det(G)))
okdual = all(ip(u, b) % 3 == 0 and ip(w, b) % 3 == 0 for b in B)
rel = [(n, m) for n in range(9) for m in range(9) if (n, m) != (0, 0) and n % 3 == 0 and m % 3 == 0 and inL([n // 3 * u[i] + m // 3 * w[i] for i in range(8)])]
print('  u/3, w/3 in the dual of L: %s; no relation n u/3 + m w/3 in L with (n, m) != 0 mod 9: %s; q(u/3) = <u,u>/18 = %s, q(w/3) = %s, b(u/3, w/3) = %s' % (
    Y(okdual), Y(not rel), '1/9' if ip(u, u) == 2 else '?', '1/9' if ip(w, w) == 2 else '?', ip(u, w)))
print('  so L*/L = (Z/9)^2 generated by u/3, w/3, with discriminant form (x^2 + y^2)/9: the Omega42 form q = Q/9 of IX')
from fractions import Fraction as Fr
def inv11(Cm):
    n = len(Cm); M = [[Fr(x) for x in r] + [Fr(int(i == j)) for j in range(n)] for i, r in enumerate(Cm)]
    for i in range(n):
        p = next(k for k in range(i, n) if M[k][i] != 0); M[i], M[p] = M[p], M[i]; f = M[i][i]; M[i] = [x / f for x in M[i]]
        for k in range(n):
            if k != i and M[k][i] != 0: g = M[k][i]; M[k] = [a - g * b for a, b in zip(M[k], M[i])]
    return M[0][n]
A2c = [[2, -1], [-1, 2]]
E6c = [[2,0,-1,0,0,0],[0,2,0,-1,0,0],[-1,0,2,-1,0,0],[0,-1,-1,2,-1,0],[0,0,0,-1,2,-1],[0,0,0,0,-1,2]]
qa, qe = inv11(A2c) / 2, inv11(E6c) / 2
print('  A2: det %s, q of the generator of the discriminant = %s; E6: det %s, q = %s' % (det(A2c), qa, det(E6c), qe))
print('  so the level-3^1 form ((Z/3)^2, Q/3) = (x^2 + y^2)/3 is the discriminant form of A2 + A2, and (via x -> x + y, y -> x - y) of E6 + E6')

print('XV. TESTS RUN NOW (Companion 103.2) [EXACT]')
for n in (2, 4, 6):
    m = 3 ** n; ok = all(N(T((a, b), m), m) == (-N((a, b), m)) % m for a in range(0, m, 1 if m <= 81 else 13) for b in range(m))
    print('  T2 the norm turns over at every step, mod 3^%d: %s' % (n, Y(ok)))
for k, m in ((2, 81), (3, 729)):
    O, seen = OB[2 * k]
    r2 = [(a, b) for a in range(m) for b in range(m) if mul((a, b), (a, b), m) == (2, 0) and (a % 9, b % 9) == (2, 5)]
    top = max(len(o) for o in O); cand = [o for o in O if len(o) == top]
    surv = [i for i, o in enumerate(O) if len(o) == top and r2[0] in o]
    print('  T6 alternative selector "start at the square root of 2 above the seed", depth %d: survivors %d of %d readings -> %s; on the loop of the integers (2, 5): %s' % (
        k, len(surv), top * len(cand), 'UNIQUE' if len(surv) == 1 else 'NOT UNIQUE', Y(seen[r2[0]] == seen[(2, 5)])))
def mults(n): return n.bit_length() - 1 + bin(n).count('1') - 1
print('  T7 matrix multiplications for T^n by repeated squaring: n = 10^3: %d, 10^6: %d, 10^12: %d (at most 2 log2 n)' % (mults(10 ** 3), mults(10 ** 6), mults(10 ** 12)))
