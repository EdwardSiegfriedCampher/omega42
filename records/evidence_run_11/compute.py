#!/usr/bin/env python3
"""Evidence run 11 -- ninefold anyon data (standard library only). Run: python3 compute.py"""
import itertools, cmath, math
from fractions import Fraction as Fr

# ---------- P1: SU(N)_1 ----------
def suN(N):
    h = {a: Fr(a * (N - a), 2 * N) % 1 for a in range(N)}
    return h
def lagrangian_bosonic(N):
    h = suN(N); out = []
    for d in range(2, N):
        if N % d: continue
        L = [a for a in range(N) if a % d == 0]
        if len(L) ** 2 == N and all(h[a] == 0 for a in L):
            iso = all((h[(a + b) % N] - h[a] - h[b]) % 1 == 0 for a in L for b in L)
            if iso: out.append(d)
    return out
h9 = suN(9)
print("P1 SU(9)_1 spins h_a = a(9-a)/18 mod 1: %s" % {a: str(v) for a, v in h9.items()})
bos = [a for a in range(9) if h9[a] == 0]
print("P1 (i) bosons: %s -> exactly the Crown {0, 3, 6}: %s" % (bos, bos == [0, 3, 6]))
L = [0, 3, 6]
print("P1 (ii) {0,3,6} is a subgroup of order 3 = sqrt 9, bosonic and isotropic: %s -> Lagrangian; condensing it leaves L^perp/L = 1 anyon"
      % all((h9[(a + b) % 9] - h9[a] - h9[b]) % 1 == 0 for a in L for b in L))
print("P1     the condensed theory has no anyons and c = 8: a holomorphic theory of central charge 8, which is E8_1 (the A8 lattice glued by Z/3 is E8)")
# Galois symmetry: S_ab = (1/3) exp(-2 pi i b(a,b)), b(a,b) = h_{a+b} - h_a - h_b; sigma_k(S_ab) = S_{ka, b}
def bil(a, b): return (h9[(a + b) % 9] - h9[a] - h9[b]) % 1
galois_ok = all((k * bil(a, b)) % 1 == bil((k * a) % 9, b) for k in (1, 2, 4, 5, 7, 8) for a in range(9) for b in range(9))
print("P1 (iii) the Galois automorphism zeta -> zeta^k of Q(zeta_9) acts on the S-matrix by permuting anyons a -> k a: %s" % galois_ok)
def orbits_x2():
    seen, out = set(), []
    for a in range(9):
        if a in seen: continue
        o, x = [], a
        while x not in seen: seen.add(x); o.append(x); x = (2 * x) % 9
        out.append(o)
    return out
print("P1      h_{2a} = 4 h_a mod 1 for all a: %s | orbits of the Galois generator k = 2 on the nine anyons: %s"
      % (all(h9[(2 * a) % 9] == (4 * h9[a]) % 1 for a in range(9)), orbits_x2()))
# the condensed theory: A8 with the class-3 glue vector is even and unimodular, i.e. E8
g = [Fr(1, 3)] * 6 + [Fr(-2, 3)] * 3
roots = [[Fr(int(i == k)) - Fr(int(i == k + 1)) for i in range(9)] for k in range(8)]
dot = lambda u, v: sum(a * b for a, b in zip(u, v))
print("P1     A8 glue vector of class 3: norm %s (even), integral against every simple root: %s, 3g in A8 (coordinate sum %s, integer entries %s)"
      % (dot(g, g), all(dot(g, r).denominator == 1 for r in roots), sum(3 * x for x in g), all((3 * x).denominator == 1 for x in g)))
print("P1     det(A8) = 9 and the glue has index 3, so the overlattice has determinant 9/9 = 1: even, unimodular, rank 8 -> E8")
print("P1 NULL: SU(N)_1, N = 2..30, with a bosonic Lagrangian subgroup of multiples of d: %s"
      % {N: lagrangian_bosonic(N) for N in range(2, 31) if lagrangian_bosonic(N)})

# ---------- P2: the family as anyons ----------
N9 = 9
norm = lambda x, m: (x[0] * x[0] + x[0] * x[1] - x[1] * x[1]) % m
V = list(itertools.product(range(N9), repeat=2))
q = {x: Fr(norm(x, 9), 9) for x in V}
def bform(x, y): return (q[((x[0] + y[0]) % 9, (x[1] + y[1]) % 9)] - q[x] - q[y]) % 1
nondeg = all(any(bform(x, y) != 0 for y in V) for x in V if x != (0, 0))
print("P2 (i) the golden form q(a,b) = (a^2 + ab - b^2)/9 on (Z/9)^2 is nondegenerate (a valid abelian anyon theory): %s" % nondeg)
gauss = sum(cmath.exp(2j * math.pi * float(q[x])) for x in V) / 9
print("P2 (v) Gauss sum / D = %.6f%+.6fi -> c = 0 mod 8" % (gauss.real, gauss.imag))
bos2 = sorted(x for x in V if q[x] == 0)
core = sorted((3 * a % 9, 3 * b % 9) for a in range(3) for b in range(3))
print("P2 (iv) bosons: %d, exactly the nine core states (eight-cycle and fixed point): %s; isotropic, so Lagrangian: %s"
      % (len(bos2), bos2 == core, all(bform(x, y) == 0 for x in core for y in core)))
T = lambda x: (x[1], (x[0] + x[1]) % 9)
print("P2 (iii) T sends every spin to its conjugate (q(Tx) = -q(x)), an anti-isometry, i.e. a time-reversal symmetry of the braiding data: %s"
      % all(q[T(x)] == (-q[x]) % 1 for x in V))
print("P2      T^2 (the cat map) preserves every spin, a unitary anyon symmetry: %s" % all(q[T(T(x))] == q[x] for x in V))
for nm, vals in [("Fibonacci voice", (1, 8)), ("Lucas voice", (4, 5)), ("canonical voice", (2, 7))]:
    print("P2      %s: spins exp(2 pi i k/9) with k in %s" % (nm, vals))
# isometries
GL = [((a, b), (c, d)) for a, b, c, d in itertools.product(range(9), repeat=4) if math.gcd((a * d - b * c) % 9, 9) == 1]
def app(M, x): return ((M[0][0] * x[0] + M[0][1] * x[1]) % 9, (M[1][0] * x[0] + M[1][1] * x[1]) % 9)
targets = {"Z9 toric code, e m / 9": lambda y: Fr(y[0] * y[1] % 9, 9),
           "SU(9)_1 x SU(9)_1, 4(a^2 + b^2)/9": lambda y: Fr(4 * (y[0] ** 2 + y[1] ** 2) % 9, 9),
           "SU(9)_1 x conj(SU(9)_1), 4(a^2 - b^2)/9": lambda y: Fr(4 * (y[0] ** 2 - y[1] ** 2) % 9, 9)}
for nm, f in targets.items():
    iso = next((M for M in GL if all(f(app(M, x)) == q[x] for x in V)), None)
    nb = sum(1 for y in V if f(y) == 0)
    print("P2 (ii) isometric to %-42s %s (that theory has %d bosons)" % (nm + ":", "YES, via %s" % (iso,) if iso else "NO", nb))
# null over N
rows = []
for m in range(3, 31, 2):
    if m % 5 == 0: continue
    Vm = list(itertools.product(range(m), repeat=2))
    qm = {x: Fr(norm(x, m), m) for x in Vm}
    b = lambda x, y: (qm[((x[0] + y[0]) % m, (x[1] + y[1]) % m)] - qm[x] - qm[y]) % 1
    nb = [x for x in Vm if qm[x] == 0]
    lag = len(nb) ** 2 == m * m and all(b(x, y) == 0 for x in nb for y in nb)
    rows.append((m, len(nb), lag))
print("P2 NULL: the golden form modulo odd N (N coprime to 5), N = 3..29: (N, bosons, Lagrangian) %s" % rows)

# P2 (vi): is T distinguished among the symmetries of the anyon data?
def mmul(A, B): return tuple(tuple(sum(A[i][t] * B[t][j] for t in range(2)) % 9 for j in range(2)) for i in range(2))
iso = [M for M in GL if all(q[app(M, x)] == q[x] for x in V)]
anti = [M for M in GL if all(q[app(M, x)] == (-q[x]) % 1 for x in V)]
I2 = ((1, 0), (0, 1))
def order(M):
    k, X = 1, M
    while X != I2: X = mmul(X, M); k += 1
    return k
def ctype(M):
    seen, out = set(), []
    for x in V:
        if x in seen: continue
        c, y = 0, x
        while True:
            seen.add(y); c += 1; y = app(M, y)
            if y == x: break
        out.append(c)
    return tuple(sorted(out, reverse=True))
from collections import Counter
print("P2 (vi) unitary anyon symmetries (isometries of the golden form): %d; time-reversal symmetries (anti-isometries): %d" % (len(iso), len(anti)))
print("P2      anti-isometries by order: %s" % dict(sorted(Counter(order(M) for M in anti).items())))
fam = ctype(((0, 1), (1, 1)))
withfam = [M for M in anti if ctype(M) == fam]
inv = lambda P: next(Q for Q in GL if mmul(P, Q) == I2)
Tm = ((0, 1), (1, 1))
conjT = {mmul(mmul(P, Tm), inv(P)) for P in iso}
print("P2      anti-isometries with the family's cycle type (24, 24, 24, 8, 1): %d; conjugates of T under the unitary symmetries: %d; all of them are conjugates of T or of T^-1: %s"
      % (len(withfam), len(conjT), set(withfam) <= (conjT | {mmul(mmul(P, inv(Tm)), inv(P)) for P in iso})))

# P2 (vii): the complete symmetry group of the anyon data and its orbits
CONJ = ((1, 1), (0, 9 - 1))                     # golden conjugation a + b phi -> a + b (1 - phi): (a, b) -> (a + b, -b)
print("P2 (vii) golden conjugation preserves every spin: %s" % all(q[app(CONJ, x)] == q[x] for x in V))
def gen(gs):
    S = {I2}; fr = [I2]
    while fr:
        nx = []
        for X in fr:
            for g_ in gs:
                Y = mmul(X, g_)
                if Y not in S: S.add(Y); nx.append(Y)
        fr = nx
    return S
G = gen([Tm, CONJ])
print("P2      the group generated by T and the golden conjugation has order %d and equals the full symmetry group (unitary and time-reversal): %s"
      % (len(G), G == set(iso) | set(anti)))
powers = {I2}; X = I2
for k in range(1, 24): X = mmul(X, Tm); powers.add(X)
gens24 = {M for M in anti if order(M) == 24}
odd_gen = set(); X = I2
for k in range(1, 24):
    X = mmul(X, Tm)
    if k % 2 and math.gcd(k, 24) == 1: odd_gen.add(X)
print("P2      the 8 time-reversal symmetries of order 24 are exactly the generators of the cyclic group <T>: %s" % (gens24 == odd_gen))
seen, orbs = set(), []
for x in V:
    if x in seen: continue
    o = {app(M, x) for M in G}; seen |= o; orbs.append(o)
print("P2      orbits of the full symmetry group on the 81 anyons: %s -> the family's five orbits: %s"
      % (sorted((len(o) for o in orbs), reverse=True), sorted((len(o) for o in orbs), reverse=True) == [24, 24, 24, 8, 1]))
T12 = I2
for _ in range(12): T12 = mmul(T12, Tm)
print("P2      the half period T^12 = -I is charge conjugation (each anyon to its antiparticle): %s" % (T12 == ((8, 0), (0, 8))))
