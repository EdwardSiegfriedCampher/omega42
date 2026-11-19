#!/usr/bin/env python3
"""manifestation.py -- M312 Manifestation Phase (Core Part 3.38, L-492; Companion Part 50).

An optional Tier 3 companion reading, computed after the freeze. It reports where a strike stands in the phase
structure of the family: the state (r1, r2) mod 9 of the strike (the same state M310 and M308 use), its stratum, its
norm half, what one step of the law and its square do to that half, and the phases of the anchor and the four arms
on the canonical cycle. Every value is CDT-A; any meaning given to the halves is FRAME-INTERPRETIVE (the 1/7 and 6/7
halves of Antipodal Phase Projection, L-492) and the Striker's to judge. The reading never alters the counts, the
anchor, the arms or THE ANSWER (L-424).

  STRATUM  UNIT (72 states: norm a unit) | CORE (8 states: norm 0, residual norm N(s/3) mod 3 a unit) | STILL POINT (0, 0)
  HALF     SEVENTH (norm in {1, 2, 4}, the digits 142 of 1/7) | MANIFEST (norm in {8, 7, 5}, the digits 857 of 6/7)
           on the core: AXIS +/- (residual norm 1 or 2 mod 3); at (0, 0): STILL
  T flips every half (det T = -1); T^2 keeps it (det T^2 = +1).
  MODE     on a unit state, the voice it stands on and the turn of the voices under doubling (x2 moves to the next
           voice, three doublings return as the negative, 2^3 = -1; FP-VoiceCosets); on the core, NILPOTENT (s*s = 0,
           the ground: the field Z[phi]/3 one scale down, FP-CoreField); at (0, 0), STILL.
  NESTING  where the state stands in the tower of scales: 3 x a unit here lies in the ground one scale up; a core state is
           the whole family one scale down; the still point is still at every scale (FP-CoreRecursion).
  ARC      the half read in positive geometry (M230-K, PG-05): the lift of least real norm |N(a, b)| of the state lies on
           the arc N > 0 (SEVENTH, AXIS +) or on the golden arc N < 0, the amplituhedron A(2,1,1) with the law's
           eigenbasis as data (MANIFEST, AXIS -); the still point lies on no arc. Least |N|: 1, 4, 11 on Voices A, B, C,
           9 on the core (records/positive_geometry/, part H).

Usage:
    python3 tools/manifestation.py "DOMAIN TEXT"
    python3 tools/manifestation.py --atlases      # the phase census of the Bashar, Seth and Ra atlases
    python3 tools/manifestation.py --selftest
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import canonical_reference as cr

SEVENTH, MANIFEST = {1, 2, 4}, {8, 7, 5}
VOICE = {1: 'Voice A', 8: 'Voice A', 4: 'Voice B', 5: 'Voice B', 2: 'Voice C', 7: 'Voice C'}
T = lambda s: (s[1], (s[0] + s[1]) % 9)
N = lambda s: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
ARMS = (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))


def canonical_positions():
    s, out = (2, 5), []
    for _ in range(24): out.append(s); s = T(s)
    return out


def classify(s):
    if s == (0, 0): return 'STILL POINT', 'STILL', None
    q = N(s)
    if q == 0:
        r = (s[0] // 3) ** 2 + (s[0] // 3) * (s[1] // 3) - (s[1] // 3) ** 2
        return 'CORE', 'AXIS %s' % ('+' if r % 3 == 1 else '-'), 'the eight-step loop'
    return 'UNIT', ('SEVENTH' if q in SEVENTH else 'MANIFEST'), VOICE[q]


def mode(s):
    """FP-VoiceCosets, FP-CoreField: the voice and its turn under doubling, or the core's ground."""
    if s == (0, 0): return 'STILL (fixed by every power of the law)'
    if N(s) % 3 == 0:
        return 'GROUND: NILPOTENT (s*s = 0); one scale down the core is the field Z[phi]/3, a single orbit of 8'
    v = VOICE[N(s)]; d = ((2 * s[0]) % 9, (2 * s[1]) % 9); dd = ((4 * s[0]) % 9, (4 * s[1]) % 9)
    return '%s -> x2 -> %s -> x2 -> %s -> x2 -> %s again, as its negative (2^3 = -1)' % (v, VOICE[N(d)], VOICE[N(dd)], v)


def nesting(s):
    """FP-CoreRecursion, FP-TowerPeriods: where the state stands in the tower of scales (U36)."""
    if s == (0, 0): return 'the still point, at every scale'
    if N(s) % 3 == 0:
        return 'a core state, 3 x %s with %s on Z[phi]/3: the whole family one scale down' % (str((s[0] // 3, s[1] // 3)), str((s[0] // 3, s[1] // 3)))
    return 'a unit modulo 9; one scale up, 3 x this state lies in the ground of the family modulo 27, whose non-units are 3 x the family modulo 9'


def arc(s):
    """PG-05: the arc of the state's minimal lift, read from its half (records/positive_geometry/, part H)."""
    h = classify(s)[1]
    if h == 'STILL': return 'no arc (the still point: no direction)'
    return 'N > 0 (the positive arc)' if h in ('SEVENTH', 'AXIS +') else 'N < 0 (the golden arc, A(2,1,1))'


def half_of_position(i):
    return 'SEVENTH' if N(canonical_positions()[i % 24]) in SEVENTH else 'MANIFEST'


def reading(domain):
    x = cr.navigate(domain)
    a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    s = (r1 % 9, r2 % 9)
    stratum, half, loop = classify(s)
    nxt = classify(T(s))[1]; sq = classify(T(T(s)))[1]
    L = ['======= MANIFESTATION PHASE (M312) =======',
         'QUESTION VERBATIM: %s' % ' '.join(domain.split('\n')),
         'STATE: (%d, %d) on %s | STRATUM: %s | NORM: %d | HALF: %s' % (s[0], s[1], loop or 'the still point', stratum, N(s), half),
         'UNDER THE LAW: one step T -> %s (orientation reversed) | the square T^2 -> %s (kept)' % (nxt, sq),
         'ARC (PG-05): the least lift lies on %s; T carries it to the other arc, T^2 keeps it' % arc(s) if s != (0, 0) else 'ARC (PG-05): %s' % arc(s),
         'MODE (FP-VoiceCosets, FP-CoreField): %s' % mode(s),
         'NESTING (FP-CoreRecursion): %s' % nesting(s),
         'CANONICAL PHASES: anchor P%d %s | ' % (a, half_of_position(a)) +
         ' | '.join('%s P%d %s' % (n, (a + o) % 24, half_of_position(a + o)) for n, o in ARMS),
         'READING: CDT-A values; the halves are read as the 1/7 and 6/7 of Antipodal Phase Projection (FRAME-INTERPRETIVE, L-492). What they mean is the Striker\'s to judge.',
         '======= END MANIFESTATION PHASE =======']
    return '\n'.join(L)


def atlas_census(name, rows):
    """Phase census of a frozen atlas, with the exact chance: the strike's state is uniform over the 81 states
    when r1 and r2 run over 1..9, so P(core) = 8/81, P(still point) = 1/81, P(each half) = 36/81."""
    from math import comb
    L = ['=== %s (%d statements) ===' % (name, len(rows))]
    cnt = {'SEVENTH': 0, 'MANIFEST': 0, 'AXIS': 0, 'STILL': 0}
    for tag, text in rows:
        x = cr.navigate(text); a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
        st = (r1 % 9, r2 % 9); stratum, half, loop = classify(st)
        key = half.split()[0]; cnt[key] += 1
        L.append('  %-12s | %-52s | state %-7s | %s' % (tag, text[:52], '(%d, %d)' % st, half))
    n = len(rows)
    tail = lambda k, p: sum(comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))
    L.append('  CENSUS: SEVENTH %d | MANIFEST %d | AXIS %d | STILL %d' % (cnt['SEVENTH'], cnt['MANIFEST'], cnt['AXIS'], cnt['STILL']))
    L.append('  CHANCE: P(AXIS >= %d) = %.3f (p = 8/81 each) | P(SEVENTH >= %d) = %.3f | P(MANIFEST >= %d) = %.3f (p = 36/81 each)'
             % (cnt['AXIS'], tail(cnt['AXIS'], 8 / 81), cnt['SEVENTH'], tail(cnt['SEVENTH'], 36 / 81), cnt['MANIFEST'], tail(cnt['MANIFEST'], 36 / 81)))
    return '\n'.join(L)


def atlases():
    import bashar_lens as bl, framework_compare as fc
    out = ['MANIFESTATION PHASE (M312) OF THE FROZEN LENS ATLASES -- census after the freeze; CDT-A values, exact chance',
           atlas_census('BASHAR', [(t, x) for t, x, g in bl.ATLAS])]
    root = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'records', 'frameworks')
    for f in ('seth.txt', 'ra.txt', 'christian.txt', 'islamic.txt', 'hindu.txt', 'buddhist.txt', 'jewish.txt', 'neoplatonic.txt', 'stoic.txt', 'spinozist.txt', 'taoist.txt', 'leibnizian.txt', 'pythagorean.txt', 'heraclitean.txt', 'kauffman.txt', 'penrose.txt', 'wolfram.txt', 'barbour.txt', 'hofstadter.txt', 'hoffman.txt', 'kastrup.txt'):
        name, rows = fc.load(os.path.join(root, f)); out.append(atlas_census(name, rows))
    return '\n'.join(out)


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-70s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    S = [(i, j) for i in range(9) for j in range(9)]
    cnt = {}
    for s in S: cnt[classify(s)[0]] = cnt.get(classify(s)[0], 0) + 1
    check('strata are 72 | 8 | 1', cnt == {'UNIT': 72, 'CORE': 8, 'STILL POINT': 1})
    check('T flips the half on every unit and core state', all(classify(T(s))[1] != classify(s)[1] for s in S if s != (0, 0)))
    check('T^2 keeps the half on every state', all(classify(T(T(s)))[1] == classify(s)[1] for s in S))
    check('Yang is always in the opposite half, the other arms in the same', all(half_of_position(i) != half_of_position(i + 5) and all(half_of_position(i) == half_of_position(i + k) for k in (18, 8, 12)) for i in range(24)))
    r = reading('What is the Human Condition?')
    check('Human Condition: state (6, 0) on the core, AXIS', 'STATE: (6, 0)' in r and 'STRATUM: CORE' in r and 'HALF: AXIS' in r)
    r = reading('Explore the golden ratio connection')
    check('golden ratio: state (2, 5), canonical voice, MANIFEST half', 'STATE: (2, 5)' in r and 'HALF: MANIFEST' in r)
    best = {}
    for a in range(-40, 41):
        for b in range(-40, 41):
            n = a * a + a * b - b * b; k = (a % 9, b % 9)
            if k not in best or abs(n) < abs(best[k]): best[k] = n
    check('PG-05: the half is the real sign of the least lift on all 80 nonzero states', all((best[k] > 0) == arc(k).startswith('N > 0') for k in S if k != (0, 0)))
    check('MODE: doubling turns every unit through the three voices and returns', all(
        len({VOICE[N(((k * a) % 9, (k * b) % 9))] for k in (1, 2, 4)}) == 3 for a, b in S if N((a, b)) % 3))
    check('MODE: every core state is nilpotent', all((a * a + b * b) % 9 == 0 and (2 * a * b + b * b) % 9 == 0 for a, b in S if N((a, b)) % 3 == 0))
    check('deterministic', reading('What is time?') == reading('What is time?'))
    loop = [1]; [loop.append(loop[-1] * 2 % 9) for _ in range(5)]
    check('the halves are the two halves of the Torsion Loop under doubling', set(loop[:3]) == SEVENTH and set(loop[3:]) == MANIFEST)
    check('the state is uniform over the 81 states for r1, r2 in 1..9', len({(a % 9, b % 9) for a in range(1, 10) for b in range(1, 10)}) == 81)
    check('NESTING: (6, 0) is 3 x (2, 0), the family one scale down; a unit stands in the ground one scale up', 'Z[phi]/3' in nesting((6, 0)) and '(2, 0)' in nesting((6, 0)) and 'ground' in nesting((1, 4)))
    print('M312 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--atlases':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); print(atlases()); sys.exit(0)
    print(reading(' '.join(a)))
