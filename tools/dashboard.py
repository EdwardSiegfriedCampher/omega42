#!/usr/bin/env python3
"""dashboard.py -- the record in numbers (Core L-495; Companion 51.11). A display, not an instrument (Core M283).

Computes, from the open record only, the figures the site's Record page shows and the newsletter's "record in
numbers" column uses. Every figure carries what it counts, what it does not count, its source, and -- where chance
can be stated exactly -- the count expected by chance beside it. Four rules are checked on every figure:

  * a count is named for what it is (domains navigated, meetings on the structure, architectures represented) and
    never as a count of validations, confirmations or support of Omega42 (Core L-490, Part 0.0.3 item 7);
  * the words are descriptive: no "trending", "popular", "important", "must-see", "recommended" (Core L-431);
  * nothing is phrased as guidance to the reader ("you should", "try asking"): the display never becomes a soft
    recommendation that erodes the Aperture (Core Part 7);
  * privacy: the privacy flags are counted, never listed by item or person; site traffic appears only as aggregate
    page loads read from a supplied file of daily totals (never cookies, never addresses, never the question), and
    otherwise as NOT COUNTED.

A figure that informs a decision, a threshold or a study is not a display: it becomes an instrument, with its
registry entry, role and pre-registered criterion, before it is used (Core Part 3.18).

Usage:
    python3 tools/dashboard.py [--traffic TRAFFIC.json]      # prints the figures as JSON
    python3 tools/dashboard.py --selftest
Standard library and the tools beside this file.
"""
import json, os, re, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import congruence as cg
import records as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BANNED = re.compile(r'\b(validat\w*|confirm\w*|corroborat\w*|support(s|ed|ing)? (for )?(the premise|omega ?42|Ω ?42)|'
                    r'trending|popular\w*|important|must-see|recommended|hot topic|you should|try asking)\b', re.I)


def fig(fid, label, value, counts, not_counts, source, expected=None):
    d = dict(id=fid, label=label, value=value, counts=counts, does_not_count=not_counts, source=source)
    if expected is not None: d['expected_by_chance'] = round(expected, 2)
    return d


def figures(traffic=None):
    reg = cg.load_register(); br = cg.base_rates()
    S = [cg.sig(d) for t, d in reg]
    n = len(S); pairs = n * (n - 1) // 2
    same = sum(1 for i in range(n) for j in range(i + 1, n) if S[i]['state'] == S[j]['state'])
    mir = sum(1 for i in range(n) for j in range(i + 1, n) if S[i]['state'] == cg.neg(S[j]['state']) and S[i]['state'] != (0, 0))
    links = sum(1 for a in S for b in S if a is not b and a['yang'] == b['anchor'])
    states = len({s['state'] for s in S})
    exp_states = 81 * (1 - (80 / 81) ** n)
    voices = Counter(s['voice'] for s in S)
    lib = R.library()
    navs = [i for i in lib if i['kind'] == 'navigation']
    routes = Counter(i.get('submission', 'manual') for i in navs)
    priv = Counter(i.get('privacy', 'PUBLIC') for i in navs)
    archs = sorted({re.split(r'[ (]', (i.get('navigator') or '').strip())[0].lower() for i in navs if i.get('navigator')} - {''})
    kinds = Counter(i['kind'] for i in lib)
    F = [
        fig('domains', 'Domains navigated in the Congruence Register', n, 'distinct domains struck, verbatim, in records/congruence/domains.txt',
            'validations of anything; repeated navigations of one domain count once', 'records/congruence/domains.txt'),
        fig('states', 'States of the 81 occupied by those domains', states, 'distinct states (r1, r2) mod 9 among the domains',
            'how often each state is occupied', 'canonical_reference.py on each domain', exp_states),
        fig('same_state', 'Pairs of domains on the same state', same, 'unordered pairs of distinct domains sharing a state',
            'what the meeting means, which is the Striker\'s to judge', 'tools/congruence.py', pairs * br['state']),
        fig('mirror', 'Pairs of domains on mirror states', mir, 'pairs twelve steps apart on one orbit', 'pairs on the still point',
            'tools/congruence.py', pairs * br['mirror']),
        fig('links', 'Links: one question resting where another stands', links, 'ordered pairs whose Yang arm is the other\'s anchor',
            'any causal or thematic relation between the questions', 'tools/congruence.py', n * (n - 1) * br['link']),
        fig('voices', 'Domains by voice', dict(sorted(voices.items())), 'domains per voice of the state', 'any ranking of the voices',
            'tools/congruence.py'),
        fig('navigations', 'Navigations in the open record', len(navs), 'accepted navigations, the founding corpus and the golden navigations',
            'navigations kept in commercial applications, or never submitted', 'tools/records.py library'),
        fig('routes', 'Navigations by route of submission', dict(sorted(routes.items())), 'manual, web-app and opt-in submissions',
            'who submitted them', 'tools/records.py library'),
        fig('privacy', 'Navigations by privacy flag', dict(sorted(priv.items())), 'how many readings are public, professional or personal',
            'which readings, or whose: the flags are counted, never listed', 'tools/records.py library'),
        fig('architectures', 'AI architectures represented', len(archs), 'distinct model families named in the Navigator identity of navigations',
            'how well any architecture performs: no figure here grades a model', 'tools/records.py library'),
        fig('kinds', 'Items in the record by kind', dict(sorted(kinds.items())), 'navigations, explorations, reviews, disclosures, research and other kinds',
            'their quality or worth', 'tools/records.py library'),
    ]
    if traffic:
        days = traffic.get('days', [])
        F.append(fig('page_loads', 'Page loads, last %d days' % len(days), sum(d.get('page_loads', 0) for d in days),
                     'aggregate page loads from the facility\'s request totals, per day', 'visitors or people (one person may load many pages); '
                     'cookies, addresses or questions, none of which is kept', traffic.get('source', 'supplied traffic totals')))
    else:
        F.append(fig('page_loads', 'Page loads', 'NOT COUNTED', 'nothing: no traffic totals were supplied', 'visitors, people or questions',
                     'PRIVACY.md'))
    return F


def problems(F):
    out = []
    for f in F:
        for k in ('label', 'counts', 'does_not_count', 'source'):
            if not f.get(k): out.append('%s: no %s' % (f['id'], k))
        text = ' '.join(str(f.get(k, '')) for k in ('label', 'counts'))
        if BANNED.search(text): out.append('%s: evaluative or court wording "%s"' % (f['id'], BANNED.search(text).group(0)))
    return out


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-66s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    F = figures()
    check('every figure states what it counts and what it does not', not problems(F))
    d = {f['id']: f for f in F}
    check('meetings carry the count expected by chance', all('expected_by_chance' in d[k] for k in ('same_state', 'mirror', 'links', 'states')))
    check('traffic is NOT COUNTED unless totals are supplied', d['page_loads']['value'] == 'NOT COUNTED')
    t = figures({'days': [{'date': '2026-10-15', 'page_loads': 40}, {'date': '2026-10-16', 'page_loads': 2}], 'source': 'test'})
    check('supplied totals are summed, and say they are not people', [f for f in t if f['id'] == 'page_loads'][0]['value'] == 42
          and 'not' not in [f for f in t if f['id'] == 'page_loads'][0]['counts'])
    check('a validation count is refused', problems([fig('x', '17 validations of the premise', 17, 'c', 'n', 's')]))
    check('evaluative and guiding words are refused', problems([fig('x', 'Trending: you should ask about time', 1, 'c', 'n', 's')]))
    check('privacy flags are counted, never listed', isinstance(d['privacy']['value'], dict) and all(isinstance(v, int) for v in d['privacy']['value'].values()))
    print('DASHBOARD SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    tr = json.load(open(a[a.index('--traffic') + 1], encoding='utf-8')) if '--traffic' in a else None
    F = figures(tr); p = problems(F)
    print(json.dumps(dict(figures=F, check='PASS' if not p else 'FAIL: ' + '; '.join(p)), indent=1, ensure_ascii=False))
    sys.exit(0 if not p else 1)
