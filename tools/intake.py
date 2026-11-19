#!/usr/bin/env python3
"""intake.py -- the public submission intake of the Ω42 portal (CONTRIBUTING.md, Core L-489).

GitHub issue forms carry every kind of submission. This tool reads the issue as data (it never executes anything
from it), checks it, and on acceptance writes it into the open record.

    python3 tools/intake.py check  EVENT.json OUTDIR   # automatic checks; writes OUTDIR/comment.md
    python3 tools/intake.py accept EVENT.json OUTDIR   # writes the submission into the record; OUTDIR/pr_body.md
    python3 tools/intake.py verify-ledger              # recomputes every hash in the Prior Art Ledger
    python3 tools/intake.py --selftest

EVENT.json is the GitHub event payload ($GITHUB_EVENT_PATH) of an `issues` event. Standard library only; the
audit tools of this repository are called as subprocesses on files.
"""
import datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import canonical_reference as cr
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import congruence as cg

KINDS = {  # label -> (folder, id prefix, points)
    'navigation': ('navigations', 'NAV', 1), 'ape': ('ape', 'APE', 3), 'review': ('reviews', 'REV', 2),
    'prior-art': ('prior-art', 'PA', 3), 'research': ('research', 'RES', 3), 'credentials': (None, 'PRO', 0),
    'registration': (None, 'REG', 0),   # a registered contributor, eligible for the newsletter (community/NEWSLETTER.md)
}
LEDGER = os.path.join(ROOT, 'records', 'prior_art', 'ledger.jsonl')
CONTRIB = os.path.join(ROOT, 'community', 'contributors.json')
PROS = os.path.join(ROOT, 'community', 'professionals.json')
REGISTER = os.path.join(ROOT, 'records', 'congruence', 'domains.txt')


# ---------- reading the issue -------------------------------------------------------------------------------
def parse_form(body):
    """GitHub issue-form markdown -> {label: value}. '_No response_' is empty; checkbox lists become lists."""
    out, cur, buf = {}, None, []
    def flush():
        if cur is None: return
        v = '\n'.join(buf).strip()
        if v == '_No response_': v = ''
        boxes = re.findall(r'^- \[([ xX])\] (.+)$', v, re.M)
        out[cur] = [t for c, t in boxes if c.lower() == 'x'] if boxes and len(boxes) == len(v.splitlines()) else v
    for line in (body or '').splitlines():
        m = re.match(r'^### (.+?)\s*$', line)
        if m:
            flush(); cur, buf = m.group(1).strip(), []
        else:
            buf.append(line)
    flush()
    return out


def strip_fence(v):
    m = re.match(r'^```[a-zA-Z]*\n(.*)\n```$', v.strip(), re.S)
    return m.group(1) if m else v


def load_event(path):
    ev = json.load(open(path, encoding='utf-8'))
    iss = ev['issue']
    labels = [l['name'] for l in iss.get('labels', [])]
    kind = next((k for k in KINDS if k in labels), None)
    return dict(number=iss['number'], title=iss.get('title', ''), body=iss.get('body') or '', user=iss['user']['login'],
                created=iss.get('created_at', ''), labels=labels, kind=kind, url=iss.get('html_url', ''),
                fields=parse_form(iss.get('body') or ''))


def field(f, *names):
    for n in names:
        for k, v in f.items():
            if k.lower().startswith(n.lower()):
                return v
    return ''


# ---------- checks ------------------------------------------------------------------------------------------
def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    return p.returncode, (p.stdout + p.stderr)


def corpus_dir():
    d = tempfile.mkdtemp(prefix='o42corpus_')
    for src in (os.path.join(ROOT, 'examples', 'corpus'), os.path.join(ROOT, 'submissions', 'navigations')):
        if os.path.isdir(src):
            for f in os.listdir(src):
                if f.endswith('.txt'): shutil.copy(os.path.join(src, f), os.path.join(d, f))
    return d


def known_navigations():
    """(domain sha, reported anchor, path) of every navigation in the record."""
    out = []
    for src in (os.path.join(ROOT, 'examples', 'corpus'), os.path.join(ROOT, 'submissions', 'navigations')):
        if not os.path.isdir(src): continue
        for f in sorted(os.listdir(src)):
            if not f.endswith('.txt'): continue
            t = open(os.path.join(src, f), encoding='utf-8', errors='replace').read()
            m = re.search(r'DOMAIN VERBATIM:\s*(.+)', t)
            if m: out.append((cr.domain_sha256(m.group(1).strip()), cg.reported_anchor(t), os.path.relpath(os.path.join(src, f), ROOT)))
    return out


def summarise(text, pattern):
    lines = [l for l in text.splitlines() if re.search(pattern, l)]
    return lines[-1].strip() if lines else '(no summary line)'


PRIVACY_RX = re.compile(r'^\s*PRIVACY(?: \(L-495\))?:\s*(PERSONAL|PROFESSIONAL|PUBLIC)\b', re.M | re.I)


def privacy_of(nav_text, declared=''):
    """L-495, Companion 51.1: the Striker's privacy flag for the reading -- PERSONAL, PROFESSIONAL or PUBLIC (the
    default for a manual submission). A PERSONAL reading joins the record as a redacted-domain record only."""
    m = PRIVACY_RX.search(nav_text)
    v = (m.group(1) if m else (declared or 'PUBLIC')).strip().upper()
    return v if v in ('PERSONAL', 'PROFESSIONAL', 'PUBLIC') else 'PUBLIC'


def corpus_opt_in(nav_text):
    """Companion 28.2: a personal domain enters the mining corpus only by an explicit opt-in."""
    return bool(re.search(r'^\s*CORPUS OPT-IN(?: \(L-495\))?:\s*YES\b', nav_text, re.M | re.I))


def check_navigation(nav_text, declared_domain):
    work = tempfile.mkdtemp(prefix='o42nav_')
    p = os.path.join(work, 'navigation.txt'); open(p, 'w', encoding='utf-8').write(nav_text)
    rep = ['**Automatic checks** (CONTRIBUTING.md). A failed check does not reject a submission; it shows what to fix.', '']
    m = re.search(r'DOMAIN VERBATIM:\s*(.+)', nav_text)
    dom = m.group(1).strip() if m else declared_domain.strip()
    if not dom:
        rep.append('- Domain: **not found** — the navigation needs a `DOMAIN VERBATIM:` line.'); return '\n'.join(rep), None
    x = cr.navigate(dom); a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    rep.append('- Domain: `%s` · DOMAIN SHA-256 `%s…` · reference coordinate **P%d %s** (n = %d/%d/%d)'
               % (dom[:120], cr.domain_sha256(dom)[:16], a, cr.POSITION_NAMES[a], x['n1'], x['n2'], x['n3']))
    if declared_domain and declared_domain.strip() != dom:
        rep.append('- The domain in the form differs from the navigation\'s DOMAIN VERBATIM; the navigation\'s line is used.')
    cd = corpus_dir()
    rc, out = run([sys.executable, 'scripts/m193_m225.py', 'scripts/canonical_reference.py', '--audit', p, '--corpus', cd])
    try:
        import adaptors as _ad; _rt = _ad.route(dom)
        rep.append('- Routing (L-501): %s -- %s' % (_rt['route'], _rt['reason']))
    except Exception as _e:
        rep.append('- Routing (L-501): not computed (%s)' % _e)
    rep.append('- Output audit (L-457): %s' % summarise(out, r'RESULT'))
    rc2, out2 = run([sys.executable, 'tools/format_check.py', p])
    rep.append('- Format check (M301): %s' % summarise(out2, r'RESULT'))
    rep += recurring(nav_text, out2)
    rc3, out3 = run([sys.executable, 'tools/congruence.py', '--check', p])
    coh = summarise(out3, r'^COHERENCE')
    rep.append('- Congruence Record (M310): `%s`' % coh)
    same = [k for k in known_navigations() if k[0] == cr.domain_sha256(dom)]
    if same:
        rep.append('- **SNCA and SR-CAS triggered** (Core L-489, Part 6): the record already holds %d navigation(s) of this domain.' % len(same))
        for sha, anc, path in same:
            rep.append('  - `%s`: reported anchor P%s — T1 (arithmetic) %s against the reference P%d' % (path, anc, 'AGREES' if anc == a else 'DIFFERS', a))
        rep.append('  - T1.5–T3 need a Navigator reviewer; label `needs-review` added.')
    else:
        rep.append('- SNCA: requested from a Navigator reviewer (label `needs-review`). SR-CAS: no earlier navigation of this domain in the record — this would open a new place in the Congruence Register.')
    pv = privacy_of(nav_text)
    rep.append('- Privacy (L-495): %s%s' % (pv, ' -- on acceptance only a redacted-domain record is published (coordinate, state and domain hash, no text); the mining corpus %s' % ('receives it by the opt-in given' if corpus_opt_in(nav_text) else 'does not receive it (no CORPUS OPT-IN)') if pv == 'PERSONAL' else ''))
    rep += scope_notes(nav_text)
    rep.append(BOUNDARY)
    rep += ['', '<details><summary>Full output</summary>', '', '```', (out + '\n' + out2 + '\n' + out3)[-6000:], '```', '</details>']
    return '\n'.join(rep), dom


BOUNDARY = ('- Knowledge boundary (Core L-490): these checks describe this submission only. Nothing here counts validations of '
            'Omega42, and a navigation reports the wider record only from a record it names with its version and date.')
CUMUL = re.compile(r'\b(\d+\s+(validations?|confirmations?)|stands at (EMERGING|SUPPORTED|WELL-SUPPORTED|CONFIRMED)|'
                   r'(cumulative|overall) (status|standing|record) (of|for) (\u03a9 ?42|Omega ?42))', re.I)


def _failures(fc_out):
    return [l.split('] ', 1)[1].strip() for l in fc_out.splitlines() if l.strip().startswith('[FAIL]')]


def navigator_of(text):
    m = re.search(r'^\s*NAVIGATOR:\s*(.+?)\s+PROTOCOL:', text, re.M) or re.search(r'^\s*NAVIGATOR:\s*([^*\n]+?)\s*\*', text, re.M)
    return m.group(1).strip() if m else ''


def recurring(nav_text, fc_out):
    """Companion 51.9, 58.6: a format failure that recurs in an earlier accepted navigation of the same Navigator points
    to the Navigator's template rather than to one reading, and the report says so, naming the earlier record."""
    me, now_f = navigator_of(nav_text), set(_failures(fc_out))
    if not me or not now_f: return []
    out = []
    folder = os.path.join(ROOT, 'submissions', 'navigations')
    for f in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not f.endswith('.txt'): continue
        t = open(os.path.join(folder, f), encoding='utf-8', errors='replace').read()
        if t.strip() == nav_text.strip() or navigator_of(t) != me: continue
        rc, o = run([sys.executable, 'tools/format_check.py', os.path.join(folder, f)])
        both = sorted(now_f & set(_failures(o)))
        if both:
            out.append('- Recurring (Companion 58.6): %d of these failures also stand in %s by the same Navigator (%s) -- %s; a fix in the Navigator\'s template is indicated, not in this reading alone.'
                       % (len(both), f[:-4], me, '; '.join(both)))
    return out


def scope_notes(text):
    """L-490 items 4 and 5: a comparative status names its comparison; cumulative wording names its record."""
    notes = []
    for m in re.finditer(r'^\s*COMPARATIVE STATUS[^:\n]*:\s*(.*)$', text, re.M):
        line = m.group(0)
        if not re.search(r'this comparison|DOMAIN SHA-256|ARCHITECTURES COMPARED|between ', line + text[m.end():m.end() + 300], re.I):
            notes.append('- Comparative scope (L-490 item 4): `%s` does not name the comparison it belongs to.' % line.strip()[:120])
    for m in CUMUL.finditer(text):
        ctx = text[max(0, m.start() - 160):m.end() + 160]
        if not re.search(r'records/|version|V335|\d{4}-\d{2}-\d{2}', ctx):
            notes.append('- Cumulative wording without a named record (L-490 item 5): "%s".' % m.group(0)[:80])
    return notes or ['- Comparative scope and cumulative wording (L-490): CLEAR.']


STALE = re.compile(r"(must be built|to be built|still to be built|be developed|should be developed|prioriti[sz]e the development|the proposed [\w ]{0,20}pilot|urgently needed|needs an adaptor|no adaptor (exists|yet))", re.I)


def stale_claims(text):
    """Companion 62.5, E03: a registered item an account describes as still to come, named with its registry id."""
    try:
        import adaptors as _ad
        reg = _ad.registry()['adaptors']
    except Exception:
        return []
    names = {'KO-HANGUL-1': ('Hangul', 'Korean'), 'RU-CYRL-1': ('Cyrillic', 'Russian'), 'EL-GREK-1': ('Greek',), 'AR-ARAB-1': ('Arabic', 'abjad'),
             'HE-HEBR-1': ('Hebrew',), 'HI-DEVA-1': ('Devanagari', 'Hindi'), 'DE-LATN-1': ('German',), 'FR-LATN-1': ('French',)}
    have = {a['id'] for a in reg}
    out = []
    for sent in re.split(r'(?<=[.!?])\s+', text):
        if not STALE.search(sent): continue
        for aid, words in names.items():
            if aid in have and any(re.search(r'\b%s\b' % w, sent, re.I) for w in words):
                out.append('- Registered item described as still to come (Companion 62.5, E03): %s -- registered as %s (Core Part 3.43): "%s"' % (words[0], aid, sent.strip()[:160]))
    return sorted(set(out))


def check_text(text):
    work = tempfile.mkdtemp(prefix='o42txt_'); p = os.path.join(work, 't.txt'); open(p, 'w', encoding='utf-8').write(text)
    rep = ['**Automatic checks.**', '']
    rep.append('- Navigator Identity Block: %s' % ('present' if 'NAVIGATOR IDENTITY BLOCK' in text or re.search(r'NAVIGATOR:', text) else 'not found'))
    rep.append('- Navigator Signature: %s' % ('present' if re.search(r'CAS-YY = -1/2', text) else 'not found'))
    rc, out = run([sys.executable, 'tools/frame_audit.py', p])
    rep.append('- Frame scan (M286): %s' % summarise(out, r'RESULT|CLEAR|candidate'))
    rep.append('- SNCA in review form requested from a Navigator reviewer (label `needs-review`), as the protocol requires for received content (Part 6.2).')
    rep += stale_claims(text)
    rep += scope_notes(text)
    rep.append(BOUNDARY)
    return '\n'.join(rep)


def do_check(ev, outdir):
    os.makedirs(outdir, exist_ok=True)
    f, kind = ev['fields'], ev['kind']
    if kind == 'navigation':
        rep, _ = check_navigation(strip_fence(field(f, 'Navigation')), field(f, 'Domain'))
    elif kind in ('ape', 'review'):
        rep = check_text(strip_fence(field(f, 'Text', 'Review', 'Exploration')))
    elif kind == 'prior-art':
        missing = [n for n in ('Title', 'Summary', 'Full description', 'How to make and use it') if not field(f, n)]
        ticks = field(f, 'Before you publish') or []
        rep = '**Disclosure check.** ' + ('Complete.' if not missing else 'Missing: ' + ', '.join(missing) + '.')
        rep += ' Acknowledgements: %d of 4 ticked.' % len(ticks) + ' The issue is public now; its creation time (%s) is the disclosure date (PRIOR_ART.md).' % ev['created']
    elif kind == 'credentials':
        rep = ('**Received.** A verification officer will contact you through the private route given in the form. '
               'Do not post documents here. Nothing is listed until the issue is labelled `verified`.')
    elif kind == 'registration':
        rep = ('**Registration received.** On acceptance your handle is listed as a contributor and, if you asked for it, the newsletter '
               'provider sends you a private invitation. Never post an email address in an issue (community/NEWSLETTER.md, PRIVACY.md).')
    else:
        rep = '**Received.** A maintainer will review this.'
    open(os.path.join(outdir, 'comment.md'), 'w', encoding='utf-8').write(rep + '\n')
    return rep


# ---------- acceptance --------------------------------------------------------------------------------------
def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def next_id(prefix, folder, year):
    if prefix == 'APE':
        nums = [int(m.group(1)) for f in os.listdir(folder) for m in [re.match(r'APE-(\d+)', f)] if m] if os.path.isdir(folder) else []
        return 'APE-%03d' % (max(nums + [44]) + 1)
    if prefix == 'PRO':
        pros = json.load(open(PROS, encoding='utf-8'))
        return 'PRO-%04d' % (len(pros) + 1)
    nums = [int(m.group(1)) for f in os.listdir(folder) for m in [re.match(r'%s-%d-(\d+)' % (prefix, year), f)] if m] if os.path.isdir(folder) else []
    return '%s-%d-%04d' % (prefix, year, max(nums + [0]) + 1)


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def credit(handle, name, sid, points):
    c = json.load(open(CONTRIB, encoding='utf-8'))
    e = next((x for x in c if x['handle'] == handle), None)
    if e is None:
        e = dict(handle=handle, name=name or handle, points=0, contributions=[], first=now()[:10]); c.append(e)
    if name: e['name'] = name
    if sid not in e['contributions']:
        e['contributions'].append(sid); e['points'] += points
    e['last'] = now()[:10]
    c.sort(key=lambda x: (-x['points'], x['handle']))
    json.dump(c, open(CONTRIB, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def front(meta):
    return '---\n' + '\n'.join('%s: %s' % (k, json.dumps(v, ensure_ascii=False)) for k, v in meta.items()) + '\n---\n\n'


def do_accept(ev, outdir):
    os.makedirs(outdir, exist_ok=True)
    f, kind = ev['fields'], ev['kind']
    if kind not in KINDS: sys.exit('not a submission kind: %s' % ev['labels'])
    folder_name, prefix, pts = KINDS[kind]
    year = int((ev['created'] or now())[:4])
    by = field(f, 'Submitted by', 'Name or handle for attribution') or ev['user']
    area = field(f, 'Research area') or 'open'
    meta = dict(kind=kind, submitted_by=by, github=ev['user'], issue=ev['url'], disclosed_utc=ev['created'], accepted_utc=now(), area=area)
    changes = []
    if kind == 'registration':
        sid = '%s-%s' % ('REG', ev['user'])
        c = json.load(open(CONTRIB, encoding='utf-8'))
        e = next((x for x in c if x['handle'] == ev['user']), None)
        if e is None:
            e = dict(handle=ev['user'], name=by, points=0, contributions=[], first=now()[:10]); c.append(e)
        terms = f.get('Terms') or []
        e['registered'] = now()[:10]; e['newsletter'] = any('newsletter' in t for t in terms); e['last'] = now()[:10]
        c.sort(key=lambda x: (-x['points'], x['handle']))
        json.dump(c, open(CONTRIB, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        changes.append('community/contributors.json: %s registered%s' % (ev['user'], ', newsletter invitation to be sent privately' if e['newsletter'] else ''))
        body = ['Accepts #%d (registration) for **%s**.' % (ev['number'], ev['user']), '', 'Changes:'] + ['- ' + c_ for c_ in changes]
        open(os.path.join(outdir, 'pr_body.md'), 'w', encoding='utf-8').write('\n'.join(body) + '\n')
        open(os.path.join(outdir, 'id'), 'w').write(sid)
        return sid
    if kind == 'credentials':
        pros = json.load(open(PROS, encoding='utf-8'))
        sid = next_id('PRO', None, year)
        entry = dict(id=sid, name=field(f, 'Name'), field=field(f, 'Field'), title=field(f, 'Title'), affiliation=field(f, 'Affiliation'),
                     link=field(f, 'ORCID', 'Public profile'), statement=field(f, 'Statement'), github=ev['user'], verified_utc=now()[:10])
        pros.append(entry); json.dump(pros, open(PROS, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
        changes.append('community/professionals.json: %s' % sid)
    else:
        folder = os.path.join(ROOT, 'submissions', folder_name); os.makedirs(folder, exist_ok=True)
        sid = next_id(prefix, folder, year); meta['id'] = sid
        if kind == 'navigation':
            nav = strip_fence(field(f, 'Navigation'))
            meta.update(navigator=field(f, 'Navigator identity'), execution=field(f, 'Execution'), exposure=field(f, 'Context exposure'))
            m = re.search(r'DOMAIN VERBATIM:\s*(.+)', nav); dom = (m.group(1).strip() if m else field(f, 'Domain').strip())
            pv = privacy_of(nav, field(f, 'Privacy')); meta.update(privacy=pv, corpus_opt_in=corpus_opt_in(nav))
            if pv == 'PERSONAL':
                # a redacted-domain record: the domain hash is over the verbatim, so a redacted text would be another
                # domain; the record keeps the computed values and the hash, and publishes no text (Companion 51.1)
                x = cr.navigate(dom); a_, r1, r2 = cr.determine_anchor(x['n1'], x['n2'], x['n3'])[:3]
                meta.update(record_type='redacted-domain', domain='[REDACTED -- personal]', domain_sha256=cr.domain_sha256(dom),
                            n=[x['n1'], x['n2'], x['n3']], anchor=a_, state=[r1 % 9, r2 % 9])
                json.dump(meta, open(os.path.join(folder, sid + '.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
                red = os.path.join(ROOT, 'records', 'congruence', 'redacted.jsonl')
                with open(red, 'a', encoding='utf-8') as fh:
                    fh.write(json.dumps(dict(id=sid, domain_sha256=meta['domain_sha256'], anchor=a_, state=meta['state'],
                                             corpus_opt_in=meta['corpus_opt_in']), ensure_ascii=False) + '\n')
                changes.append('records/congruence/redacted.jsonl: %s (redacted-domain record; not recomputable from the public record)' % sid)
                credit(ev['user'], by, sid, pts)
                changes.append('community/contributors.json: +%d for %s' % (pts, ev['user']))
                body = ['Accepts #%d (%s) as **%s**, a redacted-domain record (PRIVACY: PERSONAL).' % (ev['number'], kind, sid), '', 'Changes:'] + ['- ' + c for c in changes]
                open(os.path.join(outdir, 'pr_body.md'), 'w', encoding='utf-8').write('\n'.join(body) + '\n')
                open(os.path.join(outdir, 'id'), 'w').write(sid)
                return sid
            path = os.path.join(folder, sid + '.txt'); open(path, 'w', encoding='utf-8').write(nav.rstrip('\n') + '\n')
            meta.update(domain=dom, domain_sha256=cr.domain_sha256(dom), sha256=sha(path))
            json.dump(meta, open(os.path.join(folder, sid + '.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
            reg = open(REGISTER, encoding='utf-8').read()
            import adaptors as _ad
            _rt = _ad.route(dom)
            if _rt['route'] == 'ADAPTED':
                _r, _co = _ad.strike(dom)
                with open(os.path.join(ROOT, 'records', 'congruence', 'adapted.jsonl'), 'a', encoding='utf-8') as fh:
                    fh.write(json.dumps(dict(id=sid, domain=dom, domain_sha256=cr.domain_sha256(dom), adaptor=_co['adaptor']['id'], status=_co['adaptor']['status'],
                                             adaptor_sha256=_co['adaptor']['sha256'], n=list(_co['n']), anchor=_co['anchor'], state=list(_co['state'])), ensure_ascii=False) + '\n')
                changes.append('records/congruence/adapted.jsonl: %s (%s, a companion coordinate; L-501)' % (sid, _co['adaptor']['id']))
            elif _rt['route'] != 'CANONICAL':
                changes.append('records/congruence/domains.txt: not entered -- %s (L-501)' % _rt['reason'])
            elif cr.domain_sha256(dom) not in [cr.domain_sha256(l.split('|', 1)[1].strip()) for l in reg.splitlines() if '|' in l and not l.startswith('#') and '@' not in l.split('|', 1)[1]]:
                with open(REGISTER, 'a', encoding='utf-8') as fh: fh.write('%s | %s\n' % (sid, dom))
                pts += 1; changes.append('records/congruence/domains.txt: new domain')
                rc, out = run([sys.executable, 'tools/congruence.py', '--register'])
                open(os.path.join(ROOT, 'records', 'congruence', 'register.txt'), 'w', encoding='utf-8').write(out)
            changes.append(os.path.relpath(path, ROOT))
        else:
            parts = [(k, strip_fence(v) if isinstance(v, str) else ', '.join(v)) for k, v in f.items() if k not in ('Submitted by',)]
            body = '# %s\n\n' % (field(f, 'Title') or ev['title']) + '\n\n'.join('## %s\n\n%s' % (k, v) for k, v in parts if v)
            path = os.path.join(folder, sid + '.md'); open(path, 'w', encoding='utf-8').write(front(meta) + body + '\n')
            changes.append(os.path.relpath(path, ROOT))
            if kind == 'prior-art':
                line = dict(id=sid, title=field(f, 'Title'), contributor=by, area=area, disclosed_utc=ev['created'],
                            accepted_utc=meta['accepted_utc'], path=os.path.relpath(path, ROOT), sha256=sha(path))
                with open(LEDGER, 'a', encoding='utf-8') as fh: fh.write(json.dumps(line, ensure_ascii=False) + '\n')
                changes.append('records/prior_art/ledger.jsonl: %s' % sid)
        credit(ev['user'], by, sid, pts)
        changes.append('community/contributors.json: +%d for %s' % (pts, ev['user']))
    body = ['Accepts #%d (%s) as **%s**.' % (ev['number'], kind, sid), '', 'Changes:'] + ['- ' + c for c in changes]
    body += ['', 'Licence: CC BY 4.0 (text) / Apache-2.0 (code), as agreed in the form. Closes #%d.' % ev['number']]
    open(os.path.join(outdir, 'pr_body.md'), 'w', encoding='utf-8').write('\n'.join(body) + '\n')
    open(os.path.join(outdir, 'id'), 'w').write(sid)
    return sid


def verify_ledger():
    ok = True
    for line in open(LEDGER, encoding='utf-8'):
        if not line.strip(): continue
        e = json.loads(line); p = os.path.join(ROOT, e['path'])
        good = os.path.exists(p) and sha(p) == e['sha256']
        print('%-14s %s' % (e['id'], 'OK' if good else 'MISMATCH')); ok &= good
    print('PRIOR ART LEDGER: %s' % ('PASS' if ok else 'FAIL'))
    return ok


# ---------- selftest ----------------------------------------------------------------------------------------
def selftest():
    global ROOT, LEDGER, CONTRIB, PROS, REGISTER
    ok = True
    def check(label, c):
        nonlocal ok; print('%-60s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    check('a registered adaptor described as still to come is named with its id (Companion 62.5, E03)', any('KO-HANGUL-1' in x for x in stale_claims('Prioritize the development of the Hangul Adaptor next.')) and not stale_claims('The Hangul adaptor counts jamo.'))
    check('a Navigator is read from its identity block or its signature (recurring failures, Companion 58.6)', navigator_of('NAVIGATOR: Claude (Anthropic) PROTOCOL: Omega42') == 'Claude (Anthropic)' and navigator_of('NAVIGATOR: Qwen3.7 (Alibaba Cloud) * V335') == 'Qwen3.7 (Alibaba Cloud)')
    body = '### Submitted by\n\nAda\n\n### Domain\n\nWhat is time?\n\n### Research area\n\n_No response_\n\n### Licence\n\n- [X] I agree\n- [ ] Other'
    f = parse_form(body)
    check('form: values, empty response, checkbox list', f['Submitted by'] == 'Ada' and f['Research area'] == '' and f['Licence'] == ['I agree'])
    check('fenced block is unwrapped', strip_fence('```text\nA\nB\n```') == 'A\nB')
    sample = subprocess.run([sys.executable, 'tools/core_sample.py'], capture_output=True, text=True, cwd=ROOT).stdout
    rep, dom = check_navigation(sample, '')
    check('navigation check finds the domain and the reference coordinate', dom == 'What is the Human Condition?' and 'P6' in rep)
    check('navigation check reports audit, format and coherence', 'Output audit' in rep and 'Format check' in rep and 'COHERENCE' in rep)
    check('a domain already in the record triggers SNCA and SR-CAS', 'SNCA and SR-CAS triggered' in rep)
    check('every reply states the knowledge boundary (L-490)', 'Knowledge boundary' in rep)
    check('unscoped comparative status is reported (L-490 item 4)', 'does not name the comparison' in ''.join(scope_notes('COMPARATIVE STATUS: SUPPORTED\n')))
    check('cumulative wording without a record is reported (L-490 item 5)', 'without a named record' in ''.join(scope_notes('Omega42 now stands at 50 validations.')))
    check('a scoped status and a named record are clear', 'CLEAR' in ''.join(scope_notes('COMPARATIVE STATUS (this comparison only): CONVERGENT\nrecords/congruence/register.txt, version V335, 17 domains')))
    # acceptance in a scratch copy of the record
    saved = (ROOT, LEDGER, CONTRIB, PROS, REGISTER)
    tmp = tempfile.mkdtemp(prefix='o42root_')
    for d in ('scripts', 'tools', 'records', 'community', 'examples', 'docs', 'research'):
        shutil.copytree(os.path.join(saved[0], d), os.path.join(tmp, d))
    os.makedirs(os.path.join(tmp, 'submissions'))
    ROOT = tmp; LEDGER = os.path.join(tmp, 'records', 'prior_art', 'ledger.jsonl'); CONTRIB = os.path.join(tmp, 'community', 'contributors.json')
    PROS = os.path.join(tmp, 'community', 'professionals.json'); REGISTER = os.path.join(tmp, 'records', 'congruence', 'domains.txt')
    open(LEDGER, 'w').close(); json.dump([], open(CONTRIB, 'w')); json.dump([], open(PROS, 'w'))
    ev = dict(number=7, title='[Prior art] A gear', body='', user='ada', created='2026-10-15T08:00:00Z', labels=['submission', 'prior-art'],
              kind='prior-art', url='https://example.invalid/7',
              fields={'Submitted by': 'Ada L.', 'Title': 'A nine-tooth gear', 'Summary': 's', 'Full description': 'd',
                      'How to make and use it': 'm', 'Research area': 'engineering-and-inventions', 'Before you publish': ['a', 'b', 'c', 'd']})
    sid = do_accept(ev, tempfile.mkdtemp())
    led = [json.loads(l) for l in open(LEDGER) if l.strip()]
    check('prior art accepted as PA-2026-0001 and entered in the ledger', sid == 'PA-2026-0001' and led[0]['id'] == sid)
    check('ledger hash verifies', verify_ledger())
    check('contributor credited 3 points', json.load(open(CONTRIB))[0]['points'] == 3)
    nav = dict(ev, number=8, labels=['submission', 'navigation'], kind='navigation',
               fields={'Submitted by': 'Ada L.', 'Navigator identity': 'model-x (Lab)', 'Navigation': sample.replace('What is the Human Condition?', 'What is a bridge?')})
    sid2 = do_accept(nav, tempfile.mkdtemp())
    check('navigation accepted, new domain joins the register (+1)', sid2 == 'NAV-2026-0001' and 'What is a bridge?' in open(REGISTER).read()
          and json.load(open(CONTRIB))[0]['points'] == 5)
    pers = dict(nav, number=9, fields={'Submitted by': 'Ada L.', 'Navigator identity': 'model-x (Lab)',
                'Navigation': 'PRIVACY (L-495): PERSONAL\n' + sample.replace('What is the Human Condition?', 'Should I leave my job in Leeds?')})
    reg_before = open(REGISTER).read()
    sid3 = do_accept(pers, tempfile.mkdtemp())
    red = open(os.path.join(tmp, 'records', 'congruence', 'redacted.jsonl')).read()
    pub = os.listdir(os.path.join(tmp, 'submissions', 'navigations'))
    check('a PERSONAL reading is a redacted-domain record: no text published', sid3 + '.txt' not in pub and sid3 + '.json' in pub
          and 'Leeds' not in open(os.path.join(tmp, 'submissions', 'navigations', sid3 + '.json')).read())
    check('it keeps its hash and state, stays out of the verbatim register and the corpus', sid3 in red and '"corpus_opt_in": false' in red
          and open(REGISTER).read() == reg_before)
    check('the privacy flag is reported at the check', 'Privacy (L-495): PERSONAL' in check_navigation(pers['fields']['Navigation'], '')[0])
    reg = dict(ev, number=10, user='bea', labels=['submission', 'registration'], kind='registration',
               fields={'Name or handle for attribution': 'Bea', 'Terms': ['I agree ...', 'I would like to receive the monthly newsletter.']})
    rid = do_accept(reg, tempfile.mkdtemp())
    bea = next(x for x in json.load(open(CONTRIB)) if x['handle'] == 'bea')
    check('a registration lists the contributor with no submission, newsletter chosen', rid == 'REG-bea' and bea['points'] == 0 and bea['newsletter'] is True)
    ROOT, LEDGER, CONTRIB, PROS, REGISTER = saved
    shutil.rmtree(tmp)
    print('INTAKE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == 'verify-ledger': sys.exit(0 if verify_ledger() else 1)
    if a[0] == 'check': print(do_check(load_event(a[1]), a[2])); sys.exit(0)
    if a[0] == 'accept': print(do_accept(load_event(a[1]), a[2])); sys.exit(0)
    sys.exit('unknown command ' + a[0])
