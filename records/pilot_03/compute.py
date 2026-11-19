#!/usr/bin/env python3
"""Physical pilot 03: the golden screen C11'' and the S4 test on SU(9)_1 x SU(9)_1, exactly as frozen in 00_freeze.txt.
Standard library only."""
import math
from collections import Counter
from fractions import Fraction
from itertools import product

def apply(A, x, m): return ((A[0][0] * x[0] + A[0][1] * x[1]) % m, (A[1][0] * x[0] + A[1][1] * x[1]) % m)
def mul(A, B, m):
    return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))
def mpow(A, n, m):
    R = ((1, 0), (0, 1))
    for _ in range(n): R = mul(R, A, m)
    return R
def census(A, m):
    seen, c = set(), Counter()
    for x in product(range(m), repeat=2):
        if x in seen: continue
        L, y = 0, x
        while y not in seen: seen.add(y); y = apply(A, y, m); L += 1
        c[L] += 1
    return dict(c)
def golden(A, m):
    A2 = mul(A, A, m); return A2 == (((A[0][0] + 1) % m, A[0][1]), (A[1][0], (A[1][1] + 1) % m))
FAM = {1: 1, 8: 1, 24: 3}
def screen(A, m):
    return golden(A, m) and m == 9 and census(A, m) == FAM and mpow(A, 12, m) == (((-1) % m, 0), (0, (-1) % m))

T = ((0, 1), (1, 1))
GL = [((a, b), (c, d)) for a, b, c, d in product(range(9), repeat=4) if ((a * d - b * c) % 3)]
def inv(A):
    a, b = A[0]; c, d = A[1]; di = pow((a * d - b * c) % 9, -1, 9)
    return ((d * di % 9, -b * di % 9), (-c * di % 9, a * di % 9))
conjT = {mul(mul(S, T, 9), inv(S), 9) for S in GL}

print("PILOT 03 -- PART A: golden screen C11'' (freeze SHA-256 in 02_freeze_sha256.txt)")
passing = [A for A in GL if screen(A, 9)]
print("  matrices of GL2(Z/9) passing: %d | conjugates of T: %d | passing set equals the conjugacy class of T: %s"
      % (len(passing), len(conjT), set(passing) == conjT))
nulls_pass = [A for A in GL if A not in conjT and screen(A, 9)]
print("  null matrices (not conjugate to T) passing: %d" % len(nulls_pass))
for m in (3, 6, 18, 27, 81):
    print("  golden law mod %2d: golden %s, census %s -> %s" % (m, golden(T, m), dict(sorted(census(T, m).items())) if m <= 27 else '(not the family census)', 'PASS' if screen(T, m) else 'FAIL'))
tr1 = [A for A in product(range(9), repeat=4)]
tr1 = [((a, b), (c, d)) for a, b, c, d in tr1 if (a + d) % 9 == 1 and (a * d - b * c) % 9 == 8]
print("  matrices mod 9 with trace 1 and determinant -1: %d | all conjugate to T: %s | all golden: %s"
      % (len(tr1), all(A in conjT for A in tr1), all(golden(A, 9) for A in tr1)))
calA = set(passing) == conjT and not nulls_pass and not any(screen(T, m) for m in (3, 6, 18, 27, 81))
print("  CALIBRATION (Part A): %s" % ('PASS' if calA else 'FAIL'))

print("PILOT 03 -- PART B: S4 on SU(9)_1 x SU(9)_1")
h = [Fraction(a * (9 - a), 18) for a in range(9)]
q = {x: (h[x[0]] + h[x[1]]) % 1 for x in product(range(9), repeat=2)}
iso = [A for A in GL if all(q[apply(A, x, 9)] == q[x] for x in q)]
anti = [A for A in GL if all(q[apply(A, x, 9)] == (-q[x]) % 1 for x in q)]
gold_anti = [A for A in anti if golden(A, 9)]
print("  isometries of the spins: %d | anti-isometries (time reversals): %d | golden anti-isometries: %d | T among them: %s"
      % (len(iso), len(anti), len(gold_anti), T in gold_anti))
classes, left = [], set(gold_anti)
while left:
    A = left.pop(); cl = {mul(mul(S, A, 9), inv(S), 9) for S in iso}; classes.append(cl & set(gold_anti)); left -= cl
print("  classes of golden anti-isometries under conjugation by the isometries: %d, of sizes %s" % (len(classes), sorted(len(c) for c in classes)))
golden_iso = [A for A in iso if golden(A, 9)]
print("  golden isometries: %d" % len(golden_iso))
S4 = len(classes) == 1
print("  S4 (the theory singles out T up to its own symmetries): %s" % ('MET' if S4 else 'NOT MET'))
# descriptive (not a criterion of the freeze): the golden anti-isometries in the anyon labels
print("  [descriptive] golden anti-isometries: %s | conjugates of T: %s | mutually inverse: %s"
      % (gold_anti, all(A in conjT for A in gold_anti), len(gold_anti) == 2 and mul(gold_anti[0], gold_anti[1], 9) == ((1, 0), (0, 1))))
