#!/usr/bin/env python3
"""validation.py -- the period pattern of the trace map, its linear part at the fixed point, the census modulo 243, the exact
count of the Penrose zero modes, the diffraction of the Fibonacci chain and the weak-coupling gaps, and the scaling fit
(Companion Part 227; F220; APE-482).

  V1 period-pattern      the trace map's period equals the law's Pisano period modulo 2, 4, 8, 16, 32, 9, 27, 81, 18, 36, 48, 54,
                         72 and 108; it differs modulo 3, 6, 12, 24 and modulo every prime from 5 to 31 (exact)
  V2 fixed-point-law     at the fixed point (1, 1, 1) the trace map's linear part has characteristic polynomial (t + 1)(t^2 - 3t + 1):
                         the law's square A^2 beside -1 (exact)
  V3 census-243          modulo 243 the trace map is a bijection of period 648 with 144,816 orbits, counted by fixed points of its
                         powers and Moebius inversion: 2, 80, 1, 972, 8491, 324, 7776, 13608, 34020, 12636, 4374, 22680, 14580,
                         16524, 8748 orbits of lengths 1, 2, 3, 4, 6, 8, 12, 18, 24, 36, 54, 72, 108, 216, 648 (exact)
  V4 orbit-distribution  modulo 9 the law (cycle type 1, 8, 24, 24, 24 on 81 states) and the trace map share the period 24 and not
                         the orbit-length distribution (exact)
  V5 penrose-rank        on the bipartite Penrose patches the zero modes are N_A + N_B - 2 rank D, the rank exact over two primes,
                         equal to the eigenvalue count; the sublattice imbalance is a small part of them (exact)
  V6 diffraction         the Fourier amplitudes of the Fibonacci chain of length 987 sit at frac(n F_(k-1)/F_k), the gap positions,
                         with amplitude |sin(pi n / phi)| / (pi |n|) to five digits (numerical)
  V7 weak-gaps           at weak coupling the gap labeled n has width 2 V |sin(pi n / phi)| / (pi |n|), the pair n, -n agreeing on
                         average within 0.1 percent at V = 0.02 (numerical)
  V8 scaling-fit         W(L, 1) for L = 89 to 1597: local exponents 0.28663 to 0.28669 with the true length ratios, a log-log fit
                         delta = 0.28668 with rms residual below 10^-5, an offset c within 2 x 10^-4 of zero, an exponential in L
                         rejected by an 11 percent misfit (numerical)

    python3 tools/validation.py --selftest
    python3 tools/validation.py --gaps       writes records/spectra/gaps_V1.5.json, each gap's length, label, IDS, center and width
Standard library and numpy; scipy is not needed.
"""
import sys, math, itertools
from collections import Counter
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
PHI = (1 + 5 ** .5) / 2
def pisano(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1): return k
def perm(m):
    import numpy as np
    s = np.arange(m ** 3, dtype=np.int64); x, y, z = s // (m * m), (s // m) % m, s % m
    return ((2 * x * y - z) % m) * m * m + x * m + y
def period_and_census(m):
    """the period of the trace map modulo m and its census, from the fixed points of its powers"""
    import numpy as np
    T = perm(m); N = m ** 3
    assert len(np.unique(T)) == N
    def power(n):
        R = np.arange(N, dtype=np.int64); B = T.copy()
        while n:
            if n & 1: R = B[R]
            B = B[B]; n >>= 1
        return R
    ident = np.arange(N, dtype=np.int64)
    # the order of T: the smallest n with T^n = id, among the divisors of a multiple found by doubling
    mult = 2 * pisano(m) * 3 if m > 1 else 1
    while not (power(mult) == ident).all(): mult *= 2
    divs = [d for d in range(1, mult + 1) if mult % d == 0]
    fix = {d: int((power(d) == ident).sum()) for d in divs}
    per = min(d for d in divs if fix[d] == N)
    def mu(n):
        r, p = 1, 2
        while p * p <= n:
            if n % p == 0:
                n //= p
                if n % p == 0: return 0
                r = -r
            p += 1
        return -r if n > 1 else r
    cen = {}
    for l in divs:
        if per % l: continue
        c = sum(mu(l // d) * fix[d] for d in divs if l % d == 0) // l
        if c: cen[l] = c
    return per, cen
# V1
good = [2, 4, 8, 16, 32, 9, 27, 81, 18, 36, 48, 54, 72, 108]; bad = [3, 6, 12, 24, 5, 7, 11, 13, 17, 19, 23, 29, 31]
def per_only(m):
    c = Counter(); T = perm(m).tolist(); seen = bytearray(m ** 3)
    for s in range(m ** 3):
        if seen[s]: continue
        n = 0; u = s
        while not seen[u]: seen[u] = 1; u = T[u]; n += 1
        c[n] += 1
    p = 1
    for n in c: p = p * n // math.gcd(p, n)
    return p
rows_g = [(m, per_only(m), pisano(m)) for m in good]; rows_b = [(m, per_only(m), pisano(m)) for m in bad]
P('period-pattern', all(a == b for _, a, b in rows_g) and all(a != b for _, a, b in rows_b),
  'the period of the trace map against the law\'s Pisano period, equal at', [(m, a) for m, a, _ in rows_g], '; different at', rows_b,
  '| the equality holds at every modulus built from 2 and from 9 that was tested, and fails at 3 and at every prime from 5 to 31')
# V2
from fractions import Fraction as Fr
J = [[2, 2, -1], [1, 0, 0], [0, 1, 0]]
def charpoly3(M):
    tr = M[0][0] + M[1][1] + M[2][2]
    m2 = sum(M[i][i] * M[j][j] - M[i][j] * M[j][i] for i in range(3) for j in range(i + 1, 3))
    det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    return [1, -tr, m2, -det]
cp = charpoly3(J)
prod = [1, -3 + 1, 1 - 3, 1]   # (t + 1)(t^2 - 3t + 1) = t^3 - 2t^2 - 2t + 1
P('fixed-point-law', cp == [1, -2, -2, 1] == prod and (2 * 1 * 1 - 1, 1, 1) == (1, 1, 1),
  'the trace map fixes (1, 1, 1), and its Jacobian there, [[2, 2, -1], [1, 0, 0], [0, 1, 0]], has characteristic polynomial t^3 - 2t^2 - 2t + 1 = (t + 1)(t^2 - 3t + 1):',
  'the factor t^2 - 3t + 1 is the characteristic polynomial of A^2, eigenvalues phi^2 and phi^-2: the linear part of the trace map at its fixed point is the law\'s square beside -1')
# V3
per243, cen243 = period_and_census(243)
f220 = {1: 2, 2: 80, 3: 1, 4: 972, 6: 8491, 8: 324, 12: 7776, 18: 13608, 24: 34020, 36: 12636, 54: 4374, 72: 22680, 108: 14580, 216: 16524, 648: 8748}
P('census-243', per243 == 648 == pisano(243) and cen243 == f220 and sum(l * c for l, c in cen243.items()) == 243 ** 3 and sum(cen243.values()) == 144816,
  'modulo 243 the trace map is a bijection of the 14,348,907 triples with period %d, the Pisano period %d; its %d orbits by length:' % (per243, pisano(243), sum(cen243.values())),
  sorted(cen243.items()), '| counted from the fixed points of its powers by Moebius inversion, they equal the census computed independently in F220')
# V4
law9 = Counter()
seen = set()
for a in range(9):
    for b in range(9):
        if (a, b) in seen: continue
        n = 0; s = (a, b)
        while s not in seen: seen.add(s); s = (s[1], (s[0] + s[1]) % 9); n += 1
        law9[n] += 1
_, cen9 = period_and_census(9)
P('orbit-distribution', sorted(law9.items()) == [(1, 1), (8, 1), (24, 3)] and max(cen9) == 24 and sorted(cen9.items()) != sorted(law9.items()),
  'modulo 9 the law on the 81 states has orbits', sorted(law9.items()), 'and the trace map on the 729 triples has', sorted(cen9.items()),
  '| the same period 24, two different orbit-length distributions: a shared period, recorded with what it leaves unshared')
# V5
def rank_mod(M, p):
    import numpy as np
    M = M.copy() % p; r = 0; rows, cols = M.shape
    for c in range(cols):
        piv = np.nonzero(M[r:, c])[0]
        if len(piv) == 0: continue
        i = r + piv[0]; M[[r, i]] = M[[i, r]]
        M[r] = (M[r] * pow(int(M[r, c]), p - 2, p)) % p
        nz = np.nonzero(M[:, c])[0]; nz = nz[nz != r]
        if len(nz): M[nz] = (M[nz] - np.outer(M[nz, c], M[r])) % p
        r += 1
        if r == rows: break
    return r
def penrose_counts(N):
    import numpy as np
    sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
    import quasicrystal2d as q2
    verts, edges, _ = q2.tiling(N); n = len(verts)
    adj = [[] for _ in range(n)]
    for a, b in edges: adj[a].append(b); adj[b].append(a)
    col = [-1] * n; bip = True
    for s in range(n):
        if col[s] >= 0: continue
        col[s] = 0; st = [s]
        while st:
            u = st.pop()
            for w in adj[u]:
                if col[w] < 0: col[w] = 1 - col[u]; st.append(w)
                elif col[w] == col[u]: bip = False
    A_ = [i for i in range(n) if col[i] == 0]; B_ = [i for i in range(n) if col[i] == 1]
    ia = {v: k for k, v in enumerate(A_)}; ib = {v: k for k, v in enumerate(B_)}
    D = np.zeros((len(A_), len(B_)), dtype=np.int64)
    for a, b in edges:
        if col[a] == 0: D[ia[a], ib[b]] = 1
        else: D[ia[b], ib[a]] = 1
    r1, r2 = rank_mod(D, 1000003), rank_mod(D, 998244353)
    Ad = np.zeros((n, n))
    for a, b in edges: Ad[a, b] = Ad[b, a] = 1
    ev = int((abs(np.linalg.eigvalsh(Ad)) < 1e-8).sum())
    return n, bip, len(A_), len(B_), r1, r2, len(A_) + len(B_) - 2 * r1, ev
pc = [penrose_counts(N) for N in (4, 8)]
P('penrose-rank', all(b and r1 == r2 and z == ev for _, b, _, _, r1, r2, z, ev in pc) and all(abs(na - nb) < z for _, _, na, nb, _, _, z, _ in pc),
  'the Penrose patches are bipartite, H = [[0, D], [D^T, 0]], and the zero modes are N_A + N_B - 2 rank D with rank D exact over the primes 1000003 and 998244353:',
  [(n, 'N_A %d, N_B %d, rank %d, zero modes %d, eigenvalue count %d, imbalance %d' % (na, nb, r1, z, ev, abs(na - nb))) for n, _, na, nb, r1, _, z, ev in pc],
  '| the global imbalance accounts for a small part of the zero modes; the rest are confined by local mismatches')
# V6, V7
def word(k):
    w = 'a'
    for _ in range(k): w = ''.join('ab' if c == 'a' else 'a' for c in w)
    return w
import numpy as np
w = word(14); L = len(w); seq = np.array([1.0 if c == 'a' else 0.0 for c in w])
amp = np.abs(np.fft.fft(seq) / L); fprev = 610
peaks = sorted(range(1, L // 2), key=lambda q: -amp[q])[:12]; rows6 = []; ok6 = True
for q in peaks:
    n = min((n for n in range(-60, 61) if n and ((n * fprev - q) % L == 0 or (n * fprev + q) % L == 0)), key=abs)
    pred = abs(math.sin(math.pi * n / PHI)) / (math.pi * abs(n))
    ok6 = ok6 and abs(amp[q] - pred) < 2e-5; rows6.append((abs(n), round(float(amp[q]), 5)))
P('diffraction', ok6 and L == 987, 'the twelve strongest Fourier amplitudes of the Fibonacci chain of length 987 sit at q = frac(n F_(k-1)/F_k), the positions of the gaps of the same labels, with amplitude |sin(pi n/phi)|/(pi |n|) to within 2 x 10^-5: (|n|, amplitude)', sorted(rows6))
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
import spectra as sp
V = 0.02; lo, hi = sp.spectrum(987, V); pairs = {}
for i in range(986):
    g = lo[i + 1] - hi[i]
    if g > 1e-4:
        n = min((n for n in range(-40, 41) if n and (i + 1 - n * fprev) % 987 == 0), key=abs, default=None)
        if n is not None and abs(n) <= 4: pairs[n] = float(g)
ok7 = True; rows7 = []
for n in (1, 2, 3, 4):
    pred = 2 * V * abs(math.sin(math.pi * n / PHI)) / (math.pi * n); mean = (pairs[n] + pairs[-n]) / 2
    ok7 = ok7 and abs(mean / pred - 1) < 1e-3 and abs(pairs[n] / pred - 1) < 5e-3; rows7.append((n, round(pairs[n] / pred, 4), round(pairs[-n] / pred, 4), round(mean / pred, 5)))
P('weak-gaps', ok7, 'at V = 0.02 on length 987 the gaps labeled n and -n have widths, as fractions of 2V |sin(pi n/phi)|/(pi |n|), of (n, gap n, gap -n, their mean):', rows7,
  '| the gap of label n opens by the Fourier amplitude of the same label: diffraction and spectrum share their labels and, at weak coupling, their magnitudes')
# V8
Ls = [89, 144, 233, 377, 610, 987, 1597]
W = [float((lambda lh: (lh[1] - lh[0]).sum())(sp.spectrum(L_, 1.0))) for L_ in Ls]
loc = [-math.log(W[i + 1] / W[i]) / math.log(Ls[i + 1] / Ls[i]) for i in range(len(Ls) - 1)]
x = np.log(Ls); y = np.log(W); Am = np.vstack([x, np.ones_like(x)]).T
(dd, cc), *_ = np.linalg.lstsq(Am, y, rcond=None); res = y - (dd * x + cc)
# offset: W = a L^-delta + c with delta fixed at the fit, c by least squares on the residual of the power law
Lr = np.array(Ls, float); Bm = np.vstack([Lr ** dd, np.ones_like(Lr)]).T; (aa, c0), *_ = np.linalg.lstsq(Bm, np.array(W), rcond=None)
be = -np.polyfit(Lr, np.log(W), 1)[0]; ex = np.exp(np.polyval(np.polyfit(Lr, np.log(W), 1), Lr)); mis = float(np.sqrt((((np.array(W) - ex) / np.array(W)) ** 2).mean()))
ok8 = max(loc) - min(loc) < 2e-4 and float(np.sqrt((res ** 2).mean())) < 1e-5 and abs(c0) < 2e-4 and mis > 0.05
P('scaling-fit', ok8, 'W(L, 1) for L = 89 to 1597:', [round(v, 6) for v in W], '; local exponents with the true length ratios', [round(v, 5) for v in loc],
  '; the log-log fit gives delta = %.5f with rms residual %.1e; a constant offset fitted beside it is %.1e; an exponential in L misfits by %.0f percent: W ~ L^(-0.2867) at V = 1' % (-dd, float(np.sqrt((res ** 2).mean())), c0, 100 * mis))
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('VALIDATION SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--gaps']:
        import json, os
        rec = []
        for L_, fp in ((233, 144), (377, 233), (610, 377), (987, 610)):
            lo, hi = sp.spectrum(L_, 1.5)
            for i in range(L_ - 1):
                if lo[i + 1] - hi[i] >= 0.02:
                    ids = (i + 1) / L_
                    n = min(range(-60, 61), key=lambda n: abs(((n / PHI - ids + 0.5) % 1) - 0.5))
                    rec.append({'length': L_, 'label': n, 'states_below': i + 1, 'ids': round(ids, 9), 'center': round(float((lo[i + 1] + hi[i]) / 2), 6),
                                'width': round(float(lo[i + 1] - hi[i]), 6), 'congruence': (i + 1 - n * fp) % L_ == 0})
        out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'records', 'spectra', 'gaps_V1.5.json')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        json.dump({'_about': 'The gaps of width at least 0.02 of the Fibonacci Hamiltonian at V = 1.5 on four approximants (Companion Part 227.7): length, integer label, states below, integrated density of states, center and width, each its own field; the label found from the IDS and checked by the congruence states_below = label x F_(k-1) mod F_k. Written by python3 tools/validation.py --gaps.',
                   'gaps': rec}, open(out, 'w'), indent=1)
        print('GAP RECORD: %d gaps written to records/spectra/gaps_V1.5.json' % len(rec)); sys.exit(0)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    print(__doc__); sys.exit(2)
