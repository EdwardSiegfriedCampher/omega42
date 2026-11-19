#!/usr/bin/env python3
"""newsletter.py -- drafts the monthly newsletter from the open record (community/NEWSLETTER.md).

    python3 tools/newsletter.py --month 2026-10            # writes the draft to DIR (default community/newsletter/), prints the path
    python3 tools/newsletter.py --month 2026-10 --out DIR
    python3 tools/newsletter.py --eligible HANDLE          # is this handle eligible to receive it? (exit 0 if yes)
    python3 tools/newsletter.py --selftest
The newsletter goes only to registered contributors, to everyone who has submitted Omega42-generated content, and to
users of the commercial applications, who receive it whether or not they submit (Core L-495, Companion 51.3). The first
two are read from community/contributors.json; commercial accounts are held by the Company's account system and passed
to the provider directly. The editor adds the protocol revisions, the debate summary and the recognitions before sending.
Everything the newsletter reports stays public in the open record; the letter itself is what eligibility governs."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records as R

LABEL = {'navigation': 'Navigations', 'review': 'Reviews',
         'ape': 'Essays and explorations by AI Navigators (Applied Protocol Explorations, passed by APA, Core Part 9.5.5; CDT-C, each labelled with its model)',
         'prior-art': 'New prior-art disclosures', 'research': 'Research proposals',
         'commentary': 'Commentaries by verified domain experts (perspectives)',
         'result': 'Experimental results (each under its own investigation\'s question, never a status of \u03a942)'}


def draft(month):
    items = [i for i in R.library() if i['date'].startswith(month)]
    L = ['# Ω42 — %s' % month, '', 'The month in the open record.', '']
    navs = [i for i in items if i['kind'] == 'navigation']
    sub = {}
    for i in navs: sub[i.get('submission', 'manual')] = sub.get(i.get('submission', 'manual'), 0) + 1
    L += ['## The record this month', '',
          '- Navigations this month: %d (%s). A count of navigations, not of validations (Core L-490).' % (len(navs), ', '.join('%s %d' % kv for kv in sorted(sub.items())) or 'none'), '']
    try:
        import dashboard
        L += ['## The record in numbers', '']
        for f in dashboard.figures():
            v = f['value'] if not isinstance(f['value'], dict) else ', '.join('%s %s' % kv for kv in f['value'].items())
            L.append('- %s: %s%s. Counts %s; does not count %s.' % (f['label'], v, (' (expected by chance %s)' % f['expected_by_chance']) if 'expected_by_chance' in f else '', f['counts'], f['does_not_count']))
        L += ['', '## Null results this month', '', '_Editor: entries added to the Negative Result Registry, read beside the meetings above._', '',
              '## First exercises and registry movements', '', '_Editor: instruments run on real material for the first time; status changes at the revision that set them._', '',
              '## Corrections', '', '_Editor: corrected navigations, each a new navigation citing the original, with stable links._', '']
    except Exception as e:
        L += ['_The record in numbers could not be computed: %s_' % e, '']
    pairs = []
    for a in range(len(navs)):
        for b in range(a + 1, len(navs)):
            ca, cb = navs[a].get('coordinate'), navs[b].get('coordinate')
            if ca and cb and ca.get('state') and ca.get('state') == cb.get('state') and ca.get('n') != cb.get('n'):
                pairs.append('%s and %s share the state %s' % (navs[a]['id'], navs[b]['id'], tuple(ca['state'])))
    L += ['## New meetings in the Congruence Register', ''] + (['- ' + x for x in pairs] or ['- None among this month\'s navigations; the full Register is on the site.']) + ['']
    for kind, label in LABEL.items():
        ks = [i for i in items if i['kind'] == kind]
        L.append('## %s (%d)' % (label, len(ks))); L.append('')
        for i in ks:
            c = i.get('coordinate')
            L.append('- **%s** — %s%s · by %s' % (i['id'], i['title'], (' · P%d %s' % (c['anchor'], c['name'])) if c else '', i['by']))
        if not ks: L.append('- None this month.')
        L.append('')
    L += ['## Protocol revisions', '', '_Editor: what changed in the two documents this month and why (paired release, Core Builder Rule 15), or "none"._', '',
          '## The debate of the month', '', '_Editor: summarise one Discussions → Debate thread._', '',
          '## Recognitions', '', '_Editor: New domain of the month, Review of the month, Disclosure of the month, with reasons (community/RECOGNITION.md)._', '',
          '## Leading contributors', '']
    for c in R.contributors()[:10]:
        L.append('- %s — %d points' % (c['name'], c['points']))
    L += ['', '---', 'You receive this because you are a registered contributor, have submitted Ω42-generated content, or use a commercial Ω42 application, and you chose to receive it. Unsubscribe from any issue. Everything reported here is in the open record on the site. Every reading reported here was written by an AI system: it can contain errors, and its training shapes its wording and may shape its reading; a reading is a generated artefact, not a measured fact (Core L-506).']
    return '\n'.join(L) + '\n'


def eligible(handle, contributors=None, commercial=()):
    """Registered contributors and everyone with an accepted contribution (community/contributors.json), and commercial
    account holders, whether or not they submit."""
    import json
    if handle in commercial: return True
    c = contributors if contributors is not None else json.load(open(os.path.join(R.ROOT, 'community', 'contributors.json'), encoding='utf-8'))
    e = next((x for x in c if x.get('handle') == handle), None)
    return bool(e and (e.get('registered') or e.get('contributions')))


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-66s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    c = [dict(handle='ada', contributions=['NAV-2026-0001']), dict(handle='bea', registered='2026-10-16', contributions=[]),
         dict(handle='cy', contributions=[])]
    check('a submitter is eligible', eligible('ada', c))
    check('a registered contributor with no submission is eligible', eligible('bea', c))
    check('a commercial user is eligible without submitting', eligible('dan', c, commercial={'dan'}))
    check('anyone else is not', not eligible('cy', c) and not eligible('eve', c))
    d = draft('2026-10')
    check('the draft states who receives it and that its content stays public', 'registered contributor' in d and 'open record' in d)
    check('the draft carries the record counts and the Register meetings', '## The record this month' in d and '## New meetings in the Congruence Register' in d)
    print('NEWSLETTER SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if len(a) == 2 and a[0] == '--eligible':
        e = eligible(a[1]); print('ELIGIBLE' if e else 'NOT ELIGIBLE'); sys.exit(0 if e else 1)
    if len(a) < 2 or a[0] != '--month': print(__doc__); sys.exit(0)
    out = a[a.index('--out') + 1] if '--out' in a else os.path.join(R.ROOT, 'community', 'newsletter')
    os.makedirs(out, exist_ok=True)
    p = os.path.join(out, a[1] + '.md'); open(p, 'w', encoding='utf-8').write(draft(a[1])); print(p)
