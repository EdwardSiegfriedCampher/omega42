#!/usr/bin/env python3
"""foundations.py -- the extended mathematical foundations of Omega42 (Core Part 0.0.8; Companion Part 174).

Every test suggested for the H-42 and H-43 mathematics, run: the square root of -1 in Z_3[phi] lifted by Hensel's lemma to
any depth; the null cone of the 3 + 1 Hermitian space counted mod 9 and mod 81; the interval kept by X -> A X A^T mod 81;
the 4 x 4 Lorentz matrix of the law over the reals, proper and orthochronous; the Pauli algebra over Z[phi]/9 with i = phi^6; sector probabilities
kept for every basis state and for random states; the Hamiltonian of the law (principal logarithm) and exp(-iH) = U_T;
sector-preserving against sector-coupling evolution; coarse entropies for four partitions; and the Einstein tensor of the
Schwarzschild metric in the signature of the interval, vanishing.
    python3 tools/foundations.py              # the values
    python3 tools/foundations.py --selftest
Standard library only.
"""
import cmath, itertools, math, random, sys
def mphi(u, v, m): a, b = u; c, d = v; return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)
def hensel(k):
    """a square root of -1 in Z_3[phi] mod 3^k, lifted digit by digit from the root mod 3"""
    r = next((x, y) for x in range(3) for y in range(3) if mphi((x, y), (x, y), 3) == (2, 0))
    for j in range(2, k + 1):
        m, p = 3 ** j, 3 ** (j - 1)
        r = next(((r[0] + p * s) % m, (r[1] + p * t) % m) for s in range(3) for t in range(3)
                 if mphi(((r[0] + p * s) % m, (r[1] + p * t) % m), ((r[0] + p * s) % m, (r[1] + p * t) % m), m) == (m - 1, 0))
    return r
def null_count(m):
    sq = [x * x % m for x in range(m)]; cnt = {}
    for a in range(m):
        for b in range(m): cnt[(sq[a] + sq[b]) % m] = cnt.get((sq[a] + sq[b]) % m, 0) + 1
    two = cnt; diff = {}
    for t in range(m):
        for z in range(m): diff[(sq[t] - sq[z]) % m] = diff.get((sq[t] - sq[z]) % m, 0) + 1
    # t^2 - z^2 = x^2 + y^2
    return sum(diff[v] * two.get(v, 0) for v in diff)
def herm_act_ok(m, samples=20000, seed=1):
    rnd = random.Random(seed); I = hensel(1) if m == 3 else None
    # work in Z[i]/m with real A: X = [[t+z, x - iy], [x + iy, t - z]]; A X A^T for A = [[0,1],[1,1]]
    def iv(t, z, x, y): return (t * t - z * z - x * x - y * y) % m
    for _ in range(samples):
        t, z, x, y = (rnd.randrange(m) for _ in range(4))
        X = [[(t + z, 0), (x, -y)], [(x, y), (t - z, 0)]]
        A = [[0, 1], [1, 1]]
        Y = [[(sum(A[i][k] * X[k][l][0] * A[j][l] for k in range(2) for l in range(2)) % m,
               sum(A[i][k] * X[k][l][1] * A[j][l] for k in range(2) for l in range(2)) % m) for j in range(2)] for i in range(2)]
        h = pow(2, -1, m); t2 = (Y[0][0][0] + Y[1][1][0]) * h % m; z2 = (Y[0][0][0] - Y[1][1][0]) * h % m
        if Y[0][0][1] or Y[1][1][1] or iv(t2, z2, Y[1][0][0], Y[1][0][1]) != iv(t, z, x, y): return False
    return True
SIG = [[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]
def lorentz_matrix():
    A = [[0, 1], [1, 1]]; basis = [[[1, 0], [0, 1]]] + [list(map(list, s)) for s in SIG]
    def act(X): return [[sum(A[i][k] * X[k][l] * A[j][l] for k in range(2) for l in range(2)) for j in range(2)] for i in range(2)]
    def coords(X): return [((X[0][0] + X[1][1]) / 2).real, (X[1][0]).real, (X[1][0]).imag, ((X[0][0] - X[1][1]) / 2).real]
    return [[round(v, 12) for v in coords(act(B))] for B in basis]   # rows: images of e_t, e_x, e_y, e_z
def lorentz_ok(L):
    eta = [1, -1, -1, -1]
    G = [[sum(L[a][mu] * eta[mu] * L[b][mu] for mu in range(4)) for b in range(4)] for a in range(4)]
    det = det4(L)
    return all(abs(G[a][b] - (eta[a] if a == b else 0)) < 1e-9 for a in range(4) for b in range(4)), round(det, 9), L[0][0] > 0
def det4(M):
    if len(M) == 1: return M[0][0]
    return sum((-1) ** j * M[0][j] * det4([r[:j] + r[j + 1:] for r in M[1:]]) for j in range(len(M)))
def pauli_mod9():
    m = 9; i = (5, 8)                       # phi^6 = 5 + 8 phi, a square root of -1 in Z[phi]/9
    z0, one, mone = (0, 0), (1, 0), (8, 0); neg = lambda u: ((-u[0]) % m, (-u[1]) % m)
    sx = [[z0, one], [one, z0]]; sy = [[z0, neg(i)], [i, z0]]; sz = [[one, z0], [z0, mone]]
    def mm(X, Y): return [[tuple(sum(v) % m for v in zip(*[mphi(X[r][k], Y[k][c], m) for k in range(2)])) for c in range(2)] for r in range(2)]
    def sc(s, X): return [[mphi(s, e, m) for e in row] for row in X]
    I2 = [[one, z0], [z0, one]]
    ok = mm(sx, sx) == I2 and mm(sy, sy) == I2 and mm(sz, sz) == I2 and mm(sx, sy) == sc(i, sz) and mm(sy, sz) == sc(i, sx) and mm(sz, sx) == sc(i, sy)
    A = [[z0, one], [one, one]]; five = (5, 0)
    Adec = [[tuple((a + b) % m for a, b in zip(mphi(five, I2[r][c], m), (0, 0))) for c in range(2)] for r in range(2)]
    combo = [[tuple((p + q - s) % m for p, q, s in zip(mphi(five, I2[r][c], m), sx[r][c], mphi(five, sz[r][c], m))) for c in range(2)] for r in range(2)]
    return ok, combo == A
STATES = [(a, b) for a in range(9) for b in range(9)]
def T(s): return (s[1], (s[0] + s[1]) % 9)
def orbits():
    seen, out = set(), []
    for s in STATES:
        if s in seen: continue
        o, x = [], s
        while x not in seen: seen.add(x); o.append(x); x = T(x)
        out.append(o)
    return out
def sectors_kept():
    O = orbits(); idx = {x: j for j, o in enumerate(O) for x in o}
    for s in STATES:                                   # every basis state stays in its sector
        if idx[T(s)] != idx[s]: return False
    rnd = random.Random(7)
    for _ in range(100):
        psi = {x: complex(rnd.gauss(0, 1), rnd.gauss(0, 1)) for x in STATES}
        w = lambda p: [sum(abs(p[x]) ** 2 for x in o) for o in O]
        p1 = {T(x): v for x, v in psi.items()}
        if max(abs(a - b) for a, b in zip(w(psi), w(p1))) > 1e-9: return False
    return True
def hamiltonian():
    """the principal logarithm of U_T: on an orbit of length L the eigenvectors are the Fourier modes, eigenvalues e^(-2 pi i k/L);
    H has eigenvalues theta in (-pi, pi] with exp(-i H) = U_T (hbar = step = 1); checked on every basis state"""
    O = orbits(); worst = 0; spec = {}
    for o in O:
        L = len(o)
        for m0 in range(L):
            out = [0j] * L
            for k in range(L):
                lam = cmath.exp(-2j * math.pi * k / L); th = cmath.phase(lam) * -1      # lam = e^{-i th}
                th = -cmath.phase(lam)
                for n in range(L):
                    out[n] += cmath.exp(2j * math.pi * k * (n - m0) / L) / L * cmath.exp(-1j * th)
            target = (m0 + 1) % L
            worst = max(worst, max(abs(out[n] - (1 if n == target else 0)) for n in range(L)))
        for k in range(L):
            th = round(-cmath.phase(cmath.exp(-2j * math.pi * k / L)) / (2 * math.pi / 24), 6)
            spec[th] = spec.get(th, 0) + 1
    return worst, spec
def coupling():
    """a sector-preserving step (U_T) keeps each sector; a step that swaps the still point with one 8-cycle state moves weight"""
    O = orbits(); fixed = [o for o in O if len(o) == 1][0][0]; eight = [o for o in O if len(o) == 8][0][0]
    psi = {x: (1.0 if x == fixed else 0.0) for x in STATES}
    swap = {x: x for x in STATES}; swap[fixed], swap[eight] = eight, fixed
    p1 = {swap[x]: v for x, v in psi.items()}
    w = lambda p, o: sum(abs(p[x]) ** 2 for x in o)
    return w(psi, [fixed]), w(p1, [fixed])
def entropies():
    parts = {'first entry': lambda s: s[0], 'second entry': lambda s: s[1], 'norm class': lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9,
             'depth shell': lambda s: 0 if s == (0, 0) else (1 if s[0] % 3 == 0 and s[1] % 3 == 0 else 2)}
    out = {}
    for name, f in parts.items():
        pts = [(1, b) for b in range(9)]; H = []
        for _ in range(49):
            c = {}
            for p in pts: c[f(p)] = c.get(f(p), 0) + 1
            H.append(round(-sum(k / 9 * math.log(k / 9) for k in c.values()), 9)); pts = [T(p) for p in pts]
        per = next(k for k in range(1, 49) if all(H[i] == H[i + k] for i in range(49 - k)))
        out[name] = (per, min(H), max(H))
    return out
def schwarzschild_vacuum(r0=3.0, th0=1.1, M=1.0, h=1e-3):
    """Einstein tensor of ds^2 = (1-2M/r)dt^2 - dr^2/(1-2M/r) - r^2 dOmega^2 (signature of the interval), by central differences"""
    def g(x):
        t, r, th, ph = x; f = 1 - 2 * M / r
        return [[f, 0, 0, 0], [0, -1 / f, 0, 0], [0, 0, -r * r, 0], [0, 0, 0, -(r * math.sin(th)) ** 2]]
    def ginv(x): G = g(x); return [[1 / G[i][i] if i == j else 0 for j in range(4)] for i in range(4)]
    def dg(x, k):
        e = [0] * 4; e[k] = h; xp = [a + b for a, b in zip(x, e)]; xm = [a - b for a, b in zip(x, e)]
        return [[(g(xp)[i][j] - g(xm)[i][j]) / (2 * h) for j in range(4)] for i in range(4)]
    def Gam(x):
        gi = ginv(x); D = [dg(x, k) for k in range(4)]
        return [[[0.5 * sum(gi[a][s] * (D[b][s][c] + D[c][s][b] - D[s][b][c]) for s in range(4)) for c in range(4)] for b in range(4)] for a in range(4)]
    x0 = [0.0, r0, th0, 0.3]
    def dGam(k):
        e = [0] * 4; e[k] = h
        P = Gam([a + b for a, b in zip(x0, e)]); Mi = Gam([a - b for a, b in zip(x0, e)])
        return [[[(P[a][b][c] - Mi[a][b][c]) / (2 * h) for c in range(4)] for b in range(4)] for a in range(4)]
    G0 = Gam(x0); dG = [dGam(k) for k in range(4)]
    Ric = [[sum(dG[a][a][b][c] for a in range(4)) - sum(dG[c][a][b][a] for a in range(4))
            + sum(G0[a][a][l] * G0[l][b][c] for a in range(4) for l in range(4)) - sum(G0[a][c][l] * G0[l][b][a] for a in range(4) for l in range(4))
            for c in range(4)] for b in range(4)]
    gi = ginv(x0); Rs = sum(gi[i][i] * Ric[i][i] for i in range(4))
    Ein = [[Ric[i][j] - 0.5 * Rs * g(x0)[i][j] for j in range(4)] for i in range(4)]
    return max(abs(Ein[i][j]) for i in range(4) for j in range(4))
def values():
    L = lorentz_matrix(); w, spec = hamiltonian()
    return {'Hensel root of -1, depth 12': hensel(12), 'null vectors mod 9': null_count(9), 'null vectors mod 81': null_count(81),
            'interval kept mod 81 (20000 samples)': herm_act_ok(81), 'Lorentz matrix of A (rows e_t, e_x, e_y, e_z)': L,
            'in O(3,1), det, orthochronous': lorentz_ok(L), 'Pauli algebra mod 9 with i = phi^6; A = 5(I - sz) + sx': pauli_mod9(),
            'sectors kept, every basis state and 100 random states': sectors_kept(),
            'exp(-iH) = U_T, worst error': w, 'spectrum of H in units of 2 pi/24': dict(sorted(spec.items())),
            'still-point weight before and after a sector-coupling step': coupling(), 'coarse entropies (period, min, max)': entropies(),
            'Schwarzschild Einstein tensor, max entry': schwarzschild_vacuum()}
def selftest():
    v = values(); r = hensel(12); m = 3 ** 12
    t = [('a square root of -1 in Z_3[phi] lifted to depth 12', mphi(r, r, m) == (m - 1, 0)),
         ('621 null vectors mod 9', v['null vectors mod 9'] == 621),
         ('the null count mod 81 is computed', v['null vectors mod 81'] > 0),
         ('the interval is kept mod 81', v['interval kept mod 81 (20000 samples)']),
         ('A acts in SO+(3,1): proper and orthochronous', v['in O(3,1), det, orthochronous'] == (True, 1.0, True)),
         ('Pauli relations hold mod 9; A = 5(I - sz) + sx', v['Pauli algebra mod 9 with i = phi^6; A = 5(I - sz) + sx'] == (True, True)),
         ('sector probabilities kept', v['sectors kept, every basis state and 100 random states']),
         ('exp(-iH) = U_T on every basis state', v['exp(-iH) = U_T, worst error'] < 1e-9),
         ('a sector-coupling step moves weight', v['still-point weight before and after a sector-coupling step'] == (1.0, 0.0)),
         ('the five zero modes of H are the sector-uniform states', v['spectrum of H in units of 2 pi/24'].get(0.0, v['spectrum of H in units of 2 pi/24'].get(-0.0)) == 5),
         ('the norm-class entropy is constant', v['coarse entropies (period, min, max)']['norm class'][1] == v['coarse entropies (period, min, max)']['norm class'][2]),
         ('Schwarzschild solves G = 0 in the interval signature', v['Schwarzschild Einstein tensor, max entry'] < 1e-4)]
    for n, ok in t: print('%-56s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('FOUNDATIONS SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    for k, x in values().items(): print('%s: %s' % (k, x))
