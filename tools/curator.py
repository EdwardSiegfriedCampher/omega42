#!/usr/bin/env python3
"""curator.py -- the deterministic baseline of the curator (agents/curator/SPEC.md).

Sorts every item of the open record into a research database: area (declared, else by keyword, else "open"),
duplicates (same text, or same domain), the coordinate and state of each navigation, its COHERENCE line (M310),
and links between items that share a state, mirror one, or rest where another stands; a navigation on
consciousness, mind or experience is filed with the CT-42 studies its state would enter (Core L-498, M315). The AI curator agent
refines this output; it never replaces the computed fields.

    python3 tools/curator.py            # writes records/curation/index.json and records/curation/report.md
    python3 tools/curator.py --selftest
"""
import hashlib, json, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records as R
import congruence as cg
import aperture_audit as ap
import consciousness as cs

OUT = os.path.join(R.ROOT, 'records', 'curation')


def classify(text, areas):
    t = text.lower(); best, score = 'open', 0
    for a in areas:
        s = sum(t.count(k) for k in a['keywords'])
        if s > score: best, score = a['slug'], s
    return best


def coherence_line(path):
    p = subprocess.run([sys.executable, os.path.join(R.ROOT, 'tools', 'congruence.py'), '--check', path], capture_output=True, text=True)
    m = re.search(r'^COHERENCE: (.+)$', p.stdout, re.M)
    return m.group(1) if m else 'NOT COMPUTED'


def build():
    areas = R.areas(); items = R.library()
    by_text, by_dom = {}, {}
    for it in items:
        fp = os.path.join(R.ROOT, it['path'])
        text = open(fp, encoding='utf-8', errors='replace').read() if os.path.exists(fp) else ''
        it['text_sha256'] = hashlib.sha256(text.encode()).hexdigest()
        if it['area'] == 'open':
            basis = ap.the_answer(text) if '\u250c\u2500 THE ANSWER' in text else text[:4000]
            it['area'] = classify(it['title'] + '\n' + basis, areas); it['area_source'] = 'keyword'
        else:
            it['area_source'] = 'declared'
        by_text.setdefault(it['text_sha256'], []).append(it['id'])
        if it['kind'] == 'navigation' and it.get('coordinate') and it['title']:
            s = cg.sig(it['title']); it['state'] = list(s['state']); it['voice'] = s['voice']; it['yang'] = s['yang']
            by_dom.setdefault(s['sha'], []).append(it['id'])
            it['coherence'] = coherence_line(fp)
            if cs.concerns(it['title']): it['ct_studies'] = cs.studies(tuple(s['state']))   # CT-42 (Core L-498, M315)
    navs = [i for i in items if 'state' in i]
    for i in navs:
        rel = []
        for j in navs:
            if i is j: continue
            if j['state'] == i['state']: rel.append([j['id'], 'same state'])
            elif tuple(j['state']) == cg.neg(tuple(i['state'])) and tuple(i['state']) != (0, 0): rel.append([j['id'], 'mirror'])
            if i['yang'] == j['coordinate']['anchor']: rel.append([j['id'], 'rests where it stands'])
        i['related'] = rel
    dups = [v for v in by_text.values() if len(v) > 1]
    same_domain = [v for v in by_dom.values() if len(v) > 1]
    return dict(items=items, duplicates=dups, same_domain=same_domain)


def report(db):
    L = ['# Curation report', '', 'Built by tools/curator.py (the deterministic baseline). %d items.' % len(db['items']), '']
    from collections import Counter
    c = Counter(i['area'] for i in db['items'])
    L += ['## By area', ''] + ['- %s: %d' % (k, v) for k, v in sorted(c.items())] + ['']
    L += ['## Same domain, several navigations (SR-CAS candidates)', ''] + (['- ' + ', '.join(v) for v in db['same_domain']] or ['- none']) + ['']
    L += ['## Identical texts', ''] + (['- ' + ', '.join(v) for v in db['duplicates']] or ['- none']) + ['']
    L += ['## Coherence lines with a FAIL or REVIEW', '']
    bad = [i for i in db['items'] if 'FAIL' in i.get('coherence', '') or 'REVIEW' in i.get('coherence', '')]
    L += (['- %s: %s' % (i['id'], i['coherence']) for i in bad] or ['- none'])
    return '\n'.join(L) + '\n'


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-58s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    areas = R.areas()
    check('keyword classification: a question about the Collatz map -> mathematics', classify('The Fibonacci recurrence modulo 9 and the Pisano period', areas) == 'mathematics')
    check('keyword classification: nothing matched -> open', classify('zzz', areas) == 'open')
    db = build()
    check('the corpus navigations of one domain are grouped for SR-CAS', any(len(v) >= 4 for v in db['same_domain']))
    check('every navigation with a domain carries a state and a coherence line', all('coherence' in i for i in db['items'] if 'state' in i))
    check('a navigation on consciousness is filed with its CT-42 studies', all('ct_studies' in i for i in db['items'] if 'state' in i and cs.concerns(i['title'])))
    print('CURATOR SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    db = build(); os.makedirs(OUT, exist_ok=True)
    json.dump(db, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    open(os.path.join(OUT, 'report.md'), 'w', encoding='utf-8').write(report(db))
    print('records/curation/index.json: %d items' % len(db['items']))
