#!/usr/bin/env python3
"""physics_map.py -- the Physical Mapping Register (Core Part 0.0.5 Rule 37; Companion Part 226; F219; APE-481).

Every application of Omega42 to a physical system is one entry B = (P, M, Phi, I, R, E):
  P  the physical system, as it exists in the laboratory or in nature
  M  its established mathematical model
  Phi the Omega42 representation and the map between it and M
  I  what the map preserves, and what it leaves aside
  R  the results, each in the register of Core Part 0.0.10, each with its class
  E  the evidence: the recompute commands, the replication returns and the measurements of Core Appendix S
The seven classes of a result: established mathematical result; independently reproduced result; new structural
correspondence; new computational result; candidate theorem; physical prediction; experimentally supported result.

    python3 tools/physics_map.py --check   every entry complete, every result in the register, every class one of the seven
    python3 tools/physics_map.py --list    the register, one line an entry
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(REPO, 'records', 'physics', 'mappings.json')
MATH = os.path.join(REPO, 'records', 'math', 'results.json')
CLASSES = ('established mathematical result', 'independently reproduced result', 'new structural correspondence', 'new computational result',
           'candidate theorem', 'physical prediction', 'experimentally supported result')
FIELDS = ('id', 'system', 'model', 'representation', 'map', 'preserves', 'leaves_aside', 'results', 'evidence')   # map: its domain and codomain (Rule 38)
def problems(d, ids):
    P = []; seen = set()
    for e in d.get('entries', []):
        tag = e.get('id', '?')
        if tag in seen: P.append('%s twice' % tag)
        seen.add(tag)
        for f in FIELDS:
            if not e.get(f): P.append('%s: %s missing' % (tag, f))
        for r in e.get('results', []):
            if r.get('mf') not in ids: P.append('%s: %s not in the mathematical register' % (tag, r.get('mf')))
            if r.get('class') not in CLASSES: P.append('%s: %s class %r' % (tag, r.get('mf'), r.get('class')))
        ev = e.get('evidence', {})
        if not ev.get('recompute'): P.append('%s: no recompute command' % tag)
    return P
def selftest(ids):
    good = {'entries': [{'id': 'PM-001', 'system': 's', 'model': 'm', 'representation': 'r', 'map': 'domain d; codomain c', 'preserves': 'p', 'leaves_aside': 'l',
                         'results': [{'mf': 'MF-01', 'class': CLASSES[0]}], 'evidence': {'recompute': 'c'}}]}
    bad = json.loads(json.dumps(good)); bad['entries'][0]['results'][0]['class'] = 'a discovery'
    miss = json.loads(json.dumps(good)); del miss['entries'][0]['leaves_aside']
    return problems(good, {'MF-01'}) == [] and problems(bad, {'MF-01'}) != [] and problems(miss, {'MF-01'}) != []
if __name__ == '__main__':
    ids = {r['id'] for r in json.load(open(MATH, encoding='utf-8'))['results']}
    a = sys.argv[1:]
    d = json.load(open(REG, encoding='utf-8'))
    if a == ['--check']:
        P = problems(d, ids); st = selftest(ids)
        print('PHYSICAL MAPPING REGISTER: %d entries, %d results | selftest %s | %s' % (len(d['entries']), sum(len(e['results']) for e in d['entries']), 'PASS' if st else 'FAIL', 'PASS' if not P and st else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P or not st else 0)
    if a == ['--list']:
        for e in d['entries']:
            print('%s  %s | %s | results %s' % (e['id'], e['system'], e['model'], ', '.join('%s (%s)' % (r['mf'], r['class']) for r in e['results'])))
        sys.exit(0)
    print(__doc__); sys.exit(2)
