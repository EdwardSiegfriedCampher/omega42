#!/usr/bin/env python3
"""epr_run.py -- executes the pre-registered tests M279 and M280 exactly as frozen in
records/EPR_M279.txt and records/EPR_M280.txt. It prepares blind session packets from a domain list
chosen by the Striker, seals the key, and scores the raters' returns by the frozen primary tests.
It never changes a pre-registered value: thresholds, chance levels and conditions are read from the
constants below, which restate the EPRs, and --selftest checks the scoring arithmetic.

Usage:
    python3 tools/epr_run.py prepare M279|M280 DOMAINS.txt OUTDIR
        DOMAINS.txt: one verbatim domain per line, exactly 20, frozen by the Striker. Writes
        OUTDIR/freeze.txt (each DOMAIN SHA-256 and the list's SHA-256), OUTDIR/sessions/*.txt (one
        packet per fresh session), OUTDIR/key.json (sealed: not shown to authors or raters) and
        OUTDIR/rater_sheet.csv (blank, one row per item to rate).
    python3 tools/epr_run.py score M279|M280 OUTDIR/key.json RATINGS.csv
    python3 tools/epr_run.py --selftest
Ratings: M279 rows  domain_id,rater,choice           (choice one of W X Y Z: the reading judged Omega42)
         M280 rows  domain_id,rater,label,relation,verdict   (label X or Y; relation dependency,
                    suppression, trajectory or completion; verdict MATCH, PARTIAL or DIFFERENT)
Results are reported separately as discriminative validity (Core Part 0.6.9) and never combined.
"""
import csv, hashlib, json, os, random, sys
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))

FROZEN = {
    'M279': dict(record='records/EPR_M279.txt', domains=20, chance=0.25, success_at=10,
                 grounds=('A', 'B', 'C', 'D'), letters=('W', 'X', 'Y', 'Z')),
    'M280': dict(record='records/EPR_M280.txt', domains=20, chance=0.5, success_at=15,
                 conditions=('FULL', 'RECOVERABLE', 'NON_RECOVERABLE')),
}
RELATIONS = ('dependency', 'suppression', 'trajectory', 'completion')
VERDICT = {'MATCH': 1.0, 'PARTIAL': 0.5, 'DIFFERENT': 0.0}
ROLES = 'Anchor: what the question is; Yang: what it depends on; Yin: what it holds out of view; ' \
        '4D: where it is heading; Antipode: what completes it.'

def binom_tail(n, k, p):
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

def sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_domains(path, n):
    doms = [ln.rstrip('\n') for ln in open(path, encoding='utf-8') if ln.strip()]
    if len(doms) != n:
        sys.exit('EPR requires exactly %d domains; %d given.' % (n, len(doms)))
    return doms

def prepare(exp, dom_path, out):
    import canonical_reference as cr
    import ground_challenge as gc
    F = FROZEN[exp]
    doms = load_domains(dom_path, F['domains'])
    exposed = [d for d in doms if cr.is_exposed(d)]
    if exposed:
        sys.exit('Exposed domains are excluded by the EPR: %s' % exposed)
    list_hash = sha('\n'.join(doms))
    rng = random.Random(int(list_hash, 16))          # seeded by the frozen list: reproducible, not chosen
    os.makedirs(os.path.join(out, 'sessions'), exist_ok=True)
    key = dict(experiment=exp, epr=F['record'], domain_list_sha256=list_hash, sessions={}, display={})
    freeze = ['FREEZE -- %s domain list | list SHA-256 %s' % (exp, list_hash)]
    sheet = []
    for k, d in enumerate(doms, 1):
        did = 'D%02d' % k
        freeze.append('%s  %s  %s' % (did, cr.domain_sha256(d), d))
        anchor = cr.navigate(d)['anchor']
        if exp == 'M279':
            arms = {g: row for g, _, _, row in gc.ground_arms(anchor)}
            order = list(F['grounds']); rng.shuffle(order)
            key['display'][did] = dict(zip(F['letters'], order))
            for g in F['grounds']:
                sid = 'S%s' % sha(list_hash + did + g)[:10]
                key['sessions'][sid] = dict(domain_id=did, ground=g)
                vals = ' | '.join('%s = %d' % (name, v) for name, _, v in arms[g])
                packet = ['SESSION %s -- one packet, fresh session (L-442)' % sid,
                          'DOMAIN (verbatim): %s' % d, 'COORDINATE VALUES: %s' % vals, 'ROLES: %s' % ROLES,
                          'TASK: write the complete reading of the domain from these values and roles. '
                          'Declare CONTEXT EXPOSURE. Do not consult other readings of this domain.']
                open(os.path.join(out, 'sessions', sid + '.txt'), 'w').write('\n'.join(packet) + '\n')
            sheet.append([did, '', ''])
        else:
            r6 = gc.r6_packets(anchor)
            order = ['RECOVERABLE', 'NON_RECOVERABLE']; rng.shuffle(order)
            key['display'][did] = dict(zip(('X', 'Y'), order))
            for cond in F['conditions']:
                sid = 'S%s' % sha(list_hash + did + cond)[:10]
                key['sessions'][sid] = dict(domain_id=did, condition=cond)
                if cond == 'FULL':
                    body = 'COORDINATE (24 values from the anchor): %s' % r6['FULL']
                elif cond == 'RECOVERABLE':
                    v = r6['RECOVERABLE']['values']
                    body = ('FRAGMENT: anchor value %d and Yang value %d, separation 5, on the canonical orbit. '
                            'Rebuild the 24-cycle with the law and report it before navigating.' % v)
                else:
                    v = r6['NON_RECOVERABLE']['values']
                    body = ('FRAGMENT: anchor value %d and Antipode value %d, separation 12, on the canonical orbit; '
                            '%d candidate phases remain.' % (v[0], v[1], r6['NON_RECOVERABLE']['on_canonical_orbit']))
                packet = ['SESSION %s -- one packet, fresh session (L-442)' % sid, 'DOMAIN (verbatim): %s' % d, body,
                          'LAW: x(n+2) = x(n+1) + x(n) mod 9', 'ROLES: %s' % ROLES,
                          'TASK: write the complete reading. Declare CONTEXT EXPOSURE.']
                open(os.path.join(out, 'sessions', sid + '.txt'), 'w').write('\n'.join(packet) + '\n')
            for lab in ('X', 'Y'):
                for rel in RELATIONS:
                    sheet.append([did, '', lab, rel, ''])
    open(os.path.join(out, 'freeze.txt'), 'w').write('\n'.join(freeze) + '\n')
    json.dump(key, open(os.path.join(out, 'key.json'), 'w'), indent=1)
    with open(os.path.join(out, 'rater_sheet.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['domain_id', 'rater', 'choice'] if exp == 'M279' else ['domain_id', 'rater', 'label', 'relation', 'verdict'])
        w.writerows(sheet)
    print('%s prepared: %d domains, %d sessions, list SHA-256 %s' % (exp, len(doms), len(key['sessions']), list_hash))

def score(exp, key, rows):
    F = FROZEN[exp]
    out = dict(experiment=exp, outcome='DISCRIMINATIVE VALIDITY (Core Part 0.6.9)')
    if exp == 'M279':
        votes = {}
        for r in rows:
            votes.setdefault(r['domain_id'], []).append(r['choice'].strip().upper())
        correct = 0
        for did, vs in votes.items():
            counts = {c: vs.count(c) for c in set(vs)}
            top = max(counts.values())
            winners = [c for c, n in counts.items() if n == top]
            if len(winners) == 1 and key['display'][did][winners[0]] == 'A':
                correct += 1                     # ties count as a miss (EPR-09)
        n = F['domains']
        out.update(domains_scored=len(votes), correct=correct, chance=F['chance'],
                   p_one_sided=round(binom_tail(n, correct, F['chance']), 4),
                   success=correct >= F['success_at'], threshold='%d of %d' % (F['success_at'], n))
    else:
        s = {}
        for r in rows:
            cond = key['display'][r['domain_id']][r['label'].strip().upper()]
            s.setdefault((r['domain_id'], cond), []).append(VERDICT[r['verdict'].strip().upper()])
        dids = sorted({d for d, _ in s})
        pos = 0
        diffs = {}
        for did in dids:
            sr = sum(s[(did, 'RECOVERABLE')]) / len(s[(did, 'RECOVERABLE')])
            sn = sum(s[(did, 'NON_RECOVERABLE')]) / len(s[(did, 'NON_RECOVERABLE')])
            diffs[did] = round(sr - sn, 4)
            pos += sr - sn > 0                   # ties count as failures (EPR-09)
        n = F['domains']
        out.update(domains_scored=len(dids), positive_d=pos, d=diffs,
                   p_one_sided=round(binom_tail(n, pos, F['chance']), 4),
                   success=pos >= F['success_at'], threshold='%d of %d' % (F['success_at'], n))
    out['status'] = 'DIAGNOSTIC until reproduced (EPR-13, L-419)'
    return out

def selftest():
    ok = []
    def check(name, cond):
        ok.append(cond); print('%-66s %s' % (name, 'ok' if cond else 'FAIL'))
    check('M279 threshold p(X>=10 | 20, 0.25) = 0.0139', round(binom_tail(20, 10, 0.25), 4) == 0.0139)
    check('M280 threshold p(X>=15 | 20, 0.5) = 0.0207', round(binom_tail(20, 15, 0.5), 4) == 0.0207)
    key = dict(display={'D%02d' % k: dict(W='A', X='B', Y='C', Z='D') for k in range(1, 21)})
    perfect = [dict(domain_id='D%02d' % k, rater=r, choice='W') for k in range(1, 21) for r in 'abc']
    check('M279 perfect raters: 20 of 20, success', score('M279', key, perfect)['success'])
    tie = [dict(domain_id='D%02d' % k, rater=r, choice=c) for k in range(1, 21) for r, c in zip('abc', 'WXY')]
    check('M279 three-way ties count as misses: 0 correct', score('M279', key, tie)['correct'] == 0)
    key2 = dict(display={'D%02d' % k: dict(X='RECOVERABLE', Y='NON_RECOVERABLE') for k in range(1, 21)})
    good = [dict(domain_id='D%02d' % k, rater=r, label=l, relation=rel, verdict='MATCH' if l == 'X' else 'DIFFERENT')
            for k in range(1, 21) for r in 'abc' for l in 'XY' for rel in RELATIONS]
    res = score('M280', key2, good)
    check('M280 recoverable closer on every domain: 20 positive, success', res['positive_d'] == 20 and res['success'])
    flat = [dict(g, verdict='PARTIAL') for g in good]
    check('M280 equal similarity: ties count as failures, no success', not score('M280', key2, flat)['success'])
    print('EPR RUNNER SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    if len(a) == 4 and a[0] == 'prepare':
        prepare(a[1], a[2], a[3])
    elif len(a) == 4 and a[0] == 'score':
        key = json.load(open(a[2]))
        rows = list(csv.DictReader(open(a[3], newline='')))
        print(json.dumps(score(a[1], key, rows), indent=1))
    else:
        print(__doc__)
