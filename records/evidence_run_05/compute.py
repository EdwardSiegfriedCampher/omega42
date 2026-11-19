#!/usr/bin/env python3
"""Evidence run 05 -- computations (standard library only). Run: python3 compute.py"""
import itertools
from fractions import Fraction as Fr

# ---------- E-A: the triangular lattice on an N x N torus, Eisenstein coordinates a + b*omega ----------
def emul(u, v, m):                     # omega^2 = -1 - omega
    a, b = u; c, d = v
    return ((a*c - b*d) % m, (a*d + b*c - b*d) % m)
ROT60 = (1, 1)                          # 1 + omega = exp(i pi / 3)
def cycle_type(f, pts):
    seen, out = set(), []
    for p in pts:
        if p in seen: continue
        c, x = [], p
        while x not in seen: seen.add(x); c.append(x); x = f(x)
        out.append(c)
    return out
def epow(u, k, m):
    x = (1, 0)
    for _ in range(k): x = emul(x, u, m)
    return x
print("E-A rotation by 60 degrees is multiplication by 1 + omega: (1+omega)^6 = 1: %s, (1+omega)^3 = -1: %s"
      % (epow(ROT60, 6, 10**6) == (1, 0), epow(ROT60, 3, 10**6) == (10**6 - 1, 0)))
for N in range(2, 10):
    pts = list(itertools.product(range(N), repeat=2))
    cyc = cycle_type(lambda p: emul(ROT60, p, N), pts)
    ct = sorted((len(c) for c in cyc), reverse=True)
    extra = ""
    if N == 3:
        small = sorted(p for c in cyc if len(c) <= 2 for p in c)
        sub = sorted({emul((1, N - 1), p, N) for p in pts})          # multiples of 1 - omega
        extra = " | fixed site and 2-cycle = the sqrt3 x sqrt3 sublattice through the centre: %s" % (small == sub)
    print("E-A triangular lattice, %d x %d torus (%2d sites): 60-degree rotation, cycle type %s%s" % (N, N, N * N, ct, extra))
z9 = cycle_type(lambda v: (2 * v) % 9, range(9))
print("E-A Z/9 under x2: cycle type %s, cycles %s" % (sorted((len(c) for c in z9), reverse=True), z9))
sq = cycle_type(lambda p: ((-p[1]) % 3, p[0]), list(itertools.product(range(3), repeat=2)))
print("E-A NULL square lattice, 3 x 3 torus: 90-degree rotation, cycle type %s" % sorted((len(c) for c in sq), reverse=True))
# mapping freedom: bijections Z/9 -> sites intertwining x2 with the rotation
def count_intertwiners():
    A = {c[0]: c for c in z9}; B = cycle_type(lambda p: emul(ROT60, p, 3), list(itertools.product(range(3), repeat=2)))
    n = 1
    for L in (6, 2, 1):
        ka = sum(1 for c in z9 if len(c) == L); kb = sum(1 for c in B if len(c) == L)
        assert ka == kb
        n *= L ** ka * __import__('math').factorial(ka)
    return n
print("E-A bijections carrying x2 on Z/9 to the rotation on the nine sites (M230-D): %d" % count_intertwiners())

# ---------- E-B: the 24-cell's vertices (Hurwitz units) acting on the family's nine-state core ----------
def m3(P, Q): return tuple(tuple(sum(P[i][t] * Q[t][j] for t in range(2)) % 3 for j in range(2)) for i in range(2))
def det3(P): return (P[0][0] * P[1][1] - P[0][1] * P[1][0]) % 3
M2 = [((a, b), (c, d)) for a, b, c, d in itertools.product(range(3), repeat=4)]
NEG = ((2, 0), (0, 2)); I2 = ((1, 0), (0, 1))
I_, J_ = next((P, Q) for P in M2 for Q in M2 if m3(P, P) == NEG and m3(Q, Q) == NEG and m3(P, Q) == tuple(tuple((-x) % 3 for x in r) for r in m3(Q, P)))
K_ = m3(I_, J_)
units = [(s, 0, 0, 0) for s in (1, -1)] + [(0, s, 0, 0) for s in (1, -1)] + [(0, 0, s, 0) for s in (1, -1)] + [(0, 0, 0, s) for s in (1, -1)]
units = [tuple(Fr(x) for x in u) for u in units] + [tuple(Fr(s, 2) for s in sg) for sg in itertools.product((1, -1), repeat=4)]
def red(x): return (x.numerator * pow(x.denominator, -1, 3)) % 3
def image(q):
    a, b, c, d = (red(x) for x in q)
    return tuple(tuple((a * I2[i][j] + b * I_[i][j] + c * J_[i][j] + d * K_[i][j]) % 3 for j in range(2)) for i in range(2))
def qmul(p, q):
    a1, b1, c1, d1 = p; a2, b2, c2, d2 = q
    return (a1*a2 - b1*b2 - c1*c2 - d1*d2, a1*b2 + b1*a2 + c1*d2 - d1*c2, a1*c2 - b1*d2 + c1*a2 + d1*b2, a1*d2 + b1*c2 - c1*b2 + d1*a2)
imgs = [image(u) for u in units]
print("E-B the 24 Hurwitz units (the 24-cell's vertices) are closed under multiplication: %s" % all(qmul(p, q) in units for p in units for q in units))
print("E-B reduced modulo 3 they map to %d distinct 2 x 2 matrices over F3, all of determinant 1: %s, and the map is a homomorphism: %s"
      % (len(set(imgs)), all(det3(P) == 1 for P in imgs), all(image(qmul(p, q)) == m3(image(p), image(q)) for p in units for q in units)))
SL = [P for P in M2 if det3(P) == 1]
print("E-B |SL(2,3)| = %d, so the 24 vertices are exactly SL(2,3), acting on the plane F3^2 = the family's nine core states (3a, 3b)" % len(SL))
T3 = ((0, 1), (1, 1)); T3sq = m3(T3, T3)
print("E-B T reduced to the core: det %d -> among the 24 vertex-matrices: %s | T^2 on the core: among them: %s"
      % (det3(T3), T3 in imgs, T3sq in imgs))
core = [(3 * a, 3 * b) for a in range(3) for b in range(3)]
Tfam = lambda s: (s[1], (s[0] + s[1]) % 9)
print("E-B T on the family's core states equals T reduced mod 3 on F3^2:", all(Tfam(s) == (3 * ((T3[0][0]*(s[0]//3) + T3[0][1]*(s[1]//3)) % 3), 3 * ((T3[1][0]*(s[0]//3) + T3[1][1]*(s[1]//3)) % 3)) for s in core))
# null: all subgroups of order 24 of GL(2,3)
GL = [P for P in M2 if det3(P) != 0]
def gen(gs):
    S = {I2}; frontier = [I2]
    while frontier:
        nxt = []
        for x in frontier:
            for g in gs:
                y = m3(x, g)
                if y not in S: S.add(y); nxt.append(y)
        frontier = nxt
    return frozenset(S)
subs = {gen([a, b]) for a in GL for b in GL}
def order(P):
    k, X = 1, P
    while X != I2: X = m3(X, P); k += 1
    return k
o24 = [S for S in subs if len(S) == 24]
print("E-B NULL: |GL(2,3)| = %d; subgroups of order 24 generated by two elements: %d" % (len(GL), len(o24)))
for S in o24:
    stats = {}
    for P in S: stats[order(P)] = stats.get(order(P), 0) + 1
    print("E-B      order-24 subgroup: element orders %s | equals SL(2,3): %s" % (dict(sorted(stats.items())), set(S) == set(SL)))
s4 = {1: 1, 2: 9, 3: 8, 4: 6}
print("E-B NULL: an S4 (the cube's rotation group, element orders %s) inside GL(2,3): %s" % (s4, any(
    {o: sum(1 for P in S if order(P) == o) for o in set(order(P) for P in S)} == s4 for S in o24)))
comm = gen([m3(m3(a, b), m3(inv, invb)) for a in GL for b in GL
             for inv in [next(X for X in GL if m3(a, X) == I2)] for invb in [next(X for X in GL if m3(b, X) == I2)]])
print("E-B the commutator subgroup of GL(2,3) is SL(2,3): %s -- so SL(2,3) is the only subgroup of index 2, i.e. of order 24" % (set(comm) == set(SL)))
pairs = [(P, Q) for P in M2 for Q in M2 if m3(P, P) == NEG and m3(Q, Q) == NEG and m3(P, Q) == tuple(tuple((-x) % 3 for x in r) for r in m3(Q, P))]
print("E-B mapping freedom (M230-D): %d choices of the images of i and j; every choice gives the same image set SL(2,3): %s"
      % (len(pairs), all({tuple(tuple((red(q[0]) * I2[a][b] + red(q[1]) * P[a][b] + red(q[2]) * Q[a][b] + red(q[3]) * m3(P, Q)[a][b]) % 3
                              for b in range(2)) for a in range(2)) for q in units} == set(SL) for P, Q in pairs)))
print("E-B largest element order in GL(2,3): %d" % max(order(P) for P in GL))
