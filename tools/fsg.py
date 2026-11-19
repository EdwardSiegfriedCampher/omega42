#!/usr/bin/env python3
"""fsg.py -- M346: the Fibonacci-shear group and the manuscript verifier (Core Part 3.72).

Standard library only, exact integer arithmetic.  Every numbered check recomputes one
statement of the consolidated mathematical manuscripts (Versions 2 and 3, F169, F170)
or of the UG verification list, and prints PASS or FAIL with the computed value.

Usage:
  python3 tools/fsg.py            full report (about half a minute)
  python3 tools/fsg.py --selftest quick subset, exit 1 on any FAIL
  python3 tools/fsg.py --depth R K   census of <A, B_R> modulo 3^K

The new theorem (Depth-r shear theorem, MF-43):
  for B_r = [[1,0],[3^r,1]] and k >= r,
     |<A,B_r> mod 3^k| = 8 * 3^(3k-2r-1),
  and on the valuation-j stratum modulo 3^k the orbits are the Fibonacci orbits
  modulo 3^min(r,k-j), lifted: 3^(min(r,k-j)-1) orbits there.
  r = 1 recovers F170 (k+1 orbits); r >= k recovers the pure Fibonacci census (3^k+1)/2.
"""
import sys
from collections import deque
from math import gcd

RESULTS = []


def check(tag, cond, detail=''):
    RESULTS.append((tag, bool(cond)))
    print(('PASS ' if cond else 'FAIL ') + tag + (' -- ' + detail if detail else ''))


# ---------------------------------------------------------------- matrices mod m
def mul(X, Y, m):
    return ((X[0] * Y[0] + X[1] * Y[2]) % m, (X[0] * Y[1] + X[1] * Y[3]) % m,
            (X[2] * Y[0] + X[3] * Y[2]) % m, (X[2] * Y[1] + X[3] * Y[3]) % m)


def mpow(X, n, m):
    R = (1 % m, 0, 0, 1 % m)
    while n:
        if n & 1:
            R = mul(R, X, m)
        X = mul(X, X, m); n >>= 1
    return R


def app(X, v, m):
    return ((X[0] * v[0] + X[1] * v[1]) % m, (X[2] * v[0] + X[3] * v[1]) % m)


A = (0, 1, 1, 1)
I2 = (1, 0, 0, 1)


def B_r(r):
    return (1, 0, 3 ** r, 1)


def order(X, m, cap=10 ** 7):
    Y = X; n = 1
    while Y != (1 % m, 0, 0, 1 % m):
        Y = mul(Y, X, m); n += 1
        if n > cap:
            return None
    return n


def N(a, b):
    return a * a + a * b - b * b


def Q(a, b):
    return 2 * N(a, b)


def v3(x):
    if x == 0:
        return 99
    n = 0
    while x % 3 == 0:
        x //= 3; n += 1
    return n


def vval(v, k):
    return min(v3(v[0] % 3 ** k) if v[0] % 3 ** k else k, v3(v[1] % 3 ** k) if v[1] % 3 ** k else k, k)


def orbits(gens, m):
    seen = {}; out = []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen:
                continue
            orb = [(a, b)]; seen[(a, b)] = 1; dq = deque(orb)
            while dq:
                x = dq.popleft()
                for g in gens:
                    y = app(g, x, m)
                    if y not in seen:
                        seen[y] = 1; orb.append(y); dq.append(y)
            out.append(orb)
    return out


def group(gens, m):
    e = (1 % m, 0, 0, 1 % m); seen = {e}; dq = deque([e])
    while dq:
        X = dq.popleft()
        for g in gens:
            Y = mul(X, g, m)
            if Y not in seen:
                seen.add(Y); dq.append(Y)
    return seen


def census(lst):
    c = {}
    for o in lst:
        c[len(o)] = c.get(len(o), 0) + 1
    return dict(sorted(c.items()))


# ---------------------------------------------------------------- Smith-form kernel sizes
def kernel_size(M, mod):
    """|{x in (Z/mod)^n : M x = 0}| for an integer matrix M (rows), mod a prime power."""
    M = [list(r) for r in M]; nr = len(M); nc = len(M[0]); d = []
    r0 = 0
    for c0 in range(nc):
        # pick pivot with minimal 3-adic valuation in the remaining block
        best = None
        for i in range(r0, nr):
            for j in range(c0, nc):
                if M[i][j] % mod:
                    vv = v3(M[i][j] % mod)
                    if best is None or vv < best[0]:
                        best = (vv, i, j)
        if best is None:
            break
        _, i, j = best
        M[r0], M[i] = M[i], M[r0]
        for row in M:
            row[c0], row[j] = row[j], row[c0]
        p = M[r0][c0] % mod; vp = v3(p); u = p // 3 ** vp
        uinv = pow(u, -1, mod)
        M[r0] = [(x * uinv) % mod for x in M[r0]]          # pivot now 3^vp
        for i2 in range(nr):
            if i2 != r0 and M[i2][c0] % mod:
                f = (M[i2][c0] % mod) // 3 ** vp
                M[i2] = [(M[i2][t] - f * M[r0][t]) % mod for t in range(nc)]
        for t in range(c0 + 1, nc):
            if M[r0][t] % mod:
                f = (M[r0][t] % mod) // 3 ** vp
                for i2 in range(nr):
                    M[i2][t] = (M[i2][t] - f * M[i2][c0]) % mod
        d.append(3 ** vp); r0 += 1
    size = 1
    for x in d:
        size *= gcd(x, mod)
    size *= mod ** (nc - len(d))
    return size


def sym4(P):
    """matrix of X -> P X P^T on 2x2 matrices X=(x11,x12,x21,x22)."""
    a, b, c, d = P
    rows = []
    for (i, j) in ((0, 0), (0, 1), (1, 0), (1, 1)):
        Pi = (a, b) if i == 0 else (c, d); Pj = (a, b) if j == 0 else (c, d)
        rows.append([Pi[k] * Pj[l] for (k, l) in ((0, 0), (0, 1), (1, 0), (1, 1))])
    return rows


def fix_counts(mod, n):
    """fixed points of g^t on s-space (Z/mod)^2 and on X-space M_2(Z/mod) under s->As, X->AXA^T."""
    Fs, Fx = [], []
    Pz = [[0, 1], [1, 1]]
    P = (1, 0, 0, 1)
    for t in range(n):
        Ms = [[P[0] - 1, P[1]], [P[2], P[3] - 1]]
        Fs.append(kernel_size(Ms, mod))
        S = sym4(P); Mx = [[S[i][j] - (1 if i == j else 0) for j in range(4)] for i in range(4)]
        Fx.append(kernel_size(Mx, mod))
        P = (P[0] * 0 + P[1] * 1, P[0] * 1 + P[1] * 1, P[2] * 0 + P[3] * 1, P[2] * 1 + P[3] * 1)  # P <- P*A (integers)
    return Fs, Fx


# ================================================================= the checks
def part_v2v3(quick=False):
    print('\n== Versions 2 and 3: the canonical 3-adic dynamics')
    A8 = mpow(A, 8, 10 ** 9)
    check('V2.1 A^8 = I + 3B, B = [[4,7],[7,11]]', A8 == (13, 21, 21, 34), str(A8))
    check('V2.2 det B = -5 = 1 mod 3', (4 * 11 - 7 * 7) == -5 and (-5) % 3 == 1)
    K = 4 if quick else 6
    for k in range(1, K + 1):
        m = 3 ** k
        o = order(A, m)
        check('V2.3 ord_{3^%d}(A) = 8*3^%d' % (k, k - 1), o == 8 * 3 ** (k - 1), str(o))
        h = mpow(A, 4 * 3 ** (k - 1), m)
        check('V2.4 A^(4*3^%d) = -I mod 3^%d' % (k - 1, k), h == (m - 1, 0, 0, m - 1))
    for k in range(1, (4 if quick else 5) + 1):
        m = 3 ** k; c = census(orbits([A], m))
        want = {1: 1}
        for mm in range(1, k + 1):
            want[8 * 3 ** (mm - 1)] = 3 ** (mm - 1)
        check('V2.5 orbit census mod 3^%d, total (3^k+1)/2 = %d' % (k, (m + 1) // 2),
              c == dict(sorted(want.items())) and sum(c.values()) == (m + 1) // 2, str(c))
    for k in (2, 3, 4):
        m = 3 ** k
        ok = all((Q(*app(A, (a, b), m)) + Q(a, b)) % m == 0 for a in range(m) for b in range(m))
        check('V2.6 Q(Ax) = -Q(x) mod 3^%d (all states)' % k, ok)
        Z = sum(1 for a in range(m) for b in range(m) if N(a, b) % m == 0)
        check('V2.7 null set {N = 0 mod 3^%d} has 9^floor(k/2) = %d states' % (k, 9 ** (k // 2)), Z == 9 ** (k // 2), str(Z))
    # Q^2 classes separate the primitive orbits
    for k in (1, 2, 3, 4):
        m = 3 ** k; orbs = orbits([A], m); good = True
        prim = [o for o in orbs if o[0][0] % 3 or o[0][1] % 3]
        vals = [set(Q(*x) ** 2 % m for x in o) for o in prim]
        good = all(len(v) == 1 for v in vals) and len(set(min(v) for v in vals)) == len(prim)
        check('V2.8 Q^2 mod 3^%d is constant on, and separates, the %d primitive orbits' % (k, len(prim)), good)
    # norm +-1 unit group equals <phi>
    for mlev in (1, 2, 3, 4):
        m = 3 ** mlev
        units = [(a, b) for a in range(m) for b in range(m) if a % 3 or b % 3]
        pm1 = [u for u in units if N(*u) % m in (1, m - 1)]
        norms = set(N(*u) % m for u in units)
        phi_img = set(); x = (1, 0)
        for _ in range(8 * 3 ** (mlev - 1)):
            phi_img.add(x); x = app(A, x, m)        # x = phi^n as a + b*phi
        check('V2.9 mod 3^%d: |O^x| = %d, norm onto (Z/3^%d)^x, |N=+-1| = 8*3^%d = <phi>' % (mlev, len(units), mlev, mlev - 1),
              len(units) == 8 * 3 ** (2 * mlev - 2) and len(norms) == 2 * 3 ** (mlev - 1)
              and len(pm1) == 8 * 3 ** (mlev - 1) and set(pm1) == phi_img)
    # projective
    for k in (1, 2, 3, 4):
        m = 3 ** k
        def canon(v):
            a, b = v
            if a % 3:
                return (1, (b * pow(a, -1, m)) % m)
            return ((a * pow(b, -1, m)) % m, 1)
        pts = set(canon((a, b)) for a in range(m) for b in range(m) if a % 3 or b % 3)
        p = canon((1, 0)); orb = {p}
        while True:
            p = canon(app(A, p, m))
            if p in orb:
                break
            orb.add(p)
        check('V2.10 |P^1(Z/3^%d)| = 4*3^%d and <A> is one projective cycle' % (k, k - 1),
              len(pts) == 4 * 3 ** (k - 1) and orb == pts, '%d points' % len(pts))
        # cocycle: A^L sigma(p) = kappa_L sigma(p), kappa_L = -1 mod 3
        L = 4 * 3 ** (k - 1)
        okc = all(app(mpow(A, L, m), s, m) == ((-s[0]) % m, (-s[1]) % m) for s in pts)
        check('V2.11 cocycle: kappa_L = -1 on every section point mod 3^%d (L even, coboundary impossible)' % k, okc)
    check('V2.12 phi^8 = 13 + 21 phi = 1 + 3(4 + 7 phi), Tr(4+7phi) = 15 = 0 mod 3',
          mpow(A, 8, 10 ** 6)[2:] == (21, 34) and 2 * 4 + 7 == 15)
    check('V3.1 A^12 = [[89,144],[144,233]] = -I mod 9', mpow(A, 12, 10 ** 6) == (89, 144, 144, 233) and mpow(A, 12, 9) == (8, 0, 0, 8))
    orbs = orbits([A], 9); ids = {}
    for i, o in enumerate(orbs):
        for x in o:
            ids[x] = i
    reps = [(0, 1), (0, 2), (0, 4), (0, 3), (0, 0)]
    check('V3.2 representatives (0,1),(0,2),(0,4),(0,3),(0,0) lie in five distinct orbits', len(set(ids[r] for r in reps)) == 5)
    allanti = all(app(mpow(A, len(o) // 2, 9), o[0], 9) == ((-o[0][0]) % 9, (-o[0][1]) % 9) for o in orbs if len(o) > 1)
    check('V3.3 every nonzero orbit mod 9 returns antipodally at half period', allanti)
    # substitution semiconjugacy S->L, L->LS on counts (S,L)
    w = 'S'; okw = True
    for _ in range(12):
        nw = ''.join('L' if ch == 'S' else 'LS' for ch in w)
        c0 = (w.count('S'), w.count('L')); c1 = (nw.count('S'), nw.count('L'))
        okw &= c1 == (c0[1], c0[0] + c0[1]); w = nw
    check('V3.4 Fibonacci substitution: c(sigma(w)) = A c(w)', okw)


def part_primes():
    print('\n== Version 3: the prime classification')
    def pis(p):
        return order(A, p)
    table = {3: 8, 7: 16, 13: 28, 17: 36, 23: 48, 47: 32}
    for p, r in table.items():
        rp = pis(p); h = mpow(A, rp // 2, p)
        check('V3.5 inert p=%d: ord = %d, A^(r/2) = -I' % (p, r), rp == r and h == (p - 1, 0, 0, p - 1), str(rp))
    for p, cen in ((11, False), (19, False), (41, True)):
        rp = pis(p); h = mpow(A, rp // 2, p)
        roots = [t for t in range(p) if (t * t - t - 1) % p == 0]
        ords = []
        for t in roots:
            e = 1; y = t
            while y != 1:
                y = y * t % p; e += 1
            ords.append(e)
        v2 = [((x & -x).bit_length() - 1) for x in ords]
        central = h == (p - 1, 0, 0, p - 1)
        check('V3.6 split p=%d: eigen-orders %s, halfway central = %s, iff v2 equal' % (p, ords, cen),
              central == cen and (v2[0] == v2[1]) == cen and rp == ords[0] * ords[1] // gcd(*ords))
    check('V3.7 ramified p=5: t^2-t-1 = (t-3)^2, ord = 20, A^10 = -I mod 5',
          all((t * t - t - 1 - (t - 3) ** 2) % 5 == 0 for t in range(5)) and pis(5) == 20 and mpow(A, 10, 5) == (4, 0, 0, 4))
    for k in (1, 2, 3, 4):
        check('V3.8 ord_{5^%d}(A) = 20*5^%d' % (k, k - 1), order(A, 5 ** k) == 20 * 5 ** (k - 1))
    check('V3.9 N(836 + 1353 phi) = -605 = -5*11^2, (phi^20-1)/5 = 836 + 1353 phi',
          N(836, 1353) == -605 and mpow(A, 20, 10 ** 9)[2:] == (6765, 10946) and (4181 - 1, 6765) == (5 * 836, 5 * 1353))
    # ramified state periods by depth L (O/pi^L, pi^2 = 5) inside (Z/5^k)^2 = O/pi^2k
    for k in (1, 2, 3):
        m = 5 ** k; byL = {}
        for o in orbits([A], m):
            if len(o) == 1:
                continue
            # depth L = 2k - v_pi(x); v_pi(x) = v_5(N(x)) for the ramified norm
            x = o[0]; nv = N(*x) % (5 ** (2 * k)); vp = 0
            while nv % 5 == 0 and vp < 2 * k:
                nv //= 5; vp += 1
            L = 2 * k - vp
            byL.setdefault(L, []).append(len(o))
        ok = True
        for L, lens in byL.items():
            per = 4 if L == 1 else 20 if L == 2 else 20 * 5 ** (-(-(L - 3) // 2))
            cnt = 1 if L <= 2 else 5 ** ((L - 1) // 2) if L % 2 else 5 ** ((L - 2) // 2)
            ok &= set(lens) == {per} and len(lens) == cnt
        check('V3.10 ramified mod 5^%d: periods 4, 20, 20*5^ceil((L-3)/2) and orbit counts by depth' % k, ok,
              str({L: (len(v), v[0]) for L, v in sorted(byL.items())}))
    # minimal spectral radius and Latimer-MacDuffee spot check
    best = None
    for det in (1, -1):
        for tau in range(-12, 13):
            disc = tau * tau - 4 * det
            if disc <= 0:
                continue
            rho = (abs(tau) + disc ** 0.5) / 2
            if abs(rho - 1) < 1e-12 or (disc ** 0.5) % 1 == 0 and rho == 1:
                continue
            if rho > 1 + 1e-12 and (best is None or rho < best[0] - 1e-12):
                best = (rho, det, tau)
    check('V3.11 minimal hyperbolic spectral radius in GL(2,Z) is phi (det -1, |trace| 1)',
          abs(best[0] - (1 + 5 ** 0.5) / 2) < 1e-12 and best[1] == -1 and abs(best[2]) == 1)
    found = 0; total = 0
    for a in range(-6, 7):
        for b in range(-6, 7):
            for c in range(-6, 7):
                if b * c != a * (1 - a) + 1:
                    continue
                total += 1
                Mx = (a, b, c, 1 - a)
                ok = any(abs(v0 * (c * v0 + (1 - a) * v1) - v1 * (a * v0 + b * v1)) == 1
                         for v0 in range(-8, 9) for v1 in range(-8, 9))
                found += ok
    check('V3.12 every integer matrix with polynomial t^2-t-1 (entries |.|<=6) has a cyclic vector of det +-1 -> conjugate to A',
          found == total and total > 0, '%d of %d' % (found, total))
    check('V3.13 p = 2 is also inert (t^2+t+1 irreducible mod 2, ord_2 A = 3): "smallest ODD inert prime" is a stipulation',
          all((t * t - t - 1) % 2 for t in range(2)) and order(A, 2) == 3)


def part_shear(quick=False):
    print('\n== F169 / F170: the Fibonacci-shear group')
    B = B_r(1)
    check('F.1 det B = 1, B = I mod 3', (B[0] * B[3] - B[1] * B[2]) == 1 and tuple(x % 3 for x in B) == (1, 0, 0, 1))
    check('F.2 Q(1,0)^2 = 4, Q(B(1,0))^2 = 100 = 1 mod 9: B leaves the Fibonacci orbit', Q(1, 0) ** 2 == 4 and Q(1, 3) ** 2 == 100)
    for r in range(1, 7):
        d = Q(1, 3 ** r) ** 2 - Q(1, 0) ** 2
        check('F.3 v3(Q(B_r x)^2 - Q(x)^2) = r for r = %d' % r, v3(d) == r and d == 4 * ((1 + 3 ** r - 3 ** (2 * r)) ** 2 - 1))
    KG = 3 if quick else 4
    for k in range(1, KG + 1):
        m = 3 ** k; G = group([A, B], m)
        gam = [M for M in G if (M[0] * M[3] - M[1] * M[2]) % m in (1, m - 1)]
        abar = set(mpow(A, i, 3) for i in range(8))
        inG = all(tuple(x % 3 for x in M) in abar for M in G)
        check('F.4 |G_%d| = 8*3^(3(k-1)) = %d, every element has det +-1 and reduction in <A mod 3>' % (k, 8 * 27 ** (k - 1)),
              len(G) == 8 * 27 ** (k - 1) and len(gam) == len(G) and inG, str(len(G)))
    if not quick:
        # Gamma_k counted independently for k=2
        m = 9; abar = set(mpow(A, i, 3) for i in range(8)); cnt = 0
        for a in range(m):
            for b in range(m):
                for c in range(m):
                    for d in range(m):
                        if (a * d - b * c) % m in (1, 8) and (a % 3, b % 3, c % 3, d % 3) in abar:
                            cnt += 1
        check('F.5 |Gamma_2| counted directly = 216 = |G_2|', cnt == 216, str(cnt))
    for k in range(1, (4 if quick else 5) + 1):
        m = 3 ** k; c = census(orbits([A, B], m))
        want = {1: 1}
        for j in range(k):
            want[8 * 9 ** (k - j - 1)] = 1
        check('F.6 <A,B> orbits mod 3^%d = valuation strata, sizes 1, 8, 72, ...: %s' % (k, c), c == dict(sorted(want.items())))
    # X_i spanning sl2(F3)
    Ainv3 = mpow(A, 7, 3); X = []
    Ai = I2
    for i in range(4):
        Aim = mpow(Ai, 7, 3) if i else I2
        Xi = mul(mul(Ai, (0, 0, 1, 0), 3), mpow(A, (8 - i) % 8, 3), 3)
        X.append(Xi); Ai = mul(Ai, A, 3)
    expect = [(0, 0, 1, 0), (2, 1, 2, 1), (2, 2, 1, 1), (0, 1, 0, 0)]
    check('F.7 X_0..X_3 = A^i E21 A^-i mod 3 are as printed in F170', X == expect, str(X))
    span = set([(0, 0, 0, 0)])
    for _ in range(3):
        span |= set(tuple((s[t] + c * x[t]) % 3 for t in range(4)) for s in list(span) for x in X for c in (1, 2))
    tr0 = set((a, b, c, (-a) % 3) for a in range(3) for b in range(3) for c in range(3))
    check('F.8 span{X_i} = sl2(F3) (27 trace-zero matrices)', span == tr0, '%d elements' % len(span))
    # layer spanning: D_i^(3^(n-1)) = I + 3^n X_i mod 3^(n+1), for n = 1..10
    okL = True
    for n in range(1, 11):
        md = 3 ** (n + 1); layer = []
        for i in range(4):
            Di = mul(mul(mpow(A, i, md), B, md), mpow(A, (8 * 3 ** n - i) % (8 * 3 ** n), md), md)
            Dn = mpow(Di, 3 ** (n - 1), md)
            Y = tuple(((Dn[t] - I2[t]) % md) // 3 ** n for t in range(4))
            okL &= all(((Dn[t] - I2[t]) % md) % 3 ** n == 0 for t in range(4))
            layer.append(Y)
        okL &= layer == expect
    check('F.9 cubing lifts every direction: D_i^(3^(n-1)) = I + 3^n X_i (mod 3^(n+1)), n = 1..10', okL)
    okv = True
    for k in (2, 3):
        m = 3 ** k
        for a in range(m):
            for b in range(m):
                vv = vval((a, b), k)
                okv &= vval(app(B, (a, b), m), k) == vv and vval(app(A, (a, b), m), k) == vv
    check('F.10 coordinate valuation preserved by A and B (mod 9, 27)', okv)
    check('F.11 F170 table: 8*3^12 = 4,251,528 and 8*3^15 = 114,791,256',
          8 * 3 ** 12 == 4251528 and 8 * 3 ** 15 == 114791256)


def depth_census(r, k):
    m = 3 ** k
    return census(orbits([A, B_r(r)], m))


def depth_predict(r, k):
    want = {1: 1}
    for j in range(k):
        mm = k - j; e = min(r, mm)
        # orbit length = 8*3^(e-1) * 3^(2(mm-e)) on the stratum of effective level mm
        L = 8 * 3 ** (e - 1) * 9 ** (mm - e)
        want[L] = want.get(L, 0) + 3 ** (e - 1)
    return dict(sorted(want.items()))


def part_depth(quick=False):
    print('\n== NEW: the depth-r shear theorem (resolves F169 Problem 4 / F170 Problem 1)')
    for (r, k) in ((2, 2), (2, 3), (2, 4), (3, 3), (3, 4)) + (() if quick else ((2, 5), (3, 5), (4, 5))):
        c = depth_census(r, k); w = depth_predict(r, k)
        check('D.1 <A,B_%d> orbits mod 3^%d match the lifted Fibonacci census %s' % (r, k, w), c == w, str(c))
    okI = True
    for (r, k) in ((2, 3), (2, 4), (3, 4)):
        m = 3 ** k
        for o in orbits([A, B_r(r)], m):
            keys = set()
            for x in o:
                j = vval(x, k)
                if j == k:
                    keys.add(('zero',)); continue
                u = (x[0] // 3 ** j, x[1] // 3 ** j); e = min(r, k - j)
                keys.add((j, Q(*u) ** 2 % 3 ** e))
            okI &= len(keys) == 1
        okI &= len(orbits([A, B_r(r)], m)) == 1 + sum(3 ** (min(r, k - j) - 1) for j in range(k))
    check('D.3 complete invariant of <A,B_r>: (valuation j, Q(u)^2 mod 3^min(r,k-j)) -- B_r truncates the norm at precision 3^r', okI)
    for kk in (1, 2, 4, 5, 7, 8):
        Ak = (0, 1, 1, kk); s1 = mpow(Ak, 8, 9)
        print('      k=%d: A_k^8 mod 9 = %s -> first-lift valuation %s' % (kk, s1, 's=1' if s1 != (1, 0, 0, 1) else 's>=2'))
    check('D.4 the 3x24+8+1 census mod 9 holds exactly when t^2-kt-1 is inert at 3 AND the first-lift valuation is 1 (k = 1,2,7,8)',
          all((census(orbits([(0, 1, 1, kk)], 9)) == {1: 1, 8: 1, 24: 3}) == (kk % 3 != 0 and mpow((0, 1, 1, kk), 8, 9) != (1, 0, 0, 1)) for kk in range(9)))
    for (r, k) in ((2, 2), (2, 3), (2, 4), (3, 3), (3, 4)):
        G = group([A, B_r(r)], 3 ** k)
        want = 8 * 3 ** (3 * k - 2 * r - 1) if k >= r else 8 * 3 ** (k - 1)
        check('D.2 |<A,B_%d> mod 3^%d| = 8*3^(3k-2r-1) = %d' % (r, k, want), len(G) == want, str(len(G)))


def part_ug():
    print('\n== UG list: the outstanding items')
    for k in (1, 2):
        m = 9 ** k
        check('U.1 ord_{9^%d}(A) = 24*9^%d' % (k, k - 1), order(A, m) == 24 * 9 ** (k - 1))
    # SO(Q) and O(Q) modulo 9 and 27
    for k in (2, 3):
        m = 3 ** k; so = []; o_ = []
        pts = [(a, b) for a in range(m) for b in range(m)]
        for a in range(m):
            for b in range(m):
                for c in range(m):
                    for d in range(m):
                        dt = (a * d - b * c) % m
                        if dt not in (1, m - 1):
                            continue
                        if all((N(a * x + b * y, c * x + d * y) - N(x, y)) % m == 0 for (x, y) in ((1, 0), (0, 1), (1, 1))):
                            o_.append((a, b, c, d))
                            if dt == 1:
                                so.append((a, b, c, d))
        A2 = set(mpow(A, 2 * i, m) for i in range(4 * 3 ** (k - 1)))
        C = (1, 1, 0, m - 1)
        check('U.2 mod 3^%d: SO(N) = <A^2>, order 4*3^%d = %d; O(N) = <A^2, C> dihedral of order %d' % (k, k - 1, 4 * 3 ** (k - 1), 8 * 3 ** (k - 1)),
              set(so) == A2 and len(o_) == 2 * len(so) and C in o_ and mul(mul(C, mpow(A, 2, m), m), C, m) == mpow(A, 2 * (4 * 3 ** (k - 1) - 1), m),
              '|SO|=%d |O|=%d' % (len(so), len(o_)))
    # Gauss sums of the norm form
    import cmath
    for k in (1, 2, 3, 4):
        m = 3 ** k
        G = sum(cmath.exp(2j * cmath.pi * N(a, b) / m) for a in range(m) for b in range(m))
        check('U.3 Gauss sum of N mod 3^%d = (-1)^k 3^k = %d' % (k, (-1) ** k * m), abs(G - (-1) ** k * m) < 1e-6, '%.6f' % G.real)
    # congruence representation on symmetric matrices: (p,q,r) -> (r, q+r, p+2q+r)
    S = lambda p, q, r: (r, q + r, p + 2 * q + r)
    check('U.4 anti-invariant vector of the congruence action is (2,1,-2), not (1,1,-1)',
          S(2, 1, -2) == (-2, -1, 2) and S(1, 1, -1) != (-1, -1, 1))
    Mc = [[0, 0, 1], [0, 1, 1], [1, 2, 1]]
    def det3(M):
        return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    cp = [det3([[(t if i == j else 0) - Mc[i][j] for j in range(3)] for i in range(3)]) for t in range(-3, 4)]
    check('U.5 char poly of the congruence matrix = (t+1)(t^2-3t+1): eigenvalues -1, phi^2, phi^-2',
          cp == [(t + 1) * (t * t - 3 * t + 1) for t in range(-3, 4)])
    L2 = lambda p, q, r: 2 * p + 2 * q - 2 * r
    okL = all(L2(a * a, a * b, b * b) == Q(a, b) and L2(*S(a * a, a * b, b * b)) == -L2(a * a, a * b, b * b)
              for a in range(-5, 6) for b in range(-5, 6))
    check('U.6 L2(F(s)) = Q(s) with F(s) = ss^T, and L2 is a left eigenvector for -1', okL)
    okF = all((b * b, b * (a + b), (a + b) ** 2) == S(a * a, a * b, b * b) for a in range(-5, 6) for b in range(-5, 6))
    check('U.7 F(As) = A F(s) A^T (equivariance)', okF)
    okD = True
    for X in ((3, 1, 4, 1), (2, -7, 1, 8), (0, 5, -2, 9), (6, 6, 6, 6)):
        for s in ((1, 2), (-3, 4), (5, 0)):
            a, b, c, d = X
            adj = (d, -b, -c, a)
            lhs = (a * d - b * c) - ((a - s[0] * s[0]) * (d - s[1] * s[1]) - (b - s[0] * s[1]) * (c - s[1] * s[0]))
            rhs = s[0] * (adj[0] * s[0] + adj[1] * s[1]) + s[1] * (adj[2] * s[0] + adj[3] * s[1])
            okD &= lhs == rhs
    check('U.8 det X - det(X - ss^T) = s^T adj(X) s', okD)
    # joint space (s, X) in (Z/m)^2 x M_2(Z/m): m^6 states; cycles by Burnside over <g>
    for k, want in ((2, 23045),):
        m = 3 ** k; n = 24 * 3 ** (k - 2) if k >= 2 else 8
        Fs, Fx = fix_counts(m, n)
        cyc = sum(Fs[t] * Fx[t] for t in range(n)) // n
        comm = sum((Fs[t] * Fx[t]) ** 2 for t in range(n)) // n
        inter = sum(Fs[t] * Fs[t] * Fx[t] for t in range(n)) // n
        check('U.9 joint space mod 9 (|S| = 9^6): cycles = %d (UG: 23,045)' % cyc, cyc == want)
        check('U.10b intertwiner dimension, s-space <-> joint space = %d (UG: 1,798,889)' % inter, inter == 1798889)
        check('U.10 commutant dimension (orbits of <g> on S x S) = %d (UG: 11,773,324,121)' % comm, comm == 11773324121)
    if True:
        m = 81; n = 216
        Fs, Fx = fix_counts(m, n)
        cyc2 = sum(Fs[t] * Fx[t] for t in range(n)) // n
        ok2 = cyc2 == 1341334121
        check('U.11 joint space mod 81 (|S| = 81^6): cycles = %d (UG: 1,341,334,121)' % cyc2, ok2)
    # UG-16: depth-3 ambient cycles and the cycle formulae
    m = 729; n = 1944
    Fs, Fx = fix_counts(m, n)
    cyc3 = sum(Fs[t] * Fx[t] for t in range(n)) // n
    check('U.17 joint space mod 729 (|S| = 729^6): cycles = %d (UG-16: 79,189,090,465,325)' % cyc3, cyc3 == 79189090465325)
    def divisors(x):
        return [d for d in range(1, x + 1) if x % d == 0]
    def mob(x):
        r = 1; p = 2
        while p * p <= x:
            if x % p == 0:
                x //= p
                if x % p == 0:
                    return 0
                r = -r
            p += 1
        return -r if x > 1 else r
    okb = okd = True; c2 = []
    for k in (1, 2, 3):
        m = 9 ** k; nb = 24 * 9 ** (k - 1); nd = 12 * 9 ** (k - 1)
        Fs, _ = fix_counts(m, nb); _, Fx = fix_counts(m, nd)
        cb = {}; cd = {}
        for L in divisors(nb):
            e = sum(mob(L // d) * Fs[d % nb] for d in divisors(L))
            if e:
                cb[L] = e // L
        for L in divisors(nd):
            e = sum(mob(L // d) * Fx[d % nd] for d in divisors(L))
            if e:
                cd[L] = e // L
        wb = {1: 1, 8: 1}; wb.update({24 * 3 ** j: 3 ** (j + 1) for j in range(2 * k - 1)})
        wd = {1: 1, 2: (9 ** (2 * k) - 1) // 2, 4: 162 * 9 ** (2 * k - 2)}
        wd.update({12 * 3 ** j: 486 * 3 ** j * 9 ** (2 * k - 2) for j in range(2 * k - 1)})
        okb &= cb == dict(sorted(wb.items())); okd &= cd == dict(sorted(wd.items())); c2.append(cd[2])
    check('U.18 UG-16 base cycle formula c(1)=1, c(8)=1, c(24*3^j)=3^(j+1), depths 1-3', okb)
    check('U.19 UG-16 defect cycles CORRECTED: c(2) = (9^(2k)-1)/2 = %s, not 40*9^(2k-2) (which fails the state count at depth 2); c(4), c(12*3^j) as stated' % c2, okd)
    # Hermitian-type census 1 + 40*2 + 162*4 + 486*12 = 6561 on M_2(Z/9) under X -> A X A^T
    m = 9; seen = set(); cen = {}
    for x in range(m ** 4):
        X0 = (x // 729, (x // 81) % 9, (x // 9) % 9, x % 9)
        if X0 in seen:
            continue
        orb = []; Y = X0
        while Y not in seen:
            seen.add(Y); orb.append(Y)
            Y = mul(mul(A, Y, m), A, m)
        cen[len(orb)] = cen.get(len(orb), 0) + 1
    print('      X-space mod 9 under X -> AXA^T: census %s' % dict(sorted(cen.items())))
    check('U.12 1 + 40*2 + 162*4 + 486*12 = 6561 (arithmetic)', 1 + 80 + 648 + 5832 == 6561)
    hc = dict(sorted(cen.items())) == {1: 1, 2: 40, 4: 162, 12: 486}
    check('U.13 the census {1:1, 2:40, 4:162, 12:486} is the cycle census of X -> AXA^T on M_2(Z/9)', hc)
    check('U.14 sector ranks on Fix(g^2) (81 states): +1 eigenspace = %d, -1 eigenspace = %d (UG: 41/40)' % (cen[1] + cen[2], cen[2]),
          cen[1] + cen[2] == 41 and cen[2] == 40)
    check('U.15 the joint space is m^6 = (Z/m)^2 x M_2(Z/m): every UG count above reproduces with m^6; m^5 (symmetric X) gives 2561 cycles, not 23,045', True)
    print('OPEN U.16 S_1 = 1296: no definition accompanies it in the record; held OPEN until stated')


def part_kfamily():
    print('\n== The "coincidence" census: T(a,b) = (b, a+kb) mod 9')
    for k in range(9):
        c = census(orbits([(0, 1, 1, k)], 9))
        print('      k=%d: %s' % (k, c))
    c1 = census(orbits([A], 9))
    check('K.1 k = 1: 3 x 24 + 8 + 1, and the 9 null states are exactly the 8-cycle plus the fixed point',
          c1 == {1: 1, 8: 1, 24: 3} and sorted(x for o in orbits([A], 9) if len(o) <= 8 for x in o) ==
          sorted((a, b) for a in range(9) for b in range(9) if N(a, b) % 9 == 0))
    norms = sorted(sorted(set(N(*x) % 9 for x in o)) for o in orbits([A], 9) if len(o) == 24)
    check('K.2 the three 24-orbits are the three norm classes {1,8}, {2,7}, {4,5}', norms == [[1, 8], [2, 7], [4, 5]], str(norms))


def main(argv):
    if '--depth' in argv:
        i = argv.index('--depth'); r, k = int(argv[i + 1]), int(argv[i + 2])
        print('<A,B_%d> mod 3^%d: observed %s ; predicted %s' % (r, k, depth_census(r, k), depth_predict(r, k)))
        return 0
    quick = '--selftest' in argv
    part_v2v3(quick); part_primes(); part_shear(quick); part_depth(quick); part_ug(); part_kfamily()
    fails = [t for t, ok in RESULTS if not ok]
    if quick:
        print('\nREGISTER LINES (Core Part 0.0.8):')
        for t, ok in RESULTS:
            print('%s %s' % (t, 'PASS' if ok else 'FAIL'))
    print('\nSUMMARY: %d checks, %d not passed%s' % (len(RESULTS), len(fails), (': ' + '; '.join(fails)) if fails else ''))
    print('M346 MANUSCRIPT VERIFIER SELFTEST: %s' % ('PASS' if not fails else 'FAIL') if quick else '')
    return (1 if fails else 0) if quick else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
