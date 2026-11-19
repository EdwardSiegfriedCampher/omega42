#!/usr/bin/env python3
"""records.py -- reads the open record of the Ω42 portal: accepted submissions, the corpus, the golden navigations,
the Prior Art Ledger, contributors and professionals. Shared by site_build.py, newsletter.py and curator.py."""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import canonical_reference as cr

KIND_DIRS = {'navigations': 'navigation', 'ape': 'ape', 'reviews': 'review', 'prior-art': 'prior-art', 'research': 'research',
             'commentaries': 'commentary', 'results': 'result'}


def front_matter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m: return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        k, _, v = line.partition(': ')
        try: meta[k] = json.loads(v)
        except Exception: meta[k] = v
    return meta, text[m.end():]


def coordinate(domain):
    x = cr.navigate(domain); a, r1, r2 = cr.determine_anchor(x['n1'], x['n2'], x['n3'])[:3]
    return dict(anchor=a, name=cr.POSITION_NAMES[a], n=[x['n1'], x['n2'], x['n3']], state=[r1 % 9, r2 % 9])


def nav_meta_from_text(t):
    g = lambda rx: (re.search(rx, t).group(1).strip() if re.search(rx, t) else '')
    return dict(domain=g(r'DOMAIN VERBATIM:\s*(.+)'), navigator=g(r'NAVIGATOR:\s*([^\n*|]+?)(?:\s+PROTOCOL:|\s*\*|\n)'))


def library():
    """Every item of the open record, newest first."""
    items = []
    sub = os.path.join(ROOT, 'submissions')
    for d, kind in KIND_DIRS.items():
        p = os.path.join(sub, d)
        if not os.path.isdir(p): continue
        for f in sorted(os.listdir(p)):
            fp = os.path.join(p, f)
            if f.endswith('.json') and kind == 'navigation':
                m = json.load(open(fp, encoding='utf-8'))
                if m.get('record_type') == 'redacted-domain':      # L-495, Companion 51.1: hash and computed values, no text
                    items.append(dict(id=m['id'], kind=kind, title='[Personal reading -- redacted]', by=m.get('submitted_by', ''),
                                      navigator=m.get('navigator', ''), area=m.get('area', 'open'), date=m.get('accepted_utc', '')[:10],
                                      path='records/congruence/redacted.jsonl#' + m['id'], sha256='', submission=m.get('submission', 'manual'), privacy='PERSONAL',
                                      coordinate=dict(anchor=m['anchor'], name=cr.POSITION_NAMES[m['anchor']], n=m['n'], state=m['state'])))
                    continue
                items.append(dict(id=m['id'], kind=kind, title=m.get('domain', ''), submission=m.get('submission', 'manual'), by=m.get('submitted_by', ''), navigator=m.get('navigator', ''),
                                  area=m.get('area', 'open'), date=m.get('accepted_utc', '')[:10], path='submissions/%s/%s.txt' % (d, m['id']),
                                  sha256=m.get('sha256', ''), coordinate=coordinate(m['domain']) if m.get('domain') else None))
            elif f.endswith('.md'):
                meta, body = front_matter(open(fp, encoding='utf-8').read())
                t = re.search(r'^# (.+)$', body, re.M)
                items.append(dict(id=meta.get('id', f[:-3]), kind=kind, title=t.group(1) if t else f, by=meta.get('submitted_by', ''),
                                  area=meta.get('area', 'open'), date=str(meta.get('accepted_utc', ''))[:10], path='submissions/%s/%s' % (d, f)))
    for f in sorted(os.listdir(os.path.join(ROOT, 'examples', 'corpus'))):
        if not f.endswith('.txt'): continue
        t = open(os.path.join(ROOT, 'examples', 'corpus', f), encoding='utf-8', errors='replace').read()
        m = nav_meta_from_text(t)
        items.append(dict(id='CORPUS-' + f[:-4], kind='navigation', title=m['domain'], by='founding corpus', navigator=m['navigator'],
                          area='open', date='2026-10-08', path='examples/corpus/' + f, coordinate=coordinate(m['domain']) if m['domain'] else None))
    gn = os.path.join(ROOT, 'records', 'golden_navigations')
    for f, title in (('01_navigations.txt', 'Golden ratio: the matrix of φ, the spectrum of the three loops, exact physical realisations'),
                     ('03_further_navigations.txt', 'Golden ratio: nine further questions')):
        if os.path.exists(os.path.join(gn, f)):
            items.append(dict(id='GOLD-' + f[:2], kind='navigation', title=title, by='ESC (Originator)', navigator='claude-opus-5-5 (Anthropic)',
                              area='mathematics', date='2026-10-14', path='records/golden_navigations/' + f))
    items.sort(key=lambda x: (x['date'], x['id']), reverse=True)
    return items


def ledger():
    p = os.path.join(ROOT, 'records', 'prior_art', 'ledger.jsonl')
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()] if os.path.exists(p) else []


def contributors():
    return json.load(open(os.path.join(ROOT, 'community', 'contributors.json'), encoding='utf-8'))


def professionals():
    return json.load(open(os.path.join(ROOT, 'community', 'professionals.json'), encoding='utf-8'))


def areas():
    return json.load(open(os.path.join(ROOT, 'research', 'areas.json'), encoding='utf-8'))
