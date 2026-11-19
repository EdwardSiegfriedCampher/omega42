#!/usr/bin/env python3
"""Physical pilot 01: method calibration of the spectral screen C11, exactly as frozen in 00_freeze.txt.
Standard library only."""
import cmath, math
from fractions import Fraction

def powers(x):
    L = len(x); return [abs(sum(x[n] * cmath.exp(-2j * math.pi * k * n / L) for n in range(L))) ** 2 for k in range(L)]

def k3(x):
    """odd harmonics only; exactly two nonzero levels in ratio 1:2; the larger exactly at 3, 9, 15, 21."""
    if len(x) != 24: return False, 'length %d' % len(x)
    P = powers(x); tot = sum(P) or 1
    if any(P[k] > 1e-9 * tot for k in range(0, 24, 2)): return False, 'even harmonics present'
    lv = sorted({round(P[k] / tot, 9) for k in range(1, 24, 2) if P[k] > 1e-9 * tot})
    if len(lv) != 2: return False, '%d nonzero odd levels' % len(lv)
    if abs(lv[1] / lv[0] - 2) > 1e-6: return False, 'level ratio %.4f' % (lv[1] / lv[0])
    big = sorted(k for k in range(1, 24, 2) if abs(P[k] / tot - lv[1]) < 1e-9)
    return big == [3, 9, 15, 21], 'larger level at %s' % big

def centred(v, m):
    v %= m
    return v - m if v > m // 2 else v

def mat_pow_ident(m, n):
    """T^n mod m as (e1, e2) images."""
    e1, e2 = (1, 0), (0, 1)
    for _ in range(n): e1 = (e1[1], (e1[0] + e1[1]) % m); e2 = (e2[1], (e2[0] + e2[1]) % m)
    return e1, e2

def ground(m):
    ident = ((1, 0), (0, 1)); neg = (((-1) % m, 0), (0, (-1) % m))
    P = next(n for n in range(1, 10000) if mat_pow_ident(m, n) == ident)
    K1 = P == 24
    K2 = P == 24 and mat_pow_ident(m, 12) == neg
    seen, orbs = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o, x = [], (a, b)
            while x not in seen: seen.add(x); o.append(x); x = (x[1], (x[0] + x[1]) % m)
            orbs.append(o)
    Lmax = max(len(o) for o in orbs); longest = [o for o in orbs if len(o) == Lmax]
    res = [k3([centred(a, m) for a, b in o]) for o in longest]
    K3 = any(r[0] for r in res)
    nulls = sum(1 for a in range(m) for b in range(m) if (a * a + a * b - b * b) % m == 0)
    K4 = nulls == 9
    return P, K1, K2, K3, K4, '%d longest orbit(s) of length %d; K3 met by %d; null states %d' % (len(longest), Lmax, sum(r[0] for r in res), nulls)

rows = []
def row(name, K1, K2, K3, K4, S3, note):
    c11 = K1 and K2 and K3 and K4
    rows.append((name, c11))
    print('%-34s K1 %-5s K2 %-5s K3 %-5s K4 %-5s | C11 %-4s | S3 %-14s | %s' % (name, K1, K2, K3, K4, 'PASS' if c11 else 'FAIL', S3, note))

print('PILOT 01 -- C11 method calibration (freeze SHA-256 in 02_freeze_sha256.txt)')
P, K1, K2, K3, K4, note = ground(9)
row('S0 family, mod 9', K1, K2, K3, K4, 'internal', note)

# S1 quantum cat map N = 9: V = U(T R) K
N = 9; w = cmath.exp(2j * math.pi / N); inv2 = pow(2, -1, N)
def U(a, b, c_, d):
    bi = pow(b % N, -1, N)
    return [[w ** ((inv2 * bi * (a * k * k - 2 * j * k + d * j * j)) % N) / math.sqrt(N) for k in range(N)] for j in range(N)]
def mm(A, B): return [[sum(A[i][t] * B[t][j] for t in range(N)) for j in range(N)] for i in range(N)]
def conj(A): return [[x.conjugate() for x in r] for r in A]
def prop(A, B):
    i, j = max(((i, j) for i in range(N) for j in range(N)), key=lambda p: abs(B[p[0]][p[1]]))
    if abs(B[i][j]) < 1e-12: return False
    k = A[i][j] / B[i][j]
    return abs(abs(k) - 1) < 1e-9 and all(abs(A[x][y] - k * B[x][y]) < 1e-9 for x in range(N) for y in range(N))
UB = U(0, -1, 1, -1); V2 = mm(UB, conj(UB))
I9 = [[1.0 * (i == j) for j in range(N)] for i in range(N)]; PAR = [[1.0 * ((i + j) % N == 0) for j in range(N)] for i in range(N)]
M, per = I9, None
for j in range(1, 25):
    M = mm(M, V2)
    if prop(M, I9): per = 2 * j; break
M12 = I9
for _ in range(6): M12 = mm(M12, V2)
psi = [0j] * N; psi[2] = 1
sig = []
for t in range(24):
    sig.append(sum(centred(x, N) * abs(psi[x]) ** 2 for x in range(N)))
    psi = [sum(UB[i][k] * psi[k].conjugate() for k in range(N)) for i in range(N)]
ok3, n3 = k3(sig)
row('S1 quantum cat map, N = 9', per == 24, prop(M12, PAR), ok3, True, 'NOT MET (N)', 'period of V %s; quantum observable: %s; mean %.3f' % (per, n3, sum(sig) / 24))

for m in (6, 10, 12, 16, 18):
    P, K1, K2, K3, K4, note = ground(m)
    row('S%d cat-map ground, mod %d' % ({6: 2, 10: 3, 12: 4, 16: 5, 18: 6}[m], m), K1, K2, K3, K4, 'NOT MET (N)', 'period %d; %s' % (P, note))

# S7 string
y = [sum(math.sin(n * math.pi / 5) / n ** 2 * math.sin(n * math.pi * 0.3) * math.cos(2 * math.pi * n * t / 24) for n in range(1, 400)) for t in range(24)]
ok3, n3 = k3(y)
row('S7 plucked string', True, all(abs(y[(t + 12) % 24] + y[t]) < 1e-9 for t in range(24)), ok3, False, 'NOT MET', 'sampled; %s' % n3)
# S8 closed pipe
p = [sum(math.cos(2 * math.pi * n * t / 24) / n ** 2 for n in range(1, 400, 2)) for t in range(24)]
ok3, n3 = k3(p)
row('S8 pipe closed at one end', True, all(abs(p[(t + 12) % 24] + p[t]) < 1e-9 for t in range(24)), ok3, False, 'NOT MET', 'sampled; %s' % n3)
# S9 spin-1/2, 30 degrees per step about x
th = math.radians(30); Ux = [[math.cos(th / 2), -1j * math.sin(th / 2)], [-1j * math.sin(th / 2), math.cos(th / 2)]]
def m2(A, B): return [[sum(A[i][t] * B[t][j] for t in range(2)) for j in range(2)] for i in range(2)]
Mp, pers = [[1, 0], [0, 1]], None; powers_list = []
for n in range(1, 49):
    Mp = m2(Mp, Ux); powers_list.append(Mp)
    if pers is None and abs(Mp[0][0] - 1) < 1e-12 and abs(Mp[0][1]) < 1e-12 and abs(Mp[1][1] - 1) < 1e-12: pers = n
M12s = powers_list[11]
amp = [math.cos(math.radians(15) * t) for t in range(24)]
ok3, n3 = k3(amp)
row('S9 spin-1/2, 30 degrees per step', pers == 24, abs(M12s[0][0] + 1) < 1e-12 and abs(M12s[1][1] + 1) < 1e-12, ok3, False, 'NOT MET (step)', 'period %s; U^12 = -I; observable: %s' % (pers, n3))
# S10 ring of 24 sites
occ = [1.0 if t == 0 else 0.0 for t in range(24)]
ok3, n3 = k3(occ)
row('S10 24-site ring rotation', True, False, ok3, False, 'NOT MET', 'shift^12 is a rotation by 12 sites, not a negation; observable: %s' % n3)
# S11 SU(9)_1 modular T
h = [Fraction(a * (9 - a), 18) for a in range(9)]
ordT = next(n for n in range(1, 1000) if all((n * x).denominator == 1 for x in h))
half = [((ordT // 2) * x) % 1 for x in h] if ordT % 2 == 0 else None
null_lab = sum(1 for a in range(9) for b in range(9) if (h[a] + h[b]).denominator == 1)
tw = [math.cos(2 * math.pi * float(h[1]) * t) for t in range(24)]
ok3, n3 = k3(tw)
row('S11 SU(9)_1 twist T', ordT == 24, False, ok3, null_lab == 9, 'modulus 9 own', 'order of T = %d; spins at half order %s; null labels of the 81-anyon product %d; observable: %s' % (ordT, [str(x) for x in half] if half else None, null_lab, n3))
# S12 day cycle
d = [math.cos(2 * math.pi * t / 24) + 0.3 * math.cos(4 * math.pi * t / 24 + 1) for t in range(24)]
ok3, n3 = k3(d)
row('S12 day-cycle model, hourly', True, all(abs(d[(t + 12) % 24] + d[t]) < 1e-9 for t in range(24)), ok3, False, 'NOT MET', n3)

c = dict(rows)
calib = c['S0 family, mod 9'] and not any(v for k, v in c.items() if k.split()[0] in ('S%d' % i for i in range(2, 13)))
print('CALIBRATION: %s -- S0 %s; null systems passing C11: %s; S1 (reported): %s'
      % ('PASS' if calib else 'FAIL', 'PASS' if c['S0 family, mod 9'] else 'FAIL',
         [k for k, v in c.items() if v and k.split()[0] not in ('S0', 'S1')] or 'NONE', 'PASS' if c['S1 quantum cat map, N = 9'] else 'FAIL'))
