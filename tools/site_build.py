#!/usr/bin/env python3
"""site_build.py -- builds the Ω42 portal (GitHub Pages) from site/ and the open record.

    python3 tools/site_build.py --out _site [--repo OWNER/REPO]
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
NAV = [('index', 'Home'), ('protocol', 'Protocol'), ('strike', 'Strike'), ('library', 'Library'), ('construct-x', 'Construct X'), ('submit', 'Submit'),
       ('forum', 'Forum'), ('research', 'Research'), ('community', 'Community'), ('governance', 'Governance')]
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
    man = os.path.join(ROOT, 'records', 'releases', 'manifest.json')
    if os.path.exists(man):
        api['release.json'] = json.load(open(man, encoding='utf-8'))   # the release record (RELEASES.md)
    os.makedirs(os.path.join(out, 'lab'), exist_ok=True)
    shutil.copy(os.path.join(SITE, 'construct_x_lab.html'), os.path.join(out, 'lab', 'index.html'))
    for k, v in api.items():
        json.dump(v, open(os.path.join(out, 'api', k), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    # pages
    layout = open(os.path.join(SITE, 'layout.html'), encoding='utf-8').read()
    subs = {'{{REPO}}': repo, '{{VERSION}}': version, '{{BASE}}': '', '{{PROTOCOL_ROWS}}': '\n'.join(rows),
            '{{SCRIPT_SHA_SHORT}}': script_sha[:16], '{{NEWSLETTER_ACTION}}': cfg.get('newsletter', {}).get('form_action') or '#subscribe'}
    pages = []
    for f in sorted(os.listdir(os.path.join(SITE, 'pages'))):
        src = open(os.path.join(SITE, 'pages', f), encoding='utf-8').read()
        m = re.match(r'<!--(\{.*?\})-->\n', src, re.S); meta = json.loads(m.group(1)); body = src[m.end():]
        nav = ''.join('<a href="%s.html"%s>%s</a>' % (k, ' aria-current="page"' if k == meta.get('nav') else '', t) for k, t in NAV)
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
    r = build(out, repo); print('built %d pages and %d data files into %s (%s)' % (len(r['pages']), len(r['api']), out, r['version']))
