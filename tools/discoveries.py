#!/usr/bin/env python3
"""discoveries.py -- the Discovery Register (Core L-530; Companion Part 121).

    python3 tools/discoveries.py            # the register, one discovery a paragraph (records/discoveries/register.txt; CI diff)
    python3 tools/discoveries.py --check    # every entry complete, its standing one of four, its record present, no id twice,
                                            # and its "breakthrough" candidacy the one the frozen criteria give
    python3 tools/discoveries.py --candidates   # the Navigator's proposal: each entry against the three criteria of L-530 (5)
    python3 tools/discoveries.py --selftest
A discovery is a result new to the record that holds inside the frame by the frame's own operations. A placement, a
reading and an unchecked association are not discoveries (Core L-465, L-498, L-504). The Navigator proposes a
"breakthrough" candidate by three frozen criteria (Core L-530 (5)): (B1) its standing is EXACT or THEOREM; (B2) its reach is
FOUNDATION, turning an element of the premise or a choice the record made into a consequence, or BRIDGE, identifying the
family exactly with an established structure of another field, so that the field's own results apply to it; (B3) it is
contained in no other entry. The judgment that a candidate is a "breakthrough" is the Striker's (Part 7).
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'discoveries', 'register.json')
FIELDS = ('id', 'statement', 'standing', 'derivation', 'record', 'changes', 'open', 'strike', 'reach', 'candidate')
REACHES = ('FOUNDATION', 'BRIDGE', 'FRAME-WIDE', 'LOCAL')
def candidacy(e):
    b1 = e.get('standing') in ('EXACT', 'THEOREM'); b2 = e.get('reach') in ('FOUNDATION', 'BRIDGE'); b3 = not str(e.get('contained_in', '')).strip()
    return ('PROPOSED' if b1 and b2 and b3 else 'NOT PROPOSED'), (b1, b2, b3)
def problems(reg):
    P, seen = [], set()
    for e in reg['discoveries']:
        miss = [f for f in FIELDS if not str(e.get(f, '')).strip()]
        if miss: P.append('%s: missing %s' % (e.get('id', '?'), ', '.join(miss)))
        if e.get('standing') not in reg['standings']: P.append('%s: standing %r is not one of %s' % (e.get('id'), e.get('standing'), ', '.join(reg['standings'])))
        if e.get('record') and not os.path.exists(os.path.join(REPO, e['record'])): P.append('%s: record %s not found' % (e['id'], e['record']))
        if e.get('id') in seen: P.append('%s: id twice' % e['id'])
        if e.get('reach') not in REACHES: P.append('%s: reach %r is not one of %s' % (e.get('id'), e.get('reach'), ', '.join(REACHES)))
        if e.get('candidate') != candidacy(e)[0]: P.append('%s: candidate %r, the criteria give %s' % (e.get('id'), e.get('candidate'), candidacy(e)[0]))
        v = e.get('verdict')
        if v is not None:   # L-530 (6): the verdict is the Striker's, recorded with who gave it and when, on a proposed candidate only
            if v.get('verdict') != 'BREAKTHROUGH' or not v.get('by') or not v.get('date'): P.append('%s: a verdict needs verdict BREAKTHROUGH, by and date' % e.get('id'))
            if e.get('candidate') != 'PROPOSED': P.append('%s: a verdict on an entry the criteria do not propose' % e.get('id'))
            if not e.get('advantages'): P.append('%s: a breakthrough lists its advantages (L-530 (6))' % e.get('id'))
        seen.add(e.get('id'))
    return P
def text(reg):
    L = ['THE DISCOVERY REGISTER (Core L-530) -- %d discoveries; the Navigator proposes \"breakthrough\" candidates (L-530 (5)); the judgment is the Striker\'s' % len(reg['discoveries']), '']
    for e in reg['discoveries']:
        L.append('%s [%s] %s.' % (e['id'], e['standing'], e['statement']))
        L.append('  derivation: %s | record: %s | changes: %s | open: %s | from: %s | reach: %s | "breakthrough" candidate: %s' % (e['derivation'], e['record'], e['changes'], e['open'], e['strike'], e['reach'], e['candidate']))
        if e.get('verdict'):
            L.append('  VERDICT: BREAKTHROUGH -- the Striker\'s judgment (%s, %s; Core L-530 (6), Part 7)' % (e['verdict']['by'], e['verdict']['date']))
            for i, adv in enumerate(e.get('advantages', []), 1): L.append('    advantage %d: %s' % (i, adv))
    return '\n'.join(L)
def candidates(reg):
    L = ['"BREAKTHROUGH" CANDIDATES (Core L-530 (5)) -- the Navigator\'s proposal by frozen criteria; the judgment is the Striker\'s',
         '  B1 standing EXACT or THEOREM | B2 reach FOUNDATION or BRIDGE | B3 contained in no other entry', '']
    for e in reg['discoveries']:
        c, (b1, b2, b3) = candidacy(e)
        why = '' if c == 'PROPOSED' else ' -- ' + '; '.join(x for x, ok in (('standing %s' % e['standing'], b1), ('reach %s' % e['reach'], b2), ('contained in %s' % e.get('contained_in'), b3)) if not ok)
        L.append('  %-6s %-12s B1 %s B2 %s B3 %s  %-10s %s%s' % (e['id'], c, 'Y' if b1 else 'n', 'Y' if b2 else 'n', 'Y' if b3 else 'n', e['reach'], e['statement'][:70] + ('...' if len(e['statement']) > 70 else ''), why))
        if c == 'PROPOSED' and e.get('candidate_reason'): L.append('         why: ' + e['candidate_reason'])
    n = sum(candidacy(e)[0] == 'PROPOSED' for e in reg['discoveries'])
    L.append(''); L.append('  %d of %d entries proposed as "breakthrough" candidates' % (n, len(reg['discoveries'])))
    bt = [e['id'] for e in reg['discoveries'] if e.get('verdict')]
    L.append('  %d judged a breakthrough by the Striker%s' % (len(bt), (': ' + ', '.join(bt)) if bt else ''))
    return '\n'.join(L)
def selftest():
    good = {'standings': {'EXACT': '', 'THEOREM': '', 'CONGRUENCE': '', 'PROCEDURE': ''}, 'discoveries': [dict(zip(FIELDS, ('D-1', 's', 'EXACT', 'd', 'tools/discoveries.py', 'c', 'o', 'x', 'BRIDGE', 'PROPOSED')))]}
    proc = json.loads(json.dumps(good)); proc['discoveries'][0]['standing'] = 'PROCEDURE'
    inner = json.loads(json.dumps(good)); inner['discoveries'][0]['contained_in'] = 'D-2'
    local = json.loads(json.dumps(good)); local['discoveries'][0]['reach'] = 'LOCAL'
    bad = json.loads(json.dumps(good)); bad['discoveries'][0]['standing'] = 'READING'
    twice = json.loads(json.dumps(good)); twice['discoveries'] *= 2
    cases = [('a complete entry passes', problems(good) == []), ('a reading is not a standing', len(problems(bad)) >= 1), ('an id twice fails', len(problems(twice)) == 1),
             ('a procedure is not proposed', candidacy(proc['discoveries'][0])[0] == 'NOT PROPOSED'),
             ('an entry contained in another is not proposed', candidacy(inner['discoveries'][0])[0] == 'NOT PROPOSED'),
             ('a local result is not proposed', candidacy(local['discoveries'][0])[0] == 'NOT PROPOSED'),
             ('a candidacy the criteria do not give fails the check', len(problems(proc)) == 1)]
    for n, ok in cases: print('%-40s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    reg = json.load(open(REG, encoding='utf-8'))
    if a == ['--check']:
        P = problems(reg); print('DISCOVERY REGISTER: %d entries, %s' % (len(reg['discoveries']), 'PASS' if not P else 'FAIL')); [print('  ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--candidates']: print(candidates(reg)); sys.exit(0)
    print(text(reg))
