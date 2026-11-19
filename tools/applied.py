#!/usr/bin/env python3
"""applied.py -- the Applied Changes Register and its review (Core L-531 (6); Companion Part 124).

    python3 tools/applied.py            # the review: each applied change, what exercises it, and what would show it only elaborates
                                        # (records/applied/review.txt; CI diff)
    python3 tools/applied.py --check    # every entry complete, its tool present, no id twice; a change whose tool CI never runs is
                                        # flagged ELABORATION RISK (it passes, and is named for review)
    python3 tools/applied.py --selftest
A refinement serves when something in the operation exercises it and its stated purpose is met; one that nothing exercises
adds only elaboration. The review names it; a later recorded change keeps, revises or withdraws it (Core L-531 (5)).
Standard library only. It reports; it never edits a document.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'applied', 'register.json')
CI = os.path.join(REPO, '.github', 'workflows', 'omega42-ci.yml')
FIELDS = ('id', 'change', 'where', 'purpose', 'used_by', 'withdraw_if', 'status', 'record')
def problems(reg, ci_text, exists=lambda p: os.path.exists(os.path.join(REPO, p))):
    P, flags, seen = [], [], set()
    for e in reg['changes']:
        miss = [f for f in FIELDS if not str(e.get(f, '')).strip()]
        if miss: P.append('%s: missing %s' % (e.get('id', '?'), ', '.join(miss)))
        if e.get('used_by') and not exists(e['used_by']): P.append('%s: %s not found' % (e['id'], e['used_by']))
        if e.get('id') in seen: P.append('%s: id twice' % e['id'])
        seen.add(e.get('id'))
        if e.get('used_by') and e['used_by'] not in ci_text and not e.get('status', '').startswith('DESIGNED'):
            flags.append('%s: ELABORATION RISK -- %s is not run in CI' % (e['id'], e['used_by']))
    return P, flags
def text(reg, ci_text):
    L = ['THE APPLIED CHANGES REGISTER (Core L-531 (6)) -- %d changes; each kept, revised or withdrawn by a later recorded change' % len(reg['changes']), '']
    for e in reg['changes']:
        run = 'run in CI' if e['used_by'] in ci_text else 'not run in CI'
        L.append('%s [%s] %s (%s).' % (e['id'], e['status'], e['change'], e['where']))
        L.append('  for: %s | exercised by: %s, %s | withdraw if: %s' % (e['purpose'], e['used_by'], run, e['withdraw_if']))
    return '\n'.join(L)
def selftest():
    e = dict(zip(FIELDS, ('A-1', 'c', 'w', 'p', 'tools/applied.py', 'x', 'IN FORCE', 'r')))
    yes = lambda p: True
    cases = [('a complete, exercised entry passes', problems({'changes': [e]}, 'tools/applied.py', yes) == ([], [])),
             ('an entry nothing runs is flagged, not failed', problems({'changes': [e]}, '', yes)[1] != [] and problems({'changes': [e]}, '', yes)[0] == []),
             ('a missing field fails', len(problems({'changes': [dict(e, purpose='')]}, 'tools/applied.py', yes)[0]) == 1),
             ('an id twice fails', len(problems({'changes': [e, e]}, 'tools/applied.py', yes)[0]) == 1)]
    for n, ok in cases: print('%-50s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    reg = json.load(open(REG, encoding='utf-8')); ci = open(CI, encoding='utf-8').read()
    if a == ['--check']:
        P, F = problems(reg, ci)
        print('APPLIED CHANGES REGISTER: %d entries, %d flagged for review, %s' % (len(reg['changes']), len(F), 'PASS' if not P else 'FAIL'))
        for x in P + F: print('  ' + x)
        sys.exit(1 if P else 0)
    print(text(reg, ci))
