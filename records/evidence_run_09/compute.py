#!/usr/bin/env python3
"""Evidence run 09 -- E8 as the icosian ring: an eightfold lattice with an intrinsic golden endomorphism.
Standard library only. Run: python3 compute.py"""
import itertools, math
from fractions import Fraction as Fr

# numbers a + b sqrt5 with rational a, b
def add(x, y): return (x[0] + y[0], x[1] + y[1])
def mul(x, y): return (x[0] * y[0] + 5 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])
def neg(x): return (-x[0], -x[1])
Z0 = (Fr(0), Fr(0)); ONE = (Fr(1), Fr(0))
PHI = (Fr(1, 2), Fr(1, 2)); IPHI = (Fr(-1, 2), Fr(1, 2))          # phi and 1/phi = phi - 1
def half(x): return (x[0] / 2, x[1] / 2)
def qmul(p, q):
    a1, b1, c1, d1 = p; a2, b2, c2, d2 = q
    m = mul
    return (add(add(m(a1, a2), neg(m(b1, b2))), add(neg(m(c1, c2)), neg(m(d1, d2)))),
            add(add(m(a1, b2), m(b1, a2)), add(m(c1, d2), neg(m(d1, c2)))),
            add(add(m(a1, c2), neg(m(b1, d2))), add(m(c1, a2), m(d1, b2))),
            add(add(m(a1, d2), m(b1, c2)), add(neg(m(c1, b2)), m(d1, a2))))
# the 120 unit icosians
units = set()
for i in range(4):
    for s in (1, -1):
        v = [Z0] * 4; v[i] = (Fr(s), Fr(0)); units.add(tuple(v))
for sg in itertools.product((1, -1), repeat=4):
    units.add(tuple((Fr(s, 2), Fr(0)) for s in sg))
base = [Z0, ONE, PHI, IPHI]
even_perms = [p for p in itertools.permutations(range(4)) if sum(1 for i in range(4) for j in range(i + 1, 4) if p[i] > p[j]) % 2 == 0]
for p in even_perms:
    for sg in itertools.product((1, -1), repeat=3):
        vals = [Z0, ONE, PHI, IPHI]
        signed = [vals[0]] + [vals[k] if sg[k - 1] == 1 else neg(vals[k]) for k in (1, 2, 3)]
        v = [None] * 4
        for pos, k in zip(p, range(4)): v[pos] = half(signed[k])
        units.add(tuple(v))
units = sorted(units)
print("H1 unit icosians: %d | closed under multiplication: %s" % (len(units), all(qmul(a, b) in set(units) for a in units for b in units)))
# integer coordinates: 4 x (a, b) scaled by 4
def vec(q): return [int(4 * c) for x in q for c in x]
def hnf(rows):
    A = [r[:] for r in rows if any(r)]; n = len(A[0]); out = []; col = 0
    while A and col < n:
        piv = [r for r in A if r[col] != 0]; rest = [r for r in A if r[col] == 0]
        if not piv: col += 1; continue
        while len(piv) > 1:
            piv.sort(key=lambda r: abs(r[col])); p = piv[0]; new = [p]
            for r in piv[1:]:
                q = r[col] // p[col]; r2 = [a - q * b for a, b in zip(r, p)]
                (new if r2[col] != 0 else rest).append(r2)
            piv = new
        p = piv[0]
        if p[col] < 0: p = [-a for a in p]
        out.append(p); A = [r for r in rest if any(r)]; col += 1
    return out
B = hnf([vec(u) for u in units])
print("H1 the icosian ring has rank %d over Z" % len(B))
def from_vec(v): return tuple((Fr(v[2 * i], 4), Fr(v[2 * i + 1], 4)) for i in range(4))
BQ = [from_vec(b) for b in B]
def bil(x, y):
    s = Z0
    for a, b in zip(x, y): s = add(s, mul(a, b))
    return s
def det(M):
    M = [[Fr(x) for x in r] for r in M]; n = len(M); d = Fr(1)
    for i in range(n):
        p = next((k for k in range(i, n) if M[k][i] != 0), None)
        if p is None: return Fr(0)
        if p != i: M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        for k in range(i + 1, n):
            f = M[k][i] / M[i][i]; M[k] = [a - f * b for a, b in zip(M[k], M[i])]
    return d
found = None
cands = {'1': ONE, 'phi': PHI, '1/phi': IPHI, 'phi^2': mul(PHI, PHI), '1/sqrt5': (Fr(0), Fr(1, 5)), 'phi/sqrt5': mul(PHI, (Fr(0), Fr(1, 5))),
         '1/(phi sqrt5)': mul(IPHI, (Fr(0), Fr(1, 5))), 'phi^2/sqrt5': mul(mul(PHI, PHI), (Fr(0), Fr(1, 5)))}
for nm, lam in cands.items():
    for scale in (Fr(1), Fr(2), Fr(1, 2)):
        G = [[scale * 2 * mul(lam, bil(x, y))[0] for y in BQ] for x in BQ]          # Tr(a + b sqrt5) = 2a
        if all(g.denominator == 1 for r in G for g in r) and all(G[i][i] % 2 == 0 for i in range(8)) and det(G) == 1:
            if all(G[i][i] > 0 for i in range(8)):
                found = (nm, lam, scale); break
    if found: break
nm, lam, scale = found
print("H1 form <x, y> = %s * Tr(%s * x.y): integral, even, determinant 1, rank 8 -> the E8 lattice (unique even unimodular in rank 8)" % (scale, nm))
def q(x): return scale * 2 * mul(lam, bil(x, x))[0]
roots = [u for u in units if q(u) == 2] + [tuple(mul(PHI, c) for c in u) for u in units if q(tuple(mul(PHI, c) for c in u)) == 2] \
        + [tuple(mul(IPHI, c) for c in u) for u in units if q(tuple(mul(IPHI, c) for c in u)) == 2]
print("H1 vectors of norm 2 among the units u, phi*u and u/phi: %d (E8 has 240)" % len(set(roots)))
# H2: multiplication by phi
def coords(x):
    v = [Fr(c) for c in vec_frac(x)]
    c = []
    for b in B:
        piv = next(i for i in range(8) if b[i] != 0)
        ci = v[piv] / b[piv]; c.append(ci); v = [a - ci * bb for a, bb in zip(v, b)]
    assert all(a == 0 for a in v) and all(x.denominator == 1 for x in c)
    return [int(x) for x in c]
def vec_frac(qq): return [4 * c for x in qq for c in x]
Gphi = [coords(tuple(mul(PHI, c) for c in b)) for b in BQ]
I8 = [[int(i == j) for j in range(8)] for i in range(8)]
def mm(A, C): return [[sum(a * b for a, b in zip(r, col)) for col in zip(*C)] for r in A]
G2 = mm(Gphi, Gphi)
print("H2 multiplication by phi is an integer endomorphism of E8 with phi^2 = phi + 1: %s" % (G2 == [[a + b for a, b in zip(r1, r2)] for r1, r2 in zip(Gphi, I8)]))
print("H2 it is self-adjoint for the E8 form: %s" % all(scale * 2 * mul(lam, bil(tuple(mul(PHI, c) for c in x), y))[0] == scale * 2 * mul(lam, bil(x, tuple(mul(PHI, c) for c in y)))[0] for x in BQ for y in BQ))

# H3: quotients (E8 is a torsion-free module over the principal ideal domain Z[phi] of Z-rank 8, hence free of rank 4)
def T(s, m): return (s[1], (s[0] + s[1]) % m)
def ker_count(k, m):
    c = 0
    for s in itertools.product(range(m), repeat=2):
        x = s
        for _ in range(k): x = T(x, m)
        c += x == s
    return c
def orbit_counts(m, rank):
    P = next(k for k in range(1, 100) if ker_count(k, m) == m * m)
    divs = [d for d in range(1, P + 1) if P % d == 0]
    fixed = {d: ker_count(d, m) ** rank for d in divs}
    exact = {}
    for d in divs:
        exact[d] = fixed[d] - sum(exact[e] for e in divs if e < d and d % e == 0)
    return {d: exact[d] // d for d in sorted(divs, reverse=True) if exact[d]}
print("H3 E8/9E8 = (Z[phi]/9)^4, phi acting as T: %d elements; orbits by length %s" % (81 ** 4, orbit_counts(9, 4)))
print("H3 E8/8E8 = (Z[phi]/8)^4, phi acting as T mod 8: %d elements; orbits by length %s" % (64 ** 4, orbit_counts(8, 4)))
print("H3 reference: the family itself (rank 1): %s" % orbit_counts(9, 1))

# H4: isometries commuting with phi
def lr(a, b): return [coords(qmul(qmul(a, bq), b)) for bq in BQ]
mats = set()
for a in units:
    for b in units:
        mats.add(tuple(map(tuple, lr(a, b))))
comm = all(mm([list(r) for r in M], Gphi) == mm(Gphi, [list(r) for r in M]) for M in mats)
print("H4 E8: left-and-right multiplications by unit icosians give %d distinct isometries, all commuting with phi: %s" % (len(mats), comm))
G0 = [[0] * 8 for _ in range(8)]
for k in range(4): G0[2 * k][2 * k + 1] = 1; G0[2 * k + 1][2 * k] = 1; G0[2 * k + 1][2 * k + 1] = 1
cnt = 0
for perm in itertools.permutations(range(8)):
    M = [[G0[perm[i]][perm[j]] for j in range(8)] for i in range(8)]
    if any((M[i][j] != 0) != (G0[i][j] != 0) for i in range(8) for j in range(8)): continue
    for sg in itertools.product((1, -1), repeat=8):
        if all(sg[i] * M[i][j] * sg[j] == G0[i][j] for i in range(8) for j in range(8)): cnt += 1
print("H4 Z^8 with four golden blocks: signed permutations commuting with phi: %d" % cnt)

# H5: Zamolodchikov's E8 masses
c = math.cos; pi = math.pi
m1 = 1.0; m2 = 2 * c(pi / 5); m3 = 2 * c(pi / 30); m4 = 2 * m2 * c(7 * pi / 30); m5 = 2 * m2 * c(2 * pi / 15)
m6 = 2 * m2 * c(pi / 30); m7 = 4 * m2 * c(pi / 5) * c(7 * pi / 30); m8 = 4 * m2 * c(pi / 5) * c(2 * pi / 15)
ms = [m1, m2, m3, m4, m5, m6, m7, m8]; phi = (1 + 5 ** 0.5) / 2
print("H5 Zamolodchikov masses / m1: %s" % [round(x, 4) for x in ms])
pairs = [(i + 1, j + 1) for i in range(8) for j in range(8) if abs(ms[j] / ms[i] - phi) < 1e-9]
print("H5 pairs with m_j / m_i = phi exactly: %s -> the eight masses form %d golden pairs" % (pairs, len(pairs)))
# H5 check: the masses are the Perron-Frobenius eigenvector of the E8 Cartan matrix (power iteration on the adjacency matrix)
edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)]                 # E8 Dynkin diagram: chain of 7 with a branch at node 2
Adj = [[0] * 8 for _ in range(8)]
for a, b in edges: Adj[a][b] = Adj[b][a] = 1
v = [1.0] * 8
for _ in range(2000):
    w = [sum(Adj[i][j] * v[j] for j in range(8)) + v[i] for i in range(8)]       # shift by I to make the iteration converge
    s = max(w); v = [x / s for x in w]
pf = sorted(v); pf = [x / pf[0] for x in pf]
print("H5 Perron-Frobenius eigenvector of the E8 diagram, sorted and scaled: %s | matches the mass list: %s"
      % ([round(x, 4) for x in pf], all(abs(a - b) < 1e-6 for a, b in zip(pf, ms))))
