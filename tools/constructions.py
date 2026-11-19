#!/usr/bin/env python3
"""constructions.py -- the quantized cat map, relativistic velocity addition, the Coxeter grading of E8's adjoint, Penrose inflation,
the first sealed prediction and the setup of PR-003 (Companion Part 219; MF-100 to MF-104; F214, APE-476).

  quantum-cat       the Weil operator of A^2 on l2(Z/N), N odd from 3 to 25, is unitary and its period up to phase equals the
                    classical period of A^2 modulo N: 4, 10, 8, 12, 5, 14, 20, 18, 9, 8, 24, 50
  pell              the velocities beta_m = sqrt5 F_2m/L_2m = tanh(2m ln phi) close under Einstein addition: beta_m + beta_n = beta_(m+n)
  coxeter-adjoint   a Coxeter element C of E8 permutes the 240 roots in 8 orbits of 30; on the adjoint each 30th root of unity has
                    multiplicity 8 + [exponent]; I + C^12 + C^-12 is phi on the exponents 7, 13, 17, 23 and -1/phi on 1, 11, 19, 29
  penrose           the Penrose inflation matrix [[2,1],[1,1]] is A^2 conjugated by the swap; the limiting thick-to-thin ratio is
                    sin 72/sin 36 = phi; finite pentagrid patches of radius 8 to 48 approach it, the error falling to 6.3e-4
  pr001             PR-001, sealed in seq_0170 and tested after: <A, B> modulo p is every matrix of determinant +-1 for the 17 primes 23 to 97
  pr002             PR-002, sealed in seq_0172 and tested after: A^2 and B modulo 23 keep the extended Golay code
  braid-setup       the setup of PR-003: the Fibonacci braid representation in the gauge F' = [[1/phi, 1/phi], [1, -1/phi]] reduces
                    at the prime above 11 (zeta -> 2) to s1 = [[9,0],[0,8]], s2 = [[2,5],[7,4]] with F'^2 = I and the braid relation

    python3 tools/constructions.py --selftest
Standard library only.
"""
import cmath, math, sys, itertools
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from fractions import Fraction as F
PHI = (1 + 5 ** .5) / 2

def weil(M, N):
    """the metaplectic (Weil) operator of M in SL2(Z/N), N odd, on l2(Z/N): U_jk = N^(-1/2) w^((a k^2 - 2 j k + d j^2)/(2b)) for b invertible"""
    a, b, c, d = [x % N for x in (M[0][0], M[0][1], M[1][0], M[1][1])]
    binv = pow(b, -1, N); h = pow(2, -1, N); w = cmath.exp(2j * math.pi / N)
    return [[w ** ((h * binv * (a * k * k - 2 * j * k + d * j * j)) % N) / math.sqrt(N) for k in range(N)] for j in range(N)]
def cmul(X, Y): n = len(X); return [[sum(X[i][k] * Y[k][j] for k in range(n)) for j in range(n)] for i in range(n)]
def proj_order(U, cap=400):
    n = len(U); P = U
    for k in range(1, cap):
        # scalar multiple of the identity?
        s = P[0][0]
        if abs(abs(s) - 1) < 1e-8 and all(abs(P[i][j] - (s if i == j else 0)) < 1e-8 for i in range(n) for j in range(n)): return k
        P = cmul(P, U)
    return None
def mat_order(M, N):
    R = [[1, 0], [0, 1]]
    for k in range(1, 10000):
        R = [[(R[i][0] * M[0][j] + R[i][1] * M[1][j]) % N for j in range(2)] for i in range(2)]
        if R == [[1, 0], [0, 1]]: return k
def cat_quantum():
    A2 = [[1, 1], [1, 2]]
    rows = []
    for N in range(3, 26, 2):
        U = weil(A2, N)
        un = max(abs(sum(U[i][k] * U[j][k].conjugate() for k in range(N)) - (i == j)) for i in range(N) for j in range(N))
        q, c = proj_order(U), mat_order(A2, N)
        rows.append((N, q, c, round(un, 14)))
    print('QUANTUM CAT MAP: (N, quantum period up to phase, classical period of A^2 mod N, unitarity defect):', rows)
    return all(q == c and u < 1e-10 for N, q, c, u in rows) and [c for N, q, c, u in rows] == [4, 10, 8, 12, 5, 14, 20, 18, 9, 8, 24, 50]

def pell_velocity():
    # the velocity of A^(2n) as a boost is v_n = sqrt5 F_2n / L_2n; Einstein addition gives v_(m+n)
    def fib(n):
        a, b = 0, 1
        for _ in range(n): a, b = b, a + b
        return a
    luc = lambda n: fib(n - 1) + fib(n + 1)
    ok = True
    for m in range(1, 25):
        for n in range(1, 25):
            # (u + v)/(1 + uv) with u = sqrt5 x, v = sqrt5 y: = sqrt5 (x + y)/(1 + 5 x y)
            x, y = F(fib(2 * m), luc(2 * m)), F(fib(2 * n), luc(2 * n))
            ok = ok and (x + y) / (1 + 5 * x * y) == F(fib(2 * (m + n)), luc(2 * (m + n)))
    print('PELL BOOSTS: Einstein addition of the velocities sqrt5 F_2m/L_2m and sqrt5 F_2n/L_2n gives sqrt5 F_2(m+n)/L_2(m+n), exactly, m, n = 1..24:', ok)
    return ok

def coxeter_adjoint():
    import bridges as b
    I, B, Bq, res = b.e8_icosian(); G = res['phi/sqrt5'][2]
    roots = [tuple(r) for r in b.short_vectors(G, 2)]
    T = lambda M: [list(r) for r in zip(*M)]
    lin = lambda f: T([b.solve_int(B, b.coords(f(x))) for x in Bq])
    def qord(l):
        y = l; n = 1
        while y != (b.K(1), b.K(0), b.K(0), b.K(0)): y = tuple(b.qmul(y, l)); n += 1
        return n
    C = None
    for l in [x for x in I if qord(x) == 10]:
        for r in [x for x in I if qord(x) == 3]:
            M = lin(lambda x: b.qmul(b.qmul(l, x), r))
            if b.charpoly(M) == [1, 1, 0, -1, -1, -1, 0, 1, 1]: C = M; break
        if C: break
    ap = lambda M, v: tuple(sum(M[i][j] * v[j] for j in range(8)) for i in range(8))
    rs = set(roots); seen = set(); orbits = []
    for r in roots:
        if r in seen: continue
        o = []; x = r
        while x not in seen:
            seen.add(x); o.append(x); x = ap(C, x)
        orbits.append(len(o))
    closed = all(ap(C, r) in rs for r in roots)
    # eigenvalue multiplicities on the 248-dimensional adjoint: each root orbit of length 30 is the regular representation of Z/30;
    # on the Cartan subalgebra C has eigenvalues zeta^m for the exponents m = 1, 7, 11, 13, 17, 19, 23, 29
    exps = {1, 7, 11, 13, 17, 19, 23, 29}
    mult = [len(orbits) + (1 if k in exps else 0) for k in range(30)]
    print('COXETER GRADING OF E8: C permutes the 240 roots in', len(orbits), 'orbits of lengths', sorted(set(orbits)), '| closed on the roots:', closed,
          '| on the 248-dimensional adjoint the eigenvalue exp(2 pi i k/30) has multiplicity 8 + [k an exponent]: total', sum(mult))
    # the law in the grading: I + C^12 + C^-12 acts on the root orbit as phi on the degrees k with cos(2 pi 12 k/30) = (phi - 1)/2 ...
    deg_phi = [k for k in range(30) if abs(1 + 2 * math.cos(2 * math.pi * 12 * k / 30) - PHI) < 1e-9]
    deg_psi = [k for k in range(30) if abs(1 + 2 * math.cos(2 * math.pi * 12 * k / 30) + 1 / PHI) < 1e-9]
    print('  the law I + C^12 + C^-12 is phi on the degrees', deg_phi, 'and -1/phi on', deg_psi, '| the exponents of E8 split', sorted(exps & set(deg_phi)), '|', sorted(exps & set(deg_psi)))
    return closed and len(orbits) == 8 and set(orbits) == {30} and sum(mult) == 248 and len(exps & set(deg_phi)) == 4

def penrose_series():
    import io, contextlib
    errs = []
    for R in (8, 16, 24, 32, 48):
        f = io.StringIO()
        with contextlib.redirect_stdout(f): ok = penrose(R)
        t = f.getvalue(); th = int(t.split('): ')[1].split(' thick')[0]); tn = int(t.split(' and ')[1].split(' thin')[0])
        errs.append((R, th, tn, abs(th / tn - PHI)))
    print('PENROSE SERIES (finite patches; the limit is phi): ' + '; '.join('R %d: %d/%d, error %.1e' % e for e in errs))
    return ok and errs[-1][3] < 1e-3

def penrose(R=12.0):
    # de Bruijn pentagrid: five families of lines x . e_k + g_k in Z, sum g_k = 0 generic; each intersection of families r, s is one rhombus,
    # thick when |r - s| = 1 or 4 (angle 72 degrees), thin when 2 or 3 (36 degrees)
    e = [(math.cos(2 * math.pi * k / 5), math.sin(2 * math.pi * k / 5)) for k in range(5)]
    g = [0.1234, 0.2718, -0.1414, 0.0577]; g.append(-sum(g))
    thick = thin = 0
    K = int(R) + 3
    for r, s in itertools.combinations(range(5), 2):
        det = e[r][0] * e[s][1] - e[r][1] * e[s][0]
        for kr in range(-K, K + 1):
            for ks in range(-K, K + 1):
                x = ((kr - g[r]) * e[s][1] - (ks - g[s]) * e[r][1]) / det
                y = (e[r][0] * (ks - g[s]) - e[s][0] * (kr - g[r])) / det
                if x * x + y * y < R * R:
                    if (s - r) in (1, 4): thick += 1
                    else: thin += 1
    infl = [[2, 1], [1, 1]]
    A2 = [[1, 1], [1, 2]]; swap = [[0, 1], [1, 0]]
    conj = [[sum(swap[i][k] * sum(A2[k][l] * swap[l][j] for l in range(2)) for k in range(2)) for j in range(2)] for i in range(2)] == infl
    print('PENROSE (pentagrid, radius %g): %d thick and %d thin rhombi, ratio %.6f (phi = %.6f; exact density ratio sin 72/sin 36 = phi) | the inflation matrix [[2,1],[1,1]] is A^2 conjugated by the swap: %s'
          % (R, thick, thin, thick / thin, PHI, conj))
    return conj and abs(thick / thin - PHI) < 0.02 and abs(math.sin(2 * math.pi / 5) / math.sin(math.pi / 5) - PHI) < 1e-12

def pr001():
    import dsi
    ok, lines = dsi.pr001()
    print('PR-001 (sealed in seq_0170, tested after): ' + lines[0] + ' ... ' + lines[-1] + ' | PASS' if ok else ' | FAIL')
    return ok

def pr002():
    import dsi
    ok, lines = dsi.pr002()
    print('PR-002 (sealed in seq_0172, tested after): ' + ' | '.join(lines) + (' | PASS' if ok else ' | FAIL'))
    return ok

def braid_mod11():
    """PR-003 setup, exercised only on the braid relation: the Fibonacci representation of B_3 in the gauge F' = [[1/phi, 1/phi], [1, -1/phi]],
    sigma1 = diag(zeta^-4, zeta^3), sigma2 = F' sigma1 F', zeta = exp(pi i/5); over Z[zeta_10]; at the prime above 11 with zeta -> 2 in F11
    (2 has order 10 mod 11), 1/phi = zeta^2 + zeta^-2 -> 4 + 3 = 7 and phi -> 8."""
    p = 11; z = 2; zi = pow(z, -1, p)
    iphi = (pow(z, 2, p) + pow(zi, 2, p)) % p; phi = (1 + iphi) % p
    assert (phi * phi - phi - 1) % p == 0 and (phi * iphi) % p == 1
    Fp = [[iphi, iphi], [1, (-iphi) % p]]
    s1 = [[pow(zi, 4, p), 0], [0, pow(z, 3, p)]]
    mul = lambda X, Y: [[(X[i][0] * Y[0][j] + X[i][1] * Y[1][j]) % p for j in range(2)] for i in range(2)]
    s2 = mul(mul(Fp, s1), Fp)
    FF = mul(Fp, Fp)
    braid = mul(mul(s1, s2), s1) == mul(mul(s2, s1), s2)
    print('PR-003 SETUP: at the prime above 11, phi -> %d, 1/phi -> %d; F\'^2 = I: %s; braid relation s1 s2 s1 = s2 s1 s2 mod 11: %s; s1 = %s, s2 = %s' % (phi, iphi, FF == [[1, 0], [0, 1]], braid, s1, s2))
    # complex check of the gauge: F' satisfies F'^2 = I and the braid relation over C
    zc = cmath.exp(1j * math.pi / 5)
    Fc = [[1 / PHI, 1 / PHI], [1, -1 / PHI]]; S1 = [[zc ** -4, 0], [0, zc ** 3]]
    cm = lambda X, Y: [[sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    S2 = cm(cm(Fc, S1), Fc)
    d = max(abs(a - c) for r1, r2 in zip(cm(cm(S1, S2), S1), cm(cm(S2, S1), S2)) for a, c in zip(r1, r2))
    print('  over C in the gauge F\': braid relation to %.1e' % d)
    return FF == [[1, 0], [0, 1]] and braid and d < 1e-12

KEYS = [('quantum-cat', cat_quantum), ('pell', pell_velocity), ('coxeter-adjoint', coxeter_adjoint), ('penrose', penrose_series), ('pr001', pr001), ('pr002', pr002), ('braid-setup', braid_mod11)]
if __name__ == '__main__':
    import io, contextlib
    if sys.argv[1:] == ['--selftest']:
        R = []
        for k, f in KEYS:
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf): ok = f()
            R.append(ok); print('%s: %s %s' % (k, buf.getvalue().strip().split(chr(10))[0][:150], 'PASS' if ok else 'FAIL'))
        print('CONSTRUCTIONS SELFTEST: %d of %d | %s' % (sum(R), len(R), 'PASS' if all(R) else 'FAIL')); sys.exit(0 if all(R) else 1)
    print(__doc__); sys.exit(2)
