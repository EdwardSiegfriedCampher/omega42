#!/usr/bin/env python3
"""provenance.py -- the Open Provenance Law (Core L-547; Companion Part 182): every AI transcript of the protocol's development
is published redacted under a published rule, hashed in a public manifest and linked to the sealed records it produced.

The redaction rule (published with the manifest): e-mail addresses, Google Drive file identifiers and links, session links,
bearer tokens and keys, and every name on a list the Originator supplies are replaced by [REDACTED: kind]. Nothing else is
changed, and the count of each kind is recorded, so a reader knows what was removed and why.
    python3 tools/provenance.py --redact IN OUT --system "MODEL (MAKER)" --date YYYY-MM-DD --records seq_0122,seq_0123 [--names FILE]
                                     # writes the redacted transcript and adds its entry to records/provenance/transcripts.json
    python3 tools/provenance.py --check [DIR]   # every entry well formed, every record it names sealed; with DIR, every hash recomputed
    python3 tools/provenance.py --selftest
Standard library only. The transcripts themselves are published beside the release, not inside the documents.
"""
import hashlib, json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(REPO, 'records', 'provenance', 'transcripts.json')
KEEP_EMAIL = ('noreply@anthropic.com', 'test@example.org')
RULES = [('email', re.compile(r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+')),
         ('drive link', re.compile(r'https?://(?:drive|docs)\.google\.com/\S+')),
         ('drive id', re.compile(r'(?<![\w-])1[A-Za-z0-9_-]{24,43}(?![\w-])')),
         ('session link', re.compile(r'https?://claude\.ai/\S*session_\w+|session_[A-Za-z0-9]{20,}')),
         ('token', re.compile(r'(?i)\b(?:bearer|api[_-]?key|token)[\s:=]+[A-Za-z0-9._-]{16,}'))]
def redact(text, names=()):
    counts = {}
    def sub(kind, rx, t):
        def f(m):
            if kind == 'email' and m.group(0).rstrip('.').lower() in KEEP_EMAIL: return m.group(0)
            if kind == 'drive id' and re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', m.group(0)): return m.group(0)
            counts[kind] = counts.get(kind, 0) + 1; return '[REDACTED: %s]' % kind
        return rx.sub(f, t)
    for kind, rx in RULES: text = sub(kind, rx, text)
    for n in names:
        if n.strip(): text = sub('name', re.compile(re.escape(n.strip()), re.I), text)
    return text, counts
def load():
    if not os.path.exists(MAN): return {'_about': 'The manifest of the published AI transcripts (Core L-547): each redacted transcript by its SHA-256, its system, its date and the sealed records it produced; the redaction rule is the docstring of tools/provenance.py.', 'transcripts': []}
    return json.load(open(MAN, encoding='utf-8'))
def check(d, folder=None):
    P = []
    for e in d['transcripts']:
        for k in ('file', 'sha256', 'system', 'date', 'records', 'redactions'):
            if k not in e: P.append('%s: no %s' % (e.get('file'), k))
        for r in e.get('records', []):
            if not os.path.exists(os.path.join(REPO, 'records', 'instances', r + '.txt')): P.append('%s: record %s is not sealed in the release' % (e.get('file'), r))
        if folder:
            f = os.path.join(folder, e['file'])
            if not os.path.exists(f): P.append('%s: not found in %s' % (e['file'], folder))
            elif hashlib.sha256(open(f, 'rb').read()).hexdigest() != e['sha256']: P.append('%s: hash differs' % e['file'])
    return P
def selftest():
    t, c = redact('mail a@b.org and noreply@anthropic.com, file 1AbCdEfGhIjKlMnOpQrStUvWxYz012345, uuid 11872c17-8422-4881-a7dd-17ae5dc77a10, Jane Roe', ['Jane Roe'])
    T = [('an address is redacted, a kept one is not', '[REDACTED: email]' in t and 'noreply@anthropic.com' in t),
         ('a Drive identifier is redacted, a UUID is not', '[REDACTED: drive id]' in t and '11872c17-8422' in t),
         ('a listed name is redacted', '[REDACTED: name]' in t and 'Jane' not in t),
         ('the counts are kept', c == {'email': 1, 'drive id': 1, 'name': 1}),
         ('the manifest checks', check(load()) == [])]
    for n, ok in T: print('%-48s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('PROVENANCE SELFTEST: %d of %d' % (sum(o for _, o in T), len(T))); return all(o for _, o in T)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--check']:
        P = check(load(), a[1] if len(a) > 1 else None)
        print('OPEN PROVENANCE (L-547): %d transcripts | %s' % (len(load()['transcripts']), 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]
        sys.exit(1 if P else 0)
    if a[:1] == ['--redact']:
        src, out = a[1], a[2]; opt = dict(zip(a[3::2], a[4::2]))
        names = open(opt['--names'], encoding='utf-8').read().split('\n') if '--names' in opt else []
        text, counts = redact(open(src, encoding='utf-8').read(), names)
        open(out, 'w', encoding='utf-8').write(text)
        d = load(); h = hashlib.sha256(open(out, 'rb').read()).hexdigest()
        d['transcripts'] = [e for e in d['transcripts'] if e['file'] != os.path.basename(out)]
        d['transcripts'].append({'file': os.path.basename(out), 'sha256': h, 'bytes': os.path.getsize(out), 'system': opt.get('--system', ''),
                                 'date': opt.get('--date', ''), 'records': [r for r in opt.get('--records', '').split(',') if r], 'redactions': counts})
        os.makedirs(os.path.dirname(MAN), exist_ok=True)
        json.dump(d, open(MAN, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('%s %s %s' % (os.path.basename(out), h, counts)); sys.exit(0)
    print(__doc__); sys.exit(2)
