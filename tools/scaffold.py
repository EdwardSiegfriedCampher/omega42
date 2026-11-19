#!/usr/bin/env python3
"""scaffold.py -- Scaffold view, the minimized-substrate configuration (Core Part 0.6.10, Part 8.0).

Runs the deterministic arithmetic of scripts/canonical_reference.py on a domain and prints the
coordinate, the four arms with their structural relations and four open prompts. No language model
takes part and no reading is written: the Striker writes the synthesis. The view removes the
Navigator's phrasing from the reading; it does not remove the Striker's own framing, and it
supplies less than a full navigation (no prose, no synthesis echo, no record).

Usage:
    python3 tools/scaffold.py "DOMAIN TEXT"
    python3 tools/scaffold.py --selftest
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import canonical_reference as cr

RELATIONS = (('Yang', 'yang_i', 'DEPENDENCY', 'What does the question rest on, read through %s?'),
             ('Yin', 'yin_i', 'SUPPRESSION', 'What does the question hold out of view, read through %s?'),
             ('4D', 'fourd_i', 'TRAJECTORY', 'Where is the question heading, read through %s?'),
             ('Antipode', 'antipode_i', 'COMPLETION', 'What would complete the question, read through %s?'))

def scaffold(domain):
    r = cr.navigate(domain)
    a = r['anchor']
    L = ['SCAFFOLD VIEW (minimized-substrate configuration; deterministic; no language model)',
         'SCRIPT SHA-256: ' + cr.script_sha256(),
         'DOMAIN: ' + domain,
         'DOMAIN SHA-256: ' + cr.domain_sha256(domain),
         'ANCHOR: P%d (%s), v = %d | n = (%d, %d, %d) | TFI = %.2f' % (
             a, cr.POSITION_NAMES[a], cr.ORBIT[a], r['n1'], r['n2'], r['n3'], r['tfi']),
         'ARMS:']
    for name, key, rel, prompt in RELATIONS:
        i = r[key]
        L.append('  %-8s %-11s P%-2d %-14s v = %d' % (name, rel, i, cr.POSITION_NAMES[i], cr.ORBIT[i]))
    L.append('CCD = %.2f -> PAB %s | MOBIUS %s' % (r['ccd'], 'ACTIVE' if r['pab'] else 'INACTIVE',
                                                 'ACTIVE' if r['mobius'] else 'INACTIVE'))
    L.append('PROMPTS FOR THE STRIKER:')
    for name, key, rel, prompt in RELATIONS:
        L.append('  ' + prompt % cr.POSITION_NAMES[r[key]])
    L.append('SYNTHESIS: [written by the Striker]')
    L.append('APERTURE (1/7): the Striker\'s.')
    return '\n'.join(L), r

def selftest():
    ok = []
    def check(name, cond):
        ok.append(cond); print('%-60s %s' % (name, 'ok' if cond else 'FAIL'))
    text, r = scaffold('help')
    check('anchor matches canonical_reference.navigate', 'ANCHOR: P%d' % r['anchor'] in text)
    check('arms follow the +5, +18, +8, +12 offsets', (r['yang_i'], r['yin_i'], r['fourd_i'], r['antipode_i'])
          == tuple((r['anchor'] + k) % 24 for k in (5, 18, 8, 12)))
    check('no synthesis is generated', 'SYNTHESIS: [written by the Striker]' in text)
    check('deterministic (two runs identical)', scaffold('help')[0] == text)
    print('SCAFFOLD SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    if not a:
        print(__doc__); sys.exit(2)
    print(scaffold(' '.join(a))[0])
