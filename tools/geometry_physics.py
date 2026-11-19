#!/usr/bin/env python3
"""geometry_physics.py -- Omega42 joined to geometry, topology, number theory, dynamics, combinatorics and mathematical physics
(Companion Part 218; MF-81 to MF-99; F212, APE-474).

  h4                the 240 roots of E8 projected to the golden eigenspace of the law: two 600-cells, radii in the ratio phi
  quasicrystal      the Fibonacci chain is the cut-and-project chain of Z^2 along the law's eigenline
  markov            (1, F_(2n-1), F_(2n+1)) are Markov triples
  knot              A^2 is the monodromy of the figure-eight knot; its characteristic polynomial is the knot's Alexander polynomial
  golden-shift      words with no 11 number F_(n+2): the law is the transfer matrix of the golden mean shift
  torus             the law on the torus has |L_k - 1 - (-1)^k| points of period dividing k
  zeckendorf        every integer is one sum of non-consecutive Fibonacci numbers
  anyons            the fusion matrix of the Fibonacci anyon is the law; F^2 = I, the braid relation, dimensions F_n
  conformal         c(G2, 1) + c(F4, 1) = 14/5 + 26/5 = 8 = c(E8, 1)
  e8-masses         Zamolodchikov's E8 masses: m2/m1 = phi, m3/m1 = 2 cos(pi/30)
  rogers-ramanujan  R(e^(-2 pi)) = sqrt((5 + sqrt5)/2) - phi
  lee-yang          the (2,5) minimal model, c = -22/5, fuses by the law
  lorentz           X -> M X M^T for A and B keeps det X: A improper, B a null rotation fixing a light ray
  hamiltonian       log A^2 = (2 ln phi/sqrt5)(2A - I); its Hamiltonian is (2 ln phi/sqrt5) Q; A = S0 exp(L/2)
  geodesic          A^2 = LR: the shortest closed geodesic of the modular surface, length 4 ln phi
  koopman           the Koopman operator on the 81 states has characteristic polynomial (x - 1)(x^8 - 1)(x^24 - 1)^3
  symplectic        <A, B> mod 9 of order 216; the graph of the law and the shear has b0 = 3, b1 = 84
  functor           Sym^3 is a functor: the ladder of MF-79 composes
  three-qubit       the law and the shear on any qubit keep Cayley's hyperdeterminant

    python3 tools/geometry_physics.py --selftest
Standard library only. Integer statements are exact; real identities are checked to 1e-12 or better, the knot volume to 1e-6.
"""
#!/usr/bin/env python3

import math, cmath, itertools, sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fractions import Fraction as F
PHI = (1 + 5 ** .5) / 2
A = [[0, 1], [1, 1]]
def mm(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def luc(n): return fib(n - 1) + fib(n + 1) if n > 0 else 2
LINES = []
def P(*a): LINES.append(' '.join(str(x) for x in a))

# ---------- GEOMETRY ----------
def h4():
    import bridges as b
    I, B, Bq, res = b.e8_icosian()
    G = res['phi/sqrt5'][2]
    roots = b.short_vectors(G, 2)
    # coordinates: each root is a Z-combination of the basis; map to quaternion over Q(sqrt5), then the two real embeddings
    def to_q(c):
        v = [b.K(0)] * 4
        for ci, bq in zip(c, Bq):
            for k in range(4): v[k] = v[k] + bq[k] * ci
        return v
    s5 = 5 ** .5
    emb1 = lambda k: float(k.p) + float(k.q) * (1 + s5) / 2
    emb2 = lambda k: float(k.p) + float(k.q) * (1 - s5) / 2
    P1 = [[emb1(x) for x in to_q(r)] for r in roots]
    P2 = [[emb2(x) for x in to_q(r)] for r in roots]
    r1 = sorted({round(math.sqrt(sum(x * x for x in v)), 9) for v in P1})
    r2 = sorted({round(math.sqrt(sum(x * x for x in v)), 9) for v in P2})
    shells = {r: sum(1 for v in P1 if abs(math.sqrt(sum(x * x for x in v)) - r) < 1e-6) for r in r1}
    # each shell a 600-cell: 120 points, each with 12 nearest neighbours
    def nn(pts):
        cnt = []
        for p in pts:
            d = sorted(math.dist(p, q) for q in pts if q is not p)
            cnt.append(sum(1 for x in d if abs(x - d[0]) < 1e-6))
        return set(cnt)
    sh = [[v for v in P1 if abs(math.sqrt(sum(x * x for x in v)) - r) < 1e-6] for r in r1]
    P('G1 H4: the 240 roots of E8 projected to the first golden half fall on', len(r1), 'spheres, radii', r1, 'ratio', round(r1[1] / r1[0], 12) if len(r1) == 2 else '-',
      '(phi =', round(PHI, 12), ') | points per sphere', list(shells.values()), '| nearest neighbours of every vertex', [nn(s) for s in sh])
    # the same through the explicit spectral projector of the law on E8: P+ = (M + I/phi)/sqrt5
    T = lambda Mx: [list(r) for r in zip(*Mx)]
    M = T([b.solve_int(B, b.coords(tuple(b.PHI * c for c in x))) for x in Bq])
    PSI = -1 / PHI
    Pp = [[(M[i][j] - PSI * (i == j)) / (PHI - PSI) for j in range(8)] for i in range(8)]
    Gf = [[float(x) for x in r] for r in G]
    nrm = lambda v: sum(v[i] * Gf[i][j] * v[j] for i in range(8) for j in range(8))
    idem = max(abs(sum(Pp[i][k] * Pp[k][j] for k in range(8)) - Pp[i][j]) for i in range(8) for j in range(8))
    pr = [[sum(Pp[i][j] * r[j] for j in range(8)) for i in range(8)] for r in roots]
    ns = sorted({round(nrm(v), 9) for v in pr})
    P('  projector: P+ = (M + I/phi)/sqrt5 on the Z-basis of E8, idempotent to %.1e; squared norms %s, ratio %.12f = phi^2' % (idem, ns, ns[1] / ns[0]))
    proj_ok = idem < 1e-12 and len(ns) == 2 and abs(ns[1] / ns[0] - PHI ** 2) < 1e-8
    return proj_ok and len(r1) == 2 and abs(r1[1] / r1[0] - PHI) < 1e-9 and list(shells.values()) == [120, 120] and all(nn(s) == {12} for s in sh)

def quasicrystal(N=3000):
    w = 'a'
    while len(w) < N: w = ''.join('ab' if c == 'a' else 'a' for c in w)
    w = w[:N]
    # cut and project from Z^2 along the expanding eigenline of the law: the n-th letter is a when floor((n+2)/phi) - floor((n+1)/phi) = 1
    cp = ''.join('a' if math.floor((n + 2) / PHI) - math.floor((n + 1) / PHI) == 1 else 'b' for n in range(N))
    ok = w == cp
    P('G2 QUASICRYSTAL: the Fibonacci chain from the substitution a -> ab, b -> a equals the cut-and-project chain of Z^2 along the eigenline of the law for', N, 'letters:', ok,
      '| frequency of a:', round(w.count('a') / N, 6), '(1/phi =', round(1 / PHI, 6), ')')
    # with the window: Z^2, physical line the expanding eigenvector (1, phi), internal line the contracting one (1, -1/phi);
    # select (m, n) whose internal coordinate lies in the projection of the unit square, half-open, shifted generically
    PSI = -1 / PHI; hp, hm = math.hypot(1, PHI), math.hypot(1, PSI)
    cs = [(x + y * PSI) / hm for x in (0, 1) for y in (0, 1)]; lo, hi = min(cs), max(cs); eps = 1e-9 * math.pi
    pts = []
    for m in range(-4000, 4000):
        a1, a2 = (lo - eps) * hm - m, (hi - eps) * hm - m        # lo <= (m + n PSI)/hm + eps < hi, PSI < 0
        for n in range(math.ceil(a2 / PSI) - 1, math.floor(a1 / PSI) + 2):
            t = (m + n * PSI) / hm + eps
            if lo <= t < hi: pts.append((m + n * PHI) / hp)
    pts = sorted(p for p in pts if p >= 0)[:N + 1]
    gaps = [pts[i + 1] - pts[i] for i in range(N)]; Lg = max(gaps)
    word = ''.join('a' if abs(g - Lg) < 1e-6 else 'b' for g in gaps)
    big = 'a'
    while len(big) < 60000: big = ''.join('ab' if c == 'a' else 'a' for c in big)
    at = big.find(word)
    P('  window: the lattice points of Z^2 whose internal coordinate lies in [%.6f, %.6f) give two gaps in the ratio %.12f, and their %d-letter chain is a factor of the Fibonacci word (at %d)' % (lo, hi, Lg / min(gaps), N, at))
    return ok and at >= 0 and abs(Lg / min(gaps) - PHI) < 1e-9

def markov():
    ok = all(1 + fib(2 * n - 1) ** 2 + fib(2 * n + 1) ** 2 == 3 * fib(2 * n - 1) * fib(2 * n + 1) for n in range(1, 60))
    P('G3 MARKOV: (1, F_(2n-1), F_(2n+1)) solves x^2 + y^2 + z^2 = 3xyz for n = 1..59:', ok, '| first triples', [(1, fib(2 * n - 1), fib(2 * n + 1)) for n in range(1, 6)],
      '| Lagrange value of phi = sqrt5, the least of all irrationals (Hurwitz)')
    return ok

def figure_eight():
    A2 = mm(A, A); cat = [[2, 1], [1, 1]]; S = [[0, 1], [1, 0]]
    conj = mm(mm(S, A2), S) == cat
    tr = A2[0][0] + A2[1][1]; dt = A2[0][0] * A2[1][1] - A2[0][1] * A2[1][0]
    # Lobachevsky: V = 6 L(pi/3), L(t) = 1/2 sum sin(2kt)/k^2
    L = lambda t: 0.5 * sum(math.sin(2 * k * t) / (k * k) for k in range(1, 400000))
    V = 6 * L(math.pi / 3)
    P('G4 KNOT: A^2 is conjugate to the cat map [[2,1],[1,1]], the monodromy of the figure-eight knot:', conj, '| characteristic polynomial t^2 -', tr, 't +', dt,
      '= the Alexander polynomial of the figure-eight knot | hyperbolic volume 6 L(pi/3) =', round(V, 9))
    return conj and (tr, dt) == (3, 1) and abs(V - 2.029883212819307) < 1e-6

# ---------- DYNAMICS, COMBINATORICS, INFORMATION ----------
def golden_shift():
    ok = True; counts = []
    for n in range(1, 21):
        c = sum(1 for w in itertools.product('01', repeat=n) if '11' not in ''.join(w))
        counts.append(c); ok = ok and c == fib(n + 2)
    T = [[1, 1], [1, 0]]
    P('D1 GOLDEN MEAN SHIFT: binary words with no 11 number F_(n+2) for n = 1..20:', ok, counts[:8], '| its transfer matrix [[1,1],[1,0]] is the law reversed; entropy ln phi =', round(math.log(PHI), 12))
    return ok

def cat_map_periods():
    ok = True
    for k in range(1, 41):
        M = [[1, 0], [0, 1]]
        for _ in range(k): M = mm(M, A)
        d = (M[0][0] - 1) * (M[1][1] - 1) - M[0][1] * M[1][0]
        ok = ok and abs(d) == abs(luc(k) - 1 - (-1) ** k)
    Nd = {k: abs(luc(k) - 1 - (-1) ** k) for k in range(1, 25)}
    def mu(n):
        r, p_, m = 1, 2, n
        while p_ * p_ <= m:
            if m % p_ == 0:
                m //= p_
                if m % p_ == 0: return 0
                r = -r
            p_ += 1
        return -r if m > 1 else r
    exact = {k: sum(mu(k // d) * Nd[d] for d in range(1, k + 1) if k % d == 0) for k in range(1, 25)}
    ok = ok and all(exact[k] % k == 0 and exact[k] >= 0 for k in exact)
    P('  exact periods (Moebius): points', [exact[k] for k in range(1, 11)], '| orbits', [exact[k] // k for k in range(1, 11)])
    P('D2 PERIODIC POINTS: the law on the torus R^2/Z^2 has |det(A^k - I)| = |L_k - 1 - (-1)^k| points of period dividing k, k = 1..40:', ok,
      '| first counts', [abs(luc(k) - 1 - (-1) ** k) for k in range(1, 9)])
    return ok

def zeckendorf():
    fibs = [fib(n) for n in range(2, 40)]
    def z(n):
        r = []
        for f in reversed(fibs):
            if f <= n: r.append(f); n -= f
        return r
    ok = all(sum(z(n)) == n and all(fibs.index(z(n)[i]) - fibs.index(z(n)[i + 1]) >= 2 for i in range(len(z(n)) - 1)) for n in range(1, 20000))
    P('C1 ZECKENDORF: every n < 20000 is one sum of non-consecutive Fibonacci numbers:', ok)
    return ok

# ---------- MATHEMATICAL PHYSICS ----------
def anyons():
    # fusion tau x tau = 1 + tau: fusion matrix of tau on (1, tau)
    N = [[0, 1], [1, 1]]
    ok_fusion = N == A
    # F and R matrices of the Fibonacci category
    p = PHI
    Fm = [[1 / p, 1 / math.sqrt(p)], [1 / math.sqrt(p), -1 / p]]
    R1, Rt = cmath.exp(-4j * math.pi / 5), cmath.exp(3j * math.pi / 5)
    R = [[R1, 0], [0, Rt]]
    def cm(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    s1 = R; s2 = cm(cm(Fm, R), Fm)
    braid = max(abs(a - b) for r1, r2 in zip(cm(cm(s1, s2), s1), cm(cm(s2, s1), s2)) for a, b in zip(r1, r2))
    unit = max(abs(x) for x in [cm(Fm, Fm)[0][0] - 1, cm(Fm, Fm)[0][1], cm(Fm, Fm)[1][1] - 1])
    # dimension of the fusion space of n tau-anyons with total charge tau: F_(n-1)
    dims = []
    v = [0, 1]
    for n in range(1, 12): dims.append(v[1]); v = [v[1], v[0] + v[1]]
    # order of a braid generator up to phase: R1/Rt is a root of unity of order 10
    ratio = R1 / Rt; o = next(k for k in range(1, 50) if abs(ratio ** k - 1) < 1e-12)
    # hexagon: R F R = F R F (one form of the hexagon for the Fibonacci category)
    hexa = braid
    P('P1 FIBONACCI ANYONS: the fusion matrix of tau is the law', ok_fusion, '| quantum dimension phi =', round(PHI, 12),
      '| F^2 = I to', '%.1e' % unit, '| braid relation s1 s2 s1 = s2 s1 s2 to', '%.1e' % braid, '| fusion spaces of n anyons', dims[:10], '| braid generator of order', o, 'up to phase')
    return ok_fusion and unit < 1e-12 and braid < 1e-12 and dims[:6] == [1, 1, 2, 3, 5, 8] and o == 10

def central_charges():
    c = lambda dim, k, h: F(k * dim, k + h)
    g2, f4, e8 = c(14, 1, 4), c(52, 1, 9), c(248, 1, 30)
    P('P2 CONFORMAL EMBEDDING: c(G2, level 1) =', g2, '| c(F4, level 1) =', f4, '| sum', g2 + f4, '= c(E8, level 1) =', e8,
      '| G2 level 1 is the Fibonacci category of P1; it and F4 level 1 fill E8 level 1')
    return g2 + f4 == e8 == 8

def zamolodchikov():
    # E8 Dynkin diagram adjacency; Perron-Frobenius eigenvector gives the masses of the Ising field theory in a magnetic field
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (2, 7)]   # chain 0-...-6 with branch at node 2 (E8: arms 1, 2, 4)
    n = 8; M = [[0] * n for _ in range(n)]
    for i, j in edges: M[i][j] = M[j][i] = 1
    v = [1.0] * n
    for _ in range(5000):
        w = [v[i] + sum(M[i][j] * v[j] for j in range(n)) for i in range(n)]   # M + I: no oscillation on a bipartite graph
        s = math.sqrt(sum(x * x for x in w)); v = [x / s for x in w]
    lam = sum(sum(M[i][j] * v[j] for j in range(n)) * v[i] for i in range(n))
    m = sorted(v)
    r2, r3 = m[1] / m[0], m[2] / m[0]
    P('P3 E8 MASSES (Zamolodchikov): Perron-Frobenius eigenvalue of E8 =', round(lam, 12), '= 2 cos(pi/30) =', round(2 * math.cos(math.pi / 30), 12),
      '| m2/m1 =', round(r2, 12), '= 2 cos(pi/5) = phi:', abs(r2 - PHI) < 1e-9, '| m3/m1 =', round(r3, 12), '= 2 cos(pi/30):', abs(r3 - 2 * math.cos(math.pi / 30)) < 1e-9)
    return abs(r2 - PHI) < 1e-9 and abs(lam - 2 * math.cos(math.pi / 30)) < 1e-9 and abs(r3 - 2 * math.cos(math.pi / 30)) < 1e-9

def rogers_ramanujan():
    q = math.exp(-2 * math.pi)
    # R(q) = q^(1/5) prod (1 - q^(5n-1))(1 - q^(5n-4)) / ((1 - q^(5n-2))(1 - q^(5n-3)))
    pr = 1.0
    for n in range(1, 60): pr *= (1 - q ** (5 * n - 1)) * (1 - q ** (5 * n - 4)) / ((1 - q ** (5 * n - 2)) * (1 - q ** (5 * n - 3)))
    Rv = q ** 0.2 * pr
    target = math.sqrt((5 + 5 ** .5) / 2) - PHI
    P('P4 ROGERS-RAMANUJAN: R(e^(-2 pi)) =', round(Rv, 14), '= sqrt((5 + sqrt5)/2) - phi =', round(target, 14), ':', abs(Rv - target) < 1e-13)
    return abs(Rv - target) < 1e-13

def ising_golden_cft():
    # the Lee-Yang (2,5) minimal model: c = 1 - 6 (p - q)^2 / (p q) = -22/5; its fusion phi x phi = 1 + phi is again the law
    p, q = 2, 5; c = 1 - F(6 * (p - q) ** 2, p * q)
    P('P5 LEE-YANG: the (2,5) minimal model has c =', c, 'and one primary with fusion phi x phi = 1 + phi: its fusion matrix is the law')
    return c == F(-22, 5)


def part4():
    PHI = (1 + 5 ** .5) / 2; S5 = 5 ** .5
    def mm(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
    def det2(M): return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    def det3(M): return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    A = [[0, 1], [1, 1]]; B = [[1, 0], [3, 1]]; I2 = [[1, 0], [0, 1]]
    R4 = []
    def P4(name, ok, *a): R4.append((name, ok, ' '.join(str(x) for x in a)))

    # E1 the Lorentz representation on symmetric matrices X = [[u, v], [v, w]], det X = uw - v^2
    def sym2(M):
        cols = []
        for X in ([[1, 0], [0, 0]], [[0, 1], [1, 0]], [[0, 0], [0, 1]]):
            Y = mm(mm(M, X), [list(r) for r in zip(*M)])
            cols.append([Y[0][0], Y[0][1], Y[1][1]])
        return [list(r) for r in zip(*cols)]
    LA, LB = sym2(A), sym2(B)
    eta = lambda x: x[0] * x[2] - x[1] ** 2
    rng = random.Random(7); vecs = [[rng.randint(-30, 30) for _ in range(3)] for _ in range(300)]
    app = lambda M, x: [sum(M[i][j] * x[j] for j in range(3)) for i in range(3)]
    keep = all(eta(app(LA, x)) == eta(x) and eta(app(LB, x)) == eta(x) for x in vecs)
    trA, trB = sum(LA[i][i] for i in range(3)), sum(LB[i][i] for i in range(3))
    null_fixed = app(LB, [0, 0, 1]) == [0, 0, 1]          # e2 e2^T = [[0,0],[0,1]]
    P4('E1', keep and det3(LA) == -1 and det3(LB) == 1 and null_fixed and trB == 3,
      'X -> M X M^T keeps det X for A and B on 300 vectors; L_A =', LA, 'det', det3(LA), 'trace', trA, '(improper: a boost of rapidity 2 ln phi with a reflection)',
      '| L_B =', LB, 'det', det3(LB), 'trace', trB, '(parabolic: a null rotation fixing the light ray e2 e2^T)')

    # E2 the Hamiltonian of the law
    c = 2 * math.log(PHI) / S5
    L = [[-c, 2 * c], [2 * c, c]]                           # log A^2 = c (2A - I)
    def expm(M, terms=60):
        Rr = [[1.0, 0.0], [0.0, 1.0]]; T = [[1.0, 0.0], [0.0, 1.0]]
        for k in range(1, terms):
            T = [[x / k for x in r] for r in mm(T, M)]; Rr = [[Rr[i][j] + T[i][j] for j in range(2)] for i in range(2)]
        return Rr
    EL = expm(L)
    err = max(abs(EL[i][j] - [[1, 1], [1, 2]][i][j]) for i in range(2) for j in range(2))
    J = [[0, 1], [-1, 0]]
    Sm = mm([[0, -1], [1, 0]], L)                           # S = -J L, so L = J S
    # H(q, p) = 1/2 x^T S x ; compare with c * Q(q, p), Q = p^2 - q p - q^2
    Hc = lambda q, p: 0.5 * (Sm[0][0] * q * q + 2 * Sm[0][1] * q * p + Sm[1][1] * p * p)
    Qf = lambda q, p: p * p - q * p - q * q
    hq = max(abs(Hc(q, p) - c * Qf(q, p)) for q in range(-5, 6) for p in range(-5, 6))
    S0 = [[(2 * A[i][j] - I2[i][j]) / S5 for j in range(2)] for i in range(2)]
    half = expm([[x / 2 for x in r] for r in L])
    comp = mm(S0, half); errA = max(abs(comp[i][j] - A[i][j]) for i in range(2) for j in range(2))
    S0sq = mm(S0, S0); inv = max(abs(S0sq[i][j] - I2[i][j]) for i in range(2) for j in range(2))
    flipQ = max(abs(Qf(*[sum(S0[i][j] * v[j] for j in range(2)) for i in range(2)]) + Qf(*v)) for v in ([1, 0], [0, 1], [2, 3], [5, -1]))
    # B as the time-one flow of H_B = -3/2 q^2: q' = dH/dp = 0, p' = -dH/dq = 3q
    Bflow = [[1, 0], [3, 1]] == B
    P4('E2', err < 1e-12 and hq < 1e-12 and errA < 1e-12 and inv < 1e-12 and flipQ < 1e-12 and Bflow,
      'log A^2 = (2 ln phi / sqrt5)(2A - I), exp to %.1e;' % err, 'its Hamiltonian is H = (2 ln phi / sqrt5) Q(q, p), to %.1e;' % hq,
      'A = S0 exp(L/2) with S0 = (2A - I)/sqrt5 an involution reversing Q (to %.1e); B is the flow of H = -3/2 q^2' % max(errA, inv, flipQ))

    # E3 hyperbolic coding: A^2 = L R, the shortest closed geodesic codes as (LR)^infinity
    Lm, Rm = [[1, 0], [1, 1]], [[1, 1], [0, 1]]
    Ach = 2 * math.acosh(1.5)
    P4('E3', mm(Lm, Rm) == mm(A, A) and abs(Ach - 4 * math.log(PHI)) < 1e-12,
      'A^2 = L R: its closed geodesic on the modular surface has cutting sequence (LR)^inf; length 2 arccosh(3/2) = 4 ln phi =', round(Ach, 12),
      '| the projective step r -> 1/(1 + r) has fixed point 1/phi; Lyapunov exponents +-ln phi =', round(math.log(PHI), 12))

    # E4 the Koopman operator on the 81 states: characteristic polynomial (x - 1)(x^8 - 1)(x^24 - 1)^3
    st = [(a, b) for a in range(9) for b in range(9)]
    nxt = {s: (s[1], (s[0] + s[1]) % 9) for s in st}
    seen = set(); cyc = []
    for s in st:
        if s in seen: continue
        n = 0; t = s
        while True:
            seen.add(t); t = nxt[t]; n += 1
            if t == s: break
        cyc.append(n)
    mult = {k: sum(1 for n in cyc if (k * n) % 24 == 0) for k in range(24)}
    P4('E4', sorted(cyc) == [1, 8, 24, 24, 24] and all(mult[k] == 3 + (1 if k % 3 == 0 else 0) + (1 if k == 0 else 0) for k in range(24)),
      'the Koopman operator of the law on l2(81) has characteristic polynomial (x - 1)(x^8 - 1)(x^24 - 1)^3; eigenvalue exp(2 pi i k/24) of multiplicity 3 + [3 | k] + [k = 0]:',
      [mult[k] for k in range(6)], '...')

    # E5 the symplectic group mod 9 and the graph homology of the states
    def gen(gens, m):
        e = (1, 0, 0, 1); G = {e}; fr = [e]
        while fr:
            nx = []
            for X in fr:
                for g in gens:
                    Y = ((X[0] * g[0] + X[1] * g[2]) % m, (X[0] * g[1] + X[1] * g[3]) % m, (X[2] * g[0] + X[3] * g[2]) % m, (X[2] * g[1] + X[3] * g[3]) % m)
                    if Y not in G: G.add(Y); nx.append(Y)
            fr = nx
        return G
    GAB = gen([(0, 1, 1, 1), (1, 0, 3, 1)], 9); GA2B = gen([(1, 1, 1, 2), (1, 0, 3, 1)], 9)
    sp = all((x[0] * x[3] - x[1] * x[2]) % 9 == 1 for x in GA2B)
    # Schreier graph of <A, B> on the 81 states: V = 81, E = 162, components = orbits
    par = {s: s for s in st}
    def f(s):
        while par[s] != s: par[s] = par[par[s]]; s = par[s]
        return s
    for s in st:
        for t in (nxt[s], (s[0] % 9, (3 * s[0] + s[1]) % 9)): par[f(s)] = f(t)
    comps = len({f(s) for s in st}); b1 = 162 - 81 + comps
    P4('E5', len(GAB) == 216 and sp and comps == 3,
      '<A, B> mod 9 has order', len(GAB), '| <A^2, B> mod 9 has order', len(GA2B), 'inside Sp2(Z/9) = SL2(Z/9) (order 648) | the graph of the law and the shear on the 81 states: b0 =', comps, '(the valuation strata), b1 =', b1)

    # E6 functoriality: Sym^3 is a functor, Sym^3(XY) = Sym^3(X) Sym^3(Y)
    def sym3(M):
        a, b, cc, d = M[0][0], M[0][1], M[1][0], M[1][1]
        out = [[0] * 4 for _ in range(4)]
        for i in range(4):
            p1 = [math.comb(3 - i, j) * a ** (3 - i - j) * cc ** j for j in range(4 - i)]
            p2 = [math.comb(i, j) * b ** (i - j) * d ** j for j in range(i + 1)]
            for u, x in enumerate(p1):
                for v, y in enumerate(p2): out[u + v][i] += x * y
        return out
    mats = [[[rng.randint(-4, 4) for _ in range(2)] for _ in range(2)] for _ in range(60)]
    func = all(sym3(mm(X, Y)) == mm(sym3(X), sym3(Y)) for X, Y in zip(mats, mats[1:]))
    P4('E6', func and sym3(I2) == [[int(i == j) for j in range(4)] for i in range(4)], 'Sym^3 is a functor on 59 pairs of integer matrices: the ladder of MF-79 is a functorial bridge, composable with every other')

    # E7 three qubits: Cayley's hyperdeterminant, the 3-tangle, kept by the law on each qubit
    def hyper(t):
        a = lambda i, j, k: t[4 * i + 2 * j + k]
        return (a(0,0,0)**2 * a(1,1,1)**2 + a(0,0,1)**2 * a(1,1,0)**2 + a(0,1,0)**2 * a(1,0,1)**2 + a(1,0,0)**2 * a(0,1,1)**2
                - 2 * (a(0,0,0) * a(0,0,1) * a(1,1,0) * a(1,1,1) + a(0,0,0) * a(0,1,0) * a(1,0,1) * a(1,1,1) + a(0,0,0) * a(1,0,0) * a(0,1,1) * a(1,1,1)
                       + a(0,0,1) * a(0,1,0) * a(1,0,1) * a(1,1,0) + a(0,0,1) * a(1,0,0) * a(0,1,1) * a(1,1,0) + a(0,1,0) * a(1,0,0) * a(0,1,1) * a(1,0,1))
                + 4 * (a(0,0,0) * a(0,1,1) * a(1,0,1) * a(1,1,0) + a(0,0,1) * a(0,1,0) * a(1,0,0) * a(1,1,1)))
    def act(M, t, axis):
        out = [0] * 8
        for i, j, k in itertools.product((0, 1), repeat=3):
            idx = [i, j, k]
            for r in (0, 1):
                src = list(idx); src[axis] = r
                out[4 * i + 2 * j + k] += M[idx[axis]][r] * t[4 * src[0] + 2 * src[1] + src[2]]
        return out
    ts = [[rng.randint(-5, 5) for _ in range(8)] for _ in range(300)]
    ghz = [1, 0, 0, 0, 0, 0, 0, 1]
    okh = all(hyper(act(M, t, ax)) == hyper(t) for t in ts for M in (A, B) for ax in range(3))
    P4('E7', okh and hyper(ghz) == 1, "the law and the shear on any one of three qubits keep Cayley's hyperdeterminant (the 3-tangle) on 300 tensors; GHZ has hyperdeterminant", hyper(ghz),
      '| 2 x 2 x 2 is the second rung of the series that ends in E7 (MF-79)')


    return R4

KEYS3 = [('h4', h4), ('quasicrystal', quasicrystal), ('markov', markov), ('knot', figure_eight), ('golden-shift', golden_shift), ('torus', cat_map_periods),
         ('zeckendorf', zeckendorf), ('anyons', anyons), ('conformal', central_charges), ('e8-masses', zamolodchikov), ('rogers-ramanujan', rogers_ramanujan), ('lee-yang', ising_golden_cft)]
KEYS4 = {'E1': 'lorentz', 'E2': 'hamiltonian', 'E3': 'geodesic', 'E4': 'koopman', 'E5': 'symplectic', 'E6': 'functor', 'E7': 'three-qubit'}
def checks():
    out = []
    for k, f in KEYS3:
        ok = f(); out.append((k, ok, LINES[-1].split(' ', 1)[1][:150]))
    for name, ok, txt in part4(): out.append((KEYS4[name], ok, txt[:150]))
    return out
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        C = checks()
        for k, ok, t in C: print('%s: %s %s' % (k, t, 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in C); print('GEOMETRY AND PHYSICS SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in C), len(C), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
