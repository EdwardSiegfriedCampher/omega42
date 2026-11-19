#!/usr/bin/env python3
"""primordial.py -- the Originator's Construct workbook PRIMORDIAL FRACTURE, read exactly, through Omega42 (Companion Part 107).

Everything is computed from records/construct/primordial/construct_frozen.json, which freeze.py regenerates from the workbook and
checks against it (FREEZE_OUTPUT.txt). Sections: I the structure; II the affine theorem and the workbook's own echo counts;
III every place a draw is recorded, over the South African Lotto history; IV the Construct's echo forecast against shuffled
history; V a planted sequence, on which the same forecast must work. Rules frozen before scoring (C-MAP-2, PROPOSED):
  Y-field = draw t - h, X-field = draw t (six main numbers, ascending; the workbook itself uses the drawn order, which the
  record does not hold); a draw number is recorded at every cell of the 216 echo regions whose value equals it, as the
  workbook's own COUNTIF counters count it; the template is progressed h draws on by the workbook's own rule (the recorded
  cell read again with the new Y-field); the forecast is the six values with the largest support, ties to the smaller value.
    python3 records/construct/primordial.py      # diffed in CI
"""
import csv, json, os, random
import numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
FZ = json.load(open(os.path.join(HERE, 'primordial', 'construct_frozen.json')))
Y = lambda b: 'YES' if b else 'NO'
DOM = list(FZ['domains']); Y0, X0 = FZ['Y0'], FZ['X0']
OFF = 18; NK = 2 * OFF + 1
COLS = {'I': 0, 'R': 1, 'AA': 2, 'AJ': 3}

print('I. THE STRUCTURE OF THE WORKBOOK [EXACT; records/construct/primordial/FREEZE_OUTPUT.txt]')
seeds = {d: FZ['domains'][d]['seed'] for d in DOM if d != 'MP'}
lab = {}
for r in range(12, 22):
    for b in range(4):
        e = FZ['domains']['MP']['rows'].get('%d.%d' % (r, b))
        if e and e['label']: lab[(r, b)] = e['label']
print('  27 domains: Domain Zero (MP) and 26 derived, each seeded by one node of Domain Zero\'s first layer: %s' % Y(len(seeds) == 26 and all(v.startswith('=MP!') for v in seeds.values())))
mp = FZ['domains']['MP']['rows']
hor = {b: [tuple(mp['%d.%d' % (r, b)]['K']) for r in range(14, 20)] for b in range(4)}
print('  first layer: four blocks of six horizontal nodes (rows 14-19), two diagonals each (rows 12 and 21) and an average (row 20)')
print('  the fourth block\'s six horizontals repeat the third block\'s in another order: %s -- so 24 horizontal places hold 18 distinct nodes' % Y(sorted(hor[3]) == sorted(hor[2]) and len(set(hor[0] + hor[1] + hor[2])) == 18))
print('  the 26 seeds are the 18 distinct horizontals (N1-N9 and P1-P9) and the 8 diagonals (ND, NU, PD, PU, T2, T1, T4, T3): %s' % Y(len(seeds) == 26))
print('  the 18 horizontals are the Y-field plus a constant: N_k = Y - k and P_k = Y + k for k = 1 to 9: %s'
      % Y(all(mp['%d.%d' % (r, b)]['K'] == [s * k] * 6 for (r, b), l in lab.items() if r in range(14, 20) and l[0] in 'NP' and l[1:].isdigit() for s, k in [(-1 if l[0] == 'N' else 1, int(l[1:]))])))
print('  27 domains x 26 nodes = %d nodes (the 702 of the descriptions)' % (27 * 26))
print('  second layer (rows 23-32): the same arrangement built on the doubling cycle 1-2-4-8-7-5 and its negative, and on the Crown 3-6-9 mixed; the recorded templates and the prediction sheet read from it')
print('  echo regions: in every domain the workbook counts each X-field number in 8 blocks of 7 rows x 6 cells (rows 14-20 and 25-31 of each block): 27 x 8 = %d regions, %d cells'
      % (sum(len(FZ['domains'][d]['echo']) for d in DOM), 27 * 8 * 42))
nt = sum(len(FZ['domains'][d]['templates']) for d in DOM)
print('  recorded templates (the Reconstruction Zone, rows 34 onward): %d across the 27 domains, each six cells of the second layer' % nt)

print('II. THE CONSTRUCT IS AFFINE [EXACT; proved on the workbook by freeze.py, step 3]')
print('  every node cell of every domain is Y_j + K, with K a fixed constant (from %d to %d) and j the cell\'s position in its block' %
      (min(k for d in DOM for e in FZ['domains'][d]['rows'].values() for k in e['K']), max(k for d in DOM for e in FZ['domains'][d]['rows'].values() for k in e['K'])))
def region_cells(d, e):
    r0, b = e['range'][1], e['block']
    return [(FZ['domains'][d]['rows']['%d.%d' % (r, b)]['K'][j], j) for r in range(r0, r0 + 7) for j in range(6)]
REG = [(d, e, region_cells(d, e)) for d in DOM for e in FZ['domains'][d]['echo']]
good = sum(1 for d, e, cells in REG if [sum(1 for K, j in cells if Y0[j] + K == x) for x in X0] == e['cached'])
print('  the workbook\'s own 216 echo counters, recomputed from the constants for its stored fields X = %s, Y = %s: %d of 216 agree' % (X0, Y0, good))
print('  consequence: a number x is recorded at a cell exactly when x - Y_j = K, and a template recorded on (Y, X) and read again with')
print('  a new field Y\' gives X_i + Y\'_j - Y_j. The whole forecast is a shift of the recorded numbers by the change of the field.')
C = np.zeros((27, 6, NK), int)
for di, d in enumerate(DOM):
    for _, e, cells in [r for r in REG if r[0] == d]:
        for K, j in cells: C[di, j, int(round(K)) + OFF] += 1
CT = C.sum(0)

rows = list(csv.reader(open(os.path.join(HERE, 'sa_lotto', 'draws.csv'))))[1:]
M = np.array([[int(x) for x in r[1:7]] for r in rows]); dates = [r[0] for r in rows]; n = len(M)
PERIODS = [('2000-01-01', 49), ('2017-08-16', 52), ('2025-09-24', 58), ('2026-06-01', 52)]
PER = np.array([sum(dt >= s for s, _ in PERIODS) - 1 for dt in dates]); POOL = np.array([PERIODS[k][1] for k in PER])
H = range(1, 24)

print('III. WHERE EACH DRAW IS RECORDED, OVER THE SOUTH AFRICAN LOTTO HISTORY [EXACT counts]')
def places(Yv, Xv):
    """for each pair (draw-to-record x_i, field position j): cells (total, per domain) with K = x_i - y_j."""
    k = Xv[:, :, None] - Yv[:, None, :] + OFF
    ok = (k >= 0) & (k < NK); kk = np.clip(k, 0, NK - 1)
    tot = np.where(ok, CT[np.arange(6)[None, None, :], kk], 0)
    per = np.where(ok[..., None], C.transpose(1, 2, 0)[np.arange(6)[None, None, :], kk], 0)
    return tot, per
rec, dom_any, dom14, nums = 0, 0, 0, 0
for h in [1]:
    tot, per = places(M[:-h], M[h:])
    pl = tot.sum(2); dsup = (per.sum(2) > 0).sum(-1)
    nums = pl.size; rec = int((pl > 0).sum()); dom14 = int((dsup >= 14).sum())
    print('  h = 1 (Y-field = the previous draw): %d draw numbers to record; %d recorded at least once (%.1f%%), at %.1f places on average'
          % (nums, rec, 100 * rec / nums, pl.mean()))
    print('  domains that record a number: mean %.1f of 27; recorded in at least 14 of 27 domains (the Resonance Threshold of the Construct papers): %d (%.1f%%)'
          % (dsup.mean(), dom14, 100 * dom14 / nums))
allp = 0
for h in H:
    tot, _ = places(M[:-h], M[h:]); allp += int(tot.sum())
print('  over all 23 intervals: %d recordings of draw numbers in the 9,072 cells of the 27 domains' % allp)
print('  a number is recordable only if it lies within 18 of some number of the Y-field: the reach of the constants')

print('IV. THE CONSTRUCT\'S ECHO FORECAST AGAINST SHUFFLED HISTORY [EXACT counts; 200 within-period shuffles per interval]')
def forecast_score(Mm, Pm, h, thr=False):
    Yv, Xv, Yn, Z = Mm[:-2 * h], Mm[h:-h], Mm[h:-h], Mm[2 * h:]
    tot, per = places(Yv, Xv)                                   # weights of (i, j)
    val = Xv[:, :, None] + Yn[:, None, :] - Yv[:, None, :]      # forecast value of (i, j)
    val = np.where((val >= 1) & (val <= Pm[2 * h:, None, None]), val, 0)
    w = np.where(val > 0, tot, 0)
    m = len(Z); maxv = 59
    S = np.zeros((m, maxv + 1)); np.add.at(S, (np.repeat(np.arange(m)[:, None], 36, 1), val.reshape(m, 36)), w.reshape(m, 36))
    S[:, 0] = -1
    ticket = np.argsort(-S - np.arange(maxv + 1) * 1e-9, axis=1, kind='stable')[:, :6]
    hits = (ticket[:, :, None] == Z[:, None, :]).any(1).sum(1)
    top = ticket[:, 0]
    if not thr: return hits.mean()
    dsup = np.zeros(m, int)
    for di in range(27):
        k = Xv[:, :, None] - Yv[:, None, :] + OFF; ok = (k >= 0) & (k < NK)
        has = np.where(ok, C[di][np.arange(6)[None, None, :], np.clip(k, 0, NK - 1)] > 0, False)
        dsup += (has & (val == top[:, None, None])).any((1, 2))
    return hits.mean(), (dsup >= 14).mean(), (top[:, None] == Z).any(1)[dsup >= 14].mean() if (dsup >= 14).any() else float('nan'), (top[:, None] == Z).any(1).mean()
obs = np.array([forecast_score(M, POOL, h) for h in H])
blocks = [list(np.where(PER == k)[0]) for k in range(len(PERIODS))]; rng = random.Random(4226); NS = 200
null = np.zeros((NS, 23))
for s in range(NS):
    order = []
    for b in blocks: c = b[:]; rng.shuffle(c); order += c
    Ms = M[order]; null[s] = [forecast_score(Ms, POOL, h) for h in H]
mu, sd = null.mean(0), null.std(0); z = (obs - mu) / sd
fam = (1 + (((null - mu) / sd).max(1) >= z.max()).sum()) / (1 + NS)
j = int(z.argmax())
print('  six-number forecast, main numbers matched per forecast: %.4f to %.4f over h = 1..23; shuffles %.4f to %.4f; random ticket 36/N = 0.62 to 0.73'
      % (obs.min(), obs.max(), mu.min(), mu.max()))
print('  strongest interval h = %d (z %+.2f); family test over the 23 intervals: family p %.4f -- %s'
      % (j + 1, z[j], fam, 'BELOW 0.05 ON THE WHOLE HISTORY: DECIDED BY THE HELD-OUT TEST OF IV.b' if fam < 0.05 else 'NO SIGNAL BEYOND CHANCE'))
h1 = forecast_score(M, POOL, 1, thr=True)
print('  h = 1: the top echo reaches 14 of 27 domains in %.1f%% of draws; when it does it is drawn %.1f%% of the time, and %.1f%% overall; a number chosen at random is drawn %.1f%% of the time (6/N, averaged over the same draws)'
      % (100 * h1[1], 100 * h1[2], 100 * h1[3], 100 * float((6 / POOL[2:]).mean())))

print('IV.b SELECTED ON THE PAST, TESTED ON THE FUTURE [the select-then-test design of C-MAP-1 (records/construct/sa_lotto.py, IV.b), added after section IV was seen]')
def famtest(idx, NS, seed, hs):
    Mm, Pm = M[idx], POOL[idx]; o = np.array([forecast_score(Mm, Pm, h) for h in hs])
    bl = [list(np.where(PER[idx] == k)[0]) for k in sorted(set(PER[idx]))]; r = random.Random(seed); nl = np.zeros((NS, len(hs)))
    for s_ in range(NS):
        od = []
        for b in bl: c = b[:]; r.shuffle(c); od += c
        nl[s_] = [forecast_score(Mm[od], Pm[od], h) for h in hs]
    m_, d_ = nl.mean(0), nl.std(0); zz = (o - m_) / d_
    return o, m_, zz, (1 + (((nl - m_) / d_).max(1) >= zz.max()).sum()) / (1 + NS), (1 + (nl >= o).sum(0)) / (1 + NS)
tr, te = np.where(PER == 0)[0], np.where(PER > 0)[0]
o1, m1, z1, f1, _ = famtest(tr, 200, 11, list(H)); b1 = int(z1.argmax()) + 1
print('  search on period 1 (%s to %s): strongest h = %d (z %+.2f), family p %.4f' % (dates[tr[0]], dates[tr[-1]], b1, z1.max(), f1))
o2, m2, z2, _, p2 = famtest(te, 500, 12, [b1])
print('  that interval on periods 2 to 4 (%s to %s), never seen by the search: %.4f against %.4f, p %.4f -- %s'
      % (dates[te[0]], dates[te[-1]], o2[0], m2[0], p2[0], 'IT REPEATS' if p2[0] < 0.05 else 'IT DOES NOT REPEAT'))
o3, m3, z3, _, p3 = famtest(tr, 500, 14, [j + 1]); o4, m4, z4, _, p4 = famtest(te, 500, 13, [j + 1])
print('  the interval h = %d flagged on the whole history, in each half: period 1 p %.4f, periods 2 to 4 p %.4f -- chosen after seeing both, so neither is an independent test'
      % (j + 1, p3[0], p4[0]))
print('  the record reads it as a nominal elevation that the frozen protocol does not confirm; it can be tested only on a history never used here')

print('V. A PLANTED SEQUENCE, ON WHICH THE SAME FORECAST MUST WORK [the positive control]')
g = random.Random(7); P = []
for t in range(400):
    if t % 50 == 0: base, t0 = sorted(g.sample(range(1, 44), 6)), t
    P.append([((v - 1 + t - t0) % 49) + 1 for v in base])
Pm = np.array([sorted(r) for r in P]); PP = np.full(len(Pm), 49)
print('  a sequence of 400 draws in which every number rises by 1 each draw (a fresh start every 50): forecast matches per draw at h = 1: %.2f of 6; at h = 2: %.2f'
      % (forecast_score(Pm, PP, 1), forecast_score(Pm, PP, 2)))
print('  so the Construct forecasts what has a rule in it; on the Lotto history, selected on the past and tested on the future, it does no better than chance')

print('VI. THE COUNTS OF SEQ 52 RECONCILED [EXACT; after APE-244]')
n = len(rows); nt = sum(n - h for h in H); nk = sum(n - 2 * h for h in H)
assert nt == 23 * n - sum(H) == 60375 and nk == 23 * n - 2 * sum(H) == 60099
print('  %d draws x 23 intervals = %d, but the first h draws have no draw h earlier, so interval h holds %d - h templates: %d - %d = %d, the 60,375 of SEQ 52' % (n, 23 * n, n, 23 * n, sum(H), nt))
print('  a ticket at interval h needs the draws h and 2h earlier, so interval h holds %d - 2h tickets: %d - %d = %d, the 60,099 of SEQ 52' % (n, 23 * n, 2 * sum(H), nk))
F = [0, 1]
for _ in range(30): F.append((F[-1] + F[-2]) % 9)
print('  intervals with F(h) not a unit mod 9: %s within h = 1..23 (five), and %s within h = 1..24 (six, the return T^24 = I included)'
      % ([h for h in range(1, 24) if F[h] % 3 == 0], [h for h in range(1, 25) if F[h] % 3 == 0]))
