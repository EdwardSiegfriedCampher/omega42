#!/usr/bin/env python3
"""resonance.py -- M319 Resonance Profile (Core Part 3.45, L-514; Companion Part 80).

How closely an object or idea resonates with Omega42 is two questions, not one, and the Profile answers them side
by side, never combined (L-486, L-514):

  COHERENCE  how well the idea fits the frame -- JUDGED, CDT-C, by a named number of judges, NON-BLIND unless stated:
             FEATURES  the six features of the frame (records/frameworks/philosophy_selection.txt), each 1, 0.5 or 0,
                       shown as a strip of six cells and as a share of 6, with its STATUS (A PRIORI, scored before
                       anything was struck; ADDENDUM, after the fact; RETROACTIVE, after the computed layer)
             ROLES     the share of the five M309 roles filled          } reported apart, never summed (APE-139)
             RELATIONS the share of the four M309 relations that hold   }
             TENSIONS  the places the correspondence pulls against itself (records/frameworks/tensions.txt)
             JUDGES    how many judges scored it; agreement is measured with --agreement once a second judge has
                       scored the same features blind (M300) -- until then ACCURACY: ONE JUDGE, NOT MEASURED
  CONGRUENCE how much the idea's own frozen statements meet the structure -- COMPUTED, CDT-A, with its chance:
             K         the CONGRUENCE PERCENTILE: the share of random atlases with the same word counts (each r1
                       held at its count, r2 and r3 drawn; E13) whose meeting score is below the atlas's own, ties
                       counting half. The meeting score sums, in standard units of that same null, the four
                       measures in which statements meet the cycle -- HOME (on the canonical cycle), SEEDS (on an
                       orbit's seed), LINKS (one resting where another stands), MIRRORS (twelve steps apart). K = 0.5
                       is chance; K near 1 is more meeting than chance, near 0 less. The uniform K is printed beside.
             BAND      ABOVE CHANCE at K >= 0.95, BELOW CHANCE at K <= 0.05, otherwise AT CHANCE -- and with N
                       atlases about N/20 fall above 0.95 by chance alone, so a band is read in its family.
  AT A GLANCE the card (one per idea) and the MAP: features share across, K up, each idea a letter; the two axes are
             never multiplied, added or turned into a distance, and the corner of the map is not a verdict.

Objects. An object enters when it has a frozen statement atlas or a counted representation; its coherence column
then carries its Correspondence Depth (Core Part 0.14.5, M230) in place of the features, and its congruence the same
K. Every value is printed with the record it comes from.

THE ONE FIGURE (L-514 as amended 22 October 2026, at the Originator's decision on E14). The profile is presented first
as one number, PROXIMITY: how many times its chance an idea's own statements meet the structure (an object: how many
times its frozen look-alikes it scores); 1.00 is chance. It is the congruence answer stated plainly, and it says so.
Everything else -- fit, reading integrity, placement, robustness, provenance -- is shown when the Striker asks.

Usage:
    python3 tools/resonance.py                     # the one figure for every idea and object (records/resonance/proximity.txt)
    python3 tools/resonance.py --detail             # the rest: every card, the map, the family lines (records/resonance/profiles.txt)
    python3 tools/resonance.py --detail NAME        # one card in full (also --card NAME)
    python3 tools/resonance.py --map                # the map alone
    python3 tools/resonance.py --atlas FILE         # the congruence of any frozen atlas (an object or idea not yet registered)
    python3 tools/resonance.py --agreement A.txt B.txt   # two judges' feature tables: agreement and weighted kappa
    python3 tools/resonance.py --selftest
Standard library and the tools beside this file.
"""
import os, re, sys, random, statistics
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import framework_compare as fc
import bashar_lens as bl

FW = os.path.join(ROOT, 'records', 'frameworks')
PHI = 'records/frameworks/philosophy_selection.txt'; PHA = 'records/frameworks/philosophy_selection_addendum.txt'
CON = 'records/frameworks/contemporary_selection.txt'; RET = 'records/resonance/features_retroactive.txt'
MEET = ('HOME', 'SEEDS', 'LINKS', 'MIRRORS')
TRIALS = 20000
# name, code on the map, atlas (None: the Bashar atlas of M308), feature record, row prefix, status, navigation
IDEAS = [
    ('Christian', 'CH', 'christian.txt', RET, 'Christian', 'RETROACTIVE', 'NAV-2026-0011'),
    ('Islamic', 'IS', 'islamic.txt', RET, 'Islamic', 'RETROACTIVE', 'NAV-2026-0012'),
    ('Hindu', 'HI', 'hindu.txt', RET, 'Hindu', 'RETROACTIVE', 'NAV-2026-0013'),
    ('Buddhist', 'BU', 'buddhist.txt', RET, 'Buddhist', 'RETROACTIVE', 'NAV-2026-0014'),
    ('Jewish', 'JE', 'jewish.txt', RET, 'Jewish', 'RETROACTIVE', 'NAV-2026-0015'),
    ('Neoplatonic', 'NE', 'neoplatonic.txt', PHI, 'Neoplatonism', 'A PRIORI', 'NAV-2026-0016'),
    ('Stoic', 'ST', 'stoic.txt', PHI, 'Stoicism', 'A PRIORI', 'NAV-2026-0017'),
    ('Spinozist', 'SP', 'spinozist.txt', PHI, 'Spinozism', 'A PRIORI', 'NAV-2026-0018'),
    ('Taoist', 'TA', 'taoist.txt', PHI, 'Philosophical Taoism', 'A PRIORI', 'NAV-2026-0019'),
    ('Leibnizian', 'LE', 'leibnizian.txt', PHI, 'Leibniz', 'A PRIORI', 'NAV-2026-0020'),
    ('Pythagorean', 'PY', 'pythagorean.txt', PHI, 'Pythagoreanism', 'A PRIORI', 'NAV-2026-0021'),
    ('Heraclitean', 'HE', 'heraclitean.txt', PHI, 'Heraclitus', 'A PRIORI', 'NAV-2026-0022'),
    ('Kauffman', 'KA', 'kauffman.txt', CON, 'Louis H. Kauffman', 'A PRIORI', 'NAV-2026-0023'),
    ('Penrose', 'PE', 'penrose.txt', CON, 'Roger Penrose', 'A PRIORI', 'NAV-2026-0024'),
    ('Wolfram', 'WO', 'wolfram.txt', CON, 'Stephen Wolfram', 'A PRIORI', 'NAV-2026-0025'),
    ('Barbour', 'BA', 'barbour.txt', CON, 'Julian Barbour', 'A PRIORI', 'NAV-2026-0026'),
    ('Hofstadter', 'HO', 'hofstadter.txt', CON, 'Douglas Hofstadter', 'A PRIORI', 'NAV-2026-0027'),
    ('Hoffman', 'HF', 'hoffman.txt', RET, 'Donald Hoffman', 'RETROACTIVE', None),
    ('Kastrup', 'KS', 'kastrup.txt', RET, 'Bernardo Kastrup', 'RETROACTIVE', None),
    ('Bashar', 'BS', None, RET, 'Bashar', 'RETROACTIVE', None),
    ('Seth', 'SE', 'seth.txt', RET, 'Seth', 'RETROACTIVE', None),
    ('Ra', 'RA', 'ra.txt', RET, 'Ra', 'RETROACTIVE', None),
]
CELL = {1.0: '●', 0.5: '◐', 0.0: '○'}


def features(path, prefix):
    """The six scores of a candidate, read from its frozen record (the row whose name begins with the prefix)."""
    for line in open(os.path.join(ROOT, path), encoding='utf-8'):
        if line.startswith('#') or '|' not in line: continue
        cells = [c.strip() for c in line.split('|')]
        name = cells[0]
        if name == prefix or name.startswith(prefix + ' ') or name.startswith(prefix + ' ('):
            try: return [float(c) for c in cells[1:7]]
            except ValueError: return None
    return None


def coherence_of_nav(nav):
    """ROLES and RELATIONS as the navigation records them: apart (APE-139), or recovered from an averaged SCORE."""
    if not nav: return None, None
    t = open(os.path.join(ROOT, 'submissions', 'navigations', nav + '.txt'), encoding='utf-8').read()
    m = re.search(r'ROLES ([01]\.\d+) and RELATIONS ([01]\.\d+)', t)
    if m: return float(m.group(1)), float(m.group(2))
    m = re.search(r'SCORE = \(([01]\.\d+) \+ ([01]\.\d+)\) / 2', t)
    if m: return float(m.group(1)), float(m.group(2))
    return None, None


def tensions_of(nav):
    if not nav: return None
    for line in open(os.path.join(FW, 'tensions.txt'), encoding='utf-8'):
        if line.startswith(nav + ' |'):
            m = re.search(r'TENSIONS (\d+)', line)
            return int(m.group(1)) if m else None
    return None


def objects_block():
    """The object cards (APE-143's panel, merged): placement, depth, PROXIMITY, Margin and times its look-alikes."""
    panels = object_proximity()
    L = ['OBJECTS (the Resonance Ledger, first pass; records/resonance/objects.txt): PROXIMITY | 1 PLACEMENT | 4 CONGRUENCE: DEPTH, MARGIN against a frozen class of look-alikes, TIMES ITS LOOK-ALIKES | 2 READING INTEGRITY: NOT APPLICABLE (no reading)']
    for line in open(os.path.join(ROOT, 'records', 'resonance', 'objects.txt'), encoding='utf-8'):
        if line.startswith('#') or line.startswith('OBJECT') or '|' not in line: continue
        o, pl, d, pn = [x.strip() for x in line.split('|')]
        key = pn.split(' (')[0]
        if key in panels and ' (' not in pn:
            P = panels[key]
            mar = 'PROXIMITY %d | MARGIN %s, p %s, %s, against %d look-alikes (%s) | TIMES ITS LOOK-ALIKES %.2f' % (prox_figure(P['share']), P['M'], P['p'], P['band'], P['n'], key, P['ratio'])
        elif key in panels:
            mar = 'a look-alike of %s in %s (%s)' % (panels[key]['obj'], key, pn.split(' (', 1)[1].rstrip(')'))
        else:
            mar = 'PROXIMITY PENDING (no class of look-alikes frozen)'
        L.append('  %-44s %s -- depth 1, NOT A FINDING | DEPTH %s | %s' % (o, pl, d, mar))
    p1 = panels.get('PANEL 1')
    if p1: L.append('  the 24-cell against the five regular 4-polytopes alone (PANEL 1): MARGIN %s, p %s, %s -- superseded by PANEL 3, whose class is large enough to judge it' % (p1['M'], p1['p'], p1['band']))
    L.append('  CALIBRATION (records/resonance/calibration.txt): 24-tone equal temperament returns Margin 0 as M230-E requires; the 24-cell outscores all 46 distinct Wythoffian uniform 4-polytopes (M 0.620, p 0.021, DISCRIMINATING); no uniform 4-polytope carries the signature of T itself')
    return L


def placement_of(nav):
    """Row 1, PLACEMENT: the navigation's coordinate -- depth 1, universal, never a finding."""
    if not nav: return None
    t = open(os.path.join(ROOT, 'submissions', 'navigations', nav + '.txt'), encoding='utf-8').read()
    m = re.search(r'n = \((\d+), (\d+), (\d+)\) \| r = \((\d), (\d), (\d)\) \| ANCHOR P(\d+)', t)
    st = re.search(r'state \((\d), (\d)\) on (Voice [ABC]|the Wheel|Wheel|[A-Za-z ]+?), norm', t)
    return dict(n=tuple(int(x) for x in m.group(1, 2, 3)), anchor=int(m.group(7)), state=(int(st.group(1)), int(st.group(2))) if st else None) if m else None


def integrity_of(nav):
    """Row 2, READING INTEGRITY (APE-141, APE-142, APE-143): the checks a reading must pass, recomputed now --
    the five fields of its M310 COHERENCE line, the M301 format check and the M224-A audit. Counts, never weights."""
    if not nav: return None
    path = os.path.join(ROOT, 'submissions', 'navigations', nav + '.txt'); t = open(path, encoding='utf-8').read()
    m = re.search(r'^COHERENCE: (.*)$', t, re.M)
    fields = [f.strip() for f in m.group(1).split('|')] if m else []
    coh = sum(1 for f in fields if re.search(r'\b(PASS|CLEAR)\b', f))
    import format_check as fmt
    res = fmt.check(t); fails = sum(1 for r in res if r[0] == 'FAIL')
    import subprocess
    a = subprocess.run([sys.executable, os.path.join(ROOT, 'scripts', 'm193_m225.py'), os.path.join(ROOT, 'scripts', 'canonical_reference.py'), '--audit', path], capture_output=True, text=True).stdout
    am = re.search(r'FAILURES: (\d+) \| RESULT: (\w+)', a); n_audit = len(re.findall(r'^\s*\[(PASS|FAIL)\]', a, re.M))
    return dict(coh=coh, coh_n=len(fields), fmt=len(res) - fails, fmt_n=len(res), audit=(n_audit - int(am.group(1))) if am else 0, audit_n=n_audit)


def proximity(sigs, trials=TRIALS, seed=319):
    """TIMES CHANCE, shown in the detail: the meetings counted (HOME, SEEDS, LINKS, MIRRORS) over the meetings expected
    at the same word counts (E13); 1.00 is chance. Returns (figure, lower, upper), the bounds being the 5th and 95th
    percentiles of the same figure for the chance atlases themselves. Its chance range differs from atlas to atlas,
    which is why it is not the one figure: PROXIMITY is (Companion Part 83)."""
    null = _null(sigs, True, trials, seed); obs = fc.measures(sigs)
    exp = sum(statistics.fmean(n[k] for n in null) for k in MEET)
    if exp <= 0: return None, None, None
    got = sum(obs[k] for k in MEET); vals = sorted(sum(n[k] for k in MEET) / exp for n in null)
    return got / exp, vals[int(0.05 * len(vals))], vals[int(0.95 * len(vals)) - 1]


def prox_figure(K):
    """PROXIMITY, the one figure (L-514 as amended 22 October 2026; E14 as adopted): out of 100 chance look-alikes,
    how many the idea or object is closer to Omega42's structure than -- 50 is chance, 100 closer than every one,
    0 farther than every one. For an idea it is 100 K (random atlases with the same word counts); for an object, its
    share of frozen look-alikes it outscores, ties counting half. One scale for every idea and every object."""
    return int(round(100 * K))


def object_proximity():
    """An object's figures: its PROXIMITY (the share of its frozen look-alikes it outscores, ties half) and its score
    over the mean of theirs (TIMES ITS LOOK-ALIKES, in the detail), read from records/resonance/polytopes_output.txt.
    Panels 1 and 2 list every member; Panel 3 lists its nulls by score ("nulls at s = x: n")."""
    text = open(os.path.join(ROOT, 'records', 'resonance', 'polytopes_output.txt'), encoding='utf-8').read()
    res = {}
    for block in re.split(r'^(?==== PANEL)', text, flags=re.M):
        h = re.match(r'=== (PANEL \d+)', block)
        if not h: continue
        sc = [(m.group(1).strip(), float(m.group(2))) for m in re.finditer(r'^  (\S.*?)\s+C24 .*?s = ([0-9.]+)\s*$', block, re.M)]
        obj, s_obj = sc[0]
        grouped = [(float(a), int(n)) for a, n in re.findall(r'^  nulls at s = ([0-9.]+): (\d+)', block, re.M)]
        nulls = [x for x, n in grouped for _ in range(n)] if grouped else [x for _, x in sc[1:]]
        mean = sum(nulls) / len(nulls)
        share = (sum(1 for x in nulls if x < s_obj) + 0.5 * sum(1 for x in nulls if x == s_obj)) / len(nulls)
        mm = re.search(r'MARGIN M = ([-0-9.]+|NONE) \| p = ([0-9.]+) .*?\| (DISCRIMINATING|NONDISCRIMINATING|NEGATIVE|UNDERPOWERED|PENDING)', block)
        res[h.group(1)] = dict(obj=obj, ratio=s_obj / mean if mean > 0 else None, s=s_obj, mean=mean, n=len(nulls), members=sc, share=share,
                               M=mm.group(1), p=mm.group(2), band=mm.group(3))
    return res


def jackknife(sigs, trials=4000):
    """The statement jackknife (APE-141, control 3): K recomputed with each statement left out in turn, on its own
    conditioned null; the range shows how much K rests on any one statement."""
    ks = [percentile(sigs[:i] + sigs[i + 1:], True, trials, seed=319 + i)[0] for i in range(len(sigs))] if len(sigs) > 2 else []
    return (min(ks), max(ks)) if ks else None


def rows_of(atlas):
    if atlas is None: return [(r[0], r[1]) for r in bl.ATLAS]
    return fc.load(os.path.join(FW, atlas))[1]


def meeting(m, mu, sd):
    return sum((m[k] - mu[k]) / sd[k] for k in MEET if sd[k] > 0)


def _null(sigs, conditioned, trials, seed):
    rng = random.Random(seed + len(sigs) + (1000 if conditioned else 0))
    pool = fc.pool(); by = {}
    for s in pool: by.setdefault(s['r1'], []).append(s)
    draw = (lambda: [rng.choice(by[s['r1']]) for s in sigs]) if conditioned else (lambda: [rng.choice(pool) for _ in sigs])
    return [fc.measures(draw()) for _ in range(trials)]


def _K(obs, null, keys):
    mu = {k: statistics.fmean(n[k] for n in null) for k in keys}
    sd = {k: statistics.pstdev([n[k] for n in null]) for k in keys}
    f = lambda m: sum((m[k] - mu[k]) / sd[k] for k in keys if sd[k] > 0)
    a = f(obs); vals = [f(n) for n in null]
    below = sum(1 for v in vals if v < a - 1e-12); tie = sum(1 for v in vals if abs(v - a) <= 1e-12)
    return (below + 0.5 * tie) / len(null)


def percentile(sigs, conditioned=True, trials=TRIALS, seed=319, loo=False):
    """K: the share of null atlases of the same size (and, conditioned, the same r1 for every statement) whose
    meeting score falls below the atlas's own, ties half. Returns (K, Monte Carlo standard error), and with
    loo=True also the range of K over the four leave-one-measure-out scores, computed on the same null sample."""
    null = _null(sigs, conditioned, trials, seed); obs = fc.measures(sigs)
    K = _K(obs, null, MEET); se = (K * (1 - K) / trials) ** 0.5
    if not loo: return K, se
    ks = [_K(obs, null, tuple(k for k in MEET if k != out)) for out in MEET]
    return K, se, (min(ks), max(ks))


def band(K):
    return 'ABOVE CHANCE' if K >= 0.95 else ('BELOW CHANCE' if K <= 0.05 else 'AT CHANCE')


def bar(K, width=20):
    i = min(width - 1, int(K * width)); cells = ['-'] * width
    cells[width // 2] = '|'; cells[i] = '#'
    return '[' + ''.join(cells) + ']'


def profile(idea, trials=TRIALS):
    name, code, atlas, src, prefix, status, nav = idea
    f = features(src, prefix)
    roles, rel = coherence_of_nav(nav)
    sigs = [fc.strike(t) for _, t in rows_of(atlas)]
    Kc, ec, rng = percentile(sigs, True, trials, loo=True); Ku, eu = percentile(sigs, False, trials)
    m = fc.measures(sigs)
    jk = jackknife(sigs, max(1000, trials // 5))
    prox = proximity(sigs, trials)
    return dict(prox=prox, placement=placement_of(nav), integrity=integrity_of(nav), jack=jk, independence='C' if nav else '-', name=name, code=code, atlas=atlas or 'tools/bashar_lens.py (the M308 atlas)', source=src, status=status, nav=nav,
                features=f, fshare=(sum(f) / 6 if f else None), roles=roles, relations=rel, tensions=tensions_of(nav),
                K=Kc, Kse=ec, Kloo=rng, Ku=Ku, Kuse=eu, n=len(sigs), meet={k: m[k] for k in MEET},
                paraphrase=bool(atlas) and 'paraphrased by the Navigator' in open(os.path.join(FW, atlas), encoding='utf-8').readline())


def card(p):
    f = p['features']
    strip = ''.join(CELL[x] for x in f) if f else 'NOT SCORED'
    coh = 'FEATURES %s %s/6 (%.2f) %s' % (strip, ('%g' % sum(f)) if f else '-', p['fshare'] or 0, p['status'])
    coh += ' | ROLES %s [RETIRED as a measure: control texts reach 1.00, avenue 2] | RELATIONS %s | TENSIONS %s' % (('%.2f' % p['roles']) if p['roles'] is not None else 'NOT RECORDED',
                                                       ('%.3g' % p['relations']) if p['relations'] is not None else 'NOT RECORDED',
                                                       p['tensions'] if p['tensions'] is not None else 'NOT RECORDED')
    con = 'K %.3f +/- %.3f given word counts %s %s | leave one measure out %.2f to %.2f%s | uniform K %.3f | HOME %d SEEDS %d LINKS %d MIRRORS %d of %d statements%s' % (
        p['K'], p['Kse'], bar(p['K']), band(p['K']), p['Kloo'][0], p['Kloo'][1], '' if band(p['Kloo'][0]) == band(p['Kloo'][1]) == band(p['K']) else ' (BAND NOT ROBUST)', p['Ku'], p['meet']['HOME'], p['meet']['SEEDS'], p['meet']['LINKS'], p['meet']['MIRRORS'], p['n'],
        ' | ATLAS PARAPHRASED' if p['paraphrase'] else '')
    pl = p['placement']; ri = p['integrity']
    place = ('P%d, state %s, n = %s -- depth 1, universal, NOT A FINDING' % (pl['anchor'], pl['state'], pl['n'])) if pl else 'NONE (no navigation; the atlas alone is profiled)'
    integ = ('M310 %d of %d | format %d of %d | audit %d of %d -- %d of %d checks evaluated, recomputed now' % (ri['coh'], ri['coh_n'], ri['fmt'], ri['fmt_n'], ri['audit'], ri['audit_n'],
             ri['coh'] + ri['fmt'] + ri['audit'], ri['coh_n'] + ri['fmt_n'] + ri['audit_n'])) if ri else 'NOT APPLICABLE (no reading)'
    jk = (' | one statement left out %.2f to %.2f%s' % (p['jack'][0], p['jack'][1], '' if band(p['jack'][0]) == band(p['jack'][1]) == band(p['K']) else ' (BAND NOT ROBUST)')) if p['jack'] else ''
    glance = 'GLANCE %s | RI %s | FIT %s%s | K %.3f %s | IND %s | J1' % ('P%d' % pl['anchor'] if pl else '--', ('%d/%d' % (ri['coh'] + ri['fmt'] + ri['audit'], ri['coh_n'] + ri['fmt_n'] + ri['audit_n'])) if ri else '--',
             ('%.2f' % p['fshare']) if p['fshare'] is not None else '--', (' (R %.2f, L %.3g, T %s)' % (p['roles'], p['relations'], p['tensions'])) if p['roles'] is not None else '', p['K'], band(p['K']), p['independence'])
    px = p['prox']
    return '\n'.join(['%-12s [%s] %s' % (p['name'].upper(), p['code'], p['nav'] or 'lens only (no navigation)'),
                      '  PROXIMITY %d -- closer to the structure than %d in 100 chance atlases with the same word counts (50 is chance); the one figure, congruence; the rows below on request' % (prox_figure(p['K']), prox_figure(p['K'])),
                      '  CONTROL: thirteen bus-timetable sentences chosen for Voice C read PROXIMITY 100, and thirteen unselected ones 82 (avenue 3, records/avenues/adversarial_atlas_output.txt); not quoted as evidence before avenue 10',
                      '  TIMES CHANCE %.2f -- its statements meet the structure %.2f times as often as chance (a chance atlas of this size lies between %.2f and %.2f nine times in ten, so the same figure means more for one atlas than another)' % (px[0], px[0], px[1], px[2]),
                      '  ' + glance,
                      '  1 PLACEMENT: ' + place,
                      '  2 READING INTEGRITY (computed checks of the reading, counted, never weighted): ' + integ,
                      '  3 FIT (judged, CDT-C, 1 judge, NON-BLIND): ' + coh,
                      '  4 CONGRUENCE (computed, CDT-A): ' + con + jk,
                      '  5 PROVENANCE: atlas %s; roles %s; independence %s (B blind, S same Navigator, C contaminated, - none attempted); judges 1, agreement NOT MEASURED' % (
                          'PARAPHRASED by the Navigator' if p['paraphrase'] else 'QUOTED from the sources its first line names', 'frozen before the atlas was struck' if p['nav'] and p['nav'] >= 'NAV-2026-0016' else ('frozen RETROACTIVE' if p['nav'] else 'NONE'), p['independence']),
                      '  SOURCES: features %s; atlas records/frameworks/%s' % (p['source'], p['atlas']) if p['atlas'] and not p['atlas'].startswith('tools') else
                      '  SOURCES: features %s; atlas %s' % (p['source'], p['atlas'])])


def grid(ps):
    """The map: FEATURES share across (0 to 1), K up (1 at the top); the chance line K = 0.5 is marked."""
    W, H, C = 13, 11, 7
    cells = {}
    for p in ps:
        if p['fshare'] is None: continue
        x = round(p['fshare'] * (W - 1)); y = round((1 - p['K']) * (H - 1))
        cells.setdefault((y, x), []).append(p['code'])
    L = ['MAP (M319): FEATURES share across, CONGRUENCE PERCENTILE K up; two axes side by side, never combined (L-514)']
    for y in range(H):
        K = 1 - y / (H - 1)
        row = []
        for x in range(W):
            c = cells.get((y, x))
            row.append(('/'.join(c)).ljust(C) if c else ('  .'.ljust(C) if y != (H - 1) // 2 else '  -'.ljust(C)))
        L.append('%4.1f |%s%s' % (K, ''.join(row), '  <- chance (K = 0.5)' if y == (H - 1) // 2 else ''))
    L.append('     +' + '-' * C * W)
    L.append('      ' + ''.join(('%.2f' % (x / (W - 1))).ljust(C) for x in range(W)))
    L.append('      FEATURES share of 6 (coherence, judged) -- codes: ' + ', '.join('%s %s' % (p['code'], p['name']) for p in ps))
    return '\n'.join(L)


def headline(ps):
    """The one-figure view (L-514, E14): PROXIMITY for every idea and object, in the order of the register -- never
    sorted, never ranked; python3 tools/resonance.py --detail shows the rest."""
    L = ['======= M319 PROXIMITY -- ONE FIGURE (Core L-514, Part 3.45; Companion Part 83) =======',
         'PROXIMITY: out of 100 chance look-alikes, how many the idea or object is closer to the structure of Omega42 than. 50 is chance; 100 closer than every one; 0 farther than every one. For an idea the look-alikes are random atlases with its own word counts; for an object, its frozen class. Listed in the order of the register, never ranked. For the rest -- fit, reading integrity, placement, robustness, provenance, times chance -- ask for the detail (python3 tools/resonance.py --detail [NAME]).', '']
    for p in ps:
        px = p['prox']
        L.append('  %-12s PROXIMITY %3d' % (p['name'], prox_figure(p['K'])))
    L.append('')
    panels = object_proximity()
    for line in open(os.path.join(ROOT, 'records', 'resonance', 'objects.txt'), encoding='utf-8'):
        if line.startswith('#') or line.startswith('OBJECT') or '|' not in line: continue
        o, pl, d, pn = [x.strip() for x in line.split('|')]
        key = pn.split(' (')[0]
        if key not in panels:
            L.append('  %-44s PROXIMITY PENDING  (no class of look-alikes frozen)' % o); continue
        P = panels[key]
        if ' (' not in pn:
            L.append('  %-44s PROXIMITY %3d  (against %d frozen look-alikes)' % (o, prox_figure(P['share']), P['n'])); continue
        mine = next((x for nm, x in P['members'] if nm.lower().startswith(o.lower())), None); others = [x for nm, x in P['members'] if not nm.lower().startswith(o.lower())]
        sh = (sum(1 for x in others if x < mine) + 0.5 * sum(1 for x in others if x == mine)) / len(others)
        L.append('  %-44s PROXIMITY %3d  (a look-alike in %s, against the other %d members of its class)' % (o, prox_figure(sh), key, len(others)))
    L.append('')
    L.append('CONTROL (avenue 3, records/avenues/adversarial_atlas_output.txt): thirteen bus-timetable sentences chosen only for standing on Voice C read PROXIMITY 100, and thirteen unselected ones 82. An idea\'s figure is therefore not quoted as evidence before avenue 10 (sampled atlases), and is read beside this control.')
    L.append('A figure is a reading of the record, not a grade of the idea, the frame or the premise (L-490, L-505). With 22 ideas, about one reads 95 or more and about one 5 or less by chance alone; a figure that one statement or one measure can move is marked in the detail.')
    L.append('======= END M319 PROXIMITY =======')
    return '\n'.join(L)


def report(trials=TRIALS):
    ps = [profile(i, trials) for i in IDEAS]
    out = ['======= M319 RESONANCE PROFILES (Core Part 3.45, L-514; Companion Part 80) =======',
           'Two answers, side by side and never combined: COHERENCE, judged against the frame (CDT-C); CONGRUENCE, computed against chance (CDT-A). %d trials per null; K = 0.5 is chance.' % trials, '']
    for p in ps: out += [card(p), '']
    out.append(grid(ps)); out.append('')
    out += objects_block(); out.append('')
    above = [p['name'] for p in ps if p['K'] >= 0.95]; below = [p['name'] for p in ps if p['K'] <= 0.05]
    out.append('FAMILY (L-514): %d ideas; by chance alone about %.1f fall ABOVE CHANCE and %.1f BELOW CHANCE on the conditioned K; observed ABOVE %d (%s), BELOW %d (%s)' % (
        len(ps), len(ps) / 20, len(ps) / 20, len(above), ', '.join(above) or 'none', len(below), ', '.join(below) or 'none'))
    outer = [p for p in ps if band(p['K']) != 'AT CHANCE']; keep = [p['name'] for p in outer if band(p['Kloo'][0]) == band(p['Kloo'][1]) == band(p['K'])]
    out.append('ROBUSTNESS: of the %d ideas outside the chance band, %d keep their band when any one meeting measure is left out%s' % (len(outer), len(keep), (' (' + ', '.join(keep) + ')') if keep else ''))
    jk = [p for p in ps if p['jack']]; stable = [p for p in jk if band(p['jack'][0]) == band(p['jack'][1]) == band(p['K'])]
    out.append('STATEMENT JACKKNIFE: of the %d ideas, %d keep their band whichever single statement is left out; %d move -- a band that one statement can move is a property of the atlas as chosen (APE-141, control 3)' % (len(jk), len(stable), len(jk) - len(stable)))
    xs = [p['fshare'] for p in ps if p['fshare'] is not None]; ys = [p['K'] for p in ps if p['fshare'] is not None]
    out.append('THE TWO AXES: Spearman rank correlation of the features share with K over %d ideas = %.2f -- printed to show whether the two answers move together, never to merge them' % (len(xs), spearman(xs, ys)))
    out.append('ACCURACY: coherence has one judge and no agreement measured (M300; --agreement); congruence is exact up to its Monte Carlo error, printed on each card, and measures the atlas as worded -- the Navigator\'s own words where the atlas is paraphrased')
    out.append('READING: the profile says how an idea fits the frame and how its statements meet the structure; it does not grade the idea, the frame or the premise (L-490, L-505), and its corner is no verdict')
    out.append('======= END M319 RESONANCE PROFILES =======')
    return '\n'.join(out), ps


def spearman(x, y):
    def rank(v):
        o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
            for k in range(i, j + 1): r[o[k]] = (i + j) / 2 + 1
            i = j + 1
        return r
    a, b = rank(x), rank(y); ma, mb = statistics.fmean(a), statistics.fmean(b)
    den = (sum((u - ma) ** 2 for u in a) * sum((v - mb) ** 2 for v in b)) ** 0.5
    return sum((u - ma) * (v - mb) for u, v in zip(a, b)) / den if den else 0.0


def margin(s_obj, nulls):
    """APE-143: M = (s_obj - mean of nulls) / (1 - mean of nulls), in [-1, 1]; NONDISCRIMINATING when every null scores 1."""
    if not nulls: return None, 'PENDING'
    m = sum(nulls) / len(nulls)
    if m >= 1.0: return 0.0, 'NONDISCRIMINATING'
    return round((s_obj - m) / (1.0 - m), 4), 'OK'


def p_perm(s_obj, nulls):
    """The permutation p: (1 + nulls scoring at or above the object) / (1 + nulls); its least value is 1 / (1 + nulls)."""
    return round((1 + sum(1 for s in nulls if s >= s_obj)) / (1 + len(nulls)), 4)


def p_family(p, k_prime):
    """Look-elsewhere: 1 - (1 - p)^k' for k' features chosen after the object was seen; 0 when every feature was frozen first."""
    return round(1 - (1 - p) ** k_prime, 4) if k_prime else 0.0


def margin_band(M, status, p, n_nulls):
    """DISCRIMINATING at M >= 0.25 and p <= 0.10 (APE-143); UNDERPOWERED when M >= 0.25 but the class is too small for p to
    reach 0.10; NEGATIVE below 0; NONDISCRIMINATING otherwise; PENDING with no nulls."""
    if status != 'OK': return status
    if M < 0: return 'NEGATIVE'
    if M >= 0.25 and p <= 0.10: return 'DISCRIMINATING'
    if M >= 0.25 and 1 / (1 + n_nulls) > 0.10: return 'UNDERPOWERED (the class of %d nulls cannot reach p <= 0.10)' % n_nulls
    return 'NONDISCRIMINATING'


def read_table(path):
    T = {}
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or '|' not in line or line.startswith('CANDIDATE'): continue
        c = [x.strip() for x in line.split('|')]
        try: T[c[0]] = [float(v) for v in c[1:7]]
        except ValueError: pass
    return T


def agreement(A, B):
    """Two judges' feature tables: exact agreement over the shared cells and quadratic-weighted kappa on {0, 0.5, 1}."""
    keys = sorted(set(A) & set(B)); pairs = [(a, b) for k in keys for a, b in zip(A[k], B[k])]
    if not pairs: return None
    cats = [0.0, 0.5, 1.0]; n = len(pairs)
    exact = sum(a == b for a, b in pairs) / n
    w = lambda i, j: ((i - j) / 2) ** 2
    obs = sum(w(cats.index(a), cats.index(b)) for a, b in pairs) / n
    pa = [sum(a == c for a, _ in pairs) / n for c in cats]; pb = [sum(b == c for _, b in pairs) / n for c in cats]
    exp = sum(pa[i] * pb[j] * w(i, j) for i in range(3) for j in range(3))
    kappa = 1 - obs / exp if exp > 0 else 1.0
    return dict(ideas=len(keys), cells=n, exact=exact, kappa=kappa)


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-74s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    check('every registered idea has its six feature scores in its record', all(features(i[3], i[4]) and len(features(i[3], i[4])) == 6 for i in IDEAS))
    check('feature totals match the TOTAL column of their records', all(_total_ok(i) for i in IDEAS))
    check('ROLES and RELATIONS read apart from NAV-2026-0023 (1.00, 0.875)', coherence_of_nav('NAV-2026-0023') == (1.0, 0.875))
    check('ROLES and RELATIONS recovered from an averaged score, NAV-2026-0011 (1.00, 0.75)', coherence_of_nav('NAV-2026-0011') == (1.0, 0.75))
    sig = [fc.strike(t) for t in bl.LAWS]
    K1, e1 = percentile(sig, True, 4000); K2, _ = percentile(sig, True, 4000)
    check('K is reproducible (fixed seed) and lies in [0, 1]', K1 == K2 and 0 <= K1 <= 1 and e1 < 0.02)
    rnd = random.Random(7); pool = fc.pool()
    Ks = [percentile([rnd.choice(pool) for _ in range(8)], False, 1500, seed=s)[0] for s in range(30)]
    check('random atlases give K near chance on average (0.35 to 0.65)', 0.35 <= statistics.fmean(Ks) <= 0.65)
    home = [s for s in pool if s['voice'] == 'Voice C']
    Kh = percentile([rnd.choice(home) for _ in range(9)], False, 3000)[0]
    check('an atlas built on the canonical cycle reads ABOVE CHANCE', Kh >= 0.95)
    off = [s for s in pool if s['voice'] != 'Voice C' and s['state'] not in fc.SEEDS]
    Ko = percentile([rnd.choice(off) for _ in range(9)], False, 3000)[0]
    check('an atlas kept off the cycle and the seeds reads below an on-cycle one', Ko < Kh)
    Kr = percentile(sig, True, 3000, loo=True)
    check('the leave-one-out range is computed on the same null and brackets sensible values', len(Kr) == 3 and 0 <= Kr[2][0] <= Kr[2][1] <= 1)
    check('Spearman of a series with itself is 1, with its reverse -1', abs(spearman([1, 2, 3], [1, 2, 3]) - 1) < 1e-9 and abs(spearman([1, 2, 3], [3, 2, 1]) + 1) < 1e-9)
    check('Margin: (0.70 against four nulls of 0.30) = 0.5714, a tie 0.0, below -0.4000 (APE-143)', margin(0.70, [0.30] * 4)[0] == 0.5714 and margin(0.50, [0.50] * 4)[0] == 0.0 and margin(0.30, [0.50] * 4)[0] == -0.4)
    check('Margin: every null at 1.00 is NONDISCRIMINATING; no nulls PENDING', margin(0.90, [1.0] * 4)[1] == 'NONDISCRIMINATING' and margin(0.9, [])[1] == 'PENDING')
    check('permutation p when no null reaches the object: 1/5 = 0.2 (APE-143 printed 1.0)', p_perm(0.70, [0.30] * 4) == 0.2)
    check('p_family: 0 when frozen first; 1 - (43/48)^6 = 0.4832 for six tests after the fact', p_family(5 / 48, 0) == 0.0 and p_family(5 / 48, 6) == 0.4832)
    check('a large Margin on five nulls is UNDERPOWERED, on twenty can be DISCRIMINATING', margin_band(0.6, 'OK', 1 / 6, 5).startswith('UNDERPOWERED') and margin_band(0.6, 'OK', 1 / 21, 20) == 'DISCRIMINATING')
    pr_on = proximity([rnd.choice(home) for _ in range(9)], 3000)[0]
    pr_rand = statistics.fmean(proximity([rnd.choice(pool) for _ in range(8)], 1500, seed=s)[0] for s in range(20))
    check('TIMES CHANCE: an atlas on the canonical cycle reads above 1; random atlases average near 1 (0.8 to 1.2)', pr_on > 1.0 and 0.8 <= pr_rand <= 1.2)
    check('PROXIMITY: the planted on-cycle atlas reads 95 or more; 50 is chance (K 0.5)', prox_figure(Kh) >= 95 and prox_figure(0.5) == 50)
    op = object_proximity()
    check('PROXIMITY of an object: the 24-cell 100 (outscores all 46 uniform look-alikes), 24-tone equal temperament 50 (ties all three)', prox_figure(op['PANEL 3']['share']) == 100 and op['PANEL 3']['n'] == 46 and prox_figure(op['PANEL 2']['share']) == 50)
    check('bands: 0.97 ABOVE, 0.50 AT, 0.03 BELOW', (band(0.97), band(0.5), band(0.03)) == ('ABOVE CHANCE', 'AT CHANCE', 'BELOW CHANCE'))
    A = {'x': [1, 0.5, 0, 1, 1, 0], 'y': [0, 0, 1, 1, 0.5, 0.5]}
    g = agreement(A, A); check('agreement of a judge with itself: exact 1.00, kappa 1.00', g['exact'] == 1 and abs(g['kappa'] - 1) < 1e-9)
    B = {'x': [0, 0.5, 1, 0, 0, 1], 'y': [1, 1, 0, 0, 0.5, 0.5]}
    check('agreement of opposed judges: kappa below zero', agreement(A, B)['kappa'] < 0)
    print('M319 RESONANCE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def _total_ok(i):
    for line in open(os.path.join(ROOT, i[3]), encoding='utf-8'):
        c = [x.strip() for x in line.split('|')]
        if len(c) > 7 and (c[0] == i[4] or c[0].startswith(i[4] + ' ')):
            try: return abs(sum(float(v) for v in c[1:7]) - float(c[7])) < 1e-9
            except ValueError: return False
    return False


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a and a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a and a[0] == '--agreement':
        g = agreement(read_table(a[1]), read_table(a[2]))
        print('AGREEMENT (M319, M300): %s' % ('no shared ideas' if not g else '%d ideas, %d cells | exact %.2f | quadratic-weighted kappa %.2f' % (g['ideas'], g['cells'], g['exact'], g['kappa']))); sys.exit(0)
    if a and a[0] == '--atlas':
        name, rows = fc.load(a[1]); sigs = [fc.strike(t) for _, t in rows]
        K, e = percentile(sigs, True); Ku, _ = percentile(sigs, False)
        print('%s: CONGRUENCE K %.3f +/- %.3f given word counts %s %s | uniform K %.3f | %d statements | coherence: judge the six features before reading K' % (name, K, e, bar(K), band(K), Ku, len(sigs))); sys.exit(0)
    text, ps = report()
    if not a:
        print(headline(ps)); sys.exit(0)
    if a[0] == '--detail' and len(a) == 1:
        print(text); sys.exit(0)
    if a[0] in ('--card', '--detail'):
        print(card(next(p for p in ps if p['name'].lower() == a[1].lower()))); sys.exit(0)
    if a and a[0] == '--map':
        print(grid(ps)); sys.exit(0)
    print(text)
