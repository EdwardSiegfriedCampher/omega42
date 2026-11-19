#!/usr/bin/env python3
"""open_register.py -- the register of open items (Core Part 12, item 39; Core L-531 (3); Companion Part 141).

Every item the record keeps OPEN, each with what it needs, who can close it, the condition under which it closes and the
avenue it belongs to, so that an item is never closed by a plausible answer and a study not run is never replaced by a
forecast of its result.

    python3 tools/open_register.py           # the register, one item a line (records/open/register.txt; CI diff)
    python3 tools/open_register.py --check   # every item complete, no id twice
    python3 tools/open_register.py --selftest
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'open', 'register.json')
FIELDS = ('id', 'item', 'needs', 'decider', 'closure', 'avenue', 'since')
def problems(r):
    P, seen = [], set()
    for e in r['items']:
        miss = [f for f in FIELDS if not str(e.get(f, '')).strip()]
        if miss: P.append('%s: missing %s' % (e.get('id', '?'), ', '.join(miss)))
        if e.get('id') in seen: P.append('%s: id twice' % e['id'])
        seen.add(e.get('id'))
    return P
def text(r):
    L = ['THE REGISTER OF OPEN ITEMS (Core Part 12, item 39) -- %d items, each closed only when its condition is met by those named' % len(r['items']), '']
    for e in r['items']:
        L.append('%s [%s, since %s] %s' % (e['id'], e['avenue'], e['since'], e['item']))
        L.append('  needs: %s | closed by: %s | closes when: %s' % (e['needs'], e['decider'], e['closure']))
    return '\n'.join(L)
def selftest():
    good = {'items': [dict((f, 'x') for f in FIELDS)]}
    bad = {'items': [dict((f, 'x') for f in FIELDS if f != 'closure')]}
    cases = [('a complete item passes', problems(good) == []), ('an item without its closure fails', len(problems(bad)) == 1), ('an id twice fails', len(problems({'items': good['items'] * 2})) == 1)]
    for n, ok in cases: print('%-40s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('OPEN REGISTER SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    r = json.load(open(REG, encoding='utf-8'))
    if a == ['--check']:
        P = problems(r); print('OPEN REGISTER: %d items, %s' % (len(r['items']), 'PASS' if not P else 'FAIL')); [print('  ' + p) for p in P]; sys.exit(1 if P else 0)
    print(text(r))
