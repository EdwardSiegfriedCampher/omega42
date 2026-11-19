#!/usr/bin/env python3
"""prominence.py -- M313 Tool Prominence Register (Core Part 3.39, L-494 item 4).

Reads records/prominence/register.json, prints the register (records/prominence/register.txt, diffed in CI) and,
with --check, fails when
  * an entry has a role other than FOUNDATION, LEADING, CONTEXTUAL or CANDIDATE;
  * there is not exactly one FOUNDATION entry -- the defined structure, which no tool replaces;
  * a LEADING entry lacks any of the six promotion fields (structure, construction, mapping, preserved_lost,
    contribution, open) or any of the criteria A to D;
  * an entry has no class of inquiries it serves.
A tool can therefore take the lead only with its mapping, its preserved and lost properties, its contribution and its
open questions on record; prominence follows demonstrated contribution, never prestige or analogy alone.

Usage:
    python3 tools/prominence.py            # the register
    python3 tools/prominence.py --check
    python3 tools/prominence.py --selftest
Standard library only.
"""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, 'records', 'prominence', 'register.json')
FIELDS = ('structure', 'construction', 'mapping', 'preserved_lost', 'contribution', 'open')


def problems(reg):
    out = []
    roles = set(reg['roles'])
    if sum(e['role'] == 'FOUNDATION' for e in reg['entries']) != 1: out.append('there must be exactly one FOUNDATION entry')
    for e in reg['entries']:
        if e['role'] not in roles: out.append('%s: unknown role %s' % (e['tool'], e['role']))
        if not e.get('class'): out.append('%s: no class of inquiries' % e['tool'])
        if e['role'] == 'LEADING':
            out += ['%s: promotion field %s missing' % (e['tool'], f) for f in FIELDS if not e.get(f)]
            out += ['%s: criterion %s missing' % (e['tool'], c) for c in 'ABCD' if not e.get('criteria', {}).get(c)]
    return out


def text(reg):
    L = ['M313 TOOL PROMINENCE REGISTER (Core Part 3.39, %s) | %s | %s' % (reg['law'].split(';')[0], reg['spec'], reg['date']),
         'Roles: ' + ' | '.join('%s -- %s' % kv for kv in reg['roles'].items())]
    for e in reg['entries']:
        L.append('')
        L.append('%s: %s' % (e['role'], e['tool']))
        L.append('  CLASS: %s' % e['class'])
        for f in FIELDS:
            if e.get(f): L.append('  %s: %s' % (f.upper().replace('_', ' AND '), e[f]))
        for c, v in sorted(e.get('criteria', {}).items()): L.append('  CRITERION %s: %s' % (c, v))
        if e.get('note'): L.append('  NOTE: %s' % e['note'])
    p = problems(reg)
    L.append('')
    L.append('CHECK: %s' % ('PASS' if not p else 'FAIL -- ' + '; '.join(p)))
    return '\n'.join(L)


def selftest():
    reg = json.load(open(REG, encoding='utf-8')); ok = True
    def check(label, c):
        nonlocal ok; print('%-66s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    check('the register passes', not problems(reg))
    bad = json.loads(json.dumps(reg)); lead = next(e for e in bad['entries'] if e['role'] == 'LEADING'); del lead['mapping']
    check('a LEADING entry without its mapping fails', any('mapping' in p for p in problems(bad)))
    bad = json.loads(json.dumps(reg)); bad['entries'][0]['role'] = 'LEADING'
    check('removing the FOUNDATION entry fails', any('FOUNDATION' in p for p in problems(bad)))
    bad = json.loads(json.dumps(reg)); bad['entries'][-1]['role'] = 'DOMINANT'
    check('an unknown role fails', any('unknown role' in p for p in problems(bad)))
    print('M313 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    reg = json.load(open(REG, encoding='utf-8'))
    if a and a[0] == '--check':
        p = problems(reg); print('M313 CHECK: %s' % ('PASS' if not p else 'FAIL -- ' + '; '.join(p))); sys.exit(0 if not p else 1)
    print(text(reg))
