#!/usr/bin/env python3
"""bridges.py -- Omega42 and the exceptional structures of conventional mathematics (Companion Part 217; MF-73 to MF-79; F211, APE-473).

  wheel    3Z[phi]/9Z[phi] is the field F9, and the law (multiplication by phi) generates its 8 units: the Wheel is F9*
  e8       the 120 unit icosians span a Z[phi]-module of rank 4 (Z-rank 8); with 2 Tr((phi/sqrt5)<x, y>) it is even, unimodular,
           with 240 roots: E8; the law is an integer 8x8 matrix with M^2 = M + I, and on E8/9E8 its census is
           1 + 820 x 8 + 1,793,340 x 24 -- Omega42's census four times over
  coxeter  C(x) = l x r (l of order 10, r of order 3) is a Coxeter element of E8 (characteristic polynomial Phi_30) and
           I + C^12 + C^-12 = phi: the law is a polynomial in E8's Coxeter element
  hamming  <A^2, B> mod 7 acts on the projective line over F7 as PSL2(F7) and keeps the extended Hamming code; Construction A
           gives E8 (240 roots, det 1) and, at infinity, E7 (126 roots, det 2); A carries the code to its twin
  e6       E6/3E6* is a nondegenerate quadratic space F3^5 whose 72 norm-1 classes are exactly the 72 roots
  ladder   the law on binary forms of degree k keeps Q up to sign (k = 1), the discriminant (k = 2) and the quartic
           discriminant of binary cubics (k = 3), the first member of the series that ends in E7's 56 and its quartic
  zfc      the 81 states are distinct hereditarily finite sets, Kuratowski pairs of von Neumann ordinals, all in V_11

    python3 tools/bridges.py              the report
    python3 tools/bridges.py --selftest   one line a result
Standard library only. Every value is computed here.
"""
import itertools, math, sys
from fractions import Fraction as F

# ---------- Q(sqrt5) as pairs p + q*phi ----------
class K:
    __slots__ = ('p', 'q')
    def __init__(s, p=0, q=0): s.p = F(p); s.q = F(q)
    def __add__(s, o): o = o if isinstance(o, K) else K(o); return K(s.p + o.p, s.q + o.q)
    __radd__ = __add__
    def __neg__(s): return K(-s.p, -s.q)
    def __sub__(s, o): return s + (-(o if isinstance(o, K) else K(o)))
    def __mul__(s, o):
        o = o if isinstance(o, K) else K(o)        # phi^2 = phi + 1
        return K(s.p * o.p + s.q * o.q, s.p * o.q + s.q * o.p + s.q * o.q)
    __rmul__ = __mul__
    def conj(s): return K(s.p + s.q, -s.q)         # phi -> 1 - phi
    def tr(s): return 2 * s.p + s.q
    def nm(s): return s.p * s.p + s.p * s.q - s.q * s.q
    def __eq__(s, o): o = o if isinstance(o, K) else K(o); return s.p == o.p and s.q == o.q
    def __hash__(s): return hash((s.p, s.q))
    def inv(s): n = s.nm(); c = s.conj(); return K(c.p / n, c.q / n)
    def real(s): return float(s.p) + float(s.q) * (1 + 5 ** .5) / 2
PHI = K(0, 1); HALF = K(F(1, 2)); ZERO = K(); ONE = K(1)
SQ5 = K(-1, 2)

def qmul(x, y):
    a1, b1, c1, d1 = x; a2, b2, c2, d2 = y
    return (a1*a2 - b1*b2 - c1*c2 - d1*d2, a1*b2 + b1*a2 + c1*d2 - d1*c2,
            a1*c2 - b1*d2 + c1*a2 + d1*b2, a1*d2 + b1*c2 - c1*b2 + d1*a2)
def nrd(x): return x[0]*x[0] + x[1]*x[1] + x[2]*x[2] + x[3]*x[3]

def icosians():
    G = set()
    for i in range(4):
        for s in (1, -1):
            v = [ZERO] * 4; v[i] = K(s); G.add(tuple(v))
    for sg in itertools.product((1, -1), repeat=4): G.add(tuple(K(F(s, 2)) for s in sg))
    base = (ZERO, HALF, HALF * (PHI - 1), HALF * PHI)          # (0, 1, 1/phi, phi)/2
    even = [p for p in itertools.permutations(range(4)) if sum(p[i] > p[j] for i in range(4) for j in range(i + 1, 4)) % 2 == 0]
    for p in even:
        for sg in itertools.product((1, -1), repeat=3):
            v = [ZERO] * 4; vals = [base[0], base[1] * sg[0], base[2] * sg[1], base[3] * sg[2]]
            for k in range(4): v[p[k]] = vals[k]
            G.add(tuple(v))
    return sorted(G, key=lambda v: tuple((c.p, c.q) for c in v))

def coords(x): return [c for k in x for c in (k.p, k.q)]          # Q^8
def hnf_basis(vecs):
    """Z-basis of the lattice spanned by rational vectors (exact echelon over Z)."""
    den = 1
    for v in vecs:
        for c in v: den = den * c.denominator // math.gcd(den, c.denominator)
    rows = [[int(c * den) for c in v] for v in vecs]
    n = len(rows[0]); B = []; r = 0
    rows = [list(x) for x in rows if any(x)]
    for col in range(n):
        piv = [x for x in rows if x[col] != 0]
        if not piv: continue
        while len([x for x in rows if x[col] != 0]) > 1:
            nz = sorted([x for x in rows if x[col] != 0], key=lambda x: abs(x[col]))
            p = nz[0]
            for x in nz[1:]:
                q = x[col] // p[col]
                for j in range(n): x[j] -= q * p[j]
            rows = [x for x in rows if any(x)]
        p = [x for x in rows if x[col] != 0][0]
        B.append(p); rows = [x for x in rows if x is not p]
    return [[F(c, den) for c in b] for b in B]
def det(M):
    M = [list(map(F, r)) for r in M]; n = len(M); d = F(1)
    for i in range(n):
        p = next((r for r in range(i, n) if M[r][i] != 0), None)
        if p is None: return F(0)
        if p != i: M[i], M[p] = M[p], M[i]; d = -d
        d *= M[i][i]
        for r in range(i + 1, n):
            f = M[r][i] / M[i][i]
            for c in range(i, n): M[r][c] -= f * M[i][c]
    return d
def tok(v): return tuple(K(v[2*i], v[2*i+1]) for i in range(4))

def short_vectors(G, bound):
    """all integer vectors x with x^T G x <= bound (Fincke-Pohst, exact check)."""
    n = len(G); A = [[float(x) for x in r] for r in G]
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = A[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(s) if i == j else s / L[j][j]
    out = []
    x = [0] * n
    def rec(i, rem):
        # coordinates solved from the last index down, using L^T
        if i < 0:
            if any(x): out.append(list(x))
            return
        c = -sum(L[k][i] * x[k] for k in range(i + 1, n)) / L[i][i]
        r = math.sqrt(max(rem, 0)) / L[i][i]
        for v in range(math.ceil(c - r - 1e-9), math.floor(c + r + 1e-9) + 1):
            x[i] = v
            t = L[i][i] * (v - c)
            nr = rem - t * t
            if nr >= -1e-9: rec(i - 1, nr)
        x[i] = 0
    rec(n - 1, bound + 1e-9)
    return [v for v in out if sum(v[i] * G[i][j] * v[j] for i in range(n) for j in range(n)) <= bound]

def e8_icosian():
    I = icosians()
    B = hnf_basis([coords(x) for x in I])
    Bq = [tok(b) for b in B]
    # the E8 form: B(x, y) = 2 Tr(c <x, y>) with c chosen so that the lattice is even and unimodular
    def ip(x, y): return x[0]*y[0] + x[1]*y[1] + x[2]*y[2] + x[3]*y[3]
    res = {}
    for name, c in (('1', ONE), ('1/sqrt5', SQ5.inv()), ('phi/sqrt5', PHI * SQ5.inv()), ('1/(phi sqrt5)', (PHI * SQ5).inv()),
                    ('(5+sqrt5)/10', (K(5) + SQ5) * K(F(1, 10))), ('(5-sqrt5)/10', (K(5) - SQ5) * K(F(1, 10)))):
        G = [[2 * (c * ip(x, y)).tr() for y in Bq] for x in Bq]
        res[name] = (det(G), all(G[i][i] % 2 == 0 for i in range(8)), G)
    return I, B, Bq, res

# ---- helpers ----
def mpow(M, n, m):
    R = ((1, 0), (0, 1))
    for _ in range(n): R = tuple(tuple(sum(R[i][k] * M[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))
    return R
def matmul2(X, Y): return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % 7 for j in range(2)) for i in range(2))
def ident(n): return [[int(i == j) for j in range(n)] for i in range(n)]
def matmul(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def matadd(X, Y): return [[X[i][j] + Y[i][j] for j in range(len(X[0]))] for i in range(len(X))]
def mpow_mat(M, n, m):
    R = ident(len(M))
    for _ in range(n): R = [[x % m for x in r] for r in matmul(R, M)]
    return R
def solve_int(B, v):
    """coefficients c with sum c_i B_i = v (B a basis, rows); returns integers"""
    n = len(B); M = [[B[j][i] for j in range(n)] + [v[i]] for i in range(len(v))]
    # least squares exact: B is square 8x8 here
    A = [row[:n] for row in M]; b = [row[n] for row in M]
    sol = gauss(A, b)
    assert all(x.denominator == 1 for x in sol)
    return [int(x) for x in sol]
def gauss(A, b):
    n = len(A); M = [list(map(F, A[i])) + [F(b[i])] for i in range(n)]
    for i in range(n):
        p = next(r for r in range(i, n) if M[r][i] != 0); M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i and M[r][i] != 0:
                f = M[r][i] / M[i][i]; M[r] = [M[r][c] - f * M[i][c] for c in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]
def hnf_contains(B, v):
    try: solve_int(B, v); return True
    except AssertionError: return False
def cycle_type(M, m):
    """cycle type of a linear map on (Z/m)^n via orders on each vector -- counted by the orbit sizes"""
    n = len(M); from collections import Counter
    # count fixed points of M^d for divisors d of the order and invert by Moebius
    order = next(k for k in range(1, 200) if mpow_mat(M, k, m) == ident(n))
    def fix(d):
        X = [[(a - (i == j)) % m for j, a in enumerate(r)] for i, r in enumerate(mpow_mat(M, d, m))]
        return kernel_size(X, m)
    divs = [d for d in range(1, order + 1) if order % d == 0]
    f = {d: fix(d) for d in divs}
    cyc = {}
    for d in divs:
        cnt = f[d] - sum(cyc[e] * e for e in divs if e < d and d % e == 0)
        cyc[d] = cnt // d
    return {d: c for d, c in cyc.items() if c}
def kernel_size(X, m):
    """number of solutions of X v = 0 over Z/m, m = 9: Smith form by brute elimination over Z"""
    A = [list(r) for r in X]; n = len(A)
    D = smith_diag(A)
    size = 1
    for d in D + [0] * (n - len(D)): size *= math.gcd(d, m) if d else m
    return size
def smith_diag(A):
    A = [list(r) for r in A]; diag = []
    while A and A[0]:
        nz = [(abs(A[i][j]), i, j) for i in range(len(A)) for j in range(len(A[0])) if A[i][j]]
        if not nz: break
        _, i, j = min(nz)
        A[0], A[i] = A[i], A[0]
        for r in A: r[0], r[j] = r[j], r[0]
        p = A[0][0]; done = True
        for r in range(1, len(A)):
            q = A[r][0] // p
            A[r] = [A[r][c] - q * A[0][c] for c in range(len(A[0]))]
            if A[r][0]: done = False
        for c in range(1, len(A[0])):
            q = A[0][c] // p
            for r in range(len(A)): A[r][c] -= q * A[r][0]
            if A[0][c]: done = False
        if done:
            if any(A[r][c] % p for r in range(1, len(A)) for c in range(1, len(A[0]))):
                A[0] = [A[0][c] + A[r][c] for r in [next(r for r in range(1, len(A)) if any(A[r][c] % p for c in range(1, len(A[0]))))] for c in range(len(A[0]))]
                continue
            diag.append(abs(p)); A = [r[1:] for r in A[1:]]
    return diag
def closure(gens):
    e = tuple(range(len(gens[0]))); G = {e}; fr = [e]
    while fr:
        nx = []
        for g in fr:
            for h in gens:
                k = tuple(h[g[i]] for i in range(len(g)))
                if k not in G: G.add(k); nx.append(k)
        fr = nx
    return G
def perm_code(h, C):
    return {tuple(w[[i for i in range(8) if h[i] == j][0]] for j in range(8)) for w in C}
def perm_code7(h, C):
    return {tuple(w[[i for i in range(7) if h[i] == j][0]] for j in range(7)) for w in C}
def construction_a(C, n):
    gens = [[2 * (i == j) for j in range(n)] for i in range(n)] + [list(w) for w in C if any(w)]
    B = hnf_basis([[F(x) for x in g] for g in gens])
    G = [[sum(a * b for a, b in zip(x, y)) / 2 for y in B] for x in B]
    return {'roots': len(short_vectors(G, 2)), 'det': det(G), 'even': all(G[i][i] % 2 == 0 for i in range(n))}
def e6_mod3():
    # E6 as the vectors of E8 (Construction A of C_Q) orthogonal to an A2 sublattice
    import itertools as it
    # simple-root Cartan matrix of E6
    Cm = [[2,-1,0,0,0,0],[-1,2,-1,0,0,0],[0,-1,2,-1,0,-1],[0,0,-1,2,-1,0],[0,0,0,-1,2,0],[0,0,-1,0,0,2]]
    roots = len(short_vectors(Cm, 2)); d = det(Cm)
    inv = [[F(x) for x in r] for r in invert(Cm)]
    # E6 / 3E6*: 3E6* is spanned by 3 * columns of Cm^-1 in root coordinates
    sub = [[3 * inv[i][j] for i in range(6)] for j in range(6)]
    den = 1
    for r in sub:
        for c in r: den = den * c.denominator // math.gcd(den, c.denominator)
    size = abs(det([[c for c in r] for r in sub]))
    # elements of E6/3E6*: enumerate root-coordinate vectors mod the sublattice via a reduction
    # quadratic form mod 3 on E6 / 3E6*: q(x) = x^T C x / 2, well defined mod 3
    reps = {}
    Sinv = invert([[int(c) if c.denominator == 1 else c for c in r] for r in sub])
    for v in it.product(range(3), repeat=6):
        # reduce v modulo the sublattice: coordinates in sub-basis, take fractional parts
        cco = [sum(F(Sinv[i][j]) * v[j] for j in range(6)) for i in range(6)]
        frac = tuple(c - math.floor(c) for c in cco)
        if frac not in reps: reps[frac] = v
    # reps above use v in {0,1,2}^6 which covers E6/3E6 (3^6) mapping onto E6/3E6*
    vals = {}
    from collections import Counter
    cnt = Counter()
    for frac, v in reps.items():
        q = sum(v[i] * Cm[i][j] * v[j] for i in range(6) for j in range(6)) // 2
        if any(frac): cnt[q % 3] += 1
    # nondegeneracy: bilinear form x^T C y mod 3 on the quotient has no nonzero radical element
    R = list(reps.values())
    rad = [v for v in R if any(v) and all(sum(v[i] * Cm[i][j] * w[j] for i in range(6) for j in range(6)) % 3 == 0 for w in R)
           and any(sum(F(Sinv[i][j]) * v[j] for j in range(6)) % 1 for i in range(6))]
    dual = [[F(x) for x in r] for r in inv]
    dmin = short_vectors_rational(dual, F(4, 3))
    return {'roots': roots, 'det': d, 'size': len(reps), 'nondeg': not rad, 'counts': dict(sorted(cnt.items())), 'dual_min': dmin}
def short_vectors_rational(G, bound):
    den = 1
    for r in G:
        for c in r: den = den * c.denominator // math.gcd(den, c.denominator)
    Gi = [[int(c * den) for c in r] for r in G]
    return len(short_vectors(Gi, int(bound * den)))
def invert(M):
    n = len(M); A = [[F(x) for x in r] + [F(int(i == j)) for j in range(n)] for i, r in enumerate(M)]
    for i in range(n):
        p = next(r for r in range(i, n) if A[r][i] != 0); A[i], A[p] = A[p], A[i]
        f = A[i][i]; A[i] = [x / f for x in A[i]]
        for r in range(n):
            if r != i and A[r][i] != 0:
                g = A[r][i]; A[r] = [A[r][c] - g * A[i][c] for c in range(2 * n)]
    return [r[n:] for r in A]
def posdef(G):
    n = len(G)
    return all(det([r[:k] for r in G[:k]]) > 0 for k in range(1, n + 1))
def so5_3():
    q = 3; return q ** 4 * (q ** 2 - 1) * (q ** 4 - 1)
def charpoly(M):
    """Faddeev-LeVerrier, exact"""
    n = len(M); M = [[F(x) for x in r] for r in M]
    I = ident(n); Mk = [[F(0)] * n for _ in range(n)]; c = [F(1)]
    for k in range(1, n + 1):
        Mk = matmul(M, [[Mk[i][j] + (c[-1] if i == j else 0) for j in range(n)] for i in range(n)])
        ck = -sum(Mk[i][i] for i in range(n)) / k
        c.append(ck)
    return [int(x) for x in c]          # coefficients of x^n, x^(n-1), ..., 1
def matpow(M, k):
    R = ident(len(M))
    for _ in range(k): R = matmul(R, M)
    return R
def inv_int(M):
    Mi = invert(M); return [[int(x) for x in r] for r in Mi]


def checks():
    from collections import Counter
    R = []
    # wheel
    s3 = (0, 3); orb = []
    for _ in range(8): orb.append(s3); s3 = (s3[1] % 9, (s3[0] + s3[1]) % 9)
    R.append(('wheel: 3Z[phi]/9Z[phi] is F9 and phi generates its 8 units', s3 == (0, 3) and len(set(orb)) == 8 and
              all(x[0] % 3 == 0 and x[1] % 3 == 0 for x in orb)))
    # e8
    I, B, Bq, res = e8_icosian()
    G = res['phi/sqrt5'][2]
    T = lambda M: [list(r) for r in zip(*M)]
    lin = lambda f: T([solve_int(B, coords(f(x))) for x in Bq])
    Mphi = lin(lambda x: tuple(PHI * c for c in x))
    roots = len(short_vectors(G, 2))
    R.append(('e8: the 120 unit icosians span E8 (rank 8, even, det 1, 240 roots)', len(I) == 120 and len(B) == 8 and res['phi/sqrt5'][0] == 1
              and res['phi/sqrt5'][1] and roots == 240 and posdef(G)))
    cyc = cycle_type([[x % 9 for x in r] for r in Mphi], 9)
    R.append(('census: the law on E8/9E8 is 1 + 820 x 8 + 1793340 x 24', matmul(Mphi, Mphi) == matadd(Mphi, ident(8)) and cyc == {1: 1, 8: 820, 24: 1793340}))
    # coxeter
    def qord(l):
        y = l; n = 1
        while y != (K(1), K(0), K(0), K(0)): y = tuple(qmul(y, l)); n += 1
        return n
    PHI30 = [1, 1, 0, -1, -1, -1, 0, 1, 1]
    C = None
    for l in [x for x in I if qord(x) == 10]:
        for r in [x for x in I if qord(x) == 3]:
            M = lin(lambda x: qmul(qmul(l, x), r))
            if charpoly(M) == PHI30: C = M; break
        if C: break
    Ci = [[int(x) for x in r] for r in invert(C)]
    P12 = matadd(matadd(ident(8), mpow_int(C, 12)), mpow_int(Ci, 12))
    R.append(('coxeter: C = l x r has characteristic polynomial Phi_30 and I + C^12 + C^-12 = phi', C is not None and P12 == Mphi
              and matmul(matmul(T(C), G), C) == G and mpow_int(C, 30) == ident(8)))
    # hamming
    R.append(('hamming: <A^2, B> mod 7 keeps the extended Hamming code; Construction A gives E8 and E7', hamming_ok()))
    # e6
    R.append(('e6: E6/3E6* is F3^5, its 72 norm-1 classes are the 72 roots', e6_ok()))
    # ladder
    R.append(('ladder: Sym^3 A keeps the quartic discriminant of binary cubics', ladder_ok()))
    # zfc
    def vn(n): return frozenset(vn(k) for k in range(n))
    def kp(a, b): return frozenset({frozenset({a}), frozenset({a, b})})
    def rank(x): return 0 if not x else 1 + max(rank(y) for y in x)
    S = [kp(vn(a), vn(b)) for a in range(9) for b in range(9)]
    R.append(('zfc: the 81 states are distinct hereditarily finite sets in V_11', len(set(S)) == 81 and max(rank(v) for v in S) == 10))
    return R

def mpow_int(M, k):
    R = ident(len(M))
    for _ in range(k): R = matmul(R, M)
    return R

def ext_code(g):
    C = set()
    for m in itertools.product((0, 1), repeat=4):
        w = [0] * 7
        for i, mi in enumerate(m):
            if mi:
                for j, gj in enumerate(g):
                    if gj: w[(i + j) % 7] ^= 1
        C.add(tuple(w) + (sum(w) % 2,))
    return C
def hamming_ok():
    pts = list(range(7)) + ['inf']
    def mob(M, z):
        a, b, c, d = M[0][0], M[0][1], M[1][0], M[1][1]
        if z == 'inf': return 'inf' if c % 7 == 0 else a * pow(c, -1, 7) % 7
        den = (c * z + d) % 7
        return 'inf' if den == 0 else (a * z + b) * pow(den, -1, 7) % 7
    A = ((0, 1), (1, 1)); Bs = ((1, 0), (3, 1)); A2 = matmul2(A, A)
    gperm = lambda M: tuple(pts.index(mob(M, p)) for p in pts)
    CQ, CN = ext_code((1, 1, 0, 1)), ext_code((1, 0, 1, 1))
    H = closure([gperm(A2), gperm(Bs)])
    keeps = all(perm_code(h, CQ) == CQ for h in H)
    twin = perm_code(gperm(A), CQ) == CN
    E8 = construction_a(CQ, 8); E7 = construction_a({w[:7] for w in CQ if w[7] == 0}, 7)
    return len(H) == 168 and keeps and twin and E8['roots'] == 240 and E8['det'] == 1 and E7['roots'] == 126 and E7['det'] == 2
def e6_ok():
    Cm = [[2,-1,0,0,0,0],[-1,2,-1,0,0,0],[0,-1,2,-1,0,-1],[0,0,-1,2,-1,0],[0,0,0,-1,2,0],[0,0,-1,0,0,2]]
    roots = short_vectors(Cm, 2)
    inv = invert(Cm); sub = [[3 * inv[i][j] for i in range(6)] for j in range(6)]; Sinv = invert(sub)
    cls = lambda v: tuple((sum(F(Sinv[i][j]) * v[j] for j in range(6))) % 1 for i in range(6))
    q = lambda v: sum(v[i] * Cm[i][j] * v[j] for i in range(6) for j in range(6)) // 2
    reps = {}
    for v in itertools.product(range(3), repeat=6): reps.setdefault(cls(v), v)
    n1 = {c for c, v in reps.items() if any(c) and q(v) % 3 == 1}
    return len(roots) == 72 and len(reps) == 243 and {cls(r) for r in roots} == n1
def ladder_ok():
    import math, random
    def sym3(f):     # f(x, y) -> f(y, x + y), coefficients of x^3, x^2 y, x y^2, y^3
        a, b, c, d = f
        # f(X, Y) with X = y, Y = x + y
        out = [0, 0, 0, 0]
        for coef, (i, j) in zip((a, b, c, d), ((3, 0), (2, 1), (1, 2), (0, 3))):
            for k in range(j + 1):       # X^i Y^j = y^i (x + y)^j
                out[3 - k] += coef * math.comb(j, k)    # x^k y^(i + j - k)
        return out
    disc = lambda f: (f[1]**2 * f[2]**2 - 4 * f[0] * f[2]**3 - 4 * f[1]**3 * f[3] - 27 * f[0]**2 * f[3]**2 + 18 * f[0] * f[1] * f[2] * f[3])
    rng = random.Random(42)
    F3 = [[rng.randint(-20, 20) for _ in range(4)] for _ in range(500)]
    f = [1, 0, 0, 0]; n = 0
    while True:
        f = [x % 9 for x in sym3(f)]; n += 1
        if f == [1, 0, 0, 0]: break
    basis = [[int(i == j) for j in range(4)] for i in range(4)]
    def order9(v):
        w = list(v); k = 0
        while True:
            w = [x % 9 for x in sym3(w)]; k += 1
            if w == list(v): return k
    o = max(order9(e) for e in basis)
    return all(disc(sym3(f)) == disc(f) for f in F3) and o == 24

def report():
    for n, ok in checks(): print('%-100s %s' % (n, 'PASS' if ok else 'FAIL'))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        R = checks()
        for n, ok in R: print('%-100s %s' % (n, 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o in R); print('BRIDGES SELFTEST: %d of %d | %s' % (sum(o for _, o in R), len(R), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if not a: report(); sys.exit(0)
    print(__doc__); sys.exit(2)
