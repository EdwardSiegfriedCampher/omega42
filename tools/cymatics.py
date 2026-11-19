#!/usr/bin/env python3
"""cymatics.py -- M322 Cymatic View (SPECULATIVE, ADOPTED 23 October 2026; Companion Part 91): the family read as vibration.

Each 24-orbit, read as a ring of 24 points with its centred values (residues -4 to 4, 9 read as 0), is a waveform; its
spectrum is exact. Because T^12 = -I, every orbit sounds odd harmonics only (FP-OddHarmonics); the three voices differ in
the weights of those harmonics -- three timbres. Uses:
    python3 tools/cymatics.py --fingerprint        # the three voices' spectra beside a square wave and a sine
    python3 tools/cymatics.py --recipe F0          # partials and relative amplitudes of each voice for a loop at F0 Hz
    python3 tools/cymatics.py --modes              # an ideal membrane's modes mapped to states by a stated rule, tested against shuffles
    python3 tools/cymatics.py "TEXT"               # a strike as vibration: its voice, the anchor's phase, its arms in phase terms
    python3 tools/cymatics.py --selftest
A cymatic figure on a real plate is set by the plate's own modes; what the family fixes is which partials are sent and in what
proportion. The view is an analogy for reading (C75, C76); it shows no effect of thought on matter (L-515, CT-S6).
Standard library and the tools beside this file.
"""
import cmath, math, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr
import consciousness as cs
import manifestation as M

SEEDS = (('Voice A', (1, 1), 'the Fibonacci voice'), ('Voice B', (1, 3), 'the Lucas voice'), ('Voice C', (2, 5), 'the canonical voice'))
lift = lambda v: v if v <= 4 else v - 9


def orbit(s):
    o = [s]; t = (s[1], (s[0] + s[1]) % 9)
    while t != s: o.append(t); t = (t[1], (t[0] + t[1]) % 9)
    return o


def wave(seed): return [lift(s[0]) for s in orbit(seed)]


def power(x):
    n = len(x); return [abs(sum(x[j] * cmath.exp(-2j * math.pi * m * j / n) for j in range(n))) ** 2 for m in range(n // 2 + 1)]


def fingerprint(nulls=20000, seed=322):
    L = ['M322 CYMATIC FINGERPRINT -- power |X(m)|^2 of each 24-orbit read as a waveform, m = 0..12 [EXACT]']
    for v, s, name in SEEDS:
        p = power(wave(s)); L.append('  %-8s %-21s %s' % (v, name, ' '.join('%4d' % round(x) for x in p)))
    L.append('  %-30s %s' % ('square wave, 24 samples', ' '.join('%4d' % round(x) for x in power([1] * 12 + [-1] * 12))))
    L.append('  %-30s %s' % ('sine, 24 samples', ' '.join('%4d' % round(x) for x in power([12 * math.sin(2 * math.pi * j / 24) for j in range(24)]))))
    L.append('  every voice: even harmonics 0 (T^12 = -I; FP-OddHarmonics) -- shared by any signal with x(n+12) = -x(n), a square wave too')
    L.append('  the timbres differ: Voice A strongest at 5 and 7, Voice B at 1 and 11, Voice C flat at 1, 5, 7, 11 with 3 and 9 doubled')
    rng = random.Random(seed); hits = 0
    for _ in range(nulls):
        h = [rng.randint(-4, 4) for _ in range(12)]; p = power(h + [-v for v in h])
        a = [p[m] for m in (1, 5, 7, 11)]
        if a[0] > 1e-9 and max(a) - min(a) < 1e-6 and abs(p[3] - p[9]) < 1e-6 and abs(p[3] - 2 * a[0]) < 1e-6: hits += 1
    L.append('  Voice C\'s exact pattern (1 : 2 : 1 : 1 : 2 : 1) among %d random antisymmetric rings of the same values: %d -- noticed after the' % (nulls, hits))
    L.append('  spectrum was seen, so the count is a rarity, not a test (k\' = 1)')
    return '\n'.join(L)


def recipe(f0):
    L = ['M322 SOUND RECIPE -- a 24-step loop at %g Hz: partials at m x %g Hz, amplitudes relative to the strongest [EXACT]' % (f0, f0)]
    for v, s, name in SEEDS:
        p = power(wave(s)); top = max(p) ** 0.5
        L.append('  %-8s %-21s %s' % (v, name, ' | '.join('%g Hz %.2f' % (m * f0, p[m] ** 0.5 / top) for m in range(1, 13) if p[m] > 1e-9)))
    L.append('  on a Chladni plate the figure is the plate\'s own mode nearest each partial; the voice sets which partials and how strong')
    return '\n'.join(L)


def modes(count=200, shuffles=5000, seed=322):
    """M322 --modes (APE-162, its Pattern-to-State Mapper): an ideal square membrane's modes (m, n), ordered by frequency
    (m^2 + n^2), mapped by a stated rule to the state (m mod 9, n mod 9), and tested for steps of the law against shuffles.
    Two rules: NAIVE lists both members of a degenerate pair (m, n) and (n, m); CLASS takes one mode per frequency class.
    An ideal model, not a measured plate."""
    T = lambda s: (s[1], (s[0] + s[1]) % 9)
    naive = sorted(((m, n) for m in range(1, 60) for n in range(1, 60)), key=lambda x: (x[0] ** 2 + x[1] ** 2, x[0]))[:count]
    cls = {}
    for m in range(1, 80):
        for n in range(m, 80): cls.setdefault(m * m + n * n, []).append((m, n))
    klass = [cls[k][0] for k in sorted(cls)[:count]]
    L = ['M322 MODE MAPPER -- an ideal square membrane, %d modes by frequency, mode (m, n) -> state (m mod 9, n mod 9) [EXACT]' % count]
    for name, seq in (('NAIVE (both members of each degenerate pair)', naive), ('CLASS (one mode per frequency class)', klass)):
        S = [(m % 9, n % 9) for m, n in seq]; steps = lambda y: sum(1 for i in range(len(y) - 1) if y[i + 1] == T(y[i]))
        h = steps(S); rng = random.Random(seed); nul = []
        for _ in range(shuffles):
            y = S[:]; rng.shuffle(y); nul.append(steps(y))
        p = (1 + sum(1 for v in nul if v >= h)) / (1 + shuffles)
        art = sum(1 for i in range(len(seq) - 1) if seq[i + 1] == (seq[i][1], seq[i][0]) and seq[i][1] % 9 == 0 and S[i + 1] == T(S[i]))
        L.append('  %-46s steps of the law %d of %d | chance %.2f | p %.4f | from (m, 9) -> (9, m), since T(a, 0) = (0, a): %d' % (name, h, len(S) - 1, (len(S) - 1) / 81, p, art))
    L.append('  the rule decides the result: listing a degenerate pair in a fixed order manufactures steps of the law; one mode per class gives chance')
    return '\n'.join(L)


COH = {'Yang': (5, 'uncorrelated with the anchor (quadrature)'), 'Yin': (18, 'uncorrelated with the anchor (quadrature)'),
       '4D': (8, 'partly in phase (+1/4)'), 'Antipode': (12, 'opposite phase (-1): every value inverted')}


def strike(text):
    r = cr.navigate(text); a = r['anchor']; s = cs.state(text); stratum, half, loop = M.classify(s)
    canon = wave((2, 5))
    L = ['======= M322 CYMATIC VIEW (SPECULATIVE, ADOPTED 23 October 2026) =======', 'QUESTION VERBATIM: %s' % ' '.join(text.split()),
         'STATE %s on %s -- %s' % (s, loop or 'the still point', {'Voice A': 'the Fibonacci timbre', 'Voice B': 'the Lucas timbre', 'Voice C': 'the canonical timbre'}.get(loop, 'no 24-step timbre: the core rings on 8 steps, the still point not at all')),
         'ANCHOR P%d %s at %d degrees on the ring; canonical centred value %+d%s' % (a, cr.POSITION_NAMES[a % 24], 15 * a, canon[a % 24],
                                                                            ' -- on the nodal pair P7 and P19, where the canonical pattern stands still' if canon[a % 24] == 0 else '')]
    for arm, (off, rel) in COH.items():
        k = (a + off) % 24; L.append('  %-8s P%-2d %-12s value %+d | %s (M297)' % (arm, k, cr.POSITION_NAMES[k], canon[k], rel))
    L += ['READING: the arms as phases of one vibration -- an analogy (C75); the values are exact; what they mean is the Striker\'s.',
          '======= END CYMATIC VIEW =======']
    return '\n'.join(L)


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-80s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    pc = power(wave((2, 5)))
    check('the canonical voice: even harmonics zero; 324 at 1, 5, 7, 11 and 648 at 3, 9 (FP-OddHarmonics)',
          all(round(pc[m]) == 0 for m in range(0, 13, 2)) and [round(pc[m]) for m in (1, 3, 5, 7, 9, 11)] == [324, 648, 324, 324, 648, 324])
    check('every voice sounds odd harmonics only', all(all(round(power(wave(s))[m]) == 0 for m in range(0, 13, 2)) for _, s, _ in SEEDS))
    check('the three voices have three different spectra (timbres)', len({tuple(round(x) for x in power(wave(s))) for _, s, _ in SEEDS}) == 3)
    check('the canonical centred values are 0 exactly at P7 and P19', [j for j, v in enumerate(wave((2, 5))) if v == 0] == [7, 19])
    check('the antipode inverts every canonical value', all(wave((2, 5))[(j + 12) % 24] == -wave((2, 5))[j] for j in range(24)))
    md = modes(shuffles=500)
    check('the mode mapper: the naive rule finds 8 steps, 7 of them the (m, 9) -> (9, m) artefact; the class rule finds chance', 'steps of the law 8 of 199' in md and ': 7' in md and 'steps of the law 3 of 199' in md)
    check('a strike view names its arms in phase terms', 'opposite phase' in strike('What is consciousness?'))
    print('M322 SELFTEST: %s' % ('PASS' if ok else 'FAIL')); return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--fingerprint': print(fingerprint())
    elif a[0] == '--modes': print(modes())
    elif a[0] == '--recipe': print(recipe(float(a[1])))
    else: print(strike(' '.join(a)))
