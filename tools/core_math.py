#!/usr/bin/env python3
"""core_math.py -- the complete mathematical register in the Core (Core Part 0.0.10; Part 0.0.5 Rule 19).

records/math/results.json is the one source of Omega42's mathematics. This tool writes, from it, the paragraphs of Core
Part 0.0.10, one for every result, with its statement, domain, derivation, dependencies and the command that recomputes
it, and the paragraphs of Companion Part 216.1, one for every result, with what does not follow from it (Core Part 0.0.5
Rule 35); and it confirms that the Core and the Companion, as rendered in ai/, hold every one of them word for word, so
that an AI given the Core alone can recompute and extend every result.

    python3 tools/core_math.py --paras      # the paragraphs of Part 0.0.10, one a line
    python3 tools/core_math.py --scope      # the paragraphs of Companion Part 216.1, one a line
    python3 tools/core_math.py --check      # every register entry stands in the Core and its scope in the Companion
    python3 tools/core_math.py --selftest
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'math', 'results.json')
CORE = os.path.join(REPO, 'ai', 'Omega42_Core_V335_Rev450.md')
COMP = os.path.join(REPO, 'ai', 'Omega42_Companion_V335_Rev450.md')
HEAD = '0.0.10 THE COMPLETE MATHEMATICAL REGISTER'
INTRO = ('0.0.10.0 Source. Every result of records/math/results.json, written here by tools/core_math.py and never by hand '
         '(Part 0.0.5 Rule 19). Each entry gives its status, statement, domain, derivation, what it depends on, and the command '
         'whose named selftest line recomputes it; python3 tools/math_register.py runs every check, and python3 '
         'tools/core_math.py --check confirms that this part holds the register as it stands.')
SCOPE_HEAD = ('216.1 What does not follow from each result [EXACT for the results; CONSTRUCTED for the scopes]. For every '
              'result of records/math/results.json, what does not follow from it, written here by tools/core_math.py and never by '
              'hand (Core Part 0.0.5 Rules 19 and 35); the result itself, with its recompute command, stands in Core Part 0.0.10.')
def clean(s):
    return ' '.join(str(s).split()).rstrip('.;, ')
def entry(i, r):
    return ('0.0.10.%d %s [%s]. %s. Domain: %s. Derivation: %s. Depends on: %s. Recompute: python3 %s '
            '--selftest, the line beginning "%s".') % (i, r['id'], r['status'], clean(r['statement']), clean(r['domain']),
            clean(r['derivation']), clean(r.get('depends') or 'none'), r['tool'], clean(r['check']))
def scope(i, r):
    return '216.1.%d %s (Core Part 0.0.10.%d). Does not follow: %s.' % (i, r['id'], i, clean(r['does_not_follow']))
def scope_paras(results=None):
    if results is None: results = json.load(open(REG, encoding='utf-8'))['results']
    return [SCOPE_HEAD] + [scope(i, r) for i, r in enumerate(results, 1)]
def paras(results=None):
    if results is None: results = json.load(open(REG, encoding='utf-8'))['results']
    return [HEAD, INTRO] + [entry(i, r) for i, r in enumerate(results, 1)]
def check(core_text=None, comp_text=None):
    if core_text is None:
        if not os.path.exists(CORE): return ['no Core edition at ai/; run python3 tools/ai_edition.py --build']
        core_text = open(CORE, encoding='utf-8').read()
    if comp_text is None:
        comp_text = open(COMP, encoding='utf-8').read() if os.path.exists(COMP) else core_text
    lines = set(l.strip().lstrip('#').strip() for l in core_text.split('\n'))
    results = json.load(open(REG, encoding='utf-8'))['results']
    P = []
    for i, r in enumerate(results, 1):
        if entry(i, r) not in lines: P.append('%s is not in the Core as generated (Part 0.0.10.%d)' % (r['id'], i))
    if INTRO not in lines: P.append('the source paragraph 0.0.10.0 is missing')
    clines = set(l.strip().lstrip('#').strip() for l in comp_text.split('\n'))
    for i, r in enumerate(results, 1):
        if scope(i, r) not in clines: P.append('%s: its scope is not in the Companion as generated (Part 216.1.%d)' % (r['id'], i))
        if 'Does not follow' in entry(i, r): P.append('%s: a scope stands in the Core' % r['id'])
    if SCOPE_HEAD not in clines: P.append('the head paragraph of Companion Part 216.1 is missing')
    return P
def selftest():
    r = {'id': 'MF-99', 'status': 'EXACT', 'statement': 'A^24 = I mod 9.', 'domain': 'Z/9', 'derivation': 'direct', 'depends': '',
         'does_not_follow': 'anything else', 'tool': 'tools/x.py', 'check': 'cycle: A^24'}
    e = entry(3, r)
    text = '\n'.join([HEAD, INTRO, e])
    cases = [('an entry carries its id, status and recompute command', e.startswith('0.0.10.3 MF-99 [EXACT]. A^24 = I mod 9. Domain: Z/9.') and 'python3 tools/x.py --selftest' in e),
             ('an empty dependency is written as none', 'Depends on: none.' in e),
             ('no doubled full stop', '..' not in e),
             ('the Core entry carries no scope; the Companion line does', 'Does not follow' not in e and scope(3, r) == '216.1.3 MF-99 (Core Part 0.0.10.3). Does not follow: anything else.'),
             ('the register as it stands is in a text that holds it', not [p for p in check('\n'.join(paras()), '\n'.join(scope_paras())) if 'MF-' in p]),
             ('a Core that lacks an entry fails the check', any('MF-' in p for p in check(text)))]
    for n, ok in cases: print('%-58s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('CORE MATHEMATICS SELFTEST: %s' % ('PASS' if all(ok for _, ok in cases) else 'FAIL')); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--paras']: print('\n'.join(paras())); sys.exit(0)
    if a == ['--scope']: print('\n'.join(scope_paras())); sys.exit(0)
    if a == ['--check']:
        P = check(); n = len(json.load(open(REG, encoding='utf-8'))['results'])
        print('CORE MATHEMATICS (Part 0.0.10; Companion Part 216.1): %d register entries | %s' % (n, 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
