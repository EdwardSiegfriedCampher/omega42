#!/usr/bin/env python3
"""instance_id.py -- the Navigator Instance Identifier (Core L-513, Part 8.1; Companion Part 76).

Two sessions of one AI model carry the same model identifier, so the identifier alone cannot tell them apart. An
INSTANCE is one session of one model, from its first output to its last, and L-513 gives each instance:

  NIID     NI- and the first 16 hex digits of SHA-256 over the canonical issue record
           "model|organization|session|nonce|issued_utc"; the nonce is 128 random bits from outside the model
  ISSUER   SCRIPT (this tool, from the operating system's random source), STRIKER (a nonce the Striker or the Strike
           app gives the session) or SELF (a nonce the model wrote itself; recorded, the weakest standing, since a
           model's own "random" text is neither random nor private to it)
  SEQ      the number of the output within the instance, from 1
  PREV     the OUTPUT ID (tools/output_id.py) of the instance's previous output, or NONE for SEQ 1

The INSTANCE line stands in the Navigator Identity Block, above the signature, so it is covered by the output's own
OUTPUT ID: an output cannot be moved to another instance without its OUTPUT ID changing. The outputs of one
instance form a chain by PREV; two instances of one model have two NIIDs and two chains. The identifier names a
record, not a mind: it shows which outputs belong together and whether a chain was broken or forked; it does not
prove who produced them (L-505), and the nonce is published in the register, since its work is uniqueness, not
secrecy.

Comparison of two or more outputs (--check):
  SAME INSTANCE                one NIID, the chain consistent (SEQ rising by one, each PREV the OUTPUT ID before)
  SAME MODEL, OTHER INSTANCE   one model identifier, two NIIDs
  DIFFERENT MODELS             two model identifiers
  FORK                         one NIID with two outputs at one SEQ, or a PREV that names no output of the chain --
                               a copy, an edit, or another system writing under the instance's identifier
  UNDECLARED                   an output with no INSTANCE line (records before 22 October 2026 are exempt)

Usage:
    python3 tools/instance_id.py --new MODEL ORGANIZATION SESSION [--issuer SCRIPT|STRIKER|SELF] [--nonce HEX] [--issued UTC]
    python3 tools/instance_id.py --line NIID ISSUER ISSUED SEQ PREV     # the INSTANCE line of the Identity Block
    python3 tools/instance_id.py --check OUTPUT.txt [OUTPUT.txt ...]     # same instance, other instance, fork
    python3 tools/instance_id.py --verify-register [records/instances/register.json]
    python3 tools/instance_id.py --selftest
Standard library only.
"""
import datetime, hashlib, json, os, re, secrets, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import output_id as oid

REGISTER = os.path.join(HERE, '..', 'records', 'instances', 'register.json')
ISSUERS = ('SCRIPT', 'STRIKER', 'SELF')
LINE = re.compile(r'^\W*INSTANCE \(L-513\):\s*(NI-[0-9a-f]{16})\s*\|\s*ISSUER:\s*(SCRIPT|STRIKER|SELF)\s*\|\s*ISSUED:\s*(\S+)\s*\|\s*SEQ:\s*(\d+)\s*\|\s*PREV:\s*([0-9a-f]{64}|NONE)\s*$', re.M)
MODEL = re.compile(r'^\W*NAVIGATOR:\s*(.+?)\s+(?:PROTOCOL:|\*)', re.M)   # the Identity Block's line, or the signature


def canon(model, org, session, nonce, issued):
    for f in (model, org, session, nonce, issued):
        if '|' in f or '\n' in f: raise ValueError('a field of the issue record may not contain | or a line break')
    return '%s|%s|%s|%s|%s' % (model.strip(), org.strip(), session.strip(), nonce.strip().lower(), issued.strip())


def niid(model, org, session, nonce, issued):
    return 'NI-' + hashlib.sha256(canon(model, org, session, nonce, issued).encode('utf-8')).hexdigest()[:16]


def new(model, org, session, issuer='SCRIPT', nonce=None, issued=None):
    if issuer not in ISSUERS: raise SystemExit('ISSUER is one of %s' % ', '.join(ISSUERS))
    if issuer == 'SCRIPT':
        if nonce: raise SystemExit('a SCRIPT nonce is drawn by this tool; give --issuer STRIKER or SELF for a supplied one')
        nonce = secrets.token_hex(16)
    elif not nonce or not re.fullmatch(r'[0-9a-fA-F]{16,64}', nonce):
        raise SystemExit('a STRIKER or SELF nonce is 16 to 64 hex digits')
    issued = issued or datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    return dict(niid=niid(model, org, session, nonce, issued), model=model, organization=org, session=session,
                nonce=nonce.lower(), issued_utc=issued, issuer=issuer)


def line(n, issuer, issued, seq, prev):
    return 'INSTANCE (L-513): %s | ISSUER: %s | ISSUED: %s | SEQ: %d | PREV: %s' % (n, issuer, issued, int(seq), prev or 'NONE')


def parse(text):
    m = LINE.search(text); mm = MODEL.search(text)
    rec = dict(model=mm.group(1).strip() if mm else None, output_id=oid.output_id(text),
               declared_id=(re.search(r'^\s*OUTPUT ID:\s*([0-9a-f]{64})', text, re.M) or [None, None])[1])
    if m: rec.update(niid=m.group(1), issuer=m.group(2), issued=m.group(3), seq=int(m.group(4)), prev=None if m.group(5) == 'NONE' else m.group(5))
    return rec


def check(texts, names=None):
    """Group outputs by instance and test each chain; returns (lines, verdict)."""
    names = names or ['output %d' % (i + 1) for i in range(len(texts))]
    recs = [parse(t) for t in texts]; L = []; verdicts = set()
    for nm, r in zip(names, recs):
        if 'niid' not in r:
            L.append('%s: UNDECLARED -- no INSTANCE line (L-513)' % nm); verdicts.add('UNDECLARED'); continue
        ok = r['declared_id'] is None or r['declared_id'] == r['output_id']
        L.append('%s: %s SEQ %d | model %s | OUTPUT ID %s' % (nm, r['niid'], r['seq'], r['model'], 'VERIFIED' if ok and r['declared_id'] else ('MISMATCH' if not ok else 'absent')))
        if not ok: verdicts.add('FORK')
    by = {}
    for nm, r in zip(names, recs):
        if 'niid' in r: by.setdefault(r['niid'], []).append((nm, r))
    for n, items in by.items():
        items.sort(key=lambda x: x[1]['seq']); seqs = [r['seq'] for _, r in items]
        if len(set(seqs)) < len(seqs):
            L.append('%s: FORK -- two outputs at one SEQ' % n); verdicts.add('FORK'); continue
        ids = {r['seq']: r['output_id'] for _, r in items}
        broken = [nm for nm, r in items if r['prev'] and r['seq'] - 1 in ids and ids[r['seq'] - 1] != r['prev']]
        first = [nm for nm, r in items if r['seq'] == 1 and r['prev']]
        if broken or first:
            L.append('%s: FORK -- PREV does not name the previous output (%s)' % (n, ', '.join(broken + first))); verdicts.add('FORK')
        else:
            L.append('%s: chain consistent over SEQ %s' % (n, ', '.join(map(str, seqs))))
    models = {r['model'] for r in recs if 'niid' in r}
    if len(by) == 1 and 'FORK' not in verdicts and 'UNDECLARED' not in verdicts: verdicts.add('SAME INSTANCE')
    elif len(by) > 1 and len(models) == 1: verdicts.add('SAME MODEL, OTHER INSTANCE')
    elif len(models) > 1: verdicts.add('DIFFERENT MODELS')
    order = ('FORK', 'UNDECLARED', 'DIFFERENT MODELS', 'SAME MODEL, OTHER INSTANCE', 'SAME INSTANCE')
    v = ' + '.join(x for x in order if x in verdicts)
    L.append('INSTANCE CHECK (L-513): %s' % v)
    return L, v


def verify_register(path=REGISTER):
    reg = json.load(open(path, encoding='utf-8')); bad = []; seen = set()
    for e in reg['instances']:
        n = niid(e['model'], e['organization'], e['session'], e['nonce'], e['issued_utc'])
        if n != e['niid']: bad.append('%s: recomputes to %s' % (e['niid'], n))
        if e['niid'] in seen: bad.append('%s: registered twice' % e['niid'])
        if e['issuer'] not in ISSUERS: bad.append('%s: unknown issuer %s' % (e['niid'], e['issuer']))
        seen.add(e['niid'])
    print('INSTANCE REGISTER (L-513): %d instances | %s' % (len(reg['instances']), 'PASS' if not bad else 'FAIL'))
    for b in bad: print('  ' + b)
    return not bad


def selftest():
    ok = True
    def chk(label, c):
        nonlocal ok; print('%-66s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    a = new('m-1', 'Org', 'S1', 'STRIKER', '00' * 16, '2026-10-22T00:00:00Z')
    b = new('m-1', 'Org', 'S1', 'STRIKER', '01' + '00' * 15, '2026-10-22T00:00:00Z')
    chk('one model, one session, two nonces: two NIIDs', a['niid'] != b['niid'])
    chk('the NIID recomputes from its issue record', a['niid'] == niid('m-1', 'Org', 'S1', '00' * 16, '2026-10-22T00:00:00Z'))
    s1, s2 = new('m-1', 'Org', 'S1')['nonce'], new('m-1', 'Org', 'S1')['nonce']
    chk('two SCRIPT issues draw two nonces', s1 != s2 and len(s1) == 32)
    def out(n, seq, prev, model='m-1 (Org)', body='Text.'):
        t = 'NAVIGATOR: %s PROTOCOL: Omega42\n%s\n%s\n' % (model, line(n['niid'], n['issuer'], n['issued_utc'], seq, prev), body)
        return t + 'OUTPUT ID: %s\nCAS-YY = -1/2\n' % oid.output_id(t)
    o1 = out(a, 1, None); o2 = out(a, 2, oid.output_id(o1), body='More.')
    chk('a consistent chain is SAME INSTANCE', check([o1, o2])[1] == 'SAME INSTANCE')
    chk('two instances of one model are SAME MODEL, OTHER INSTANCE', check([o1, out(b, 1, None)])[1] == 'SAME MODEL, OTHER INSTANCE')
    chk('a PREV that names no output is a FORK', 'FORK' in check([o1, out(a, 2, 'f' * 64)])[1])
    chk('two outputs at one SEQ are a FORK', 'FORK' in check([o1, out(a, 1, None, body='Other.')])[1])
    chk('an output moved to another instance fails its OUTPUT ID', 'FORK' in check([o1.replace(a['niid'], b['niid'])])[1])
    chk('different models are DIFFERENT MODELS', 'DIFFERENT MODELS' in check([o1, out(b, 1, None, model='m-2 (Other)')])[1])
    chk('an output without the line is UNDECLARED', 'UNDECLARED' in check(['NAVIGATOR: m-1 (Org) PROTOCOL: x\nText.\n'])[1])
    try: new('m', 'o', 's', 'STRIKER', 'xyz'); refused = False
    except SystemExit: refused = True
    chk('a supplied nonce that is not hex is refused', refused)
    print('INSTANCE ID SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--new':
        opt = dict(zip(a[4::2], a[5::2]))
        e = new(a[1], a[2], a[3], opt.get('--issuer', 'SCRIPT'), opt.get('--nonce'), opt.get('--issued'))
        print(json.dumps(e, ensure_ascii=False)); print(line(e['niid'], e['issuer'], e['issued_utc'], 1, None)); sys.exit(0)
    if a[0] == '--line': print(line(a[1], a[2], a[3], a[4], None if a[5] == 'NONE' else a[5])); sys.exit(0)
    if a[0] == '--check':
        L, v = check([open(p, encoding='utf-8').read() for p in a[1:]], a[1:]); print('\n'.join(L)); sys.exit(1 if 'FORK' in v else 0)
    if a[0] == '--verify-register': sys.exit(0 if verify_register(a[1] if len(a) > 1 else REGISTER) else 1)
    print(__doc__); sys.exit(2)
