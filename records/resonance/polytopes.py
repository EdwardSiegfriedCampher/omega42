#!/usr/bin/env python3
"""polytopes.py -- the object panels of M319 (Core Part 3.45; Companion Part 81), computed against the classes frozen in
records/resonance/object_panels_frozen.txt.

Panel 1: the six regular convex 4-polytopes, each the orbit of a fundamental weight under its Coxeter group, every
symmetry of the group enumerated; the four frozen features decided over the whole group. Panel 2: cyclic systems of 24
states under their own step. Then the Margin, its permutation p and p_family (APE-143), as tools/resonance.py defines
them. Standard library only.

    python3 records/resonance/polytopes.py      # prints the panels (diffed in CI against polytopes_output.txt)
"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
from resonance import margin, p_perm, p_family, margin_band

R = 6


def key(v): return tuple(round(x, R) + 0.0 for x in v)
def mat_key(M): return tuple(round(x, R) + 0.0 for row in M for x in row)
def mul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def app(M, v): return [sum(M[i][k] * v[k] for k in range(4)) for i in range(4)]


def roots(m):
    """Unit simple roots for a linear Coxeter diagram with edge labels m = (m12, m23, m34)."""
    G = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    for i, mi in enumerate(m):
        G[i][i + 1] = G[i + 1][i] = -math.cos(math.pi / mi)
    L = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(i + 1):
            s = G[i][j] - sum(L[i][k] * L[j][k] for k in range(j))
            L[i][j] = math.sqrt(s) if i == j else s / L[j][j]
    return L


def group(m):
    A = roots(m)
    gens = [[[(1.0 if i == j else 0.0) - 2 * A[r][i] * A[r][j] for j in range(4)] for i in range(4)] for r in range(4)]
    I = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    seen = {mat_key(I): I}; frontier = [I]
    while frontier:
        nxt = []
        for M in frontier:
            for g in gens:
                P = mul(g, M); k = mat_key(P)
                if k not in seen: seen[k] = P; nxt.append(P)
        frontier = nxt
    return A, list(seen.values())


def weight(A, j):
    """The fundamental weight w_j: w_j . a_i = 0 for i != j, solved in the plane orthogonal to the other roots."""
    rows = [A[i] for i in range(4) if i != j]
    # the null vector of the 3 x 4 system, by cofactors
    def det3(M): return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                         + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    w = [(-1) ** c * det3([[r[k] for k in range(4) if k != c] for r in rows]) for c in range(4)]
    if sum(a * b for a, b in zip(w, A[j])) < 0: w = [-x for x in w]
    n = math.sqrt(sum(x * x for x in w)); return [x / n for x in w]


def power(M, n):
    P = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
    for _ in range(n): P = mul(M, P)
    return P


def is_minus_I(M): return all(abs(M[i][j] - (-1.0 if i == j else 0.0)) < 1e-6 for i in range(4) for j in range(4))


def cycles(g, V, index):
    seen = set(); lens = []
    for s in range(len(V)):
        if s in seen: continue
        n = 0; t = s
        while t not in seen:
            seen.add(t); n += 1; t = index[key(app(g, V[t]))]
        lens.append(n)
    return lens


def polytope(name, m, j, W=None):
    A, G = W if W else group(m)
    w = weight(A, j)
    orbit = {}
    for g in G:
        v = app(g, w); orbit.setdefault(key(v), v)
    V = list(orbit.values()); index = {key(v): i for i, v in enumerate(V)}
    f1 = len(V) == 24
    f2 = all(key([-x for x in v]) in index for v in V)
    f3 = f4 = False
    for g in G:
        if not f3 and is_minus_I(power(g, 6)) and set(cycles(g, V, index)) == {12}: f3 = True
        if not f4 and is_minus_I(power(g, 12)) and set(cycles(g, V, index)) == {24}: f4 = True
        if f3 and f4: break
    return dict(name=name, group=len(G), vertices=len(V), F=[f1, f2, f3, f4])


def cyclic(name, n=24):
    step = lambda s: (s + 1) % n
    f1 = n == 24
    order = next(k for k in range(1, n + 1) if all((s + k) % n == s for s in range(n)))
    f2 = order == 24
    half = lambda s: (s + 12) % n
    f3 = all(half(s) != s and half(half(s)) == s for s in range(n))
    return dict(name=name, F=[f1, f2, f3])


def score(F): return sum(1 for x in F if x) / len(F)


def panel(title, obj, nulls, labels):
    L = ['=== %s ===' % title]
    for p in [obj] + nulls:
        extra = ' | group %d | %d vertices' % (p['group'], p['vertices']) if 'group' in p else ''
        L.append('  %-28s %s%s | s = %.2f' % (p['name'], ' '.join('%s %s' % (l, 'YES' if f else 'NO') for l, f in zip(labels, p['F'])), extra, score(p['F'])))
    s_obj = score(obj['F']); ns = [score(p['F']) for p in nulls]
    M, status = margin(s_obj, ns); p = p_perm(s_obj, ns)
    band = margin_band(M, status, p, len(ns))
    L.append('  MARGIN M = %s | p = %.4f (%d nulls; the least p this class allows is %.4f) | p_family = %.4f (k\' = 0) | %s' % (
        ('%.4f' % M) if M is not None else 'NONE', p, len(ns), 1 / (1 + len(ns)), p_family(p, 0), band))
    return '\n'.join(L), M, p, band


def panel3(WA, WB, WF, WH):
    """Panel 3 (records/resonance/object_panel3_frozen.txt): the 24-cell against the Wythoffian convex uniform 4-polytopes.
    For g with g^6 = -I every vertex orbit has length 4 or 12, so all are 12 exactly when no vertex is fixed by g^4;
    for g with g^12 = -I, all orbits are 24 exactly when no vertex is fixed by g^8. Vectorized with numpy."""
    import numpy as np
    from itertools import combinations
    rows = []
    for gname, (A, G) in (('A4', WA), ('B4', WB), ('F4', WF), ('H4', WH)):
        Gs = [np.array(g) for g in G]
        c6 = [g for g in Gs if np.allclose(np.linalg.matrix_power(g, 6), -np.eye(4), atol=1e-6)]
        c12 = [g for g in Gs if np.allclose(np.linalg.matrix_power(g, 12), -np.eye(4), atol=1e-6)]
        W = [np.array(weight(A, j)) for j in range(4)]
        for k in range(1, 5):
            for ring in combinations(range(4), k):
                x = sum(W[j] for j in ring)
                pts = {}
                for g in Gs:
                    v = g @ x; pts.setdefault(tuple(np.round(v, 6) + 0.0), v)
                V = np.array(list(pts.values())); V = V / np.linalg.norm(V[0])
                d = np.round(np.sort(np.linalg.norm(V - V[0], axis=1)), 4)
                sig = (len(V), tuple(d))
                keys = {tuple(np.round(v, 6) + 0.0) for v in V}
                f1 = len(V) == 24
                f2 = all(tuple(np.round(-v, 6) + 0.0) in keys for v in V)
                f3 = any(not np.any(np.all(np.abs(V @ np.linalg.matrix_power(g, 4).T - V) < 1e-6, axis=1)) for g in c6)
                f4 = any(not np.any(np.all(np.abs(V @ np.linalg.matrix_power(g, 8).T - V) < 1e-6, axis=1)) for g in c12)
                rows.append(dict(name='%s ringed %s' % (gname, ''.join(str(j + 1) for j in ring)), sig=sig, vertices=len(V), F=[f1, f2, f3, f4]))
    seen = {}; uniq = []
    for r in rows:
        if r['sig'] in seen:
            # one vertex set, several constructions: its symmetries are those of every group that builds it, so a
            # feature found under any of them holds (the frozen features are decided over the whole symmetry group)
            first = seen[r['sig']]; first['also'].append(r['name']); first['F'] = [a or b for a, b in zip(first['F'], r['F'])]; continue
        r['also'] = []; seen[r['sig']] = r; uniq.append(r)
    cell = [r for r in uniq if r['F'][0] and r['vertices'] == 24]
    obj = cell[0]; nulls = [r for r in uniq if r is not obj]
    L = ['=== PANEL 3: the 24-cell against the Wythoffian convex uniform 4-polytopes (A4, B4, F4, H4; %d constructions, %d distinct vertex sets) ===' % (len(rows), len(uniq))]
    L.append('  24-cell (%s; also %s)  C24 %s CA %s CT2 %s CT %s | s = %.2f' % (obj['name'], ', '.join(obj['also']) or 'none', *['YES' if f else 'NO' for f in obj['F']], score(obj['F'])))
    dist = {}
    for r in nulls: dist.setdefault(score(r['F']), []).append(r)
    for sc in sorted(dist, reverse=True):
        L.append('  nulls at s = %.2f: %d -- %s' % (sc, len(dist[sc]), '; '.join('%s (%d vertices%s)' % (r['name'], r['vertices'], '' if not r['F'][2] else ', T^2 signature') for r in dist[sc])))
    s_obj = score(obj['F']); ns = [score(r['F']) for r in nulls]
    M, status = margin(s_obj, ns); p = p_perm(s_obj, ns); band = margin_band(M, status, p, len(ns))
    share = (sum(1 for x in ns if x < s_obj) + 0.5 * sum(1 for x in ns if x == s_obj)) / len(ns)
    L.append('  MARGIN M = %.4f | p = %.4f (%d nulls; the least p this class allows is %.4f) | p_family = %.4f (k\' = 0) | %s | share of look-alikes outscored %.4f' % (M, p, len(ns), 1 / (1 + len(ns)), p_family(p, 0), band, share))
    return '\n'.join(L)


if __name__ == '__main__':
    WA, WB, WF, WH = group((3, 3, 3)), group((4, 3, 3)), group((3, 4, 3)), group((5, 3, 3))
    P = [polytope('5-cell (A4)', None, 0, WA), polytope('16-cell (B4)', None, 3, WB), polytope('tesseract (B4)', None, 0, WB),
         polytope('600-cell (H4)', None, 3, WH), polytope('120-cell (H4)', None, 0, WH), polytope('24-cell (F4)', None, 0, WF)]
    by = {p['name']: p for p in P}
    print('M319 OBJECT PANELS -- features and null classes frozen in records/resonance/object_panels_frozen.txt; every value computed here [CDT-A]')
    t, M, p, band = panel('PANEL 1: the 24-cell against the regular convex 4-polytopes', by['24-cell (F4)'], [x for x in P if x['name'] != '24-cell (F4)'], ('C24', 'CA', 'CT2', 'CT'))
    print(t)
    C = [cyclic('24-tone equal temperament'), cyclic('24-hour day'), cyclic('24-item cyclic list'), cyclic('24 half-hour marks of a 12-hour face')]
    t2, M2, p2, band2 = panel('PANEL 2: 24-tone equal temperament against cyclic 24-systems', C[0], C[1:], ('C24', 'CC', 'CA'))
    print(t2)
    print(panel3(WA, WB, WF, WH))
    print('READING: the Margin says how far the object exceeds its frozen look-alikes on the frozen features; it does not say that the cycle produces the object (L-480), and it grades nothing (L-490)')
