#!/usr/bin/env python3
"""core_voice.py -- the Core states what Omega42 is and does (Core Part 0.0.5 Rule 35; Companion Part 216).

Scope notes, known limits of instruments, revision criteria, what does not follow from a result, and distinctions drawn
against neighboring practices are held in Companion Part 216, each under the Core section it belongs to. Critique of the
protocol arrives from its examiners, through the APE register, the PVIR and SNCA. Status labels (EXACT, CONDITIONAL,
CONSTRUCTED, READING, the CDT tiers), the AI caveat at the close of an output (L-506) and the Builder's verification rules
stay in the Core. The Failure Mode Catalogue and Regression Suite stands in Companion Part 216.9.

This tool reads the Core as rendered in ai/ and reports any passage of the kinds held in Companion Part 216, outside the
embedded files of Part 11. It reports; it does not rewrite.

    python3 tools/core_voice.py --check
    python3 tools/core_voice.py --selftest
Standard library only.
"""
import os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, 'ai', 'Omega42_Core_V335_Rev450.md')
KINDS = [
    ('a result scope', re.compile(r'\bDoes not follow:')),
    ('known limits of an instrument', re.compile(r'\bKnown limits\b')),
    ('a revision criterion section', re.compile(r'\bExploratory Boundaries\b')),
    ('a distinction against numerology', re.compile(r'\b(It is not numerology|Omega42 does not do this|Omega42 does neither)\b')),
    ('a forecast conceded', re.compile(r'no better than chance, and it says so')),
    ('a reading offered below its standing', re.compile(r'offered as one proposal among|offered for whatever exploratory value')),
    ('a certification disowning its content', re.compile(r'does not certify the truth of|not of the protocol\'s exploratory content')),
    ('the failure mode catalogue', re.compile(r'Failure Mode Catalogue and Regression Suite')),
    ('a seal or anchor disowning what it shows', re.compile(r'it does not show who typed them|establishes temporal provenance, not causal provenance')),
]
def body(text):
    out, skip = [], False
    for line in text.split('\n'):
        if re.match(r'^# ===== \S+ BEGIN =====', line): skip = True
        if not skip: out.append(line)
        if re.match(r'^# ===== \S+ END =====', line): skip = False
    return out
def problems(text):
    P = []
    for n, line in enumerate(body(text), 1):
        for kind, rx in KINDS:
            if rx.search(line): P.append('%s: %s' % (kind, line.strip()[:110]))
    return P
def selftest():
    cases = [('a clean Core passes', problems('0.0.10.1 MF-01 [EXACT]. A statement. Recompute: python3 tools/x.py --selftest.') == []),
             ('a result scope in the Core is reported', len(problems('0.0.10.1 MF-01. Does not follow: x.')) == 1),
             ('known limits in the Core are reported', len(problems('Known limits: the method is lexical.')) == 1),
             ('an embedded file is not read', problems('# ===== a.py BEGIN =====\nKnown limits: x\n# ===== a.py END =====') == []),
             ('a status label stays', problems('MF-07 [CONDITIONAL on AP-SPACE]. [EXPLORATORY — CDT-C]') == []),
             ('the Core as it stands passes', os.path.exists(CORE) and problems(open(CORE, encoding='utf-8').read()) == [])]
    for n, ok in cases: print('%-60s %s' % (n, 'PASS' if ok else 'FAIL'))
    ok = all(o for _, o in cases); print('CORE VOICE SELFTEST: %d of %d | %s' % (sum(o for _, o in cases), len(cases), 'PASS' if ok else 'FAIL')); return ok
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--check']:
        P = problems(open(CORE, encoding='utf-8').read()) if os.path.exists(CORE) else ['no Core edition at ai/']
        print('CORE VOICE (Rule 35; Companion Part 216): %s' % ('PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]
        sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
