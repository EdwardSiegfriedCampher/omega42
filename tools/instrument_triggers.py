#!/usr/bin/env python3
"""instrument_triggers.py -- M327 Instrument Selector (Core L-527, Part 3.53; Companion Part 108).

Every instrument outside Tiers 0 to 2 has a trigger, frozen in records/instruments/triggers.json: a feature of the strike
that this script computes from the domain text and its coordinate, or a situation the Navigator declares. An instrument
runs when one of its triggers holds, and not otherwise; the Striker naming an instrument is a trigger of every instrument.
The selector reads; it never changes the canonical computation (L-494 (4)), and it prints the coordinate it read from.

    python3 tools/instrument_triggers.py --select "DOMAIN" [--situation KEY ...] [--rows FILE] [--request MXXX ...]
    python3 tools/instrument_triggers.py --situations          # the declared situations and the lexicon
    python3 tools/instrument_triggers.py --check               # the register is well formed, and the comparative guard holds
    python3 tools/instrument_triggers.py --corpus FILE         # how many instruments the computed triggers fire, per domain
    python3 tools/instrument_triggers.py --selftest

The comparative guard (L-491; Part 0.0.4, items 7 and 8): an instrument of the comparative register triggers only on
what a person brings -- a choice to investigate, a proposed ground, a taxonomy named in the question, or a request --
never on every navigation, on the coordinate or on a session event; so no trigger makes scientific inquiry a step of a
routine reading. Standard library only.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'scripts')); sys.path.insert(0, HERE)
import canonical_reference as cr
REG = json.load(open(os.path.join(REPO, 'records', 'instruments', 'triggers.json'), encoding='utf-8'))
INSTR = REG['instruments']; LEX = REG['lexicon']; SIT = REG['situations']; COMP = REG['computed']
PERSON_KEYS = {'comparative_inquiry', 'ground_proposed'}            # what a person brings, besides lexical keys

def has(text, phrase):
    return re.search(r'(?<![\w])' + re.escape(phrase) + r'(?![\w])', text) is not None   # Unicode-aware word boundaries

def rows_of(lines):
    rows = [[int(x) for x in re.findall(r'-?\d+', l)] for l in lines]
    return [r for r in rows if len(r) >= 6]

_R = None
def profile():
    global _R
    if _R is None:
        import restored_instruments as ri
        _R = ri.resonance([t for _, t in ri.corpus()])
    return _R

def features(domain, rows=None):
    t = domain.lower(); f = set()
    for p in REG.get('lexicon_exempt', []): t = t.replace(p, ' ')   # the frame's own name is not a request for research (Core Part 3.53)
    for k, ps in LEX.items():
        if any(has(t, p) for p in ps): f.add('lex:' + k)
    nav = cr.navigate(domain)
    sents = [s for s in re.split(r'(?<=[.!?])\s+|(?<=[\u3002\uff1f\uff01])', domain.strip()) if re.search(r'\w', s)]
    if len(sents) >= 2: f.add('sentences_ge2')
    if len(nav['content']) <= 3: f.add('content_le3')
    if cr.math_tokens(domain) or re.search(r'\d\s*[*/]\s*\d', domain): f.add('math')
    if re.search(r'\S\s*=\s*\S', domain): f.add('equation')
    if any(ch.isalpha() and not ('a' <= ch.lower() <= 'z') and 'LATIN' not in __import__('unicodedata').name(ch, '') for ch in domain): f.add('nonlatin')
    if re.search(r'(?<![\d.=+*/-])-?\d+(?:\s*,\s*-?\d+|\s+-?\d+){2,}(?![\d=+*/-])', domain): f.add('int_sequence')
    rr = rows if rows is not None else rows_of(domain.split('\n'))
    if len(rr) >= 10: f.add('rows6')
    vis = [c for c in domain if not c.isspace()]
    if vis and sum(c.isalpha() for c in vis) < len(vis) / 2: f.add('not_prose')
    import restored_instruments as ri
    if any(w in ri.M191_CATEGORIES[c] for w in re.findall(r'[a-z]+', t) for c in ri.M191_CATEGORIES): f.add('m191')
    a = nav['anchor']
    if a in (4, 5, 18) or nav['antipode_i'] == 18: f.add('void')
    if cr.is_crown(a): f.add('crown_anchor')
    canon = {(cr.orbit_value(i), cr.orbit_value(i + 1)) for i in range(24)}
    if (nav['r1'], nav['r2']) not in canon: f.add('pair_off_orbit')
    R = profile().get(nav['anchor_value'])
    if R is not None and (R > 1.2 or R == 0): f.add('amplified_or_severe')
    return f, nav

def fires(keys, present):
    return [k for k in keys if all(x in present for x in k.split('+'))]

def select(domain, situations=(), rows=None, requests=()):
    f, nav = features(domain, rows); present = f | set(situations)
    out = []
    for e in INSTR:
        hit = fires(e['triggers'], present)
        if e['id'] in requests: hit = hit + ['striker_request']
        if hit: out.append((e, hit))
    return out, f, nav

def check():
    P = []
    known = set(COMP) | set(SIT) | {'lex:' + k for k in LEX}
    ids = [e['id'] for e in INSTR]
    if len(ids) != len(set(ids)): P.append('duplicate ids')
    for e in INSTR:
        if not e['triggers']: P.append('%s has no trigger' % e['id'])
        for k in e['triggers']:
            for x in k.split('+'):
                if x not in known: P.append('%s: unknown key %s' % (e['id'], x))
        if e['record'] == 'COMPARATIVE':
            bad = [x for k in e['triggers'] for x in k.split('+') if not (x in PERSON_KEYS or x.startswith('lex:'))]
            if bad: P.append('%s: comparative instrument triggered by %s (L-491 guard)' % (e['id'], bad))
    return P

def report(domain, situations=(), rows=None, requests=()):
    out, f, nav = select(domain, situations, rows, requests)
    L = ['M327 INSTRUMENT SELECTOR (Core L-527) | domain: %s' % domain.replace('\n', ' ')[:120],
         '  coordinate read (unchanged by the selector): anchor P%d = %d (%s), r = (%d, %d, %d)' % (nav['anchor'], nav['anchor_value'], nav['anchor_name'], nav['r1'], nav['r2'], nav['r3']),
         '  computed features: %s' % (', '.join(sorted(f)) or 'none'),
         '  situations declared: %s' % (', '.join(situations) or 'none')]
    for e, hit in out:
        L.append('  RUNS  %-7s %-42s Part %-5s trigger: %s%s' % (e['id'], e['name'][:42], e['part'], ', '.join(hit),
                 '  [offered to the Striker; kept only if chosen]' if e['record'] == 'STRIKER-SIDE' else '  [comparative register]' if e['record'] == 'COMPARATIVE' else ''))
    if not out: L.append('  no registered trigger matched: the Striker may still name any instrument, and a question the register did not anticipate may be named for amendment (L-527 (2))')
    L.append('  %d of %d register entries triggered; Tiers 0 to 2 run by their own rules (Core Part 3.9)' % (len(out), len(INSTR)))
    return '\n'.join(L)

def selftest():
    def ids(d, s=(), rows=None, req=()): return {e['id'] for e, _ in select(d, s, rows, req)[0]}
    rows = [[(7 * t + k) % 49 + 1 for k in range(6)] for t in range(20)]
    cases = [
     ('a decision fires the Field Kit and offers the intention worksheet', {'M321', 'M306'} <= ids('Should I take the job in Cape Town or stay where I am?')),
     ('a question about sound fires the Cymatic View and the Mode Address', {'M322', 'M289'} <= ids('What does the music of the spheres sound like?')),
     ('a question naming a cultural taxonomy fires the Cultural Pattern Companion', 'M218' in ids('Is astrology a map of the soul?')),
     ('two sentences fire the constellation, the transduction and the sentence count', {'M157', 'M190', 'M261'} <= ids('Love is patient. Love is kind.')),
     ('an equation fires the Goedel transduction and the equation comparator', {'M223', 'M231'} <= ids('Why does E = mc^2 hold?')),
     ('rows with a question about the next one fire the Construct Engine, and not the Echo Test', 'M326' in ids('What comes next in this sequence?', rows=rows) and 'M325' not in ids('What comes next in this sequence?', rows=rows)),
     ('rows with a claimed pattern fire the Echo Test', 'M325' in ids('These rows follow a pattern.', ('pattern_claimed',), rows=rows)),
     ('a research question fires the literature search but no comparative instrument (L-491)', 'M248' in ids('What does the research say about sleep and memory?') and not any(e['record'] == 'COMPARATIVE' and e['id'] != 'M218' for e, _ in select('What does the research say about sleep and memory?')[0])),
     ('a choice to investigate fires the comparative register', {'M196', 'M279', 'M280', 'M282', 'TIER-C'} <= ids('Do readings differ from decoys?', ('comparative_inquiry',))),
     ('the Congruence Record and the Aperture audit run on every navigation', {'M310', 'M281'} <= ids('What is time?', ('every_navigation',))),
     ('a request fires the instrument named', 'M260' in ids('What is time?', req=('M260',))),
     ('the coordinate the selector reads equals the canonical one', select('What is the human condition?')[2]['anchor'] == cr.navigate('What is the human condition?')['anchor']),
     ('a sorites, a chart and the multiverse fire M329, M330 and M331', 'M329' in ids('Where does a heap begin?') and 'M330' in ids('What does my natal chart say?') and 'M331' in ids('Is the multiverse real?')),
     ('a question about phonetics fires the Phonetic Reading and the sound instruments', {'M332', 'M289', 'M322'} <= ids('How do the vowels of a language shape what we hear?')),
     ('a question about the truth of a statement fires the Standing Record', 'M333' in ids('Is this statement true or false?')),
     ('the register is well formed and the comparative guard holds', not check()),
    ]
    for nm, ok in cases: print('%s  %s' % ('PASS' if ok else 'FAIL', nm))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--check']:
        P = check(); print('M327 REGISTER CHECK: %d entries, %s' % (len(INSTR), 'PASS' if not P else 'FAIL -- ' + '; '.join(P))); sys.exit(1 if P else 0)
    if a[:1] == ['--situations']:
        for k, v in SIT.items(): print('  %-22s %s' % (k, v))
        for k, v in COMP.items(): print('  %-22s %s (computed)' % (k, v))
        sys.exit(0)
    if a[:1] == ['--corpus'] and len(a) == 2:
        doms = [l.rstrip('\n') for l in open(a[1], encoding='utf-8') if l.strip()]
        from collections import Counter
        n = [len(select(d)[0]) for d in doms]; c = Counter(i for d in doms for i in [e['id'] for e, _ in select(d)[0]])
        print('M327 CORPUS: %d domains; register entries fired by computed triggers alone: mean %.2f, median %d, max %d, none in %d'
              % (len(doms), sum(n) / len(n), sorted(n)[len(n) // 2], max(n), n.count(0)))
        print('  most frequent: ' + ', '.join('%s %d' % kv for kv in c.most_common(10)))
        sys.exit(0)
    if a[:1] == ['--select'] and len(a) >= 2:
        sit, req, rows, i = [], [], None, 2
        while i < len(a):
            if a[i] == '--situation': sit.append(a[i + 1]); i += 2
            elif a[i] == '--request': req.append(a[i + 1]); i += 2
            elif a[i] == '--rows': rows = rows_of(open(a[i + 1], encoding='utf-8').read().split('\n')); i += 2
            else: i += 1
        bad = [s for s in sit if s not in SIT]
        if bad: print('unknown situation(s): %s (python3 tools/instrument_triggers.py --situations)' % bad); sys.exit(2)
        print(report(a[1], sit, rows, req)); sys.exit(0)
    print(__doc__)
