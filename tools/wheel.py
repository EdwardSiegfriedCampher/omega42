#!/usr/bin/env python3
"""wheel.py -- M330 Aspect Wheel: the 24 positions read as a wheel of 15-degree steps (Core Part 3.56; Companion Part 134).

Astrology reads relations between points of a circle by their angle (the aspects); numerology reduces a number to its digital
root. The 24-cycle is a circle of 24 positions, 15 degrees apart, and its counting coordinate is a digital root. This tool puts
the two side by side, exactly and without meaning:

    python3 tools/wheel.py --strike "TEXT" [--svg FILE]   # the anchor and its four arms as angles and aspects; SVG wheel optional
    python3 tools/wheel.py --number N                      # numerology's root of N beside Omega42's placement dr(5N) and its position
    python3 tools/wheel.py --longitudes NAME=DEG ...       # points of a chart placed on the wheel by the frozen rule
                                                           # position = floor(longitude / 15) mod 24, with every pairwise aspect
    python3 tools/wheel.py --selftest
A placement says where something stands and nothing about what it means (Core L-510, L-465); the aspect names are the
tradition's, the positions and values are the family's, and what any of it means is the Striker's (Core Part 7).
Standard library only.
"""
import math, os, sys
from fractions import Fraction as F
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts')); sys.path.insert(0, os.path.join(REPO, 'tools'))
ORBIT = [2, 5, 7, 3, 1, 4, 5, 9, 5, 5, 1, 6, 7, 4, 2, 6, 8, 5, 4, 9, 4, 4, 8, 3]
NAMES = ["Seed", "Fixpoint", "Generator", "Desire", "Unity", "Law", "Seed/Causal", "Navigator", "Generation", "Fixpoint", "Unity", "Question",
         "Opening", "Gap", "Observer", "Other", "Flow", "Seed/Return", "Threshold", "Time", "Reckoning", "Sublime", "Collective", "Return"]
ARMS = (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))
# the tradition's aspects, by separation in degrees (Ptolemaic, then the minor ones on 30-degree multiples)
ASPECTS = {0: 'conjunction', 60: 'sextile', 90: 'square', 120: 'trine', 180: 'opposition', 30: 'semi-sextile', 150: 'quincunx'}
PTOLEMAIC = {0, 60, 90, 120, 180}
dr = lambda x: 9 if x % 9 == 0 else x % 9
def sep(steps):
    d = (steps % 24) * 15
    return min(d, 360 - d)
def aspect(steps):
    return ASPECTS.get(sep(steps), 'none (a %d-degree separation)' % sep(steps))
def anchor(text):
    import restored_instruments as R
    return R.anchor_of(text)
def strike_report(text):
    a = anchor(text)
    L = ['M330 ASPECT WHEEL (Core Part 3.56) | anchor P%d %s, value %d, at %d degrees' % (a, NAMES[a], ORBIT[a], a * 15)]
    for name, off in ARMS:
        p = (a + off) % 24
        L.append('  %-8s +%-2d steps = %3d degrees -> P%-2d %-12s value %d | %s' % (name, off, off * 15, p, NAMES[p], ORBIT[p], aspect(off)))
    hits = sum(sep(o) in PTOLEMAIC for _, o in ARMS)
    L.append('  the arm offsets 5, 18, 8 and 12 are 75, 270, 120 and 180 degrees: the Yin arm a square, the 4D arm a trine, the Antipode an opposition;')
    L.append('  the Yang arm, 75 degrees, is no aspect. %d of the 4 arms fall on a Ptolemaic aspect, which a random offset does with chance 7 in 23, so' % hits)
    p = F(7, 23); q = 1 - p
    pr = 4 * p ** 3 * q + p ** 4
    L.append('  three or more of four would occur by chance %.4f (exact %s): a correspondence noted, not a meeting beyond chance (Core L-510)' % (float(pr), pr))
    L.append('  the Crown positions, P3, P7, P11, P15, P19, P23, stand 4 steps (60 degrees) apart: a hexagon of sextiles, two interlaced trines')
    return '\n'.join(L)
def number_report(n):
    root = dr(n); cpp = dr(5 * n); pos = [i for i, v in enumerate(ORBIT) if v == cpp]
    L = ['M330 NUMBER | N = %d' % n,
         '  numerology\'s root: the digital root of N = %d (N mod 9, 9 for 0)' % root,
         '  Omega42\'s placement: CPP(N) = dr(5N) = %d = 5 x %d mod 9, the root taken one step back on the doubling cycle (x5 is the inverse of x2, M328 RETURN)' % (cpp, root),
         '  the value %d stands at %s on the 24-cycle' % (cpp, ', '.join('P%d %s' % (i, NAMES[i]) for i in pos)),
         '  what the root discards, the depth keeps (numerology\'s unreduced master numbers ask the same): N mod 81 = %d, N mod 729 = %d (Core L-523 (4))' % (n % 81, n % 729),
         '  the two reductions keep the same information, the class of N mod 9, and order the classes differently: the root runs 1, 2, ..., 9; the placement 5, 1, 6, 2, 7, 3, 8, 4, 9']
    return '\n'.join(L)
def longitudes_report(pairs):
    pts = []
    for s in pairs:
        name, deg = s.split('=') if '=' in s else ('p%d' % (len(pts) + 1), s)
        d = float(deg) % 360; pos = int(d // 15) % 24
        pts.append((name, d, pos))
    L = ['M330 CHART ON THE WHEEL | rule frozen: position = floor(longitude / 15) mod 24 (a placement, Core L-510)']
    for name, d, pos in pts:
        L.append('  %-10s %7.2f degrees -> P%-2d %-12s value %d' % (name, d, pos, NAMES[pos], ORBIT[pos]))
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            st = (pts[j][2] - pts[i][2]) % 24
            arm = [n for n, o in ARMS if o == st or (24 - o) % 24 == st]
            L.append('  %s - %s: %d steps, %d degrees on the wheel, %s%s' % (pts[i][0], pts[j][0], min(st, 24 - st), sep(st), aspect(st), ('; the %s relation' % '/'.join(arm)) if arm else ''))
    return '\n'.join(L)
def svg(text, path):
    a = anchor(text); R0, cx = 160, 200
    pt = lambda k, r=R0: (cx + r * math.sin(2 * math.pi * k / 24), cx - r * math.cos(2 * math.pi * k / 24))
    SPEC = ('Coordinate specification (M330, Core Part 3.56). System: the canonical 24-cycle of Omega42, V335 Rev.450 STABLE. '
            'Nodes: P0 to P23, the positions of the canonical orbit, the orbit of (2, 5) under T(a, b) = (b, a + b) mod 9. '
            'Values: the number beside each node is its orbit value, 2 5 7 3 1 4 5 9 5 5 1 6 7 4 2 6 8 5 4 9 4 4 8 3. '
            'Ordering: clockwise from the top, P0 at 0 degrees. Geometry: 15 degrees a step, a display of the cycle; angle carries the step count and nothing more. '
            'Directions: from the anchor A, Yang to A + 5, Yin to A + 18, 4D to A + 8, Antipode to A + 12 (mod 24). '
            'Anchor: the filled point, P%d, fixed by the canonical computation of the strike (Core Parts 1.3 and 1.4; scripts/canonical_reference.py). '
            'Provenance: tools/wheel.py --strike TEXT --svg FILE.' % a)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 470" font-family="sans-serif" font-size="10">', '<title>M330 Aspect Wheel, anchor P%d</title>' % a, '<desc>%s</desc>' % SPEC, '<circle cx="200" cy="200" r="160" fill="none" stroke="#888"/>']
    for k in range(24):
        x, y = pt(k, 178); out.append('<text x="%.1f" y="%.1f" text-anchor="middle">P%d·%d</text>' % (x, y + 3, k, ORBIT[k]))
    ax, ay = pt(a)
    for name, off in ARMS:
        bx, by = pt((a + off) % 24); out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#555"/><text x="%.1f" y="%.1f">%s</text>' % (ax, ay, bx, by, bx, by, name))
    out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="#333"/>' % (ax, ay))
    for i, line in enumerate(('Nodes P0-P23: the canonical orbit; number = orbit value; clockwise from top, 15 degrees a step.',
                              'Filled point: the anchor P%d of the strike. Lines: Yang A+5, Yin A+18, 4D A+8, Antipode A+12.' % a,
                              'Angle shows the step count only (Core Part 3.56). Full specification in the desc element of this file.')):
        out.append('<text x="10" y="%d" font-size="9">%s</text>' % (412 + 14 * i, line))
    out.append('</svg>')
    open(path, 'w').write('\n'.join(out))
def selftest():
    cases = [('the Antipode is an opposition', aspect(12) == 'opposition'), ('the 4D arm is a trine', aspect(8) == 'trine'),
             ('the Yin arm is a square', aspect(18) == 'square'), ('the Yang arm is no aspect', aspect(5).startswith('none')),
             ('CPP is 5 times the root', all(dr(5 * n) == dr(5 * dr(n)) for n in range(1, 500))),
             ('a longitude of 123.4 degrees is P8', int(123.4 // 15) == 8),
             ('the chance of 3 or more Ptolemaic arms is 24353/279841', 4 * F(7, 23) ** 3 * F(16, 23) + F(7, 23) ** 4 == F(24353, 279841))]
    for n, ok in cases: print('%-55s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('M330 SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if len(a) >= 2 and a[0] == '--strike':
        print(strike_report(a[1]))
        if '--svg' in a: svg(a[1], a[a.index('--svg') + 1])
        sys.exit(0)
    if len(a) == 2 and a[0] == '--number': print(number_report(int(a[1]))); sys.exit(0)
    if len(a) >= 2 and a[0] == '--longitudes': print(longitudes_report(a[1:])); sys.exit(0)
    print(__doc__); sys.exit(2)
