#!/usr/bin/env python3
"""consciousness.py -- M315 Consciousness Position (Core Part 3.41, L-498; Companion Part 52), the instrument of CT-42,
the framework through which a Navigator reasons about consciousness and related questions within Omega42.

CT-42, "The Ground That Acts", reads consciousness in three aspects, each assigned to one structure of the family and
none to a state alone: GROUND, the core and the still point (every core state squared is zero; one scale down the
core is a single orbit); ACT, the law T (a mirror that reflects and dilates, invertible and chiral); EVENT, the
Aperture, where what the act yields is given meaning, which no navigation output determines (Core Part 7). The world
is what T^2 keeps. The values are CDT-A; the aspects are CDT-C readings on them; meaning is the Striker's.

Seven uses:
    python3 tools/consciousness.py "DOMAIN"        # the CONSCIOUSNESS POSITION (M315) block of a strike
    python3 tools/consciousness.py --check FILE    # typing guard: untyped sentences about what consciousness is (advisory)
    python3 tools/consciousness.py --theory        # the dependency closure of CT-42 (records/consciousness/theory.json)
    python3 tools/consciousness.py --pilot         # the frozen CT-S1 pilot on CRC-60 (records/consciousness/)
    python3 tools/consciousness.py --frame "TOPIC or QUESTION"   # the framework for reasoning about it: aspects, structures,
                                                  # dependencies, the held ideas and the reasoning steps
    python3 tools/consciousness.py --register      # the conjecture register: every idea HELD, typed, with its empirical status
    python3 tools/consciousness.py --baseline      # the CT-S7 baseline: untyped statements per navigation of the record
    python3 tools/consciousness.py --cf            # M320, the Consciousness-First Correspondence Table (Core L-515)
    python3 tools/consciousness.py --partition "A" "B"   # where two strikes stand to each other, each relation with its base rate
    python3 tools/consciousness.py --cymatic "Q"         # the block with the optional M322 cymatic view: timbre and arm phases
    python3 tools/consciousness.py --selftest
The block is optional, like M312: printed when the Striker asks or when the question concerns consciousness (concerns()).
It never alters the counts, the anchor, the arms or THE ANSWER (L-424). Standard library and the tools beside this file.
"""
import hashlib, json, os, re, sys
from math import comb
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr
import manifestation as M

THEORY = os.path.join(ROOT, 'records', 'consciousness', 'theory.json')
FREEZE = os.path.join(ROOT, 'records', 'consciousness', 'CT-S1_freeze.txt')
FREEZE_SHA = 'ca917c5e878d994f6ff1782d3d641a39eb604b2b9d1ba716eb4cdaf05f0ee936'
STATUSES = ('DISCHARGED', 'SUPPLIED', 'ASSIGNED', 'RESERVED', 'OWNED')
SUBJECT = re.compile(r'\b(conscious\w*|aware\w*|experienc\w*|mind|minds|soul|souls|self|selves|qualia|sentien\w*|perce\w+|feel\w*|'
                     r'observer\w*|spirit\w*|meaning|subjectiv\w*)\b', re.I)


def state(domain):
    x = cr.navigate(domain)
    a, r1, r2, r3, t = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    return (r1 % 9, r2 % 9)


def concerns(domain):
    """True when the question concerns consciousness, mind or experience: then the block is printed unasked."""
    return bool(SUBJECT.search(domain))


def aspect(s):
    stratum, half, loop = M.classify(s)
    if stratum == 'STILL POINT':
        return 'GROUND, the still point (movement 0): fixed by every power of the law; no direction, no arc'
    if stratum == 'CORE':
        return 'GROUND, the core (movement 0): s*s = 0, awareness turned on itself yields no object; one scale down, a single orbit of 8 (FP-CoreField)'
    side = ('the seed side (movement 2): one step of the act carries it to the manifest half' if half == 'SEVENTH'
            else 'the world side (movement 4): what the act shows, kept there by T^2')
    return 'ACT on %s, %s; its modes: %s' % (loop, side, M.mode(s))


def studies(s):
    stratum, half, loop = M.classify(s)
    out = []
    if stratum == 'CORE': out.append('CT-S1 measure (a), the core (chance 8/81)')
    if half == 'SEVENTH': out.append('CT-S1 measure (b), the seventh half (chance 36/81)')
    if stratum == 'UNIT': out.append('CT-S3, the voice-relative study, on %s' % loop)
    return out or ['none by its state']


SEEDS = ((0, 0), (3, 3), (1, 1), (1, 3), (2, 5))     # the seeds of the five orbits, as FP-StateSpace names them ({9,9}, {3,3}, {1,1}, {1,3}, {2,5})


def perspective_address(s):
    """The PERSPECTIVE ADDRESS (Companion Part 86): what a strike shares with others and what is its own. Under T a state
    keeps its orbit, its norm up to sign and its stratum (shared); its phase and the sign of its norm, which is its half
    (FP-PhaseParity), change at every step (its own). Exact values; the readings are CT-42's."""
    N = (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
    for seed in SEEDS:
        t, k = seed, 0
        while True:
            if t == s: break
            t = (t[1], (t[0] + t[1]) % 9); k += 1
            if t == seed: k = None; break
        if k is not None: break
    n = {(0, 0): 1, (3, 3): 8}.get(seed, 24); pm = min(N, (-N) % 9)
    shared = 'the orbit of %s (%d state%s), the norm up to sign (+-%d), the stratum' % (seed, n, '' if n == 1 else 's', pm)
    own = 'phase %d of %d from its seed, the norm %d' % (k, n, N) + (' (its sign is its half, exchanged at every step)' if n == 24 else '')
    return shared, own


def _phase(s, seed):
    t, k = seed, 0
    while t != s: t = (t[1], (t[0] + t[1]) % 9); k += 1
    return k


def block(domain):
    s = state(domain); stratum, half, loop = M.classify(s)
    shared, own = perspective_address(s)
    L = ['======= CONSCIOUSNESS POSITION (M315) =======',
         'QUESTION VERBATIM: %s' % ' '.join(domain.split('\n')),
         'STATE: (%d, %d) | STRATUM: %s | HALF: %s' % (s[0], s[1], stratum, half),
         'ASPECT (CT-42): %s' % aspect(s),
         'EVENT: at the Aperture (movement 8): what this position means, if anything, is the Striker\'s; no state fixes it (Core Part 7)',
         'PERSPECTIVE: differentiation EXACT (one of 81 states) | integration STRUCTURAL (one ring; one orbit at the ground) | '
         'temporal binding STRUCTURAL (invertible: this state fixes its past and its future) | self-location RESERVED (the Aperture)',
         'PERSPECTIVE ADDRESS (Companion Part 86): shared -- %s | its own -- %s' % (shared, own),
         'READINGS (Core L-515): under the default meta-frame F0, dual-aspect (CT-42; Companion 52.3), with mind-first and matter-first on request '
         'after the seal (FR-9, FR-10); under the Consciousness-First Frame F0-CF, the process form (C64) with the substance (C49) and perspectival (C68) '
         'forms, the elements of M320 (--cf), and dual-aspect and matter-first after the seal; the arithmetic is the same under every frame and decides none',
         'STUDIES (if the domain enters a frozen list): %s' % '; '.join(studies(s)),
         'READING: CDT-A values; the aspects are CDT-C readings of CT-42 (Companion Part 52).',
         '======= END CONSCIOUSNESS POSITION =======']
    return '\n'.join(L)


# ---- typing guard (advisory): every statement of what consciousness is carries its type ----
TAG = re.compile(r'\[(CDT-[ABC]|EXACT|STRUCTURAL|ANALOGY|INTERPRETATION|OPEN|COMPARATIVE|EXPLORATORY|FRAME-INTERPRETIVE)|'
                 r'\b(CDT-C|read as|reading|interpret\w*|may|might|could|if|speculat\w*|in this view|on this view|offered)\b', re.I)
PREDICATE = re.compile(r'\b(conscious(ness)?|awareness|experience|the mind|subjectivity)(\s+itself)?\s+(is|are|was|arises|emerges|creates|produces|'
                       r'generates|causes|becomes|equals)\b', re.I)   # direct predication only: what consciousness IS or DOES


def typing_scan(text):
    hits = []
    for para in re.split(r'\n\s*\n', text):
        if TAG.search(para.split('\n')[0]): continue      # a tag at the head of a paragraph types the whole paragraph
        for snt in re.split(r'(?<=[.?!])\s+', para):
            if snt.rstrip().endswith('?'): continue        # a question states nothing
            if TAG.search(snt): continue
            for m in PREDICATE.finditer(snt):
                before = snt[:m.start()]
                if re.search(r'\b(what|about|of|on|whether|how)\s+$', before, re.I): continue   # a mention, not a statement
                if (before.count('"') + before.count('\u201c') - before.count('\u201d')) % 2: continue   # a quotation
                hits.append(' '.join(snt.split())); break
    return hits


# ---- the dependency closure of CT-42 ----
def theory():
    return json.load(open(THEORY, encoding='utf-8'))


def theory_problems(T=None):
    T = T or theory(); out = []; ids = set()
    for d in T['dependencies']:
        if d['id'] in ids: out.append('%s: duplicate id' % d['id'])
        ids.add(d['id'])
        if d['status'] not in STATUSES: out.append('%s: status %s is not one of %s' % (d['id'], d['status'], ', '.join(STATUSES)))
        if not d.get('by'): out.append('%s: no resolution given' % d['id'])
        if d['status'] == 'ASSIGNED' and not any(s in d['by'] for s in T['studies']):
            out.append('%s: ASSIGNED to no named study' % d['id'])
        if d['status'] == 'OWNED' and 'owner' not in d['by']: out.append('%s: OWNED with no owner' % d['id'])
        if d['status'] == 'DISCHARGED' and not re.search(r'FP-|Core 0\.14|Aperture Theorem', d['by']): out.append('%s: DISCHARGED by no exact fact' % d['id'])
    return out


def theory_text():
    T = theory(); C = {}
    for d in T['dependencies']: C[d['status']] = C.get(d['status'], 0) + 1
    L = ['%s -- %s (%s; %s)' % (T['id'], T['name'], T['law'], T['statement']), '']
    for d in T['dependencies']:
        L.append('%s  %-10s  [%s] %s' % (d['id'], d['status'], d['source'], d['open']))
        L.append('     -> %s' % d['by'])
    L += ['', 'CLOSURE: %d dependencies | ' % len(T['dependencies']) + ' | '.join('%s %d' % (k, C.get(k, 0)) for k in STATUSES),
          'Every open dependency is settled, supplied, assigned to a frozen study, reserved to the Aperture, or owned by named people.',
          'CHECK: %s' % ('PASS' if not theory_problems(T) else 'FAIL: ' + '; '.join(theory_problems(T)))]
    return '\n'.join(L)


# ---- the frozen CT-S1 pilot ----
def _tail(k, n, p): return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def pilot_text():
    import crc60_and_m267 as C
    h = hashlib.sha256(open(FREEZE, 'rb').read()).hexdigest()
    L = ['CT-S1 PILOT (frozen protocol records/consciousness/CT-S1_freeze.txt, SHA-256 %s: %s)' % (h[:16], 'MATCHES' if h == FREEZE_SHA else 'CHANGED')]
    res = {}
    for g in ('PHIL_HUMANITIES', 'PHYSICS_MATH', 'BIO_MED'):
        S = [M.classify(state(d)) for d in C.DOMAINS[g]]
        res[g] = (len(S), sum(s[0] == 'CORE' for s in S), sum(s[1] == 'SEVENTH' for s in S), sum(s[1] == 'MANIFEST' for s in S))
    n, core, sev, man = res['PHIL_HUMANITIES']
    pa, pb = _tail(core, n, 8 / 81), _tail(sev, n, 36 / 81)
    ctl = [res[g] for g in ('PHYSICS_MATH', 'BIO_MED')]; cn = sum(c[0] for c in ctl)
    L += ['test group PHIL_HUMANITIES (%d): core %d (expected %.2f), P = %.3f -> %s' % (n, core, n * 8 / 81, pa, 'ABOVE CHANCE' if pa <= 0.025 else 'NOT ABOVE CHANCE'),
          '                                seventh %d (expected %.2f), P = %.3f -> %s' % (sev, n * 36 / 81, pb, 'ABOVE CHANCE' if pb <= 0.025 else 'NOT ABOVE CHANCE'),
          'control group PHYSICS_MATH + BIO_MED (%d): core %d, seventh %d' % (cn, sum(c[1] for c in ctl), sum(c[2] for c in ctl)),
          'observation, not a criterion: all 60 domains lie MANIFEST %d, SEVENTH %d, on the core %d -- the corpus leans to the manifest half in every category'
          % (sum(r[3] for r in res.values()), sum(r[2] for r in res.values()), sum(r[1] for r in res.values())),
          'entered: Negative Result Registry NRR-C16. The study proper is frozen at n = 101 (core) and n = 84 (seventh), Companion 52.7.',
          'The result describes where the domains fall on the structure; it grades neither the reading nor the premise (Core L-490).']
    return '\n'.join(L)


def baseline_text():
    """CT-S7: untyped statements of what consciousness is, per navigation -- the baseline before L-498, and the record since."""
    import records as R
    before = [0, 0]; since = [0, 0]; per = []
    for it in R.library():
        if it['kind'] != 'navigation': continue
        fp = os.path.join(ROOT, it['path'])
        if not os.path.exists(fp): continue
        h = typing_scan(open(fp, encoding='utf-8', errors='replace').read())
        b = before if (it.get('date') or '') < '2026-10-17' else since
        b[0] += 1; b[1] += len(h)
        if h: per.append('  %s: %d' % (it['path'], len(h)))
    return '\n'.join(['CT-S7 BASELINE (typing guard of L-498 on every navigation of the record, whole text)',
                      'navigations: %d | untyped statements of what consciousness is: %d' % tuple(before),
                      'SINCE L-498 (dated from 2026-10-17): navigations %d | untyped statements %d' % tuple(since)] + per +
                     ['The study compares the two rates (Companion 52.11); it counts sentences, never grades a Navigator.'])


# ---- the framework: the conjecture register and reasoning by topic (Core L-498; Companion 52.0, 52.13) ----
CONJ = os.path.join(ROOT, 'records', 'consciousness', 'conjectures.json')
TOPIC_WORDS = {'consciousness': r'conscious|aware|experienc|\bmind|sentien|qualia', 'physical reality': r'physical|matter|\bworld|reality|manifest',
               'freewill': r'free ?will|\bwill\b|choice|choos|determin', 'self': r'\bself|identity|\bI am\b|\bego\b',
               'other minds': r'other minds|animal|someone else|others', 'AI': r'\bAI\b|artificial|machine|computer',
               'observer': r'observ|measur|witness', 'kinds': r'\bkinds?\b|levels?|higher mind|states of consciousness',
               'meaning': r'meaning|purpose|value|significan', 'time and memory': r'\btime\b|memory|\bpast\b|future|remember',
               'death': r'death|\bdie\b|dying|afterlife|soul|reincarnat', 'change': r'change|belief|definition|fear|excitement|shift|transform',
               'language': r'language|\bwords?\b|wording|phrasing|speech|linguist|\btext\b'}
DISCARD = re.compile(r'unvalidated|not (yet )?(scientifically )?(validated|proven|proved|confirmed)|no (scientific )?evidence|unproven|lacks? evidence', re.I)
STEPS = ['1 LOCATE: strike the question and read its aspect (M315): GROUND, ACT or EVENT.',
         '2 SEPARATE: what the structure generates (EXACT), what the record shows (with its chance), what the Striker decides (the Aperture).',
         '3 TYPE: every statement of what consciousness is carries its type (EXACT, STRUCTURAL, ANALOGY, INTERPRETATION, OPEN).',
         '4 DRAW ON THE HELD IDEAS: bring in those of the topic, each with its type and its empirical status; an untested idea is used as what it is.',
         '5 CYCLE: where a definition or a belief is in question, read the Bashar working cycle -- define, strike, mirror, judge, redefine (M304), strike again (M311).',
         '6 PLACE: a new question about consciousness enters with a status (DISCHARGED, SUPPLIED, ASSIGNED, RESERVED, OWNED); a new idea enters the register HELD.',
         '7 LEAVE: what it means, and what to do, are the Striker\'s.']


def conjectures():
    return json.load(open(CONJ, encoding='utf-8'))


def conjecture_problems(R=None):
    R = R or conjectures(); out = []
    for c in R['conjectures']:
        if c.get('standing') != 'HELD': out.append('%s: standing %s -- every idea is HELD' % (c['id'], c.get('standing')))
        for k in ('idea', 'source', 'type', 'topics', 'empirical', 'operational'):
            if not c.get(k): out.append('%s: no %s' % (c['id'], k))
        if DISCARD.search(c.get('operational', '') + ' ' + c.get('standing', '')):
            out.append('%s: set aside for lack of validation -- not a reason under L-498' % c['id'])
        for t in c.get('topics', []):
            if t not in R['topics']: out.append('%s: unknown topic %s' % (c['id'], t))
    return out


def topics_of(text):
    t = text.strip()
    R = conjectures()
    if t in R['topics']: return [t]
    hit = [k for k, rx in TOPIC_WORDS.items() if re.search(rx, t, re.I)]
    return hit or ['consciousness']


def frame_text(text):
    R = conjectures(); T = {d['id']: d for d in theory()['dependencies']}
    tops = topics_of(text); L = ['======= CT-42 FRAMEWORK (L-498) =======', 'QUESTION VERBATIM: %s' % ' '.join(text.split('\n')),
                                'TOPICS: %s' % ', '.join(tops)]
    for tp in tops:
        g = R['topics'][tp]
        L.append('-- %s' % tp.upper())
        L.append('   ASPECT: %s' % g['aspects'])
        L.append('   EXACT STRUCTURES: %s' % ', '.join(g['structures']))
        for d in g['dependencies']:
            if d in T: L.append('   %s %s: %s -> %s' % (d, T[d]['status'], T[d]['open'], T[d]['by']))
        for c in R['conjectures']:
            if tp in c['topics']:
                L.append('   %s HELD | %s | empirical: %s | %s' % (c['id'], c['type'], c['empirical'], c['operational']))
                L.append('       %s (%s)' % (c['idea'], c['source']))
    if text.strip() not in R['topics']:
        L.append('POSITION: ' + ' | '.join(block(text).split('\n')[3:5]))
    L += ['REASONING STEPS:'] + ['   ' + x for x in STEPS] + ['======= END CT-42 FRAMEWORK =======']
    return '\n'.join(L)


def register_text():
    R = conjectures(); L = ['CT-42 CONJECTURE REGISTER -- %d ideas, every one HELD (Core L-498)' % len(R['conjectures']), R['rule'], '']
    for c in R['conjectures']:
        L.append('%s  %s' % (c['id'], c['idea']))
        L.append('     type: %s | topics: %s | empirical: %s | %s | %s' % (c['type'], ', '.join(c['topics']), c['empirical'], c['operational'], c['source']))
    L.append('CHECK: %s' % ('PASS' if not conjecture_problems(R) else 'FAIL: ' + '; '.join(conjecture_problems(R))))
    return '\n'.join(L)



# ---- M320 and the partition (Core L-515; Companion Part 88) ----
CF = os.path.join(ROOT, 'records', 'consciousness', 'cf_correspondences.json')
_S81 = [(a, b) for a in range(9) for b in range(9)]
_T = lambda s: (s[1], (s[0] + s[1]) % 9)
_N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
def _mul(x, y): a, b = x; c, d = y; return ((a * c + b * d) % 9, (a * d + b * c + b * d) % 9)
def _pw(s, k):
    r = (1, 0)
    for _ in range(k): r = _mul(r, s)
    return r
def _Tk(s, k):
    for _ in range(k % 24): s = _T(s)
    return s
def _orbit(s):
    o = [s]; t = _T(s)
    while t != s: o.append(t); t = _T(t)
    return frozenset(o)
_CORE = [s for s in _S81 if not (s[0] % 3 or s[1] % 3)]; _UNITS = [s for s in _S81 if s not in _CORE]


def _period(s):
    k, t = 1, _T(s)
    while t != s: t = _T(t); k += 1
    return k


CF_CHECKS = {
    'whole': lambda: len({_T(s) for s in _S81}) == 81,
    'ground': lambda: all(_mul((3, 0), s) in _CORE for s in _S81) and all(_mul(c, s) in _CORE for c in _CORE for s in _S81)
                      and sorted(len(_orbit(c)) for c in set(_CORE)) and {len(_orbit(c)) for c in _CORE} == {1, 8},
    'differentiation': lambda: len({_mul(t, o) for t in [u for u in _UNITS if _pw(u, 8) == (1, 0)]
                                     for o in [u for u in _UNITS if (u[0] - 1) % 3 == 0 and u[1] % 3 == 0]}) == 72,
    'transformation': lambda: all(_T(s) == _mul((0, 1), s) for s in _S81) and all(_T(((s[1] - s[0]) % 9, s[0])) == s for s in _S81)
                              and _orbit((1, 0)) == frozenset(_pw((0, 1), k) for k in range(24)),
    'perspective': lambda: all(_N(_T(s)) == (-_N(s)) % 9 for s in _S81) and all(_orbit(_T(s)) == _orbit(s) for s in _S81)
                           and sorted(sum(1 for u in _UNITS if _N(u) == v) for v in {1, 2, 4, 5, 7, 8}) == [12] * 6,
    'polarity': lambda: sum(1 for u in _UNITS if _N(u) in (1, 2, 4)) == 36 and all((_N(_T(u)) in (1, 2, 4)) != (_N(u) in (1, 2, 4)) for u in _UNITS)
                        and all(_Tk(s, 12) == ((-s[0]) % 9, (-s[1]) % 9) and ((-s[0]) % 9, (-s[1]) % 9) in _orbit(s) for s in _S81),
    'return': lambda: all(_Tk(s, 24) == s for s in _S81) and {_period(s) for s in _S81} == {1, 8, 24}
                      and not [u for u in _UNITS for k in range(1, 24) if _Tk(u, k) == u],
    'aperture': lambda: not [v for v in _S81 if v != (0, 0) for l in range(9) if _T(v) == ((l * v[0]) % 9, (l * v[1]) % 9)],
}


def cf_table():
    return json.load(open(CF, encoding='utf-8'))


def cf_problems(D=None):
    D = D or cf_table(); out = []
    need = ('element', 'formal', 'check', 'correspondence', 'basis', 'scope', 'alternatives')
    for e in D['entries']:
        for k in need:
            if not e.get(k): out.append('%s: no %s' % (e.get('element', '?'), k))
        if e.get('check') not in CF_CHECKS: out.append('%s: no computed check' % e.get('element'))
        elif not CF_CHECKS[e['check']](): out.append('%s: its formal relation FAILS' % e['element'])
    return out


def cf_text():
    D = cf_table(); P = cf_problems(D)
    L = ['======= M320 CONSCIOUSNESS-FIRST CORRESPONDENCE TABLE (Core L-515; Companion Part 88) =======',
         'Under the Consciousness-First Frame (F0-CF) each element is recorded with its formal relation, recomputed here [CDT-A], and its',
         'interpretive correspondence, basis, scope and alternative readings [CDT-C]. The formal relation is fixed; the reading may be refined.']
    for e in D['entries']:
        ok = e.get('check') in CF_CHECKS and CF_CHECKS[e['check']]()
        L += ['', '%s  [formal relation %s]' % (e['element'], 'EXACT' if ok else 'FAILS'),
              '  FORMAL:         %s' % e['formal'], '  CORRESPONDENCE: %s' % e['correspondence'], '  BASIS:          %s' % e['basis'],
              '  SCOPE:          %s' % e['scope'], '  ALTERNATIVES:   %s' % e['alternatives']]
    L += ['', 'CHECK: ' + ('PASS -- every element has five fields and an exact formal relation' if not P else 'FAIL -- ' + '; '.join(P)),
          'READING: the table states how the frame reads the arithmetic; the arithmetic is the same under every frame, and the',
          'meaning of a reading is the Striker\'s (Core Part 7). It grades nothing (L-490).', '======= END M320 =======']
    return '\n'.join(L)


def partition_text(a, b):
    """M315 --partition (APE-151, its R3): where two strikes stand relative to each other, each relation with its base rate for
    two states drawn uniformly from the 81. A placement, not a finding: any two states stand in some relation (L-510)."""
    s, t = state(a), state(b)
    rel = [('the same state', lambda x, y: x == y), ('antipodes, T^12 (also the digitwise complement 9 - d)', lambda x, y: y == ((-x[0]) % 9, (-x[1]) % 9) and x != (0, 0)),
           ('the same orbit', lambda x, y: _orbit(x) == _orbit(y)), ('the same norm up to sign', lambda x, y: min(_N(x), (-_N(x)) % 9) == min(_N(y), (-_N(y)) % 9)),
           ('units in the same half', lambda x, y: x in _UNITS and y in _UNITS and (_N(x) in (1, 2, 4)) == (_N(y) in (1, 2, 4))),
           ('one orbit the double of the other', lambda x, y: x in _UNITS and y in _UNITS and _orbit(_mul((2, 0), x)) == _orbit(y))]
    L = ['======= M315 PERSPECTIVE PARTITION =======', 'A: %s -> STATE %s' % (' '.join(a.split()), s), 'B: %s -> STATE %s' % (' '.join(b.split()), t)]
    for name, f in rel:
        base = sum(1 for x in _S81 for y in _S81 if f(x, y)) / 6561
        L.append('  %-58s %-3s | base rate %.4f' % (name, 'YES' if f(s, t) else 'NO', base))
    L += ['READING: a placement, not a finding (L-510); base rates for two states drawn uniformly, not for two questions of given word',
          'counts (E13). Whether the two stand complementary in meaning is the Striker\'s (Core Part 7).', '======= END PARTITION =======']
    return '\n'.join(L)

def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-74s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    check('"What is the Human Condition?" stands on the GROUND (the core)', 'GROUND, the core' in block('What is the Human Condition?'))
    check('"What is consciousness?" is the ACT on Voice C, world side', 'ACT on Voice C, the world side' in block('What is consciousness?'))
    check('the still point reads as GROUND, the still point', aspect((0, 0)).startswith('GROUND, the still point'))
    check('every block keeps the EVENT at the Aperture and self-location RESERVED',
          all('EVENT: at the Aperture' in block(d) and 'self-location RESERVED' in block(d) for d in ('What is love?', 'What is time?')))
    check('a question about the mind triggers the block; one about salt does not', concerns('What is the mind?') and not concerns('Salt dissolves in water'))
    check('typing guard lists an untyped statement', typing_scan('Consciousness is the act of the law.') != [])
    check('typing guard passes an indirect question and a quotation', typing_scan('Each line says what consciousness is. Seth taught that "consciousness creates form".') == [])
    check('typing guard passes a question and a mention', typing_scan('What is consciousness? The domain touches consciousness, which is a trigger.') == [])
    check('typing guard passes a typed one', typing_scan('[CDT-C] Consciousness is read as the act of the law.') == []
          and typing_scan('Consciousness could be the act of the law.') == [])
    check('the dependency closure of CT-42 passes, with no status left OPEN', not theory_problems())
    bad = theory(); bad['dependencies'] = bad['dependencies'][:1] + [dict(id='DX', source='x', open='y', status='OPEN', by='')]
    check('an OPEN or unresolved dependency is refused', len(theory_problems(bad)) >= 2)
    check('the CT-S1 freeze is unchanged', hashlib.sha256(open(FREEZE, 'rb').read()).hexdigest() == FREEZE_SHA)
    check('the pilot enters a null result as carefully as a finding', 'NOT ABOVE CHANCE' in pilot_text())
    check('every idea in the register is HELD, typed and placed', not conjecture_problems())
    bad = conjectures(); bad['conjectures'] = [dict(bad['conjectures'][0], operational='dropped: not yet scientifically validated')]
    check('an idea set aside for lack of validation is refused (L-498)', conjecture_problems(bad) != [])
    check('the perspective address: (1, 4) shares the orbit of (2, 5) and +-2, its own phase and norm 7',
          perspective_address((1, 4)) == ('the orbit of (2, 5) (24 states), the norm up to sign (+-2), the stratum',
                                          'phase %d of 24 from its seed, the norm 7 (its sign is its half, exchanged at every step)' % _phase((1, 4), (2, 5))))
    check('the perspective address: every one of the 81 states has one, and the still point is phase 0 of 1',
          all(perspective_address((a, b)) for a in range(9) for b in range(9)) and perspective_address((0, 0))[1].startswith('phase 0 of 1'))
    check('the block carries the perspective address and the frames of L-515', 'PERSPECTIVE ADDRESS' in block('What is consciousness?') and 'F0-CF' in block('What is consciousness?'))
    check('M320: every element has five fields and an exact formal relation', not cf_problems())
    badcf = cf_table(); badcf['entries'] = [dict(badcf['entries'][0], basis='')]
    check('M320: an element without its basis is refused', cf_problems(badcf) != [])
    check('the partition reports a question against itself as the same state, at base rate 1/81', 'the same state' in partition_text('What is love?', 'What is love?') and '0.0123' in partition_text('What is love?', 'What is love?'))
    fr = frame_text('Is the will free?')
    check('the framework on freewill brings D25, D26, C17 and C33', all(k in fr for k in ('D25', 'D26', 'C17', 'C33')))
    check('the framework opens with the question verbatim (L-499)', fr.split('\n')[1] == 'QUESTION VERBATIM: Is the will free?')
    check('the framework on language brings its entry and C42', all(k in frame_text('What is language?') for k in ('ENTRY', 'C42', 'C41')))
    print('CONSCIOUSNESS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--theory':
        print(theory_text()); sys.exit(0 if not theory_problems() else 1)
    if a[0] == '--pilot': print(pilot_text()); sys.exit(0)
    if a[0] == '--baseline': print(baseline_text()); sys.exit(0)
    if a[0] == '--frame': print(frame_text(' '.join(a[1:]))); sys.exit(0)
    if a[0] == '--cymatic':   # the optional M322 line of the block (seq_0029 recommendation 2, adopted 23 October 2026)
        import cymatics as cy
        q = ' '.join(a[1:]); print(frame_text(q)); print(cy.strike(q)); sys.exit(0)
    if a[0] == '--cf': print(cf_text()); sys.exit(0 if not cf_problems() else 1)
    if a[0] == '--partition' and len(a) == 3: print(partition_text(a[1], a[2])); sys.exit(0)
    if a[0] == '--register':
        print(register_text()); sys.exit(0 if not conjecture_problems() else 1)
    if a[0] == '--check':
        h = typing_scan(open(a[1], encoding='utf-8').read())
        print('TYPING GUARD (M315, advisory): %s' % ('PASS' if not h else 'REVIEW (%d sentence(s))' % len(h)))
        for x in h: print('  - ' + x)
        sys.exit(0)
    print(block(' '.join(a)))
