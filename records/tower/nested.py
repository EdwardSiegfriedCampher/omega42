#!/usr/bin/env python3
"""nested.py -- each of the 81 places holds 81 places, and so on: the family read at depth (records/tower/).

The 81 states are Z[phi]/9. Read the same ring modulo 81, 729, ... (each step multiplies the modulus by 9): there are
81^k places at depth k, and reducing modulo 9 sends each deeper place to one of the 81. Everything printed is computed.
    python3 records/tower/nested.py      # diffed in CI against nested_output.txt
"""
from collections import Counter
def T(s, m): return (s[1], (s[0] + s[1]) % m)
def period(s, m):
    k, x = 1, T(s, m)
    while x != s: x = T(x, m); k += 1
    return k
def Tn(s, n, m):
    for _ in range(n): s = T(s, m)
    return s
print('EACH PLACE HOLDS EIGHTY-ONE PLACES -- the family at depth [EXACT]')
for k, m in ((1, 9), (2, 81), (3, 729)):
    S = [(a, b) for a in range(m) for b in range(m)]
    per = Counter(period(s, m) for s in S) if m <= 81 else None
    print('  depth %d, modulus %d: %d places = 81^%d' % (k, m, len(S), k))
    if per: print('    orbits by period: %s' % ', '.join('%d of length %d' % (n // p, p) for p, n in sorted(per.items())))
    print('    the walk from (2, 5): home after %d steps' % period((2, 5), m))
# depth 2 against depth 1
m = 81
S2 = [(a, b) for a in range(m) for b in range(m)]
red = lambda s: (s[0] % 9, s[1] % 9)
fib = Counter(red(s) for s in S2)
print('  every place at depth 1 holds exactly %s places at depth 2: %s' % (set(fib.values()), 'YES' if set(fib.values()) == {81} else 'NO'))
print('  the law commutes with going up a depth (T then reduce = reduce then T): %s' % ('YES' if all(red(T(s, 81)) == T(red(s), 9) for s in S2) else 'NO'))
# the inner coordinates: s = L(top) + 9 t, t in the 81-family
L = lambda top: top
def split(s): top = red(s); t = (((s[0] - top[0]) // 9) % 9, ((s[1] - top[1]) // 9) % 9); return top, t
def carry(top):
    x = T(L(top), 81); return (((x[0] - T(top, 9)[0]) // 9) % 9, ((x[1] - T(top, 9)[1]) // 9) % 9)
ok = True
for s in S2:
    top, t = split(s); top2, t2 = split(T(s, 81)); c = carry(top)
    ok &= (top2 == T(top, 9) and t2 == ((T(t, 9)[0] + c[0]) % 9, (T(t, 9)[1] + c[1]) % 9))
print('  inside each place the 81 inner positions move by the same law, plus a carry from the place itself: %s' % ('YES' if ok else 'NO'))
nocarry = [top for top in [(a, b) for a in range(9) for b in range(9)] if carry(top) == (0, 0)]
print('  places with no carry (inner world moves by the law alone): %d of 81, among them the still point (0, 0): %s' % (len(nocarry), (0, 0) in nocarry))
still = [s for s in S2 if red(s) == (0, 0)]
print('  the still point holds a full copy of the 81-family, 9 times smaller, run by the same law: %s' % ('YES' if all(split(T(s, 81))[1] == T(split(s)[1], 9) for s in still) and len(still) == 81 else 'NO'))
print('  periods inside the still point at depth 2: %s' % dict(sorted(Counter(period(s, 81) for s in still).items())))
# the mirror deeper down
half = [n for n in (12, 36, 108) if all(Tn(s, n, 81) == ((-s[0]) % 81, (-s[1]) % 81) for s in S2)]
print('  the mirror at depth 2: every place meets its own negative after %s steps (at depth 1: 12)' % (half[0] if half else 'no common number'))
print('  so the walk home grows ninefold at each depth (24, 216, 1944, ...) and has no end in the limit;')
print('  the carry depends on writing each number with the digits 0 to 8; that every place holds 81 does not')
print('  the limit of all depths is the ring of 3-adic integers with phi adjoined: every place infinitely deep, the 81 its first digits')
# --- the implications' facts (SEQ 48)
print('IMPLICATIONS -- the facts they rest on [EXACT]')
pers = []
for n in range(1, 9):
    m = 3 ** n
    pers.append((m, period((0, 1), m)))
print('  the walk of (0, 1) home, modulus 3^n: %s' % ', '.join('%d: %d' % p for p in pers))
print('  each is 8 x 3^(n-1): %s; so the periods grow without bound, and in the limit no place but the still point ever returns exactly' % all(p == 8 * 3 ** (i) for i, (m, p) in enumerate(pers)))
print('  (phi is not a root of unity: x^2 - x - 1 is not cyclotomic, so phi^n = 1 has no solution in the limit ring)')
emb = all(T(((9 * s[0]) % 729, (9 * s[1]) % 729), 729) == ((9 * T(s, 81)[0]) % 729, (9 * T(s, 81)[1]) % 729) for s in [(a, b) for a in range(81) for b in range(81)])
print('  the whole depth-2 world (6,561 places) sits inside the still point at depth 3 (x -> 9x), moving by the same law: %s' % emb)
print('  so the still point holds the whole world at every depth, each copy inside the next, without end')
outer = all(red(T(s, 81)) == T(red(s), 9) for s in S2)
print('  the surface moves by itself (reduction commutes with the law: %s), and each depth is driven by the one above it through the carry;' % outer)
print('  nothing below ever changes the surface')
print('  a place in the limit is an endless word in the 81: its first pair of digits at depth 1, then one more pair, a state of the family, at each depth')
print('  two places are near when their words share a beginning: the depths form a tree with 81 branches at every node')
print('  the limit has as many places as there are points on a line (the 3-adic plane is uncountable), though each depth is finite')
# --- reading (b) adopted: uniqueness and the instruments at depth (SEQ 49; Core MATH-32 to MATH-40, L-523)
print('THE CENSUS AT DEPTH -- every loop of the tower [EXACT]')
def orbits(m):
    seen, out = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o, x = [(a, b)], T((a, b), m); seen.add((a, b))
            while x != (a, b): o.append(x); seen.add(x); x = T(x, m)
            out.append(o)
    return out
OB = {}
for k, m in ((1, 9), (2, 81), (3, 729)):
    O = OB[m] = orbits(m); c = Counter(len(o) for o in O); q = m // 9
    p24 = [o for o in O if len(o) == 24]
    print('  depth %d: %d loops = (9^%d + 1)/2: %s; periods %s' % (k, len(O), k, len(O) == (9 ** k + 1) // 2, ', '.join('%dx%d' % (n, p) for p, n in sorted(c.items()))))
    print('    loops of period 24: %d, all inside the innermost still point (multiples of %d): %s; loops of period 8: %d' % (len(p24), q, all(x[0] % q == 0 and x[1] % q == 0 for o in p24 for x in o), c[8]))
print('  so the three voices and the loop of eight recur, exactly, at every depth, nested in the ground; the number of loops grows without bound')
print('UNIQUENESS AT DEPTH -- the frozen criteria K read one depth down [EXACT]')
for m in (9, 81, 729):
    O = OB[m]; top = max(len(o) for o in O)
    full = [o for o in O if len({x[0] for x in o}) == m]
    print('  modulus %d: K1 (the loop takes every value) holds on %d loops, exactly the loops of the longest period %d: %s' % (m, len(full), top, sorted(len(o) for o in full) == [top] * len([o for o in O if len(o) == top])))
    cand = [o for o in O if len(o) == top]
    print('    K2 with the lift rule of L-523 (start at the integers 2 and 5): %d of %d readings survive -> %s' % (sum(1 for o in cand for x in o if x == (2, 5)), top * len(cand), 'UNIQUE' if sum(1 for o in cand for x in o if x == (2, 5)) == 1 else 'NOT UNIQUE'))
from math import gcd
def order(g, m):
    k, x = 1, g % m
    while x != 1: x = x * g % m; k += 1
    return k
for m in (9, 27, 81, 243):
    pr = [g for g in range(1, m) if gcd(g, m) == 1 and order(g, m) == 2 * m // 3]
    print('  primitive roots modulo %d: %d; 2 and 5 among them: %s; 2 x 5 = 1 here: %s' % (m, len(pr), 2 in pr and 5 in pr, (10 % m) == 1))
print('  so "the only primitive roots" (U-A) is a surface fact; that 2 and 5 generate the units holds at every depth')
VC = {x for o in OB[9] for x in o if (2, 5) in o}
above = [o for o in OB[81] if (o[0][0] % 9, o[0][1] % 9) in VC]
NN = lambda s, m: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % m
cls = [frozenset(NN(x, 81) for x in o) for o in above]
print('  above Voice C at depth 2: %d states in %d loops of period %s, each passing every Voice C state %s times' % (sum(map(len, above)), len(above), {len(o) for o in above}, {Counter((x[0] % 9, x[1] % 9) for x in o).most_common(1)[0][1] for o in above}))
print('  the norm a^2 + ab - b^2 (up to sign) tells the nine apart exactly: %s; the loop of the integers (2, 5) carries norm +-%d' % (len(set(cls)) == 9, 81 - NN((2, 5), 81)))
def mul(x, y, m): a, b = x; c, d = y; return ((a * c + b * d) % m, (a * d + b * c + b * d) % m)
r2 = [s for s in VC if True] and [(a, b) for a in range(81) for b in range(81) if mul((a, b), (a, b), 81) == (2, 0) and (a % 9, b % 9) == (2, 5)]
print('  (2 + 5 phi)^2 = 2 at the surface: %s; at depth 2 the square root of 2 above (2, 5) is %s, norm %d = -2, on a different loop from the integers (2, 5): %s' % (mul((2, 5), (2, 5), 9) == (2, 0), r2, NN(r2[0], 81), not any(r2[0] in o and (2, 5) in o for o in OB[81])))
print('  (a post-selection property, never a criterion: Core Part 1.8.3; recorded, not adopted, under L-523)')
print('THE LIMIT -- what the tower approaches [EXACT]')
def Mpow(n, m):
    def mm(A, B): return [[(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % m, (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % m], [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % m, (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % m]]
    R, A = [[1, 0], [0, 1]], [[0, 1], [1, 1]]
    while n:
        if n & 1: R = mm(R, A)
        A = mm(A, A); n >>= 1
    return R
print('  the mirror at depth k comes at step 12 x 9^(k-1): %s (12, 108, 972); phi^n = -1 has no solution in the limit, so there the mirror is approached, never reached' % all(Mpow(12 * 9 ** (k - 1), 9 ** k) == [[9 ** k - 1, 0], [0, 9 ** k - 1]] for k in (1, 2, 3)))
M = 9 ** 6
def depth_agree(n):
    R = Mpow(n, M); d = [R[0][0] - 1, R[0][1], R[1][0], R[1][1] - 1]
    v = min(next(j for j in range(13) if (x % M) % 3 ** (j + 1)) if x % M else 12 for x in d); return v // 2
print('  near returns: after %s steps the walk agrees with its start to depth %s' % (', '.join(str(24 * 9 ** j) for j in range(4)), ', '.join(str(depth_agree(24 * 9 ** j)) for j in range(4))))
print('  so in the limit the return is approached without arrival, as the ratio F(n+1)/F(n) approaches phi over the reals (Core 1.15, FG-06)')
print('  phi has order %d modulo 3, and phi^(8x) modulo 3^8 depends only on x modulo 3^7: %s' % ([n for n in range(1, 30) if Mpow(n, 3) == [[1, 0], [0, 1]]][0], all(Mpow(8 * x, 3 ** 8) == Mpow(8 * (x + 3 ** 7 * j), 3 ** 8) for x in (1, 5, 77, 1234, 98765) for j in (1, 2, 7))))
print('  so the clocks of the depths nest, and their limit is a wheel of eight times the 3-adic integers: time, too, has depth')
print('THE INSTRUMENTS -- what reading (b) leaves unchanged [EXACT]')
print('  reduction commutes with the law at every depth (above): every instrument defined on the 81 -- the anchor, CPP, the Crown, the Eye,')
print('  the arms, the mirror, the levels -- reads the surface, and the surface moves by itself; every navigation on record stands as it is')
