#!/usr/bin/env python3
"""pvir.py -- the Protocol Vulnerability and Improvement Register (Core L-560 (4); Part 0.0.5 Rule 30; IMPROVE.md).

Any person or AI may examine Omega42 and enter what they find: a vulnerability or an improvement. Each entry names one of
ten classes and one of five forms, a severity, a status, and, where one can be written, a test that shows it. Entries that
recur, above all from different AI architectures, rise in priority. This tool keeps the register well formed and prints it.

    python3 tools/pvir.py --check     # every entry well formed; identifiers unique and in order
    python3 tools/pvir.py --list      # the register, one line an entry, with counts by class, form and status
    python3 tools/pvir.py --selftest
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'pvir', 'register.json')
CLASSES = ('mathematical', 'logical', 'structural', 'representational', 'navigational', 'computational', 'epistemic',
           'architectural', 'operational', 'existential')
FORMS = ('break', 'improve', 'extend', 'reinterpret', 'rebuild')
SEVERITY = ('low', 'medium', 'high')
STATUS = ('proposed', 'under investigation', 'verified', 'accepted', 'rejected')
FIELDS = ('id', 'title', 'class', 'form', 'severity', 'status', 'test', 'finder', 'date', 'resolution')
def problems(entries):
    P = []
    for n, e in enumerate(entries, 1):
        tag = e.get('id', '#%d' % n)
        for f in FIELDS:
            if f not in e or not str(e[f]).strip(): P.append('%s: no %s' % (tag, f))
        if e.get('id') != 'PV-%03d' % n: P.append('%s: expected PV-%03d' % (tag, n))
        if e.get('class') not in CLASSES: P.append('%s: class %r is not one of the ten' % (tag, e.get('class')))
        if e.get('form') not in FORMS: P.append('%s: form %r is not one of the five' % (tag, e.get('form')))
        if e.get('severity') not in SEVERITY: P.append('%s: severity %r' % (tag, e.get('severity')))
        if e.get('status') not in STATUS: P.append('%s: status %r' % (tag, e.get('status')))
    return P
def listing(entries):
    L = ['PROTOCOL VULNERABILITY AND IMPROVEMENT REGISTER (Core L-560 (4)): %d entries' % len(entries)]
    for e in entries:
        L.append('  %s %-19s %-16s %-11s %-6s %s' % (e['id'], e['status'], e['class'], e['form'], e['severity'], e['title']))
    for name, key, vals in (('class', 'class', CLASSES), ('form', 'form', FORMS), ('status', 'status', STATUS)):
        L.append('  by %s: %s' % (name, ', '.join('%s %d' % (v, sum(e[key] == v for e in entries)) for v in vals if any(e[key] == v for e in entries))))
    return '\n'.join(L)
def load():
    return json.load(open(REG, encoding='utf-8'))['entries']
def selftest():
    ok_e = {'id': 'PV-001', 'title': 't', 'class': 'existential', 'form': 'extend', 'severity': 'low', 'status': 'proposed',
            'test': 'none can be written', 'finder': 'x', 'date': '2026-11-12', 'resolution': 'open'}
    cases = [('a well-formed entry passes', problems([ok_e]) == []),
             ('an unknown class is refused', any('class' in p for p in problems([dict(ok_e, **{'class': 'cosmic'})]))),
             ('an unknown form is refused', any('form' in p for p in problems([dict(ok_e, form='praise')]))),
             ('identifiers must run in order', any('expected' in p for p in problems([dict(ok_e, id='PV-002')]))),
             ('a missing test field is reported', any('no test' in p for p in problems([dict(ok_e, test='')]))),
             ('ten classes and five forms', len(CLASSES) == 10 and len(FORMS) == 5),
             ('the register in the repository is well formed', problems(load()) == [])]
    for n, ok in cases: print('%-50s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('PVIR SELFTEST: %s' % ('PASS' if all(ok for _, ok in cases) else 'FAIL')); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--list']: print(listing(load())); sys.exit(0)
    if a == ['--check']:
        P = problems(load()); print('PVIR: %d entries | %s' % (len(load()), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
