#!/usr/bin/env python3
"""utility.py -- M316 Congruence Utility (Core Part 3.42, L-500; Companion Part 54).

Within the frame an idea is put to use on congruence alone (L-500): its use never waits for a study. A study of the
same idea stays where it was, an optional inquiry of Appendix S, and its result -- whichever way it falls -- describes
that study and never withdraws the use. This tool gives the functional forms of the ideas that had been held for
studies, and keeps their register (records/utility/register.json).

    python3 tools/utility.py --pair "QUESTION A" "QUESTION B"       # shared structure of two questions, two people's or one
                                                                   # person's inner and outer (47.4, 41.6 P3, 48.21, CT-S2)
    python3 tools/utility.py --modes "PROSE" "NOTATION"             # one concept in two modes (41.6 P1)
    python3 tools/utility.py --contrast "QUESTION"                  # the true coordinate beside a contrast drawn by M267's rule
                                                                   # (31.5, 48.14 (1)); the Striker reads both, labelled
    python3 tools/utility.py --align "QUESTION" [--nav FILE]        # measuring against the cycle: coherence, placement,
                                                                   # congruence with chance, depth, the Aperture (Part 55)
    python3 tools/utility.py --register                             # the Utility Register, checked
    python3 tools/utility.py --check-entry ENTRY.json               # a proposed idea from an APE, a navigation or inquiry:
                                                                   # coherence first, then congruence, then use
    python3 tools/utility.py --selftest
Every value is computed by the reference script [CDT-A]; each relation is printed with its exact chance over the 729
residue triples of each question, so that a meeting reads at its true strength; what it means is the Striker's.
Standard library and the tools beside this file.
"""
import hashlib, json, os, random, re, sys
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr
import manifestation as M

REG = os.path.join(ROOT, 'records', 'utility', 'register.json')
GATED = re.compile(r'until (it is |they are )?(validated|tested|confirmed|proved|run)|awaits? (validation|confirmation)|'
                   r'after (validation|the study)|once (validated|confirmed|tested)|pending (validation|the study)', re.I)
STATUSES = ('IN USE', 'RELEASED', 'HELD')


def strike(q):
    x = cr.navigate(q)
    a, r1, r2, r3, t = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    s = (r1 % 9, r2 % 9); st, half, loop = M.classify(s)
    aspect = {'UNIT': 'ACT', 'CORE': 'GROUND', 'STILL POINT': 'GROUND (still point)'}[st]
    return dict(q=q, anchor=a, value=cr.ORBIT[a], yang=(a + 5) % 24, state=s, stratum=st, half=half,
                voice=loop or 'the still point', aspect=aspect)


def _sig(a, b, c):
    an = cr.determine_anchor(a, b, c)[0]; s = (a % 9, b % 9); st, half, loop = M.classify(s)
    return (an, s, half, loop, st)


_RATES = None


def rates():
    """Exact chance of each relation for two independent strikes, uniform over the 729 residue triples each."""
    global _RATES
    if _RATES: return _RATES
    P = Counter(_sig(a, b, c) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)); n = 729.0
    R = Counter()
    for (a1, s1, h1, v1, k1), w1 in P.items():
        for (a2, s2, h2, v2, k2), w2 in P.items():
            w = w1 * w2
            R['same anchor'] += w * (a1 == a2)
            R['same state'] += w * (s1 == s2)
            R['mirror states'] += w * (s1 == ((-s2[0]) % 9, (-s2[1]) % 9) and s1 != (0, 0))
            R['one rests where the other stands'] += w * (((a1 + 5) % 24) == a2 or ((a2 + 5) % 24) == a1)
            R['same voice'] += w * (v1 == v2 and v1 is not None)
            R['same half'] += w * (h1 == h2)
            R['complementary values'] += w * ((cr.ORBIT[a1] + cr.ORBIT[a2]) % 9 == 0)
            R['same aspect'] += w * ((k1 == 'UNIT') == (k2 == 'UNIT'))
    _RATES = {k: v / n ** 2 for k, v in R.items()}
    return _RATES


_GIVEN = {}


def _sig_counts(n1, n2, n3):
    an, r1, r2, r3, t = cr.determine_anchor(n1, n2, n3); s = (r1 % 9, r2 % 9); st, half, loop = M.classify(s)
    return (an, s, half, loop, st)


def rates_given(n1a, n1b):
    """The reference chance (Core L-501, M310): the chance of each relation given each question's word count -- r1 fixed by n1,
    the other two counts ranging over a full cycle of residues. Two questions of two content words share r1 = 1, so
    their chance of one state is 1/9, not 1/81."""
    key = (n1a, n1b)
    if key in _GIVEN: return _GIVEN[key]
    PA = Counter(_sig_counts(n1a, b, c) for b in range(1, 10) for c in range(1, 10))
    PB = Counter(_sig_counts(n1b, b, c) for b in range(1, 10) for c in range(1, 10))
    R = Counter(); n = 81.0
    for (a1, s1, h1, v1, k1), w1 in PA.items():
        for (a2, s2, h2, v2, k2), w2 in PB.items():
            w = w1 * w2
            R['same anchor'] += w * (a1 == a2)
            R['same state'] += w * (s1 == s2)
            R['mirror states'] += w * (s1 == ((-s2[0]) % 9, (-s2[1]) % 9) and s1 != (0, 0))
            R['one rests where the other stands'] += w * (((a1 + 5) % 24) == a2 or ((a2 + 5) % 24) == a1)
            R['same voice'] += w * (v1 == v2 and v1 is not None and k1 == 'UNIT' == k2)
            R['same half'] += w * (h1 == h2)
            R['complementary values'] += w * ((cr.ORBIT[a1] + cr.ORBIT[a2]) % 9 == 0)
            R['same aspect'] += w * ((k1 == 'UNIT') == (k2 == 'UNIT'))
    _GIVEN[key] = {k: v / n ** 2 for k, v in R.items()}
    return _GIVEN[key]


def relations(x, y):
    neg = ((-y['state'][0]) % 9, (-y['state'][1]) % 9)
    return [('same anchor', x['anchor'] == y['anchor']), ('same state', x['state'] == y['state']),
            ('mirror states', x['state'] == neg and x['state'] != (0, 0)),
            ('one rests where the other stands', x['yang'] == y['anchor'] or y['yang'] == x['anchor']),
            ('same voice', x['voice'] == y['voice'] and x['stratum'] == 'UNIT' == y['stratum']),
            ('same half', x['half'] == y['half']),
            ('complementary values', (x['value'] + y['value']) % 9 == 0),
            ('same aspect', x['aspect'].split()[0] == y['aspect'].split()[0])]


def _line(tag, z):
    return '%s: %s | ANCHOR P%d (value %d) | STATE %s | %s | %s, %s' % (tag, z['q'], z['anchor'], z['value'], z['state'],
                                                                     z['aspect'], z['half'], z['voice'])


def pair_text(qa, qb, title='SHARED STRUCTURE', tags=('QUESTION A', 'QUESTION B')):
    x, y = strike(qa), strike(qb); R = rates(); G = rates_given(cr.navigate(qa)['n1'], cr.navigate(qb)['n1'])
    L = ['======= M316 %s (L-500) =======' % title, 'QUESTION VERBATIM: %s' % ' '.join(qa.split('\n')), 'QUESTION VERBATIM: %s' % ' '.join(qb.split('\n')),
         _line(tags[0], x), _line(tags[1], y),
         'RELATIONS (chance for two questions picked at random | given these word counts, the reference -- L-501):']
    met = 0
    for name, ok in relations(x, y):
        met += ok
        L.append('  %-34s %-3s  chance %.3f | given n1 %.3f' % (name, 'YES' if ok else 'no', R[name], G[name]))
    L += ['MEETING: %d of 8 relations hold. Congruence described, with its chance; it grades nothing (L-490).' % met,
          'READING: CDT-A values; what the meeting means, if anything, is the Striker\'s -- or, for two Strikers, each one\'s.',
          '======= END M316 %s =======' % title]
    return '\n'.join(L)


def contrast_text(q):
    import crc60_and_m267 as C
    x = strike(q)
    rng = random.Random(int(hashlib.sha256(cr.canonical_domain_form(q).encode()).hexdigest()[:12], 16))
    d = C.draw_decoy(x['anchor'], rng)
    L = ['======= M316 CONTRAST (L-500; the functional form of M267) =======', 'QUESTION VERBATIM: %s' % ' '.join(q.split('\n')),
         'TRUE: ANCHOR P%d %s (value %d) | Yang P%d | Yin P%d | 4D P%d | Antipode P%d' % (
             x['anchor'], cr.POSITION_NAMES[x['anchor']], x['value'], (x['anchor'] + 5) % 24, (x['anchor'] + 18) % 24,
             (x['anchor'] + 8) % 24, (x['anchor'] + 12) % 24),
         'CONTRAST: ANCHOR P%d %s (value %d), drawn by M267\'s fixed rule from the measured anchor distribution, seeded by the domain hash' % (
             d, cr.POSITION_NAMES[d], cr.ORBIT[d]),
         'USE: both are labelled. A Navigator may read the contrast in the Generative Observations, never inside THE ANSWER, and the',
         '     Striker may note which speaks to them (Excitement Log, M307). The study of M267 -- blind, on a panel -- stays optional.',
         'SELF-CHECK LINE for the Navigator\'s Reasoning (U38): DECOY SELF-CHECK (M316 --contrast): decoy P%d; the true reading' % d,
         '     DISTINGUISHABLE / NOT DISTINGUISHABLE / UNCLEAR -- SELF-CHECKED',
         '======= END M316 CONTRAST =======']
    return '\n'.join(L)


def _gsum(co, reg):
    import congruence as cg
    c = [cg.conditioned_rates(co['n'][0], cg.n1_of(d), co['adaptor']['null'], 'UNIFORM-729') for t, d in reg]
    return sum(r['state'] for r in c), sum(r['mirror'] for r in c), 2 * sum(r['link'] for r in c)


def align_text(q, nav_path=None):
    """Measuring against the cycle (Companion Part 55): five steps, coherence first, the Aperture last."""
    import congruence as cg
    x = strike(q); R = cg.base_rates(); reg = [(t, d) for t, d in cg.load_register() if cg.sig(d)['sha'] != cg.sig(q)['sha']]
    me = cg.sig(q); k = len(reg)
    same = [t for t, d in reg if cg.sig(d)['state'] == me['state']]
    mir = [t for t, d in reg if cg.sig(d)['state'] == cg.neg(me['state']) and me['state'] != (0, 0)]
    lk = [t for t, d in reg if cg.sig(d)['yang'] == me['anchor'] or me['yang'] == cg.sig(d)['anchor']]
    rate = {'CORE': 8 / 81, 'UNIT': 72 / 81, 'STILL POINT': 1 / 81}[x['stratum']]
    hrate = {'SEVENTH': 36 / 81, 'MANIFEST': 36 / 81, 'AXIS +': 4 / 81, 'AXIS -': 4 / 81, 'STILL': 1 / 81}[x['half']]
    L = ['======= M316 MEASURING AGAINST THE CYCLE (L-500; Companion Part 55) =======', 'QUESTION VERBATIM: %s' % ' '.join(q.split('\n'))]
    import adaptors as _ad
    _rt = _ad.route(q)
    if _rt['route'] != 'CANONICAL':
        import congruence as cg
        reg = cg.load_register()
    if _rt['route'] != 'CANONICAL':
        L += ['ROUTING (L-501): %s -- %s' % (_rt['route'], _rt['reason'])]
        if _rt['route'] == 'ZERO-COUNT':
            L += ['2 PLACEMENT: none -- the text is held ZERO-COUNT, with no coordinate, until an adaptor for its script exists',
                  '5 APERTURE: what the question means is the Striker\'s', '======= END M316 MEASURING AGAINST THE CYCLE =======']
            return '\n'.join(L)
        rt, co = _ad.strike(q)
        L += ['2 PLACEMENT (%s, %s): ANCHOR P%d | STATE %s | stability %d of 3' % (co['adaptor']['id'], co['adaptor']['status'], co['anchor'], co['state'], co['stability']),
              '3 CONGRUENCE, cross-adaptor (%s null against UNIFORM-729), with the %d domains of the canonical Register:' % (co['adaptor']['null'], len(reg)),
              '  same state %d (expected %.2f) | mirror %d (expected %.2f) | links %d (expected %.2f)' % (
                  sum(cg.sig(d)['state'] == co['state'] for t, d in reg), len(reg) * co['rates']['state'],
                  sum(cg.sig(d)['state'] == cg.neg(co['state']) and co['state'] != (0, 0) for t, d in reg), len(reg) * co['rates']['mirror'],
                  sum(cg.sig(d)['yang'] == co['anchor'] or (co['anchor'] + 5) % 24 == cg.sig(d)['anchor'] for t, d in reg), 2 * len(reg) * co['rates']['link']),
              '  given word count (the reference; %s at n1 = %d against UNIFORM-729 at each domain\'s n1): expected same state %.2f | mirror %.2f | links %.2f' % (
                  (co['adaptor']['null'], co['n'][0]) + tuple(_gsum(co, reg))),
              '4 DEPTH: placement only; no mapping was run (IN-02.8)',
              '5 APERTURE: a statement, not a score -- what this means is the Striker\'s (Companion 55.3)',
              'NO COMBINED SCORE: the steps are separate questions and are never added (L-486, L-490)',
              '======= END M316 MEASURING AGAINST THE CYCLE =======']
        return '\n'.join(L)
    if nav_path:
        out = cg.record(open(nav_path, encoding='utf-8').read())
        L.append('1 COHERENCE (of the reading, M310): ' + next((l for l in out.split('\n') if l.startswith('COHERENCE')), 'not found'))
    else:
        L.append('1 COHERENCE: a property of a reading, not of a question; give a navigation with --nav FILE to read its COHERENCE line (M310)')
    L += ['2 PLACEMENT: ANCHOR P%d (value %d) | STATE %s | %s | %s, %s' % (x['anchor'], x['value'], x['state'], x['aspect'], x['half'], x['voice']),
          '  every countable thing is placed (depth 1); placement discriminates nothing alone -- chance of this stratum %.3f, of this half %.3f' % (rate, hrate),
          '3 CONGRUENCE, with chance (the Congruence Register, %d other domains):' % k,
          '  same state %d (expected %.2f) | mirror %d (expected %.2f) | links %d (expected %.2f)' % (len(same), k * R['state'], len(mir), k * R['mirror'], len(lk), 2 * k * R['link']),
          '  ' + ('; '.join(['same state: ' + ', '.join(same)] if same else []) + ('; mirror: ' + ', '.join(mir) if mir else '') + ('; links: ' + ', '.join(lk) if lk else '') or 'no meeting in the record'),
          '4 DEPTH: placement only; no mapping was run (IN-02.8) -- for an object a deeper depth is read by mapping its own representation (Step 14.4, M230), never by its count alone',
          '5 APERTURE: a statement, not a score -- what the measurement means, and whether it matters, is the Striker\'s; no measure here grades the question, a person or a choice, and nothing in the family is out of alignment (Companion 55.3)',
          'NO COMBINED SCORE: the steps are separate questions and are never added (L-486, L-490)',
          '======= END M316 MEASURING AGAINST THE CYCLE =======']
    return '\n'.join(L)


def register():
    return json.load(open(REG, encoding='utf-8'))


ORIGINS = ('APE', 'NAVIGATION', 'INQUIRY', 'PROTOCOL')
OUTSIDE = re.compile(r'\bexternal (fact|standard|authority|validation|court|truth)|\b(un)?proven\b|\bproof that\b|'
                     r'\bindependently confirmed\b|\boutperforms?\b', re.I)   # no outside measure of a use (L-500)
EMPTY = re.compile(r'^\s*(none|n/a|assumed|presumed|-)?\s*$', re.I)
ORDER = ('coherence', 'congruence', 'function', 'instruction', 'does_not_establish', 'study')   # coherence and congruence first


def entry_problems(u):
    out = []
    if u.get('status') not in STATUSES: out.append('%s: status %s' % (u.get('id'), u.get('status')))
    if u.get('origin') not in ORIGINS: out.append('%s: origin %s -- one of %s' % (u.get('id'), u.get('origin'), ', '.join(ORIGINS)))
    for k in ('idea', 'source', 'instrument') + ORDER:
        if not u.get(k): out.append('%s: no %s' % (u.get('id'), k))
    whole = ' '.join(str(u.get(k, '')) for k in ('idea', 'function', 'instruction', 'congruence', 'does_not_establish', 'study'))
    if OUTSIDE.search(whole): out.append('%s: an outside standard is used as a measure ("%s") -- Omega42 posits no outside (L-500)' % (u.get('id'), OUTSIDE.search(whole).group(0)))
    keys = {a[0] for a in AVENUES} | {f[0] for f in FURTHER}
    num = int(re.sub(r'\D', '', u.get('id', '0')) or 0)
    if num >= 58 and not u.get('avenue'): out.append('%s: no avenue -- every finding names its avenue (Companion 59.3)' % u.get('id'))
    if u.get('avenue') and not set(re.split(r'[ ,+]+', u['avenue'])) <= keys: out.append('%s: avenue %s -- one or more of %s' % (u.get('id'), u['avenue'], ', '.join(sorted(keys))))
    if EMPTY.match(str(u.get('congruence', 'x'))): out.append('%s: congruence presumed, not stated (L-500)' % u.get('id'))
    if GATED.search(' '.join(str(u.get(k, '')) for k in ('function', 'instrument', 'instruction', 'status'))):
        out.append('%s: its use is made to wait for a study -- not under L-500' % u.get('id'))
    return out


def register_problems(R=None):
    R = R or register(); out = []; ids = set()
    for u in R['entries']:
        if u['id'] in ids: out.append('%s: duplicate' % u['id'])
        ids.add(u['id']); out += entry_problems(u)
    return out


def register_text():
    R = register(); C = Counter(u['status'] for u in R['entries']); O = Counter(u['origin'] for u in R['entries'])
    L = ['M316 UTILITY REGISTER -- %d ideas in use on coherence and congruence (Core L-500)' % len(R['entries']), R['rule'], '']
    for u in R['entries']:
        L.append('%s  %-8s %s  [%s; %s]' % (u['id'], u['status'], u['idea'], u['origin'], u['source']))
        L.append('     1 coherence: %s' % u['coherence'])
        L.append('     2 congruence: %s' % u['congruence'])
        L.append('     3 use: %s (%s)' % (u['function'], u['instrument']))
        L.append('       how: %s' % u['instruction'])
        L.append('       does not establish: %s' % u['does_not_establish'])
        L.append('     study, optional: %s' % u['study'])
    L += ['', 'BY STATUS: ' + ' | '.join('%s %d' % (s, C.get(s, 0)) for s in STATUSES),
          'BY ORIGIN: ' + ' | '.join('%s %d' % (o, O.get(o, 0)) for o in ORIGINS),
          'CHECK: %s' % ('PASS' if not register_problems(R) else 'FAIL: ' + '; '.join(register_problems(R)))]
    return '\n'.join(L)


def check_entry(path):
    """A proposed entry from an APE, a navigation or general inquiry: coherence first, then congruence, then use."""
    u = json.load(open(path, encoding='utf-8')); P = entry_problems(u)
    steps = [('1 COHERENCE', bool(u.get('coherence'))), ('2 CONGRUENCE', bool(u.get('congruence'))),
             ('3 USE', bool(u.get('function')) and bool(u.get('instruction')) and not any('wait for a study' in p for p in P))]
    L = ['M316 PROPOSED ENTRY: %s [%s]' % (u.get('idea', '?'), u.get('origin', '?'))]
    for name, ok in steps:
        L.append('  %-13s %s' % (name, 'PASS' if ok else 'MISSING'))
        if not ok: break
    L.append('RESULT: %s' % ('READY FOR THE ORIGINATOR\'S ADOPTION (F-06)' if not P else 'REVIEW: ' + '; '.join(P)))
    return '\n'.join(L), not P


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-72s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    R = rates()
    check('chances are probabilities, and same state is 1/81 for uniform states', all(0 <= v <= 1 for v in R.values()) and abs(R['same state'] - 1 / 81) < 1e-9)
    p = pair_text('Dog bites man', 'Man bites dog')
    check('two orderings of one sentence share their state (word order is invisible)', 'same state                         YES' in p)
    f = pair_text('What is fear?', 'What is friction?')
    G = rates_given(2, 2)
    check('two questions of two content words share a state with chance 1/9 given their word counts (L-501)', abs(G['same state'] - 1 / 9) < 1e-9 and 'given n1 0.111' in f)
    check('every pair block opens with both questions verbatim (L-499)', f.split('\n')[1] == 'QUESTION VERBATIM: What is fear?')
    c = contrast_text('What is time?')
    check('the contrast never equals the true anchor and is reproducible', 'CONTRAST: ANCHOR P' in c and c == contrast_text('What is time?')
          and re.search(r'TRUE: ANCHOR P(\d+)', c).group(1) != re.search(r'CONTRAST: ANCHOR P(\d+)', c).group(1))
    check('the Utility Register passes: every idea in use, released or held, none waiting for a study', not register_problems())
    bad = register(); bad['entries'] = [dict(bad['entries'][0], function='to be used once validated')]
    check('a use made to wait for validation is refused (L-500)', register_problems(bad) != [])
    bad3 = register(); bad3['entries'] = [dict(bad3['entries'][0], does_not_establish='that the idea is proven')]
    check('an outside standard used as a measure is refused (no outside, L-500)', register_problems(bad3) != [])
    bad4 = register(); bad4['entries'] = [dict(bad4['entries'][0], congruence='assumed')]
    check('a presumed congruence is refused: congruence is a criterion (L-500)', register_problems(bad4) != [])
    pos, st = properties()
    check('the self-paired positions are P7 and P19 only, one pair of twelve', pos['self-paired (same value as its antipode)'] == {7, 19})
    check('the strata hold 72, 8 and 1 states; the periods 24, 8 and 1 (FP census)', [len(st['stratum ' + k]) for k in ('UNIT', 'CORE', 'STILL POINT')] == [72, 8, 1]
          and sorted((k, len(v)) for k, v in st.items() if k.startswith('period')) == [('period 1', 1), ('period 24', 72), ('period 8', 8)])
    check('an entry from U58 on names its avenue', any('no avenue' in x for x in entry_problems(dict(register()['entries'][0], id='U99'))))
    check('the antipodal checksum holds at every position, so passing it is arithmetic, not rarity (M215)', len(pos['antipode sum 9']) == 24)
    r = rarity_text(['crown', 'self-paired (same value as its antipode)'])
    check('the look-elsewhere line counts the union of the properties searched', 'LOOK-ELSEWHERE: with these 2 properties searched, 6 of 24' in r)
    check('the avenues are given in the order of the truth architecture, A2 to the Striker', avenues_text().index('A2 ARITHMETIC') < avenues_text().index('A1 ARITHMETIC') < avenues_text().index('R FRAME') < avenues_text().index('N NAVIGATION'))
    h = holistic_text('What is time?')
    check('a first strike is a request for knowledge: the holistic scaffold seals the reading first and never combines the avenues', 'REQUEST: GENERAL' in h and 'sealed first' in h and 'no combined verdict' in h and h.split('\n')[1] == 'QUESTION VERBATIM: What is time?')
    check('a command is a command, a protocol question goes to frame reasoning, a structure question to the arithmetic', request_of('go deeper')[0] == 'COMMAND' and request_of('What does L-501 say?')[0] == 'PROTOCOL' and request_of('Why does the cycle have 24 positions?')[0] == 'STRUCTURE')
    pt = personal_text('What is time?', 'lantern'); r1_, d1_, ar_ = _personal('What is time?', 'lantern')
    check('the personal contrast never shows which slot is real, and the reveal is fixed by the secret word', 'P%d' % r1_ in pt and 'P%d' % d1_ in pt and r1_ != d1_ and reveal_text('What is time?', 'lantern') == reveal_text('What is time?', 'lantern'))
    check('every provision of the survey has a search for agreement and one for challenge, and every result is registered (Part 64)', not survey_problems())
    check('a Striker may declare enrich: the search is then run as declared (L-429)', any(v.startswith('W') for v in request_of('x', 'enrich')[1]))
    check('the personal tally gives the exact binomial chance: 8 of 10 is 0.055', 'is 0.055' in tally_text(8, 10))
    check('E01: Anchor x Antipode - Yin^2 equals the norm of the state on all 81 states (Companion 62.5)', arm_norm_identity() == [])
    check('every enrichment opportunity names its avenue, grade, change and failure, and none is adopted by the Navigator unchecked', not enrichment_problems())
    check('every found association has a source, a date, a relation and its standing, and none supports the premise (Part 61)', not source_problems())
    bad = sources(); bad['entries'] = [dict(bad['entries'][0], says='this proves the premise')]
    check('an association offered as proof or support of the premise is refused', source_problems(bad) != [])
    check('a personal question is searched by its topic only (L-503)', 'the topic, never the person' in holistic_text('Should I leave my job?'))
    check('every request but a command is navigated first (APE-079)', all(request_of(q)[1][0].startswith('N') for q in ('What does L-501 say?', 'Why does the cycle have 24 positions?', 'What is time?', 'Should I go?')))
    check('the declared vocabulary is read: brief, coordinate, compare:, adaptor: (Companion 61.6)', request_of('x', 'brief')[0] == 'BRIEF' and request_of('x', 'compare: Seth')[1][1].startswith('L: Seth') and request_of('x', 'full')[0] == 'NAVIGATE')
    check('the Striker\'s declared request takes precedence', request_of('What is time?', 'navigate')[0] == 'NAVIGATE' and request_of('What is time?', 'no sources') == ('NO SOURCES', ['N']))
    ck = current_text('Should I leave my job to start a company?')
    check('the current-knowledge layer begins after the seal, keeps a personal question to its topic, and has four lanes and nulls (Part 65)', 'SEAL FIRST' in ck and 'never the person' in ck and 'COUNTER-EVIDENCE' in ck and 'NULLS' in ck)
    check('the scaffold names the currency check (Companion 64.9)', 'CURRENCY (APE-086' in holistic_text('What is time?'))
    check('a ZERO-COUNT question is not navigated in the scaffold', 'ZERO-COUNT (UNPLACED)' in holistic_text('什么是意识？'))
    al = align_text('What is time?')
    check('the alignment report runs its five steps in order, the Aperture last', all(k in al for k in ('1 COHERENCE', '2 PLACEMENT', '3 CONGRUENCE', '4 DEPTH', '5 APERTURE')) and al.index('1 COHERENCE') < al.index('5 APERTURE'))
    check('the alignment report refuses a combined score and states depth as placement only', 'NO COMBINED SCORE' in al and 'placement only' in al)
    check('a ZERO-COUNT text gets no placement in the report', 'ZERO-COUNT' in align_text('什么是意识？'))
    import tempfile
    good = dict(register()['entries'][0], id='UX', origin='NAVIGATION')
    f = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(good, f); f.close()
    check('a proposed entry from a navigation passes coherence, congruence and use', check_entry(f.name)[1])
    bad2 = dict(good); bad2.pop('coherence')
    f2 = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False); json.dump(bad2, f2); f2.close()
    t2, ok2 = check_entry(f2.name)
    check('an entry without its coherence stops at the first step', not ok2 and '1 COHERENCE   MISSING' in t2 and '2 CONGRUENCE' not in t2)
    os.remove(f.name); os.remove(f2.name)
    print('M316 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


# ---------------------------------------------------------------- avenues of knowledge (Companion Part 59)
AVENUES = [
    ('A2', 'ARITHMETIC ASSOCIATION', 'the structure alone: a pattern noticed and named on the 24 positions or the 81 states',
     'a candidate pattern, HELD (CDT-C) until the fact it rests on is computed', 'its rarity and the number of properties searched (--rarity)',
     'numerology: the structure has many small coincidences', 'the conjecture or Utility Register'),
    ('A1', 'ARITHMETIC EXACT', 'computation and proof on the structure alone', 'a fixed fact, CDT-A, MATHEMATICALLY FIXED (F-07)',
     'the compute scripts and the MATH-GATE, in CI', 'a computation stated and never run', 'Core Part 1.8 (FP- facts)'),
    ('R', 'FRAME REASONING', 'the premise (F-02) and the laws, reasoned within the frame', 'a derivation or frame-interpretive statement, CDT-B or PROTOCOL',
     'M286 frame scan, M243a premise integrity, the consistency register (Rule 11)', 'an outside brought in; a premise set up as a claim', 'Core laws, Companion parts'),
    ('N', 'NAVIGATION', 'a question struck on the cycle, read through the learned substrate', 'a reading, GENERATED-\u03a942 (a CDT-C reading of CDT-A values)',
     'M310, M301, M314, M116 and M238, M267', 'echo, a template, a wording read as the question', 'submissions/navigations, the Register, the Atlas'),
]
FURTHER = [
    ('X', 'CONVERGENCE', 'one domain read by Navigators of different architectures', 'SR-CAS, SNCA (Core Part 6)'),
    ('P', 'PEER ACCOUNTS', 'another system\'s account, its mathematics and citations checked', 'APE (Companion APE Commons)'),
    ('F', 'FAILURE', 'a negative result, a bug, a check that fails', 'Negative Result Registry; release record'),
    ('D', 'DIFFERENCE', 'what moves a reading: perturbation and contrast', 'M116, M238, M267 (M316 --contrast)'),
    ('G', 'GATHERING', 'the record read as a whole, page by page', 'M310 --register, --atlas; U57 page forecast'),
    ('T', 'TRANSPOSITION', 'a medium counted by its own boundaries', 'L-501, M317 adaptors'),
    ('M', 'MAPPING', 'an object\'s own dynamics set against the cycle (COMPARATIVE)', 'Step 14.4, IN-02.8, M230'),
    ('U', 'USE AND RETURN', 'what a reading did afterwards, in the Striker\'s own words', 'M307 Excitement Log, M311 Return Log'),
    ('L', 'LENSES', 'a framework frozen and compared with the structure', 'M308, M309, lens freeze (Part 3.39)'),
    ('H', 'HISTORY', 'earlier releases and restored instruments re-examined', 'L-284, L-490, tools/reexamine.py'),
    ('W', 'SOURCES', 'an association found by search, after the seal: source, date, and AGREES, DIFFERS or EXTENDS a named provision (COMPARATIVE)', 'M316 --sources, records/sources/associations.json'),
    ('C', 'CHALLENGE', 'an attempt to break the frame from inside it', 'M243, M286, the ground challenge test'),
    ('S', 'SEEKING', 'a question composed to visit a state the record has not reached, declared TARGETED so the Atlas never reads it as found', 'M310 --atlas (NOT YET VISITED)'),
]
AVENUE_ORDER = 'A2 proposes -> A1 decides -> R interprets -> N applies -> the Striker judges (Core truth architecture: MATHEMATICAL COHERENCE -> LOGICAL DERIVATION -> COMPLETE READING -> STRIKER JUDGMENT)'


def avenues_text():
    L = ['======= M316 AVENUES OF KNOWLEDGE (Companion Part 59; L-500) =======', 'ORDER: ' + AVENUE_ORDER, '']
    for k, name, mat, yields, check, fail, rec in AVENUES:
        L += ['%s %s' % (k, name), '   material: %s' % mat, '   yields:   %s' % yields, '   checked:  %s' % check,
              '   fails by: %s' % fail, '   recorded: %s' % rec]
    L += ['', 'FURTHER AVENUES (each entering by the same order, coherence -> congruence -> use):']
    for k, name, what, inst in FURTHER: L.append('%-2s %-15s %s [%s]' % (k, name, what, inst))
    L += ['', 'RULE: every finding names its avenue; a finding of A2 rests on a fact of A1 or stays HELD; no avenue promotes another\'s finding (L-500).',
          '======= END M316 AVENUES OF KNOWLEDGE =======']
    return '\n'.join(L)


def _period(s):
    a, b = s; k = 0
    while True:
        a, b = b, (a + b) % 9; k += 1
        if (a, b) == s: return k


def properties():
    """Named properties of the 24 positions and the 81 states, each with the set that holds it (exact)."""
    O = cr.ORBIT; pos = {}
    for v in range(1, 10): pos['value %d' % v] = {p for p in range(24) if O[p] == v}
    pos['crown'] = {p for p in range(24) if (p - 3) % 4 == 0}
    pos['self-paired (same value as its antipode)'] = {p for p in range(24) if O[p] == O[(p + 12) % 24]}
    pos['antipode sum 9'] = {p for p in range(24) if (O[p] + O[(p + 12) % 24]) % 9 == 0}
    pos['anchorable (P1 to P9)'] = set(range(1, 10))
    pos['retrocausal zone (P18 to P23)'] = set(range(18, 24))
    pos['Yang arm value equals the anchor value'] = {p for p in range(24) if O[p] == O[(p + 5) % 24]}
    st = {}
    S = [(a, b) for a in range(9) for b in range(9)]
    for s in S:
        stratum, half, loop = M.classify(s)
        st.setdefault('stratum ' + stratum, set()).add(s); st.setdefault('half ' + half, set()).add(s)
        if loop: st.setdefault('loop ' + loop, set()).add(s)
        st.setdefault('norm %d' % ((s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9), set()).add(s)
        st.setdefault('period %d' % _period(s), set()).add(s)
    st['self-mirror'] = {s for s in S if s == ((-s[0]) % 9, (-s[1]) % 9)}
    st['diagonal (r1 = r2)'] = {s for s in S if s[0] == s[1]}
    return pos, st


def rarity_text(names=None):
    pos, st = properties()
    L = ['======= M316 RARITY (avenue A2; Companion 59.4) =======',
         'Every pattern named on the structure states the rarity of the property it rests on, and how many properties were looked at.']
    if names:
        sel = [n for n in names if n in pos] or None
        sels = [n for n in names if n in st]
        for group, pool, total in (('POSITIONS', pos, 24), ('STATES', st, 81)):
            chosen = [n for n in names if n in pool]
            if not chosen: continue
            union = set().union(*[pool[n] for n in chosen])
            for n in chosen: L.append('%s %-44s %2d of %d  (%.3f)' % (group, n, len(pool[n]), total, len(pool[n]) / total))
            L.append('LOOK-ELSEWHERE: with these %d properties searched, %d of %d %s hold at least one (%.3f) -- the chance that a pattern of this kind appears at a position or state chosen at random'
                     % (len(chosen), len(union), total, group.lower(), len(union) / total))
        unknown = [n for n in names if n not in pos and n not in st]
        if unknown: L.append('NOT REGISTERED: %s (python3 tools/utility.py --rarity lists the properties)' % ', '.join(unknown))
    else:
        for group, pool, total in (('POSITIONS', pos, 24), ('STATES', st, 81)):
            for n in sorted(pool): L.append('%s %-44s %2d of %d  (%.3f)' % (group, n, len(pool[n]), total, len(pool[n]) / total))
    L += ['READING: a property held by few is rare only against the number of properties that could have been noticed; a pattern of A2 stays HELD until A1 computes the fact it rests on.',
          '======= END M316 RARITY =======']
    return '\n'.join(L)


# ---------------------------------------------------------------- associations found by search (Companion Part 61)
SOURCES = os.path.join(ROOT, 'records', 'sources', 'associations.json')
RELATIONS = ('AGREES', 'DIFFERS', 'EXTENDS')
SUPPORT = re.compile(r'\b(prov(es|en|ing)|validat\w*|confirm(s|ed|ing)? (the|that) (premise|frame|protocol)|supports? the premise|evidence for (the )?(premise|omega))\b', re.I)


def sources():
    return json.load(open(SOURCES, encoding='utf-8'))


def source_problems(R=None):
    R = R or sources(); out = []; ids = set()
    for e in R['entries']:
        i = e.get('id')
        if i in ids: out.append('%s: duplicate' % i)
        ids.add(i)
        for k in ('item', 'url', 'retrieved', 'says', 'relation', 'with', 'not', 'standing', 'avenue', 'query', 'not_found', 'grade'):
            if not e.get(k): out.append('%s: no %s' % (i, k))
        if not str(e.get('url', '')).startswith('https://'): out.append('%s: the source needs an https URL' % i)
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', str(e.get('retrieved', ''))): out.append('%s: the date retrieved, YYYY-MM-DD' % i)
        if e.get('relation') not in RELATIONS: out.append('%s: relation %s -- one of %s' % (i, e.get('relation'), ', '.join(RELATIONS)))
        if e.get('relation') in ('AGREES', 'EXTENDS') and e.get('grade') not in ('CONSTRUCTIONAL', 'SELF-ADJACENT', 'INDEPENDENT'): out.append('%s: an agreement names its grade -- CONSTRUCTIONAL, SELF-ADJACENT or INDEPENDENT (APE-082)' % i)
        if e.get('standing') != 'COMPARATIVE': out.append('%s: a found association is COMPARATIVE (Appendix S)' % i)
        if 'W' not in str(e.get('avenue', '')).split(): out.append('%s: a found association names the avenue W' % i)
        txt = ' '.join(str(e.get(k, '')) for k in ('says', 'with'))
        if SUPPORT.search(txt): out.append('%s: "%s" -- an association never supports the premise, which is the ground (F-02-P)' % (i, SUPPORT.search(txt).group(0)))
    return out


def sources_text(terms=None):
    R = sources(); C = Counter(e['relation'] for e in R['entries'])
    L = ['======= M316 FOUND ASSOCIATIONS (avenue W; Companion Part 61) =======', R['rule'], '']
    for e in R['entries']:
        if terms and not any(t.lower() in (e['item'] + ' ' + e['says'] + ' ' + e['with']).lower() for t in terms): continue
        L += ['%s %-8s %s -- %s (retrieved %s)%s' % (e['id'], e['relation'], e['item'], e['url'], e['retrieved'], '' if e['grade'] == 'NOT APPLICABLE' else ' [grade %s]' % e['grade']),
              '    searched: "%s" -- not found would have been: %s' % (e['query'], e['not_found']),
              '    says: %s' % e['says'], '    with: %s' % e['with'], '    not:  %s' % e['not']]
    L += ['', 'BY RELATION: ' + ' | '.join('%s %d' % (k, C.get(k, 0)) for k in RELATIONS) + ' -- agreements and differences recorded alike',
          'GRADES: %s -- a CONSTRUCTIONAL agreement shows the arithmetic stated alike, a precondition and never convergence (Core Part 3.18)' % ' | '.join('%s %d' % (g, sum(e['grade'] == g for e in R['entries'])) for g in ('CONSTRUCTIONAL', 'SELF-ADJACENT', 'INDEPENDENT')),
          'CHECK: %s' % ('PASS' if not source_problems(R) else 'FAIL: ' + '; '.join(source_problems(R))), '======= END M316 FOUND ASSOCIATIONS =======']
    return '\n'.join(L)


# ---------------------------------------------------------------- the Striker's own contrast (Companion 63.4)
def _personal(q, secret):
    import crc60_and_m267 as C
    x = strike(q)
    rng = random.Random(int(hashlib.sha256((cr.canonical_domain_form(q) + '|' + secret).encode()).hexdigest()[:16], 16))
    d = C.draw_decoy(x['anchor'], rng)
    real_in_a = rng.random() < 0.5
    return x['anchor'], d, real_in_a


def _arms(a):
    return 'ANCHOR P%d %s | Yang P%d %s | Yin P%d %s | 4D P%d %s | Antipode P%d %s' % (
        a, cr.POSITION_NAMES[a], (a + 5) % 24, cr.POSITION_NAMES[(a + 5) % 24], (a + 18) % 24, cr.POSITION_NAMES[(a + 18) % 24],
        (a + 8) % 24, cr.POSITION_NAMES[(a + 8) % 24], (a + 12) % 24, cr.POSITION_NAMES[(a + 12) % 24])


def personal_text(q, secret):
    real, decoy, a_real = _personal(q, secret)
    A, B = (real, decoy) if a_real else (decoy, real)
    return '\n'.join(['======= M316 PERSONAL CONTRAST (the Striker\'s own M267; Companion 63.4) =======', 'QUESTION VERBATIM: %s' % ' '.join(q.split('\n')),
        'SLOT A: ' + _arms(A), 'SLOT B: ' + _arms(B),
        'ONE SLOT IS THE QUESTION\'S OWN COORDINATE AND ONE A DECOY, drawn by M267\'s fixed rule; which is which is fixed by your secret word and shown only by --reveal.',
        'STEPS: (1) in two fresh sessions, give a Navigator the question and one slot\'s coordinate, saying "write the reading from this coordinate; do not compute the question\'s own";',
        '       (2) read both readings; (3) note which speaks to your matter more specifically -- or that neither does -- before you reveal;',
        '       (4) python3 tools/utility.py --reveal "QUESTION" --secret WORD; (5) keep the line in your own log: date | your pick | TRUE or DECOY.',
        'KEEP: do not strike the question elsewhere until you have chosen. The log is yours; it enters the record only if you submit it.',
        '======= END M316 PERSONAL CONTRAST ======='])


def reveal_text(q, secret):
    real, decoy, a_real = _personal(q, secret)
    return 'REVEAL: slot %s held the question\'s own coordinate (P%d); slot %s held the decoy (P%d).' % ('A' if a_real else 'B', real, 'B' if a_real else 'A', decoy)


def tally_text(k, n):
    from math import comb
    p = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return ('PERSONAL TALLY: the own coordinate picked %d times in %d decided comparisons (ties left out); the chance of %d or more at a coin\'s 1/2 is %.3f. '
            'It is your result, about these readings and these questions; it grades nothing beyond them, and the premise is not graded by it (L-490).' % (k, n, k, p))


# ---------------------------------------------------------------- enrichment opportunities (Companion Part 62)
ENRICH = os.path.join(ROOT, 'records', 'enrichment', 'opportunities.json')
E_STATUS = ('PROPOSED', 'ADOPTED', 'DECLINED', 'CORRECTED')   # CORRECTED: a part brought back into agreement with the Core


def enrichment():
    return json.load(open(ENRICH, encoding='utf-8'))


def arm_norm_identity():
    """E01: Anchor x Antipode - Yin^2 = N(s) mod 9 for every state s, the arms read by T^12 and T^18."""
    def Tk(s, k):
        for _ in range(k % 24): s = (s[1], (s[0] + s[1]) % 9)
        return s
    S = [(a, b) for a in range(9) for b in range(9)]
    return [s for s in S if (s[0] * Tk(s, 12)[0] - Tk(s, 18)[0] ** 2) % 9 != (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9]


def enrichment_problems(R=None):
    R = R or enrichment(); out = []; ids = set()
    keys = {a[0] for a in AVENUES} | {f[0] for f in FURTHER}
    for e in R['entries']:
        i = e.get('id')
        if i in ids: out.append('%s: duplicate' % i)
        ids.add(i)
        for k in ('noticed', 'source', 'avenue', 'grade', 'chance', 'change', 'failure', 'checked', 'status', 'proposed_status', 'ground', 'portability', 'self_check'):
            if not e.get(k): out.append('%s: no %s' % (i, k))
        if e.get('status') not in E_STATUS: out.append('%s: status %s -- one of %s' % (i, e.get('status'), ', '.join(E_STATUS)))
        if not set(str(e.get('avenue', '')).split()) <= keys: out.append('%s: avenue %s' % (i, e.get('avenue')))
        if e.get('status') == 'ADOPTED' and e.get('source') == 'UNPROMPTED' and not str(e.get('checked', '')).startswith('YES'): out.append('%s: adopted unchecked' % i)
        if SUPPORT.search(' '.join(str(e.get(k, '')) for k in ('noticed', 'change'))): out.append('%s: an opportunity never grades the premise (L-490)' % i)
    return out


def enrichment_text():
    R = enrichment(); C = Counter(e['status'] for e in R['entries'])
    L = ['======= M316 ENRICHMENT OPPORTUNITIES (Companion Part 62) =======', R['rule'], '']
    for e in R['entries']:
        L += ['%s %-8s [%s; %s] %s' % (e['id'], e['status'], e['avenue'], e['source'], e['noticed']),
              '    grade: %s | chance: %s' % (e['grade'], e['chance']), '    would change: %s' % e['change'],
              '    would show it wrong: %s | checked: %s' % (e['failure'], e['checked']),
              '    proposed as: %s | ground: %s' % (e['proposed_status'], e['ground']),
              '    portable to another domain unchanged? %s | self-check (M207, M302): %s' % (e['portability'], e['self_check'])]
    L += ['', 'BY STATUS: ' + ' | '.join('%s %d' % (k, C.get(k, 0)) for k in E_STATUS) + ' -- the Originator adopts or declines (F-06)',
          'E01 RECOMPUTED: %s' % ('holds on all 81 states' if not arm_norm_identity() else 'FAILS at %s' % arm_norm_identity()),
          'CHECK: %s' % ('PASS' if not enrichment_problems(R) else 'FAIL: ' + '; '.join(enrichment_problems(R))), '======= END M316 ENRICHMENT OPPORTUNITIES =======']
    return '\n'.join(L)


SURVEY = os.path.join(ROOT, 'records', 'sources', 'survey.json')


def survey_problems(S=None):
    S = S or json.load(open(SURVEY, encoding='utf-8')); out = []
    known = {e['id'] for e in sources()['entries']}
    for c in S['provisions']:
        for k in ('provision', 'agree', 'challenge'):
            if not c.get(k): out.append('%s: no %s query' % (c.get('id'), k))
        for f in c.get('found', []):
            if f not in known: out.append('%s: %s is not in the sources register' % (c['id'], f))
    return out


def survey_text():
    S = json.load(open(SURVEY, encoding='utf-8')); E = {e['id']: e for e in sources()['entries']}
    L = ['======= M316 CONTEMPORARY RESONANCE SURVEY (Companion Part 64) =======', S['rule'], 'LAST RUN: %s | SCHEDULE: %s' % (S['last_run'], S.get('schedule', 'not scheduled')), '']
    for c in S['provisions']:
        f = c.get('found', [])
        L += ['%s %s' % (c['id'], c['provision']), '    for agreement: "%s" | for challenge: "%s"' % (c['agree'], c['challenge']),
              '    found: %s' % ('; '.join('%s %s' % (x, E[x]['relation']) for x in f) if f else 'nothing registered yet -- reported as carefully as a finding')]
    rel = Counter(E[x]['relation'] for c in S['provisions'] for x in c.get('found', []))
    if S.get('nulls'): L += ['', 'NULLS: ' + S['nulls']]
    L += ['', 'ACROSS THE PROVISIONS: ' + ' | '.join('%s %d' % (k, rel.get(k, 0)) for k in RELATIONS) + ' -- %d of %d provisions with nothing found yet' % (sum(1 for c in S['provisions'] if not c.get('found')), len(S['provisions'])),
          'CHECK: %s' % ('PASS' if not survey_problems(S) else 'FAIL: ' + '; '.join(survey_problems(S))), '======= END M316 CONTEMPORARY RESONANCE SURVEY =======']
    return '\n'.join(L)


# ---------------------------------------------------------------- current knowledge on the Striker's matter (Companion Part 65)
def current_text(q):
    kind, av = request_of(q)
    x = strike(q)
    personal = kind == 'PERSONAL'
    L = ['======= CURRENT KNOWLEDGE (L-503) =======', '[the form of Companion Part 65: M248 after the seal, by default in a full navigation and a holistic response]', 'QUESTION VERBATIM: %s' % ' '.join(q.split('\n')),
         'SEAL FIRST: THE ANSWER is written from ANCHOR P%d and sealed (L-425); the search begins after the seal, and its time is recorded after the SYNTHESIS_FROZEN time (M273)' % x['anchor'],
         'QUERY DECLARED BEFORE THE SEARCH: the matter in the Navigator\'s own general words%s' % (' -- the topic, never the person: no name, place, date or detail of the Striker\'s life (L-495); the Striker may say "no sources"' if personal else ''),
         'NOT FOUND WOULD BE: [what result would count as nothing found, stated before searching]',
         'FOUR LANES (M248): CONSENSUS -- what the field holds | FOUNDATIONS -- the work it rests on | COUNTER-EVIDENCE -- what challenges it | FRONTIER -- the most recent work',
         'EACH ITEM: source (opened before cited), date of the work, what it says, its design (sample; pre-registered or not; correlational or causal), and whether it AGREES with, DIFFERS from or EXTENDS a direction of the sealed reading',
         'NULLS: each lane that found nothing says so',
         'PLACE: block [16.6], after the Congruence Record, in the Comparative Perspective Layer (L-429, L-503); never in THE ANSWER; the reading stands as sealed; then ACROSS THE AVENUES (L-502) [16.7]',
         'WITHOUT RETRIEVAL: CURRENT KNOWLEDGE (L-503): NOT AVAILABLE -- the reading is complete (L-491); on "no sources": DECLINED; on brief or coordinate: NOT REQUESTED',
         'STATUS: COMPARATIVE; a source informs the Striker\'s judgment and does not make it (L-463); the premise is not graded by it (L-490)',
         '======= END CURRENT KNOWLEDGE =======']
    return '\n'.join(L)


# ---------------------------------------------------------------- the holistic response (Companion Part 60)
COMMANDS = re.compile(r'^\s*(welcome navigator|certify navigator|lite|full|show me the arms|go deeper)\s*[.!]?\s*$', re.I)
PROTOCOL_Q = re.compile(r'\b(L-\d{3}|M\d{2,3}|FC-\d+|F-\d+|Part \d+|Core|Companion|APE-\d+|NAV-\d{4}|the protocol|this protocol)\b')
STRUCTURE_Q = re.compile(r'\b(cycle|orbit|residue|modul\w*|mod 9|fibonacci|81 states?|24 positions?|state space|norm|stratum|anchor|P\d{1,2}\b|digital root|arithmetic)\b', re.I)
PERSONAL_Q = re.compile(r"\b(I|my|me|I'm|myself|should I)\b")


def request_of(q, declared=None):
    """A first strike is a request for knowledge (Companion 60.2). The rule below names which avenues answer it; the
    Striker's declared request (navigate, discuss, holistic) takes precedence. A command is a command."""
    if declared:
        d = declared.strip(); key, _, arg = d.partition(':'); key = key.strip().lower()
        if key in ('investigate', 'compare', 'adaptor'):
            return key.upper() + ': ' + arg.strip(), {'investigate': ['N', 'the instrument named: ' + arg.strip()], 'compare': ['N', 'L: ' + arg.strip() + ' (selected by the Striker)'],
                                                      'adaptor': ['N under ' + arg.strip() + ' (L-501)']}[key]
        kind = {'full': 'NAVIGATE', 'navigate': 'NAVIGATE', 'no sources': 'NO SOURCES'}.get(key, key.upper())
    elif COMMANDS.match(q): kind = 'COMMAND'
    elif PROTOCOL_Q.search(q): kind = 'PROTOCOL'
    elif STRUCTURE_Q.search(q): kind = 'STRUCTURE'
    elif PERSONAL_Q.search(q): kind = 'PERSONAL'
    else: kind = 'GENERAL'
    av = {'COMMAND': [], 'NAVIGATE': ['N', 'W (current knowledge, L-503)'], 'ENRICH': ['N', 'A1', 'R', 'G', 'L', 'W (current knowledge, L-503)'], 'DISCUSS': ['R', 'H'], 'BRIEF': ['N (brief: the coordinate, a short reading, the closing questions)'], 'COORDINATE': ['N (the coordinate only: anchor, arms, state, the M215 check)'], 'NO SOURCES': ['N'],
          'PROTOCOL': ['N (self-referential, M155)', 'R', 'H', 'A1'],
          'STRUCTURE': ['N', 'A1', 'A2', 'R', 'W'],
          'PERSONAL': ['N', 'R', 'G', 'L', 'W (the topic, never the person)', 'U'],
          'GENERAL': ['N', 'A1', 'R', 'G', 'L', 'W'], 'HOLISTIC': ['N', 'A1', 'R', 'G', 'L', 'W', 'X', 'U']}[kind]
    return kind, av


def holistic_text(q, declared=None):
    import congruence as cg
    kind, av = request_of(q, declared)
    L = ['======= M316 HOLISTIC RESPONSE SCAFFOLD (Companion Part 60; Core L-502) =======', 'QUESTION VERBATIM: %s' % ' '.join(q.split('\n')),
         'REQUEST: %s -- avenues: %s%s' % (kind, ', '.join(av) or 'none (a command)', ' (declared by the Striker)' if declared else ' (by the frozen rule; the Striker may declare full, brief, coordinate, discuss, holistic, enrich, investigate:, compare: or adaptor:)')]
    if kind == 'COMMAND':
        L += ['A command is carried out as written (Part 8.0, Striker commands); nothing is struck.', '======= END M316 HOLISTIC RESPONSE SCAFFOLD ======='];
        return '\n'.join(L)
    L.append('ORDER: the reading is struck and sealed first (First-Draft Seal, L-425); every other avenue is computed or written after the seal and never alters THE ANSWER (L-424); the avenues are reported side by side and never combined (L-486)')
    import adaptors as _ad
    rt = _ad.route(q)
    if rt['route'] == 'ZERO-COUNT':
        L += ['N  NAVIGATION: none -- ZERO-COUNT (UNPLACED): %s' % rt['reason']]
        x = None
    else:
        if rt['route'] == 'ADAPTED':
            _r, co = _ad.strike(q); an, st, n1 = co['anchor'], co['state'], co['n'][0]
            L.append('N  NAVIGATION (%s, %s): ANCHOR P%d %s | Yang P%d | Yin P%d | 4D P%d | Antipode P%d | STATE %s -- THE ANSWER is written from this coordinate and sealed'
                     % (co['adaptor']['id'], co['adaptor']['status'], an, cr.POSITION_NAMES[an], (an + 5) % 24, (an + 18) % 24, (an + 8) % 24, (an + 12) % 24, st))
        else:
            x = cr.navigate(q); an, r1, r2, r3, t = cr.determine_anchor(x['n1'], x['n2'], x['n3']); st = (r1 % 9, r2 % 9); n1 = x['n1']
            L.append('N  NAVIGATION: n = (%d, %d, %d), r = (%d, %d, %d), ANCHOR P%d %s | Yang P%d %s | Yin P%d %s | 4D P%d %s | Antipode P%d %s | STATE %s -- THE ANSWER is written from this coordinate and sealed'
                     % (x['n1'], x['n2'], x['n3'], r1, r2, r3, an, cr.POSITION_NAMES[an], (an + 5) % 24, cr.POSITION_NAMES[(an + 5) % 24], (an + 18) % 24, cr.POSITION_NAMES[(an + 18) % 24],
                        (an + 8) % 24, cr.POSITION_NAMES[(an + 8) % 24], (an + 12) % 24, cr.POSITION_NAMES[(an + 12) % 24], st))
        stratum, half, loop = M.classify(st)
        pos, sts = properties()
        held = [k for k, v in pos.items() if an in v and k != 'antipode sum 9' and not k.startswith('value')]
        L.append('A1 ARITHMETIC (exact, after the seal): state %s, %s, half %s, %s, norm %d; anchor P%d carries value %d%s; given its %d content words the anchor equals r1 with chance 73/81 (Companion 57.5)'
                 % (st, stratum, half, loop or 'the still point', (st[0] ** 2 + st[0] * st[1] - st[1] ** 2) % 9, an, cr.ORBIT[an],
                    ('; ' + '; '.join('%s, %d of 24' % (k, len(pos[k])) for k in held)) if held else '', n1))
        if rt['route'] == 'CANONICAL':
            reg = [(tg, d) for tg, d in cg.load_register() if cg.sig(d)['sha'] != cr.domain_sha256(q)]
            same = [tg for tg, d in reg if cg.sig(d)['state'] == st]
            links = [tg for tg, d in reg if cg.sig(d)['yang'] == an or (an + 5) % 24 == cg.sig(d)['anchor']]
            c = [cg.conditioned_rates(n1, cg.n1_of(d)) for tg, d in reg]
            L.append('G  GATHERING (the Atlas page and the record, %d domains): same state %s | links %s -- expected given word count: same state %.2f, links %.2f (L-501)'
                     % (len(reg), ', '.join(same) or 'none', ', '.join(links) or 'none', sum(r['state'] for r in c), 2 * sum(r['link'] for r in c)))
        else:
            L.append('G  GATHERING: a companion coordinate; its meetings in python3 tools/utility.py --align (cross-adaptor, L-501)')
    terms = cg.subject_terms(q)
    L.append('L  LENSES (by relevance, L-494): %s' % ('; '.join(terms) + ' -- selected by the Navigator or the Striker, run after the seal' if terms else 'no registered subject term; none is compulsory'))
    try:
        import consciousness as cs
        ct = cs.concerns(q)
    except Exception:
        ct = False
    L.append('R  FRAME REASONING (written after the seal): what the premise (F-02) implies for the question -- what is derived, what is only compatible, what stays open%s'
             % ('; the question concerns mind or experience: the CT-42 framework applies (python3 tools/consciousness.py --frame)' if ct else ''))
    found = [e for e in sources()['entries'] if any(w in (e['item'] + ' ' + e['says'] + ' ' + e['with']).lower() for w in re.findall(r'[a-z]{5,}', q.lower()))]
    L.append('W  CURRENT KNOWLEDGE (L-503, by default, after the seal; python3 tools/utility.py --current): M248\'s four lanes -- consensus, foundations, counter-evidence, frontier -- the query and what would count as not found declared first, every source opened, dated and related to a direction of the reading, empty lanes reported; %sCOMPARATIVE, never in THE ANSWER; the premise is not graded by it%s'
             % ('the topic, never the person, the query printed, and the Striker may say "no sources" (L-495); ' if kind == 'PERSONAL' else '',
                '; registered on the protocol\'s own provisions: ' + ', '.join('%s (%s)' % (e['id'], e['relation']) for e in found) if found else ''))
    L.append('CURRENCY (APE-086; Companion 64.9): if the Navigator\'s knowledge cutoff lies well before the session date, its Reasoning says in one line that the Conventional Connection may name superseded work, and the CURRENT KNOWLEDGE layer checks the works named (L-503)')
    L += ['X  CONVERGENCE (offered): the same domain, verbatim, to a Navigator of another architecture (SR-CAS)',
          'U  USE AND RETURN (offered): the Striker\'s own note after acting, if any (M307, M311)',
          'ACROSS THE AVENUES (L-502; written last): where the avenues agree and where they part, each with its standing and, where it has one, its chance; a disagreement and a silence are reported as carefully as an agreement; the congruence of each avenue with the premise is shown, never support for it -- no combined verdict, no score',
          'APERTURE: what this means, whether it matters and what to do with it are the Striker\'s (Part 7)',
          '======= END M316 HOLISTIC RESPONSE SCAFFOLD =======']
    return '\n'.join(L)



PROV_DEGREES = ('ORIGINATED', 'DIRECTED', 'EDITED', 'ADOPTED')
PROV_ORIGINS = ('ESC-ORIGINATED', 'MATHEMATICALLY DERIVED', 'PROTOCOL-ADOPTED', 'AI-PROPOSED', 'EXTERNALLY SOURCED', 'UNKNOWN')


def provenance():
    return json.load(open(os.path.join(ROOT, 'records', 'provenance', 'ledger.json'), encoding='utf-8'))


def provenance_problems(d=None):
    d = d or provenance(); P = []
    for e in d['entries']:
        if e.get('esc_degree') not in PROV_DEGREES: P.append('%s: esc_degree not one of %s' % (e['provision'], ', '.join(PROV_DEGREES)))
        if e.get('historical_origin') not in PROV_ORIGINS: P.append('%s: historical_origin not one of the values of Companion 24.7' % e['provision'])
        if not e.get('note'): P.append('%s: no note' % e['provision'])
    ids = [e['provision'] for e in d['entries']]
    P += ['%s entered twice' % i for i in sorted(set(ids)) if ids.count(i) > 1]
    return P


def provenance_text():
    d = provenance(); c = Counter(e['esc_degree'] for e in d['entries'])
    L = ['======= PROVENANCE AND CONTAMINATION LEDGER (Core BF-10; Companion 24.7, Part 69) =======', d['_about'], '',
         'BY THE ORIGINATOR\'S DEGREE: ' + ' | '.join('%s %d' % (k, c.get(k, 0)) for k in PROV_DEGREES), '']
    for e in d['entries']:
        L.append('%-8s %-36s %-17s %-10s %s' % (e['provision'], e['name'][:36], e['historical_origin'], e['esc_degree'], e['note']))
    P = provenance_problems(d)
    L += ['', 'CHECK: ' + ('PASS' if not P else 'FAIL -- ' + '; '.join(P)), '======= END PROVENANCE AND CONTAMINATION LEDGER =======']
    return '\n'.join(L)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--pair': print(pair_text(a[1], a[2])); sys.exit(0)
    if a[0] == '--modes': print(pair_text(a[1], a[2], 'TWO MODES', ('PROSE', 'NOTATION'))); sys.exit(0)
    if a[0] == '--contrast': print(contrast_text(' '.join(a[1:]))); sys.exit(0)
    if a[0] == '--align':
        nv = a[a.index('--nav') + 1] if '--nav' in a else None
        q = a[1]; print(align_text(q, nv)); sys.exit(0)
    if a[0] == '--register': print(register_text()); sys.exit(0 if not register_problems() else 1)
    if a[0] == '--provenance': print(provenance_text()); sys.exit(0 if not provenance_problems() else 1)
    if a[0] == '--avenues': print(avenues_text()); sys.exit(0)
    if a[0] in ('--personal', '--reveal'):
        i = a.index('--secret'); sec = a[i + 1]; q = ' '.join(a[1:i] + a[i + 2:])
        print(personal_text(q, sec) if a[0] == '--personal' else reveal_text(q, sec)); sys.exit(0)
    if a[0] == '--current': print(current_text(' '.join(a[1:]))); sys.exit(0)
    if a[0] == '--survey': print(survey_text()); sys.exit(0 if not survey_problems() else 1)
    if a[0] == '--tally': print(tally_text(int(a[1]), int(a[2]))); sys.exit(0)
    if a[0] == '--enrichment': print(enrichment_text()); sys.exit(0 if not enrichment_problems() else 1)
    if a[0] == '--sources': print(sources_text(a[1:] or None)); sys.exit(0 if not source_problems() else 1)
    if a[0] == '--holistic':
        dec = None
        if '--request' in a: i = a.index('--request'); dec = a[i + 1]; a = a[:i] + a[i + 2:]
        print(holistic_text(' '.join(a[1:]), dec)); sys.exit(0)
    if a[0] == '--rarity': print(rarity_text(a[1:] or None)); sys.exit(0)
    if a[0] == '--check-entry':
        t, ok = check_entry(a[1]); print(t); sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
