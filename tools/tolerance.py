#!/usr/bin/env python3
"""tolerance.py -- M329 Tolerance Chain Check (Core Part 3.55; Companion Part 125).

A tolerance principle -- one small step never changes a status -- is checked before it is chained. For a chain of
unit steps from N down to 1 the check prints, with actual values:

  THE CHAIN        the number of steps, the absolute step and its relative size at the top (1/N) and at the bottom (1/2)
  DRIFT            the cumulative relative change, the sum of 1/n for n = 2 to N (H_N - 1, beside ln N + gamma - 1)
  TRANSITIVITY     for a relative tolerance delta: two tolerated steps that compose into an untolerated one, and the
                   number of unit steps after which the change from the top exceeds delta (floor(delta N) + 1)
  RESOLUTION       N and 1 read modulo 9, 27, 81 and 729, the 3-adic valuation of N - 1, and the class of n under dr(5n)
                   for n = 1 to 9: every unit step changes it, every step of nine keeps it
  DEGREES          for a linear degree mu(n) = (n - 1)/(N - 1), the first count at each threshold
  PRESERVATION     under any one sharp cutoff c the step n -> n - 1 keeps the status at all steps but one (n = c); with a band
                   the status label changes at exactly two steps (n = LO and n = HI): the tolerance premise is false at so few
                   steps that each step looks safe
  STATUS           with --band LO HI (the admissible cutoffs): DEFINITE-OUT, BORDERLINE and DEFINITE-IN counts; without
                   a band the status of every count is CONTEXT-DEPENDENT, a decision the check does not make

    python3 tools/tolerance.py --chain N [--delta D] [--band LO HI] [--theta T ...]
    python3 tools/tolerance.py --selftest
It reads a tolerance principle and never decides a predicate: the status of a count is the Striker's (Core Part 7).
Standard library only; exact rational arithmetic where a value is printed exactly.
"""
import math, sys
from fractions import Fraction as F
GAMMA = 0.5772156649015329
dr = lambda x: 9 if x % 9 == 0 else x % 9
def v3(x):
    k = 0
    while x and x % 3 == 0: x //= 3; k += 1
    return k
def num(x):
    x = F(x)
    return format(x.numerator, ',') if x.denominator == 1 else format(float(x), ',.6g')
def first_at(N, theta):
    """least integer n with (n - 1)/(N - 1) >= theta"""
    return math.ceil(F(theta) * (N - 1) + 1)
def report(N, delta=F(1, 100), band=None, thetas=(F(1, 4), F(1, 2), F(3, 4), F(9, 10))):
    L = ['M329 TOLERANCE CHAIN CHECK (Core Part 3.55) | chain %s -> 1 by unit steps' % format(N, ',')]
    L.append('  THE CHAIN: %s steps | absolute step 1 | relative step 1/%s = %.6g at the top, 1/2 = 0.5 at the bottom' % (format(N - 1, ','), format(N, ','), 1 / N))
    h = math.fsum(1 / n for n in range(2, N + 1)) if N <= 10 ** 7 else math.log(N) + GAMMA - 1
    L.append('  DRIFT: sum of 1/n for n = 2 to N = %.10f (ln N + gamma - 1 = %.10f): each step small against the count it leaves, the steps add up to %.2f in relative terms' % (h, math.log(N) + GAMMA - 1, h))
    d = F(delta); a = F(N); b = a * (1 - d); c = b * (1 - d)
    L.append('  TRANSITIVITY (relative tolerance delta = %s): %s ~ %s and %s ~ %s, each a change of exactly %s; %s to %s is a change of %s > %s, so tolerance does not compose; from the top, unit steps stay within delta for %s steps and leave it at step %s' % (
        float(d), num(a), num(b), num(b), num(c), float(d), num(a), num(c), float(1 - (1 - d) ** 2), float(d),
        format(math.floor(d * N), ','), format(math.floor(d * N) + 1, ',')))
    mods = ', '.join('mod %d: %d and 1%s' % (m, N % m, '' if N % m == 1 else ' (apart)') for m in (9, 27, 81, 729))
    L.append('  RESOLUTION: %s | N - 1 = %s has 3-adic valuation %d, so |N - 1|_3 = 1/%d while |1|_3 = 1 | the class dr(5n) for n = 1 to 9: %s, then it repeats' % (
        mods, format(N - 1, ','), v3(N - 1), 3 ** v3(N - 1), ', '.join(str(dr(5 * n)) for n in range(1, 10))))
    L.append('  DEGREES (mu(n) = (n - 1)/(N - 1)): ' + '; '.join('theta %s: first n = %s, mu = %.7f' % (float(t), format(first_at(N, t), ','), float(F(first_at(N, t) - 1, N - 1))) for t in thetas))
    k = N - 1
    L.append('  PRESERVATION: under one sharp cutoff c, H(n) -> H(n - 1) holds at %s of %s steps and fails at 1 (n = c), so a step taken alone is almost always safe and the chain as a whole is not%s' % (format(k - 1, ','), format(k, ','), (' | with the band, the status label changes at 2 steps (n = %s and n = %s) and holds at %s' % (format(band[0], ','), format(band[1], ','), format(k - 2, ','))) if band else ''))
    if band:
        lo, hi = band
        L.append('  STATUS (admissible cutoffs %s to %s): DEFINITE-OUT %s counts (n < %s) | BORDERLINE %s (%s <= n < %s) | DEFINITE-IN %s (n >= %s) | precisifications %s' % (
            format(lo, ','), format(hi, ','), format(lo - 1, ','), format(lo, ','), format(hi - lo, ','), format(lo, ','), format(hi, ','), format(N - hi + 1, ','), format(hi, ','), format(hi - lo + 1, ',')))
    else:
        L.append('  STATUS: CONTEXT-DEPENDENT for every count -- no band of admissible cutoffs was given, and the check does not choose one')
    L.append('  [the values are exact (CDT-A); what the predicate is, and where it applies, is the Striker\'s (Core Part 7)]')
    return '\n'.join(L)
def selftest():
    cases = [('a million: 999,999 steps', '999,999 steps' in report(10 ** 6)),
             ('threshold 3/4 gives 750,001, not 750,000', first_at(10 ** 6, F(3, 4)) == 750001),
             ('threshold 9/10 gives 900,001', first_at(10 ** 6, F(9, 10)) == 900001),
             ('10^6 and 1 agree mod 27 and part mod 81', 'mod 27: 1 and 1 |' in report(10 ** 6).replace('mod 27: 1 and 1,', 'mod 27: 1 and 1 |') and 'mod 81: 55 and 1 (apart)' in report(10 ** 6)),
             ('v3(999,999) = 3', v3(999999) == 3),
             ('a band of 100 to 10,000 gives 9,900 borderline counts and 9,901 precisifications', 'BORDERLINE 9,900' in report(10 ** 6, band=(100, 10000)) and 'precisifications 9,901' in report(10 ** 6, band=(100, 10000))),
             ('delta 1%: leaves it at step 10,001', 'leave it at step 10,001' in report(10 ** 6)),
             ('one sharp cutoff breaks 1 of 999,999 steps', 'holds at 999,998 of 999,999 steps and fails at 1' in report(10 ** 6)),
             ('a band changes the label at 2 steps', 'changes at 2 steps (n = 100 and n = 10,000)' in report(10 ** 6, band=(100, 10000)))]
    for n, ok in cases: print('%-80s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('M329 SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if not a or a[0] != '--chain': print(__doc__); sys.exit(2)
    N = int(a[1]); delta = F(1, 100); band = None; thetas = (F(1, 4), F(1, 2), F(3, 4), F(9, 10))
    if '--delta' in a: delta = F(a[a.index('--delta') + 1])
    if '--band' in a: i = a.index('--band'); band = (int(a[i + 1]), int(a[i + 2]))
    if '--theta' in a: i = a.index('--theta'); thetas = tuple(F(x) for x in a[i + 1:] if not x.startswith('--'))
    print(report(N, delta, band, thetas))
