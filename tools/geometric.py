#!/usr/bin/env python3
"""SEQ 122 recomputation (standard library only).
Recomputes every figure in the two SEQ 122 attachments and the repairs offered.
Run: python3 geometric.py  -> prints a JSON report and a PASS count."""
import json, itertools, cmath, math
from fractions import Fraction as F

R = {}
def mm(X, Y, m=None):
    n, k, p = len(X), len(Y), len(Y[0])
    Z = [[sum(X[i][t]*Y[t][j] for t in range(k)) for j in range(p)] for i in range(n)]
    return [[z % m for z in r] for r in Z] if m else Z
def mv(M, v, m): return tuple(sum(M[i][j]*v[j] for j in range(len(v))) % m for i in range(len(M)))
def mpow(M, e, m):
    n = len(M); P = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(e): P = mm(P, M, m)
    return P
def order(M, m):
    n = len(M); I = [[int(i == j) for j in range(n)] for i in range(n)]
    P, k = [r[:] for r in M], 1
    while [[x % m for x in r] for r in P] != I: P = mm(P, M, m); k += 1
    return k
A = [[0, 1], [1, 1]]

# --- 1. L_A over Q: X -> A X A^T in coordinates (t,x,y,z), X = tI + x sx + y sy + z sz
def herm(t, x, y, z):  # entries as (re, im) pairs
    return [[(t+z, 0), (x, -y)], [(x, y), (t-z, 0)]]
def coords(X):
    t = (X[0][0][0]+X[1][1][0])/2; z = (X[0][0][0]-X[1][1][0])/2
    return (t, X[1][0][0], X[1][0][1], z)
def act(M, X):  # M real 2x2, returns M X M^T
    out = [[(0, 0)]*2 for _ in range(2)]
    for i in range(2):
        for j in range(2):
            re = im = 0
            for a in range(2):
                for b in range(2):
                    re += M[i][a]*X[a][b][0]*M[j][b]; im += M[i][a]*X[a][b][1]*M[j][b]
            out[i][j] = (re, im)
    return out
E4 = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
cols = [coords(act(A, herm(*[F(c) for c in e]))) for e in E4]
L = [[cols[j][i] for j in range(4)] for i in range(4)]
R['L_A'] = [[str(x) for x in r] for r in L]
eta = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]]
LT = [list(r) for r in zip(*L)]
R['LT_eta_L_eq_eta'] = mm(mm(LT, eta), L) == eta
def det(M):
    if len(M) == 1: return M[0][0]
    return sum((-1)**j*M[0][j]*det([r[:j]+r[j+1:] for r in M[1:]]) for j in range(len(M)))
R['det_L'] = str(det(L)); R['L00'] = str(L[0][0])
# characteristic polynomial check: (x^2-3x+1)(x+1)^2
def charpoly_at(x): return det([[ (x if i == j else 0) - L[i][j] for j in range(4)] for i in range(4)])
R['charpoly_is_(x2-3x+1)(x+1)2'] = all(charpoly_at(F(x)) == (x*x-3*x+1)*(x+1)**2 for x in range(-5, 6))
v1, v2 = (0, 0, 1, 0), (0, 1, 0, 2)
Lv = lambda v: tuple(sum(L[i][j]*v[j] for j in range(4)) for i in range(4))
R['minus1_eigenplane'] = Lv(v1) == tuple(-c for c in v1) and Lv(v2) == tuple(-c for c in v2)
R['eigenplane_spacelike'] = [v[0]**2-v[1]**2-v[2]**2-v[3]**2 for v in (v1, v2)]

# --- spinor B = iA: B X B^dag = A X A^T and det B = 1 (complex arithmetic)
B = [[1j*a for a in r] for r in A]
def cmat(X): return [[complex(*e) for e in r] for r in X]
def dag(M): return [[M[j][i].conjugate() for j in range(2)] for i in range(2)]
ok = True
for e in E4:
    X = cmat(herm(*e)); Y = mm(mm(B, X), dag(B)); Z = cmat(act(A, herm(*e)))
    ok &= all(abs(Y[i][j]-Z[i][j]) < 1e-12 for i in range(2) for j in range(2))
R['spinor_B_ok'] = ok; R['det_B'] = str(B[0][0]*B[1][1]-B[0][1]*B[1][0])

# --- 2. L_A mod 9, order, census, fixed points
def Lmod(m):
    inv2 = pow(2, -1, m)
    return [[(x.numerator*pow(x.denominator, -1, m)) % m for x in r] for r in L]
L9 = Lmod(9); R['L_A_mod9'] = L9; R['order_L_mod9'] = order(L9, 9)
R['order_A_mod9'] = order(A, 9); R['A12_mod9'] = mpow(A, 12, 9)
states = list(itertools.product(range(9), repeat=4))
seen, census = set(), {}
for s in states:
    if s in seen: continue
    o, c = 0, s
    while True:
        seen.add(c); o += 1; c = mv(L9, c, 9)
        if c == s: break
    census[o] = census.get(o, 0)+1
R['census_6561'] = dict(sorted(census.items())); R['orbits_6561'] = sum(census.values())
fix = {}
for d in (1, 2, 3, 4, 6, 12):
    P = mpow(L9, d, 9); fix[d] = sum(1 for s in states if mv(P, s, 9) == s)
R['fixed_points'] = fix
# depth-2 geometric order (mod 81) and A order mod 81
L81 = Lmod(81); R['order_L_mod81'] = order(L81, 81); R['order_A_mod81'] = order(A, 81)
R['A_half_mod81_is_minusI'] = mpow(A, R['order_A_mod81']//2, 81) == [[80, 0], [0, 80]]

# --- 3. H_Q from spectral projectors on l2(81)
st = list(itertools.product(range(9), repeat=2)); idx = {s: i for i, s in enumerate(st)}
perm = [idx[mv(A, s, 9)] for s in st]
orb, seen2 = [], set()
for s in range(81):
    if s in seen2: continue
    o, c = [], s
    while c not in seen2: seen2.add(c); o.append(c); c = perm[c]
    orb.append(len(o))
R['orbits_81'] = sorted(orb, reverse=True)
mult = {k: sum(1 for Lj in orb if (k*Lj) % 24 == 0) for k in range(-11, 13)}
R['mult_k0'] = mult[0]; R['mult_sum'] = sum(mult.values())
R['mult_profile'] = {'4': sum(1 for k in mult if k and mult[k] == 4), '3': sum(1 for k in mult if mult[k] == 3)}
# exactness: exp(-i H dt/hbar) = U on a random vector, with H = (2pi/24) sum k Pi_k (hbar = dt = 1)
import random; random.seed(122)
psi = [complex(random.random(), random.random()) for _ in range(81)]
def Un(v, n):
    for _ in range(n % 24):
        w = [0j]*81
        for i in range(81): w[perm[i]] = v[i]
        v = w
    return v
pows = [Un(psi, n) for n in range(24)]
out = [0j]*81
for k in range(-11, 13):
    Pk = [sum(cmath.exp(2j*math.pi*k*n/24)*pows[n][i] for n in range(24))/24 for i in range(81)]
    ph = cmath.exp(-1j*2*math.pi*k/24)
    out = [out[i]+ph*Pk[i] for i in range(81)]
target = Un(psi, 1)
R['expH_equals_U'] = max(abs(out[i]-target[i]) for i in range(81)) < 1e-9
R['uniform_weights'] = [str(F(Lj, 81)) for Lj in sorted(orb, reverse=True)]
R['joint_dim'] = 81+6561; R['joint_zero_mult'] = mult[0]+R['orbits_6561']
R['joint_order'] = math.lcm(R['order_A_mod9'], R['order_L_mod9'])
# coupling: H_c = g(|u1><u2| + h.c.), exact two-level rotation
g, tau = 0.7, 1.3
R['coupling_p'] = [round(math.cos(g*tau)**2, 12), round(math.sin(g*tau)**2, 12)]

# --- 4. Hensel roots of x^2 = -1 in Z[phi]/3^12  (phi^2 = phi + 1)
M12 = 3**12
def zmul(u, v, m):
    a, b = u; c, d = v
    return ((a*c+b*d) % m, (a*d+b*c+b*d) % m)
gpt = (255713, 20015); mine = (275728, 511426)
R['gpt_root_sq'] = zmul(gpt, gpt, M12); R['mine_root_sq'] = zmul(mine, mine, M12)
R['roots_are_negatives'] = ((gpt[0]+mine[0]) % M12, (gpt[1]+mine[1]) % M12) == (0, 0)
R['phi6_mod9'] = (lambda p: p)(
    __import__('functools').reduce(lambda x, _: zmul(x, (0, 1), 9), range(6), (1, 0)))

# --- 5. null counts by convolution of square distributions
def null_count(m):
    sq = [0]*m
    for x in range(m): sq[x*x % m] += 1
    pos = [0]*m
    for a in range(m):
        for b in range(m): pos[(a+b) % m] += sq[a]*sq[b]   # x^2+y^2
    three = [0]*m
    for a in range(m):
        for b in range(m): three[(a+b) % m] += pos[a]*sq[b]  # x^2+y^2+z^2
    return sum(sq[t]*three[t] for t in range(m))           # t^2 = x^2+y^2+z^2
R['null'] = {k: null_count(3**k) for k in range(1, 5)}
N = {0: 1, 1: 21}
for k in range(2, 5): N[k] = 20*3**(3*(k-1))+81*N[k-2]
R['null_recurrence'] = N

# --- 6. Kottler: f = 1 - rs/r - Lam r^2/3; mixed Einstein tensor (exact, rational)
def kottler(rs, Lam, r):
    f = 1-rs/r-Lam*r*r/3; f1 = rs/r**2-2*Lam*r/3; f2 = -2*rs/r**3-2*Lam/3
    return ((r*f1+f-1)/r**2, (r*f2+2*f1)/(2*r))
R['kottler_G_mixed'] = [str(x) for x in kottler(F(2), F(1, 10), F(7))]
R['kottler_ok'] = all(x == -F(1, 10) for x in kottler(F(2), F(1, 10), F(7)))

# --- 7. Qwen's embedding E(a,b) = (a+b, a, b, a-b)
Eq = lambda a, b: ((a+b) % 9, a % 9, b % 9, (a-b) % 9)
img = {Eq(*s) for s in st}
R['qwen_E_injective'] = len(img) == 81
R['qwen_E_intertwines'] = sum(1 for s in st if mv(L9, Eq(*s), 9) == Eq(*mv(A, s, 9)))
R['qwen_image_invariant'] = sum(1 for s in st if mv(L9, Eq(*s), 9) in img)
# linear intertwiners M9 -> V9 (solve L E = E A over Z/9 by brute force on generators)
lin = 0
for e1 in states:            # E(1,0)
    # E A (1,0) = E(0,1) must equal L E(1,0): determines E(0,1)
    e2 = mv(L9, e1, 9)
    # second condition: L E(0,1) = E(A(0,1)) = E(1,1) = e1 + e2
    if mv(L9, e2, 9) == tuple((x+y) % 9 for x, y in zip(e1, e2)): lin += 1
R['linear_intertwiners'] = lin
# the native quadratic embedding s -> s s^T (null vectors): t=(a2+b2)/2, x=ab, y=0, z=(a2-b2)/2
i2 = pow(2, -1, 9)
Q2 = lambda a, b: ((a*a+b*b)*i2 % 9, a*b % 9, 0, (a*a-b*b)*i2 % 9)
R['quad_intertwines'] = all(mv(L9, Q2(*s), 9) == Q2(*mv(A, s, 9)) for s in st)
R['quad_null'] = all((t*t-x*x-y*y-z*z) % 9 == 0 for (t, x, y, z) in (Q2(*s) for s in st))
R['quad_fibre_is_sign'] = all(Q2(*s) == Q2((-s[0]) % 9, (-s[1]) % 9) for s in st)
qimg = {Q2(*s) for s in st}; R['quad_image_size'] = len(qimg)
qorb, qs = [], set()
for p in qimg:
    if p in qs: continue
    o, c = 0, p
    while True:
        qs.add(c); o += 1; c = mv(L9, c, 9)
        if c == p: break
    qorb.append(o)
R['quad_image_orbits'] = sorted(qorb, reverse=True)
# extra coincidences of the quadratic map beyond +-s
fib = {}
for s in st: fib.setdefault(Q2(*s), set()).add(s)
R['quad_fibre_sizes'] = dict(sorted({len(v): sum(1 for w in fib.values() if len(w) == len(v)) for v in fib.values()}.items()))
# Qwen's metric Tr(rho X_mu X_nu) with rho = I/2 (maximally mixed 2x2): Euclidean
sig = [[[1, 0], [0, 1]], [[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]]]
def tr(M): return M[0][0]+M[1][1]
gq = [[(tr(mm(sig[m], sig[n]))/2).real for n in range(4)] for m in range(4)]
R['qwen_metric_rho_half_I'] = gq
# repair: polarization of det, g(X,Y) = (tr X tr Y - tr XY)/2 = eta
gd = [[((tr(sig[m])*tr(sig[n])-tr(mm(sig[m], sig[n])))/2).real for n in range(4)] for m in range(4)]
R['det_polarization_metric'] = gd

checks = [
 ('L_A in SO+(3,1), eigenvalues phi^2, phi^-2, -1, -1', R['LT_eta_L_eq_eta'] and R['det_L'] == '1' and R['charpoly_is_(x2-3x+1)(x+1)2']),
 ('spacelike period-2 eigenplane of L_A', R['minus1_eigenplane'] and all(q < 0 for q in R['eigenplane_spacelike'])),
 ('spinor B = iA, det 1, B X B^dag = A X A^T', R['spinor_B_ok']),
 ('L_A mod 9 and order 12', R['L_A_mod9'] == [[6, 1, 0, 4], [1, 1, 0, 8], [0, 0, 8, 0], [4, 8, 0, 4]] and R['order_L_mod9'] == 12 and R['order_A_mod9'] == 24),
 ('geometric census 1 + 40x2 + 162x4 + 486x12', R['census_6561'] == {1: 1, 2: 40, 4: 162, 12: 486} and R['orbits_6561'] == 689),
 ('fixed points of L^d', R['fixed_points'] == {1: 1, 2: 81, 3: 1, 4: 729, 6: 81, 12: 6561}),
 ('geometric order 108 at depth 2', R['order_L_mod81'] == 108 and R['order_A_mod81'] == 216 and R['A_half_mod81_is_minusI']),
 ('H_Q from spectral projectors, exp = U_A', R['mult_k0'] == 5 and R['mult_sum'] == 81 and R['expH_equals_U']),
 ('joint system 6642, zero multiplicity 694, order 24', R['joint_dim'] == 6642 and R['joint_zero_mult'] == 694 and R['joint_order'] == 24),
 ('Hensel roots +-r12 mod 3^12', R['gpt_root_sq'] == (M12-1, 0) and R['mine_root_sq'] == (M12-1, 0) and R['roots_are_negatives']),
 ('null recurrence N_k', R['null'] == {k: N[k] for k in range(1, 5)}),
 ('Kottler G = -Lambda g', R['kottler_ok']),
 ('null embedding s -> s s^T equivariant', R['quad_intertwines'] and R['quad_null'] and R['quad_fibre_is_sign'] and R['quad_image_orbits'] == [12, 12, 12, 1]),
 ('linear embedding E(a,b) not equivariant', R['linear_intertwiners'] == 1 and R['qwen_E_intertwines'] == 1),
 ('trace form Euclidean, det form Lorentzian', R['qwen_metric_rho_half_I'] == [[float(i == j) for j in range(4)] for i in range(4)] and R['det_polarization_metric'] == [[float(i == j)*(1 if i == 0 else -1) for j in range(4)] for i in range(4)]),
]
R['PASS'] = f"{sum(1 for _, c in checks if c)} of {len(checks)}"
import sys
if '--selftest' in sys.argv:
    for n, c in checks: print(f"{n} ... {'PASS' if c else 'FAIL'}")
    print('geometric.py selftest', R['PASS']); sys.exit(0 if all(c for _, c in checks) else 1)
print(json.dumps(R, indent=1, default=str))
