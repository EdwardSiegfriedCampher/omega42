#!/usr/bin/env python3
"""Evidence run 08 -- the operator (mod 9) and the manifestor (mod 8). Standard library only. Run: python3 compute.py"""
import itertools, math
from collections import Counter
def T(s, m): return (s[1], (s[0] + s[1]) % m)
def orbits(m):
    seen, out = set(), []
    for s in itertools.product(range(m), repeat=2):
        if s in seen: continue
        o = [s]; x = T(s, m)
        while x != s: o.append(x); x = T(x, m)
        seen |= set(o); out.append(o)
    return out
def pisano(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1): return k
def mpow(k, m):
    M = ((1 % m, 0), (0, 1 % m)); A = ((0, 1), (1, 1))
    for _ in range(k): M = tuple(tuple(sum(M[i][t] * A[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
    return M
norm = lambda s, m: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % m
def family_type(q):
    P = pisano(q); longs = [o for o in orbits(q) if len(o) == P]
    vals = [frozenset(norm(s, q) for s in o) for o in longs]
    return len(longs) >= 3 and all(a.isdisjoint(b) for a, b in itertools.combinations(vals, 2))

# G1
m = 72
print("G1 modulus 72: Pisano period %d | T^12 = %s | modulo 9: %s | modulo 8: %s"
      % (pisano(72), mpow(12, 72), mpow(12, 9), mpow(12, 8)))
o72 = Counter(len(o) for o in orbits(72))
print("G1 orbit sizes on the 5184 states modulo 72: %s" % dict(sorted(o72.items(), reverse=True)))
def orb(s, m):
    o = [s]; x = T(s, m)
    while x != s: o.append(x); x = T(x, m)
    return o
print("G1 the canonical seed (2, 5): period %d modulo 72, %d modulo 9, %d modulo 8" % (len(orb((2, 5), 72)), len(orb((2, 5), 9)), len(orb((2, 5), 8))))
hits = []
for p in range(2, 101):
    for q in range(2, 101):
        if p == q or p * q > 200 or math.gcd(p, q) != 1: continue
        Pp, Pq = pisano(p), pisano(q)
        if Pq % Pp: continue                                                  # (i)
        if Pq % 2: continue
        h = Pq // 2
        if mpow(h, q) != (((q - 1) % q, 0), (0, (q - 1) % q)) or mpow(h, p) != ((1, 0), (0, 1)): continue   # (ii)
        if not family_type(q): continue                                       # (iii)
        hits.append((p, q))
print("G1 NULL: coprime pairs (manifest p, operator q), p q <= 200, meeting all three criteria: %d -> %s" % (len(hits), hits))
crit12 = []
for p in range(2, 101):
    for q in range(2, 101):
        if p == q or p * q > 200 or math.gcd(p, q) != 1: continue
        Pp, Pq = pisano(p), pisano(q)
        if Pq % Pp or Pq % 2: continue
        h = Pq // 2
        if mpow(h, q) == (((q - 1) % q, 0), (0, (q - 1) % q)) and mpow(h, p) == ((1, 0), (0, 1)): crit12.append((p, q))
print("G1 NULL: pairs meeting criteria (i) and (ii) only: %d" % len(crit12))
print("G1 operator moduli q <= 100 of family type (iii): %s" % [q for q in range(2, 101) if family_type(q)])

# G2
o8 = Counter(len(o) for o in orbits(8))
print("G2 modulus 8: orbit sizes on 64 states %s | Pisano period %d | T^6 = %s (half-period negation: %s)"
      % (dict(sorted(o8.items(), reverse=True)), pisano(8), mpow(6, 8), mpow(6, 8) == ((7, 0), (0, 7))))
print("G2 norm values on the mod-8 orbits of length 12: %s" % [sorted({norm(s, 8) for s in o}) for o in orbits(8) if len(o) == 12])
print("G2 family type modulo 8: %s" % family_type(8))

# G3
F = [0, 1]
for _ in range(60): F.append(F[-1] + F[-2])
cls = [x % 8 for x in F]
per = next(P for P in range(1, 40) if cls[:24] == cls[P:P + 24])
triv = [n for n in range(1, 61) if F[n] % 8 == 0]
print("G3 Fibonacci stack: classes F(n) mod 8 = %s ... | period %d | classes visited %s"
      % (cls[:13], per, sorted(set(cls))))
print("G3 segments trivializable by interactions (8 | F(n)), n = 1..60: %s | exactly the multiples of 6: %s"
      % (triv, triv == [n for n in range(1, 61) if n % 6 == 0]))

# G4
def dsum(n, b):
    s = 0
    while n: s += n % b; n //= b
    return s
print("G4 base 10 digit sums agree with n mod 9 for n < 10^5: %s | base 9 digit sums agree with n mod 8: %s"
      % (all(dsum(n, 10) % 9 == n % 9 for n in range(1, 10 ** 5)), all(dsum(n, 9) % 8 == n % 8 for n in range(1, 10 ** 5))))

# G5
eight = [o for o in orbits(3) if len(o) == 8][0]
for o in [o for o in orbits(9) if len(o) == 24]:
    red = [(s[0] % 3, s[1] % 3) for s in o]
    cover = Counter(red)
    print("G5 long orbit from %s reduces mod 3 onto the eight-cycle: %s, each state covered %s times"
          % (o[0], set(red) == set(eight), sorted(set(cover.values()))))

# G1 (continued): why (8, 9) -- the half-period matrix over the integers
A12 = [[0, 1], [1, 1]]
M = [[1, 0], [0, 1]]
for _ in range(12): M = [[sum(M[i][t] * A12[t][j] for t in range(2)) for j in range(2)] for i in range(2)]
gp = math.gcd(math.gcd(M[0][0] - 1, M[0][1]), M[1][1] - 1)
gm = math.gcd(math.gcd(M[0][0] + 1, M[0][1]), M[1][1] + 1)
print("G1 over the integers T^12 = %s; the largest modulus with T^12 = +I is gcd(T^12 - I) = %d; the largest with T^12 = -I is gcd(T^12 + I) = %d"
      % (M, gp, gm))
print("G1 divisors of %d of family type: %s -> the manifest layer 8 and the operator layer 9 are fixed by the cycle's own half period"
      % (gm, [d for d in range(2, gm + 1) if gm % d == 0 and family_type(d)]))
