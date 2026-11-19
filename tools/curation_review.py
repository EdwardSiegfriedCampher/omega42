#!/usr/bin/env python3
"""curation_review.py -- the curator's refining layer (agents/curator/SPEC.md, "What the agent adds", items 1 and 3).

Reads the deterministic baseline (records/curation/index.json, built by tools/curator.py) and the frozen texts, and
writes PROPOSALS beside it, never over it:

  1. AREA REVIEW  every item whose declared area is not one of the registered areas (records/curation areas, via
                  records.areas()) gets a proposed registered area, with a one-line reason: an alias where the declared
                  slug names a registered area, else the keyword score of the title (weight 5) and the text;
  2. CHAMBER      the architecture that produced the item, read from its submitted_by line;
  3. DISPOSITION  for an APE, what the protocol did with it, read from the labels of the receiving Navigator's notes
                  (Adopted, Corrected, Refined, Holding, Not taken, Already in place, Form, ...);
  4. THREADS      items that share a domain (the baseline's same-domain groups), a Discovery number (F123) or a title
                  close enough (Jaccard >= 0.5 on content words).

Outputs records/curation/agent/catalogue.json and records/curation/agent/catalogue.md. The baseline's computed fields
are copied, never changed. A person accepts or rejects each proposal (SPEC: "It never accepts, rejects or moderates").

    python3 tools/curation_review.py
    python3 tools/curation_review.py --selftest
Standard library only.
"""
import collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records as R

INDEX = os.path.join(ROOT, 'records', 'curation', 'index.json')
OUT = os.path.join(ROOT, 'records', 'curation', 'agent')
NAVIGATOR = 'claude-opus-5-5 (Anthropic; serving model may differ), acting as curator under agents/curator/SPEC.md'

ALIASES = {  # declared slug -> registered area, where the slug names one
    'consciousness': 'consciousness-and-mind', 'philosophy-of-mind': 'consciousness-and-mind',
    'governance': 'law-and-governance', 'language': 'language-and-extraction', 'review': 'cross-architecture',
    'mathematics': 'mathematics', 'physics': 'physics', 'philosophy': 'philosophy',
    'arts-music-and-literature': 'arts-music-and-literature', 'personal-practice': 'personal-practice'}
CHAMBERS = [('Claude', r'claude|anthropic'), ('ChatGPT', r'chatgpt|openai|\bgpt'), ('Grok', r'grok|xai'),
            ('Qwen', r'qwen|alibaba'), ('Gemini', r'gemini|google'), ('DeepSeek', r'deepseek'), ('Mistral', r'mistral'),
            ('Llama', r'llama|meta\b'), ('Copilot', r'copilot|microsoft'), ('Kimi', r'kimi|moonshot'),
            ('unidentified', r'unidentified|unnamed|unsigned|web interface')]
STOP = set('the of and a an in on to for with by from its is as at omega42 ω42 into how what'.split())


def chamber(by):
    b = (by or '').lower()
    return next((name for name, rx in CHAMBERS if re.search(rx, b)), 'other')


def text_of(it):
    p = os.path.join(ROOT, it['path']) if it.get('path') else None
    try:
        return open(p, encoding='utf-8', errors='replace').read() if p and os.path.isfile(p) else ''
    except OSError:
        return ''


def _count(text, k):
    k = k.strip()
    return len(re.findall(r'(?<![a-z])' + re.escape(k) + r'(?![a-z])', text))


IDF = {}


def score(title, body, area):
    """Whole-word counts (a substring count would find 'time' in 'spacetime' and 'art' in 'part'), each keyword
    weighted by its rarity across the record (inverse document frequency), so a word every text uses
    ('navigator', 'decision') does not decide an area."""
    t, b = title.lower(), body.lower()[:6000]
    return round(sum((5 * _count(t, k) + _count(b, k)) * IDF.get(k, 1.0) for k in area['keywords']), 1)


def propose_area(it, body, areas, slugs):
    d = it.get('area', 'open')
    if d in slugs:
        return d, 'declared area is registered'
    if d in ALIASES and ALIASES[d] in slugs:
        return ALIASES[d], f'declared "{d}" names the registered area {ALIASES[d]}'
    sc = sorted(((score(it.get('title', ''), body, a), a['slug']) for a in areas if a['keywords']), reverse=True)
    if sc and sc[0][0] > 0:
        top, second = sc[0], sc[1] if len(sc) > 1 else (0, '')
        conf = 'high' if top[0] >= 2 * max(second[0], 0.1) else 'low'
        return top[1], f'declared "{d}" is not registered; keywords score {top[0]} for {top[1]} (next {second[1]}, {second[0]}); confidence {conf}'
    return 'open', f'declared "{d}" is not registered and no area keyword occurs'


def disposition(body):
    head = body.split('\n---\n', 2)
    notes = re.findall(r'^- ([A-Z][A-Za-z ]{2,40}?)(?: as [^:]*)?:', head[1] if len(head) > 1 else body[:4000], re.M)
    kinds = []
    for n in notes:
        k = n.split(' and ')[0].strip().lower()
        k = {'recomputed': 'adopted', 'entered': 'adopted', 'taken': 'adopted', 'made operational': 'adopted'}.get(k, k)
        if k not in kinds: kinds.append(k)
    return kinds or ['none recorded']


def words(t):
    return {w for w in re.findall(r'[a-zα-ωΩ0-9]+', t.lower()) if w not in STOP and len(w) > 2}


def build():
    base = json.load(open(INDEX))
    areas = R.areas(); slugs = {a['slug'] for a in areas}
    items = base['items']; rows = []
    import math
    texts = [text_of(it).lower()[:6000] for it in items]
    for a in areas:
        for k in a['keywords']:
            df = sum(1 for t in texts if _count(t, k))
            IDF[k] = math.log((1 + len(texts)) / (1 + df))
    for it in items:
        body = text_of(it)
        area, why = propose_area(it, body, areas, slugs)
        rows.append(dict(id=it['id'], kind=it['kind'], title=it.get('title', ''), date=it.get('date', ''), by=it.get('by', ''),
                         chamber=chamber(it.get('by', '')), declared_area=it.get('area', ''), proposed_area=area, reason=why,
                         changed=area != it.get('area', ''), disposition=disposition(body) if it['kind'] == 'ape' else [],
                         discoveries=sorted(set(re.findall(r'\bF(\d{2,3})\b', it.get('title', '') + ' ' + body[:3000])), key=int)[:6],
                         path=it.get('path', ''), text_sha256=it.get('text_sha256', '')))
    # threads
    threads = [dict(kind='same domain', members=g) for g in base.get('same_domain', [])]
    byF = collections.defaultdict(list)
    for r in rows:
        if r['discoveries']: byF['F' + r['discoveries'][0]].append(r['id'])
    threads += [dict(kind=f'discovery {f}', members=m) for f, m in sorted(byF.items()) if len(m) > 1]
    W = {r['id']: words(r['title']) for r in rows}
    seen = set()
    for i, a in enumerate(rows):
        grp = [a['id']] + [b['id'] for b in rows[i + 1:] if W[a['id']] and len(W[a['id']] & W[b['id']]) / len(W[a['id']] | W[b['id']]) >= 0.5]
        if len(grp) > 1 and a['id'] not in seen:
            seen.update(grp); threads.append(dict(kind='close titles', members=grp))
    cand = [r['id'] for r in rows if re.search(r'construct|primordial|workbook', r['title'], re.I)]
    new_areas = [dict(slug='construct-and-workbook', reason='work gathers on the Construct, Construct X and the PRIMORDIAL FRACTURE workbook, '
                      'which no registered area names', members=cand)] if len(cand) >= 5 else []
    summary = dict(items=len(rows), changed=sum(r['changed'] for r in rows),
                   high_confidence=sum('confidence high' in r['reason'] for r in rows),
                   low_confidence=sum('confidence low' in r['reason'] for r in rows),
                   spot_check='the Navigator accepted about 8 of 16 sampled keyword proposals (19 Nov 2026); proposals are a first sort for a person to decide',
                   by_area=collections.Counter(r['proposed_area'] for r in rows).most_common(),
                   by_chamber=collections.Counter(r['chamber'] for r in rows).most_common(),
                   by_disposition=collections.Counter(d for r in rows for d in r['disposition']).most_common(),
                   threads=len(threads), proposed_new_areas=[(a['slug'], len(a['members'])) for a in new_areas])
    return dict(_about='Proposals of the curator (agents/curator/SPEC.md). The baseline (records/curation/index.json) is not changed; '
                       'a person accepts or rejects each proposal.', navigator=NAVIGATOR, summary=summary, items=rows, threads=threads,
                proposed_new_areas=new_areas)


def markdown(cat):
    s = cat['summary']; L = [f"# Curation catalogue (proposals)", "",
         f"Prepared by {cat['navigator']}. The computed baseline is unchanged; every proposed area below awaits a person's decision.", "",
         f"{s['items']} items; {s['changed']} proposed area changes ({s['high_confidence']} high confidence, {s['low_confidence']} low); {s['threads']} threads.",
         "", f"Spot check: {s['spot_check']}.", "", "## By proposed area", "",
         "| Area | Items |", "|---|---|"] + [f"| {a} | {n} |" for a, n in s['by_area']] + ["", "## By chamber (contributing architecture)", "",
         "| Chamber | Items |", "|---|---|"] + [f"| {a} | {n} |" for a, n in s['by_chamber']] + ["", "## What the protocol did (APE notes)", "",
         "| Disposition | APEs |", "|---|---|"] + [f"| {a} | {n} |" for a, n in s['by_disposition'][:14]] + ["", "## Items, by area then newest first", ""]
    order = sorted(cat['items'], key=lambda r: (r['proposed_area'], -int(re.sub(r'\D', '', r['id']) or 0)))
    cur = None
    for r in order:
        if r['proposed_area'] != cur:
            cur = r['proposed_area']; L += ["", f"### {cur}", "", "| Item | Title | Chamber | Disposition | Proposal |", "|---|---|---|---|---|"]
        prop = 'kept' if not r['changed'] else f"from {r['declared_area']}" + (' (low confidence)' if 'confidence low' in r['reason'] else '')
        L.append(f"| {r['id']} | {r['title'][:90].replace('|', '/')} | {r['chamber']} | {', '.join(r['disposition'][:3])} | {prop} |")
    for a in cat.get('proposed_new_areas', []):
        L += ["", f"## Proposed new area: {a['slug']} (for the Committee)", "", a['reason'] + '.', "", ', '.join(a['members'])]
    L += ["", "## Threads", ""] + [f"- {t['kind']}: {', '.join(t['members'][:12])}{' …' if len(t['members']) > 12 else ''}" for t in cat['threads']]
    return "\n".join(L) + "\n"


def selftest():
    areas = [dict(slug='mathematics', keywords=['orbit', 'modular']), dict(slug='physics', keywords=['quantum'])]
    slugs = {a['slug'] for a in areas}
    assert propose_area(dict(area='mathematics', title=''), '', areas, slugs)[0] == 'mathematics'
    assert propose_area(dict(area='protocol', title='A quantum walk'), '', areas, slugs)[0] == 'physics'
    assert propose_area(dict(area='protocol', title='Nothing here'), '', areas, slugs)[0] == 'open'
    assert score('spacetime and its parts', '', dict(keywords=['time', 'art'])) == 0
    IDF.clear()
    assert chamber('Grok (xAI) for ESC') == 'Grok' and chamber('ChatGPT (OpenAI), relayed') == 'ChatGPT'
    assert disposition('x\n---\nFrozen\n\n- Adopted: a\n- Holding: b\n- Corrected: c\n---\nbody')[:3] == ['adopted', 'holding', 'corrected']
    print('curation_review selftest: PASS')


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        selftest(); sys.exit()
    cat = build(); os.makedirs(OUT, exist_ok=True)
    json.dump(cat, open(os.path.join(OUT, 'catalogue.json'), 'w'), indent=1, ensure_ascii=False)
    open(os.path.join(OUT, 'catalogue.md'), 'w').write(markdown(cat))
    print(f"catalogue: {cat['summary']['items']} items, {cat['summary']['changed']} proposed area changes, {cat['summary']['threads']} threads")
