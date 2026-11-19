#!/usr/bin/env python3
"""echo_test.py -- M325 Construct Echo Test (Tier 3, ADOPTED 28 October 2026; Core Part 3.51; Companion Part 105).

The Construct's interval bank turned into a test of any claimed pattern in a sequence. Each row of the sequence is a
vector of integers, read mod 9. For every interval h = 1 to 23 the template (row t - h, row t) is progressed to row t + h
by three rules frozen in advance (F1 the Omega42 law y + x, F2 the constant step 2x - y, F3 the echo x), and the
matches are counted. The same rules are run on the rows shuffled, and a rule shows a signal only if it beats the
shuffles after correction for all 69 tests, by the maximum statistic over the family.

It is a calibration instrument: on a sequence with no memory it must report NO SIGNAL, and on a sequence that obeys
one of the rules it must report a SIGNAL. The selftest runs both controls. The reference record is the South African
Lotto history, records/construct/sa_lotto.py.
    python3 tools/echo_test.py --file rows.csv [--shuffles 1000]    # one row per line, integers separated by commas
    python3 tools/echo_test.py --selftest
Needs numpy.
"""
import random, sys
import numpy as np

RULES = ['F1 law y+x', 'F2 step 2x-y', 'F3 echo x']

def scores(R):
    s = np.zeros((3, 23))
    for j, h in enumerate(range(1, 24)):
        y, x, z = R[:-2 * h], R[h:-h], R[2 * h:]
        for r, f in enumerate([(y + x) % 9, (2 * x - y) % 9, x]): s[r, j] = (f == z).mean()
    return s

def test(rows, shuffles=1000, seed=4224):
    R = np.array(rows) % 9
    obs = scores(R); rng = random.Random(seed); idx = list(range(len(R))); null = []
    for _ in range(shuffles): rng.shuffle(idx); null.append(scores(R[idx]))
    null = np.array(null); mu, sd = null.mean(0), null.std(0) + 1e-12
    z = (obs - mu) / sd; fam = (1 + (((null - mu) / sd).reshape(shuffles, -1).max(1) >= z.max()).sum()) / (1 + shuffles)
    r, j = np.unravel_index(int(z.argmax()), z.shape)
    return {'rule': RULES[r], 'h': j + 1, 'z': float(z.max()), 'family_p': float(fam), 'signal': bool(fam < 0.05)}

def report(res):
    return 'M325 ECHO TEST: strongest %s at h = %d, z %+.2f, family p %.4f -- %s' % (
        res['rule'], res['h'], res['z'], res['family_p'], 'A SIGNAL BEYOND CHANCE' if res['signal'] else 'NO SIGNAL BEYOND CHANCE')

def selftest():
    g = random.Random(1)
    iid = [[g.randrange(1, 50) for _ in range(6)] for _ in range(400)]
    law = [[g.randrange(9) for _ in range(6)] for _ in range(6)]
    for t in range(6, 400): law.append([(law[t - 6][i] + law[t - 3][i]) % 9 if i < 3 else g.randrange(9) for i in range(6)])
    a, b = test(iid, 200), test(law, 200)
    cases = [('a sequence with no memory reports no signal', not a['signal']),
             ('a sequence that follows the law at h = 3 in half its positions reports a signal', b['signal']),
             ('and names the law at h = 3', b['rule'] == RULES[0] and b['h'] == 3)]
    for name, ok in cases: print('%s  %s' % ('PASS' if ok else 'FAIL', name))
    print('  negative control: ' + report(a)); print('  positive control: ' + report(b))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--file'] and len(a) >= 2:
        rows = [[int(v) for v in line.split(',') if v.strip()] for line in open(a[1]) if line.strip() and not line[0].isalpha()]
        n = int(a[a.index('--shuffles') + 1]) if '--shuffles' in a else 1000
        print(report(test(rows, n))); sys.exit(0)
    print(__doc__)
