#!/usr/bin/env python3
"""Physical pilot 04: S5 for the anyon candidate, exactly as frozen in 00_freeze.txt. Standard library only."""
from itertools import product
def apply(A, x): return ((A[0][0] * x[0] + A[0][1] * x[1]) % 9, (A[1][0] * x[0] + A[1][1] * x[1]) % 9)
def mul(A, B): return tuple(tuple(sum(A[i][k] * B[k][j] for k in range(2)) % 9 for j in range(2)) for i in range(2))
GL = [((a, b), (c, d)) for a, b, c, d in product(range(9), repeat=4) if (a * d - b * c) % 3]
golden = [A for A in GL if mul(A, A) == (((A[0][0] + 1) % 9, A[0][1]), (A[1][0], (A[1][1] + 1) % 9))]
V = list(product(range(9), repeat=2))
def table(f): return tuple(f[2] * 0 + (f[0] * x[0] * x[0] + f[1] * x[0] * x[1] + f[2] * x[1] * x[1]) % 9 for x in V)
forms = [f for f in product(range(9), repeat=3) if (f[1] * f[1] - 4 * f[0] * f[2]) % 3]
tab = {f: table(f) for f in forms}
idx = {x: i for i, x in enumerate(V)}
def transform(t, A): return tuple(t[idx[apply(A, x)]] for x in V)
classes, seen = [], set()
for f in forms:
    t = tab[f]
    if t in seen: continue
    orbit = {transform(t, A) for A in GL}; seen |= orbit; classes.append(orbit)
def has_golden_anti(t):
    return sum(1 for A in golden if all(t[idx[apply(A, x)]] == (-t[i]) % 9 for i, x in enumerate(V)))
su9 = table((4, 0, 4)); toric = table((0, 1, 0)); fam = table((1, 1, 8))
print("PILOT 04 -- S5 on the label group Z/9 x Z/9 (freeze SHA-256 in 02_freeze_sha256.txt)")
print("  golden matrices in GL2(Z/9): %d | nondegenerate forms: %d | theories (classes under relabelling): %d" % (len(golden), len(forms), len(classes)))
with_prop = []
for k, cl in enumerate(classes):
    rep = next(iter(cl)); n = has_golden_anti(rep)
    tags = [nm for nm, t in (('SU(9)_1 x SU(9)_1', su9), ('Z9 toric code', toric), ('family norm a^2+ab-b^2', fam)) if t in cl]
    print("  class %d: %3d forms | golden anti-isometries of a representative: %d %s" % (k + 1, len(cl), n, tags))
    if n: with_prop.append(k)
su9_class = next(k for k, cl in enumerate(classes) if su9 in cl)
S5 = su9_class in with_prop and len(with_prop) <= 2
print("  classes with a golden anti-isometry: %d of %d (SU(9)_1 x SU(9)_1 among them: %s)" % (len(with_prop), len(classes), su9_class in with_prop))
print("  S5: %s" % ('MET' if S5 else 'NOT MET'))
