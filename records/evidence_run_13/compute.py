#!/usr/bin/env python3
"""Evidence run 13 -- quasicrystals, prediction first (standard library). Run: python3 compute.py"""
import itertools, math
from collections import Counter
def pisano(m):
    a, b, k = 0, 1, 0
    while True:
        a, b, k = b, (a + b) % m, k + 1
        if (a, b) == (0, 1): return k
nrm = lambda a, b: a*a + a*b - b*b                     # norm of a + b*tau, tau^2 = tau + 1 (Q(sqrt5) norm up to sign)
print("P1  STRUCTURALLY DEFINED ELEMENTS OF THE GOLDEN MODULE")
F = [0, 1]
while len(F) < 30: F.append(F[-1] + F[-2])
# tau^k = F(k-1) + F(k) tau ; approximant period vectors F(n+1) + F(n) tau = tau^(n+1)... check both
def mul(x, y):                                          # (a + b tau)(c + d tau)
    a, b = x; c, d = y
    return (a*c + b*d, a*d + b*c + b*d)
p = (1, 0); pw = []
for k in range(1, 25): p = mul(p, (0, 1)); pw.append(p)
print("  tau^k = F(k-1) + F(k) tau for k = 1..24:", all(pw[k-1] == (F[k-1], F[k]) for k in range(1, 25)))
apx = [(F[n], F[n+1]) for n in range(1, 24)]            # period: F(n) short + F(n+1) long tiles = F(n) + F(n+1) tau
print("  approximant period F(n) + F(n+1) tau (F(n) short and F(n+1) long tiles, long/short = tau) equals tau^(n+1):",
      all(apx[n-1] == pw[n] for n in range(1, 24)))
print("  norms of the inflation tau^k and of every approximant period:", sorted({abs(nrm(*x)) for x in pw + apx}), "-> units")
L, S = (0, 1), (1, 0)                                   # substitution L -> LS, S -> L: count long and short tiles
cnt = [(1, 0)]
for _ in range(23): l, s_ = cnt[-1]; cnt.append((l + s_, l))
print("  tile counts under L -> LS, S -> L: after n + 1 steps F(n+1) long and F(n) short tiles:",
      all(cnt[n] == (F[n+1], F[n]) for n in range(1, 23)))
print("  so the period of an approximant, short length 1 and long length tau, is F(n) + F(n+1) tau = tau^(n+1), a unit;")
print("  the expression with the counts exchanged, F(n+1) + F(n) tau, has norms", sorted({abs(nrm(F[n+1], F[n])) for n in range(1, 8)}),
      "... and is the period of no approximant")
print("  |Z[tau]/(x)| = |N(x)| = 1 for each: the golden module supplies no finite modulus")

print("\nP2  MEASURED INTEGERS")
M24 = [m for m in range(2, 101) if pisano(m) == 24]
base = len(M24) / 99
print("  integers m in 2..100 with pi(m) = 24:", M24, "| base rate %.3f" % base)
data = [  # (integer, source class, retrieved or inferred, symmetry-forced)
    (4,  'Tsai cluster, inner tetrahedron (retrieved)', False),
    (20, 'Tsai cluster, dodecahedron (retrieved)', True),
    (12, 'Tsai cluster, icosahedron (retrieved)', True),
    (30, 'Tsai cluster, icosidodecahedron (retrieved)', True),
    (44, 'Bergman cluster through the 3rd shell (retrieved)', False),
    (2,  'decagonal Al-Co-Cu / Al-Ni-Co, layers per 0.4 nm period (retrieved)', False),
    (6,  'decagonal Al-Mn-Pd, 1.2 nm period / 0.2 nm layers (INFERRED)', False),
    (8,  'decagonal Al-Fe-Pd, 1.6 nm period / 0.2 nm layers (INFERRED)', False)]
for m, src, forced in data:
    print("  %3d  pi = %3d  %-5s %s%s" % (m, pisano(m), 'YES' if pisano(m) == 24 else 'no', src, '  [symmetry-forced]' if forced else ''))
free = [m for m, s, f in data if not f]
hits = [m for m in free if pisano(m) == 24]
k, n = len(hits), len(free)
pval = sum(math.comb(n, i) * base**i * (1 - base)**(n - i) for i in range(k, n + 1))
print("  9 occurs: %s | non-forced integers %d, period-24 hits %d (%s) -> rate %.2f vs base %.3f | binomial P(>= %d hits) = %.2f"
      % (9 in [m for m, s, f in data], n, k, hits, k / n, base, k, pval))
print("  verdict at the 0.05 level:", "period-24 excess SIGNIFICANT" if pval < 0.05 else "period-24 rate at chance level", "| 9 does not occur")
print("  the only hit, m = 6, rests on an inferred layer count")
# cycle type of T on (Z/6)^2
seen, ct = set(), Counter()
for v in itertools.product(range(6), repeat=2):
    if v in seen: continue
    L, y = 0, v
    while y not in seen: seen.add(y); y = (y[1], (y[0] + y[1]) % 6); L += 1
    ct[L] += 1
print("  T modulo 6 on 36 states: cycle type %s (the family modulo 9: 24^3, 8, 1) -- period 24 without the family's structure" % dict(sorted(ct.items(), reverse=True)))
