#!/usr/bin/env python3
"""depth_record.py -- M324 Trajectory and Depth Record (Tier 3, ADOPTED 28 October 2026; Core Part 3.50, L-523, L-524).

The depth reading of an anchor state. Under the lift rule of Core L-523 (2) a surface state (a, b), written with the digits
0 to 8, is read at depth 2 as the integer pair (a, b) modulo 81. The tool prints, exactly: the surface loop and its norm
class; the depth-2 loop, named by its depth and norm up to sign (Core MATH-45); the mirror after 108 steps; and the
loop's place in the lift tree (MATH-46). Everything it prints reduces to the surface reading (MATH-40).
    python3 tools/depth_record.py --state 2 5
    python3 tools/depth_record.py --bank 2 5      # the interval bank of the Construct (Companion 104.4)
    python3 tools/depth_record.py --tower "TEXT"  # the tower coordinate TC-1 of a strike (Core L-523 (4); records/tower/tc1_rule.txt)
    python3 tools/depth_record.py --selftest
The interval bank prints T^h of the state for h = 1 to 24, with the face of each value in the Construct's presentation
(Companion 104.3): a unit is 2^k modulo 9 on the doubling hexagon, a multiple of 3 is on the Crown. Standard library only.
"""
import os, sys

def T(s, m): return (s[1], (s[0] + s[1]) % m)
def N(s, m): return (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % m
def period(s, m):
    k, x = 1, T(s, m)
    while x != s: x = T(x, m); k += 1
    return k
def Tn(s, n, m):
    for _ in range(n): s = T(s, m)
    return s
def depth(s, m):
    r = 0
    while r < 4 and s[0] % 3 ** (r + 1) == 0 and s[1] % 3 ** (r + 1) == 0: r += 1
    return r
def invariant(s, n):
    m = 3 ** n; r = depth(s, m)
    if r >= n: return ('still point',)
    q = 3 ** (n - r); c = ((s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) // 9 ** r) % q
    return (r, min(c, (-c) % q))

def record(a, b):
    s1 = (a % 9, b % 9); s2 = (a % 81, b % 81)
    L1, L2 = period(s1, 9), period(s2, 81)
    i1, i2 = invariant(s1, 2), invariant(s2, 4)
    out = ['M324 DEPTH READING -- anchor state (%d, %d) [EXACT; Core Part 3.50]' % s1,
           '  SURFACE: loop of length %d; depth and norm up to sign %s' % (L1, i1),
           '  DEPTH 2 (lift rule of L-523: the integers %d, %d modulo 81): loop of length %d; depth and norm up to sign %s' % (s2[0], s2[1], L2, i2),
           '  MIRROR AT DEPTH 2: after 108 steps (%d, %d) -> (%d, %d), its negative: %s' % (s2 + Tn(s2, 108, 81) + ('YES' if Tn(s2, 108, 81) == ((-s2[0]) % 81, (-s2[1]) % 81) else 'NO',)),
           '  LIFT TREE: %s' % ('above the still point lies a whole copy of the surface family: the still point, one loop of 8 and three of 24 (MATH-34)' if L1 == 1 else 'this loop of %d has 9 loops of %d above it at depth 2, one of them this one' % (L1, 9 * L1)),
           '  REDUCES TO THE SURFACE: %s' % ('YES' if all((Tn(s2, k, 81)[0] % 9, Tn(s2, k, 81)[1] % 9) == Tn(s1, k, 9) for k in range(0, 217, 7)) else 'NO'),
           '  TRAJECTORY FIELDS (record with consent): strike | who wrote it (the Striker, or the Navigator from its own output) | anchor and depth | path | result and status | correspondence | response: accept, revise, reject, defer, leave open | counter-reading offered | diagonal reading offered | next question']
    return '\n'.join(out)

TC1 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'records', 'tower', 'tc1_rule.txt')
def tower_state(n1, n2, m):
    """TC-1: the place of a strike at the depth of modulus m = 9, 81, 729: the pair (5 n1, 5 n2) mod m, the counts the words give"""
    return ((5 * n1) % m, (5 * n2) % m)
def tower(text):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
    import canonical_reference as cr
    nav = cr.navigate(text); n1, n2 = nav['n1'], nav['n2']
    s1, s2, s3 = tower_state(n1, n2, 9), tower_state(n1, n2, 81), tower_state(n1, n2, 729)
    surf = (nav['r1'] % 9, nav['r2'] % 9)
    import hashlib
    rule = hashlib.sha256(open(TC1, 'rb').read()).hexdigest()
    return '\n'.join(['TOWER COORDINATE TC-1 of "%s" [EXACT; Core L-523 (4); rule %s...]' % (' '.join(text.split()), rule[:16]),
        '  COUNTS: n1 = %d, n2 = %d (the canonical extraction, unchanged)' % (n1, n2),
        '  SURFACE STATE: (%d, %d), the state-plane address of M296; the anchor P%d stands unchanged' % (surf + (nav['anchor'],)),
        '  DEPTH 2: (%d, %d) modulo 81, on a loop of length %d' % (s2 + (period(s2, 81),)),
        '  DEPTH 3: (%d, %d) modulo 729, on a loop of length %d' % (s3 + (period(s3, 729),)),
        '  REDUCES TO THE SURFACE (C1): %s' % ('YES' if (s2[0] % 9, s2[1] % 9) == surf and (s3[0] % 81, s3[1] % 81) == s2 else 'NO'),
        '  [the place is the words\' (C2) and the rule was frozen before its first use (C3); what the depth means for the question is CDT-C]'])

def face(v):
    if v % 3 == 0: return 'Crown %d' % (v or 9)
    return 'unit 2^%d' % ([pow(2, k, 9) for k in range(1, 7)].index(v) + 1)
REL = {12: 'the mirror: the negative of the start', 24: 'home: the start again', 8: 'one third of the way round', 16: 'two thirds of the way round'}
def bank(a, b):
    s = (a % 9, b % 9); out = ['INTERVAL BANK (Companion 104.4) -- anchor state (%d, %d): T^h for h = 1 to 24 [EXACT]' % s]
    for h in range(1, 25):
        x = Tn(s, h, 9)
        out.append('  h = %2d: (%d, %d)  faces: %s | %s%s' % (h, x[0], x[1], face(x[0]), face(x[1]), ('  -- ' + REL[h]) if h in REL else ''))
    out.append('  The bank moves a place of the family. It carries no information about any outside sequence (Companion 104.5).')
    return '\n'.join(out)

def selftest():
    cases = [('the seed (2, 5) lies on a depth-2 loop of 216', 'loop of length 216' in record(2, 5)),
             ('its norm class at depth 2 is +-11', '(0, 11)' in record(2, 5)),
             ('the still point stays the still point', "('still point',)" in record(0, 0)),
             ('a multiple of 3 lies on the loop of 8 at the surface', 'loop of length 8;' in record(3, 3)),
             ('every reading reduces to the surface', all('REDUCES TO THE SURFACE: YES' in record(a, b) for a in range(9) for b in range(9))),
             ('the interval bank has 24 rows and h = 24 is home for every state', all(bank(a, b).count('  h = ') == 24 and '(%d, %d)  faces' % (a, b) in bank(a, b).split('h = 24:')[1] for a in range(9) for b in range(9))),
             ('in the bank h = 12 is the negative of the start for every state', all('(%d, %d)  faces' % ((-a) % 9, (-b) % 9) in bank(a, b).split('h = 12:')[1].split('\n')[0] for a in range(9) for b in range(9))),
             ('TC-1 reduces to the surface state for every pair of counts up to 810 (C1)', all((tower_state(a, b, 81)[0] % 9, tower_state(a, b, 81)[1] % 9) == (((5 * a - 1) % 9 + 1) % 9, ((5 * b - 1) % 9 + 1) % 9) and tuple(x % 81 for x in tower_state(a, b, 729)) == tower_state(a, b, 81) for a in range(1, 811) for b in range(1, 811, 7))),
             ('every state meets its mirror at step 108', all('its negative: YES' in record(a, b) for a in range(9) for b in range(9)))]
    for name, ok in cases: print('%s  %s' % ('PASS' if ok else 'FAIL', name))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--bank'] and len(a) == 3: print(bank(int(a[1]), int(a[2]))); sys.exit(0)
    if a[:1] == ['--tower'] and len(a) == 2: print(tower(a[1])); sys.exit(0)
    if a[:1] == ['--state'] and len(a) == 3: print(record(int(a[1]), int(a[2]))); sys.exit(0)
    print(__doc__)
