#!/usr/bin/env python3
"""Zero and the canonical selection (Core Part 1.8.7). Run: python3 compute.py"""
import itertools
from collections import Counter
N = 9
T = lambda v: (v[1], (v[0] + v[1]) % N)
Tinv = lambda v: ((v[1] - v[0]) % N, v[0])
nrm = lambda a, b: (a*a + a*b - b*b) % N
def mul(x, y): a, b = x; c, d = y; return ((a*c + b*d) % N, (a*d + b*c + b*d) % N)
S81 = list(itertools.product(range(N), repeat=2))
units = [v for v in S81 if nrm(*v) % 3]
inv = {u: next(w for w in units if mul(u, w) == (1, 0)) for u in units}
seen, orbits = set(), []
for v in S81:
    if v in seen: continue
    o = [v]; y = T(v)
    while y != v: o.append(y); y = T(y)
    seen |= set(o); orbits.append(o)
def voice(o):
    dom = Counter(s[0] for s in o).most_common(2)
    return {frozenset([1, 8]): 'Voice A', frozenset([2, 7]): 'Voice B', frozenset([4, 5]): 'Voice C'}.get(frozenset(x for x, _ in dom), 'core') if len(o) == 24 else ('eight-cycle' if len(o) == 8 else 'fixed point')
V = {voice(o): o for o in orbits}
print("(a) complete spectrum <=> orbit of units <=> norm != 0 (outside the zero layer):")
for o in orbits:
    full = set(s[0] for s in o) == set(range(9))
    print("    %-11s len %2d | complete spectrum %-5s | all units %-5s | norm values %s" % (voice(o), len(o), full, all(s in units for s in o), sorted({nrm(*s) for s in o})))
print("    equivalence holds for every orbit:", all((set(s[0] for s in o) == set(range(9))) == all(s in units for s in o) for o in orbits))
print("(b) each voice's dominant pair = its zero-seeds; after a zero the next value repeats:")
for name in ('Voice A', 'Voice B', 'Voice C'):
    o = V[name]; c = Counter(s[0] for s in o)
    zs = sorted(s[1] for s in o if s[0] == 0)
    dom = sorted(x for x, k in c.items() if k == max(c.values()))
    rep = all(T(s)[1] == s[1] for s in o if s[0] == 0)
    print("    %s: zero-seeds %s | dominant values %s (x%d) | equal: %s | (0,x) -> (x,x): %s" % (name, zs, dom, max(c.values()), zs == dom, rep))
F = [(0, 1)]
for _ in range(23): F.append(T(F[-1]))
for name, x in (('Voice A', 1), ('Voice B', 2), ('Voice C', 5)):
    print("    %s = %d x the Fibonacci orbit from (0, 1): %s" % (name, x, {((x*a) % 9, (x*b) % 9) for a, b in F} == set(V[name])))
print("    1/2 mod 9 = %d, so Voice C = (1/2) x the Fibonacci orbit" % pow(2, -1, 9))
print("(c) the K2 order convention is the choice between a seed and its inverse:")
print("    (5,2) = phi^4 * (2,5)^-1, with phi^4 = (2,3):", mul((2, 3), inv[(2, 5)]) == (5, 2), "| T^4(1,0) = (2,3):", (lambda v: T(T(T(T(v)))))((1, 0)) == (2, 3))
print("    inversion maps Voice C onto Voice B: %s | Voice B onto Voice C: %s | fixes Voice A: %s" % (
      {inv[u] for u in V['Voice C']} == set(V['Voice B']), {inv[u] for u in V['Voice B']} == set(V['Voice C']), {inv[u] for u in V['Voice A']} == set(V['Voice A'])))
print("    inversion reverses the law, inv(T(u)) = T^-1(inv(u)), on all 72 units:", all(inv[T(u)] == Tinv(inv[u]) for u in units))
print("    norm of the inverse = inverse of the norm (2 <-> 5, 7 <-> 4, 1 and 8 fixed):", all(nrm(*inv[u]) == pow(nrm(*u), -1, 9) for u in units))
print("(d) K-zero adversarial set: unit orbit, adjacent zero-seed values, start at a zero state:")
surv = []
for name in ('Voice A', 'Voice B', 'Voice C'):
    zs = sorted(s for s in V[name] if s[0] == 0)
    if abs(zs[0][1] - zs[1][1]) == 1: surv += [(name, s) for s in zs]
print("    survivors:", surv, "-> 2, one orbit; related by T^12 = -I:", len(surv) == 2 and ((-surv[0][1][0]) % 9, (-surv[0][1][1]) % 9) == surv[1][1])
c = [(2, 5)]
while T(c[-1]) != (2, 5): c.append(T(c[-1]))
print("    the canonical reading from (2,5) meets the zero states at P%d (0,5) and P%d (0,4)" % (c.index((0, 5)), c.index((0, 4))))
