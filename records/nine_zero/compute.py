#!/usr/bin/env python3
"""Nine and zero (Companion Part 39): every arithmetic statement of the Part, recomputed. Run: python3 compute.py"""
import itertools, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import canonical_reference as cr
N = 9
T = lambda v: (v[1], (v[0] + v[1]) % N)
nrm = lambda a, b: (a*a + a*b - b*b) % N
dr = lambda n: 1 + (n - 1) % 9 if n > 0 else 0
print("39.1 dr(n+9) = dr(n), n = 1..10000:", all(dr(n + 9) == dr(n) for n in range(1, 10001)),
      "| dr(9n) = 9:", all(dr(9 * n) == 9 for n in range(1, 10001)),
      "| n = digit sum mod 9:", all(n % 9 == sum(map(int, str(n))) % 9 for n in range(10001)))
seen, orbits = set(), []
for v in itertools.product(range(N), repeat=2):
    if v in seen: continue
    o = [v]; y = T(v)
    while y != v: o.append(y); y = T(y)
    seen |= set(o); orbits.append(o)
print("39.2 orbits: length | norms | steps with value 0 | seeds (0, x)")
for o in sorted(orbits, key=len, reverse=True):
    print("     %2d | %-6s | %-7s | %s" % (len(o), sorted({nrm(*s) for s in o}), [i for i, s in enumerate(o) if s[0] == 0], [s for s in o if s[0] == 0]))
print("     the nine seeds (0, x) generate all 81 states:", len(set().union(*[set(o) for o in orbits if any(s[0] == 0 for s in o)])) == 81)
F = [0, 1]
while len(F) < 30: F.append(F[-1] + F[-2])
O = cr.ORBIT; val = [x % 9 for x in O]
for i in [i for i, x in enumerate(val) if x == 0]:
    k = val[(i + 1) % 24]
    print("     canonical zero at P%d (%s): the next 12 values are %d x F(n) mod 9: %s" % (i, cr.POSITION_NAMES[i], k, [val[(i + j) % 24] for j in range(12)] == [(k * F[j]) % 9 for j in range(12)]))
canon = [(2, 5)]
while T(canon[-1]) != (2, 5): canon.append(T(canon[-1]))
print("     canonical states with a zero coordinate:", [s for s in canon if 0 in s], "| (0,0) on a 24-cycle:", any((0, 0) in o for o in orbits if len(o) == 24))
print("     (0,0) is fixed:", T((0, 0)) == (0, 0), "| T(5,0) =", T((5, 0)))
def mul(x, y): a, b = x; c, d = y; return ((a*c + b*d) % N, (a*d + b*c + b*d) % N)
core = [v for v in itertools.product(range(N), repeat=2) if nrm(*v) == 0]
sq0 = [v for v in itertools.product(range(N), repeat=2) if mul(v, v) == (0, 0)]
print("39.3 norm-0 states = states whose square is 0 in Z[phi]/9:", sorted(core) == sorted(sq0), "(%d)" % len(core),
      "| 3^2, 6^2, 9^2 mod 9:", [(x * x) % 9 for x in (3, 6, 9)], "| u*9 mod 9 for units:", {(u * 9) % 9 for u in (1, 2, 4, 5, 7, 8)})
print("     antipodal pairs with equal values:", [(i, i + 12) for i in range(12) if O[i] == O[i + 12]],
      "| orbit sum (display 1-9) %d, (display 0-8) %d, both = 0 mod 9: %s" % (sum(O), sum(val), sum(O) % 9 == sum(val) % 9 == 0))
cpp = lambda v: dr(5 * v)
cyc = []
for v in range(1, 10):
    o = [v]; y = cpp(v)
    while y != v: o.append(y); y = cpp(y)
    if set(o) not in [set(c) for c in cyc]: cyc.append(o)
print("     CPP(v) = dr(5v) on 1..9, cycles:", cyc)
print("39.4 antipodal sums: display 1-9 %s, display 0-8 %s; = 0 mod 9 in both: %s" % (
      sorted({O[i] + O[i + 12] for i in range(12)}), sorted({val[i] + val[i + 12] for i in range(12)}),
      all((O[i] + O[i + 12]) % 9 == 0 == (val[i] + val[i + 12]) % 9 for i in range(12))))
r = cr.navigate('')
print("39.5 the empty domain: n = (%d, %d, %d), anchor P%d (%s); arms Yang P%d, Yin P%d, 4D P%d, Antipode P%d" % (
      r['n1'], r['n2'], r['n3'], r['anchor'], cr.POSITION_NAMES[r['anchor']], r['yang_i'], r['yin_i'], r['fourd_i'], r['antipode_i']))
z = [0, 1]
for _ in range(200): z.append(z[-1] + z[-2])
print("39.8 over the integers the recurrence from (0, 1) never returns to a state (first 200 steps):", len({(z[i], z[i + 1]) for i in range(200)}) == 200)
print("39.2 fixed points of T on the 81 states:", [v for v in itertools.product(range(N), repeat=2) if T(v) == v])
print("39.3 1/7 = 0.%s... ; its repeating digits are the units of Z/9Z: %s" % (str(10**6 // 7), sorted(set(int(c) for c in str(10**6 // 7))) == [1, 2, 4, 5, 7, 8]))
print("39.5 dr(5n) over one period takes the values", sorted({dr(5 * n) for n in range(1, 10)}), "| dr(6n) takes", sorted({dr(6 * n) for n in range(1, 10)}))
print("     counts differing by 9 share the value: dr(5n) = dr(5(n + 9)) for n = 1..1000:", all(dr(5 * n) == dr(5 * (n + 9)) for n in range(1, 1001)))
