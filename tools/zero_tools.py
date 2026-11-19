#!/usr/bin/env python3
"""zero_tools.py -- the zero instruments of Core Part 3.30 and the FB-8 and FB-9 scans of M243a.

  M283 Display Invariance Check: flags arithmetic claims about orbit values that hold only in the display 1 to 9
       (the class 0 written 9), not in the residues -- for example "9 is the highest value".
  M284 Octave Index: writes each count as n = r + 9k (r in 1..9) and reports k, the magnitude the digital root
       forgets; two domains with the same r and different k share an address (L8) at different octaves.
  M285 Cyclic Completion Score (ACS-c): 1 - d/4, d the cyclic distance between v_S and v_A on Z/9Z, reported beside
       the frozen ACS = 1 - |v_S - v_A|/8, with the chance level of each.
  FB-8 Aperture-state conflation (M243a): flags sentences that place the Striker, the judgment or the Aperture at a
       mathematical state -- zero, the ground, the still point, a position, the units, the Torsion Loop or the Crown.
  FB-9 Ring conflation (M243a): flags sentences that give the 81-state family the unit or nilpotent counts of the
       nine-element ring Z/9Z (6 units, 3 non-units) or give Z/9Z those of Z[phi]/9 (72 units, 9 non-units).
A flag is a candidate for review, not a verdict (L-420). The arithmetic is canonical_reference.py's, unchanged.

Usage:
    python3 tools/zero_tools.py --octave "DOMAIN" ["DOMAIN" ...]
    python3 tools/zero_tools.py --acs-c ANCHOR_INDEX ECHO_INDEX
    python3 tools/zero_tools.py --audit TEXT_FILE [...]
    python3 tools/zero_tools.py --selftest
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import canonical_reference as cr

def octave(n):
    """n = r + 9k with r in 1..9; the empty count n = 0 gives r = 9, k = -1."""
    r = 1 + (n - 1) % 9
    return r, (n - r) // 9

def octave_report(domains):
    L, rows = [], []
    for d in domains:
        x = cr.navigate(d)
        ks = [octave(x[k])[1] for k in ('n1', 'n2', 'n3')]
        rows.append((d, x['anchor'], ks))
        L.append('M284 OCTAVE INDEX: "%s" | n = (%d, %d, %d) | octave k = (%d, %d, %d) | anchor P%d (%s)%s' % (
            d, x['n1'], x['n2'], x['n3'], ks[0], ks[1], ks[2], x['anchor'], cr.POSITION_NAMES[x['anchor']],
            ' | NULL STRIKE (L-468)' if (x['n1'], x['n2'], x['n3']) == (0, 0, 0) else ''))
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            if rows[i][1] == rows[j][1] and rows[i][2] != rows[j][2]:
                L.append('  SHARED ADDRESS (L8): "%s" and "%s" -- anchor P%d at different octaves %s / %s' % (
                    rows[i][0], rows[j][0], rows[i][1], rows[i][2], rows[j][2]))
    return '\n'.join(L)

def cyc(a, b):
    return min((a - b) % 9, (b - a) % 9)

def acs_c(anchor_index, echo_index):
    v_a = cr.ORBIT[(anchor_index + 12) % 24]; v_s = cr.ORBIT[echo_index]
    return round(1 - cyc(v_s, v_a) / 4, 3), v_a, v_s

def acs_c_chance(anchor_index):
    v_a = cr.ORBIT[(anchor_index + 12) % 24]
    return round(sum(1 - cyc(cr.ORBIT[e], v_a) / 4 for e in range(1, 10)) / 9, 3)

def acs_c_block(a, e):
    s, va, vs = acs_c(a, e)
    lin, _, _ = cr.acs(a, e)
    return ('M285 CYCLIC COMPLETION SCORE: anchor P%d, echo P%d | v_A = %d, v_S = %d | cyclic d = %d\n'
            '  ACS-c = 1 - %d/4 = %.3f (chance %.3f) | ACS (frozen, linear) = %.3f (chance %.3f)' % (
            a, e, va, vs, cyc(vs, va), cyc(vs, va), s, acs_c_chance(a), lin, cr.acs_chance(a)))

DISPLAY = [r"\b(?:9|nine)\b[^.;]{0,40}\b(?:highest|largest|greatest|maximum|maximal|top|fullest|last|biggest)\b",
           r"\b(?:highest|largest|greatest|maximum|maximal|top|fullest|biggest)\s+(?:orbit\s+)?(?:value|digit|number)\b[^.;]{0,30}\b(?:9|nine)\b",
           r"\b(?:1|one)\b[^.;]{0,25}\b(?:farthest|furthest|most distant)\b[^.;]{0,25}\b(?:9|nine)\b",
           r"\bsums? to 117\b|\btotal(?:s|ling)? (?:of )?117\b"]
MAGNITUDE = r"\b(?:smooth(?:est|er|ness)?|curvature|squared (?:second )?differences|median|cent(?:er|re) of the (?:digit|value)s?|middle value|extreme values?)\b"
ORBITWORD = r"\b(?:orbits?|cycles?|voices?|values?|digits?|sequences?)\b"
INTRINSIC = r"\b(?:centred|centered|cyclic distance|residue|display)\b"
JUDGE = r"\b(?:Striker|Aperture|judg(?:e)?ment)\b"
GROUND = r"\b(?:zero|the ground|ground state|still point|fixed point|unmarked|P\d{1,2}|\(0, ?0\)|\{9, ?9\}|Torsion Loop|units?|Crown|nilpotents?|orbit value|state of the (?:cycle|family|arithmetic))\b"
LINK = r"\b(?:is|are|stands? at|sits? at|lies at|located at|carried by|resides? (?:at|in)|equals|=)\b"
NEG = r"\b(?:not|never|no|neither|nor|distinct from|apart from|versus|wrong|would be|mistaken)\b"

BIG = r"\b(?:81|eighty-one)\b|\bfamily\b|\b24-cycles?\b|Z\[(?:phi|\u03c6)\]"
SMALLCOUNT = r"\b(?:6|six) units\b|\b(?:2|two|3|three) nilpotents?\b"
BIGCOUNT = r"\b(?:72|seventy-two) units\b|\b(?:9|nine) nilpotents?\b"
SMALL = r"Z/9Z(?!\s*\[)(?![^.;]{0,40}(?:phi|\u03c6))|\bbase ring\b"

def ring_conflation(s):
    return bool((re.search(BIG, s, re.I) and re.search(SMALLCOUNT, s, re.I) and not re.search(SMALL, s, re.I) and not re.search(NEG, s, re.I))
                or (re.search(SMALL, s) and re.search(BIGCOUNT, s, re.I) and not re.search(BIG, s, re.I) and not re.search(NEG, s, re.I)))

def sentences(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def audit(text):
    disp, fb8 = [], []
    for s in sentences(text):
        if any(re.search(p, s, re.I) for p in DISPLAY): disp.append(s)
        elif re.search(MAGNITUDE, s, re.I) and re.search(ORBITWORD, s, re.I) and not re.search(INTRINSIC, s, re.I): disp.append(s)
        if re.search(JUDGE, s) and re.search(GROUND, s, re.I) and re.search(LINK, s, re.I) and not re.search(NEG, s, re.I):
            fb8.append(s)
    return disp, fb8

def selftest():
    ok = []
    def check(name, cond):
        ok.append(cond); print('%-64s %s' % (name, 'ok' if cond else 'FAIL'))
    check('octave: 9 -> (9, 0); 10 -> (1, 1); 18 -> (9, 1); 0 -> (9, -1)', [octave(n) for n in (9, 10, 18, 0)] == [(9, 0), (1, 1), (9, 1), (9, -1)])
    check('octave: n = r + 9k for n = 0..500', all(r + 9 * k == n and 1 <= r <= 9 for n in range(501) for r, k in [octave(n)]))
    check('null strike anchors at P9 with octave (-1, -1, -1)', 'P9 (Fixpoint)' in octave_report(['']) and '(-1, -1, -1)' in octave_report(['']))
    check('ACS-c known answer: anchor P7, echo P4 (v_A 9, v_S 1) = 0.750', acs_c(7, 4)[0] == 0.75)
    check('ACS-c identical values = 1.000; frozen ACS there = 0.000', acs_c(7, 7)[0] == 1.0 and cr.acs(7, 4)[0] == 0.0)
    check('ACS-c lies in [0, 1] for all 81 pairs', all(0 <= acs_c(a, e)[0] <= 1 for a in range(1, 10) for e in range(1, 10)))
    d, f = audit('Nine is the highest value on the cycle. The antipode completes the question.')
    check('M283 flags "nine is the highest value", passes a neutral sentence', len(d) == 1 and not f)
    d, f = audit('The Striker stands at zero, the still point. The Striker does not stand at zero.')
    check('FB-8 flags "the Striker stands at zero", passes its negation', len(f) == 1 and 'does not' not in f[0])
    d, f = audit('The 1/7 Aperture is carried by the Torsion Loop. A reading that says the Striker stands at zero would be wrong.')
    check('FB-8 flags the Aperture carried by the Torsion Loop, passes a warning', len(f) == 1 and 'Torsion' in f[0])
    r = [x for x in sentences('The 81-state family has 6 units and 3 nilpotents. The ring Z/9Z has 6 units; the 81-state ring Z[phi]/9 has 72 units.') if ring_conflation(x)]
    check('FB-9 flags six units given to the 81-state family, passes the correct pair', len(r) == 1 and '81-state family has 6' in r[0])
    r = [x for x in sentences('Z/9Z has 72 units. Z[phi]/9 has 72 units and 9 nilpotents.') if ring_conflation(x)]
    check('FB-9 flags 72 units given to Z/9Z, passes the extension ring', len(r) == 1 and r[0].startswith('Z/9Z has 72'))
    print('ZERO TOOLS SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--octave'] and len(a) > 1: print(octave_report(a[1:])); sys.exit(0)
    if a[:1] == ['--acs-c'] and len(a) == 3: print(acs_c_block(int(a[1]), int(a[2]))); sys.exit(0)
    if a[:1] == ['--audit'] and len(a) > 1:
        for p in a[1:]:
            d, f = audit(open(p, encoding='utf-8').read())
            print('M283 / FB-8 SCAN: %s | DISPLAY-DEPENDENT %d | APERTURE-STATE %d | %s' % (p, len(d), len(f), 'FLAGGED' if d or f else 'CLEAR'))
            for s in d: print('  M283  ' + s[:150])
            for s in f: print('  FB-8  ' + s[:150])
            for s in [x for x in sentences(open(p, encoding='utf-8').read()) if ring_conflation(x)]: print('  FB-9  ' + s[:150])
        sys.exit(0)
    print(__doc__); sys.exit(2)
