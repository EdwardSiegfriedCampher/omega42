#!/usr/bin/env python3
"""esoteric.py -- the esoteric traditions read against the law (Companion Part 180; M218, M267, M289).

Each correspondence is graded before any interpretation: STRUCTURAL (the tradition's object is an object of the law), COUNT
(only the numbers agree; recorded, and tested against decoys before it is called more), ASSIGNED (a mapping someone chose; never
a finding), INTERPRETIVE (a reading or a shared theme, offered through M218). The aspects of astrology are the elements of order 2, 3, 4, 6, 8 and 12 of the law's cycle of 24, at 15 degrees a step.
    python3 tools/esoteric.py --aspects P     # the anchor P (0 to 23) with its arms read as aspects (the M218 Astrology Companion)
    python3 tools/esoteric.py --grades        # the traditions and their grades
    python3 tools/esoteric.py --selftest
Standard library only.
"""
import sys
ORBIT = [2, 5, 7, 3, 1, 4, 5, 9, 5, 5, 1, 6, 7, 4, 2, 6, 8, 5, 4, 9, 4, 4, 8, 3]
NAMES = ['Seed', 'Fixpoint', 'Generator', 'Desire', 'Unity', 'Law', 'Seed/Causal', 'Navigator', 'Generation', 'Fixpoint', 'Unity', 'Question',
         'Opening', 'Gap', 'Observer', 'Other', 'Flow', 'Seed/Return', 'Threshold', 'Time', 'Reckoning', 'Sublime', 'Collective', 'Return']
ARMS = [('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12)]
ASPECTS = {0: 'conjunction', 2: 'semi-sextile', 3: 'semi-square', 4: 'sextile', 6: 'square', 8: 'trine', 10: 'quincunx', 12: 'opposition'}
A = ((0, 1), (1, 1))
def mul(X, Y, m=9): return tuple(tuple(sum(X[i][t]*Y[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
def pw(e, m=9):
    P = ((1, 0), (0, 1))
    for _ in range(e): P = mul(P, A, m)
    return P
def order(X, m=9):
    I = ((1, 0), (0, 1)); k, P = 1, X
    while P != I: P = mul(P, X, m); k += 1
    return k
def aspect(steps):
    s = steps % 24; s = min(s, 24 - s)
    return ASPECTS.get(s, 'no classical aspect'), s * 15
GRADES = [
 ('sacred geometry and the golden ratio', 'STRUCTURAL', 'the law is multiplication by the golden number'),
 ('astrology: the aspects', 'STRUCTURAL', 'opposition, trine, square, sextile, semi-sextile, semi-square are elements of order 2, 3, 4, 6, 12, 8'),
 ('astrology: the twelve signs', 'COUNT', 'the geometric representation has order 12; which sign stands where is ASSIGNED'),
 ('numerology: digit reduction', 'STRUCTURAL', 'reduction mod 9 is the ring of the law; meanings are set beside it by M218, never assigned'),
 ('runes: the Elder Futhark in three aettir', 'COUNT', 'twenty-four runes; each aett is a consecutive arc of eight steps, a trine arc of 120 degrees'),
 ('Jyotish: the 27 nakshatras', 'COUNT', 'twenty-seven primitive worlds at depth 2'),
 ('I Ching and geomancy', 'COUNT', '64 and 16 are binary; at the place 2 the law has period 3'),
 ('Tarot', 'ASSIGNED', 'no number of the law gives 78, 22 or 56; its method is served by the four arms as a spread'),
 ('Kabbalah: emanation', 'INTERPRETIVE', 'one source whole in each expression has its exact form in the unique-expression theorem'),
 ('alchemy: the four stages', 'INTERPRETIVE', 'the quarter-turn A^6 has order 4')]
def report_aspects(p):
    p %= 24; L = ['ANCHOR P%d %s (%d), phase %d degrees' % (p, NAMES[p], ORBIT[p], p * 15)]
    for name, off in ARMS:
        q = (p + off) % 24; a, deg = aspect(off)
        L.append('  %-8s P%-2d %-12s (%d)  %3d degrees: %s' % (name, q, NAMES[q], ORBIT[q], deg, a))
    L.append('  the zodiacal sign of a position is assigned by the tradition, not given by the law (ASSIGNED; M218, CDT-C)')
    return '\n'.join(L)
def checks():
    counts = {d: ORBIT.count(d) for d in range(1, 10)}
    aettir = [set(range(8*k, 8*k+8)) for k in range(3)]; classes = [set(range(i, 24, 3)) for i in range(3)]
    return [
     ('the aspects are the elements of order 2, 3, 4, 6, 12 and 8', [order(pw(s)) for s in (12, 8, 6, 4, 2, 3)] == [2, 3, 4, 6, 12, 8]),
     ('the square is the square root of -I', mul(pw(6), pw(6)) == ((8, 0), (0, 8))),
     ('the Antipode is an opposition and the 4D arm a trine', aspect(12)[0] == 'opposition' and aspect(8)[0] == 'trine'),
     ('the digits 4 and 5 five times each, every other digit twice', counts == {1: 2, 2: 2, 3: 2, 4: 5, 5: 5, 6: 2, 7: 2, 8: 2, 9: 2}),
     ('the aettir are trine arcs, not the step-3 classes', all(max(a) - min(a) == 7 for a in aettir) and not any(a == c for a in aettir for c in classes)),
     ('every tradition graded', all(g in ('STRUCTURAL', 'COUNT', 'ASSIGNED', 'INTERPRETIVE') for _, g, _ in GRADES)),
    ]
if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--aspects']: print(report_aspects(int(a[1])))
    elif a == ['--grades']: [print('%-42s %-10s %s' % g) for g in GRADES]
    elif a == ['--selftest']:
        C = checks(); [print('%-60s %s' % (n, 'PASS' if c else 'FAIL')) for n, c in C]
        print('ESOTERIC SELFTEST: %d of %d' % (sum(c for _, c in C), len(C))); sys.exit(0 if all(c for _, c in C) else 1)
    else: print(__doc__)
