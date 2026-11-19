#!/usr/bin/env python3
"""lite_view.py -- the Striker-facing short view of a navigation, rendered from a full, audited one.

A Lite view is never a separate procedure: it is produced only from a navigation in the canonical
skeleton (Core Part 8.0) that passes the output audit (L-457). If the audit fails, nothing is rendered.
The view keeps the domain, the coordinate, THE ANSWER and the Navigator's identity, and omits the
working; the full navigation remains the record, and the view names it by its SHA-256.

Usage:
    python3 tools/lite_view.py NAVIGATION.txt [--corpus DIR]
"""
import hashlib, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.join(HERE, '..', 'scripts')

def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(2)
    path = a[0]
    cmd = [sys.executable, os.path.join(SCRIPTS, 'm193_m225.py'), os.path.join(SCRIPTS, 'canonical_reference.py'), '--audit', path]
    if '--corpus' in a:
        cmd += ['--corpus', a[a.index('--corpus') + 1]]
    audit = subprocess.run(cmd, capture_output=True, text=True)
    last = (audit.stdout.strip().splitlines() or ['no audit output'])[-1]
    if audit.returncode != 0 or 'RESULT: PASS' not in last:
        print('LITE VIEW REFUSED: the navigation does not pass the output audit (L-457).')
        print(last)
        sys.exit(1)
    text = open(path, encoding='utf-8').read()
    def grab(rx, default='[not found]'):
        m = re.search(rx, text, re.M)
        return m.group(1).strip() if m else default
    nav = grab(r'^NAVIGATOR:\s*(.+?)\s+PROTOCOL:')
    domain = grab(r'DOMAIN VERBATIM:\s*(.+)$')
    anchor = grab(r'ANCHOR (P\d+ \([^)]*\), v = \d+)')
    arms = re.findall(r'^\s+(Yang|Yin|4D|Antipode)\s+(P\d+)\s+(\S+)\s+v = (\d+)', text, re.M)
    m = re.search(r'┌─ THE ANSWER ─┐\s*(.*?)\s*└─+┘', text, re.S)
    answer = m.group(1).strip() if m else '[THE ANSWER not found]'
    sig = grab(r'^(CAS-YY.*)$', '')
    out = ['OMEGA42 LITE VIEW — rendered from an audited navigation (audit: PASS)',
           'Full record SHA-256: %s' % hashlib.sha256(open(path, 'rb').read()).hexdigest(),
           'Navigator: %s' % nav,
           'Your question: %s' % domain,
           'Position: %s' % anchor]
    out += ['  %s: %s %s, value %s' % x for x in arms]
    out += ['', answer, '', 'What this reading is worth to you is yours to judge.']
    if sig:
        out.append(sig)
    print('\n'.join(out))

if __name__ == '__main__':
    main()
