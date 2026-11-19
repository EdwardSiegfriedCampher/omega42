#!/usr/bin/env python3
"""quasicrystal2d.py -- the golden ring in two dimensions: the square Fibonacci Hamiltonian and the Penrose tiling
(Companion Part 226; F219; APE-481).

  Q1 square-fibonacci   H = H_x + H_y on the square Fibonacci grid, spectrum the sum set of the chain's spectrum with itself:
                        up to V = 1.25 every gap of the approximants closes as the length grows (the spectrum an interval in the
                        limit, as Damanik and Gorodetski proved for small coupling); from V = 1.3 a gap stands at every length (numerical)
  Q2 penrose-tiles      the Penrose rhombus tiling from de Bruijn's pentagrid: interior vertex degrees 3 to 7, and the ratio of
                        thick to thin rhombi approaching phi (numerical)
  Q3 penrose-zero-modes the vertex model on Penrose patches: the fraction of states at E = 0 on patches of 503 to 3995 vertices,
                        beside the exact density 81 - 50 phi of Kohmoto, Sutherland, Arai, Tokihiro and Fujiwara, an element of
                        Z[phi] of norm 11 (numerical; the norm exact)

    python3 tools/quasicrystal2d.py --selftest
    python3 tools/quasicrystal2d.py --square V    the 2D components and widest gap at V for lengths 233 and 610
Standard library and numpy.
"""
import sys, math, random
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
PHI = (1 + 5 ** .5) / 2
def word(k):
    w = 'a'
    for _ in range(k): w = ''.join('ab' if c == 'a' else 'a' for c in w)
    return w
def bands(L, V):
    import numpy as np
    k = 1
    while len(word(k)) < L: k += 1
    w = word(k); pot = np.array([V if c == 'a' else 0.0 for c in w]); ev = []
    for sgn in (1.0, -1.0):
        H = np.diag(pot) - np.eye(L, k=1) - np.eye(L, k=-1); H[0, L - 1] = H[L - 1, 0] = -sgn
        ev.append(np.sort(np.linalg.eigvalsh(H)))
    return list(zip(np.minimum(*ev), np.maximum(*ev)))
def union(iv):
    iv = sorted(iv); out = [list(iv[0])]
    for a, b in iv[1:]:
        if a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)
        else: out.append([a, b])
    return out
def square(V, L):
    u = union(bands(L, V)); S = union([(a1 + a2, b1 + b2) for a1, b1 in u for a2, b2 in u])
    g = [S[i + 1][0] - S[i][1] for i in range(len(S) - 1)]
    return len(S), (max(g) if g else 0.0)
# Q1
rows = []; ok1 = True
for V in (0.5, 1.0, 1.25, 1.3, 1.5, 2.0):
    (c1, g1), (c2, g2) = square(V, 233), square(V, 610)
    rows.append((V, '%.2g' % g1, '%.2g' % g2))
    if V <= 1.25: ok1 = ok1 and (g2 < 1e-3 and (g1 == 0 or g2 < g1 / 4))
    else: ok1 = ok1 and g2 > 5e-3 and abs(g1 - g2) < 1e-3 * max(1, g2)
P('square-fibonacci', ok1, 'the square Fibonacci Hamiltonian H_x + H_y: its spectrum is the sum set of the chain\'s with itself; (V, widest gap at length 233, at length 610):', rows,
  '| up to V = 1.25 the gaps close as the length grows, the spectrum an interval in the limit (Damanik and Gorodetski, for small coupling); from V = 1.3 a gap of 0.0067 and more stands at both lengths')
# Q2, Q3: the pentagrid
def tiling(N, seed=1):
    import numpy as np
    rng = random.Random(seed)
    g = [rng.uniform(0, 1) for _ in range(4)]; g.append(-sum(g))
    E = [(math.cos(2 * math.pi * j / 5), math.sin(2 * math.pi * j / 5)) for j in range(5)]
    verts = {}; edges = set(); kinds = [0, 0]
    def vid(K):
        p = (round(sum(K[m] * E[m][0] for m in range(5)), 6), round(sum(K[m] * E[m][1] for m in range(5)), 6))
        if p not in verts: verts[p] = len(verts)
        return verts[p]
    for j in range(5):
        for l in range(j + 1, 5):
            Mx = np.array([E[j], E[l]])
            for kj in range(-N, N + 1):
                for kl in range(-N, N + 1):
                    x = np.linalg.solve(Mx, np.array([kj - g[j], kl - g[l]]))
                    K = [math.ceil(x[0] * E[m][0] + x[1] * E[m][1] + g[m]) for m in range(5)]
                    if max(abs(k) for k in K) > N: continue
                    cs = []
                    for dj, dl in ((0, 0), (1, 0), (1, 1), (0, 1)):
                        Kc = list(K); Kc[j] = kj + dj; Kc[l] = kl + dl; cs.append(vid(Kc))
                    for i in range(4): a_, b_ = cs[i], cs[(i + 1) % 4]; edges.add((min(a_, b_), max(a_, b_)))
                    kinds[0 if (l - j) in (1, 4) else 1] += 1          # thick (72 degrees) or thin (36 degrees)
    return verts, edges, kinds
import numpy as np
fr = []; ok2 = True; rat = []
for N in (4, 8, 12):
    verts, edges, kinds = tiling(N)
    n = len(verts); A = np.zeros((n, n))
    for a, b in edges: A[a, b] = A[b, a] = 1
    Pts = np.array(sorted(verts, key=verts.get)); r = np.hypot(Pts[:, 0], Pts[:, 1])
    deg = A.sum(1); interior = r < 0.6 * r.max()
    ok2 = ok2 and set(deg[interior].astype(int)) <= {3, 4, 5, 6, 7} and {3, 7} <= set(deg[interior].astype(int))
    rat.append(round(kinds[0] / kinds[1], 4))
    z = int(np.sum(np.abs(np.linalg.eigvalsh(A)) < 1e-8)); fr.append((n, z, round(z / n, 4)))
ok2 = ok2 and abs(rat[-1] - PHI) < 0.02
P('penrose-tiles', ok2, 'the Penrose rhombus tiling built from de Bruijn\'s pentagrid (generic offsets), patches of %s vertices: interior vertex degrees from 3 to 7;' % [f[0] for f in fr],
  'thick to thin rhombi', rat, 'approaching phi = %.4f, the five-fold order of the golden ring (MF-150)' % PHI)
norm = 81 * 81 + 81 * (-50) - 50 * 50
ok3 = norm == 11 and all(0.08 < f[2] < 0.105 for f in fr) and abs(81 - 50 * PHI - 0.0983) < 1e-4
P('penrose-zero-modes', ok3, 'the vertex model on the Penrose patches, hopping 1 along every edge: (vertices, states at E = 0, fraction)', fr,
  '| the exact density of the infinite tiling is 81 - 50 phi = %.6f (Kohmoto and Sutherland; Arai, Tokihiro, Fujiwara and Kohmoto), an element of Z[phi] of norm 81^2 - 81 x 50 - 50^2 = %d; the finite patches carry it with their boundaries' % (81 - 50 * PHI, norm))
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('QUASICRYSTAL2D SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if len(a) == 2 and a[0] == '--square':
        for L in (233, 610): print('L = %d: %d components, widest gap %.6g' % ((L,) + square(float(a[1]), L)))
        sys.exit(0)
    print(__doc__); sys.exit(2)
