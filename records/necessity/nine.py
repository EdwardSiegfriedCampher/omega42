#!/usr/bin/env python3
"""nine.py -- why the modulus is 9: the necessity of the nine, computed (Companion Part 130; D-010).

The law T(a, b) = (b, a + b) has matrix A = [[0, 1], [1, 1]], and A^n = [[F(n-1), F(n)], [F(n), F(n+1)]] over the integers.
Two properties the protocol already names fix the modulus: the cycle of 24 (Core Part 1) and the mirror twelve steps away
(IN-06; T^12 = -I). This script proves, for every modulus m >= 3:
  (1) A^12 = -I (mod m) exactly when m divides gcd(F(11) + 1, F(12), F(13) + 1) = gcd(90, 144, 234) = 18;
  (2) of the divisors 3, 6, 9 and 18, the law has period exactly 24 on 6, 9 and 18 (on 3 its period is 8, with A^4 = -I);
  (3) of 6, 9 and 18 only 9 is a power of one prime; 6 = 2 x 3 and 18 = 2 x 9 split by the Chinese remainder theorem into the
      law modulo 2 (period 3) beside the law modulo 3 (period 8) or 9 (period 24), so their 24 is lcm(3, 8) or lcm(3, 24),
      not a cycle of their own;
and it checks which of the other proposed conditions discriminate: the norm's change of sign holds for every modulus; the lift
of the period by the modulus holds for every prime power tested; x^2 - x - 1 is irreducible modulo many primes, not 3 alone.
Exact; standard library only.
"""
from math import gcd
def F(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def matpow(n, m):
    return [[F(n - 1) % m, F(n) % m], [F(n) % m, F(n + 1) % m]]
def period(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1): return k
def prime_power(m):
    p = next(d for d in range(2, m + 1) if m % d == 0)
    while m % p == 0: m //= p
    return m == 1
def census(m):
    seen, out = set(), {}
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            s, L = (a, b), 0
            while s not in seen: seen.add(s); s = (s[1], (s[0] + s[1]) % m); L += 1
            out[L] = out.get(L, 0) + 1
    return ' + '.join('%d x %d' % (v, k) for k, v in sorted(out.items(), reverse=True))
g = gcd(gcd(F(11) + 1, F(12)), F(13) + 1)
print('A^12 OVER THE INTEGERS: [[F(11), F(12)], [F(12), F(13)]] = [[%d, %d], [%d, %d]]' % (F(11), F(12), F(12), F(13)))
print('(1) A^12 = -I (mod m) iff m | gcd(F(11) + 1, F(12), F(13) + 1) = gcd(%d, %d, %d) = %d' % (F(11) + 1, F(12), F(13) + 1, g))
N = 2000
found = [m for m in range(3, N + 1) if matpow(12, m) == [[m - 1, 0], [0, m - 1]]]
print('    checked for every m from 3 to %d: the moduli are %s' % (N, found))
print('(2) periods: ' + ', '.join('m = %d: %d%s' % (m, period(m), ' (A^4 = -I)' if matpow(4, m) == [[m - 1, 0], [0, m - 1]] else '') for m in found))
full = [m for m in found if period(m) == 24]
print('    period exactly 24 with the mirror at 12: %s' % full)
print('(3) one prime: %s | 6 = 2 x 3, periods %d and %d, lcm 24 | 18 = 2 x 9, periods %d and %d, lcm 24' % ([m for m in full if prime_power(m)], period(2), period(3), period(2), period(9)))
print('    censuses: ' + ' | '.join('m = %d: %s' % (m, census(m)) for m in full))
print('THE NECESSITY OF THE NINE: 9 is the one modulus that is a power of a single prime and carries the law\'s cycle of 24 with its mirror at 12.')
print()
print('WHAT DOES NOT DISCRIMINATE:')
ok = all((b * b + b * (a + b) - (a + b) ** 2 + (a * a + a * b - b * b)) % m == 0 for m in range(2, 60) for a in range(m) for b in range(m))
print('  N(T(a, b)) = -N(a, b) for N = a^2 + ab - b^2: an identity over the integers, b^2 + b(a + b) - (a + b)^2 = -(a^2 + ab - b^2); checked for every m < 60: %s' % ok)
lift = all(period(p ** (k + 1)) == period(p ** k) * p for p in (2, 3, 5, 7) for k in range(1, 4 if p < 7 else 3))
print('  the period lifts by the prime at each power, pi(p^(k+1)) = p pi(p^k), for p = 2, 3, 5, 7 to the powers checked: %s' % lift)
irr = [p for p in range(2, 50) if all(p % d for d in range(2, p)) and all((x * x - x - 1) % p for x in range(p))]
print('  x^2 - x - 1 has no root modulo the primes %s, so irreducibility selects no single prime' % irr)
print('  the Construct\'s 27 domains are Domain Zero and 26 seeds, 18 horizontal and 8 diagonal (1 + 18 + 8), not three groups of nine')
print()
print('THE COMPLETE DERIVATION, FROM THE PREMISE\'S OWN NUMBERS:')
def gperiod(orders):
    from math import lcm
    return lcm(*[period(o) for o in orders])
print('  (4) the law T(a, b) = (b, a + b) uses only addition, so what matters is the additive group G of a coordinate. The 81 states of the')
print('      premise make |G| = 9, and there are two groups of order nine: Z/9 (cyclic) and Z/3 x Z/3. Every ring of order nine has one of them:')
print('      Z/9 has Z/9; Z/3 x Z/3, GF(9) and F3[x]/(x^2) have Z/3 x Z/3. Period of the law: on Z/9, %d; on Z/3 x Z/3, %d.' % (gperiod([9]), gperiod([3, 3])))
print('      So the premise\'s two numbers, 81 states and the cycle of 24, force G = Z/9. Nothing ternary and no "two levels" are assumed.')
print('  (5) without the count 81: T^12 = -I on G^2 needs 90g = 144g = 234g = 0, so the exponent of G divides 18; period 24 needs 9 to divide it')
print('      (exponent 3 gives period %d, exponent 2 gives %d); one world excludes 18 = 2 x 9, two laws side by side; so the exponent is 9, and the' % (period(3), period(2)))
print('      smallest such group is Z/9. The two levels of 9 = 3^2 are a consequence of the cycle of 24, not a premise.')
A8 = [[F(7), F(8)], [F(8), F(9)]]
B = [[(A8[0][0] - 1) // 3, A8[0][1] // 3], [A8[1][0] // 3, (A8[1][1] - 1) // 3]]
detB = (B[0][0] * B[1][1] - B[0][1] * B[1][0]) % 3
print('  (6) the tower, proved: A^8 = %s = I + 3B with B = %s, det B = %d mod 3, so B is invertible mod 3 and A^8 is not I mod 9;' % (A8, B, detB))
print('      for an odd prime this gives (I + 3B)^(3^j) = I + 3^(j+1) B_j with B_j invertible, so ord_{3^n}(A) = 8 x 3^(n-1) for every n.')
chk = all(period(3 ** n) == 8 * 3 ** (n - 1) for n in range(1, 8))
print('      checked for n = 1 to 7: %s. At depth k the modulus is 9^k = 3^(2k), so the period is 8 x 3^(2k-1) = 24 x 9^(k-1).' % chk)
print('      The depths are powers of the base 9 because a depth is one more base below (Core L-523); the odd powers 27, 243, ... are the')
print('      half-depths between them, and both sequences have one limit, the 3-adic integers, since each is cofinal in the other.')
bases = [b for b in range(2, 200) if (b - 1) in full]
print('  the digital root of base b is arithmetic modulo b - 1 (MATH-17); the bases whose digital root lands on %s are %s, and of them only base %d lands on a single prime' % (full, bases, [b for b in bases if prime_power(b - 1)][0]))
print()
print('THE GRAMMAR, READ OFF THE ARITHMETIC (Companion Part 133):')
M = sorted({(3 * k) % 9 for k in range(9)}); U = [u for u in range(1, 9) if u % 3]
cls = [sorted({v for v in range(9) if v % 3 == r}) for r in range(3)]
show = lambda S: '{' + ', '.join(str(x or 9) for x in S) + '}'
print('  (7) Z/9 is a local ring: its one maximal ideal is M = 3Z/9 = %s, the Crown, and Z/9 / M = Z/3, the three primary classes %s.' % (show(M), ', '.join(show(c) for c in cls)))
pw = lambda g: [pow(g, k, 9) for k in range(1, 7)]
print('  (8) the two worlds: the units U = %s, a cyclic group of order %d generated by 2 (%s) and by 5 (%s), the two primitive roots, the seeds of K2;' % (show(U), len(U), pw(2), pw(5)))
print('      and the ideal M, cyclic of order 3 under addition, generated by 3. %d + %d = 9. M328 steps each world by its generator: x2 below, +3 above.' % (len(U), len(M)))
print('  (9) the two levels: every value is v = d0 + 3 d1 with digits d0, d1 in {0, 1, 2}, so 3 x 3 = 9 addresses; the levels are coupled by the carry,')
print('      since 0 -> M -> Z/9 -> Z/3 -> 0 does not split: 1 has additive order %d, which a split product Z/3 x Z/3 would not allow (its exponent is 3).' % next(k for k in range(1, 10) if (k * 1) % 9 == 0))
voices = []
seen = set()
for a in range(9):
    for b in range(9):
        if (a, b) in seen: continue
        o, s = [], (a, b)
        while s not in seen: seen.add(s); o.append(s); s = (s[1], (s[0] + s[1]) % 9)
        if len(o) == 24: voices.append(sorted({(x * x + x * y - y * y) % 9 for x, y in o}))
cos = sorted(sorted({u, (-u) % 9}) for u in U)
cos = [c for i, c in enumerate(cos) if c not in cos[:i]]
print('  (10) the sign and the voices: -1 = T^12, the mirror; the units modulo their sign are U/{+1, -1} = %s, a cyclic group of order 3,' % cos)
print('       and the norms on the three 24-cycles are exactly these cosets: %s. The voices are U/{+1, -1}, as D-009 found by the action of the units.' % voices)
print('  (11) the depth: a depth is one more base digit below every place (Core L-523), and one base-9 digit is two 3-adic digits, so the depths are 9^k = 3^(2k).')
print('  Every element of the grammar -- three classes, the Crown, two worlds, two coupled levels, the sign, three voices, the depth -- is a part of Z/9.')
