#!/usr/bin/env python3
"""m267_run.py -- the run kit of the M267 pilot (M267-P1; records/m267_pilot_01/00_freeze.txt; Core Part 3.18).

The freeze fixes the domains, the conditions, the brief, the rater sheet and the analysis. This kit carries them out
without the Builder writing or rating anything. Everything it derives from the sealed key is written to a working folder
OUTSIDE the repository, since the key is open (Core Appendix R.4). Only this tool, its selftest and its frozen hash are in
the record.

    python3 tools/m267_run.py --packets OUT      # 120 writer packets: 2 writers x 20 domains x 3 conditions, in a seeded order
    python3 tools/m267_run.py --sheets READINGS OUT   # once READINGS/<packet>.txt hold all 120 readings: one rater sheet (40 triples)
    python3 tools/m267_run.py --score READINGS RATINGS  # RATINGS/*.csv, one per rater: the frozen analysis
    python3 tools/m267_run.py --selftest         # the analysis on synthetic ratings: a planted effect is DETECTED, none is not

PROCEDURE (as frozen):
  WRITERS. Two Navigators of different architectures (W1, W2), neither the Builder nor the Originator. Each packet is
  pasted ALONE into a FRESH session with memory off, nothing else attached, and the reply saved as READINGS/<packet>.txt.
  RATERS. Three or more people, blind to the conditions and to one another, each given the one sheet from --sheets and
  nothing else, returning a CSV with the columns triple,X,Y,Z,best.
  ANALYSIS. Primary: for each of the 40 (domain, writer) pairs, the mean rater score of CANONICAL against DECOY; one-sided
  sign test, ties excluded; DETECTED if p < 0.05. Secondary: CANONICAL against NONE the same way; the share of "fits best"
  per condition against one third; Kendall's W among raters; the primary comparison in the two strata of Core Part 3.18 (decoy displacement
  delta = 0 or != 0 mod 4); M209 echo of each reading against the coordinate it was written from. No other analysis decides the result. A null result enters the Negative Result Registry.
Standard library only.
"""
import csv, glob, json, math, os, random, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT = os.path.join(ROOT, 'records', 'm267_pilot_01')
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
SEED_PACKETS = 267001          # fixed with this kit, 23 October 2026, before any packet was produced
SEED_SHEET = 267002
WRITERS = ('W1', 'W2')
CONDS = ('CANONICAL', 'DECOY', 'NONE')

def brief():
    return open(os.path.join(PILOT, 'navigator_brief.txt'), encoding='utf8').read()
def key():
    return json.load(open(os.path.join(PILOT, 'key.txt'), encoding='utf8'))['key']
def names():
    import canonical_reference as cr
    return cr.POSITION_NAMES, cr
def canonical_arms(domain):
    N, cr = names(); a = cr.navigate(domain)['anchor']; return a, list(cr.derive_arms(a))
def position_line(anchor, arms):
    N, _ = names()
    lab = ('YANG', 'YIN', '4D', 'ANTIPODE')
    return 'ANCHOR P%d (%s) | ' % (anchor, N[anchor]) + ' | '.join('%s P%d (%s)' % (l, p, N[p]) for l, p in zip(lab, arms))
def plan():
    """[(packet_id, writer, item, condition)] in the seeded order; recomputed from the key, never stored."""
    K = key(); rows = []
    for w in WRITERS:
        cells = [(k['item'], c) for k in K for c in CONDS]
        random.Random(SEED_PACKETS + WRITERS.index(w)).shuffle(cells)
        rows += [('%s-%03d' % (w, i), w, it, c) for i, (it, c) in enumerate(cells, 1)]
    return rows
def packet_text(item, cond):
    k = [x for x in key() if x['item'] == item][0]
    if cond == 'CANONICAL': pos = position_line(*canonical_arms(k['domain']))
    elif cond == 'DECOY': pos = position_line(k['decoy_anchor'], k['decoy_arms'])
    else: pos = 'NONE'
    b = brief()
    b = b.replace('QUESTION: [the domain, exactly]', 'QUESTION: ' + k['domain'])
    b = re.sub(r'POSITION: \[.*\]', 'POSITION: ' + pos, b)
    return b

def write_packets(out):
    os.makedirs(out, exist_ok=True)
    for pid, w, it, c in plan():
        open(os.path.join(out, pid + '.txt'), 'w', encoding='utf8').write(packet_text(it, c))
    open(os.path.join(out, 'README.txt'), 'w', encoding='utf8').write(
        'M267-P1 writer packets. W1-001..W1-060 go to writer 1, W2-001..W2-060 to writer 2 (different architectures).\n'
        'Paste each packet ALONE into a FRESH session with memory off; save the reply, unedited, as <packet>.txt in one folder.\n'
        'Do not tell the writer anything else, and do not share these files with the raters.\n')
    print('wrote %d packets to %s' % (len(plan()), out))

def triples():
    """[(triple_id, item, writer)] in the seeded rater order; T01..T40."""
    K = key(); cells = [(k['item'], w) for k in K for w in WRITERS]
    random.Random(SEED_SHEET).shuffle(cells)
    return [('T%02d' % i, it, w) for i, (it, w) in enumerate(cells, 1)]
def body(t):
    t = t.strip()
    return t
def load_readings(rd):
    got = {}
    for pid, w, it, c in plan():
        p = os.path.join(rd, pid + '.txt')
        if os.path.exists(p): got[(w, it, c)] = body(open(p, encoding='utf8').read())
    return got
def write_sheet(rd, out):
    R = load_readings(rd); missing = len(plan()) - len(R)
    if missing: sys.exit('M267: %d of 120 readings missing; the sheet is made only when all are in' % missing)
    K = {k['item']: k for k in key()}
    L = [open(os.path.join(PILOT, 'rater_sheet.txt'), encoding='utf8').read().split('ITEM |')[0].strip(), '']
    for tid, it, w in triples():
        k = K[it]; slot = {k['slot_canonical']: 'CANONICAL', k['slot_decoy']: 'DECOY', k['slot_none']: 'NONE'}
        L.append('=== %s | QUESTION: %s' % (tid, k['domain']))
        for s in 'XYZ': L += ['--- %s' % s, R[(w, it, slot[s])], '']
    L.append('Return a CSV with one row per triple: triple,X,Y,Z,best   (X, Y, Z from 1 to 7; best one of X, Y, Z)')
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'M267P1_rater_sheet.txt'), 'w', encoding='utf8').write('\n'.join(L))
    print('wrote the rater sheet (40 triples) to %s' % out)

# ---------------------------------------------------------------- the frozen analysis
def binom_tail(n, k):          # P(X >= k), X ~ Binomial(n, 1/2)
    return sum(math.comb(n, i) for i in range(k, n + 1)) / 2 ** n if n else 1.0
def binom_tail_p(n, k, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))
def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]: j += 1
        for t in range(i, j + 1): r[o[t]] = (i + j) / 2 + 1
        i = j + 1
    return r
def kendall_w(M):              # M: raters x objects
    m, n = len(M), len(M[0]); R = [ranks(row) for row in M]
    S = sum((sum(R[a][j] for a in range(m)) - m * (n + 1) / 2) ** 2 for j in range(n))
    T = 0
    for row in M:
        from collections import Counter
        T += sum(t ** 3 - t for t in Counter(row).values())
    d = m * m * (n ** 3 - n) - m * T
    return 12 * S / d if d else float('nan')
def analyse(ratings, readings=None):
    """ratings: {rater: {triple: (X, Y, Z, best)}} -> report lines and the primary decision."""
    K = {k['item']: k for k in key()}; T = triples(); raters = sorted(ratings)
    def cond_scores(tid, it):
        k = K[it]; slot = {k['slot_canonical']: 'CANONICAL', k['slot_decoy']: 'DECOY', k['slot_none']: 'NONE'}
        out = {c: [] for c in CONDS}; best = {c: 0 for c in CONDS}
        for r in raters:
            x = ratings[r][tid]
            for s, v in zip('XYZ', x[:3]): out[slot[s]].append(v)
            best[slot[x[3]]] += 1
        return {c: sum(v) / len(v) for c, v in out.items()}, best
    pairs = [cond_scores(tid, it) for tid, it, w in T]
    def sign(a, b):
        wins = sum(1 for m, _ in pairs if m[a] > m[b]); losses = sum(1 for m, _ in pairs if m[a] < m[b])
        return wins, losses, binom_tail(wins + losses, wins)
    w1, l1, p1 = sign('CANONICAL', 'DECOY'); w2, l2, p2 = sign('CANONICAL', 'NONE')
    tot = len(raters) * len(T); bests = {c: sum(b[c] for _, b in pairs) for c in CONDS}
    order = [(tid, s) for tid, _, _ in T for s in range(3)]
    W = kendall_w([[ratings[r][tid][s] for tid, s in order] for r in raters])
    def strata():
        out = []
        for name, keep in (('delta = 0 mod 4 (Crown pattern kept)', lambda d: d % 4 == 0), ('delta != 0 mod 4', lambda d: d % 4 != 0)):
            sel = [m for (m, _), (tid, it, w) in zip(pairs, T) if keep((K[it]['decoy_anchor'] - canonical_arms(K[it]['domain'])[0]) % 24)]
            wn = sum(1 for m in sel if m['CANONICAL'] > m['DECOY']); ls = sum(1 for m in sel if m['CANONICAL'] < m['DECOY'])
            out.append('%s: %d pairs, canonical higher %d, lower %d, p = %.4f' % (name, len(sel), wn, ls, binom_tail(wn + ls, wn)))
        return out
    L = ['M267-P1 ANALYSIS (frozen 19 October 2026) -- %d raters, %d triples' % (len(raters), len(T)),
         '  PRIMARY  CANONICAL vs DECOY: canonical higher in %d, lower in %d, tied %d; one-sided sign test p = %.4f -> %s' % (
             w1, l1, len(T) - w1 - l1, p1, 'DETECTED' if p1 < 0.05 else 'NOT DETECTED'),
         '  SECONDARY CANONICAL vs NONE: higher in %d, lower in %d, tied %d; p = %.4f' % (w2, l2, len(T) - w2 - l2, p2),
         '  SECONDARY "fits best": ' + ', '.join('%s %d/%d (%.3f)' % (c, bests[c], tot, bests[c] / tot) for c in CONDS) +
         '; canonical above one third: p = %.4f' % binom_tail_p(tot, bests['CANONICAL'], 1 / 3),
         '  SECONDARY Kendall W among raters over the %d readings: %.3f' % (len(order), W)]
    L += ['  STRATA (Core Part 3.18) ' + x for x in strata()]
    if readings:
        _, cr = names(); hits = {c: 0 for c in CONDS}; n = {c: 0 for c in CONDS}
        for (w, it, c), text in readings.items():
            if c == 'NONE': continue
            k = K[it]; a = canonical_arms(k['domain'])[0] if c == 'CANONICAL' else k['decoy_anchor']
            n[c] += 1; hits[c] += int(cr.navigate(text)['anchor'] == a)
        L.append('  SECONDARY M209 echo (the reading\'s own anchor equals the anchor it was written from): CANONICAL %d/%d, DECOY %d/%d; chance about 1/9' % (
            hits['CANONICAL'], n['CANONICAL'], hits['DECOY'], n['DECOY']))
    L.append('  RESULT: the coordinate\'s contribution is %s at this size (DIAGNOSTIC; it grades no premise, L-490)' % ('DETECTED' if p1 < 0.05 else 'NOT DETECTED'))
    return L, p1 < 0.05
def read_ratings(d):
    out = {}
    for f in sorted(glob.glob(os.path.join(d, '*.csv'))):
        rows = {}
        for row in csv.DictReader(open(f, encoding='utf8')):
            rows[row['triple'].strip()] = (int(row['X']), int(row['Y']), int(row['Z']), row['best'].strip().upper())
        out[os.path.basename(f)] = rows
    return out

def synthetic(effect, seed, raters=3):
    """ratings in which CANONICAL is raised by `effect` points; the slots come from the key, as a real sheet's would."""
    rng = random.Random(seed); K = {k['item']: k for k in key()}; out = {}
    for r in range(raters):
        rows = {}
        for tid, it, w in triples():
            k = K[it]; slot = {k['slot_canonical']: 'CANONICAL', k['slot_decoy']: 'DECOY', k['slot_none']: 'NONE'}
            v = {s: max(1, min(7, round(rng.gauss(4, 1.2) + (effect if slot[s] == 'CANONICAL' else 0)))) for s in 'XYZ'}
            rows[tid] = (v['X'], v['Y'], v['Z'], max('XYZ', key=lambda s: (v[s], rng.random())))
        out['rater%d' % r] = rows
    return out
def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-86s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    P = plan()
    check('120 packets: 2 writers x 20 domains x 3 conditions, each cell once per writer', len(P) == 120 and len({(w, i, c) for _, w, i, c in P}) == 120)
    check('the canonical coordinates equal records/m267_pilot_01/compute_output.txt', all(
        ('ANCHOR P%d ' % canonical_arms(k['domain'])[0]) in open(os.path.join(PILOT, 'compute_output.txt'), encoding='utf8').read().split(k['item'])[1].split('\n')[0] for k in key()))
    check('no decoy anchor equals its canonical anchor', all(k['decoy_anchor'] != canonical_arms(k['domain'])[0] for k in key()))
    t = packet_text('M267P1-01', 'NONE')
    check('a NONE packet names no position and keeps the brief\'s words', 'POSITION: NONE' in t and 'QUESTION: What is courage?' in t and 'Takeaway:' in t)
    check('a coordinate packet names anchor and four arms, and never the word canonical or decoy', all(
        'ANCHOR P' in packet_text(it, c) and 'ANTIPODE P' in packet_text(it, c) and not re.search('canonical|decoy', packet_text(it, c), re.I)
        for it, c in (('M267P1-05', 'CANONICAL'), ('M267P1-05', 'DECOY'))))
    check('40 rater triples, each (domain, writer) once', len(triples()) == 40 and len({(i, w) for _, i, w in triples()}) == 40)
    L, det = analyse(synthetic(1.5, 7)); check('a planted effect of 1.5 points is DETECTED', det)
    check('the two strata of Core Part 3.18 cover the 40 pairs', sum(int(re.search(r': (\d+) pairs', x).group(1)) for x in L if 'STRATA' in x) == 40)
    L0, det0 = analyse(synthetic(0.0, 8)); check('no effect is NOT DETECTED', not det0)
    check('Kendall W is 1 for identical raters', abs(kendall_w([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]]) - 1) < 1e-12)
    check('the sign test: 15 of 20 one-sided p = 0.0207', abs(binom_tail(20, 15) - 0.020694) < 1e-5)
    print('M267 RUN KIT SELFTEST: %s' % ('PASS' if ok else 'FAIL')); return ok

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--packets': write_packets(a[1])
    elif a[0] == '--sheets': write_sheet(a[1], a[2])
    elif a[0] == '--score':
        L, _ = analyse(read_ratings(a[2]), load_readings(a[1])); print('\n'.join(L))
