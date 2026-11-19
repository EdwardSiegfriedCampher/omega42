#!/usr/bin/env python3
"""reframing_array.py -- M318 Reframing Array and the arithmetic layer of M241 (Core Part 3.44, L-511, L-510; Companion Part 72).

How a question is asked decides where it lands (Core L10). This tool computes the arithmetic layer of a question
seen from several framings; the readings are the Navigator's, written after the primary is sealed.

    python3 tools/reframing_array.py --compare "TEXT A" "TEXT B" ["TEXT C"]
        M241: two or three texts the Striker submitted, side by side: counts, anchor, state, arms, STABLE ACROSS ALL
        and VARIED with M115 distances, and the verbatim strings for SR-CAS.
    python3 tools/reframing_array.py --freeze "AXIS=TEXT" ["AXIS=TEXT" ...]
        M318 step 2: the FRAMINGS SHA-256 of the alternative framings, computed before any of their coordinates.
        Nothing else is printed, so the list cannot be chosen for its anchors (ANCHOR STEERING).
    python3 tools/reframing_array.py --array "PRIMARY" "AXIS=TEXT" ... [--sha HEX]
        M318 steps 3 and 5: checks the list against the frozen hash (when given), then computes every coordinate and
        prints the block with ACROSS THE FRAMINGS and the STRUCTURAL VERDICT; the readings are left to fill.
    python3 tools/reframing_array.py --selftest

Axes (L-511): SCOPE, STANDPOINT, DIRECTION, CONTRARY, PLAIN, or another the Navigator names. A framing that changes
only the order of the words is COORDINATE-IDENTICAL: the counts do not read word order (L-510). Every value is
computed by the reference script [CDT-A]; the verdict is structural, and which framing is relevant is the
Striker's (L-441). Standard library and the tools beside this file.
"""
import hashlib, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr
import utility as U

AXES = ('SCOPE', 'STANDPOINT', 'DIRECTION', 'CONTRARY', 'PLAIN')
FEATURES = ('anchor', 'state', 'half', 'voice', 'aspect', 'crown arms', 'mobius')


def coord(q):
    x = cr.navigate(q); z = U.strike(q)
    arms = [('Yang', x['yang_i']), ('Yin', x['yin_i']), ('4D', x['fourd_i']), ('Antipode', x['antipode_i'])]
    crown = tuple(n for n, i in arms if cr.is_crown(i))
    return dict(q=q, words=tuple(sorted(w.lower() for w in x['content'])), n=(x['n1'], x['n2'], x['n3']), anchor=x['anchor'], name=x['anchor_name'], state=z['state'],
                half=z['half'], voice=z['voice'], aspect=z['aspect'].split()[0], arms=arms,
                **{'crown arms': crown or ('none',)}, mobius='ACTIVE' if x['mobius'] else 'INACTIVE')


def fval(c, f):
    return c[f] if f != 'crown arms' else ', '.join(c[f])


def parse_framing(s):
    m = re.match(r'^\s*([A-Za-z][A-Za-z -]*?)\s*=\s*(.+)$', s, re.S)
    if not m: raise SystemExit('a framing is AXIS=TEXT: %r' % s)
    return m.group(1).strip().upper(), m.group(2).strip()


def framings_sha256(framings):
    """The hash of the frozen list: each framing as AXIS|TEXT, the text in the canonical form of L-414, one per line."""
    canon = '\n'.join('%s|%s' % (a, cr.canonical_domain_form(t)) for a, t in framings)
    return hashlib.sha256(unicodedata.normalize('NFC', canon).encode('utf-8')).hexdigest()


def one_line(t):
    """L-512 line form: a domain received on several lines is printed on one, each break as one space."""
    return re.sub(r'[ \t]*\n[ \t]*', ' ', t).strip()


def line(tag, c):
    return '%s: "%s" -> n = %s | ANCHOR P%d (%s) | STATE %s | %s, %s | arms %s' % (
        tag, one_line(c['q']), c['n'], c['anchor'], c['name'], c['state'], c['half'], c['voice'],
        ' '.join('%s P%d' % (n, i) for n, i in c['arms']))


def identical(c, p):
    if c['words'] == p['words']: return 'COORDINATE-IDENTICAL, ORDER ONLY (the same content words in another order; word order is not read, L-510)'
    return 'COORDINATE-IDENTICAL, SAME COUNTS (other words with the same counts; the difference lives only in the reading, L-510)'


def across(cs):
    holds = [f for f in FEATURES if len({fval(c, f) for c in cs}) == 1]
    parts = [f for f in FEATURES if f not in holds]
    return holds, parts


def shared_arms(cs):
    """Positions that appear among the arms of every framing (a position may serve a different arm in each)."""
    common = set.intersection(*[{i for _, i in c['arms']} for c in cs])
    return ', '.join('P%d %s' % (i, cr.POSITION_NAMES[i]) for i in sorted(common)) or 'none'


def compare_text(texts):
    if not 2 <= len(texts) <= 3: raise SystemExit('M241 takes two or three texts (Core Part 3.3)')
    cs = [coord(t) for t in texts]
    L = ['======= M241 COMPARATIVE PHRASING NAVIGATION -- ARITHMETIC LAYER (Core Part 3.3) =======']
    L += ['QUESTION VERBATIM: %s' % one_line(t) for t in texts]
    for k, c in enumerate(cs): L.append(line('TEXT ' + 'ABC'[k], c))
    holds, parts = across(cs)
    L.append('STABLE ACROSS ALL: ' + (', '.join('%s %s' % (f, fval(cs[0], f)) for f in holds) or 'NONE'))
    var = []
    for f in parts: var.append('%s (%s)' % (f, ' / '.join(str(fval(c, f)) for c in cs)))
    dist = ', '.join('D(%s,%s) = %d' % ('ABC'[i], 'ABC'[j], cr.m115_distance(cs[i]['anchor'], cs[j]['anchor']))
                     for i in range(len(cs)) for j in range(i + 1, len(cs)))
    L.append('VARIED: ' + ('; '.join(var) if var else 'NONE') + ' | M115: ' + dist)
    same = [('ABC'[i], 'ABC'[j]) for i in range(len(cs)) for j in range(i + 1, len(cs)) if cs[i]['n'] == cs[j]['n']]
    if same: L.append('COORDINATE-IDENTICAL: ' + ', '.join('%s and %s, %s' % (i, j, identical(cs['ABC'.index(i)], cs['ABC'.index(j)]).split(', ', 1)[1]) for i, j in same))
    L.append('INDEPENDENCE (L-442): [FILL: SEPARATE SESSIONS / CONTAMINATED -- NON-BLIND]')
    L.append('VERBATIM STRINGS FOR CROSS-NAVIGATOR SR-CAS: ' + ' | '.join('"%s"' % t for t in texts))
    L.append('RELEVANCE: the Striker\'s (L-441). The arithmetic is computed; the readings are each written in full by the Navigator (Steps 1-16).')
    L.append('======= END M241 COMPARATIVE PHRASING NAVIGATION =======')
    return '\n'.join(L)


def array_text(primary, framings, sha=None):
    if not 3 <= len(framings) <= 5: raise SystemExit('M318 takes three to five alternative framings (L-511)')
    h = framings_sha256(framings)
    if sha and sha.lower() != h: raise SystemExit('FRAMINGS SHA-256 MISMATCH: the list differs from the one frozen (%s, frozen %s)' % (h, sha))
    p = coord(primary); cs = [coord(t) for _, t in framings]
    L = ['======= M318 REFRAMING ARRAY (L-511) =======', 'QUESTION VERBATIM: %s' % one_line(primary), line('PRIMARY', p),
         'PRIMARY ANSWER: the full navigation of the verbatim strike, sealed before any framing was written (L-424); the domain of record (L-348, L-499)',
         'FRAMINGS FROZEN: %d | FRAMINGS SHA-256: %s | %s' % (len(framings), h, 'checked against the hash frozen before any coordinate' if sha else 'NOT CHECKED (no frozen hash given; run --freeze first)')]
    for k, ((a, t), c) in enumerate(zip(framings, cs)):
        d = cr.m115_distance(p['anchor'], c['anchor'])
        tag = 'F%d %s' % (k + 1, a)
        s = line(tag, c) + ' | D = %d' % d
        if c['n'] == p['n']: s += ' | ' + identical(c, p)
        L.append(s)
        L.append('  ALTERNATIVE FRAMING -- SELF-ESTIMATED -- CONTAMINATED -- NON-BLIND (L-442): [FILL: four sentences -- what it rests on, what it holds out of view, where it is heading, what would complete it]')
    allc = [p] + cs
    holds, parts = across(allc)
    L.append('INDEPENDENCE (L-442): CONTAMINATED -- NON-BLIND (written in one session after the primary) -- or SEPARATE SESSIONS (M300), stated')
    L.append('ACROSS THE FRAMINGS (L-502): HOLDS ' + (', '.join('%s %s' % (f, fval(p, f)) for f in holds) or 'nothing') +
             ' | PARTS ' + ('; '.join('%s (%s)' % (f, ' / '.join(str(fval(c, f)) for c in allc)) for f in parts) or 'nothing') +
             ' | ARM POSITIONS IN EVERY FRAMING: ' + shared_arms(allc) +
             ' | READINGS: [FILL: where the readings agree, part and are silent; never combined]')
    ds = [(cr.m115_distance(p['anchor'], c['anchor']), k + 1) for k, c in enumerate(cs)]
    near = min(ds); far = max(ds)
    share = sum(c['anchor'] == p['anchor'] for c in cs)
    L.append('STRUCTURAL VERDICT (computed): the robust core is %s; %d of %d framings keep the primary\'s anchor; nearest F%d (D = %d), farthest F%d (D = %d)' % (
        ', '.join('%s %s' % (f, fval(p, f)) for f in holds) if holds else 'empty -- every feature moves with the framing', share, len(cs), near[1], near[0], far[1], far[0]))
    L.append('RELEVANCE: the Striker\'s (L-441) -- which framing answers what you meant to ask is yours; strike any framing ("strike F2") to navigate it in full')
    L.append('======= END M318 REFRAMING ARRAY =======')
    return '\n'.join(L)


def selftest():
    ok = []
    def check(name, cond): ok.append(bool(cond)); print(('PASS ' if cond else 'FAIL ') + name)
    a, b = coord('Mapping Omega42 to the Moon'), coord('Mapping the Moon to Omega42')
    check('the two directions strike at one coordinate (word order is not read)', a['n'] == b['n'] == (3, 16, 6) and a['anchor'] == b['anchor'] == 6)
    check('the Moon is placed at P5, with Book and Sun', all(coord(w)['anchor'] == 5 for w in ('the Moon', 'Book', 'Sun', 'Water')))
    F = [('SCOPE', 'What is life for?'), ('STANDPOINT', 'Why are we alive?'), ('PLAIN', 'What gives life purpose?')]
    h = framings_sha256(F)
    t = array_text('What is the purpose of life?', F, h)
    check('array computes the framings: P1, P6, P2 beside the primary P6', all(s in t for s in ('ANCHOR P6 (Seed/Causal)', 'F1 SCOPE: "What is life for?" -> n = (2, 8, 2) | ANCHOR P1', 'F3 PLAIN', 'ANCHOR P2 (Generator)')))
    check('the arm position shared by every framing is reported', 'ARM POSITIONS IN EVERY FRAMING: P14 Observer' in array_text('What is the purpose of life?', [('SCOPE', 'What is my life for?'), ('STANDPOINT', 'Why are we alive?'), ('PLAIN', 'What gives life purpose?')]))
    check('one of three framings keeps the primary anchor', '1 of 3 framings keep' in t)
    check('the frozen hash is checked', 'checked against the hash frozen' in t)
    try:
        array_text('What is the purpose of life?', F[:2] + [('PLAIN', 'Life purpose')], h); bad = False
    except SystemExit as e:
        bad = 'MISMATCH' in str(e)
    check('a list changed after the freeze is refused', bad)
    t2 = array_text('Mapping Omega42 to the Moon', [('DIRECTION', 'Mapping the Moon to Omega42'), ('PLAIN', 'Does the Moon follow the Fibonacci rule?'), ('SCOPE', 'Do moons carry the cycle?')])
    check('an order-only framing is flagged COORDINATE-IDENTICAL, ORDER ONLY', 'F1 DIRECTION' in t2 and 'ORDER ONLY' in t2)
    t3 = array_text('What is the purpose of life?', [('CONTRARY', 'Can a life have no purpose?')] + F[:2])
    check('other words with the same counts are flagged SAME COUNTS', 'SAME COUNTS' in t3 and 'ORDER ONLY' not in t3)
    check('no verdict of worth: relevance is the Striker\'s', 'RELEVANCE: the Striker\'s' in t and not re.search(r'\b(best|better|most relevant|correct framing)\b', t.replace('RELEVANCE', '')))
    c = compare_text(['Mapping Omega42 to the Moon', 'Mapping the Moon to Omega42'])
    check('M241 arithmetic layer: STABLE ACROSS ALL holds every feature for the two directions', 'VARIED: NONE' in c and 'COORDINATE-IDENTICAL: A and B, ORDER ONLY' in c)
    try:
        array_text('x', F[:2]); few = False
    except SystemExit:
        few = True
    check('fewer than three framings is refused', few)
    print('SELFTEST: %d/%d PASS' % (sum(ok), len(ok)))
    return all(ok)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--compare': print(compare_text(a[1:])); sys.exit(0)
    if a[0] == '--freeze':
        F = [parse_framing(s) for s in a[1:]]
        print('FRAMINGS FROZEN: %d | FRAMINGS SHA-256: %s' % (len(F), framings_sha256(F))); sys.exit(0)
    if a[0] == '--array':
        sha = None
        if '--sha' in a: i = a.index('--sha'); sha = a[i + 1]; a = a[:i] + a[i + 2:]
        print(array_text(a[1], [parse_framing(s) for s in a[2:]], sha)); sys.exit(0)
    print(__doc__); sys.exit(2)
