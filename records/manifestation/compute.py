"""records/manifestation/compute.py -- the seventh and its phases (Core 1.8.10, L-492; Companion Part 50). Standard library only."""
from fractions import Fraction
def digits(num, den, base=10, n=None):
    r = num % den; out = []; seen = {}
    while r not in seen:
        seen[r] = len(out); r *= base; out.append(r // den); r %= den
    return out
d1 = digits(1, 7); print('1/7 digits', d1)
rot = {}
for k in range(1, 7):
    dk = digits(k, 7)
    off = next(s for s in range(6) if d1[s:] + d1[:s] == dk); rot[k] = off
    print('%d/7' % k, ''.join(map(str, dk)), 'rotation by', off, '| 10^%d mod 7 = %d' % (off, pow(10, off, 7)))
d6 = digits(6, 7)
print('6/7 digitwise = 9 - (1/7):', d6 == [9 - x for x in d1], '| equals rotation by half period 3:', rot[6] == 3, '| 10^3 mod 7 =', pow(10, 3, 7), '= -1')
print('Midy pairs of 1/7:', sorted({tuple(sorted((d1[i], d1[i + 3]))) for i in range(3)}))
print('Crown digits {0,3,6,9} in 1/7:', [x for x in d1 if x % 3 == 0])
print('1/7 + 6/7 digitwise:', [a + b for a, b in zip(d1, d6)], '-> 0.999... = 1')
# Torsion loop
t = [1]; [t.append(t[-1] * 2 % 9) for _ in range(5)]; print('x2 mod 9 loop', t, '2^3 mod 9 =', pow(2, 3, 9), '= -1')
print('same set as digits of 1/7:', sorted(t) == sorted(d1))
print('the 1/7 half {1,2,4} and the 6/7 half {8,7,5} are the first and second halves of the Torsion Loop under doubling:', set(t[:3]) == {1, 2, 4} and set(t[3:]) == {8, 7, 5})
# Family
T = lambda s: (s[1], (s[0] + s[1]) % 9)
def orbit(s):
    o = [s]
    while True:
        s = T(s)
        if s == o[0]: return o
        o.append(s)
N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
seen = set(); orbs = []
for a in range(9):
    for b in range(9):
        if (a, b) not in seen:
            o = orbit((a, b)); seen |= set(o); orbs.append(o)
for o in sorted(orbs, key=len, reverse=True):
    tag = 'canonical (2,5)' if (2, 5) in o else ('Fibonacci (0,1)' if (0, 1) in o else ('Lucas (2,1)' if (2, 1) in o else ''))
    print('orbit len %2d %-16s norms %s' % (len(o), tag, sorted({N(s) for s in o})))
print('T negates the norm on all 81:', all(N(T(s)) == (-N(s)) % 9 for s in seen))
T2 = lambda s: T(T(s))
print('T^2 preserves the norm on all 81:', all(N(T2(s)) == N(s) for s in seen))
c = orbit((2, 5)); s = (2, 5); o2 = [s]
while True:
    s = T2(s)
    if s == (2, 5): break
    o2.append(s)
print('T^2 orbit of (2,5) has length', len(o2), '(canonical 24-orbit splits into two 12-cycles)')
s = (2, 5)
for _ in range(12): s = T(s)
print('T^12(2,5) =', s, '= -(2,5) mod 9:', s == ((-2) % 9, (-5) % 9))
print('det T = -1 (matrix [[0,1],[1,1]]), det T^2 = +1')
half = {1, 2, 4}
units = [s for s in seen if N(s) % 3]
print('T exchanges the 1/7 half {1,2,4} and the 6/7 half {8,7,5} of the norm on all 72 unit states:', all((N(s) in half) != (N(T(s)) in half) for s in units))
pos = []; s = (2, 5)
for _ in range(24): pos.append(s); s = T(s)
print('canonical positions: odd P carry norm 2 (1/7 half), even P norm 7 (6/7 half):', all(N(pos[i]) == (2 if i % 2 else 7) for i in range(24)))
print('Yang (+5) always in the opposite half; Yin (+18), 4D (+8), Antipode (+12) always in the same half:', all(N(pos[i]) != N(pos[(i + 5) % 24]) for i in range(24)) and all(N(pos[i]) == N(pos[(i + k) % 24]) for i in range(24) for k in (18, 8, 12)))
# null: primes with period-6 or even period in base 10: units-only digits and pairs = voice norm pairs
voice = {frozenset({1, 8}), frozenset({4, 5}), frozenset({2, 7})}
print('NULL: primes p < 1000 whose 1/p has period 6 in base 10:', [q for q in range(7, 1000) if all(q % k for k in range(2, int(q ** .5) + 1)) and len(digits(1, q)) == 6], '(999999 = 3^3 x 7 x 11 x 13 x 37)')
print('      1/13 digits', digits(1, 13), 'carry Crown digits; only 7 is Crown-free with the three voice pairs')
hits = []
for p in [q for q in range(7, 1000) if all(q % k for k in range(2, int(q ** .5) + 1))]:
    d = digits(1, p); L = len(d)
    if L % 2 == 0 and {frozenset({d[i], d[i + L // 2]}) for i in range(L // 2)} == voice: hits.append(p)
print('primes < 1000 whose 1/p carries exactly the three voice pairs, each, and nothing else:', hits)
print()
print('=== The ground that acts: exact facts behind the completed mechanism (Companion 50.16, 50.17) ===')
def zmul(u, v, m):                     # (a + b phi)(c + d phi) mod m, phi^2 = phi + 1
    a, b = u; c, d = v
    return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)
def zorder(u, m):
    x, n = u, 1
    while x != (1, 0): x = zmul(x, u, m); n += 1
    return n
F9 = [(a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0)]
print('FP-CoreField: Z[phi]/3 is a field (every nonzero element invertible):', all(any(zmul(s, t, 3) == (1, 0) for t in F9) for s in F9),
      '| phi has order', zorder((0, 1), 3), 'there, so one orbit runs through all 8 nonzero elements')
core9 = [(a, b) for a in (0, 3, 6) for b in (0, 3, 6)]
print('FP-CoreField: every core state squares to zero mod 9 (s*s = 0, nilpotence):', all(zmul(s, s, 9) == (0, 0) for s in core9),
      '| and the core is the field one scale down: the core states divided by 3 are Z[phi]/3, with T acting as T')
U9 = [(a, b) for a in range(9) for b in range(9) if (a * a + a * b - b * b) % 3]
orb = set(); x = (1, 0)
for _ in range(24): orb.add(x); x = zmul(x, (0, 1), 9)
cos = {frozenset(zmul(u, p, 9) for p in orb) for u in U9}
print('FP-VoiceCosets: the 72 units form a group; the orbit of the law has', len(orb), 'elements; its cosets:', len(cos),
      '= the three voices, with norm pairs', sorted(sorted({N(s) for s in c}) for c in cos))
dbl = lambda s: ((2 * s[0]) % 9, (2 * s[1]) % 9)
vc = lambda s: next(i for i, c in enumerate(sorted(cos, key=lambda c: min(N(t) for t in c))) if s in c)
print('FP-VoiceCosets: doubling moves every unit to the next voice:', all(vc(dbl(s)) != vc(s) for s in U9),
      '| three doublings return to the same voice as its negative (2^3 = 8 = -1, and -1 lies in the law\'s orbit):', (8, 0) in orb)
print('FP-TowerPeriods: the order of phi mod 3, 9, 27, 81 is', [zorder((0, 1), m) for m in (3, 9, 27, 81)], '-- tripling at each scale (3 is inert in Z[phi])')
import math
ph = (1 + 5 ** 0.5) / 2
print('FP-GlideMirror: in the eigenbasis T = diag(phi, -1/phi) = reflection diag(1, -1) times dilation diag(phi, 1/phi); det of the dilation = %.6f, of T = -1' % (ph * (1 / ph)))
Ti = lambda s: ((s[1] - s[0]) % 9, s[0])
print('FP-GlideMirror: T is invertible on all 81 states (T^-1 (a, b) = (b - a, a)), so the present state fixes the past:',
      all(Ti(T(s)) == s for s in [(a, b) for a in range(9) for b in range(9)]),
      )
cs = [2, 5]
while len(cs) < 24: cs.append((cs[-1] + cs[-2]) % 9)
rv = cs[::-1]
print('FP-GlideMirror: the law is chiral -- the reversed canonical sequence obeys g(t+1) = g(t-1) - g(t):',
      all(rv[(i + 1) % 24] == (rv[i - 1] - rv[i]) % 9 for i in range(24)),
      '| and not the forward rule g(t+1) = g(t) + g(t-1):', not all(rv[(i + 1) % 24] == (rv[i] + rv[i - 1]) % 9 for i in range(24)))
print()
print('=== The halves across the tower (FP-TowerHalves; Companion 50.18, 52.4) ===')
# A state s mod m has a lift (a, b) of norm n exactly when s lies in the orbit, mod m, of an element of norm n under
# the norm-keeping units -1 and phi^2. The minimal lift is the least |n| reached; its sign is the half at that scale.
def _isnorm(n):
    n = abs(n)
    if n == 0: return True
    p = 2
    while p * p <= n:
        e = 0
        while n % p == 0: n //= p; e += 1
        if p % 5 in (2, 3) and e % 2: return False
        p += 1
    return not (n > 1 and n % 5 in (2, 3))
def tower_halves(m):
    Nr_ = lambda a, b: a * a + a * b - b * b
    units = [(a, b) for a in range(m) for b in range(m) if Nr_(a, b) % 3]
    left, sign = set(units), {}
    for n in sorted((n for n in range(-40 * m, 40 * m + 1) if n % 3 and _isnorm(n)), key=lambda n: (abs(n), -n)):
        if not left: break
        K = int(3 * abs(n) ** 0.5) + 6; orbit = set()
        for x in [(a, b) for a in range(-K, K + 1) for b in range(-K, K + 1) if Nr_(a, b) == n]:
            y = (x[0] % m, x[1] % m)
            for _ in range(24 * m):
                orbit.add(y); orbit.add(((-y[0]) % m, (-y[1]) % m)); y = zmul(y, (1, 1), m)
        for s in [s for s in left if s in orbit]: sign[s] = n; left.discard(s)
    Tm_ = lambda s: (s[1], (s[0] + s[1]) % m)
    return dict(units=len(units), covered=not left, positive=sum(sign[s] > 0 for s in units),
                function=all(len({sign[s] > 0 for s in units if Nr_(*s) % m == r}) == 1 for r in range(m) if r % 3),
                exchange=all((sign[Tm_(s)] > 0) != (sign[s] > 0) for s in units),
                keep=all((sign[Tm_(Tm_(s))] > 0) == (sign[s] > 0) for s in units),
                agree9=sum(((Nr_(*s) % 9) in (1, 2, 4)) == (sign[s] > 0) for s in units), least=sorted({abs(v) for v in sign.values()}))
for m in (9, 27, 81):
    h = tower_halves(m)
    print('mod %d: %d units, every one reached: %s | positive half: %d | the half a function of the norm mod %d: %s | T exchanges: %s, T^2 keeps: %s'
          % (m, h['units'], h['covered'], h['positive'], m, h['function'], h['exchange'], h['keep']))
    print('        agrees with the mod-9 half of its reduction: %d of %d | least |N| values: %s' % (h['agree9'], h['units'], h['least']))
print('FP-TowerHalves: at every scale the minimal-lift rule divides the units into two equal halves, exchanged by T and kept by T^2;')
print('  modulo 9 they are the seventh and the manifest of 1/7 and 6/7 (72 of 72); modulo 27 and 81 they are not the lifts of those halves')
print('  (agreement near one half): each scale draws its own seventh, and the halves do not nest as the core does')

# ---- FP-ArmNorm (Core Part 1.8.10; Companion 62.5, E01) ----------------------------------------------------------
def _Tk(s, k):
    for _ in range(k % 24): s = (s[1], (s[0] + s[1]) % 9)
    return s
_states = [(a, b) for a in range(9) for b in range(9)]
_fail = [s for s in _states if (s[0] * _Tk(s, 12)[0] - _Tk(s, 18)[0] ** 2) % 9 != (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9]
_F = [0, 1]
while len(_F) < 19: _F.append(_F[-1] + _F[-2])
print('FP-ArmNorm: Anchor x Antipode - Yin^2 = N(the state at the anchor) mod 9 on %d of 81 states; F(18) = %d = %d mod 9 (Catalan at r = 18)'
      % (81 - len(_fail), _F[18], _F[18] % 9))
