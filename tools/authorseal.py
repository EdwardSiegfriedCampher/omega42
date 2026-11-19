#!/usr/bin/env python3
"""authorseal.py -- M374 Author Seal (Core Part 3.81): prove how a piece of work was made, draft by draft.

An author seals each draft as the work grows. Every seal records the draft's SHA-256, its size, how it changed from the
previous draft (lines added, removed, kept), the time, and the hash of the seal before it, so the seals form a chain;
each seal is signed with the author's Ed25519 key (OPAL) and carries a readable fingerprint of six positions of the 24.
The log holds hashes and counts only -- never the text -- so it can be shared without sharing the work.

    python3 tools/authorseal.py init LOG --author "NAME"            a new seal log and a new signing key (LOG.key, keep it private)
    python3 tools/authorseal.py seal LOG FILE [--note "TEXT"]       seal the current draft
    python3 tools/authorseal.py verify LOG [--final FILE]           the chain, the signatures, the times; and that FILE is the last draft
    python3 tools/authorseal.py report LOG                          the authorship history, for a reader
    python3 tools/authorseal.py anchor LOG                          the head hash, to publish or send so the log cannot be rewritten later
    python3 tools/authorseal.py --selftest

What a seal shows: that these drafts existed in this order, each derived from the one before by the changes recorded, under
the author's key. What it does not show: who typed them, or that no tool helped -- the clock is the author's own until the
head hash is published somewhere others can see (anchor). A large single insertion is reported as a fact of the history,
never as an accusation. Standard library only, with tools/opal.py for Ed25519.
"""
import difflib, hashlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import opal

PASTE_SHARE = 0.40   # a single seal adding more than this share of the final text's lines (and at least 10 lines) is noted as a large insertion


def sha(b):
    return hashlib.sha256(b).hexdigest()


def body(e):
    return json.dumps({k: e[k] for k in sorted(e) if k not in ('entry_hash', 'signature', 'fingerprint')}, sort_keys=True, separators=(',', ':')).encode('utf-8')


def read_log(log):
    return [json.loads(l) for l in open(log, encoding='utf-8') if l.strip()]


def snap_path(log):
    return log + '.last'          # the private copy of the last sealed draft, used only to count changes


def init(log, author, seed=None, now=None):
    seed = seed or os.urandom(32)
    open(log + '.key', 'wb').write(seed)
    try:
        os.chmod(log + '.key', 0o600)
    except OSError:
        pass
    pub = opal.ed25519_keypair(seed)[1].hex()
    e = dict(index=0, kind='genesis', author=author, public_key=pub, time_utc=now or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), prev='0' * 64)
    return append(log, e, seed, fresh=True)


def append(log, e, seed, fresh=False):
    e['entry_hash'] = sha(body(e))
    e['signature'] = opal.ed25519_sign(seed, body(e)).hex()
    e['fingerprint'] = ' '.join(opal.ods_tokens(opal.ods_digits(bytes.fromhex(e['entry_hash'])))[:6])
    with open(log, 'w' if fresh else 'a', encoding='utf-8') as f:
        f.write(json.dumps(e, ensure_ascii=False) + '\n')
    return e


def seal(log, path, note='', now=None):
    entries = read_log(log); last = entries[-1]
    seed = open(log + '.key', 'rb').read()
    data = open(path, 'rb').read(); text = data.decode('utf-8', errors='replace').splitlines()
    prev_text = open(snap_path(log), encoding='utf-8').read().splitlines() if os.path.exists(snap_path(log)) else []
    added = removed = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=prev_text, b=text, autojunk=False).get_opcodes():
        if tag in ('replace', 'delete'):
            removed += i2 - i1
        if tag in ('replace', 'insert'):
            added += j2 - j1
    e = dict(index=last['index'] + 1, kind='draft', file=os.path.basename(path), draft_sha256=sha(data), bytes=len(data),
             lines=len(text), lines_added=added, lines_removed=removed, lines_kept=len(text) - added,
             time_utc=now or time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), prev=last['entry_hash'], note=note)
    open(snap_path(log), 'w', encoding='utf-8').write('\n'.join(text))
    return append(log, e, seed)


def verify(log, final=None):
    P = []; entries = read_log(log)
    if not entries or entries[0].get('kind') != 'genesis':
        return ['no genesis entry'], entries
    pub = bytes.fromhex(entries[0]['public_key']); prev = '0' * 64; t_prev = ''
    for e in entries:
        if e['prev'] != prev:
            P.append('entry %d: chain broken (prev does not match)' % e['index'])
        if sha(body(e)) != e['entry_hash']:
            P.append('entry %d: contents altered (hash mismatch)' % e['index'])
        if not opal.ed25519_verify(pub, body(e), bytes.fromhex(e['signature'])):
            P.append('entry %d: signature invalid' % e['index'])
        if e['time_utc'] < t_prev:
            P.append('entry %d: time goes backward' % e['index'])
        prev, t_prev = e['entry_hash'], e['time_utc']
    if [e['index'] for e in entries] != list(range(len(entries))):
        P.append('indices not consecutive: an entry was removed or reordered')
    if final is not None and entries[-1].get('draft_sha256') != sha(open(final, 'rb').read()):
        P.append('the final file is not the last sealed draft')
    return P, entries


def report(log):
    P, E = verify(log); drafts = [e for e in E if e['kind'] == 'draft']
    L = ['======= Ω42 AUTHOR SEAL REPORT (M374) =======',
         'AUTHOR (as declared): %s | KEY FINGERPRINT: %s' % (E[0]['author'], ' '.join(opal.ods_tokens(opal.ods_digits(bytes.fromhex(E[0]['public_key'])))[:4])),
         'CHAIN: %s | %d drafts sealed' % ('INTACT' if not P else 'BROKEN -- ' + '; '.join(P), len(drafts))]
    if drafts:
        L.append('SPAN: %s to %s' % (drafts[0]['time_utc'], drafts[-1]['time_utc']))
        final_lines = max(1, drafts[-1]['lines'])
        for d in drafts:
            big = d['lines_added'] / final_lines > PASTE_SHARE and d['lines_added'] >= 10 and d['index'] > 1
            L.append('  draft %-3d %s  %5d lines  +%-4d -%-4d  %s%s%s' % (d['index'], d['time_utc'], d['lines'], d['lines_added'], d['lines_removed'], d['fingerprint'],
                     '  [large single insertion: %d%% of the final text]' % round(100 * d['lines_added'] / final_lines) if big else '', ('  note: ' + d['note']) if d.get('note') else ''))
        L.append('HEAD HASH: %s (publish it to fix the history in time)' % E[-1]['entry_hash'])
    L += ['READING: the drafts existed in this order under this key, each changed from the last as shown. The seal does not',
          'show who typed them or that no tool helped; times are the author\'s own clock until the head hash is anchored.',
          '======= END REPORT =======']
    return '\n'.join(L)


def selftest():
    import tempfile
    d = tempfile.mkdtemp(); log = os.path.join(d, 'essay.seal'); f = os.path.join(d, 'essay.txt')
    init(log, 'Demo Author', seed=bytes(range(32)), now='2026-11-01T08:00:00Z')
    drafts = ['Notes: Fibonacci, the prime 3.',
              'Notes: Fibonacci, the prime 3.\nDraft: the law has period 24 modulo 9.',
              'Title\nDraft: the law has period 24 modulo 9.\nThe norm takes three classes.\nConclusion.']
    times = ['2026-11-01T09:00:00Z', '2026-11-03T14:00:00Z', '2026-11-08T20:00:00Z']
    for t, txt in zip(times, drafts):
        open(f, 'w').write(txt); seal(log, f, now=t)
    open(f, 'a').write('\n' + '\n'.join('pasted line %d' % i for i in range(20))); seal(log, f, note='imported section', now='2026-11-09T10:00:00Z')
    P0, E = verify(log, final=f); rep = report(log)
    lines = open(log, encoding='utf-8').read().splitlines()
    def tampered(mod):
        t = os.path.join(d, 't.seal'); open(t, 'w', encoding='utf-8').write('\n'.join(mod(list(lines))) + '\n'); return verify(t)[0]
    def edit(ls):
        e = json.loads(ls[2]); e['lines_added'] = 0; ls[2] = json.dumps(e); return ls
    def drop(ls):
        return ls[:2] + ls[3:]
    def swap(ls):
        ls[2], ls[3] = ls[3], ls[2]; return ls
    other = os.path.join(d, 'other.txt'); open(other, 'w').write('another text')
    cases = [
        ('a sealed history of four drafts verifies, and the final file is the last draft', not P0 and len(E) == 5),
        ('the log holds hashes and counts, never the text', 'Fibonacci' not in open(log, encoding='utf-8').read()),
        ('an edited entry is detected', any('altered' in p for p in tampered(edit))),
        ('a removed draft is detected', any('chain broken' in p or 'consecutive' in p for p in tampered(drop))),
        ('reordered drafts are detected', bool(tampered(swap))),
        ('a different final file is detected', any('not the last sealed draft' in p for p in verify(log, final=other)[0])),
        ('the report notes a large single insertion as a fact, with the author\'s note', 'large single insertion' in rep and 'imported section' in rep),
        ('the report states what a seal does not show', 'does not' in rep),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('AUTHOR SEAL SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def arg(a, k, default=None):
    return a[a.index(k) + 1] if k in a else default


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['init']:
        e = init(a[1], arg(a, '--author', 'unnamed')); print('Author Seal log %s created; key %s.key (keep it private); genesis %s' % (a[1], a[1], e['fingerprint'])); return 0
    if a[:1] == ['seal']:
        e = seal(a[1], a[2], arg(a, '--note', '')); print('sealed draft %d of %s: +%d -%d lines | %s' % (e['index'], e['file'], e['lines_added'], e['lines_removed'], e['fingerprint'])); return 0
    if a[:1] == ['verify']:
        P, E = verify(a[1], arg(a, '--final')); print('AUTHOR SEAL VERIFY: %s (%d entries)' % ('INTACT' if not P else 'FAIL: ' + '; '.join(P), len(E))); return 0 if not P else 1
    if a[:1] == ['report']:
        print(report(a[1])); return 0
    if a[:1] == ['anchor']:
        E = read_log(a[1]); print('HEAD HASH %s -- publish or send it; any later rewrite of the log will no longer match' % E[-1]['entry_hash']); return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
