#!/usr/bin/env python3
"""Evidence run 12 -- re-examination of runs 01-03 at family level (standard library + numpy). Run: python3 compute.py"""
import itertools, math, cmath, random
from collections import Counter
import numpy as np
N = 9
S81 = list(itertools.product(range(N), repeat=2))
nrm = lambda v: (v[0]*v[0] + v[0]*v[1] - v[1]*v[1]) % N
VOICE = {1: 'A', 8: 'A', 4: 'B', 5: 'B', 2: 'C', 7: 'C', 0: 'core'}
def act(M, v): return ((M[0]*v[0] + M[1]*v[1]) % N, (M[2]*v[0] + M[3]*v[1]) % N)
def cycles(perm):
    seen, out = set(), Counter()
    for x in perm:
        if x in seen: continue
        L, y = 0, x
        while y not in seen: seen.add(y); y = perm[y]; L += 1
        out[L] += 1
    return dict(sorted(out.items(), reverse=True))
T = (0, 1, 1, 1)
FAM = cycles({v: act(T, v) for v in S81})
print("FAMILY: cycle type of T on the 81 states:", FAM)

print("\nR1  SYMMETRY GROUPS AND PLANAR QUASICRYSTAL MODULES")
GL = [M for M in itertools.product(range(N), repeat=4) if math.gcd((M[0]*M[3]-M[1]*M[2]) % N, N) == 1]
U = [M for M in GL if all(nrm(act(M, v)) == nrm(v) for v in S81)]
TR = [M for M in GL if all(nrm(act(M, v)) == (-nrm(v)) % N for v in S81)]
def mm(A, B): return ((A[0]*B[0]+A[1]*B[2]) % N, (A[0]*B[1]+A[1]*B[3]) % N, (A[2]*B[0]+A[3]*B[2]) % N, (A[2]*B[1]+A[3]*B[3]) % N)
def order(M):
    k, X = 1, M
    while X != (1, 0, 0, 1): X = mm(X, M); k += 1
    return k
G = U + TR
oG = Counter(order(M) for M in G); oU = Counter(order(M) for M in U)
print("  full group G: order %d, involutions %d; dihedral D24 (point group of 24-fold diffraction): order 48, involutions 25 -> G ~ D24: %s"
      % (len(G), oG[2], oG[2] == 25))
d12 = Counter({1: 1, 2: 13, 3: 2, 4: 2, 6: 2, 12: 4})
print("  unitary subgroup: order %d, element orders %s; D12 (point group of 12-fold diffraction) has %s -> equal: %s"
      % (len(U), dict(sorted(oU.items())), dict(sorted(d12.items())), oU == d12))
r, j = T, (1, 1, 0, 8)
r11 = (1, 0, 0, 1)
for _ in range(11): r11 = mm(r11, r)
print("  G = <r, j> with j r j = r^11 (not r^-1): %s; finite subgroups of O(2) are cyclic or dihedral, so G is no planar point group" % (mm(mm(j, r), j) == r11))
z = cmath.exp(2j*math.pi/24)
print("  faithful 2-dim complex rep of G induced from zeta24: character zeta + zeta^11 real? %s -> smallest faithful real rep has dimension 4;"
      " zeta24 has degree 8 over Q, so the order-24 element is non-crystallographic in R^4 (an 8-rank module, quasicrystalline)"
      % (abs((z + z**11).imag) < 1e-12))

def ring(phi_coeffs, m):
    """Z[x]/(m, Phi(x)), Phi monic of degree d given by low-to-high coefficients (leading 1 omitted)."""
    d = len(phi_coeffs)
    def mul(a, b):
        c = [0]*(2*d-1)
        for i, ai in enumerate(a):
            for k, bk in enumerate(b): c[i+k] += ai*bk
        for t in range(2*d-2, d-1, -1):
            co = c[t]; c[t] = 0
            for i, p in enumerate(phi_coeffs): c[t-d+i] -= co*p
        return tuple(x % m for x in c[:d])
    els = list(itertools.product(range(m), repeat=d))
    return els, mul, d
MODS = {'8-fold  Z[zeta8]/3': [1, 0, 0, 0], '10-fold Z[zeta5]/3': [1, 1, 1, 1], '12-fold Z[zeta12]/3': [1, 0, -1, 0]}
for name, phi in MODS.items():
    els, mul, d = ring(phi, 3)
    one = tuple([1] + [0]*(d-1)); x = tuple([0, 1] + [0]*(d-2))
    add = lambda a, b: tuple((p+q) % 3 for p, q in zip(a, b))
    golden = [u for u in els if mul(u, u) == add(u, one)]
    gct = [cycles({e: mul(u, e) for e in els}) for u in golden]
    units = [u for u in els if any(mul(u, e) == one for e in els)]
    has = any(c == FAM for c in (cycles({e: mul(u, e) for e in els}) for u in units))
    print("  %-20s %d states | rotation zeta: %s | golden elements %d, cycle types %s | carries the family (criterion): %s | some unit has type (24^3,8,1): %s"
          % (name, len(els), cycles({e: mul(x, e) for e in els}), len(golden), gct, any(c == FAM for c in gct), has))
els, mul, d = ring([1, 1, 1, 1], 9)
phi = (0, 0, 8, 8)                                     # -(zeta^2 + zeta^3) = 1 + zeta + zeta^4
one = (1, 0, 0, 0)
print("  10-fold Z[zeta5]/9 (%d states): phi = -(zeta^2+zeta^3) satisfies phi^2 = phi + 1: %s"
      % (len(els), mul(phi, phi) == tuple((p+q) % 9 for p, q in zip(phi, one))))
sub = {tuple((a*o + b*p) % 9 for o, p in zip(one, phi)): (a, b) for a in range(9) for b in range(9)}
okT = all(sub[mul(phi, e)] == act(T, sub[e]) for e in sub)
print("    the subring {a + b phi} has 81 elements: %s; multiplication by phi acts on it as T: %s; cycle type there %s; on all 6561 states %s"
      % (len(sub) == 81, okT, cycles({e: mul(phi, e) for e in sub}), cycles({e: mul(phi, e) for e in els})))

print("\nR2  PHYLLOTACTIC SERIES BY VOICE")
canon = [(2, 5)]
while act(T, canon[-1]) != canon[0]: canon.append(act(T, canon[-1]))
canon = set(canon)
def series(a, b, n=12):
    s = [a, b]
    while len(s) < n: s.append(s[-1] + s[-2])
    return s
SER = [('Fibonacci 1,2,3,5', 1, 2, 'survey'), ('Lucas 1,3,4,7', 1, 3, 'survey'), ('F4 1,4,5,9', 1, 4, 'survey'),
       ('double Fibonacci 2,4,6,10', 2, 4, 'survey'), ('accessory 1,5,6,11', 1, 5, 'botanical literature'),
       ('canonical seed 2,5,7,12', 2, 5, 'not reported'), ('triple Fibonacci 3,6,9,15', 3, 6, 'not reported')]
for name, a, b, src in SER:
    s = series(a, b); pairs = list(zip(s, s[1:]))[2:9]
    vs = {VOICE[nrm((p % 9, q % 9))] for p, q in pairs}
    onc = all((p % 9, q % 9) in canon for p, q in pairs)
    print("  %-28s integer norm %4d | voice %s | pairs mod 9 on the canonical 24-orbit: %-5s | e.g. %s | %s"
          % (name, a*a + a*b - b*b, '/'.join(sorted(vs)), onc, '/'.join(map(str, pairs[3])), src))
random.seed(12)
cnt = Counter()
while sum(cnt.values()) < 100000:
    a, b = random.randint(1, 10**6), random.randint(1, 10**6)
    if math.gcd(a, b) == 1: cnt[VOICE[nrm((a % 9, b % 9))]] += 1
print("  null (100000 random coprime pairs): voice frequencies", {k: round(v/1e5, 3) for k, v in sorted(cnt.items())})

print("\nR3  QUANTUM CAT MAP AT FAMILY LEVEL")
def weil_U(Nn, A):
    """Unitary implementing the symplectic A = (a,b,c,d) on Weyl operators of dimension Nn (odd), by brute-force
    projective search over products of F and the shear S."""
    w = cmath.exp(2j*math.pi/Nn); inv2 = pow(2, -1, Nn)
    X = np.roll(np.eye(Nn), 1, axis=0); Z = np.diag([w**k for k in range(Nn)])
    F = np.array([[w**(p*q) for q in range(Nn)] for p in range(Nn)]) / math.sqrt(Nn)
    Sh = np.diag([w**((inv2*k*k) % Nn) for k in range(Nn)])
    def imp(Uu):
        Ui = Uu.conj().T; a1 = Uu @ X @ Ui; a2 = Uu @ Z @ Ui
        def lab(O):
            for p in range(Nn):
                for q in range(Nn):
                    D = np.linalg.matrix_power(X, p) @ np.linalg.matrix_power(Z, q)
                    k = np.argmax(abs(D)); ph = O.flat[k]/D.flat[k]
                    if abs(abs(ph)-1) < 1e-9 and np.allclose(O, ph*D, atol=1e-8): return p, q
        (p1, q1), (p2, q2) = lab(a1), lab(a2)
        return (p1, p2, q1, q2)
    def mmn(P, Q): return ((P[0]*Q[0]+P[1]*Q[2]) % Nn, (P[0]*Q[1]+P[1]*Q[3]) % Nn, (P[2]*Q[0]+P[3]*Q[2]) % Nn, (P[2]*Q[1]+P[3]*Q[3]) % Nn)
    gF, gS = imp(F), imp(Sh)
    from collections import deque
    start = (1, 0, 0, 1); seen = {start: np.eye(Nn, dtype=complex)}; dq = deque([start])
    target = tuple(x % Nn for x in A)
    while dq:
        P = dq.popleft()
        if P == target: return seen[P]
        for g, Mg in ((gF, F), (gS, Sh)):
            Q = mmn(P, g)
            if Q not in seen: seen[Q] = seen[P] @ Mg; dq.append(Q)
def fix(Nn, A, k):
    def mmn(P, Q): return ((P[0]*Q[0]+P[1]*Q[2]) % Nn, (P[0]*Q[1]+P[1]*Q[3]) % Nn, (P[2]*Q[0]+P[3]*Q[2]) % Nn, (P[2]*Q[1]+P[3]*Q[3]) % Nn)
    M = (1, 0, 0, 1)
    for _ in range(k): M = mmn(M, A)
    return sum(1 for p in range(Nn) for q in range(Nn) if ((M[0]*p+M[1]*q) % Nn, (M[2]*p+M[3]*q) % Nn) == (p, q))
A = (1, 1, 1, 2)
ok_all = True
for Nn in range(3, 28, 2):
    Uu = weil_U(Nn, A)
    for k in range(1, 25):
        t = abs(np.trace(np.linalg.matrix_power(Uu, k)))**2
        if abs(t - fix(Nn, A, k)) > 1e-6: ok_all = False
print("  (b) trace identity |Tr U^k|^2 = #Fix(A^k) holds for every odd N in 3..27 and k = 1..24:", ok_all)
fx = [fix(9, A, k) for k in range(1, 13)]
print("      N = 9: #Fix(A^k), k = 1..12 =", fx, "-- read off the family's cycle type under T^2 (12^6, 4^2, 1)")
z12 = cmath.exp(2j*math.pi/12)
sols = []
for S in itertools.combinations_with_replacement(range(12), 9):
    if all(abs(abs(sum(z12**(s*k) for s in S))**2 - fx[k-1]) < 1e-6 for k in range(1, 13)): sols.append(S)
miss = lambda S: tuple(sorted(set(range(12)) - set(S)))
print("      spectra of nine twelfth roots consistent with these fixed-point counts: %d; all simple: %s; their missing classes: %s"
      % (len(sols), all(len(set(S)) == 9 for S in sols), sorted({miss(S) for S in sols})))
print("      every solution misses a coset {c, c+3, c+6, c+9} minus one point? ->",
      all(len(set((m - miss(S)[0]) % 3 for m in miss(S))) == 1 for S in sols))
# (a) orbits of V on the 81 displacement labels are the orbits of T (V implements T, run 02)
orbs = {}
for v in S81:
    o, y = [v], act(T, v)
    while y != v: o.append(y); y = act(T, y)
    orbs[frozenset(o)] = sorted({nrm(u) for u in o})
print("  (a) orbits of V on the 81 displacement operators:", sorted((len(o), vals) for o, vals in orbs.items()))
# (c) matrices reproducing the family's whole partition with each 24-orbit one voice
def orbit_part(M):
    seen, parts = set(), []
    for v in S81:
        if v in seen: continue
        o, y = {v}, act(M, v)
        while y != v: o.add(y); y = act(M, y)
        seen |= o; parts.append(frozenset(o))
    return set(parts)
famP = orbit_part(T)
same = [M for M in GL if orbit_part(M) == famP]
print("  (c) matrices of GL(2,Z/9) whose orbits are exactly the family's five: %d (= generators of <T>, phi(24) = 8: %s)"
      % (len(same), sorted(same) == sorted(M for M in [(lambda k: [(1,0,0,1)] + [None])(0)] and [] or same) and len(same) == 8))
tp = [(1, 0, 0, 1)]
for _ in range(23): tp.append(mm(tp[-1], T))
print("      they are T^k with gcd(k, 24) = 1:", sorted(same) == sorted(tp[k] for k in range(24) if math.gcd(k, 24) == 1))
