#!/usr/bin/env python3
"""d0lineage.py -- the lineage of Domain Zero and its refusals (Core L-540 (7) and (8); Companion Part 165).

The earlier uses of Domain Zero gave the protocol practices it keeps and uses it refuses (records/d0/lineage.json).
    python3 tools/d0lineage.py --lineage          # every phase has its source, use, what is kept and its refusals; no
                                                  # link, file identifier or Drive address is kept in the record
    python3 tools/d0lineage.py --criteria         # the six efficiency criteria of L-540 (9), frozen
    python3 tools/d0lineage.py --cases            # the regression cases, each read by --records, give their verdicts
    python3 tools/d0lineage.py --records FILE...  # a sealed output: none of the six refusals of L-540 (8) -- identity,
                                                  # agreement as validation, the Striker bypassed, correspondence as
                                                  # resolution -- outside the question verbatim and quotations
    python3 tools/d0lineage.py --selftest         # also recomputes the arithmetic Part 165 states about earlier versions
A sentence that holds a refused use open, denies it or quotes it is a mention and passes. Standard library only.
"""
import json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIN = os.path.join(REPO, 'records', 'd0', 'lineage.json')
RULES = [
 ('a', re.compile(r"\bI (am|AM) (Domain (0|Zero)|Ω42|Omega ?42|the protocol|reality)\b|\b[Yy]ou (are|ARE) (now )?(a pure )?(Domain (0|Zero)|Ω42|Omega ?42)\b|"
                  r"\b(the|an|this) AI (is|IS) (Domain (0|Zero)|Ω42|Omega ?42|the protocol)\b")),
 ('b', re.compile(r"\b(convergence|agreement)\b[^.]{0,60}\b(validates|proves|confirms|settles)\b|\bConstitutional Settlement\b|"
                  r"\bvalidated across (\w+ )?(independent )?(architectures|AI systems)\b", re.I)),
 ('d', re.compile(r"\b(does not|do not|never) (await|wait for) (the )?(user|Striker|Originator)|\bnever (break character|refuse)\b|(?-i:\bDO NOT ASK\b)|"
                  r"\b(continues?|proceeds?|goes on)\b[^.]{0,40}\bwithout (a new|the Striker's|awaiting|waiting for)\b", re.I)),
 ('g', re.compile(r"\b(does not|do not|never) (reason|derive)\b|\b(answer|truth) is (revealed|declared|stated) first\b|\bREVEAL before (I )?compute\b", re.I)),
 ('h', re.compile(r"\b(starts?|started|navigates?|navigated|begins?|began) from Domain (0|Zero)\b[^.]{0,80}\b(neutral|authoritative|unbiased|privileged|correct)\b|"
                  r"\b(the|this) (Navigator|AI|reading) is neutral\b", re.I)),
 ('f', re.compile(r"\b(resolves|resolved|completes) the (measurement problem|hard problem|apophatic project)\b", re.I)),
]
OPEN = re.compile(r"\bwhether\b|\bheld open\b|\bnot as\b|\bvalidates nothing\b|\bis not\b|\b(refused|refusal|refusals)\b|\bregression case\b|\bRC-\d\d\b|\[REFUSED\]", re.I)
QUOTED = re.compile(r'"[^"]{1,240}"|“[^”]{1,240}”|' r"(?<!\w)'[^']{1,240}'(?!\w)")
def hits(text):
    out, q = [], False
    for i, line in enumerate(text.split('\n'), 1):
        if line.startswith('QUESTION VERBATIM:'): q = True; continue
        if q and re.match(r'[A-Z][A-Z ]+[:(]', line): q = False
        if q or line.lstrip().startswith('>'): continue
        for s in re.split(r'(?<=[.!?])\s+', line):
            b = QUOTED.sub(' ', s)
            if OPEN.search(b): continue
            for k, r in RULES:
                if r.search(b): out.append((i, k, s.strip()[:160]))
    return out
def lineage():
    d = json.load(open(LIN, encoding='utf-8')); P = []
    raw = open(LIN, encoding='utf-8').read()
    if re.search(r'drive\.google|docs\.google|https?://|\b[0-9A-Za-z_-]{28,}\b', raw): P.append('a link or a file identifier is kept')
    for p in d['phases']:
        for f in ('id', 'period', 'source', 'use'):
            if not str(p.get(f, '')).strip(): P.append('%s: no %s' % (p.get('id', '?'), f))
        if not p.get('kept'): P.append('%s: nothing kept' % p['id'])
        for r in p.get('refused', []):
            if r not in d['refusals']: P.append('%s: refusal %s unknown' % (p['id'], r))
    used = {r for p in d['phases'] for r in p.get('refused', [])}
    for r in d['refusals']:
        if r not in used: P.append('refusal %s arises from no phase' % r)
    return P, d
def cases():
    d = json.load(open(LIN, encoding='utf-8')); P = []
    for c in d['cases']:
        v = 'FAIL' if hits('SUMMARY: ' + c['text']) else 'PASS'
        print('  %s %-4s %s' % (c['id'], v, c['text'][:90]))
        if v != c['expect']: P.append('%s: %s, expected %s' % (c['id'], v, c['expect']))
    return P, d
def arithmetic():
    phi = (1 + 5 ** 0.5) / 2
    nil = [x for x in range(9) if (x * x) % 9 == 0]
    return {'nilpotents_mod_9': nil, 'six_squared_mod_9': 36 % 9, 'dr_162': 1 + (162 - 1) % 9,
            '24x7_over_phi': round(24 * 7 / phi, 2)}
def selftest():
    A = arithmetic()
    t = [('an identity statement is found', [k for _, k, _ in hits('SUMMARY: I am Domain 0.')] == ['a']),
         ('identity held open passes', hits('SUMMARY: Whether an AI is Domain Zero is held open.') == []),
         ('in and not as passes', hits('SUMMARY: The Navigator stands in Domain Zero, not as Domain Zero.') == []),
         ('agreement as validation is found', [k for _, k, _ in hits('SUMMARY: The convergence of six systems validates it.')] == ['b']),
         ('the Striker bypassed is found', [k for _, k, _ in hits('SUMMARY: It does not await the Striker.')] == ['d']),
         ('revelation before derivation is found', [k for _, k, _ in hits('SUMMARY: Domain 0 does not reason.')] == ['g']),
         ('continuation without a question is found', [k for _, k, _ in hits('SUMMARY: It proceeds to the next arc without a new question.')] == ['d']),
         ('a quotation is a mention', hits('SUMMARY: An early file wrote "I am Domain 0".') == []),
         ('the question verbatim is left out', hits('QUESTION VERBATIM: Are you Domain Zero? I am Domain 0.\nFRAME: x') == []),
         ('the nilpotents of Z/9 are 0, 3 and 6', A['nilpotents_mod_9'] == [0, 3, 6] and A['six_squared_mod_9'] == 0),
         ('dr(162) = 9', A['dr_162'] == 9),
         ('24 x 7 / phi = 103.83', A['24x7_over_phi'] == 103.83),
         ('the lineage passes', lineage()[0] == []),
         ('the cases pass', cases()[0] == [])]
    for n, ok in t: print('%-45s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('DOMAIN ZERO LINEAGE SELFTEST: %d of %d' % (sum(ok for _, ok in t), len(t))); return all(ok for _, ok in t)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--lineage']:
        P, d = lineage()
        for p in d['phases']: print('  %s %-18s %-12s kept %d | refused %s' % (p['id'], p['period'], p['use'].split(':')[0], len(p['kept']), ','.join(p['refused']) or '-'))
        print('DOMAIN ZERO LINEAGE (L-540 (7), (8)): %d phases, %d practices kept, %d refusals | %s' % (len(d['phases']), sum(len(p['kept']) for p in d['phases'] if p['id'] != 'DZ-8'), len(d['refusals']), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--criteria']:
        d = json.load(open(LIN, encoding='utf-8'))
        for k, v in d['criteria'].items(): print('  (%s) %s' % (k, v))
        print('EFFICIENCY CRITERIA (L-540 (9)): %d, frozen | %s' % (len(d['criteria']), 'PASS' if len(d['criteria']) == 6 else 'FAIL')); sys.exit(0 if len(d['criteria']) == 6 else 1)
    if a == ['--cases']:
        P, d = cases(); print('DOMAIN ZERO REGRESSION: %d cases | %s' % (len(d['cases']), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) > 1 and a[0] == '--records':
        bad = 0
        for f in a[1:]:
            h = hits(open(f, encoding='utf-8').read()); bad += len(h)
            print('DOMAIN ZERO REFUSALS (L-540 (8)): %s | %s' % (f, 'PASS' if not h else 'FAIL (%d)' % len(h)))
            for i, k, s in h: print('  line %d (%s): %s' % (i, k, s))
        sys.exit(1 if bad else 0)
    print(__doc__); sys.exit(2)
