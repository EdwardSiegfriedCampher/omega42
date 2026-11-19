"""records/positive_geometry/independent_check.py -- independent exact checks of the positive-geometry record
(Core FP-GoldenArc, FP-TwistedQuotient, M230-K PG-01 and PG-05; Companion 50.6 and 50.15).

Written to share no code with compute.py and to use a different method for each claim:
  1. EXACT ALGEBRA      in Q(sqrt 5), with exact signs: the eigenbasis of T, the golden-arc identity N(c1 Z1 + c2 Z2)
                        = -5 c1 c2 (PG-01), T and T^2 on the coordinates (c1, c2), the canonical form under T^2.
  2. FINITE STATES      the 81 states enumerated by union-find, not by following orbits; the norm-zero classification;
                        the norm-negation identity N(Ts) = -N(s) mod 9.
  3. TWISTED SHIFT      the operator sigma (not T): sigma acts on k x n matrices by the twisted cyclic column shift; its
                        order on matrix representatives from the powers of its n x n matrix, and its order on points of
                        Gr(2, 12) from the rank of [M ; M sigma^j], not from Pluecker coordinates.
  4. MINIMAL LIFTS      (PG-05) by solving N(a, b) = n for each candidate n in increasing |n| with an exact integer
                        square root, not by searching a box.
Standard library only. Prints PASS or FAIL per check and exits non-zero on any FAIL.
"""
import sys
from fractions import Fraction as Fr
from math import isqrt

ok = True
def check(label, cond):
    global ok
    print('%-100s %s' % (label, 'PASS' if cond else 'FAIL')); ok &= bool(cond)


class Q5:
    """x + y sqrt 5 with rational x, y; exact sign."""
    def __init__(s, x, y=0): s.x, s.y = Fr(x), Fr(y)
    def __add__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.x + o.x, s.y + o.y)
    __radd__ = __add__
    def __neg__(s): return Q5(-s.x, -s.y)
    def __sub__(s, o): return s + (-(o if isinstance(o, Q5) else Q5(o)))
    def __rsub__(s, o): return Q5(o) - s
    def __mul__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.x * o.x + 5 * s.y * o.y, s.x * o.y + s.y * o.x)
    __rmul__ = __mul__
    def inv(s): d = s.x * s.x - 5 * s.y * s.y; return Q5(s.x / d, -s.y / d)
    def __truediv__(s, o): return s * (o if isinstance(o, Q5) else Q5(o)).inv()
    def __eq__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s.x == o.x and s.y == o.y
    def sign(s):
        # sign of x + y sqrt5, exactly
        if s.y == 0: return (s.x > 0) - (s.x < 0)
        if s.x == 0: return (s.y > 0) - (s.y < 0)
        if (s.x > 0) == (s.y > 0): return 1 if s.x > 0 else -1
        return (1 if s.x > 0 else -1) * (1 if s.x * s.x > 5 * s.y * s.y else -1)


print('=== 1. Exact algebra over Q(sqrt 5) ===')
phi = Q5(Fr(1, 2), Fr(1, 2)); iphi = phi.inv()
check('phi^2 = phi + 1 and 1/phi = phi - 1', phi * phi == phi + 1 and iphi == phi - 1)
N = lambda v: v[0] * v[0] + v[0] * v[1] - v[1] * v[1]
Tv = lambda v: (v[1], v[0] + v[1])
Z1 = (Q5(1), phi); Z2 = (Q5(-1), iphi)
check('T Z1 = phi Z1 and T Z2 = (-1/phi) Z2: the rows of Z are the eigenvectors of T',
      Tv(Z1) == (phi * Z1[0], phi * Z1[1]) and Tv(Z2) == (-iphi * Z2[0], -iphi * Z2[1]))
detZ = Z1[0] * Z2[1] - Z1[1] * Z2[0]
check('det Z = sqrt 5 > 0, so Z is admissible data for A(2,1,1)', detZ == Q5(0, 1) and detZ.sign() == 1)
B = lambda u, v: u[0] * v[0] + (u[0] * v[1] + u[1] * v[0]) / 2 - u[1] * v[1]
check('N(Z1) = N(Z2) = 0 and 2 B(Z1, Z2) = -5, so N(c1 Z1 + c2 Z2) = -5 c1 c2 identically', N(Z1) == 0 and N(Z2) == 0 and 2 * B(Z1, Z2) == -5)
pts = [(Fr(p), Fr(q)) for p in range(-4, 5) for q in range(-4, 5) if (p, q) != (0, 0)]
good = True
for c1, c2 in pts:
    v = (c1 * Z1[0] + c2 * Z2[0], c1 * Z1[1] + c2 * Z2[1])
    good &= N(v) == Q5(-5 * c1 * c2) and ((c1 * c2 > 0) == (N(v).sign() < 0))
check('on 80 exact points: in the image of G>0(1,2) (c1 c2 > 0) exactly when N < 0 -- A(2,1,1)(Z) = the golden arc', good)
check('T on (c1, c2) is diag(phi, -1/phi): one entry negative, outside the positive torus', phi.sign() == 1 and (-iphi).sign() == -1)
check('T^2 on (c1, c2) is diag(phi^2, 1/phi^2): both positive, inside the positive torus', (phi * phi).sign() == 1 and (iphi * iphi).sign() == 1)
r = phi.inv() * phi.inv() * phi.inv() * phi.inv()
check('T^2 multiplies c2/c1 by phi^-4, a positive constant: d log(c2/c1) is preserved exactly', (iphi * iphi) / (phi * phi) == r and r.sign() == 1)
check('T multiplies c2/c1 by -phi^-2, a negative constant: the arc goes onto its complement', ((-iphi) / phi).sign() == -1)

print('=== 2. The 81 states, by union-find ===')
par = {(a, b): (a, b) for a in range(9) for b in range(9)}
def find(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
T9 = lambda s: (s[1], (s[0] + s[1]) % 9)
for s in list(par): par[find(s)] = find(T9(s))
from collections import Counter
sizes = sorted(Counter(find(s) for s in par).values(), reverse=True)
check('orbit sizes 24, 24, 24, 8, 1', sizes == [24, 24, 24, 8, 1])
N9 = lambda s: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
zero = sorted(s for s in par if N9(s) == 0)
check('N = 0 mod 9 exactly on the nine states with a = b = 0 mod 3', zero == sorted((a, b) for a in (0, 3, 6) for b in (0, 3, 6)))
check('the other 72 states have unit norm (no state has norm 3 or 6)', sum(1 for s in par if N9(s) % 3) == 72)
check('the nine norm-zero states are the eight-cycle and the fixed state', sorted(Counter(find(s) for s in zero).values()) == [1, 8])
check('norm-negation identity N(Ts) = -N(s) mod 9 on all 81 states', all(N9(T9(s)) == (-N9(s)) % 9 for s in par))
def Tpow(s, j):
    for _ in range(j): s = T9(s)
    return s
check('T^12 = -I on every state, T^24 = I', all(Tpow(s, 12) == ((-s[0]) % 9, (-s[1]) % 9) and Tpow(s, 24) == s for s in par))

print('=== 3. The twisted cyclic shift sigma on G>0(2, 12) ===')
n, k = 12, 2
P = [[Fr(0)] * n for _ in range(n)]
for j in range(1, n): P[j][j - 1] = Fr(1)       # column j of M sigma is column j+1 of M ...
P[0][n - 1] = Fr((-1) ** (k - 1))             # ... and the last is (-1)^(k-1) times the first
mm = lambda A, B: [[sum(A[i][t] * B[t][j] for t in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
I = [[Fr(int(i == j)) for j in range(n)] for i in range(n)]
Pw = I; powers = []
for j in range(1, 25): Pw = mm(Pw, P); powers.append(Pw)
check('sigma^12 = -I as a 12 x 12 matrix (the lift)', powers[11] == [[-x for x in row] for row in I])
check('order of sigma on matrix representatives is 24', powers[23] == I and all(powers[j] != I for j in range(23)))
t = [Fr(i * i + 1, 3) for i in range(n)]
M = [[Fr(1)] * n, t]
def minors_pos(A):
    return all(A[0][i] * A[1][j] - A[0][j] * A[1][i] > 0 for i in range(n) for j in range(i + 1, n))
def rank(rows):
    R = [r[:] for r in rows]; rk = 0
    for c in range(len(R[0])):
        p = next((i for i in range(rk, len(R)) if R[i][c] != 0), None)
        if p is None: continue
        R[rk], R[p] = R[p], R[rk]
        for i in range(len(R)):
            if i != rk and R[i][c] != 0:
                f = R[i][c] / R[rk][c]; R[i] = [a - f * b for a, b in zip(R[i], R[rk])]
        rk += 1
    return rk
check('M is a point of G>0(2,12) and every M sigma^j stays positive', minors_pos(M) and all(minors_pos(mm(M, powers[j])) for j in range(24)))
same = [j + 1 for j in range(24) if rank(M + mm(M, powers[j])) == 2]
check('M sigma^j spans the same plane as M exactly for j = 12 and 24: order 12 on points of Gr(2,12)', same == [12, 24])

print('=== 4. PG-05, minimal lifts by solving N(a, b) = n ===')
def solutions(nv, s):
    """integer (a, b) with N(a, b) = nv and (a, b) = s mod 9, b in a range: a = (-b +- sqrt(5 b^2 + 4 nv)) / 2"""
    for b in range(-60, 61):
        d = 5 * b * b + 4 * nv
        if d < 0: continue
        r = isqrt(d)
        if r * r != d: continue
        for a2 in (-b + r, -b - r):
            if a2 % 2 == 0 and (a2 // 2 % 9, b % 9) == s: return True
    return False
SEV = {1, 2, 4}
res = {}
for s in par:
    if s == (0, 0): continue
    for m in range(1, 40):
        sg = [v for v in (m, -m) if v % 9 == N9(s) or (N9(s) == 0 and v % 9 == 0)]
        hit = [v for v in sg if solutions(v, s)]
        if hit: res[s] = hit; break
check('every one of the 80 nonzero states has a least lift norm of one sign only', len(res) == 80 and all(len(v) == 1 for v in res.values()))
check('least |N| is 1 on Voice A, 4 on Voice B, 11 on Voice C, 9 on the core',
      all(abs(res[s][0]) == {1: 1, 8: 1, 4: 4, 5: 4, 2: 11, 7: 11, 0: 9}[N9(s)] for s in res))
check('half SEVENTH <-> positive least norm, MANIFEST <-> negative, on all 72 unit states',
      all((N9(s) in SEV) == (res[s][0] > 0) for s in res if N9(s)))
check('on the core, residual norm 1 mod 3 <-> positive least norm, 2 <-> negative (AXIS +/-)',
      all((((s[0] // 3) ** 2 + (s[0] // 3) * (s[1] // 3) - (s[1] // 3) ** 2) % 3 == 1) == (res[s][0] > 0) for s in res if N9(s) == 0))
check('T reverses the sign of the least norm on all 80: the arcs are exchanged as the halves are', all((res[T9(s)][0] > 0) != (res[s][0] > 0) for s in res))
print('INDEPENDENT CHECK: %s' % ('PASS' if ok else 'FAIL'))
sys.exit(0 if ok else 1)
