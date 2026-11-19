#!/usr/bin/env python3
"""Evidence run 04 -- computations (standard library only). Run: python3 compute.py"""
import itertools, random

# ---------- quadratic rings Z[x]/(x^2 - t x + n) modulo m; element (a, b) = a + b x ----------
RINGS = {'Z[phi] (golden, the family)': (1, -1), 'Z[i] (square lattice)': (0, 1),
         'Z[omega] (hexagonal lattice)': (-1, 1), 'Z[sqrt-2] (control)': (0, 2)}
def mul(u, v, t, n, m):
    a, b = u; c, d = v                      # (a + bx)(c + dx) = ac + (ad + bc)x + bd x^2,  x^2 = t x - n
    return ((a*c - n*b*d) % m, (a*d + b*c + t*b*d) % m)
def elements(m): return list(itertools.product(range(m), repeat=2))
def units(t, n, m):
    E = elements(m); one = (1 % m, 0)
    return [u for u in E if any(mul(u, v, t, n, m) == one for v in E)]
def mult_order(u, t, n, m):
    one = (1 % m, 0); k, x = 1, u
    while x != one: x = mul(x, u, t, n, m); k += 1
    return k
def cycle_type_mult(g, t, n, m):
    seen, out = set(), []
    for v in elements(m):
        if v in seen: continue
        c, x = 0, v
        while True:
            seen.add(x); c += 1; x = mul(g, x, t, n, m)
            if x == v: break
        out.append(c)
    return sorted(out, reverse=True)

print("Q2 -- THE FAMILY'S RING, MODULO 9")
T = lambda s: (s[1], (s[0] + s[1]) % 9)
print("Q2 T on (Z/9)^2 equals multiplication by phi on Z[phi]/9, state (a,b) = a + b*phi:",
      all(T(s) == mul((0, 1), s, 1, -1, 9) for s in elements(9)))
for name, (t, n) in RINGS.items():
    U = units(t, n, 9)
    maxord = max(mult_order(u, t, n, 9) for u in U)
    roots = [y for y in elements(9) if (lambda y2: ((y2[0] - y[0] - 1) % 9, (y2[1] - y[1]) % 9))(mul(y, y, t, n, 9)) == (0, 0)]
    line = "Q2 %-30s units %2d | non-units %2d | largest unit order %2d | roots of x^2 - x - 1: %d" % (name, len(U), 81 - len(U), maxord, len(roots))
    if roots:
        a = roots[0]
        ct = cycle_type_mult(a, t, n, 9)
        # conjugacy to T: in the basis (1, a) multiplication by a is T exactly; check (1, a) is a basis of the ring
        basis_ok = len({((p + q * a[0]) % 9, (q * a[1]) % 9) for p in range(9) for q in range(9)}) == 81
        line += " | multiplication by a root %s: cycle type %s | {1, root} is a basis, so it is T in that basis: %s" % (a, ct, basis_ok)
    print(line)

print("Q3 -- SIX-STATE TORSION AND THE CROWN, MODULO 3")
def torsion_profile_Z9():
    units9 = [u for u in range(9) if u % 3]
    cyc = []; x = 1
    while True:
        cyc.append(x); x = (2 * x) % 9
        if x == 1: break
    perm = {v: (2 * v) % 9 for v in range(9)}
    seen, ct = set(), []
    for v in range(9):
        if v in seen: continue
        c, y = 0, v
        while True:
            seen.add(y); c += 1; y = perm[y]
            if y == v: break
        ct.append(c)
    return len(units9), cyc, sorted(ct, reverse=True), all((v * v) % 9 == 0 for v in (0, 3, 6))
nu, cyc, ct, sqz = torsion_profile_Z9()
print("Q3 Z/9: %d units, Torsion Loop under x2: %s | cycle type of x2 on all 9: %s | non-units {0,3,6} square to zero: %s" % (nu, cyc, ct, sqz))
for name, (t, n) in RINGS.items():
    U = units(t, n, 3); NU = [v for v in elements(3) if v not in U]
    orders = sorted(mult_order(u, t, n, 3) for u in U)
    cyclic = max(orders) == len(U)
    nil = all(mul(v, w, t, n, 3) == (0, 0) for v in NU for w in NU)
    ideal = all(((v[0] + w[0]) % 3, (v[1] + w[1]) % 3) in NU for v in NU for w in NU)
    res = "Q3 %-30s units %d, cyclic: %-5s | non-units %d, an ideal: %-5s with all products zero: %-5s" % (name, len(U), cyclic, len(NU), ideal, nil)
    if cyclic and len(U) == 6:
        g = next(u for u in U if mult_order(u, t, n, 3) == 6)
        res += " | a generator %s acts with cycle type %s" % (g, cycle_type_mult(g, t, n, 3))
    match = cyclic and len(U) == 6 and len(NU) == 3 and ideal and nil
    print(res + " | criterion met: %s" % match)
# the three non-units of Z[omega]/3 are the classes of the sublattice (1 - omega)Z[omega], the sqrt3 x sqrt3 sublattice
t, n = -1, 1
NU = [v for v in elements(3) if v not in units(t, n, 3)]
mults = sorted({mul((1, 2), v, t, n, 3) for v in elements(3)})        # (1 - omega) = (1, -1) = (1, 2) mod 3
print("Q3 Z[omega]/3: the non-units are exactly the multiples of 1 - omega (the sqrt3 x sqrt3 sublattice classes): %s" % (sorted(NU) == mults))

print("Q1 -- PEER CLAIM: EVERY ORDER-24 ELEMENT OF Co0 HAS g^12 = -I")
P23, INF = 23, 23
QR = sorted(set((x * x) % P23 for x in range(1, P23)))
rows = []
base = [1 if (i in QR or i == 0) else 0 for i in range(P23)]
for s in range(P23):
    v = [base[(i - s) % P23] for i in range(P23)]; rows.append(v + [sum(v) % 2])
rows.append([1] * 24)
basis = []
for r in rows:
    r = int(''.join(map(str, r)), 2)
    for b in basis: r = min(r, r ^ b)
    if r: basis.append(r)
words = [0]
for b in basis: words += [w ^ b for w in words]
WSET = set(words)
bits = lambda w: [(w >> (23 - i)) & 1 for i in range(24)]
frombits = lambda b: int(''.join(map(str, b)), 2)
def mobius(a, b, c, d):
    out = []
    for x in range(24):
        if x == INF: y = INF if c == 0 else (a * pow(c, -1, P23)) % P23
        else:
            den = (c * x + d) % P23; y = INF if den == 0 else ((a * x + b) * pow(den, -1, P23)) % P23
        out.append(y)
    return out
inv9 = pow(9, -1, P23); QRs = set(QR)
delta = [x if x in (0, INF) else ((x ** 3 * inv9) % P23 if x in QRs else (9 * x ** 3) % P23) for x in range(24)]
def pword(w, perm):
    b = bits(w); o = [0] * 24
    for i in range(24): o[perm[i]] = b[i]
    return frombits(o)
gens = [mobius(1, 1, 0, 1), mobius(0, 22, 1, 0), delta]          # x -> x+1, x -> -1/x, and Conway's delta
print("Q1 generators preserve the Golay code (x->x+1, x->-1/x, delta): %s" % all(pword(w, p) in WSET for p in gens for w in basis))
def compose(p, q): return [q[p[i]] for i in range(24)]            # first p, then q
def cycles(p):
    seen, out = set(), []
    for i in range(24):
        if i in seen: continue
        c, x = [], i
        while x not in seen: seen.add(x); c.append(x); x = p[x]
        out.append(c)
    return out
random.seed(12)
sigma = None
for _ in range(20000):
    p = list(range(24))
    for _ in range(random.randint(1, 12)): p = compose(p, random.choice(gens))
    if sorted(len(c) for c in cycles(p)) == [2, 4, 6, 12]: sigma = p; break
cyc = cycles(sigma)
print("Q1 element of M24 with cycle type %s found by a random walk on the generators; preserves the code: %s"
      % (sorted(len(c) for c in cyc), all(pword(w, sigma) in WSET for w in basis)))
g = sigma
def apply_s(x, sgn):
    y = [0] * 24
    for i in range(24): y[g[i]] = sgn[i] * x[i]
    return y
def power_s(x, k, sgn):
    for _ in range(k): x = apply_s(x, sgn)
    return x
e = list(range(1, 25)); found = None
for w in words:
    sgn = [(-1) ** bits(w)[i] for i in range(24)]
    o = next(k for k in range(1, 100) if power_s(e, k, sgn) == e)
    if o == 24 and power_s(e, 12, sgn) != [-v for v in e]: found = (w, sgn); break
eps, sgn = found
h12 = power_s(e, 12, sgn)
def apply(x): return apply_s(x, sgn)
print("Q1 with a Golay sign change of weight %d: order 24 | 12th power is -I: %s | the 12th power negates %d coordinates and fixes %d"
      % (bin(eps).count('1'), h12 == [-v for v in e], sum(1 for a, b in zip(h12, e) if a == -b), sum(1 for a, b in zip(h12, e) if a == b)))
def in_leech(x):
    m = x[0] % 2
    if any(v % 2 != m for v in x) or sum(x) % 8 != (4 * m) % 8: return False
    if m == 0: return frombits([1 if v % 4 == 2 else 0 for v in x]) in WSET
    return frombits([1 if v % 4 == 3 else 0 for v in x]) in WSET
random.seed(24)
def random_leech():
    m = random.randint(0, 1)
    while True:
        c = bits(random.choice(words)); x = [m + 2 * ci + 4 * random.randint(-2, 2) for ci in c]
        if sum(x) % 8 != (4 * m) % 8: x[0] += 4
        if in_leech(x): return x
sample = [random_leech() for _ in range(3000)]
print("Q1 it preserves the Leech lattice on 3000 sampled vectors: %s -> an element of order 24 in Co0 whose 12th power is an involution other than -I"
      % all(in_leech(apply(x)) for x in sample))
