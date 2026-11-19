#!/usr/bin/env python3
"""construct.py -- the arithmetic of the Construct, the Originator's first instrument, read through Omega42 (records/construct/; Companion Part 104).

Every line is computed from the two Construct descriptions (APE-236, APE-237): the Lower World pattern 2-4-8-7-5-1, the Higher
World pattern 3-6-9, the Golden Set, the 24-step cycle split 18 + 6, and the interval templates. EXACT where stated.
    python3 records/construct/construct.py      # diffed in CI
"""
Y = lambda b: 'YES' if b else 'NO'
def T(s): return (s[1], (s[0] + s[1]) % 9)
dr = lambda n: 9 if n % 9 == 0 else n % 9
print('I. THE LOWER WORLD IS THE UNIT GROUP OF Z/9, TURNED BY DOUBLING [EXACT]')
lw = [2, 4, 8, 7, 5, 1]
print('  2-4-8-7-5-1 = the powers 2^1 .. 2^6 mod 9: %s; 2 has order 6, so it generates all six units: %s' % (Y(lw == [pow(2, k, 9) for k in range(1, 7)]), Y(sorted(lw) == [1, 2, 4, 5, 7, 8])))
neg = [(-x) % 9 for x in lw]
print('  the Negative Lower World -2..-1 is %s: the same cycle rotated by 3 places, because -1 = 2^3 mod 9: %s' % (neg, Y(neg == lw[3:] + lw[:3] and pow(2, 3, 9) == 8)))
print('  the pattern is led by 2, the first number of the canonical seed (2, 5), and the seed\'s second number 5 = 2^5 is the inverse of 2: %s' % Y(pow(2, 5, 9) == 5 and 2 * 5 % 9 == 1))
print('II. THE HIGHER WORLD IS THE CROWN [EXACT]')
print('  3-6-9 are the multiples of 3, the nilpotent ideal 3Z/9 (Core MATH-12): 3^2 = 0 and 6^2 = 0 mod 9: %s' % Y(9 % 9 == 0 and 36 % 9 == 0))
print('III. THE GOLDEN SET [EXACT]')
gs = [6 * x for x in [1, 5, 7, 8, 4, 2]]
print('  six times each Lower World value: %s; sum %d, digital root %d; the six units sum to 27' % (gs, sum(gs), dr(sum(gs))))
print('  the Golden Set holds 48 and 6, and 48 - 6 = 42 is itself in the set: %s -- the derivation of 42 in Core MATH-13 (42 = 2 x 24 - 6) stands inside the Construct' % Y(48 in gs and 6 in gs and 42 in gs))
print('IV. THE 24-STEP CYCLE SPLIT 18 + 6 [EXACT]')
s, cyc = (2, 5), []
for _ in range(24): cyc.append(s[0] if s[0] else 9); s = T(s)
crown = [i for i, v in enumerate(cyc) if v in (3, 6, 9)]
print('  the canonical cycle %s' % cyc)
print('  18 of its 24 values are Lower World and 6 are Higher World: %s' % Y(len(crown) == 6))
print('  the six Higher World steps are P%s: spaced four apart (the Eye, the hexagon of Core MATH-11), not the last six steps 19 to 24' % ', P'.join(map(str, crown)))
print('  so the 18 + 6 split of the Construct is exact; its placement at k = 19 to 24 is corrected to every fourth step')
print('V. THE INTERVAL TEMPLATES [EXACT]')
print('  a template for interval h is T^h; reading one place forward by h is exact for every h, and T^24 = I, T^12 = -I:')
s = (2, 5)
for h in (1, 6, 8, 12, 16, 24):
    x = s
    for _ in range(h): x = T(x)
    print('    h = %2d: (2, 5) -> %s' % (h, x))
print('  these templates move a place of the family; they carry no information about any lottery draw, which a fair draw does not take from its past')
print('VI. THE COUNTS [EXACT]')
print('  27 domains x 26 nodes = %d (the 702 nodes); 27 = 3^3, the modulus at which the tower has 14 loops (Core MATH-44)' % (27 * 26))
print('VII. THE 18 + 6 SPLIT IS THE RECONSTRUCTION OF A TEMPLATE [EXACT; after APE-238]')
F = [0, 1]
while len(F) < 30: F.append(F[-1] + F[-2])
def T2(s, d):
    for _ in range(d): s = T(s)
    return s
print('  A^d = [[F(d-1), F(d)], [F(d), F(d+1)]] mod 9 for d = 1 .. 24, so x(n+d) = F(d-1) x(n) + F(d) x(n+1): %s'
      % Y(all(T2((a, b), d) == ((F[d - 1] * a + F[d] * b) % 9, (F[d] * a + F[d + 1] * b) % 9) for d in range(1, 25) for a in range(9) for b in range(9))))
amb = {}
for d in range(1, 25):
    seen = {}
    for a in range(9):
        for b in range(9): seen.setdefault((a, T2((a, b), d)[0]), []).append(b)
    amb[d] = max(len(v) for v in seen.values())
uniq = [d for d in amb if amb[d] == 1]; three = [d for d in amb if amb[d] == 3]; nine = [d for d in amb if amb[d] == 9]
print('  given the two values x(n) and x(n+d) of a template, the state is recovered uniquely at %d intervals, three ways at %s, nine ways at %s' % (len(uniq), three, nine))
print('  the %d intervals that do not recover it are the multiples of 4, where F(d) = 0 mod 3: %s -- the six steps of the Eye' % (len(three + nine), Y(sorted(three + nine) == [4, 8, 12, 16, 20, 24] and all(F[d] % 3 == 0 for d in three + nine))))
print('  so the Construct\'s 18 Lower World and 6 Higher World steps are exactly the 18 invertible and the 6 non-invertible templates: %s' % Y(len(uniq) == 18 and len(three + nine) == 6))
