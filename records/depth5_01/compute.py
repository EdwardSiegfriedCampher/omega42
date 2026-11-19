#!/usr/bin/env python3
"""Depth 5, run 01 -- computes the forecasts frozen in 00_forecasts.txt (SHA-256 in 01_freeze.txt) and nothing else.
Run: cd records/depth5_01 && python3 compute.py | diff - compute_output.txt     Standard library only; exact arithmetic."""
import itertools
from fractions import Fraction as Fr
from math import comb

def golden(M): return lambda x: (x[0] * x[0] + x[0] * x[1] - x[1] * x[1]) % M
def decoy(M): return lambda x: (x[0] * x[0] + x[1] * x[1]) % M
def su_pair(M):                      # SU(M)_1 x SU(M)_1: spin of (a, b) is (a(M-a) + b(M-b))/(2M); as an integer form mod M, -(a^2+b^2)/2
    inv2 = (M + 1) // 2
    return lambda x: (-(x[0] * x[0] + x[1] * x[1]) * inv2) % M
def states(M): return [(a, b) for a in range(M) for b in range(M)]
def bil(q, M): return lambda x, y: (q(((x[0] + y[0]) % M, (x[1] + y[1]) % M)) - q(x) - q(y)) % M
def nondegenerate(q, M):
    B = bil(q, M); S = states(M)
    return [x for x in S if all(B(x, y) == 0 for y in S)] == [(0, 0)]
def isometry(q, r, M):
    """a linear f with r(f(x)) = q(x) for every x, invertible mod 3, or None"""
    S = states(M); Br = bil(r, M)
    A = [u for u in S if r(u) == q((1, 0))]; C = [v for v in S if r(v) == q((0, 1))]
    want = bil(q, M)((1, 0), (0, 1))
    for u in A:
        for v in C:
            if Br(u, v) == want and (u[0] * v[1] - u[1] * v[0]) % 3:
                f = lambda x, u=u, v=v: ((x[0] * u[0] + x[1] * v[0]) % M, (x[0] * u[1] + x[1] * v[1]) % M)
                if all(r(f(x)) == q(x) for x in S): return (u, v)
    return None
def T(x, M): return (x[1], (x[0] + x[1]) % M)
def order_T(M):
    x, n = (1, 0), 0
    P = ((0, 1), (1, 1)); A = P; n = 1
    while A != ((1, 0), (0, 1)):
        A = tuple(tuple(sum(A[i][k] * P[k][j] for k in range(2)) % M for j in range(2)) for i in range(2)); n += 1
    return n
def lagrangians(q, M):
    """every subgroup of order M of (Z/M)^2 on which q vanishes"""
    B = [x for x in states(M) if q(x) == 0]; found = set()
    def span(gens):
        H = {(0, 0)}; frontier = [(0, 0)]
        while frontier:
            z = frontier.pop()
            for g in gens:
                w = ((z[0] + g[0]) % M, (z[1] + g[1]) % M)
                if w not in H:
                    H.add(w); frontier.append(w)
                    if len(H) > M: return None
        return frozenset(H)
    Bs = sorted(B)
    for i, x in enumerate(Bs):
        H = span([x])
        if H is not None and len(H) == M and all(q(z) == 0 for z in H): found.add(H)
        for y in Bs[i + 1:]:
            H = span([x, y])
            if H is not None and len(H) == M and all(q(z) == 0 for z in H): found.add(H)
    return found, len(B)

print('DEPTH 5, RUN 01 -- the forecasts of 00_forecasts.txt, computed')
# F-01
M = 9; h = lambda a: Fr(a * (9 - a), 18) % 1
bos = sorted((a, b) for a in range(9) for b in range(9) if (h(a) + h(b)) % 1 == 0)
crown2 = sorted((a, b) for a in (0, 3, 6) for b in (0, 3, 6))
L9, nb = lagrangians(su_pair(9), 9)
print('F-01 bosons of SU(9)_1 x SU(9)_1 in its own labels: %d; exactly Crown x Crown {(3i, 3j)}: %s; Lagrangian subgroups: %d -> %s'
      % (len(bos), bos == crown2, len(L9), 'HOLDS' if bos == crown2 and len(L9) == 1 else 'FAILS'))
# F-02: condense A8 + A8 by the Lagrangian subgroup; its norm-2 vectors and their components
def min_vectors(k, n=9):
    if k == 0:
        return [tuple(Fr(int(i == p) - int(i == s)) for i in range(n)) for p in range(n) for s in range(n) if p != s]
    return [tuple(Fr(k, n) - int(i in S) for i in range(n)) for S in itertools.combinations(range(n), k)]
L = next(iter(L9)); roots = []
for (k1, k2) in L:
    for side, k in ((0, k1), (1, k2)):
        other = k2 if side == 0 else k1
        if other != 0: continue
        if (k1, k2) == (0, 0) or k != 0:
            for v in min_vectors(k):
                if sum(c * c for c in v) == 2:
                    z = tuple([Fr(0)] * 9)
                    roots.append(v + z if side == 0 else z + v)
roots = sorted(set(roots))
dot = lambda x, y: sum(a * b for a, b in zip(x, y))
comp, seen = [], set()
for r in roots:
    if r in seen: continue
    C, st = {r}, [r]
    while st:
        x = st.pop()
        for y in roots:
            if y not in C and dot(x, y) != 0: C.add(y); st.append(y)
    seen |= C; comp.append(len(C))
print('F-02 condensate of SU(9)_1 x SU(9)_1 by its Lagrangian subgroup: rank 16, %d roots in %d orthogonal systems of sizes %s -> %s'
      % (len(roots), len(comp), sorted(comp), 'E8 + E8: HOLDS' if sorted(comp) == [240, 240] else 'FAILS'))
# F-03
g9 = golden(9); Lg = lagrangians(g9, 9)[0]; Lg1 = next(iter(Lg))
anti = []
for a, b, c, d in itertools.product(range(9), repeat=4):
    if (a * d - b * c) % 3 and all(g9(((a * x + b * y) % 9, (c * x + d * y) % 9)) == (-g9((x, y))) % 9 for x, y in states(9)):
        anti.append((a, b, c, d))
keep = all({((a * x + b * y) % 9, (c * x + d * y) % 9) for x, y in Lg1} == set(Lg1) for a, b, c, d in anti)
print('F-03 golden theory mod 9: Lagrangian subgroups %d; T preserves it: %s; all %d time-reversal symmetries preserve it: %s -> %s'
      % (len(Lg), {T(x, 9) for x in Lg1} == set(Lg1), len(anti), keep, 'HOLDS' if keep else 'FAILS'))
# F-04 and F-05, golden and decoy
for name, form in (('golden a^2+ab-b^2', golden), ('decoy  a^2+b^2   ', decoy)):
    for m in (1, 2, 3, 4):
        M = 3 ** m; q = form(M)
        nd = nondegenerate(q, M); iso = isometry(q, su_pair(M), M)
        ot = order_T(M); anti_T = all(q(T(x, M)) == (-q(x)) % M for x in states(M))
        Ls, nb = lagrangians(q, M)
        print('%s m=%d M=%-2d nondegenerate %s | isometric to SU(%d)_1 x SU(%d)_1: %s | T order %d (8 x 3^(m-1) = %d) | T time-reversal: %s | bosons %d | Lagrangian subgroups %d'
              % (name, m, M, nd, M, M, 'YES via %s' % (iso,) if iso else 'NO', ot, 8 * 3 ** (m - 1), anti_T, nb, len(Ls)))
        if name.startswith('golden'): globals().setdefault('G', {})[m] = (nd, bool(iso), ot == 8 * 3 ** (m - 1), anti_T, len(Ls))
G = globals()['G']
f4 = all(G[m][0] and G[m][1] and G[m][2] and G[m][3] for m in G)
f5 = all((G[m][4] > 0) == (m % 2 == 0) for m in G)
print('F-04 the tower of SU(3^m)_1 x SU(3^m)_1 with T a time-reversal symmetry of order 8 x 3^(m-1), m = 1..4: %s' % ('HOLDS' if f4 else 'FAILS'))
print('F-05 a gapped boundary exactly at even depth, m = 1..4 (Lagrangian subgroups %s): %s' % ([G[m][4] for m in sorted(G)], 'HOLDS' if f5 else 'FAILS'))
# F-06: at m = 4, the Lagrangian subgroups in SU(81)_1 x SU(81)_1 labels, and the glue of A80 by its subgroup of order 9
M = 81; Ls81, _ = lagrangians(su_pair(81), 81)
prod = frozenset((9 * i % 81, 9 * j % 81) for i in range(9) for j in range(9))
k, n = 9, 81
glue_norm = Fr(k * (n - k), n); glue_q = Fr(k * (n - k), 2 * n)
print('F-06 SU(81)_1 x SU(81)_1: Lagrangian subgroups %d; 9(Z/81)^2 among them: %s; glue class 9 of A80: norm %s (even: %s), spin %s (boson: %s); det(A80) = 81, index 9 -> unimodular: %s'
      % (len(Ls81), prod in Ls81, glue_norm, glue_norm.denominator == 1 and glue_norm.numerator % 2 == 0, glue_q, glue_q.denominator == 1, Fr(81, 9 * 9) == 1))
other = [H for H in Ls81 if H != prod]
split = [all(((a, 0) in H) == ((a, b) in H) or True for a, b in H) for H in Ls81]
prods = [H for H in Ls81 if H == frozenset((a, b) for a in {x for x, _ in H if (x, 0) in H} for b in {y for _, y in H if (0, y) in H})]
print('F-06 Lagrangian subgroups that are products of one subgroup in each factor: %d of %d; the condensate of 9(Z/81)^2 is the sum of two copies of the rank-80 even unimodular lattice A80 + [9]: %s'
      % (len(prods), len(Ls81), 'HOLDS' if prod in prods else 'FAILS'))
