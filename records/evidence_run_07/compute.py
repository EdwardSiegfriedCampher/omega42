#!/usr/bin/env python3
"""Evidence run 07 -- frozen manifestations (standard library only). Run: python3 compute.py"""
import itertools, math
N = 9
T = lambda s, m=N: (s[1], (s[0] + s[1]) % m)
def orbits(m):
    seen, out = set(), []
    for s in itertools.product(range(m), repeat=2):
        if s in seen: continue
        o = [s]; x = T(s, m)
        while x != s: o.append(x); x = T(x, m)
        seen |= set(o); out.append(o)
    return out
O9 = orbits(9); LONG = [o for o in O9 if len(o) == 24]

# ---------- F1: the static invariant ----------
def qf(r, p, q): return lambda s: (r * s[0] * s[0] + p * s[0] * s[1] + q * s[1] * s[1]) % N
golden = qf(1, 1, N - 1)
print("F1 the norm form a^2 + ab - b^2 modulo 9:")
for o in O9: print("F1   orbit from %s (length %2d): values %s" % (o[0], len(o), sorted({golden(s) for s in o})))
print("F1   T sends N to -N on all 81 states: %s" % all(golden(T(s)) == (-golden(s)) % N for s in itertools.product(range(N), repeat=2)))
passing = []
for r, p, q in itertools.product(range(1, N), range(N), range(N)):
    f = qf(r, p, q)
    sgn = [e for e in (1, N - 1) if all(f(T(s)) == (e * f(s)) % N for s in itertools.product(range(N), repeat=2))]
    if not sgn: continue
    vals = [frozenset(f(s) for s in o) for o in LONG]
    if all(a.isdisjoint(b) for a, b in itertools.combinations(vals, 2)): passing.append((r, p, q, sgn[0]))
print("F1 NULL: of %d quadratic forms r a^2 + p ab + q b^2 (r a unit or not, r = 1..8), %d are T-invariant up to sign and separate the three long orbits: %s"
      % (8 * 81, len(passing), passing))

# ---------- F2: the clock chain's ground states ----------
def ground_states(L):
    c = 0
    for s in itertools.product(range(N), repeat=2):
        x = s
        for _ in range(L): x = T(x)
        c += x == s
    return c
gs = {L: ground_states(L) for L in range(1, 73)}
pred = {L: (81 if L % 24 == 0 else 9 if L % 8 == 0 else 1) for L in range(1, 73)}
print("F2 ring ground-state counts for L = 1..72 match the frozen prediction (1; 9 if 8 | L; 81 if 24 | L): %s" % (gs == pred))
print("F2 residual entropy per ring, ln(count): L = 23 -> %.3f, L = 24 -> %.3f (ln 81), L = 16 -> %.3f (ln 9)" % (math.log(gs[23]), math.log(gs[24]), math.log(gs[16])))
def energy(conf, J=1.0):
    L = len(conf)
    return -J * sum(math.cos(2 * math.pi * (conf[(n + 2) % L] - conf[(n + 1) % L] - conf[n]) / N) for n in range(L))
canon = [o for o in LONG if (2, 5) in o][0]
ring = [s[0] for s in canon[canon.index((2, 5)):] + canon[:canon.index((2, 5))]]
print("F2 the canonical orbit laid on a 24-site ring has energy %.6f = -24 J (the minimum): %s" % (energy(ring), abs(energy(ring) + 24) < 1e-9))

# ---------- F3: close-packed stacking ----------
O3 = orbits(3)
nz = [o for o in O3 if len(o) > 1]
print("F3 Fibonacci orbits modulo 3: %s" % [[s[0] for s in o] for o in O3])
print("F3 (a) any nonzero orbit with all adjacent values distinct (a legal stacking of positions): %s"
      % any(all(o[i][0] != o[(i + 1) % len(o)][0] for i in range(len(o))) for o in nz))
print("F3 (b) any nonzero orbit avoiding 0 (layer differences are +-1, never 0): %s" % any(all(s[0] != 0 for s in o) for o in nz))
def stack_from_hc(hc, layers=72):
    """positions in Z/3 from a periodic h/c string: h = neighbors equal (p[n+1] = p[n-1]), c = all three distinct"""
    p = [0, 1]
    for n in range(1, layers):
        t = hc[n % len(hc)]
        p.append(p[n - 1] if t == 'h' else (3 - p[n] - p[n - 1]) % 3)
    return p
def period(seq):
    for P in range(1, len(seq) // 2):
        if all(seq[i] == seq[i + P] for i in range(len(seq) - P)): return P
fib2 = []
a, b = 0, 1
for _ in range(6): fib2.append(a); a, b = b, (a + b) % 2
print("F3 (c) Fibonacci modulo 2: %s (period 3)" % fib2)
for label, hc in [("h = 1, c = 0 -> 'chh'", 'chh'), ("h = 0, c = 1 -> 'hcc'", 'hcc'), ("reference 'c' (3C)", 'c'), ("reference 'h' (2H)", 'h'), ("reference 'hc' (4H)", 'hc')]:
    p = stack_from_hc(hc)
    print("F3     h/c sequence %-22s -> stacking period %2d layers, positions %s"
          % (label, period(p[2:]), ''.join('ABC'[x] for x in p[2:2 + period(p[2:])])))

# ---------- F4: the scale hierarchy ----------
F = [0, 1]
for _ in range(60): F.append(F[-1] + F[-2])
res = [x % 9 for x in F]
print("F4 Fibonacci tile counts modulo 9 repeat with period %d across inflation levels" % next(P for P in range(1, 40) if res[:20] == res[P:P + 20]))
phi = (1 + 5 ** 0.5) / 2
for size, nm in [(1e3, '1 micrometer'), (1e6, '1 mm'), (1e7, '1 cm')]:
    print("F4 inflation levels from 0.5 nm tiles to %s: %.1f" % (nm, math.log(size / 0.5) / math.log(phi)))
