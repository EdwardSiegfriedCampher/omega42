#!/usr/bin/env python3
"""math_register.py -- the register of the extended mathematical foundations (Core Part 0.0.8; records/math/results.json).

Each result names the tool and the selftest line that checks it; this runs each tool's selftest once and confirms that
every named line passes, and that every result states its completion and what does not follow.
    python3 tools/math_register.py
Standard library only.
"""
import json, os, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(REPO, 'records', 'math', 'results.json'), encoding='utf-8'))
out, P = {}, []
for r in d['results']:
    if r['tool'] not in out:
        out[r['tool']] = subprocess.run([sys.executable, os.path.join(REPO, r['tool']), '--selftest'], capture_output=True, text=True).stdout
    ok = any(l.startswith(r['check']) and l.rstrip().endswith('PASS') for l in out[r['tool']].split('\n'))
    for f in ('domain', 'does_not_follow', 'derivation'):
        if not r.get(f): P.append('%s: no %s' % (r['id'], f))
    print('  %s %-11s %-30s %s' % (r['id'], 'PASS' if ok else 'FAIL', r['domain'][:30], r['statement'][:70]))
    if not ok: P.append('%s: its check did not pass' % r['id'])
print('MATHEMATICAL FOUNDATIONS REGISTER (Core Part 0.0.8): %d results | %s' % (len(d['results']), 'PASS' if not P else 'FAIL (%d)' % len(P)))
[print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
