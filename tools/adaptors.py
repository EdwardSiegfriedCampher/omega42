#!/usr/bin/env python3
"""adaptors.py -- M317 Adaptor Layer (Core Part 3.43, L-501; Companion Part 56).

An adaptor counts a medium's own boundaries at three nested granularities, under frozen and versioned rules, and the
coordinate follows by the canonical projection. The English canonical extraction (scripts/canonical_reference.py) is
the default adaptor for English, EN-CANON. Other adaptors enter as COMPANION adaptors and become CANONICAL for their
medium only by the Originator's adoption (F-06). The DOMAIN SHA-256 stays over the text (L-414); an ADAPTOR SHA-256
beside it names the rules that made the counts.

Routing: a text whose letters are mostly of a script other than Latin (by Unicode name, as M208 identifies it) is
routed to the adaptor of its script; with no adaptor for that script it is held as ZERO-COUNT, with no coordinate
entered in the Congruence Register. A Latin-script text in a language other than English is counted by its language's
adaptor when the Striker declares the language. A text with no letters at all stays a NULL STRIKE (L-468).

    python3 tools/adaptors.py --route "TEXT" [--lang de|fr]   # which adaptor counts this text, and why
    python3 tools/adaptors.py --strike "TEXT"      # the ADAPTOR block: counts, coordinate, stability, null status
    python3 tools/adaptors.py --contract           # every registered adaptor checked against the Adaptor Contract
    python3 tools/adaptors.py --selftest
Standard library and the reference script.
"""
import hashlib, json, os, re, sys, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr

REGISTRY = os.path.join(ROOT, 'records', 'adaptors', 'registry.json')
STATUSES = ('CANONICAL', 'COMPANION')
FIELDS = ('id', 'version', 'scripts', 'status', 'granularities', 'rules', 'sha256', 'lost', 'stability', 'null', 'tests')


def script_of(text):
    import adaptor_rules as _AR
    return _AR.script_of(text)



def registry():
    return json.load(open(REGISTRY, encoding='utf-8'))


def _sha(path):
    return hashlib.sha256(open(os.path.join(ROOT, path), 'rb').read()).hexdigest()


def _script_of_old(text):
    """Dominant script of the letters, by Unicode name (as M208 identifies it)."""
    from collections import Counter
    c = Counter()
    for ch in unicodedata.normalize('NFC', text):
        if unicodedata.category(ch).startswith('L'):
            n = unicodedata.name(ch, '')
            c[n.split(' ')[0] if n else 'UNKNOWN'] += 1
    return c.most_common(1)[0][0] if c else None


import adaptor_rules as AR
COUNTERS = AR.COUNTERS
hangul_counts = AR.hangul
_NULLS = {}


def null_of(name):
    if name not in _NULLS: _NULLS[name] = AR.null(name, cr.determine_anchor)
    return _NULLS[name]


def adaptor(aid):
    return next(x for x in registry()['adaptors'] if x['id'] == aid)


def route(text, lang=None):
    x = cr.navigate(text)
    if lang and lang.lower() in AR.DECLARED and x['n1'] > 0:
        aid = AR.DECLARED[lang.lower()]
        return dict(route='ADAPTED', adaptor=aid, status=adaptor(aid)['status'], script='LATIN',
                    reason='the Striker declares the language %s: counted by %s beside the canonical English count' % (lang, aid))
    sc = script_of(text)
    if sc is None:
        return dict(route='CANONICAL', adaptor='EN-CANON', reason='no letters: a NULL STRIKE under L-468 when nothing is counted')
    if sc == 'LATIN':
        return dict(route='CANONICAL', adaptor='EN-CANON', reason='the letters are Latin: the canonical extraction counts %d word(s)' % x['n1'])
    if sc in AR.SCRIPTS:
        aid = AR.SCRIPTS[sc]
        return dict(route='ADAPTED', adaptor=aid, status=adaptor(aid)['status'], script=sc,
                    reason='the letters are mostly %s, which the canonical extraction does not read: routed to %s' % (sc, aid))
    need = AR.OPEN_SCRIPTS.get(sc, 'an adaptor for the script')
    return dict(route='ZERO-COUNT', adaptor=None, script=sc,
                reason='the letters are mostly %s and no adaptor exists for it yet (it needs %s): held ZERO-COUNT -- UNPLACED, awaiting an adaptor: not a NULL STRIKE and not the still point, kept out of the Congruence Register' % (sc, need))


def coordinate(n):
    a, r1, r2, r3, tfi = cr.determine_anchor(*n)
    return dict(n=n, r=(r1, r2, r3), anchor=a, tfi=tfi, state=(r1 % 9, r2 % 9),
                arms=dict(Yang=(a + 5) % 24, Yin=(a + 18) % 24, D4=(a + 8) % 24, Antipode=(a + 12) % 24))


def strike(text, lang=None):
    rt = route(text, lang)
    if rt['route'] != 'ADAPTED': return rt, None
    a = adaptor(rt['adaptor'])
    co = coordinate(COUNTERS[a['id']](text))
    var = [coordinate(COUNTERS[a['id']](v))['anchor'] for v in AR.variants(a['id'], text)]
    co['stability'] = sum(v == co['anchor'] for v in var); co['variants'] = var
    co['adaptor'] = a
    co['rates'] = AR.rates(null_of(a['null']), null_of('UNIFORM-729'))
    co['self_rates'] = AR.rates(null_of(a['null']), null_of(a['null']))
    co['given'] = AR.rates(AR.null(a['null'], cr.determine_anchor, co['n'][0]), AR.null('UNIFORM-729', cr.determine_anchor, co['n'][0]))
    co['estimated'] = 'ESTIMATE' in a['granularities'][2]
    return rt, co


def block(text, lang=None):
    rt, co = strike(text, lang)
    L = ['======= ADAPTOR (L-501, M317) =======', 'QUESTION VERBATIM: %s' % ' '.join(text.split('\n')), 'ROUTE: %s -- %s' % (rt['route'], rt['reason'])]
    if co:
        a = co['adaptor']
        L += ['ADAPTOR (L-501): %s v%s | %s | ADAPTOR SHA-256 %s | DOMAIN SHA-256 %s (over the text, L-414)' % (
                  a['id'], a['version'], a['status'], a['sha256'], cr.domain_sha256(text)) + (' | n3 ESTIMATED' if co['estimated'] else '') + (' | LANGUAGE %s (declared; recorded in the Substrate Lock, not in the domain hash)' % lang if lang else ''),
              'LAYERS: n1 %s = %d | n2 %s = %d | n3 %s = %d%s' % (a['granularities'][0], co['n'][0], a['granularities'][1], co['n'][1], a['granularities'][2], co['n'][2],
                  ' -- n3 ESTIMATED, not counted: a recomputation agrees with the frozen rule, not with a count (CPDP)' if co['estimated'] else ''),
              'RESIDUES: r = (%d, %d, %d) | ANCHOR P%d %s (value %d) | TFI %.2f | STATE %s' % (co['r'] + (co['anchor'], cr.POSITION_NAMES[co['anchor']], cr.ORBIT[co['anchor']], co['tfi'], co['state'])),
              'ARMS: Yang P%(Yang)d | Yin P%(Yin)d | 4D P%(D4)d | Antipode P%(Antipode)d' % co['arms'],
              'STABILITY (its frozen family): %d of 3 variants keep the anchor (%s)' % (co['stability'], ', '.join('P%d' % v for v in co['variants'])),
              'NULL: %s -- chance with a canonical (EN-CANON) strike: same state %.4f, mirror %.4f, link %.4f; with a strike of the same adaptor: same state %.4f' % (a['null'], co['rates']['state'], co['rates']['mirror'], co['rates']['link'], co['self_rates']['state']),
              'GIVEN WORD COUNT (the reference, L-501): with a canonical strike of the same n1 (%d): same state %.4f, mirror %.4f, link %.4f' % ((co['n'][0],) + tuple(co['given'][k] for k in ('state', 'mirror', 'link'))),
              'NOT COUNTED: %s' % a['lost'],
              'STATUS: a %s coordinate; a meeting with an EN-CANON coordinate is a cross-adaptor relation, counted against the reference given word count above (L-501). Navigation, not mapping: depth beyond placement needs the object\'s own dynamics (IN-02.8).' % a['status']]
    elif rt['route'] == 'ZERO-COUNT':
        L += ['ADAPTOR (L-501): NONE -- ZERO-COUNT (UNPLACED) | script %s | DOMAIN SHA-256 %s (over the text, L-414)' % (rt['script'], cr.domain_sha256(text)),
              'STATUS: no counts, no anchor, no state; not a NULL STRIKE (L-468) -- a question is present that no adaptor yet reads. Recorded as unplaced, awaiting an adaptor; it enters no meeting.']
    L.append('======= END ADAPTOR =======')
    return '\n'.join(L)


def contract_problems(R=None):
    R = R or registry(); out = []
    for a in R['adaptors']:
        for f in FIELDS:
            if not a.get(f): out.append('%s: no %s' % (a.get('id'), f))
        if a.get('status') not in STATUSES: out.append('%s: status %s' % (a.get('id'), a.get('status')))
        if a.get('status') == 'CANONICAL' and not a.get('adopted'): out.append('%s: CANONICAL without the Originator\'s adoption (F-06)' % a.get('id'))
        if len(a.get('granularities', [])) != 3: out.append('%s: three granularities required' % a.get('id'))
        if a.get('code') and _sha(a['code']) != a.get('code_sha256'):
            out.append('%s: its code changed since frozen -- a new version is a protocol revision (L-501)' % a['id'])
        if a.get('rules') and os.path.exists(os.path.join(ROOT, a['rules'])) and a['id'] != 'EN-CANON' and _sha(a['rules']) != a.get('sha256'):
            out.append('%s: rules changed since frozen -- a new version is a protocol revision (L-501)' % a['id'])
        if a.get('null') and a['null'] not in ('UNIFORM-729', 'HANGUL-STRUCTURAL-1', 'AKSHARA-STRUCTURAL-1', 'ABJAD-STRUCTURAL-1'): out.append('%s: unknown null %s' % (a['id'], a['null']))
        if a['id'] in COUNTERS:
            for t in a.get('tests', []):
                got = list(COUNTERS[a['id']](t['text'])); anc = coordinate(tuple(got))['anchor']
                if got != t['n'] or anc != t['anchor']: out.append('%s: known-answer test failed on %r: n %s anchor P%d' % (a['id'], t['text'], got, anc))
        elif a['id'] == 'EN-CANON':
            for t in a.get('tests', []):
                x = cr.navigate(t['text'])
                if [x['n1'], x['n2'], x['n3']] != t['n'] or x['anchor'] != t['anchor']: out.append('EN-CANON: known-answer test failed on %r' % t['text'])
        else:
            out.append('%s: registered but not implemented' % a['id'])
    return out


def contract_text():
    R = registry(); L = ['M317 ADAPTOR CONTRACT (L-501; Core Part 3.43) -- %d adaptors' % len(R['adaptors'])]
    for a in R['adaptors']:
        L.append('%s v%s  %-9s scripts %s | layers %s | tests %d | null: %s' % (a['id'], a['version'], a['status'], ', '.join(a['scripts']), ' / '.join(a['granularities']), len(a['tests']), a['null'][:60]))
    P = contract_problems(R)
    L.append('CHECK: %s' % ('PASS' if not P else 'FAIL: ' + '; '.join(P)))
    return '\n'.join(L)


def null_rates_check():
    r = AR.rates(null_of('HANGUL-STRUCTURAL-1'), null_of('HANGUL-STRUCTURAL-1'))['state']
    u = AR.rates(null_of('UNIFORM-729'), null_of('UNIFORM-729'))['state']
    return r if abs(r - u) > 1e-4 else 0


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-74s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    check('English text stays on the canonical extraction', route('What is consciousness?')['route'] == 'CANONICAL')
    check('Greek is routed even where a lone letter gives the canonical extraction a word (Part 1.12 (8))', route('Τι είναι η συνείδηση;')['adaptor'] == 'EL-GREK-1')
    check('an English sentence with one Greek letter stays canonical', route('What is the role of φ in growth?')['route'] == 'CANONICAL')
    check('a text with no letters stays a NULL STRIKE (L-468), not routed', route('42 ? !')['route'] == 'CANONICAL')
    check('Korean is routed to KO-HANGUL-1', route('의식이란 무엇인가?')['adaptor'] == 'KO-HANGUL-1')
    check('Russian is routed to RU-CYRL-1', route('Что такое сознание?')['adaptor'] == 'RU-CYRL-1')
    check('a text half Latin stays canonical; ties between other scripts go to the first letter', AR.script_of('ab αβ') == 'LATIN' and AR.script_of('αβ ваб') == 'CYRILLIC' and AR.script_of('αβ вб') == 'GREEK')
    check('an estimated third layer is marked on the ADAPTOR line (CPDP)', 'n3 ESTIMATED' in block('ما هو الوعي؟') and 'n3 ESTIMATED' not in block('Что такое сознание?'))
    check('the reference given word count is 1/9 for same state at n1 = 2 under UNIFORM-729', abs(AR.rates(AR.null('UNIFORM-729', cr.determine_anchor, 2), AR.null('UNIFORM-729', cr.determine_anchor, 2))['state'] - 1 / 9) < 1e-9)
    check('a declared language is on the ADAPTOR line, not in the domain hash', 'LANGUAGE de (declared' in block('Was ist Bewusstsein?', 'de'))
    check('a ZERO-COUNT text is recorded UNPLACED, not as a NULL STRIKE', 'ZERO-COUNT (UNPLACED)' in block('什么是意识？'))
    check('Chinese, with no adaptor yet, is held ZERO-COUNT and names what it needs', route('什么是意识？')['route'] == 'ZERO-COUNT' and 'segmentation' in route('什么是意识？')['reason'])
    check('German is counted by DE-LATN-1 when the Striker declares it', route('Was ist Bewusstsein?', 'de')['adaptor'] == 'DE-LATN-1' and route('Was ist Bewusstsein?')['route'] == 'CANONICAL')
    check('a structural null differs from the uniform one, and both are probabilities', 0 < null_rates_check() < 1)
    check('Hangul counts: eojeol 2, blocks 8, jamo 20', hangul_counts('의식이란 무엇인가?') == (2, 8, 20))
    check('decomposed jamo compose first (NFC)', hangul_counts(unicodedata.normalize('NFD', '의식')) == hangul_counts('의식'))
    b = block('의식이란 무엇인가?')
    check('the ADAPTOR block names the adaptor, its hash, its status and the text hash', 'ADAPTOR (L-501): KO-HANGUL-1 v1 | COMPANION | ADAPTOR SHA-256' in b and 'DOMAIN SHA-256' in b)
    check('the block opens with the question verbatim (L-499)', b.split('\n')[1] == 'QUESTION VERBATIM: 의식이란 무엇인가?')
    check('every registered adaptor meets the contract', not contract_problems())
    bad = registry(); bad['adaptors'] = [dict(bad['adaptors'][1], status='CANONICAL', adopted=None)]
    check('a CANONICAL adaptor without adoption is refused', contract_problems(bad) != [])
    print('M317 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    lang = a[a.index('--lang') + 1] if '--lang' in a else None
    if lang: i = a.index('--lang'); a = a[:i] + a[i + 2:]
    if a[0] == '--route': r = route(' '.join(a[1:]), lang); print('ROUTE: %s -- %s' % (r['route'], r['reason'])); sys.exit(0)
    if a[0] == '--strike': print(block(' '.join(a[1:]), lang)); sys.exit(0)
    if a[0] == '--contract': print(contract_text()); sys.exit(0 if not contract_problems() else 1)
    print(__doc__); sys.exit(2)
