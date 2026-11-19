#!/usr/bin/env python3
"""Physical pilot 02: the revised screen C11' with held-out null systems, exactly as frozen in 00_freeze.txt.
Standard library only."""
from collections import Counter
from itertools import product

FAMILY_CENSUS = {1: 1, 8: 1, 24: 3}

def apply(A, x, m):
    return ((A[0][0] * x[0] + A[0][1] * x[1]) % m, (A[1][0] * x[0] + A[1][1] * x[1]) % m)

def matmul(A, B, m):
    return ((sum(A[0][k] * B[k][0] for k in range(2)) % m, sum(A[0][k] * B[k][1] for k in range(2)) % m),
            (sum(A[1][k] * B[k][0] for k in range(2)) % m, sum(A[1][k] * B[k][1] for k in range(2)) % m))

def mpow(A, n, m):
    R = ((1, 0), (0, 1))
    for _ in range(n): R = matmul(R, A, m)
    return R

def census(A, m):
    seen, c = set(), Counter()
    for x in product(range(m), repeat=2):
        if x in seen: continue
        L, y = 0, x
        while y not in seen: seen.add(y); y = apply(A, y, m); L += 1
        c[L] += 1
    return dict(c)

def j2(A, m):
    return mpow(A, 12, m) == (((-1) % m, 0), (0, (-1) % m))

def j3(A, m):
    states = list(product(range(m), repeat=2))
    for a, b, c in product(range(m), repeat=3):
        Q = lambda x: (a * x[0] * x[0] + b * x[0] * x[1] + c * x[1] * x[1]) % m
        if all(Q(apply(A, x, m)) == (-Q(x)) % m for x in states) and sum(1 for x in states if Q(x) == 0) == 9:
            return True, (a, b, c)
    return False, None

def screen(A, m):
    cen = census(A, m); J1 = cen == FAMILY_CENSUS; J2 = j2(A, m)
    J3, form = j3(A, m) if (J1 and J2) else (None, None)
    return J1, J2, J3, cen, form

def show(name, J1, J2, J3, note):
    ok = bool(J1 and J2 and J3)
    print('%-44s J1 %-5s J2 %-5s J3 %-13s | C11\' %s | %s' % (name, J1, J2, 'not evaluated' if J3 is None else J3, 'PASS' if ok else 'FAIL', note))
    return ok

T = ((0, 1), (1, 1))
print("PILOT 02 -- revised screen C11' (freeze SHA-256 in 02_freeze_sha256.txt)")
res = {}
J1, J2, J3, cen, form = screen(T, 9); res['P0'] = show('P0 family T mod 9', J1, J2, J3, 'census %s; anti-invariant form %s' % (cen, form))

# GL2(Z/9), conjugacy to powers of T
units9 = [u for u in range(9) if u % 3]
GL = [((a, b), (c, d)) for a, b, c, d in product(range(9), repeat=4) if ((a * d - b * c) % 9) in units9]
def inv(A):
    a, b = A[0]; c, d = A[1]; di = pow((a * d - b * c) % 9, -1, 9)
    return ((d * di % 9, -b * di % 9), (-c * di % 9, a * di % 9))
conjT = {matmul(matmul(S, T, 9), inv(S), 9) for S in GL}
powT = {mpow(T, k, 9) for k in range(1, 24) if __import__('math').gcd(k, 24) == 1}
famlike = {matmul(matmul(S, P, 9), inv(S), 9) for S in GL for P in powT}
p1 = [screen(A, 9) for A in sorted(conjT)]
res['P1'] = show('P1 all %d conjugates of T in GL2(Z/9)' % len(conjT), all(r[0] for r in p1), all(r[1] for r in p1), all(r[2] for r in p1), 'every conjugate screened')
p2 = [screen(P, 9) for P in sorted(powT)]
res['P2'] = show('P2 the %d powers T^k, gcd(k, 24) = 1' % len(powT), all(r[0] for r in p2), all(r[1] for r in p2), all(r[2] for r in p2), 'k = 1, 5, 7, 11, 13, 17, 19, 23')

# design case
J1, J2, J3, cen, form = screen(T, 18); res['D1'] = show('D1 Fibonacci mod 18 (design case)', J1, J2, J3, 'census %s' % cen)

held = {}
for m in (27, 36, 45, 63, 72, 81, 90, 99):
    cen = census(T, m); J1 = cen == FAMILY_CENSUS; J2 = j2(T, m)
    held['H1 mod %d' % m] = show('H1 Fibonacci mod %d' % m, J1, J2, None if not (J1 and J2) else j3(T, m)[0], 'census %s' % dict(sorted(cen.items())))
h2 = []
for p in range(9):
    for q in units9:
        if (p, q) == (1, 1): continue
        A = ((0, 1), (q, p)); r = screen(A, 9); h2.append(((p, q), r))
h2pass = [pq for pq, r in h2 if r[0] and r[1] and r[2]]
held['H2'] = show('H2 %d other recurrences mod 9' % len(h2), any(r[0] for _, r in h2), any(r[1] for _, r in h2), bool(h2pass) if h2pass else False,
                  'passing (p, q): %s; of these conjugate to a power of T: %s' % (h2pass or 'NONE', [pq for pq in h2pass if ((0, 1), (pq[1], pq[0])) in famlike]))
# H3 product with a two-state flip
seen, c3 = set(), Counter()
for x in product(range(9), range(9), range(2)):
    if x in seen: continue
    L, y = 0, x
    while y not in seen: seen.add(y); y = (y[1], (y[0] + y[1]) % 9, 1 - y[2]); L += 1
    c3[L] += 1
held['H3'] = show('H3 family x two-state flip', dict(c3) == FAMILY_CENSUS, None, None, 'census %s' % dict(sorted(c3.items())))
# H4 all of GL2(Z/9)
passing = [A for A in GL if all(screen(A, 9)[:3])]
inside = [A for A in passing if A in famlike]
others = [A for A in passing if A not in famlike]
held['H4'] = show('H4 all %d matrices of GL2(Z/9)' % len(GL), None, None, bool(others), '%d pass C11\'; %d of them are conjugates of a power of T coprime to 24 (the family); outside the family: %d' % (len(passing), len(inside), len(others)))
# H5 physical models of pilot 01, without a linear state space with the family census
for nm, note in (('string', 'no finite state space with a census'), ('closed pipe', 'no finite state space with a census'),
                 ('spin-1/2, 30 degrees per step', 'state space is the qubit sphere; U^12 = -I but no census 1+8+24+24+24'),
                 ('24-site ring', 'census {24: 1}'), ('day cycle', 'no finite state space with a census'), ('SU(9)_1 twist', 'order 9')):
    held['H5 ' + nm] = show('H5 ' + nm, False, None, None, note)

cal = res['P0'] and res['P1'] and res['P2'] and not any(held.values())
print("CALIBRATION: %s -- positives %s; held-out nulls passing: %s; design case D1: %s"
      % ('PASS' if cal else 'FAIL', 'PASS' if res['P0'] and res['P1'] and res['P2'] else 'FAIL',
         [k for k, v in held.items() if v] or 'NONE', 'PASS' if res['D1'] else 'FAIL'))
