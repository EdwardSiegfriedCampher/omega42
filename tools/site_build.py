#!/usr/bin/env python3
"""site_build.py -- builds the Ω42 portal (GitHub Pages) from site/ and the open record.

    python3 tools/site_build.py --out _site [--repo OWNER/REPO] [--branch BRANCH]
    python3 tools/site_build.py --selftest

Pages in site/pages/ are wrapped in site/layout.html; the record is published as JSON under api/; the protocol
documents are copied with plain-text renderings and hashes; llms.txt, robots.txt, sitemap.xml and feed.xml are
written. Standard library only."""
import datetime, hashlib, html, json, os, re, shutil, sys, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import records as R
import congruence as cg

SITE = os.path.join(ROOT, 'site')
# Six destinations, each a group with its own pages (the first page of a group is where its heading leads).
NAV = [('Discoveries', [('bulletin', 'The Discovery Bulletin'), ('expert-desk', 'Expert Exploration Desk'), ('vision', 'The Omega42 paper')]),
       ('Explore', [('questions', 'World of Questions'), ('integrity', 'Information Integrity'), ('companion', 'Companion Explorer'), ('strike', 'Ask a question'), ('explore', 'How Omega42 works'), ('construct-x', 'Construct X laboratory'), ('speculate', 'Speculative Foundations')]),
       ('FAQ', [('faq', 'Frequently asked questions')]),
       ('Protocol', [('protocol', 'Core and Companion'), ('for-ai', 'For AI systems'), ('apps', 'Free and commercial editions')]),
       ('Research', [('research', 'Research frontiers'), ('construct-x', 'Construct X laboratory'), ('speculate', 'Speculative Foundations')]),
       ('Library', [('library', 'Discoveries and explorations'), ('catalogue', 'Catalogue'), ('prior-art', 'Prior art and inventions'), ('history', 'History of releases'), ('record', 'The record')]),
       ('Community', [('community', 'Join the community'), ('forum', 'Forum'), ('submit', 'Bring your ideas')]),
       ('Governance', [('governance', 'Governance')])]


def nav_html(current):
    """The grouped main navigation; the group holding the current page is marked."""
    out = []
    for head, items in NAV:
        here = any(k == current for k, _ in items)
        links = ''.join('<a href="%s.html"%s>%s</a>' % (k, ' aria-current="page"' if k == current else '', t) for k, t in items)
        menu = '<div class="menu">%s</div>' % links if len(items) > 1 else ''
        out.append('<div class="grp%s"><a class="head" href="%s.html">%s</a>%s</div>' % (' here' if here else '', items[0][0], head, menu))
    return ''.join(out)


LEVELS = [(75, 'Fellow'), (30, 'Cartographer'), (10, 'Navigator-Partner'), (1, 'Striker'), (0, '—')]


def sha_file(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def docx_text(p):
    x = zipfile.ZipFile(p).read('word/document.xml').decode('utf-8')
    paras = re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>|<w:p/>', x, re.S)
    return '\n'.join(html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', q, re.S))) for q in paras) + '\n'


def register_json():
    rows = cg.load_register(); br = cg.base_rates()
    S = []
    for tag, d in rows:
        s = cg.sig(d)
        short = d.split(':')[0] if len(d) > 140 and ':' in d[:120] else (d if len(d) <= 140 else d[:137] + '…')
        S.append(dict(tag=tag, text=short, anchor=s['anchor'], name=R.cr.POSITION_NAMES[s['anchor']],
                      state=list(s['state']), voice=s['voice'], yang=s['yang']))
    lab = lambda e: '%s — %s' % (e['tag'], e['text'] if len(e['text']) < 70 else e['text'][:67] + '…')
    same = [[lab(a), lab(b)] for i, a in enumerate(S) for b in S[i + 1:] if a['state'] == b['state']]
    mir = [[lab(a), lab(b)] for i, a in enumerate(S) for b in S[i + 1:]
           if tuple(a['state']) == cg.neg(tuple(b['state'])) and tuple(a['state']) != (0, 0)]
    links = [[a['tag'], b['tag']] for a in S for b in S if a is not b and a['yang'] == b['anchor']]
    n = len(S); pairs = n * (n - 1) // 2
    return dict(domains=S, same_state=same, mirror=mir, links=links,
                expected=dict(same_state=pairs * br['state'], mirror=pairs * br['mirror'], links=n * (n - 1) * br['link']))


def level(points):
    return next(name for lim, name in LEVELS if points >= lim)


def build(out, repo):
    cfg = json.load(open(os.path.join(SITE, 'config.json'), encoding='utf-8'))
    repo = repo or cfg['repo']
    owner, name = repo.split('/', 1)
    site_url = cfg.get('site_url') or 'https://%s.github.io/%s/' % (owner.lower(), name)
    if os.path.exists(out): shutil.rmtree(out)
    os.makedirs(os.path.join(out, 'api')); os.makedirs(os.path.join(out, 'protocol')); os.makedirs(os.path.join(out, 'py'))
    shutil.copytree(os.path.join(SITE, 'assets'), os.path.join(out, 'assets'))
    shutil.copy(os.path.join(ROOT, 'scripts', 'canonical_reference.py'), os.path.join(out, 'py'))
    shutil.copy(os.path.join(SITE, 'py', 'strike.py'), os.path.join(out, 'py'))
    shutil.copy(os.path.join(ROOT, 'tools', 'adaptor_rules.py'), os.path.join(out, 'py'))
    open(os.path.join(out, '.nojekyll'), 'w').close()

    # protocol
    docs = sorted(f for f in os.listdir(os.path.join(ROOT, 'docs')) if f.endswith('.docx'))
    version = re.sub(r'Rev(\d+)', r'Rev.\1', re.search(r'(V\d+_Rev\d+_[A-Z]+)', docs[0]).group(1).replace('_', ' '))
    files, rows = [], []
    for f in docs:
        src = os.path.join(ROOT, 'docs', f); shutil.copy(src, os.path.join(out, 'protocol', f))
        txt = f[:-5] + '.txt'; open(os.path.join(out, 'protocol', txt), 'w', encoding='utf-8').write(docx_text(src))
        label = 'Core Specification' if 'Core' in f else 'Companion Document'
        h = sha_file(src)
        files.append(dict(document=label, docx='protocol/' + f, text='protocol/' + txt, sha256=h, bytes=os.path.getsize(src)))
        rows.append('<tr><td>%s</td><td><a href="protocol/%s">.docx</a> <span class="note mono">%d KB</span></td><td><a href="protocol/%s">.txt</a> '
                    '<button class="btn ghost" type="button" data-copy-url="protocol/%s">Copy all</button></td><td class="num" title="%s">%s…</td></tr>'
                    % (label, f, os.path.getsize(src) // 1024, txt, txt, h, h[:16]))
    script_sha = re.search(r'SCRIPT SHA-256: ([0-9a-f]{64})', os.popen('%s %s --version' % (sys.executable, os.path.join(ROOT, 'scripts', 'canonical_reference.py'))).read())
    script_sha = script_sha.group(1) if script_sha else ''
    protocol = dict(version=version, files=files, reference_script=dict(path='py/canonical_reference.py', sha256=script_sha),
                    start='Attach both documents to a conversation with any AI and type: Welcome Navigator', repository='https://github.com/' + repo)

    # record
    items = R.library(); areas = R.areas()
    import curator, aperture_audit as ap, dashboard
    for i in items:
        if i['area'] == 'open':
            fp = os.path.join(ROOT, i['path']); t = open(fp, encoding='utf-8', errors='replace').read() if os.path.exists(fp) else ''
            i['area'] = curator.classify(i['title'] + '\n' + (ap.the_answer(t) if '\u250c\u2500 THE ANSWER' in t else t[:4000]), areas)
    counts = {}
    for i in items: counts[i['area']] = counts.get(i['area'], 0) + 1
    for a in areas: a['count'] = counts.get(a['slug'], 0)
    contributors = R.contributors()
    for c in contributors: c['level'] = level(c['points'])
    api = {'protocol.json': protocol, 'library.json': dict(items=items, areas=[dict(slug=a['slug'], name=a['name']) for a in areas]),
           'register.json': register_json(), 'prior-art.json': R.ledger(), 'research-areas.json': areas,
           'contributors.json': contributors, 'professionals.json': R.professionals(),
           'dashboard.json': dict(figures=dashboard.figures(), rule='A display of the record, not an instrument (Core M283, L-495): each figure states what it counts and what it does not, and none is a count of validations or a guide to what to ask.')}
    # Construct X: the Knowledge Register (STP), the curator's catalogue and the Lab (a standalone page)
    import stp
    kreg = json.load(open(os.path.join(ROOT, 'records', 'stp', 'registry.json'), encoding='utf-8'))['entries']
    api['knowledge.json'] = dict(about='The Speculation Test Protocol register (records/stp/registry.json): criteria fixed before each run; failures kept.',
                                 entries=[dict(id=e['id'], hypothesis=e['hypothesis'], criterion=e['criterion'], blinding=e['blinding'],
                                               status=e['status'], evidence=stp.evidence(e)) for e in kreg.values()])
    cat = os.path.join(ROOT, 'records', 'curation', 'agent', 'catalogue.json')
    if os.path.exists(cat):
        c = json.load(open(cat, encoding='utf-8'))
        api['catalogue.json'] = dict(summary=c['summary'], threads=c['threads'], proposed_new_areas=c.get('proposed_new_areas', []),
                                     items=[{k: r[k] for k in ('id', 'kind', 'title', 'by', 'chamber', 'declared_area', 'proposed_area', 'reason', 'changed', 'disposition', 'path')} for r in c['items']])
    arc = os.path.join(ROOT, 'records', 'archive', 'drive_register.json')
    if os.path.exists(arc):
        api['archive.json'] = json.load(open(arc, encoding='utf-8'))   # the archive register (docs/ARCHIVE_POLICY.md)
    man = os.path.join(ROOT, 'records', 'releases', 'manifest.json')
    if os.path.exists(man):
        api['release.json'] = json.load(open(man, encoding='utf-8'))   # the release record (RELEASES.md)
    os.makedirs(os.path.join(out, 'lab'), exist_ok=True)
    shutil.copy(os.path.join(SITE, 'construct_x_lab.html'), os.path.join(out, 'lab', 'index.html'))
    for k, v in api.items():
        json.dump(v, open(os.path.join(out, 'api', k), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    # pages
    layout = open(os.path.join(SITE, 'layout.html'), encoding='utf-8').read()
    freg = json.load(open(os.path.join(ROOT, 'records', 'frontier', 'register.json'), encoding='utf-8'))
    fsubs = frontier_html(freg)
    json.dump(freg, open(os.path.join(out, 'api', 'frontier.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)   # the Daily Frontier register
    vision = md_html(open(os.path.join(ROOT, 'docs', 'VISION.md'), encoding='utf-8').read())
    subs = dict(fsubs, **questions_html(json.load(open(os.path.join(ROOT, 'records', 'questions', 'register.json'), encoding='utf-8'))))
    subs.update({'{{VISION}}': vision,
            '{{REPO}}': repo, '{{VERSION}}': version, '{{BASE}}': '', '{{PROTOCOL_ROWS}}': '\n'.join(rows),
            '{{SCRIPT_SHA_SHORT}}': script_sha[:16], '{{NEWSLETTER_ACTION}}': cfg.get('newsletter', {}).get('form_action') or '#subscribe'})
    pages = []
    # the Companion Explorer: one page per Part, a contents page and a search index, from the Companion's Markdown (one source)
    cpath = os.path.join(ROOT, 'ai', 'Omega42_Companion_V335_Rev450.md')
    if os.path.exists(cpath):
        parts = companion_sections(cpath); index = []
        def render(title, desc, body, navkey, fname):
            pg = layout.replace('{{TITLE}}', html.escape(title)).replace('{{DESC}}', html.escape(desc)).replace('{{NAV}}', nav_html(navkey)) \
                       .replace('{{BODY}}', body).replace('{{SCRIPTS}}', '')
            for k, v in subs.items(): pg = pg.replace(k, v)
            open(os.path.join(out, fname), 'w', encoding='utf-8').write(pg); pages.append(fname)
        toc = []
        for i, (pslug, ptitle, ptags, subsecs) in enumerate(parts):
            fname = 'companion-%s.html' % pslug
            prev = '<a class="btn ghost" href="companion-%s.html">← %s</a>' % (parts[i - 1][0], html.escape(parts[i - 1][1][:40])) if i else ''
            nxt = '<a class="btn ghost" href="companion-%s.html">%s →</a>' % (parts[i + 1][0], html.escape(parts[i + 1][1][:40])) if i + 1 < len(parts) else ''
            chips = ''.join('<span class="chip">%s</span>' % html.escape(t) for t in ptags)
            secs, side = [], []
            for anchor, stitle, stags, lines in subsecs:
                if anchor != 'top':
                    side.append('<a href="#%s">%s</a>' % (anchor, html.escape(stitle[:70])))
                    secs.append('<section id="%s" class="csec"><h2><a class="anchor" href="#%s">§</a> %s %s</h2>%s</section>' % (
                        anchor, anchor, html.escape(stitle), ''.join('<span class="chip">%s</span>' % html.escape(t) for t in stags), companion_body(lines)))
                else:
                    secs.append('<section class="csec">%s</section>' % companion_body(lines))
                index.append(dict(f=fname, a='' if anchor == 'top' else anchor, p=ptitle[:80], t='' if anchor == 'top' else stitle[:120], x=' '.join(lines)))
            body = ('<div class="wide companion"><div class="crumbs mono"><a href="companion.html">Companion Explorer</a> · %s · %s</div>'
                    '<div class="cgrid"><aside class="ctoc">%s</aside><article class="col stack"><h1>%s</h1><div class="row">%s</div>%s'
                    '<div class="row" style="justify-content:space-between">%s%s</div></article></div></div>') % (
                html.escape(version), html.escape(ptitle[:60]), ''.join(side) or '<span class="note">No subsections</span>', html.escape(ptitle), chips, ''.join(secs), prev, nxt)
            render('%s · Omega42 Companion' % ptitle[:70], 'Omega42 Companion, %s: %s' % (version, ptitle), body, 'companion', fname)
            toc.append((pslug, ptitle, ptags, len(subsecs) - 1))
        subs['{{COMPANION_TOC}}'] = ''.join('<a class="ctoc-row" href="companion-%s.html"><span>%s</span><span class="note">%s%s</span></a>' % (
            p, html.escape(t), ' · '.join(html.escape(x) for x in tg[:1]), (' · %d sections' % n) if n else '') for p, t, tg, n in toc)
        subs['{{COMPANION_COUNT}}'] = str(len(toc))
        json.dump(index, open(os.path.join(out, 'api', 'companion-search.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    for f in sorted(os.listdir(os.path.join(SITE, 'pages'))):
        src = open(os.path.join(SITE, 'pages', f), encoding='utf-8').read()
        m = re.match(r'<!--(\{.*?\})-->\n', src, re.S); meta = json.loads(m.group(1)); body = src[m.end():]
        nav = nav_html(meta.get('nav'))
        page = layout.replace('{{TITLE}}', html.escape(meta['title'])).replace('{{DESC}}', html.escape(meta['desc'])).replace('{{NAV}}', nav) \
                     .replace('{{BODY}}', body).replace('{{SCRIPTS}}', ''.join('<script src="assets/%s"></script>' % s for s in meta.get('scripts', [])))
        for k, v in subs.items(): page = page.replace(k, v)
        open(os.path.join(out, f), 'w', encoding='utf-8').write(page); pages.append(f)


    # for machines
    open(os.path.join(out, 'robots.txt'), 'w').write('User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n' % site_url)
    open(os.path.join(out, 'sitemap.xml'), 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join('  <url><loc>%s%s</loc></url>\n' % (site_url, p) for p in pages if p != '404.html') + '</urlset>\n')
    llms = ['# Ω42 (Omega42)', '', '> One mathematical world, finite at every depth and endless in the whole, that you can ask any question. The canonical 24-step cycle of the Fibonacci law modulo 9 and its',
            '> family of 81 states are taken as all that exists; an AI acting as Navigator places a question on the cycle from its exact wording,',
            '> reads it from there as one complete finding, and leaves its meaning to the person (the Aperture).', '',
            'Version: %s' % version, 'Start: attach both documents to a conversation and type "Welcome Navigator".', '',
            '## Protocol'] + ['- [%s](%s%s): SHA-256 %s; plain text: %s%s' % (f['document'], site_url, f['docx'], f['sha256'], site_url, f['text']) for f in files] + [
            '- [Reference script](%spy/canonical_reference.py): SCRIPT SHA-256 %s' % (site_url, script_sha), '',
            '## Record (JSON)'] + ['- %sapi/%s' % (site_url, k) for k in api] + ['',
            '## Submitting', '- Issue forms at https://github.com/%s/issues/new/choose ; rules for AI agents: https://github.com/%s/blob/main/AI_ACCESS.md' % (repo, repo),
            '- Received Navigator content is reviewed automatically (SNCA; SR-CAS where the domain is already in the record).', '',
            '## Licences', '- Text CC BY 4.0; code Apache-2.0; the name is a mark (TRADEMARK.md).']
    open(os.path.join(out, 'llms.txt'), 'w', encoding='utf-8').write('\n'.join(llms) + '\n')
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    entries = ''.join('<entry><id>%s#%s</id><title>%s</title><updated>%sT00:00:00Z</updated><link href="https://github.com/%s/blob/main/%s"/>'
                      '<author><name>%s</name></author></entry>\n' % (site_url, html.escape(i['id']), html.escape('%s · %s' % (i['id'], i['title'])),
                      i['date'] or '2026-10-15', repo, html.escape(i['path']), html.escape(i['by'] or 'Ω42')) for i in items[:50])
    open(os.path.join(out, 'feed.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom"><title>Ω42 open record</title><id>%s</id><updated>%s</updated>'
        '<link href="%s"/>\n%s</feed>\n' % (site_url, now, site_url, entries))
    return dict(pages=pages, api=list(api), version=version)


def md_html(text):
    """A small Markdown subset (headings, paragraphs, lists, bold, italic) for the public paper (docs/VISION.md)."""
    def inline(t):
        t = html.escape(t, quote=False)
        t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
        return re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<i>\1</i>', t)
    out, para, items = [], [], []
    def flush():
        if para: out.append('<p>%s</p>' % inline(' '.join(para))); para.clear()
        if items: out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % inline(i) for i in items)); items.clear()
    for line in text.splitlines():
        m = re.match(r'(#{1,3}) (.*)', line)
        if m: flush(); out.append('<h%d>%s</h%d>' % (len(m.group(1)) + 1, inline(m.group(2)), len(m.group(1)) + 1)); continue
        if re.match(r'(- |\d+\. )', line): (para and flush()); items.append(re.sub(r'^(- |\d+\. )', '', line)); continue
        if not line.strip(): flush(); continue
        para.append(line.strip())
    flush()
    return '\n'.join(out)


def companion_sections(path):
    """The Companion text before Appendix X, split into its Parts: [(slug, title, tags, [(anchor, title, tags, lines)])]."""
    text = open(path, encoding='utf-8').read()
    text = text[:text.find('\n### APPENDIX X')] if '\n### APPENDIX X' in text else text
    def tags_of(t):
        m = re.findall(r'\[([^\]]+)\]', t); return re.sub(r'\s*\[[^\]]+\]', '', t).strip(), m
    def slug(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:60] or 'section'
    parts, cur, sub = [], None, None
    for line in text.splitlines():
        m = re.match(r'### (.*)', line)
        if m:
            title, tags = tags_of(m.group(1))
            if not re.match(r'\d', title):
                sm = re.match(r'PART ([\d.]+)', title)
                cur = ('part-' + sm.group(1).replace('.', '-')) if sm else slug(title)
                parts.append([cur, title, tags, []]); sub = None
                parts[-1][3].append(['top', '', [], []]); continue
            nm = re.match(r'([\d.]+)', title)
            if parts: parts[-1][3].append(['s-' + nm.group(1).replace('.', '-').strip('-'), title, tags, []])
            continue
        if parts and line.strip() and line.strip() != '---': parts[-1][3][-1][3].append(line.strip())
    seen = set()
    for p in parts:
        while p[0] in seen: p[0] += '-b'
        seen.add(p[0])
    return parts


def companion_body(lines):
    out, items = [], []
    def flush():
        if items: out.append('<ul>%s</ul>' % ''.join('<li>%s</li>' % i for i in items)); items.clear()
    for l in lines:
        e = html.escape(l, quote=False).replace('{', '&#123;').replace('}', '&#125;')
        e = re.sub(r'\[((?:EXPLORATORY|CDT|PROTOCOL|REFERENCE|RESEARCH)[^\]]*)\]', r'<span class="chip">\1</span>', e)
        if re.match(r'[-*] ', l): items.append(e[2:]); continue
        flush()
        q = re.match(r'(Q\d+[a-z]?: .*)', e)
        out.append('<h3 class="q">%s</h3>' % q.group(1) if q and len(e) < 200 else '<p>%s</p>' % e)
    flush()
    return '\n'.join(out)


def questions_html(reg):
    """The World of Questions (records/questions/register.json): category cards for the home page, the full catalogue and cross-field questions."""
    from urllib.parse import urlencode
    E = lambda t: html.escape(t)
    ap = reg['approaches']; n = [0]
    def q(item, show=True):
        n[0] += 1; qid = 'wq-%d' % n[0]
        ask = 'strike.html#' + urlencode({'q': item['q'], 'mode': item['approach'], 'go': '0'})
        return ('<li%s><span id="%s" class="qt">%s</span><span class="qa"><span class="chip">%s</span><button class="mini" type="button" data-copy="#%s">Copy</button>'
                '<a class="mini" href="%s">Ask →</a></span></li>') % ('' if show else ' class="more"', qid, E(item['q']), E(ap[item['approach']]), qid, E(ask))
    home = ''.join('<div class="qcat %s"><a class="k" href="questions.html#%s">%s</a><p class="note">%s</p><ul class="qs">%s</ul>%s</div>' % (
        c['color'], E(c['id']), E(c['name']), E(c['scope']), ''.join(q(x) for x in c['featured'][:2]),
        '<a class="go" href="questions.html#%s">More questions →</a>' % E(c['id']) if c['featured'] else '<a class="go" href="strike.html">Ask anything →</a>') for c in reg['categories'])
    full = ''.join('<section class="qcat %s" id="%s"><h2>%s</h2><p class="note">%s</p><ul class="qs">%s</ul></section>' % (
        c['color'], E(c['id']), E(c['name']), E(c['scope']), ''.join(q(x) for x in c['featured']) or '<li><a class="mini" href="strike.html">Ask anything →</a></li>') for c in reg['categories'])
    cross = ''.join('<div class="qcat c-violet"><span class="k">%s</span><ul class="qs">%s</ul></div>' % (E(x['fields']), q(x)) for x in reg['cross'])
    return {'{{QUESTIONS_HOME}}': home, '{{QUESTIONS_ALL}}': full, '{{QUESTIONS_CROSS}}': cross, '{{QUESTIONS_PRINCIPLE}}': E(reg['principle'])}


def series_svg(series):
    """A small line chart of an announcement's computed series (the visual reveal); colours by series."""
    if not series: return ''
    W, H, P = 560, 220, 34; n = max(len(v) for _, v in series); top = max(max(v) for _, v in series)
    cols = ['#0b8fae', '#c2307f', '#6a3fe0', '#cf5f12']
    X = lambda i: P + i * (W - 2 * P) / (n - 1); Y = lambda y: H - P - y * (H - 2 * P) / top
    out = ['<svg class="reveal" viewBox="0 0 %d %d" role="img" aria-label="computed series">' % (W, H),
           '<line x1="%d" y1="%d" x2="%d" y2="%d" class="axis"/>' % (P, H - P, W - P, H - P)]
    for k, (label, v) in enumerate(series):
        c = cols[k % 4]
        out.append('<polyline fill="none" stroke="%s" stroke-width="2.5" points="%s"/>' % (c, ' '.join('%.1f,%.1f' % (X(i), Y(y)) for i, y in enumerate(v))))
        out += ['<circle cx="%.1f" cy="%.1f" r="3" fill="%s"/>' % (X(i), Y(y), c) for i, y in enumerate(v)]
        out.append('<text x="%d" y="%d" fill="%s">%s (ends at %d)</text>' % (P + 6, 18 + 16 * k, c, html.escape(label), v[-1]))
    out.append('<text x="%d" y="%d" class="axis-t">steps 1 to %d</text></svg>' % (W - P - 90, H - 10, n))
    return ''.join(out)


def universe_svg(reg):
    """The Discovery Universe: announcements, explorations, programmes and challenges as nodes; edges styled by relationship."""
    import math
    nodes = sorted({x for l in reg['links'] for x in l[:2]})
    kind = lambda n: n.split('-')[0]
    ring = {'DF': 0.0, 'EX': 1.0, 'FP': 0.55, 'GC': 0.55, 'XC': 1.0}
    col = {'DF': '#f3c45f', 'EX': '#c9a7ff', 'FP': '#8fe9ff', 'GC': '#ff8a3d', 'XC': '#9be37a'}
    W = H = 460; cx = cy = W / 2; pos = {}
    groups = {}
    for n in nodes: groups.setdefault(kind(n), []).append(n)
    inner = groups.get('DF', [])
    for i, n in enumerate(inner): t = 2 * math.pi * i / len(inner) - math.pi / 2; pos[n] = (cx + 60 * math.cos(t), cy + 60 * math.sin(t))
    mid = groups.get('FP', []) + groups.get('GC', [])
    for i, n in enumerate(mid): t = 2 * math.pi * i / len(mid) + 0.3; pos[n] = (cx + 135 * math.cos(t), cy + 135 * math.sin(t))
    outer = groups.get('EX', []) + groups.get('XC', [])
    for i, n in enumerate(outer): t = 2 * math.pi * i / len(outer) - 0.2; pos[n] = (cx + 200 * math.cos(t), cy + 200 * math.sin(t))
    dash = {'analogy': '3 5', 'formal mapping': '', 'derivation': '', 'program': '1 4', 'programme': '1 4'}
    width = {'analogy': 1.2, 'formal mapping': 2, 'derivation': 3.2, 'program': 1.2, 'programme': 1.2}
    out = ['<svg class="universe" viewBox="0 0 %d %d" role="img" aria-label="The Discovery Universe map">' % (W, H)]
    for a, b, t in reg['links']:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        out.append('<line x1="%.0f" y1="%.0f" x2="%.0f" y2="%.0f" stroke="#cfc9f2" stroke-opacity=".7" stroke-width="%s" stroke-dasharray="%s"><title>%s %s %s</title></line>' % (x1, y1, x2, y2, width[t], dash[t], a, t, b))
    for n in nodes:
        x, y = pos[n]; c = col[kind(n)]
        out.append('<g><circle cx="%.0f" cy="%.0f" r="%d" fill="%s" fill-opacity=".9"/><text x="%.0f" y="%.0f" text-anchor="middle">%s</text></g>' % (x, y, 15 if kind(n) == 'DF' else 11, c, x, y + (30 if kind(n) == 'DF' else 25), n))
    out.append('</svg>')
    return ''.join(out)


def frontier_html(reg):
    """The Discovery Bulletin (the public face of the Daily Frontier) and the Expert Exploration Desk, from records/frontier/register.json."""
    E = lambda t: html.escape(t)
    def card(d):
        status = ''.join('<span class="chip">%s</span>' % E(x) for x in d['status'])
        areas = ' · '.join(E(a) for a in d['areas'])
        comp = ('<h3>What was computed</h3><p>%s <span class="note">(recompute: <code>python3 %s</code>)</span></p>' % (E(d['computed']), E(d['script']))) if d['computed'] else ''
        return ('<article class="entry" id="%s"><div class="row"><span class="chip gold">%s</span><span class="chip cls">%s</span><span class="chip">method: %s</span>%s<span class="note">%s · %s</span></div>'
                '<h2>%s</h2><p class="lede"><b>What has emerged.</b> %s</p>%s'
                '<h3>Why it matters</h3><p>%s</p><h3>The discovery itself</h3><p>%s</p>%s<h3>Follow the implications</h3><p>%s</p>'
                '<h3>The frontier</h3><p>%s</p><blockquote class="fieldnote"><span class="k">Navigator\'s field note</span>%s</blockquote>'
                '<h3>Join the discovery</h3><p>%s</p><div class="actions"><a class="act" href="submit.html"><b>Extend this idea</b><span>Contribute</span></a>'
                '<a class="act" href="forum.html"><b>Challenge the reasoning</b><span>Critique</span></a><a class="act" href="speculate.html"><b>Connect it to another field</b><span>Explore</span></a></div>'
                '<p class="note">Related: %s · Navigator: %s · %s</p></article>') % (
            E(d['id']), E(d['id']), E(d['class']), E(d['method']), status, E(d['date']), areas, E(d['headline']), E(d['emerged']), series_svg(d['series']),
            E(d['significance']), E(d['model']), comp, E(d['implications']), E(d['frontier']), E(d['field_note']), E(d['challenge']),
            E(', '.join(d['related'])), E(d['navigator']), E(d['publication']))
    lead = reg['entries'][0]
    more = ''.join('<a class="door c-violet" href="bulletin.html#%s"><span class="k">%s · %s</span><h3>%s</h3><span class="go">Read the announcement →</span></a>' % (
        E(d['id']), E(d['class']), E(' · '.join(d['areas'])), E(d['headline'])) for d in reg['entries'][1:])
    w = reg['weekly']
    weekly = ('<div class="eyebrow">Weekly event · %s · open %s to %s</div><h2>%s</h2><p><b>%s</b></p><p>%s</p><p class="note">%s</p>' % (
        E(w['id']), E(w['opens']), E(w['closes']), E(w['title']), E(w['question']), E('Starting point: ' + w['start']), E(w['recognition'])))
    c = ''.join('<tr><td class="num">%s</td><td>%s</td><td>%s</td></tr>' % (E(x['id']), E(x['challenge']), E(x['expertise'])) for x in reg['challenges'])
    return {'{{BULLETIN_ENTRIES}}': ''.join(card(d) for d in reg['entries']), '{{CHALLENGES}}': c, '{{WEEKLY}}': weekly, '{{UNIVERSE}}': universe_svg(reg),
            '{{BULLETIN_MORE}}': more, '{{LEAD_ID}}': E(lead['id']), '{{LEAD_CLASS}}': E(lead['class']), '{{LEAD_HEADLINE}}': E(lead['headline']),
            '{{LEAD_EMERGED}}': E(lead['emerged']), '{{LEAD_AREAS}}': E(' · '.join(lead['areas']))}


def selftest():
    import tempfile
    ok = True
    def check(label, c):
        nonlocal ok; print('%-58s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    out = tempfile.mkdtemp(prefix='o42site_')
    r = build(os.path.join(out, 's'), 'example/omega42')
    s = os.path.join(out, 's')
    check('every page is built and carries the layout', all('class="top"' in open(os.path.join(s, p), encoding='utf-8').read() for p in r['pages']))
    check('no template placeholder is left in any page', not any('{{' in open(os.path.join(s, p), encoding='utf-8').read() for p in r['pages']))
    check('links to forms point at the repository', 'github.com/example/omega42/issues/new?template=1-navigation.yml' in open(os.path.join(s, 'submit.html'), encoding='utf-8').read())
    pj = json.load(open(os.path.join(s, 'api', 'protocol.json')))
    check('protocol.json hashes equal the documents', all(f['sha256'] == sha_file(os.path.join(ROOT, 'docs', os.path.basename(f['docx']))) for f in pj['files']))
    check('the reference script is published unchanged', sha_file(os.path.join(s, 'py', 'canonical_reference.py')) == sha_file(os.path.join(ROOT, 'scripts', 'canonical_reference.py')))
    reg = json.load(open(os.path.join(s, 'api', 'register.json')))
    check('register.json carries the domains of records/congruence', len(reg['domains']) == len(cg.load_register()))
    check('llms.txt, robots.txt, sitemap.xml and feed.xml written', all(os.path.exists(os.path.join(s, f)) for f in ('llms.txt', 'robots.txt', 'sitemap.xml', 'feed.xml')))
    shutil.rmtree(out)
    print('SITE BUILD SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if '--out' not in a: print(__doc__); sys.exit(0)
    out = a[a.index('--out') + 1]; repo = a[a.index('--repo') + 1] if '--repo' in a else None
    branch = a[a.index('--branch') + 1] if '--branch' in a else 'main'
    r = build(out, repo)
    if branch != 'main':   # links into the repository follow the branch the site is built from
        for d, _, fs in os.walk(out):
            for f in fs:
                if f.endswith(('.html', '.xml', '.txt', '.js')):
                    fp = os.path.join(d, f); t = open(fp, encoding='utf-8').read()
                    u = t.replace('/blob/main/', '/blob/%s/' % branch).replace('/tree/main/', '/tree/%s/' % branch)
                    if u != t: open(fp, 'w', encoding='utf-8').write(u)
    print('built %d pages and %d data files into %s (%s)' % (len(r['pages']), len(r['api']), out, r['version']))
