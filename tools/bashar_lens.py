#!/usr/bin/env python3
"""bashar_lens.py -- the Bashar Lens of Core Part 3.35 (L-487): M303 Five Laws Lens, M304 Structural Mirror,
M305 Frequency Reading, and the ground facts the lens rests on. The arithmetic is canonical_reference.py's,
unchanged; the lens adds names and arrangements, never a count, an anchor or a reading.

  --lens "DOMAIN"         M303: the navigation's computed structure arranged by the five laws, with the
                          frequency (M305) of the domain and of its three M238 parallel frames
  --mirror "Q1" "Q2"      M304: a question and its reframing, side by side -- anchors, mirrors, frequencies,
                          the cycle distance of the shift and whether the frequency changed
  --frequency "DOMAIN"    M305: the state (r1, r2) as the element a + b*phi of Z[phi]/9, its norm, its orbit
                          (Voice A, Voice B, Voice C, Wheel or Fix) and its step on that orbit from the seed
  --laws                  the five laws struck as domains (records/bashar/five_laws.txt)
  --ring                  the ground facts: T is multiplication by phi in Z[phi]/9; the norm is the field norm
  --check NAVIGATION.txt  M308 Bashar Resonance Check: the frozen navigation (or, with --domain "TEXT", a domain alone)
                          compared with the Bashar Atlas -- structural (state, anchor, frequency, with exact base
                          rates), thematic (the reading's own words) and the mapping placement; printed as block 20.5
  --atlas                 the Bashar Atlas, struck (records/bashar/atlas.txt)
  --selftest

Usage:
    python3 tools/bashar_lens.py --lens "Follow your excitement."
    python3 tools/bashar_lens.py --selftest
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import canonical_reference as cr
import crc60_and_m267 as m238v

NAMES = cr.POSITION_NAMES
T = lambda s: (s[1], (s[0] + s[1]) % 9)
SEEDS = (('Fix', (0, 0)), ('Wheel', (3, 3)), ('Voice A', (1, 1)), ('Voice B', (1, 3)), ('Voice C', (2, 5)))
LAWS = ("You exist. You always have and you always will.",
        "Everything is here and now.",
        "The One is the All and the All is the One.",
        "What you put out is what you get back.",
        "Everything changes except for the first four laws.")


def orbit_of(seed):
    out, x = [], seed
    while True:
        out.append(x); x = T(x)
        if x == seed: return out


ORBITS = {name: orbit_of(seed) for name, seed in SEEDS}


def norm(s):
    a, b = s
    return (a * a + a * b - b * b) % 9


def mul(x, y):
    """(a + b phi)(c + d phi) in Z[phi]/9, phi^2 = phi + 1."""
    a, b = x; c, d = y
    return ((a * c + b * d) % 9, (a * d + b * c + b * d) % 9)


def frequency(r1, r2):
    s = (r1 % 9, r2 % 9)
    for name, orb in ORBITS.items():
        if s in orb:
            return dict(state=s, norm=norm(s), voice=name, step=orb.index(s), period=len(orb))


def cyc(a, b):
    d = abs(a - b) % 24
    return min(d, 24 - d)


def value(i):
    return cr.orbit_value(i % 24)


def strike(text):
    x = cr.navigate(text)
    x['freq'] = frequency(x['r1'], x['r2'])
    return x


def freq_line(f):
    return '%s (state %s = %d + %d phi, norm %d, step %d of %d)' % (
        f['voice'], f['state'], f['state'][0], f['state'][1], f['norm'], f['step'], f['period'])


def lens(text):
    x = strike(text)
    a = x['anchor']; L = []
    L.append('======= M303 FIVE LAWS LENS (L-487) =======')
    L.append('DOMAIN: %s' % text)
    L.append('COUNTS: n = (%d, %d, %d) | r = (%d, %d, %d) | ANCHOR P%d %s (value %d) | TFI %.2f' % (
        x['n1'], x['n2'], x['n3'], x['r1'], x['r2'], x['r3'], a, NAMES[a], value(a), x['tfi']))
    import manifestation as _mf
    st = (x['r1'] % 9, x['r2'] % 9); stratum, half, _loop = _mf.classify(st)
    L.append('STRATUM (M312): %s -- %s | half %s' % (stratum, {'UNIT': 'the manifest world', 'CORE': 'the ground (nilpotent: s*s = 0)',
             'STILL POINT': 'the still point'}[stratum], half))
    L.append('LAW 1  YOU EXIST            -> the anchor: the question exists at P%d %s' % (a, NAMES[a]))
    L.append('LAW 2  EVERYTHING HERE/NOW  -> where it is heading is already on the cycle: 4D P%d %s | MOBIUS %s' % (
        x['fourd_i'], NAMES[x['fourd_i']], 'ACTIVE (what it will become shapes it now)' if x['mobius'] else 'INACTIVE'))
    L.append('LAW 3  THE ONE IS THE ALL   -> what it rests on: Yang P%d %s | frequency %s' % (
        x['yang_i'], NAMES[x['yang_i']], freq_line(x['freq'])))
    L.append('LAW 4  WHAT YOU PUT OUT     -> the mirror: Antipode P%d %s (value %d); %d + %d = %d, the ground' % (
        x['antipode_i'], NAMES[x['antipode_i']], value(x['antipode_i']), value(a), value(x['antipode_i']),
        value(a) + value(x['antipode_i'])))
    frames, held = [], True
    for k, v in (('MINIMAL', m238v.minimal(text, cr)), ('PB-5 L1', m238v.pb5_l1(text)), ('PB-5 L2', m238v.pb5_l2(text))):
        y = strike(v)
        frames.append('%s P%d %s, %s' % (k, y['anchor'], NAMES[y['anchor']], y['freq']['voice']))
        held &= y['anchor'] == a
    L.append('LAW 5  EVERYTHING CHANGES   -> parallel frames (M238): %s | %s' % (
        '; '.join(frames), 'the anchor holds in every frame' if held else 'the anchor moves between frames'))
    L.append('FORMULA  limiting belief to examine -> what it holds out of view: Yin P%d %s' % (x['yin_i'], NAMES[x['yin_i']]))
    L.append('STATUS: the values are canonical_reference.py\'s [CDT-A]; the law-to-structure arrangement is the lens [CDT-C]; the reading is the Navigator\'s; the meaning is the Striker\'s.')
    L.append('======= END M303 FIVE LAWS LENS =======')
    return '\n'.join(L)


def mirror(q1, q2):
    x, y = strike(q1), strike(q2)
    L = ['======= M304 STRUCTURAL MIRROR (L-487) =======']
    for tag, t, z in (('QUESTION', q1, x), ('REFRAMED', q2, y)):
        L.append('%s: %s | ANCHOR P%d %s | MIRROR P%d %s | FREQUENCY %s' % (
            tag, t, z['anchor'], NAMES[z['anchor']], z['antipode_i'], NAMES[z['antipode_i']], freq_line(z['freq'])))
    d = cyc(x['anchor'], y['anchor'])
    L.append('SHIFT: %d step(s) on the cycle | FREQUENCY %s' % (
        d, 'CHANGED (%s -> %s)' % (x['freq']['voice'], y['freq']['voice']) if x['freq']['voice'] != y['freq']['voice'] else 'UNCHANGED (%s)' % x['freq']['voice']))
    import manifestation as _mf                      # CT-42 (L-498): what the reframing kept and what it moved -- change the face, the reflection changes
    sx, sy = (x['r1'] % 9, x['r2'] % 9), (y['r1'] % 9, y['r2'] % 9)
    def _asp(st):
        k = _mf.classify(st)
        return dict(aspect={'UNIT': 'ACT', 'CORE': 'GROUND', 'STILL POINT': 'GROUND (still point)'}[k[0]], half=k[1], voice=k[2] or 'the still point')
    ax, ay = _asp(sx), _asp(sy); ax['anchor'], ay['anchor'] = 'P%d' % x['anchor'], 'P%d' % y['anchor']
    kept = [k for k in ('aspect', 'half', 'voice', 'anchor') if ax[k] == ay[k]]; moved = [k for k in ('aspect', 'half', 'voice', 'anchor') if ax[k] != ay[k]]
    L.append('CT-42 (M315): QUESTION %s, %s, %s | REFRAMED %s, %s, %s' % (ax['aspect'], ax['half'], ax['voice'], ay['aspect'], ay['half'], ay['voice']))
    L.append('THE FACE AND THE REFLECTION: kept %s | moved %s -- the reframing chose another place to read from; no state was changed by it' % (
        ', '.join(kept) or 'nothing', ', '.join(moved) or 'nothing'))
    L.append('STATUS: computed [CDT-A]; which framing to keep is the Striker\'s.')
    L.append('======= END M304 STRUCTURAL MIRROR =======')
    return '\n'.join(L)


def freq_report(text):
    x = strike(text); f = x['freq']
    return 'M305 FREQUENCY READING: "%s" | r = (%d, %d) | %s' % (text, x['r1'], x['r2'], freq_line(f))


def laws():
    L = ['FIVE LAWS STRUCK AS DOMAINS (canonical_reference.py; Core Part 3.35)']
    for i, t in enumerate(LAWS, 1):
        x = strike(t); f = x['freq']
        L.append('LAW %d | %s | n = (%d, %d, %d) | ANCHOR P%d %s | Yang P%d %s | Yin P%d %s | 4D P%d %s | Antipode P%d %s | MOBIUS %s | %s, state %s, norm %d' % (
            i, t, x['n1'], x['n2'], x['n3'], x['anchor'], NAMES[x['anchor']], x['yang_i'], NAMES[x['yang_i']],
            x['yin_i'], NAMES[x['yin_i']], x['fourd_i'], NAMES[x['fourd_i']], x['antipode_i'], NAMES[x['antipode_i']],
            'ACTIVE' if x['mobius'] else 'INACTIVE', f['voice'], f['state'], f['norm']))
    xs = [strike(t) for t in LAWS]
    voices = sorted({x['freq']['voice'] for x in xs})
    L.append('ORBITS REACHED: %s (%d of the 4 orbits longer than one state)' % (', '.join(voices), len([v for v in voices if v != 'Fix'])))
    links = ['Law %d rests on Law %d\'s anchor (P%d)' % (i + 1, j + 1, xs[i]['yang_i'])
             for i in range(5) for j in range(5) if i != j and xs[i]['yang_i'] == xs[j]['anchor']]
    L.append('LINKS: %s' % ('; '.join(links) or 'none'))
    seeds = ['Law %d stands on the seed of %s %s' % (i + 1, n, s) for i, x in enumerate(xs) for n, s in SEEDS if x['freq']['state'] == s]
    L.append('SEEDS: %s' % ('; '.join(seeds) or 'none'))
    L.append('BASE RATES (states and anchors drawn at random): five states cover the four long orbits 0.156; two or more such links among five anchors 0.197; at least one of five states on one of the five seeds 0.27.')
    return '\n'.join(L)


def ring_facts():
    states = [(a, b) for a in range(9) for b in range(9)]
    phi = (0, 1)
    f = {}
    f['T is multiplication by phi'] = all(T(s) == mul(s, phi) for s in states)
    f['norm is multiplicative'] = all(norm(mul(s, t)) == norm(s) * norm(t) % 9 for s in states for t in states)
    f['N(phi) = -1, so T reverses the norm'] = norm(phi) == 8 and all(norm(T(s)) == (-norm(s)) % 9 for s in states)
    units = [s for s in states if s[0] % 3 or s[1] % 3]
    f['72 units (the three 24-cycles), 9 non-units (Wheel and Fix)'] = len(units) == 72 and sorted(
        ORBITS['Voice A'] + ORBITS['Voice B'] + ORBITS['Voice C']) == sorted(units) and sorted(ORBITS['Wheel'] + ORBITS['Fix']) == sorted(set(states) - set(units))
    p, k = phi, 1
    while p != (1, 0): p, k = mul(p, phi), k + 1
    f['phi has multiplicative order 24'] = k == 24
    f['Voice B = (1 + 3 phi) * Voice A, Voice C = (2 + 5 phi) * Voice A'] = (
        sorted(mul((1, 3), s) for s in ORBITS['Voice A']) == sorted(ORBITS['Voice B']) and
        sorted(mul((2, 5), s) for s in ORBITS['Voice A']) == sorted(ORBITS['Voice C']))
    def Tn(s, n):
        for _ in range(n): s = T(s)
        return s
    f['T^12 = -I and T^24 = I'] = all(Tn(s, 12) == ((-s[0]) % 9, (-s[1]) % 9) and Tn(s, 24) == s for s in states)
    f['every state has exactly one predecessor'] = len({T(s) for s in states}) == 81
    f['antipodal values sum to the ground'] = all((value(i) + value(i + 12)) % 9 == 0 for i in range(24))
    return f


# ---------------------------------------------------------------- M308 Bashar Resonance Check (Core Part 3.35)
ATLAS = [
    ('LAW 1', LAWS[0], 'that you exist and always will'),
    ('LAW 2', LAWS[1], 'that everything is here and now'),
    ('LAW 3', LAWS[2], 'that the One is the All and the All is the One'),
    ('LAW 4', LAWS[3], 'that what you put out is what you get back'),
    ('LAW 5', LAWS[4], 'that everything changes except the first four laws'),
    ('FORMULA 1', 'Act on your highest excitement.', 'to act on your highest excitement'),
    ('FORMULA 2', 'Take it as far as you can.', 'to take it as far as you can'),
    ('FORMULA 3', 'Have zero insistence on the outcome.', 'to hold no insistence on the outcome'),
    ('FORMULA 4', 'Remain in a positive state whatever happens.', 'to remain in a positive state whatever happens'),
    ('FORMULA 5', 'Let go of the beliefs that no longer serve you.', 'to let go of the beliefs that no longer serve you'),
    ('TEACHING 1', 'Physical reality is a mirror.', 'that physical reality is a mirror'),
    ('TEACHING 2', 'Circumstances are neutral; you give them meaning.', 'that circumstances are neutral and you give them meaning'),
    ('TEACHING 3', 'You shift between parallel realities.', 'that you shift between parallel realities'),
    ('TEACHING 4', 'The present creates the past.', 'that the present creates the past'),
]
THEMES = [
    ('existence without end', r"\b(?:always (?:have|has) existed|exists? eternally|eternal(?:ly)?|cannot cease to exist|never ceases? to exist)\b"),
    ('here and now', r"\b(?:here and now|all at once|simultaneous(?:ly)?)\b"),
    ('the one and the all', r"\b(?:one is the all|oneness|all that is)\b"),
    ('the mirror', r"\bmirror(?:s|ed|ing)?\b"),
    ('change and the unchanging', r"\b(?:everything changes|unchanging|never changes)\b"),
    ('excitement', r"\b(?:excite(?:s|d|ment)?|exciting|passion(?:s|ate)?)\b"),
    ('beliefs and definitions', r"\b(?:beliefs?|limiting definitions?)\b"),
    ('parallel realities', r"\bparallel (?:realit(?:y|ies)|worlds?|versions?)\b"),
    ('state of being', r"\b(?:state of being|vibrational)\b"),
    ('no insistence on outcome', r"\b(?:insist(?:s|ing|ence)? on (?:the |an? )?outcome|attachment to (?:the |an? )?outcome)\b"),
    ('synchronicity', r"\bsynchronicit(?:y|ies)\b"),
    ('the present creates the past', r"\b(?:present (?:creates|shapes|fixes|implies) the past|the past is implied)\b"),
]


def _signature(n1, n2, n3):
    a, r1, r2, r3, tfi = cr.determine_anchor(n1, n2, n3)
    return a, frequency(r1, r2)


def atlas_rows():
    rows = []
    for tag, text, gist in ATLAS:
        x = strike(text)
        rows.append(dict(tag=tag, text=text, gist=gist, anchor=x['anchor'], state=x['freq']['state'], voice=x['freq']['voice']))
    return rows


def base_rates(rows):
    """Exact chance, over all 729 residue triples (each count's residue uniform), that a question shares with
    at least one atlas entry: its state; its anchor and frequency; its anchor; its frequency."""
    an = {r['anchor'] for r in rows}; vo = {r['voice'] for r in rows}; st = {r['state'] for r in rows}
    pair = {(r['anchor'], r['voice']) for r in rows}
    c = dict(state=0, pair=0, anchor=0, voice=0)
    for n1 in range(1, 10):
        for n2 in range(1, 10):
            for n3 in range(1, 10):
                a, f = _signature(n1, n2, n3)
                c['state'] += f['state'] in st; c['pair'] += (a, f['voice']) in pair
                c['anchor'] += a in an; c['voice'] += f['voice'] in vo
    return {k: v / 729 for k, v in c.items()}


def _block(text, label):
    import re
    m = re.search(r'^\u250c\u2500 ' + label + r' \u2500\u2510\s*\n(.*?)\n\u2514', text, re.S | re.M)
    return m.group(1) if m else ''


def resonance(domain, answer='', essay='', placement=None, lens_at_writing='OFF'):
    import re
    x = strike(domain); f = x['freq']; rows = atlas_rows(); br = base_rates(rows)
    L = ['======= BASHAR RESONANCE CHECK (M308) =======',
         'COORDINATE: ANCHOR P%d %s | state %s on %s (norm %d) | atlas: %d entries (Core Part 3.35)' % (
             x['anchor'], NAMES[x['anchor']], f['state'], f['voice'], f['norm'], len(rows))]
    hits = []
    for r in rows:
        if r['state'] == f['state']:
            hits.append(('STATE', r, br['state']))
        elif r['anchor'] == x['anchor'] and r['voice'] == f['voice']:
            hits.append(('ANCHOR AND FREQUENCY', r, br['pair']))
        elif r['anchor'] == x['anchor']:
            hits.append(('ANCHOR', r, br['anchor']))
        elif r['voice'] == f['voice']:
            hits.append(('FREQUENCY', r, br['voice']))
    order = {'STATE': 0, 'ANCHOR AND FREQUENCY': 1, 'ANCHOR': 2, 'FREQUENCY': 3}
    hits.sort(key=lambda h: (order[h[0]], h[1]['tag']))
    strong = [h for h in hits if h[0] in ('STATE', 'ANCHOR AND FREQUENCY')]
    anch = [h for h in hits if h[0] == 'ANCHOR']
    freq = [h for h in hits if h[0] == 'FREQUENCY']
    for lvl, group in (('STATE / PLACE AND FREQUENCY', strong), ('PLACE (ANCHOR)', anch)):
        if group:
            L.append('STRUCTURAL %s: %s' % (lvl, '; '.join('%s "%s" (%s)' % (h[1]['tag'], h[1]['text'], h[0]) for h in group)))
    if freq:
        L.append('SHARED FREQUENCY ONLY: %s (expected by chance)' % ', '.join(h[1]['tag'] for h in freq))
    L.append('BASE RATES (exact, 729 residue triples): any shared state %.3f | anchor and frequency %.3f | anchor %.3f | frequency %.3f' % (
        br['state'], br['pair'], br['anchor'], br['voice']))
    body = (answer + '\n' + essay).strip()
    themes = []
    if body:
        sents = re.split(r'(?<=[.!?])\s+', re.sub(r'\s+', ' ', body))
        for name, rx in THEMES:
            s = next((s for s in sents if re.search(rx, s, re.I)), None)
            if s:
                themes.append((name, s if len(s) < 160 else s[:157] + '...'))
        L.append('THEMATIC (the frozen reading, written with the lens %s): %s' % (lens_at_writing,
                 '; '.join('%s — "%s"' % t for t in themes) if themes else 'none of the %d themes' % len(THEMES)))
    else:
        L.append('THEMATIC: no frozen reading supplied')
    if placement is not None:
        mh = [r for r in rows if r['anchor'] == placement]
        L.append('MAPPING: placement P%d %s%s (chance %.3f: %d of the 9 placements are atlas anchors)' % (placement, NAMES[placement],
                 (' — the anchor of ' + ', '.join('%s "%s"' % (r['tag'], r['text']) for r in mh)) if mh else ' — no atlas anchor',
                 len({r['anchor'] for r in rows}) / 9, len({r['anchor'] for r in rows})))
    st = [h for h in hits if h[0] == 'STATE']
    level = ('STRONG (shared state, chance %.3f)' % br['state'] if st else
             'MODERATE (shared place and frequency, chance %.3f)' % br['pair'] if strong else
             'WEAK (shared place, chance %.3f)' % br['anchor'] if anch else 'NONE (a shared frequency alone is expected, chance %.3f)' % br['voice'])
    level += ' | THEMATIC: %d theme(s)%s' % (len(themes), '' if lens_at_writing == 'OFF' else ' (lens on at writing: not counted)')
    L.append('RESONANCE: %s' % level)
    words = []
    for lvl, r, rate in [h for h in hits if h[0] != 'FREQUENCY'][:3]:
        what = {'STATE': 'stands on the same state as', 'ANCHOR AND FREQUENCY': 'stands at the same place, on the same frequency, as',
                'ANCHOR': 'stands at the same place as'}[lvl]
        words.append('This question %s Bashar\'s statement "%s" — the teaching %s.' % (what, r['text'].rstrip('.'), r['gist']))
    if themes and lens_at_writing == 'OFF':
        words.append('Unprompted by the lens, the reading itself speaks of %s.' % ', '.join(t[0] for t in themes[:4]))
    L.append('CORRESPONDENCE: %s' % (' '.join(words) if words else 'No correspondence with the atlas is found.'))
    L.append('STATUS: computed after the freeze [CDT-A]; the correspondence is a reading [CDT-C]; a structural match counts for what its base rate allows (L-486); the check never alters the reading (L-487).')
    L.append('======= END BASHAR RESONANCE CHECK =======')
    return '\n'.join(L)


def check_navigation(path):
    import re
    t = open(path, encoding='utf-8').read()
    m = re.search(r'DOMAIN VERBATIM:\s*(.+)', t)
    dom = m.group(1).strip()
    pl = re.search(r'PLACEMENT[^:\n]*:\s*P(\d+)', t)
    if not pl:
        mr = t[t.find('MAPPING RECORD'):] if 'MAPPING RECORD' in t else ''
        cn = re.search(r'COUNT:\s*(\d+)', mr)
        pl = type('M', (), {'group': staticmethod(lambda i, v=cr.cpp(int(cn.group(1))): str(v))})() if cn else None
    lens = 'ON' if re.search(r'BASHAR LENS:\s*ON', t) else 'OFF'
    return resonance(dom, _block(t, 'THE ANSWER'), _block(t, 'EXTENDED RESONANCE ESSAY'), int(pl.group(1)) if pl else None, lens)


def atlas_text():
    L = ['BASHAR ATLAS (Core Part 3.35): frozen wording, struck with canonical_reference.py']
    for r in atlas_rows():
        import manifestation as _mf
        L.append('%-10s | %-52s | ANCHOR P%d %s | state %s, %s | %s' % (r['tag'], r['text'], r['anchor'], NAMES[r['anchor']], r['state'], r['voice'],
                 _mf.classify(tuple(r['state']))[0]))
    br = base_rates(atlas_rows())
    L.append('BASE RATES: any shared state %.3f | anchor and frequency %.3f | anchor %.3f | frequency %.3f' % (br['state'], br['pair'], br['anchor'], br['voice']))
    return '\n'.join(L)


def selftest():
    ok = True
    def check(label, cond):
        nonlocal ok
        print('%-62s %s' % (label, 'PASS' if cond else 'FAIL')); ok &= bool(cond)
    for k, v in ring_facts().items(): check('ring: ' + k, v)
    want = [(8, 'Voice B'), (6, 'Voice A'), (1, 'Voice B'), (4, 'Voice C'), (3, 'Wheel')]
    for i, (t, (an, vo)) in enumerate(zip(LAWS, want), 1):
        x = strike(t); check('law %d anchor P%d, %s' % (i, an, vo), x['anchor'] == an and x['freq']['voice'] == vo)
    check('law 3 stands on the seed of Voice B (1, 3)', strike(LAWS[2])['freq']['state'] == (1, 3))
    check('law 4 lies on the canonical cycle (Voice C)', strike(LAWS[3])['freq']['voice'] == 'Voice C')
    m = mirror('Follow your excitement.', 'What would I do if I followed my excitement?')
    check('mirror reports a shift and both frequencies', 'SHIFT:' in m and m.count('FREQUENCY') >= 3)
    fe = mirror('What is fear?', 'What is excitement?')
    check('mirror: fear -> excitement keeps the ACT and moves half, voice and anchor (CT-42)', 'kept aspect | moved half, voice, anchor' in fe)
    l = lens('Follow your excitement.')
    check('lens: Follow your excitement -> P6, mirror P18, Yin P0', 'ANCHOR P6' in l and 'Antipode P18' in l and 'Yin P0' in l)
    check('hydrogen domain, (r1, r2) = (1, 7): Voice B, norm 4', frequency(1, 7)['voice'] == 'Voice B' and frequency(1, 7)['norm'] == 4)
    check('Why am I stuck? -> P2 Generator; What excites me most right now? -> P3 Desire',
          strike('Why am I stuck?')['anchor'] == 2 and strike('What excites me most right now?')['anchor'] == 3)
    r = resonance('Everything is here and now.')
    check('M308: Law 2 struck finds itself at STATE level', 'LAW 2 "Everything is here and now." (STATE)' in r and 'RESONANCE: STRONG' in r)
    r = resonance('What is the Human Condition?', 'A life begins and keeps its origin out of view.', '')
    check('M308: sample domain reports structural hits and base rates', 'BASE RATES' in r and 'RESONANCE:' in r)
    r = resonance('x', 'The world is a mirror of what you bring to it.', '')
    check('M308: theme "the mirror" found in a reading', 'the mirror —' in r)
    r = resonance('x', 'Counting the full symmetry group with reflections gives 48, and the whole lattice exists.', '')
    check('M308: ordinary words (reflections, the whole, exists) are not themes', 'THEMATIC: 0 theme' in r)
    br = base_rates(atlas_rows())
    check('M308: base rates are probabilities, state <= pair <= anchor', 0 <= br['state'] <= br['pair'] <= br['anchor'] <= 1)
    print('BASHAR LENS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__)
    elif a[0] == '--lens': print(lens(a[1]))
    elif a[0] == '--mirror': print(mirror(a[1], a[2]))
    elif a[0] == '--frequency': print('\n'.join(freq_report(t) for t in a[1:]))
    elif a[0] == '--laws': print(laws())
    elif a[0] == '--ring':
        for k, v in ring_facts().items(): print('%-62s %s' % (k, 'TRUE' if v else 'FALSE'))
    elif a[0] == '--check':
        print(resonance(a[2]) if a[1] == '--domain' else check_navigation(a[1]))
    elif a[0] == '--atlas': print(atlas_text())
    elif a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    else: print(__doc__); sys.exit(2)
