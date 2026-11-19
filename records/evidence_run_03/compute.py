#!/usr/bin/env python3
"""Evidence run 03 -- computations (standard library + numpy). Run: python3 compute.py"""
import itertools, cmath, math, random
import numpy as np

# ---------- Q1: the golden-field question ----------
def mmul(P, Q, m): return tuple(tuple(sum(P[i][t]*Q[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
def order(M, m):
    I = ((1 % m, 0), (0, 1 % m)); k, X = 1, M
    while X != I: X = mmul(X, M, m); k += 1
    return k
def act(M, v, m): return ((M[0][0]*v[0] + M[0][1]*v[1]) % m, (M[1][0]*v[0] + M[1][1]*v[1]) % m)
def cycle_type(M, m):
    seen, out = set(), []
    for v in itertools.product(range(m), repeat=2):
        if v in seen: continue
        c, x = 0, v
        while True:
            seen.add(x); c += 1; x = act(M, x, m)
            if x == v: break
        out.append(c)
    return sorted(out, reverse=True)
N = 9
neg = lambda M, m: tuple(tuple((-x) % m for x in r) for r in M)
T = ((0, 1), (1, 1)); A = mmul(T, T, N)
for name, M in [('T', T), ('-T', neg(T, N)), ('A = T^2', A), ('-A', neg(A, N))]:
    print("Q1 %-8s trace %d det %d | order mod 9 %2d | cycle type on 81 states %s" % (
        name, (M[0][0] + M[1][1]) % N, (M[0][0]*M[1][1] - M[0][1]*M[1][0]) % N, order(M, N), cycle_type(M, N)))
# is -T conjugate to T in GL(2, Z/9)? (traces differ: 1 vs 8, so no; checked by search for completeness)
GL = [((a, b), (c, d)) for a, b, c, d in itertools.product(range(N), repeat=4) if math.gcd((a*d - b*c) % N, N) == 1]
def inv(P, m):
    a, b = P[0]; c, d = P[1]; di = pow((a*d - b*c) % m, -1, m)
    return ((d*di % m, (-b)*di % m), ((-c)*di % m, a*di % m))
conj = any(mmul(mmul(P, T, N), inv(P, N), N) == neg(T, N) for P in GL)
print("Q1 -T conjugate to T in GL(2,Z/9): %s (|GL(2,Z/9)| = %d)" % (conj, len(GL)))
# every matrix in GL(2,Z/9) of order 24 whose 81-state cycle type equals T's
same = [P for P in GL if order(P, N) == 24 and cycle_type(P, N) == cycle_type(T, N)]
traces = sorted(set((P[0][0] + P[1][1]) % N for P in same)); dets = sorted(set((P[0][0]*P[1][1] - P[0][1]*P[1][0]) % N for P in same))
print("Q1 matrices of GL(2,Z/9) with T's cycle type (24,24,24,8,1): %d | their traces %s | their determinants %s" % (len(same), traces, dets))
golden = [P for P in same if ((P[0][0] + P[1][1]) % N, (P[0][0]*P[1][1] - P[0][1]*P[1][0]) % N) in [(1, 8), (8, 8)]]
print("Q1 of these, with the golden characteristic polynomial x^2 -+ x - 1 (trace +-1, det -1): %d" % len(golden))
def mpow(M, k, m):
    X = ((1, 0), (0, 1))
    for _ in range(k): X = mmul(X, M, m)
    return X
print("Q1 -T = T^13 (so -T generates the same cyclic group as T): %s | conjugacy class sizes of T and -T: %d and %d"
      % (mpow(T, 13, N) == neg(T, N), sum(1 for P in golden if (P[0][0] + P[1][1]) % N == 1), sum(1 for P in golden if (P[0][0] + P[1][1]) % N == 8)))
print("Q1 order of A modulo 161: %d | Pisano period of 7: %d, of 23: %d" % (order(mmul(T, T, 161), 161), order(T, 7), order(T, 23)))

# ---------- Q2: spectrum of V^2 for odd N ----------
def V2_spectrum(n):
    w = cmath.exp(2j * math.pi / n); inv2 = pow(2, -1, n)
    X = np.roll(np.eye(n), 1, axis=0); Z = np.diag([w ** j for j in range(n)])
    def D(p, q): return np.linalg.matrix_power(X, p % n) @ np.linalg.matrix_power(Z, q % n)
    def proj_eq(P_, Q_):
        k = np.argmax(abs(Q_)); ph = P_.flat[k] / Q_.flat[k]
        return abs(abs(ph) - 1) < 1e-8 and np.allclose(P_, ph * Q_, atol=1e-8)
    F = np.array([[w ** (j * k) for k in range(n)] for j in range(n)]) / math.sqrt(n)
    Sh = np.diag([w ** ((inv2 * j * j) % n) for j in range(n)])
    def implemented(U):
        Ui = np.linalg.inv(U)
        for a, b, c, d in itertools.product(range(n), repeat=4):
            if (a*d - b*c) % n != 1: continue
            if proj_eq(U @ D(1, 0) @ Ui, D(a, c)) and proj_eq(U @ D(0, 1) @ Ui, D(b, d)): return ((a, b), (c, d))
    gF, gS = implemented(F), implemented(Sh)
    target = mmul(((0, 1), (1, 1)), ((1, 0), (0, n - 1)), n)
    for L in range(1, 9):
        for word in itertools.product('FS', repeat=L):
            P_ = ((1, 0), (0, 1)); W = np.eye(n, dtype=complex)
            for g in word:
                P_ = mmul(P_, gF if g == 'F' else gS, n); W = W @ (F if g == 'F' else Sh)
            if P_ == target:
                V2 = W @ np.conj(W)
                o = order(mmul(((0, 1), (1, 1)), ((0, 1), (1, 1)), n), n)
                ks = sorted(int(round(np.angle(e) / (2 * math.pi / o))) % o for e in np.linalg.eigvals(V2))
                return o, ks
for n in range(3, 28, 2):
    o, ks = V2_spectrum(n)
    present = sorted(set(ks)); missing = [k for k in range(o) if k not in present]
    mult = max(ks.count(k) for k in present)
    only3 = missing == [k for k in range(o) if k % 3 == 0 and k != 0] if o % 3 == 0 else False
    print("Q2 N = %2d | ord(A) = %2d | eigenvalue exponents k (of exp(2 pi i k / ord)) present: %s | missing: %s | max multiplicity %d | missing exactly the nonzero multiples of 3: %s"
          % (n, o, present, missing, mult, only3))

# ---------- Q3: Leech lattice ----------
P23 = 23; INF = 23                     # points 0..22 and infinity (index 23)
QR = sorted(set((x * x) % P23 for x in range(1, P23)))
def golay():
    base = [1 if (i in QR or i == 0) else 0 for i in range(P23)]   # candidate generator; tested below
    vecs = []
    for s in range(P23):
        v = [base[(i - s) % P23] for i in range(P23)]
        vecs.append(v + [sum(v) % 2])                             # extend by parity at infinity
    vecs.append([1] * 24)                                         # the all-ones word
    return vecs
def span(rows):
    basis = []
    for r in rows:
        r = int(''.join(map(str, r)), 2)
        for b in basis: r = min(r, r ^ b)
        if r: basis.append(r)
    return basis
def all_words(basis):
    words = [0]
    for b in basis: words += [w ^ b for w in words]
    return words
B = span(golay())
words = all_words(B)
wts = sorted(set(bin(w).count('1') for w in words))
print("Q3 extended QR code of length 24: dimension %d, %d codewords, weights %s" % (len(B), len(words), wts))
WSET = set(words)
def bits(w): return [(w >> (23 - i)) & 1 for i in range(24)]
def frombits(b): return int(''.join(map(str, b)), 2)
def mobius(a, b, c, d):
    perm = []
    for x in range(24):
        if x == INF: y = INF if c == 0 else (a * pow(c, -1, P23)) % P23
        else:
            den = (c * x + d) % P23
            y = INF if den == 0 else ((a * x + b) * pow(den, -1, P23)) % P23
        perm.append(y)
    return perm
def perm_word(w, perm):
    b = bits(w); out = [0] * 24
    for i in range(24): out[perm[i]] = b[i]
    return frombits(out)
def perm_order(perm):
    k, cur = 1, perm[:]
    while cur != list(range(24)): cur = [perm[c] for c in cur]; k += 1
    return k
def cycles(perm):
    seen, out = set(), []
    for i in range(24):
        if i in seen: continue
        c, x = [], i
        while x not in seen: seen.add(x); c.append(x); x = perm[x]
        out.append(c)
    return out
g = None
for a, b, c, d in itertools.product(range(P23), repeat=4):
    if (a * d - b * c) % P23 != 1: continue
    pm = mobius(a, b, c, d)
    if perm_order(pm) == 12 and sorted(len(c_) for c_ in cycles(pm)) == [12, 12]:
        g = pm; gm = (a, b, c, d); break
print("Q3 element of PSL(2,23): x -> (%dx+%d)/(%dx+%d), order 12, cycle type on 24 points %s" % (gm + (sorted(len(c_) for c_ in cycles(g)),)))
print("Q3 it preserves the Golay code: %s" % all(perm_word(w, g) in WSET for w in B))
C1, C2 = cycles(g)
eps = next(w for w in words if sum(bits(w)[i] for i in C1) % 2 == 1 and sum(bits(w)[i] for i in C2) % 2 == 1)
sgn = [(-1) ** bits(eps)[i] for i in range(24)]
print("Q3 Golay sign change with odd parity on both 12-cycles: weight %d" % bin(eps).count('1'))
def apply(x):                      # signed permutation: x -> sigma(eps * x)
    y = [0] * 24
    for i in range(24): y[g[i]] = sgn[i] * x[i]
    return y
def in_leech(x):                   # Conway's definition, coordinates scaled by sqrt 8
    m = x[0] % 2
    if any(v % 2 != m for v in x): return False
    if sum(x) % 8 != (4 * m) % 8: return False
    if m == 0:
        return frombits([1 if v % 4 == 2 else 0 for v in x]) in WSET
    return frombits([1 if v % 4 == 3 else 0 for v in x]) in WSET or frombits([1 if v % 4 == 1 else 0 for v in x]) in WSET
random.seed(24)
def random_leech():
    m = random.randint(0, 1)
    while True:
        if m == 0:
            c = bits(random.choice(words)); x = [2 * ci + 4 * random.randint(-2, 2) for ci in c]
        else:
            c = bits(random.choice(words)); x = [1 + 2 * ci + 4 * random.randint(-2, 2) for ci in c]
        # adjust the sum condition by moving one coordinate by 8 where needed
        target = (4 * m) % 8
        for i in range(24):
            if sum(x) % 8 == target: break
            x[0] += 4
        if in_leech(x): return x
sample = [random_leech() for _ in range(3000)]
print("Q3 sample of %d Leech vectors (by definition) mapped into the Leech lattice by the signed permutation: %s"
      % (len(sample), all(in_leech(apply(x)) for x in sample)))
def order_signed():
    k, x = 1, list(range(1, 25))
    y = apply(x)
    while y != x: y = apply(y); k += 1
    return k
def apply_with(perm, signs, x):
    y = [0] * 24
    for i in range(24): y[perm[i]] = signs[i] * x[i]
    return y
random.seed(7)
fails = 0
for _ in range(20):
    rp = list(range(24)); random.shuffle(rp)
    if not all(in_leech(apply_with(rp, sgn, x)) for x in sample[:300]): fails += 1
print("Q3 control: random permutations of the coordinates (same signs) rejected by the membership test: %d of 20" % fails)
print("Q3 order of the signed permutation: %d" % order_signed())
frame = [tuple(8 * s if j == i else 0 for j in range(24)) for i in range(24) for s in (1, -1)]
print("Q3 the 48 frame vectors +-8e_i are Leech vectors: %s" % all(in_leech(list(v)) for v in frame))
seen, orbs = set(), []
for v in frame:
    if v in seen: continue
    o, x = [], v
    while x not in seen: seen.add(x); o.append(x); x = tuple(apply(list(x)))
    orbs.append(o)
half = all(tuple(-c for c in o[0]) == o[12] for o in orbs)
print("Q3 orbits on the frame: %s | step 12 sends each frame vector to its negative: %s" % ([len(o) for o in orbs], half))
# null control: Z^24 has the same signed permutation (any sign pattern works there)
print("Q3 NULL (Z^24): the same signed permutation preserves Z^24 trivially, with the same two 24-cycles on +-e_i: True by construction")
