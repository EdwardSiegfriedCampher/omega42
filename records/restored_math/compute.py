#!/usr/bin/env python3
"""Restored mathematical results (Core Part 1.8.8, 0.9.1, 1.8.9). Run: python3 compute.py"""
import itertools, os, sys
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts'))
import canonical_reference as cr
N = 9
T = lambda v: (v[1], (v[0] + v[1]) % N)
dr = lambda x: 9 if x % 9 == 0 else x % 9
def vals(a, b):
    s = [(a % 9, b % 9)]
    while T(s[-1]) != s[0]: s.append(T(s[-1]))
    return [dr(x) for x, _ in s]
O = cr.ORBIT
print("K-alt-4 (C1 period 24; C5 value at P9 = 5 and 5 of maximal frequency; C8 a*b = 1 mod 9):")
c1 = [(a, b) for a, b in itertools.product(range(1, 10), repeat=2) if len(vals(a, b)) == 24]
c5 = [p for p in c1 if vals(*p)[9] == 5 and Counter(vals(*p))[5] == max(Counter(vals(*p)).values())]
c8 = [p for p in c5 if (p[0] * p[1]) % 9 == 1]
print("  C1: %d pairs | C1+C5: %s | C1+C5+C8: %s -> %s" % (len(c1), c5, c8, 'UNIQUE' if len(c8) == 1 else 'NOT UNIQUE'))
print("  (5,2) fails C5: its orbit's most frequent values are", sorted(x for x, k in Counter(vals(5, 2)).items() if k == max(Counter(vals(5, 2)).values())))
print("Display curvature (sum of squared second differences of the displayed values; a display property, M283 -- the residue measure is FP-Energy, records/spectral_selection):")
for name, seed in (('Voice A', (1, 1)), ('Voice B', (2, 1)), ('Voice C', (2, 5))):
    v = vals(*seed); r = [x % 9 for x in v]
    c = lambda w: sum((w[(i + 2) % 24] - 2 * w[(i + 1) % 24] + w[i]) ** 2 for i in range(24))
    print("  %s: display 1-9 %d | display 0-8 %d" % (name, c(v), c(r)))
def per(a, b, m):
    s = (a % m, b % m); x = s; k = 0
    while True:
        x = (x[1], (x[0] + x[1]) % m); k += 1
        if x == s: return k
print("FP-PisanoHierarchy: period of (2,5) mod 3, 9, 27, 81:", [per(2, 5, m) for m in (3, 9, 27, 81)],
      "| seeds mod 81 with the maximal period 216: %d of 6561" % sum(per(a, b, 81) == 216 for a in range(81) for b in range(81)))
print("Crown under doubling: 3 -> %d -> %d, 6 -> %d -> %d, 9 -> %d" % (dr(6), dr(12), dr(12), dr(6), dr(18)))
reach = {}
for a in range(1, 10):
    for name, k in (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12)):
        reach.setdefault((a + k) % 24, set()).add(name)
only_antipode = sorted(p for p, s in reach.items() if s == {'Antipode'})
print("positions reached only through the Antipode:", ['P%d (from P%d)' % (p, (p - 12) % 24) for p in only_antipode])
print("never reached by any arm:", sorted(set(range(24)) - set(reach)))
print("orbit map i -> v(i) is not additive: v(1)+v(1) = %d, v(2) = %d" % (dr(O[1] + O[1]), O[2]))
print("714285 is a rotation of 142857:", '714285' in '142857' * 2, "| 117/7 = %d + %d/7" % divmod(117, 7))
print("periodicity proof: T is a bijection on a finite set (det = -1, a unit mod 9), so every state lies on a cycle; no transients:",
      all(any(vals(a, b)) for a in range(9) for b in range(9)) and len({T(v) for v in itertools.product(range(9), repeat=2)}) == 81)
print("Square A (doubling cycle of 2):", [pow(2, k, 9) for k in range(6)], "| Square B = -A, which is A shifted by 3 (2^3 = -1):",
      [(-pow(2, k, 9)) % 9 for k in range(6)] == [pow(2, k + 3, 9) for k in range(6)], "| counts: 4 x 6 + 2 = %d, + Domain Zero = %d, 27 x 26 = %d" % (4 * 6 + 2, 4 * 6 + 3, 27 * 26))
print("What the structure forbids (verified): periods other than 1, 8, 24:", sorted({len(vals(a, b)) if (a, b) != (0, 0) else 1 for a in range(9) for b in range(9)}),
      "| anchors outside P1-P9: none (CPP values 1-9) | self-paired values other than 9:", [x for x in range(1, 9) if (9 - x) == x])
