#!/usr/bin/env python3
"""Frequency, standing waves and the norm form (Core 1.8.9, Companion Part 43). Standard library only.
Every number printed is computed here."""
import cmath, math
from collections import Counter
N = 9
T = lambda s: (s[1], (s[0] + s[1]) % N)
Q = lambda a, b: a * a + a * b - b * b
phi = (1 + 5 ** 0.5) / 2

# canonical orbit and voices
def orbit(s):
    out, x = [], s
    while True:
        out.append(x); x = T(x)
        if x == s: return out
canon = orbit((2, 5)); vals = [a if a else 9 for a, b in canon]
print("canonical orbit:", vals)

# FP-NormForm
ints = [(a, b) for a in range(-20, 21) for b in range(-20, 21)]
print("FP-NormForm: Q(T(x)) = -Q(x) over the integers (|a|, |b| <= 20):", all(Q(b, a + b) == -Q(a, b) for a, b in ints))
print("  eigenvalues of T over the reals: %.6f and %.6f (phi and -1/phi)" % (phi, -1 / phi))
print("  null directions b/a = phi and -1/phi: Q vanishes on both:", abs(Q(1, phi)) < 1e-12 and abs(Q(1, -1 / phi)) < 1e-12)
print("  T^2 is a boost of Q with rapidity 2 ln phi = %.4f" % (2 * math.log(phi)))

# FP-NullLayer
states = [(a, b) for a in range(N) for b in range(N)]
z3 = sorted(s for s in states if Q(*s) % 3 == 0); z9 = sorted(s for s in states if Q(*s) % 9 == 0)
zero_layer = sorted(set(orbit((3, 3))) | {(0, 0)})
print("FP-NullLayer: states with Q = 0 mod 3: %d | Q = 0 mod 9: %d | both equal the eight-cycle and the still point: %s"
      % (len(z3), len(z9), z3 == z9 == zero_layer))
seen, voices = set(), []
for s in states:
    if s in seen: continue
    o = orbit(s); seen |= set(o)
    if len(o) == 24: voices.append(o)
for o in voices:
    vc = Counter(v for v, _ in o if v); dom = sorted(v for v, c in vc.items() if c == max(vc.values()))
    norms = sorted({Q(*x) % 9 for x in o})
    print("  voice with dominant values %s: norms %s; the law sends N to -N at every step: %s"
          % (dom, norms, all(Q(*T(x)) % 9 == (-Q(*x)) % 9 for x in o)))

# FP-OddHarmonics
c = [((v % 9) + 4) % 9 - 4 for v in vals]
X = [sum(c[n] * cmath.exp(-2j * math.pi * m * n / 24) for n in range(24)) for m in range(24)]
pw = {m: round(abs(X[m]) ** 2, 6) for m in range(13)}
print("FP-OddHarmonics: c(n+12) = -c(n):", all(c[(n + 12) % 24] == -c[n] for n in range(24)))
print("  power |X(m)|^2 for m = 0..12:", {m: int(round(p)) for m, p in pw.items()})
print("  even harmonics zero:", all(pw[m] < 1e-6 for m in range(0, 13, 2)),
      "| harmonics 3 and 9: %d each | 1, 5, 7, 11: %d each" % (round(pw[3]), round(pw[1])))
print("  total power %d = 24 * sum c^2 = %d" % (round(sum(abs(x) ** 2 for x in X)), 24 * sum(x * x for x in c)))
zph = [cmath.exp(2j * math.pi * v / 9) for v in vals]
print("  phase signal z(n+12) = conj z(n):", all(abs(zph[(n + 12) % 24] - zph[n].conjugate()) < 1e-12 for n in range(24)))
e8 = [((a % 9) + 4) % 9 - 4 for a, b in orbit((3, 3))]
print("  eight-cycle c(n+4) = -c(n):", all(e8[(n + 4) % 8] == -e8[n] for n in range(8)))

# FP-ModeSpectrum (classical)
lens = sorted(len(orbit(s)) for s in {min(orbit(s)) for s in states} for s in [s])
mult = Counter()
for L in lens:
    for j in range(L): mult[(24 // L) * j % 24] += 1
print("FP-ModeSpectrum: orbit lengths", lens, "| 81 modes, multiplicity by m:", dict(sorted(mult.items())))
print("  5 at m = 0, 4 at the other multiples of 3, 3 elsewhere:",
      all(mult[m] == (5 if m == 0 else 4 if m % 3 == 0 else 3) for m in range(24)), "| total", sum(mult.values()))

# quantum: Weil representation on C^9; V = U(T R) K implements T (R = diag(1, -1) is complex conjugation)
w = cmath.exp(2j * math.pi / N); inv2 = pow(2, -1, N)
def U(a, b, c_, d):
    bi = pow(b % N, -1, N)
    return [[w ** ((inv2 * bi * (a * k * k - 2 * j * k + d * j * j)) % N) / math.sqrt(N) for k in range(N)] for j in range(N)]
def mm(A, B): return [[sum(A[i][t] * B[t][j] for t in range(N)) for j in range(N)] for i in range(N)]
def conj(A): return [[x.conjugate() for x in r] for r in A]
def prop(A, B):
    i, j = max(((i, j) for i in range(N) for j in range(N)), key=lambda p: abs(B[p[0]][p[1]]))
    k = A[i][j] / B[i][j]
    return abs(abs(k) - 1) < 1e-9 and all(abs(A[x][y] - k * B[x][y]) < 1e-9 for x in range(N) for y in range(N))
UB = U(0, -1, 1, -1); V2 = mm(UB, conj(UB)); UT2 = U(1, 1, 1, 2)
I9 = [[1.0 * (i == j) for j in range(N)] for i in range(N)]; PAR = [[1.0 * ((i + j) % N == 0) for j in range(N)] for i in range(N)]
M = I9
for _ in range(6): M = mm(M, V2)
v12 = prop(M, PAR)
for _ in range(6): M = mm(M, V2)
v24 = prop(M, I9)
print("Quantum: V^2 = quantum cat map U(T^2) up to phase:", prop(V2, UT2), "| V^12 = parity up to phase:", v12, "| V^24 = identity up to phase:", v24)
P_ = I9; tr = []
for m in range(12): P_ = mm(P_, UT2); tr.append(sum(P_[i][i] for i in range(N)))
print("  U(T^2)^12 = identity:", all(abs(P_[i][j] - (i == j)) < 1e-9 for i in range(N) for j in range(N)))
nk = [round((sum(tr[m - 1] * cmath.exp(-2j * math.pi * k * m / 12) for m in range(1, 13)) / 12).real) for k in range(12)]
print("  stationary states: eigenvalues exp(2 pi i k / 12) for k =", [k for k in range(12) if nk[k]], "each once:", all(x in (0, 1) for x in nk) and sum(nk) == 9)


# ---------------------------------------------------------------- observables, travelling and standing waves
import random
random.seed(1)
neg = lambda s: ((-s[0]) % N, (-s[1]) % N)
f = {s: random.random() for s in states}
fo = {s: (f[s] - f[neg(s)]) / 2 for s in states}; fe = {s: (f[s] + f[neg(s)]) / 2 for s in states}
def harmonics(g, o):
    L = len(o); X = [sum(g[o[n]] * cmath.exp(-2j * math.pi * k * n / L) for n in range(L)) for k in range(L)]
    return [k * 24 // L for k in range(L) if abs(X[k]) > 1e-9]
odd_ok = all(m % 2 == 1 for s in states if len(orbit(s)) > 1 for m in harmonics(fo, orbit(s)))
even_ok = all(m % 2 == 0 for s in states if len(orbit(s)) > 1 for m in harmonics(fe, orbit(s)))
print("FP-ParityHarmonics: any observable = odd part (odd harmonics only) + even part (even harmonics only), since T^12 = -I:", odd_ok and even_ok)
real_m = Counter()
for L in lens:
    for j in range(L):
        m = (24 // L) * j % 24
        if m in (0, 12): real_m[m] += 1
print("FP-StandingModes: real eigenmodes of the forward law occur only at m = 0 (%d) and m = 12 (%d); every other real mode travels around its orbit" % (real_m[0], real_m[12]))
w1 = 2 * math.pi / 24; g0 = [math.cos(w1 * i) for i in range(24)]
fwd = lambda g: [g[(i + 1) % 24] for i in range(24)]; bwd = lambda g: [g[(i - 1) % 24] for i in range(24)]
prev = [x * math.cos(-w1) for x in g0]; cur = g0[:]; standing = True
for t in range(1, 49):
    nxt = [fwd(cur)[i] + bwd(cur)[i] - prev[i] for i in range(24)]
    standing &= all(abs(nxt[i] - math.cos(w1 * t) * g0[i]) < 1e-9 for i in range(24)); prev, cur = cur, nxt
print("  the law with its reverse (K + K^-1, second order in time) holds the profile cos(2 pi n/24) fixed with amplitude cos(2 pi t/24): %s; nodes at P6 and P18" % standing)
print("  the forward law alone moves that profile one step per step (a travelling wave):", fwd(g0) != g0)

# ---------------------------------------------------------------- the light cone closes modulo 3
def null_nonzero(p): return sum(1 for a in range(p) for b in range(p) if (a, b) != (0, 0) and Q(a, b) % p == 0)
print("FP-ClosedCone: nonzero null vectors of Q modulo 3: %d (5 is not a square mod 3); modulo 11: %d (5 is a square mod 11)" % (null_nonzero(3), null_nonzero(11)))
print("  modulo 9 the null states are exactly the nine with a, b in {0, 3, 6}:", z9 == sorted((a, b) for a in (0, 3, 6) for b in (0, 3, 6)))

# ---------------------------------------------------------------- discrimination baseline over moduli
def pisano(m):
    x, n = (1 % m, 1 % m), 1
    while x != (0, 1 % m): x = (x[1], (x[0] + x[1]) % m); n += 1
    return n
def halfneg(m):
    P = pisano(m)
    if P % 2: return False
    e1, e2 = (1, 0), (0, 1)
    for _ in range(P // 2): e1 = (e1[1], (e1[0] + e1[1]) % m); e2 = (e2[1], (e2[0] + e2[1]) % m)
    return e1 == ((-1) % m, 0) and e2 == (0, (-1) % m)
hn = [m for m in range(3, 200) if halfneg(m)]
p24 = [m for m in range(2, 200) if pisano(m) == 24]
print("Baseline: moduli 3 to 199 with half-period negation: %d of 197 | with period 24: %s | with both: %s" % (len(hn), p24, [m for m in p24 if m in hn]))

# ---------------------------------------------------------------- orbit identifier example (M291)
luc = orbit((2, 1)); lc = Counter(v for v, _ in luc if v)
print("M291 example: the Lucas numbers 2, 1, 3, 4, 7, ... modulo 9 run on the 24-orbit whose dominant values are", sorted(k for k, v in lc.items() if v == max(lc.values())), "(Voice B)")

print("Scale: periods 1, 8, 24 steps and frequency ratios m/24; no constant of the law carries a unit of time or length.")
