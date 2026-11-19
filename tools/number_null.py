#!/usr/bin/env python3
"""number_null.py -- M341 Number-Resonance Null (Core Part 3.67, L-553, L-552): what a number presented as meaningful shares
with the law, set against what every number of its kind shares.

The rule is general (L-553): any numerical correspondence offered as potentially significant -- a cultural, sacred or
symbolic number, a date, a dimension, an astronomical or biological count, a constant, or a relation found in the course
of an exploration -- is read only after its null. The null is chosen by the kind of relation tested (a reversal is set
against reversal pairs, a shared residue against a declared range), and a relation chosen after searching many is graded
against the whole search (the selection correction, an empirical matter kept in Core Appendix S.10).

Each relation is graded by its GENERIC SHARE: GENERIC (half or more of the numbers of its kind have it) counts for nothing;
ORDINARY (more than 1 in 20) is one value among several and is read only as such; RARE (1 in 20 or fewer) is counted, at its share.

A number from a book, a tradition or a date meets the cycle in many ways, and most of them are generic: every two-digit
number has the residue of its reversal, every count has a placement. Before a number is read, this tool computes each
relation it has to the law and, beside each, its GENERIC SHARE -- the share of the numbers of its kind (the same number of
digits; for a pair, every pair related the same way) that have that relation too. A relation every number has counts for nothing; a rare one is counted at its share (L-486, L-501, L-510).

    python3 tools/number_null.py N [M]       # one number, or a pair (M is read as related to N: reversal, sum, difference)
    python3 tools/number_null.py --selftest
The relations for one number n: its residue modulo 9 (and whether it is G = 6, the nilpotent, or 0); its placement CPP(n) =
dr(5n); the law's power T^n, read as n modulo 24 -- the identity (0), the antiparticle (12), or an arm (Yang 5, Yin 18, 4D 8);
the canonical value at P(n mod 24); whether n is a Pisano period of a modulus up to 1000. For a pair, also: whether one is the
digit reversal of the other, whether they share residue and placement, and their difference modulo 24 read as a power of T.
Standard library only.
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
import canonical_reference as cr

dr = lambda n: 1 + (n - 1) % 9 if n > 0 else 0
T = lambda s: (s[1], (s[0] + s[1]) % 9)
POWER = {0: 'the identity: every state returns (the period)', 12: 'the antiparticle: T^12 = -I', 5: 'the Yang arm', 18: 'the Yin arm, braiding trivially',
         8: 'the 4D arm'}


def canonical_values():
    s, out = (2, 5), []
    for _ in range(24): out.append(s[0] or 9); s = T(s)
    return out


def pisano(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1): return k


_PIS = None
def pisano_set():
    global _PIS
    if _PIS is None: _PIS = {pisano(m) for m in range(2, 1001)}
    return _PIS


def kind(n):
    d = len(str(n)); return list(range(10 ** (d - 1), 10 ** d)) if d > 1 else list(range(1, 10))


def props1(n):
    V = canonical_values()
    return {'residue mod 9': dr(n) % 9, 'residue is G = 6, the nilpotent': dr(n) == 6, 'placement CPP(n) = dr(5n)': dr(5 * n),
            'T^n (n mod 24)': n % 24, 'T^n is the identity, the antiparticle or an arm': n % 24 in POWER,
            'canonical value at P(n mod 24)': V[(n - 1) % 24], 'a Pisano period of a modulus up to 1000': n in pisano_set()}


def grade(sh):
    return 'GENERIC' if sh >= 0.5 else ('RARE' if sh <= 0.05 else 'ORDINARY')


def share(test, ks):
    return sum(1 for x in ks if test(x)) / len(ks)


def report(n, m=None):
    L = ['======= M341 NUMBER-RESONANCE NULL (Core Part 3.67, L-552) =======', 'NUMBER: %d%s' % (n, '' if m is None else ' with %d' % m)]
    K = kind(n); P = props1(n)
    L.append('ONE NUMBER (generic share among the %d numbers of %d digits):' % (len(K), len(str(n))))
    for key, val in P.items():
        if isinstance(val, bool):
            sh = share(lambda x: props1(x)[key] == val, K)
        else:
            sh = share(lambda x: props1(x)[key] == val, K)
        extra = (' -- %s' % POWER[val]) if key == 'T^n (n mod 24)' and val in POWER else ''
        g = grade(sh) if isinstance(val, bool) else 'VALUE (every value is about this rare)'
        L.append('  %-48s %-6s share %.3f  %s%s' % (key, val, sh, g, extra))
    if m is not None:
        rev = lambda x: int(str(x)[::-1]) if str(x)[::-1][0] != '0' else None
        is_rev = rev(n) == m
        L.append('PAIR (%d, %d): %s' % (n, m, 'digit reversals of each other' if is_rev else 'not digit reversals'))
        # the natural population: unordered, non-palindromic reversal pairs of this many digits, both end digits nonzero
        if is_rev:
            base = sorted({tuple(sorted((x, rev(x)))) for x in K if rev(x) is not None and x != rev(x)})
            popname = '%d non-palindromic reversal pairs' % len(base)
        else:
            base = [tuple(sorted((x, y))) for x in K for y in kind(m) if x != y]
            popname = '%d pairs of their sizes' % len(base)
        diff = abs(n - m)
        tests = [('the same residue mod 9', lambda p: dr(p[0]) % 9 == dr(p[1]) % 9),
                 ('the same placement CPP', lambda p: dr(5 * p[0]) == dr(5 * p[1])),
                 ('the difference is exactly %d%s' % (diff, ', the Yin arm (18 mod 24)' if diff % 24 == 18 else (' (T^%d)' % (diff % 24) if diff % 24 in POWER else '')),
                  lambda p: abs(p[0] - p[1]) == diff),
                 ('one of the two is the period, 24', lambda p: 24 in p)]
        L.append('  (generic share among the %s; the pair is read unordered)' % popname)
        for name, t in tests:
            val = t((n, m)); sh = share(lambda p: t(p) == val, base)
            L.append('  %-58s %-5s share %.3f  %s' % (name, val, sh, grade(sh)))
        L.append('  raw difference |%d - %d| = %d, which is T^%d of the law%s  VALUE' %
                 (n, m, diff, diff % 24, (' (%s)' % POWER[diff % 24]) if diff % 24 in POWER else ''))
    L.append('RULE (L-553, L-552): a GENERIC relation counts for nothing, an ORDINARY one is one value among several, a RARE one is counted at its share (L-486, L-510).')
    L.append('SELECTION (Core Appendix S.10): this null grades one declared relation; a relation chosen after searching many must be graded against the whole search, which is an empirical correction kept in the Scientific Appendix.')
    L.append('======= END M341 NUMBER-RESONANCE NULL =======')
    return '\n'.join(L)


def selftest():
    ok = True
    r = report(42, 24)
    cases = [('42 and 24 share their residue, and so does every reversal pair (GENERIC)', 'the same residue mod 9' in r and 'share 1.000  GENERIC' in r),
             ('the natural population is the 36 non-palindromic reversal pairs', '36 non-palindromic reversal pairs' in r),
             ('the difference 18, the Yin arm, is ORDINARY at 7/36 = 0.194', 'the difference is exactly 18, the Yin arm (18 mod 24)' in r and 'share 0.194  ORDINARY' in r),
             ('one of the two being the period 24 is RARE at 1/36 = 0.028', 'one of the two is the period, 24' in r and 'share 0.028  RARE' in r),
             ('T^42 is the Yin arm (42 mod 24 = 18)', props1(42)['T^n (n mod 24)'] == 18),
             ('24 is the identity (the period)', props1(24)['T^n (n mod 24)'] == 0),
             ('42 is a Pisano period (of 58, 116, 211, 422, 844)', props1(42)['a Pisano period of a modulus up to 1000']),
             ('the canonical value at P12 is 6', canonical_values()[11] == 6)]
    for name, good in cases:
        print('  %-66s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('NUMBER-RESONANCE NULL SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    print(report(int(a[0]), int(a[1]) if len(a) > 1 else None))
