#!/usr/bin/env python3
"""framework_compare.py -- M309 computed layer (Core Part 3.36): frozen statement atlases of philosophical or
metaphysical frameworks struck with canonical_reference.py and compared with one another on the same measures, each
against its own null model (statements whose residues are drawn uniformly, the same number of statements).

Measures for an atlas of k statements:
  COVERAGE   how many of the four orbits longer than one state its states reach (Voice A, B, C, Wheel)
  HOME       statements whose state lies on the canonical cycle (Voice C, the orbit of (2, 5))
  SEEDS      statements standing exactly on the seed of an orbit ((0,0), (3,3), (1,1), (1,3), (2,5))
  LINKS      ordered pairs (i, j), i != j, in which statement i rests on (Yang) the place where statement j stands
  MIRRORS    unordered pairs whose states are each other's negative (s and -s: twelve steps apart on one orbit)
  ANCHORS    distinct anchors among P1-P9
Each measure is reported with P(null >= observed), by Monte Carlo over 200000 random atlases of the same size, and
beside it (E13, adopted 22 October 2026) with the CONDITIONED chance: the same Monte Carlo with each statement's r1 held
at the value its own content-word count gives (r1 = dr(5 n1)) and only r2 and r3 drawn, since a short statement's r1 is
fixed by its word count and the uniform null overstates how rare its placement is. Every statement line also carries
its conditioned rates: its state, (r1, r2), has chance 1/9 given n1 (1/81 uniform), and its anchor 73/81 when it is r1
(the anchor is r1 unless r2 = r3 differ from it) and 1/81 otherwise (1/9 uniform).

Usage:
    python3 tools/framework_compare.py records/frameworks/*.txt     # Bashar is read from tools/bashar_lens.py
    python3 tools/framework_compare.py --freeze-roles ATLAS "ANCHOR=TAG" "YANG=TAG" "YIN=TAG" "4D=TAG" "ANTIPODE=TAG"
                                       # M309 step 2: the five assignments frozen with their hash BEFORE the atlas is
                                       # struck (step 5), so that the assignment is blind to the computed layer
    python3 tools/framework_compare.py --verify-roles SHA ATLAS "ANCHOR=TAG" ...   # the same five, checked against the hash
    python3 tools/framework_compare.py --verify-record records/frameworks/role_assignments.txt   # every frozen assignment recomputed
    python3 tools/framework_compare.py --selftest
"""
import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canonical_reference as cr
import bashar_lens as bl

NAMES = cr.POSITION_NAMES
SEEDS = {s for _, s in bl.SEEDS}
LONG = ('Voice A', 'Voice B', 'Voice C', 'Wheel')


def load(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or '|' not in line: continue
        tag, text = [x.strip() for x in line.split('|', 1)]
        rows.append((tag, text))
    return os.path.splitext(os.path.basename(path))[0].upper(), rows


def sig_from_n(n1, n2, n3):
    a, r1, r2, r3, tfi = cr.determine_anchor(n1, n2, n3)
    f = bl.frequency(r1, r2)
    return dict(anchor=a, yang=(a + 5) % 24, state=f['state'], voice=f['voice'], r1=r1, n1=n1)


def strike(text):
    x = cr.navigate(text)
    return sig_from_n(x['n1'], x['n2'], x['n3'])


def measures(sigs):
    k = len(sigs)
    m = {}
    m['COVERAGE'] = len({s['voice'] for s in sigs} & set(LONG))
    m['HOME'] = sum(s['voice'] == 'Voice C' for s in sigs)
    m['SEEDS'] = sum(s['state'] in SEEDS for s in sigs)
    m['LINKS'] = sum(1 for i in range(k) for j in range(k) if i != j and sigs[i]['yang'] == sigs[j]['anchor'])
    neg = lambda st: ((-st[0]) % 9, (-st[1]) % 9)
    m['MIRRORS'] = sum(1 for i in range(k) for j in range(i + 1, k) if sigs[i]['state'] == neg(sigs[j]['state']) and sigs[i]['state'] != (0, 0))
    m['ANCHORS'] = len({s['anchor'] for s in sigs})
    return m


_POOL = None
def pool():
    global _POOL
    if _POOL is None:
        _POOL = [sig_from_n(a, b, c) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
    return _POOL


def null_p(k, observed, trials=200000, seed=42):
    rng = random.Random(seed + k); P = pool(); ge = {key: 0 for key in observed}
    for _ in range(trials):
        m = measures([rng.choice(P) for _ in range(k)])
        for key, v in observed.items():
            ge[key] += m[key] >= v
    return {key: ge[key] / trials for key in observed}


def cond_null_p(r1s, observed, trials=200000, seed=4242):
    """E13: the null with each statement's r1 held (its word count fixes it) and r2, r3 drawn uniformly."""
    rng = random.Random(seed + len(r1s)); by = {}
    for s in pool(): by.setdefault(s['r1'], []).append(s)
    ge = {key: 0 for key in observed}
    for _ in range(trials):
        m = measures([rng.choice(by[r]) for r in r1s])
        for key, v in observed.items():
            ge[key] += m[key] >= v
    return {key: ge[key] / trials for key in observed}


def e13_rates(s):
    """E13 per statement: (state chance, anchor chance) given n1, as exact fractions."""
    return '1/9', ('73/81' if s['anchor'] == s['r1'] else '1/81')


def report(name, rows):
    sigs = [strike(t) for _, t in rows]
    m = measures(sigs); p = null_p(len(rows), m); pc = cond_null_p([s['r1'] for s in sigs], m)
    L = ['=== %s (%d statements) ===' % (name, len(rows))]
    for (tag, t), s in zip(rows, sigs):
        sc, ac = e13_rates(s)
        L.append('  %-14s | %-56s | P%-2d %-12s | state %s %s%s | E13 n1 %d: state %s, anchor %s' % (tag, t, s['anchor'], NAMES[s['anchor']], s['state'], s['voice'],
                 ' | SEED' if s['state'] in SEEDS else '', s['n1'], sc, ac))
    k = len(rows)
    links = ['%s rests on %s' % (rows[i][0], rows[j][0]) for i in range(k) for j in range(k) if i != j and sigs[i]['yang'] == sigs[j]['anchor']]
    L.append('  LINKS: ' + ('; '.join(links) or 'none'))
    for key in ('COVERAGE', 'HOME', 'SEEDS', 'LINKS', 'MIRRORS', 'ANCHORS'):
        L.append('  %-9s %3d   P(null >= observed) = %.3f | given word counts (E13) = %.3f' % (key, m[key], p[key], pc[key]))
    return '\n'.join(L), m, p, pc


ROLES = ('ANCHOR', 'YANG', 'YIN', '4D', 'ANTIPODE')


def roles_sha(atlas, pairs):
    """M309 step 2 freeze: the five roles, each with one statement of the atlas, none used twice; the hash covers the
    atlas file and the assignments, so neither can change after the freeze without the hash changing."""
    import hashlib
    _, rows = load(atlas); tags = {tag for tag, _ in rows}
    got = {}
    for p in pairs:
        if '=' not in p: raise SystemExit('ROLE=TAG expected: %s' % p)
        r, tag = [x.strip() for x in p.split('=', 1)]
        r = r.upper()
        if r not in ROLES: raise SystemExit('unknown role %s (the five are %s)' % (r, ', '.join(ROLES)))
        if tag not in tags: raise SystemExit('%s is not a statement of %s' % (tag, atlas))
        if r in got: raise SystemExit('role %s assigned twice' % r)
        got[r] = tag
    if set(got) != set(ROLES): raise SystemExit('all five roles are assigned, each once (M309 step 2); missing: %s' % ', '.join(r for r in ROLES if r not in got))
    if len(set(got.values())) != 5: raise SystemExit('no statement fills two roles (M309 step 2)')
    h = hashlib.sha256(open(atlas, 'rb').read()).hexdigest()
    canon = h + '\n' + '\n'.join('%s=%s' % (r, got[r]) for r in ROLES)
    return hashlib.sha256(canon.encode('utf-8')).hexdigest(), got, h


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-60s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    s = strike('Everything is here and now.')
    check('Bashar Law 2 strikes to P6, state (6, 4), Voice A', s['anchor'] == 6 and s['state'] == (6, 4) and s['voice'] == 'Voice A')
    m = measures([strike(t) for t in bl.LAWS])
    check('five laws: coverage 4, home 1, seeds 1, links 2', (m['COVERAGE'], m['HOME'], m['SEEDS'], m['LINKS']) == (4, 1, 1, 2))
    check('pool holds the 729 residue triples', len(pool()) == 729)
    p = null_p(5, m, trials=20000)
    check('null probabilities lie in [0, 1]', all(0 <= v <= 1 for v in p.values()))
    sg = [strike(t) for t in bl.LAWS]
    pc = cond_null_p([x['r1'] for x in sg], m, trials=20000)
    check('E13: conditioned probabilities lie in [0, 1]', all(0 <= v <= 1 for v in pc.values()))
    by = {}
    for x in pool(): by.setdefault(x['r1'], []).append(x)
    check('E13: 81 residue triples for each r1', sorted(len(v) for v in by.values()) == [81] * 9)
    check('E13: given r1, the anchor is r1 in 73 of 81 triples', all(sum(x['anchor'] == r for x in v) == 73 for r, v in by.items()))
    check('E13: given r1, each state (r1, r2) holds 9 of 81 triples', all(sum(x['state'] == (r % 9, k % 9) for x in v) == 9 for r, v in by.items() for k in range(1, 10)))
    one = [strike('That which hath been is that which shall be')]
    check('E13: the APE-131 case -- four content words, state (2, 5) at 1/9 given n1', one[0]['n1'] == 4 and one[0]['state'] == (2, 5) and e13_rates(one[0])[0] == '1/9')
    import tempfile
    f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False); f.write('# t\nA 1 | One.\nA 2 | Two.\nA 3 | Three.\nA 4 | Four.\nA 5 | Five.\nA 6 | Six.\n'); f.close()
    five = ['ANCHOR=A 1', 'YANG=A 2', 'YIN=A 3', '4D=A 4', 'ANTIPODE=A 5']
    h1 = roles_sha(f.name, five)[0]
    check('role freeze: same five, same hash, in any order', roles_sha(f.name, list(reversed(five)))[0] == h1)
    check('role freeze: a changed assignment changes the hash', roles_sha(f.name, five[:4] + ['ANTIPODE=A 6'])[0] != h1)
    def refused(pairs):
        try: roles_sha(f.name, pairs); return False
        except SystemExit: return True
    check('role freeze: four roles are refused', refused(five[:4]))
    check('role freeze: one statement in two roles is refused', refused(five[:4] + ['ANTIPODE=A 1']))
    check('role freeze: a tag not in the atlas is refused', refused(five[:4] + ['ANTIPODE=Z 9']))
    os.unlink(f.name)
    print('FRAMEWORK COMPARE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--freeze-roles':
        h, got, ah = roles_sha(a[1], a[2:])
        print('ROLES FROZEN (M309 step 2): %s | ATLAS SHA-256: %s | ROLES SHA-256: %s -- record the time (date -u) before the atlas is struck' % (' | '.join('%s %s' % (r, got[r]) for r in ROLES), ah, h)); sys.exit(0)
    if a[0] == '--verify-record':
        import re
        bad = 0; n = 0
        for line in open(a[1], encoding='utf-8'):
            if line.startswith('#') or not line.strip(): continue
            m = re.search(r'ROLES FROZEN \(M309 step 2\): (.*?) \| ATLAS SHA-256: ([0-9a-f]{64}) \| ROLES SHA-256: ([0-9a-f]{64})', line)
            atlas = re.search(r'records/frameworks/\S+\.txt', line)
            nav = line.split('|')[0].strip()
            # the atlas is found by the tag of its statements (CHR, ISL, NEO ...), read from every frozen atlas
            prefix = m.group(1).split(' | ')[0].split(' ')[1]
            fdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'records', 'frameworks')
            cands = [os.path.join(fdir, f) for f in sorted(os.listdir(fdir)) if f.endswith('.txt') and 'frozen' in open(os.path.join(fdir, f), encoding='utf-8').readline() and 'atlas' in open(os.path.join(fdir, f), encoding='utf-8').readline() and any(tg.split(' ')[0] == prefix for tg, _ in load(os.path.join(fdir, f))[1])]
            path = atlas.group(0) if atlas else (cands[0] if len(cands) == 1 else None)
            if path is None: print('%s: atlas for tag %s not found uniquely' % (nav, prefix)); bad += 1; n += 1; continue
            pairs = []
            for part in m.group(1).split(' | '):
                r, tag = part.split(' ', 1); pairs.append('%s=%s' % (r, tag))
            h, _, ah = roles_sha(path, pairs); n += 1
            ok = h == m.group(3) and ah == m.group(2); bad += not ok
            print('%s %s' % (nav, 'VERIFIED' if ok else 'MISMATCH'))
        print('ROLE RECORD (M309 step 2): %d entries | %s' % (n, 'PASS' if not bad else 'FAIL')); sys.exit(1 if bad else 0)
    if a[0] == '--verify-roles':
        h = roles_sha(a[2], a[3:])[0]
        print('ROLES: %s' % ('VERIFIED' if h == a[1].lower() else 'MISMATCH -- the assignments or the atlas differ from the freeze')); sys.exit(0 if h == a[1].lower() else 1)
    sets = [('BASHAR (atlas of M308)', [(r[0], r[1]) for r in bl.ATLAS]), ('BASHAR FIVE LAWS', [('LAW %d' % (i + 1), t) for i, t in enumerate(bl.LAWS)])]
    sets += [load(p) for p in a]
    for name, rows in sets:
        print(report(name, rows)[0]); print()
