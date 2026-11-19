#!/usr/bin/env python3
"""structures.py -- E6's cubic norm kept by the law, the dashings of the E8 Adinkra, and the Structural Equivalence Tester
(Companion Part 221).

  S1 e6-cubic              the octonions on the Fano lines {i, i+1, i+3} mod 7 are alternative with multiplicative norm; on the Albert
                           algebra J3(O) the law and the shear, embedded as A + 1 and B + 1 and acting by X -> M X M^T, keep Freudenthal's cubic norm
  S2 adinkra-dashings      the E8 Adinkra: 64 edges, 112 two-color 4-cycles, the odd-dashing system of rank 45, 2^19 dashings, 16 classes under switching
  S3 equivalence-tester    for two linear laws on (Z/m)^2 the tester returns an invertible P with P M1 = M2 P, or a certificate that none exists
  S4 tester-extended       the tester for permutations (a conjugating relabeling or the cycle types) and for binary codes (a coordinate
                           permutation, or the weight enumerators, or an exhaustive search)

    python3 tools/structures.py --selftest
    python3 tools/structures.py --equiv a,b,c,d e,f,g,h m    the tester on M1 = [[a,b],[c,d]] and M2 = [[e,f],[g,h]] modulo m
    python3 tools/structures.py --perm 1,2,0,3 0,3,1,2        the tester on two permutations of 0..n-1
Standard library only; every value exact.
"""
import itertools, math, random, sys
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
# ---------- octonions on the Fano lines {i, i+1, i+3} mod 7 (as in A3); index 0 = real unit, 1..7 = e_0..e_6 ----------
lines = [(i % 7, (i + 1) % 7, (i + 3) % 7) for i in range(7)]
def umul(i, j):
    if i == j: return -1, None
    for a, b, c in lines:
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            if (i, j) == (x, y): return 1, z
            if (i, j) == (y, x): return -1, z
def omul(p, q):
    r = [0] * 8
    for i in range(8):
        if not p[i]: continue
        for j in range(8):
            if not q[j]: continue
            if i == 0: r[j] += p[i] * q[j]; continue
            if j == 0: r[i] += p[i] * q[j]; continue
            s, k = umul(i - 1, j - 1)
            if k is None: r[0] += s * p[i] * q[j]
            else: r[k + 1] += s * p[i] * q[j]
    return r
conj = lambda p: [p[0]] + [-x for x in p[1:]]
nrm = lambda p: sum(x * x for x in p)
re_ = lambda p: p[0]
# check alternativity and the norm on random integer octonions
rng = random.Random(5)
ro = lambda: [rng.randint(-3, 3) for _ in range(8)]
alt = all(omul(omul(p, p), q) == omul(p, omul(p, q)) for p, q in ((ro(), ro()) for _ in range(200)))
normmul = all(nrm(omul(p, q)) == nrm(p) * nrm(q) for p, q in ((ro(), ro()) for _ in range(200)))

# ---------- the Albert algebra: X = [[a, z, conj(y)], [conj(z), b, x], [y, conj(x), c]], a, b, c real; x, y, z octonions ----------
def albert_det(a, b, c, x, y, z):
    # Freudenthal's cubic norm: abc - a|x|^2 - b|y|^2 - c|z|^2 + 2 Re((x y) z)
    return a * b * c - a * nrm(x) - b * nrm(y) - c * nrm(z) + 2 * re_(omul(omul(x, y), z))
def to_mat(a, b, c, x, y, z):
    return [[[a] + [0] * 7, z, conj(y)], [conj(z), [b] + [0] * 7, x], [y, conj(x), [c] + [0] * 7]]
def from_mat(M):
    return M[0][0][0], M[1][1][0], M[2][2][0], M[1][2], M[2][0], M[0][1]
def act(Mreal, X):
    """X -> M X M^T for a real 3 x 3 matrix M (real entries commute and associate with octonions)"""
    n = 3
    add = lambda p, q: [u + v for u, v in zip(p, q)]
    sc = lambda s, p: [s * u for u in p]
    Y = [[[0] * 8 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            acc = [0] * 8
            for k in range(n):
                for l in range(n):
                    acc = add(acc, sc(Mreal[i][k] * Mreal[j][l], X[k][l]))
            Y[i][j] = acc
    return Y
def herm_ok(Y):
    return all(Y[i][i][1:] == [0] * 7 for i in range(3)) and Y[1][0] == conj(Y[0][1]) and Y[0][2] == conj(Y[2][0]) and Y[2][1] == conj(Y[1][2])
A3 = [[0, 1, 0], [1, 1, 0], [0, 0, 1]]; B3 = [[1, 0, 0], [3, 1, 0], [0, 0, 1]]
ok = True; tested = 0
for _ in range(300):
    a, b, c = rng.randint(-5, 5), rng.randint(-5, 5), rng.randint(-5, 5); x, y, z = ro(), ro(), ro()
    X = to_mat(a, b, c, x, y, z); d0 = albert_det(a, b, c, x, y, z)
    for M in (A3, B3):
        Y = act(M, X); ok = ok and herm_ok(Y) and albert_det(*from_mat(Y)) == d0; tested += 1
P('e6-cubic', alt and normmul and ok and tested == 600, 'the octonions on Omega42\'s Fano plane are alternative and their norm is multiplicative (200 pairs); on the Albert algebra J3(O), the law and the shear embedded as A + 1 and B + 1 act by X -> M X M^T,',
  'keep X Hermitian, and keep Freudenthal\'s cubic norm, the invariant of E6, on %d matrices: det M^2 = 1' % tested)

# ---------- the dashings of the E8 Adinkra ----------
G8 = [0b11111111, 0b00001111, 0b00110011, 0b01010101]
H8 = {0}
for g in G8: H8 |= {h ^ g for h in H8}
cls = {}; reps = []
for v in range(256):
    if v in cls: continue
    r = len(reps); reps.append(v)
    for c in H8: cls[v ^ c] = r
E = {}
for r, v in enumerate(reps):
    for i in range(8):
        u = cls[v ^ (1 << (7 - i))]; key = (min(r, u), max(r, u), i)
        E.setdefault(key, len(E))
# each 2-colored 4-cycle (v, i, j) must carry an odd number of dashed edges; solve over F2
rows = set()
for v in range(len(reps)):
    for i, j in itertools.combinations(range(8), 2):
        w1 = cls[reps[v] ^ (1 << (7 - i))]; w2 = cls[reps[v] ^ (1 << (7 - j))]; w3 = cls[reps[v] ^ (1 << (7 - i)) ^ (1 << (7 - j))]
        es = [E[(min(v, w1), max(v, w1), i)], E[(min(w1, w3), max(w1, w3), j)], E[(min(v, w2), max(v, w2), j)], E[(min(w2, w3), max(w2, w3), i)]]
        m = 0
        for e in es: m ^= 1 << e
        rows.add(m)
nE = len(E)
def rank_and_consistent(rows, nE):
    """Gaussian elimination over F2 of mask . x = 1 for every row"""
    piv = {}
    for m in rows:
        x, r = m, 1
        while x:
            hb = x.bit_length() - 1
            if hb in piv: px, pr = piv[hb]; x ^= px; r ^= pr
            else: piv[hb] = (x, r); break
        if not x and r: return len(piv), False
    return len(piv), True
rk, cons = rank_and_consistent(rows, nE)
sols = nE - rk if cons else None
V = len(reps)
P('adinkra-dashings', cons and nE == 64 and len(rows) == 112 and rk == 45 and V == 16, 'the E8 Adinkra has', nE, 'edges and', len(rows), 'two-colored 4-cycles; the condition that each 4-cycle carry an odd number of dashed edges is consistent, of rank', rk,
  '| admissible dashings: 2^%d; vertex switchings act as 2^%d (16 vertices, one relation), so the dashings fall into 2^%d classes' % (sols, V - 1, sols - (V - 1)))

# ---------- the Structural Equivalence Tester ----------
def cycle_type(M, m):
    """the cycle type of s -> M s on the m^2 states"""
    seen = set(); ct = []
    for s in itertools.product(range(m), repeat=2):
        if s in seen: continue
        n = 0; t = s
        while t not in seen:
            seen.add(t); t = ((M[0][0] * t[0] + M[0][1] * t[1]) % m, (M[1][0] * t[0] + M[1][1] * t[1]) % m); n += 1
        ct.append(n)
    return sorted(ct)
def equivalence(M1, M2, m):
    """(P, None) with P invertible modulo m and P M1 = M2 P, or (None, certificate)"""
    t1, t2 = (M1[0][0] + M1[1][1]) % m, (M2[0][0] + M2[1][1]) % m
    d1, d2 = (M1[0][0] * M1[1][1] - M1[0][1] * M1[1][0]) % m, (M2[0][0] * M2[1][1] - M2[0][1] * M2[1][0]) % m
    if t1 != t2: return None, 'trace %d against %d' % (t1, t2)
    if d1 != d2: return None, 'determinant %d against %d' % (d1, d2)
    if cycle_type(M1, m) != cycle_type(M2, m): return None, 'cycle types on the %d states differ' % (m * m)
    for a, b, c, d in itertools.product(range(m), repeat=4):
        if math.gcd((a * d - b * c) % m, m) != 1: continue
        if all((([[a, b], [c, d]][i][0] * M1[0][j] + [[a, b], [c, d]][i][1] * M1[1][j]) - (M2[i][0] * [[a, b], [c, d]][0][j] + M2[i][1] * [[a, b], [c, d]][1][j])) % m == 0
               for i in range(2) for j in range(2)):
            return [[a, b], [c, d]], None
    return None, 'exhaustive search of GL2(Z/%d)' % m
A_ = [[0, 1], [1, 1]]
BAB = [[(sum([[1, 0], [3, 1]][i][k] * A_[k][l] * [[1, 0], [6, 1]][l][j] for k in range(2) for l in range(2))) % 9 for j in range(2)] for i in range(2)]
cases = [('the swap [[1,1],[1,0]]', [[1, 1], [1, 0]], True), ('the twin [[0,1],[1,7]]', [[0, 1], [1, 7]], False), ('B A B^-1', BAB, True), ('A^5 = [[3,5],[5,8]]', [[3, 5], [5, 8]], False)]
rows = []; okt = True
for name, M2, exp in cases:
    Pm, cert = equivalence(A_, M2, 9)
    okt = okt and ((Pm is not None) == exp)
    if Pm is not None:
        okt = okt and all((sum(Pm[i][k] * A_[k][j] for k in range(2)) - sum(M2[i][k] * Pm[k][j] for k in range(2))) % 9 == 0 for i in range(2) for j in range(2))
    rows.append('A vs %s: %s' % (name, ('map P = %s' % Pm) if Pm else ('none, certificate: ' + cert)))
P('equivalence-tester', okt, 'the Structural Equivalence Tester on the 81 states returns a map or a certificate of none: ' + ' | '.join(rows))

# ---------- the tester extended: permutations and codes ----------
def perm_equivalence(p, q):
    """(r, None) with r p r^-1 = q for permutations p, q of range(n), or (None, certificate)"""
    def cycles(s):
        seen, cs = set(), []
        for i in range(len(s)):
            if i in seen: continue
            c = [i]; seen.add(i); j = s[i]
            while j != i: c.append(j); seen.add(j); j = s[j]
            cs.append(c)
        return sorted(cs, key=len)
    cp, cq = cycles(p), cycles(q)
    if [len(c) for c in cp] != [len(c) for c in cq]: return None, 'cycle types %s against %s' % ([len(c) for c in cp], [len(c) for c in cq])
    r = [None] * len(p)
    for a, b in zip(cp, cq):
        for x, y in zip(a, b): r[x] = y
    return r, None
def weight_enum(C):
    from collections import Counter
    return sorted(Counter(sum(w) for w in C).items())
def code_equivalence(C1, C2):
    """(sigma, None) with sigma a permutation of the coordinates taking the binary code C1 onto C2, or (None, certificate)"""
    C1, C2 = set(map(tuple, C1)), set(map(tuple, C2))
    if len(C1) != len(C2): return None, 'sizes %d against %d' % (len(C1), len(C2))
    if weight_enum(C1) != weight_enum(C2): return None, 'weight enumerators %s against %s' % (weight_enum(C1), weight_enum(C2))
    n = len(next(iter(C1)))
    for sg in itertools.permutations(range(n)):
        if {tuple(w[sg[i]] for i in range(n)) for w in C1} == C2: return list(sg), None
    return None, 'exhaustive search of the %d coordinate permutations' % math.factorial(n)
def span(gens, n):
    C = {tuple([0] * n)}
    for g in gens:
        C |= {tuple((a + b) % 2 for a, b in zip(c, g)) for c in C}
    return C
bits = lambda v, n: [(v >> (n - 1 - i)) & 1 for i in range(n)]
H_adinkra = span([bits(g, 8) for g in (0b11111111, 0b00001111, 0b00110011, 0b01010101)], 8)
# the extended Hamming code as the extended quadratic-residue code of length 8 (MF-77): residues mod 7 are 1, 2, 4
qr = [1 if i in (1, 2, 4) else 0 for i in range(7)]
H_qr = span([[qr[(j - s) % 7] for j in range(7)] + [1] for s in range(7)] + [[1] * 8], 8)
sig, cert = code_equivalence(H_adinkra, H_qr)
even8 = span([[1, 1, 0, 0, 0, 0, 0, 0], [0, 0, 1, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 1, 0, 0], [0, 0, 0, 0, 0, 0, 1, 1]], 8)
sig2, cert2 = code_equivalence(H_adinkra, even8)
A9 = [((0 * a + 1 * b) % 9) * 9 + ((a + b) % 9) for a in range(9) for b in range(9)]                 # the law as a permutation of the 81 states, s = 9a + b
SW = [((a + b) % 9) * 9 + (a % 9) for a in range(9) for b in range(9)]                               # the swap [[1,1],[1,0]]
A2 = [A9[A9[s]] for s in range(81)]
r, c1 = perm_equivalence(A9, SW); r2, c2 = perm_equivalence(A9, A2)
okp = r is not None and all(r[A9[s]] == SW[r[s]] for s in range(81)) and r2 is None
okc = sig is not None and cert2 is not None and 'weight' in cert2
P('tester-extended', okp and okc, 'the tester extended to permutations and codes: the law and the swap as permutations of the 81 states are conjugate by a relabeling, and the law and A^2 are not (%s);' % c2,
  'the code of the E8 Adinkra and the extended quadratic-residue code of MF-77 are equivalent by the coordinate permutation %s, and the Adinkra code and the pair-repetition code [8,4,2] are not (%s)' % (sig, cert2))

KEYS = {k: k for k in ('e6-cubic', 'adinkra-dashings', 'equivalence-tester', 'tester-extended')}
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('STRUCTURES SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if len(a) == 4 and a[0] == '--equiv':
        M1 = [int(x) for x in a[1].split(',')]; M2 = [int(x) for x in a[2].split(',')]; m = int(a[3])
        Pm, cert = equivalence([M1[:2], M1[2:]], [M2[:2], M2[2:]], m)
        print('EQUIVALENT: P = %s' % Pm if Pm else 'NOT EQUIVALENT: %s' % cert); sys.exit(0)
    if len(a) == 3 and a[0] == '--perm':
        r, cert = perm_equivalence([int(x) for x in a[1].split(',')], [int(x) for x in a[2].split(',')])
        print('EQUIVALENT: r = %s' % r if r else 'NOT EQUIVALENT: %s' % cert); sys.exit(0)
    print(__doc__); sys.exit(2)
