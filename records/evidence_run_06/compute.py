#!/usr/bin/env python3
"""Evidence run 06 -- half-period negation and the family (standard library only). Run: python3 compute.py"""
import itertools, random
from fractions import Fraction as Fr

# ---------- Q1: the algebra ----------
def prem(f, g, m):
    """remainder of f by monic g, coefficients mod m (lists, highest degree first)"""
    f = [c % m for c in f]
    while len(f) >= len(g):
        c = f[0]
        for i in range(len(g)): f[i] = (f[i] - c * g[i]) % m
        f.pop(0)
    while f and f[0] == 0: f.pop(0)
    return f
X12 = [1] + [0] * 11 + [1]; PHI24 = [1, 0, 0, 0, -1, 0, 0, 0, 1]; PHI8 = [1, 0, 0, 0, 1]; X6 = [1, 0, 0, 0, 0, 0, 1]; PHI12 = [1, 0, -1, 0, 1]
GOLD = [1, -1, -1]; CAT = [1, -3, 1]
for nm, f in [('x^12 + 1', X12), ('Phi24', PHI24), ('Phi8', PHI8), ('x^6 + 1', X6), ('Phi12', PHI12)]:
    print("Q1 %-9s mod (9, x^2 - x - 1): remainder %-8s | mod (9, x^2 - 3x + 1): remainder %s"
          % (nm, prem(f, GOLD, 9) or [0], prem(f, CAT, 9) or [0]))

# ---------- integer linear algebra ----------
def hnf(rows):
    """row Hermite normal form of an integer matrix of full column rank; returns the n x n upper-triangular basis"""
    A = [r[:] for r in rows if any(r)]; n = len(A[0]); out = []
    for col in range(n):
        piv = [r for r in A if r[col] != 0]
        rest = [r for r in A if r[col] == 0]
        while len(piv) > 1:
            piv.sort(key=lambda r: abs(r[col]))
            p = piv[0]; new = [p]
            for r in piv[1:]:
                q = r[col] // p[col]
                r2 = [a - q * b for a, b in zip(r, p)]
                (new if r2[col] != 0 else rest).append(r2)
            piv = new
        p = piv[0]
        if p[col] < 0: p = [-a for a in p]
        out.append(p); A = rest
    for i in range(n):
        for k in range(i):
            q = out[k][i] // out[i][i]
            out[k] = [a - q * b for a, b in zip(out[k], out[i])]
    return out
def coords(y, B):
    """coordinates of y in the upper-triangular basis B (must be integral)"""
    y = [Fr(v) for v in y]; c = []
    for i, b in enumerate(B):
        ci = y[i] / b[i]; c.append(ci); y = [a - ci * bb for a, bb in zip(y, b)]
    assert all(v == 0 for v in y) and all(x.denominator == 1 for x in c), "not in lattice"
    return [int(x) for x in c]
def matmul(A, B): return [[sum(a * b for a, b in zip(r, col)) for col in zip(*B)] for r in A]
def quotient(G, poly, m=9):
    """L / (m L + p(G) L) for G acting on coordinate row vectors, p = poly (highest degree first)"""
    n = len(G); I = [[int(i == j) for j in range(n)] for i in range(n)]
    P = [[0] * n for _ in range(n)]; Gk = I
    for c in reversed(poly):
        P = [[a + c * b for a, b in zip(r1, r2)] for r1, r2 in zip(P, Gk)]; Gk = matmul(Gk, G)
    H = hnf(P + [[m * int(i == j) for j in range(n)] for i in range(n)])
    d = [H[i][i] for i in range(n)]
    def red(v):
        v = v[:]
        for i in range(n):
            q = v[i] // d[i]
            if q: v = [a - q * b for a, b in zip(v, H[i])]
        return tuple(v)
    size = 1
    for x in d: size *= x
    return H, d, size, red
def action_cycle_type(G, d, red, limit=200000):
    n = len(G)
    size = 1
    for x in d: size *= x
    if size > limit: return None
    ranges = [range(x) for x in d]
    seen, ct = set(), {}
    for v in itertools.product(*ranges):
        v = tuple(v)
        if v in seen: continue
        L, x = 0, v
        while True:
            seen.add(x); L += 1
            x = red([sum(x[i] * G[i][j] for i in range(n)) for j in range(n)])
            if x == v: break
        ct[L] = ct.get(L, 0) + 1
    return dict(sorted(ct.items(), reverse=True))
def three_times_size(d, red):
    return len({red([3 * a for a in v]) for v in itertools.product(*[range(x) for x in d])}) if eval('*'.join(map(str, d))) <= 200000 else None

# ---------- the Golay code, M24 generators, the Leech lattice ----------
P23, INF = 23, 23
QR = set((x * x) % P23 for x in range(1, P23))
rows = []; base = [1 if (i in QR or i == 0) else 0 for i in range(P23)]
for s in range(P23):
    v = [base[(i - s) % P23] for i in range(P23)]; rows.append(v + [sum(v) % 2])
rows.append([1] * 24)
gb = []
for r in rows:
    r = int(''.join(map(str, r)), 2)
    for b in gb: r = min(r, r ^ b)
    if r: gb.append(r)
words = [0]
for b in gb: words += [w ^ b for w in words]
WSET = set(words); bits = lambda w: [(w >> (23 - i)) & 1 for i in range(24)]
def mobius(a, b, c, d):
    out = []
    for x in range(24):
        if x == INF: y = INF if c == 0 else (a * pow(c, -1, P23)) % P23
        else:
            den = (c * x + d) % P23; y = INF if den == 0 else ((a * x + b) * pow(den, -1, P23)) % P23
        out.append(y)
    return out
def cycles(p):
    seen, out = set(), []
    for i in range(24):
        if i in seen: continue
        c, x = [], i
        while x not in seen: seen.add(x); c.append(x); x = p[x]
        out.append(c)
    return out
def signed_matrix(perm, sgn):
    """matrix P with x P = signed permutation: y[perm[i]] = sgn[i] x[i]"""
    P = [[0] * 24 for _ in range(24)]
    for i in range(24): P[i][perm[i]] = sgn[i]
    return P
# run 03's element: two 12-cycles, odd sign parity on both
g3 = mobius(0, 1, 22, 3); C1, C2 = cycles(g3)
e3 = next(w for w in words if sum(bits(w)[i] for i in C1) % 2 == 1 and sum(bits(w)[i] for i in C2) % 2 == 1)
P3 = signed_matrix(g3, [(-1) ** bits(e3)[i] for i in range(24)])
# run 04's element: cycle type (2,4,6,12), found by the same seeded random walk
inv9 = pow(9, -1, P23)
delta = [x if x in (0, INF) else ((x ** 3 * inv9) % P23 if x in QR else (9 * x ** 3) % P23) for x in range(24)]
gens = [mobius(1, 1, 0, 1), mobius(0, 22, 1, 0), delta]
def compose(p, q): return [q[p[i]] for i in range(24)]
random.seed(12); sigma = None
for _ in range(20000):
    p = list(range(24))
    for _ in range(random.randint(1, 12)): p = compose(p, random.choice(gens))
    if sorted(len(c) for c in cycles(p)) == [2, 4, 6, 12]: sigma = p; break
def mat_order(P):
    I = [[int(i == j) for j in range(len(P))] for i in range(len(P))]; X = P; k = 1
    while X != I: X = matmul(X, P); k += 1
    return k
P4 = None
for w in words:
    sg = [(-1) ** bits(w)[i] for i in range(24)]; M = signed_matrix(sigma, sg)
    M12 = M
    for _ in range(11): M12 = matmul(M12, M)
    if mat_order(M) == 24 and M12 != [[-int(i == j) for j in range(24)] for i in range(24)]: P4 = M; break
# Leech lattice (coordinates scaled by sqrt 8): generators
gensL = [[2 * b for b in bits(w)] for w in gb] + [[4 if k == 0 else (4 * s if k == j else 0) for k in range(24)] for j in range(1, 24) for s in (1, -1)] \
        + [[8] + [0] * 23, [-3] + [1] * 23]
BL = hnf(gensL)
gram_det_check = None
def det_frac(M):
    M = [[Fr(x) for x in r] for r in M]; n = len(M); d = Fr(1)
    for i in range(n):
        p = next(k for k in range(i, n) if M[k][i] != 0)
        if p != i: M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        for k in range(i + 1, n):
            f = M[k][i] / M[i][i]; M[k] = [a - f * b for a, b in zip(M[k], M[i])]
    return d
gram = [[Fr(sum(a * b for a, b in zip(r, s)), 8) for s in BL] for r in BL]
print("Q2 Leech lattice basis from generators: determinant of the Gram matrix (scaled by 1/8) = %s; minimal diagonal norm %s"
      % (det_frac(gram), min(gram[i][i] for i in range(24))))
def in_basis(P, B): return [coords([sum(b[i] * P[i][j] for i in range(24)) for j in range(24)], B) for b in B]
ZB = [[int(i == j) for j in range(24)] for i in range(24)]
for label, P in [("run 03 element (12^2, g^12 = -I)", P3), ("run 04 element (2.4.6.12, g^12 != -I)", P4)]:
    for lat, B in [("Leech", BL), ("Z^24", ZB)]:
        G = in_basis(P, B)
        H, d, size, red = quotient(G, GOLD)
        ct = action_cycle_type(G, d, red)
        t3 = three_times_size(d, red)
        print("Q2 %-38s on %-5s: |L/(9L + (g^2-g-1)L)| = %d = 81^%s | |3Q| = %s | cycle type of g: %s"
              % (label, lat, size, (lambda s: next((r for r in range(0, 13) if 81 ** r == s), 'not a power of 81'))(size), t3, ct))

# ---------- Q3: the 24-cell's order-12 symmetry on the Hurwitz quaternions ----------
def qmul(p, q):
    a1, b1, c1, d1 = p; a2, b2, c2, d2 = q
    return (a1*a2 - b1*b2 - c1*c2 - d1*d2, a1*b2 + b1*a2 + c1*d2 - d1*c2, a1*c2 - b1*d2 + c1*a2 + d1*b2, a1*d2 + b1*c2 - c1*b2 + d1*a2)
u = tuple(Fr(1, 2) for _ in range(4)); iq = (Fr(0), Fr(1), Fr(0), Fr(0))
HB = hnf([[1, 1, 1, 1], [2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 2]])     # doubled coordinates
def c_map(v2):                     # v2 in doubled coordinates
    q = tuple(Fr(x, 2) for x in v2); r = qmul(qmul(u, q), iq)
    return [int(2 * x) for x in r]
Cm = [coords(c_map(b), HB) for b in HB]
I4 = [[int(i == j) for j in range(4)] for i in range(4)]
C6 = Cm
for _ in range(5): C6 = matmul(C6, Cm)
print("Q3 24-cell symmetry c: x -> u x i (u = (1+i+j+k)/2) preserves the Hurwitz lattice; c^6 = -I: %s; order %d"
      % (C6 == [[-x for x in r] for r in I4], mat_order(Cm)))
for nm, pol in [("x^2 - 3x + 1 (the cat map, T^2)", CAT), ("x^2 - x - 1 (T)", GOLD)]:
    H, d, size, red = quotient(Cm, pol)
    print("Q3   quotient by (9, %s): size %d | cycle type of c: %s" % (nm, size, action_cycle_type(Cm, d, red)))
# reference: the family under T and under T^2, for comparison
def fam_ct(M):
    seen, ct = set(), {}
    for v in itertools.product(range(9), repeat=2):
        if v in seen: continue
        L, x = 0, v
        while True:
            seen.add(x); L += 1; x = ((M[0][0]*x[0] + M[1][0]*x[1]) % 9, (M[0][1]*x[0] + M[1][1]*x[1]) % 9)
            if x == v: break
        ct[L] = ct.get(L, 0) + 1
    return dict(sorted(ct.items(), reverse=True))
print("REF the family under T: %s | under T^2: %s" % (fam_ct([[0, 1], [1, 1]]), fam_ct([[1, 1], [1, 2]])))
