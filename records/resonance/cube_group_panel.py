#!/usr/bin/env python3
"""cube_group_panel.py -- avenue 11, the cube-group panel, run under its frozen rule (records/resonance/cube_group_panel.txt).

Each of the 15 groups of order 24 is built here as a concrete set with a multiplication, its Cayley table is checked
(closure, associativity, identity, inverses), the 15 are shown pairwise non-isomorphic by invariants computed from the
tables, and the five frozen features are computed from each table, never from memory.
    python3 records/resonance/cube_group_panel.py      # diffed in CI against cube_group_panel_output.txt
Standard library only.
"""
from itertools import product, permutations
from collections import Counter

# ---------------------------------------------------------------- constructions
def cyclic(n): return [(k,) for k in range(n)], lambda x, y: ((x[0] + y[0]) % n,)
def direct(*gs):
    els = [tuple(p) for p in product(*[g[0] for g in gs])]
    return els, lambda x, y: tuple(g[1](a, b) for g, a, b in zip(gs, x, y))
def semidirect(n, h, act):
    """Z_n x| H, H = (elements, mul); act(hel) is the automorphism k -> act(hel)*k mod n, a unit of Z_n."""
    he, hm = h
    els = [(k, x) for k in range(n) for x in he]
    return els, lambda a, b: ((a[0] + act(a[1]) * b[0]) % n, hm(a[1], b[1]))
def perm_group(gens, n):
    idp = tuple(range(n)); els = {idp}; frontier = [idp]
    comp = lambda p, q: tuple(p[q[i]] for i in range(n))
    while frontier:
        new = []
        for p in frontier:
            for g in gens:
                r = comp(g, p)
                if r not in els: els.add(r); new.append(r)
        frontier = new
    return sorted(els), comp
def sl23():
    M = [(a, b, c, d) for a, b, c, d in product(range(3), repeat=4) if (a * d - b * c) % 3 == 1]
    return M, lambda x, y: ((x[0]*y[0] + x[1]*y[2]) % 3, (x[0]*y[1] + x[1]*y[3]) % 3, (x[2]*y[0] + x[3]*y[2]) % 3, (x[2]*y[1] + x[3]*y[3]) % 3)
def dicyclic(m):
    """Dic_m, order 4m: x^(2m) = 1, y^2 = x^m, y x y^-1 = x^-1; elements (k, e) = x^k y^e."""
    n = 2 * m
    def mul(a, b):
        k1, e1 = a; k2, e2 = b
        if e1 == 0: return ((k1 + k2) % n, e2)
        if e2 == 0: return ((k1 - k2) % n, 1)
        return ((k1 - k2 + m) % n, 0)
    return [(k, e) for k in range(n) for e in range(2)], mul
def dihedral(n):
    """D of order 2n: rotations r^k and reflections r^k s."""
    def mul(a, b):
        k1, e1 = a; k2, e2 = b
        return ((k1 + (k2 if e1 == 0 else -k2)) % n, (e1 + e2) % 2)
    return [(k, e) for k in range(n) for e in range(2)], mul
def quaternion():
    return dicyclic(2)

S3 = perm_group([(1, 0, 2), (1, 2, 0)], 3)
A4 = perm_group([(1, 2, 0, 3), (1, 0, 3, 2)], 4)
S4 = perm_group([(1, 0, 2, 3), (1, 2, 3, 0)], 4)
D8 = dihedral(4)
inv = lambda e: 1 if e == 0 else -1
GROUPS = [
    ('Z3:Z8', semidirect(3, cyclic(8), lambda h: (-1) ** h[0])),
    ('Z24', cyclic(24)),
    ('SL(2,3)', sl23()),
    ('Dic6', dicyclic(6)),
    ('Z4 x S3', direct(cyclic(4), S3)),
    ('D24', dihedral(12)),
    ('Z2 x Dic3', direct(cyclic(2), dicyclic(3))),
    ('Z3:D8', semidirect(3, D8, lambda h: -1 if h[0] % 2 else 1)),   # D8 acts through its quotient by the Klein four group {r^0, r^2, s, r^2 s}
    ('Z12 x Z2', direct(cyclic(12), cyclic(2))),
    ('Z3 x D8', direct(cyclic(3), D8)),
    ('Z3 x Q8', direct(cyclic(3), quaternion())),
    ('S4', S4),
    ('Z2 x A4', direct(cyclic(2), A4)),
    ('Z2 x Z2 x S3', direct(cyclic(2), cyclic(2), S3)),
    ('Z6 x Z2 x Z2', direct(cyclic(6), cyclic(2), cyclic(2))),
]
OBJECT = 'S4'

# ---------------------------------------------------------------- table checks and invariants
def table(g):
    els, mul = g; idx = {e: i for i, e in enumerate(els)}
    T = [[idx[mul(a, b)] for b in els] for a in els]
    return T
def check(T):
    n = len(T); r = range(n)
    e = [i for i in r if all(T[i][j] == j and T[j][i] == j for j in r)]
    ok = len(e) == 1 and all(all(T[a][T[b][c]] == T[T[a][b]][c] for c in r) for a in r for b in r) and all(any(T[a][b] == e[0] for b in r) for a in r)
    return ok, e[0] if e else None
def order(T, e, a):
    k, x = 1, a
    while x != e: x = T[x][a]; k += 1
    return k
def invariants(T, e):
    n = len(T); r = range(n)
    orders = [order(T, e, a) for a in r]
    centre = [a for a in r if all(T[a][b] == T[b][a] for b in r)]
    comm = {T[T[a][b]][T[[c for c in r if T[a][c] == e][0]][[d for d in r if T[b][d] == e][0]]] for a in r for b in r}
    return {'orders': tuple(sorted(Counter(orders).items())), 'centre': len(centre), 'commutators': len(comm),
            'abelian': len(centre) == n, 'orders_list': orders, 'centre_list': centre}

# ---------------------------------------------------------------- run
print('AVENUE 11 -- THE CUBE-GROUP PANEL (frozen rule: records/resonance/cube_group_panel.txt) [EXACT]')
rows, seen = [], {}
for name, g in GROUPS:
    T = table(g); ok, e = check(T); inv_ = invariants(T, e)
    F1 = int(24 in inv_['orders_list']); F2 = int(8 in inv_['orders_list'])
    F3 = int(any(inv_['orders_list'][z] == 2 for z in inv_['centre_list'])); F4 = int(3 in inv_['orders_list']); F5 = int(inv_['abelian'])
    key = (inv_['orders'], inv_['centre'], inv_['commutators'])
    seen.setdefault(key, []).append(name)
    rows.append((name, len(T), ok, (F1, F2, F3, F4, F5), sum((F1, F2, F3, F4, F5)) / 5, inv_))
print('  group            order  table  F1 F2 F3 F4 F5  score   element orders {order: count}            centre  commutators')
for name, n, ok, F, s, inv_ in rows:
    print('  %-16s %5d  %-5s  %s  %.1f    %-42s %4d   %4d' % (name, n, 'OK' if ok else 'BAD', '  '.join(map(str, F)), s, dict(inv_['orders']), inv_['centre'], inv_['commutators']))
distinct = all(len(v) == 1 for v in seen.values())
print('  all 15 tables valid groups of order 24: %s' % ('YES' if all(ok and n == 24 for _, n, ok, _, _, _ in rows) else 'NO'))
print('  pairwise non-isomorphic by (element orders, centre, commutator set): %s' % ('YES, 15 classes' if distinct and len(seen) == 15 else 'NO: %s' % [v for v in seen.values() if len(v) > 1]))
obj = [r for r in rows if r[0] == OBJECT][0]; others = [r for r in rows if r[0] != OBJECT]
prox = (sum(1 for r in others if obj[4] > r[4]) + 0.5 * sum(1 for r in others if obj[4] == r[4])) / len(others)
zlaw = [r for r in rows if r[0] == 'Z24'][0]
print('  the law\'s own group <T> = Z24 scores %.1f (it holds all five features by construction)' % zlaw[4])
print('  OBJECT %s: features %s, score %.1f; PROXIMITY %.0f (share of the other 14 it outscores, ties half, x 100)' % (OBJECT, obj[3], obj[4], 100 * prox))
low = [r[0] for r in rows if r[4] == min(x[4] for x in rows)]
print('  lowest score in the class: %s' % ', '.join(low))
print('RESULT: %s' % ('the cube group is the group of order 24 least like the law\'s own group on the frozen features: no element of order 24 or 8, no central involution, not abelian; it shares only what every group of order 24 has, an element of order 3' if low == [OBJECT] else 'the cube group shares the lowest score with %s' % ', '.join(x for x in low if x != OBJECT)))
