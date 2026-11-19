#!/usr/bin/env python3
"""sa_lotto.py -- the Construct read over the South African Lotto history, through Omega42 (Companion Part 105).

Rules frozen before any score was computed (C-MAP-1, PROPOSED; Companion 105.2):
  RESIDUE    a number n is read as n mod 9 (its digital root, with 9 read as 0), Core F-02 at the surface.
  DRAW       a draw is its six main numbers in ascending order; position i (1 to 6) is the i-th smallest. The bonus is not used.
  ORBITS     the 23 orbits of manifestation are read as the 23 intervals h = 1 to 23 (the 23 steps T^h before the
             return T^24 = I). This identification is PROPOSED; it is replaced when the Originator's own definition
             of the 23 orbits is supplied (Companion 105.6).
  TEMPLATE   for interval h and draw t, Y = draw t - h and X = draw t (the Construct's Y/X pair). At position i the pair
             of residues (y_i, x_i) is a place of the 81, with its loop, norm class and step on the loop. The draw is
             reconstructed exactly inside the template: X = Y + DELTA, number by number.
  FORECASTS  a template is progressed h draws on, to draw t + h, by three rules fixed in advance:
             F1 the Omega42 law: (y, x) -> (x, y + x), so the forecast residue is y + x;
             F2 constant step: 2x - y;      F3 echo: x.
             A ticket (F1 only) puts at each position the number nearest X's number with the forecast residue.
  NULL       the same rules run on the draws shuffled within each number-pool period, 2,000 times (Python's
             random.Random(4224)); a rule shows a signal only if it beats the shuffles after correction for all
             69 residue tests (3 rules x 23 intervals), by the maximum statistic over the family.
    python3 records/construct/sa_lotto.py            # diffed in CI
    python3 records/construct/sa_lotto.py --write F  # writes every template (60,000 rows) to F
"""
import csv, hashlib, io, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'sa_lotto', 'draws.csv')
H = range(1, 24)
SHUFFLES = 2000
PERIODS = [('2000-01-01', 49), ('2017-08-16', 52), ('2025-09-24', 58), ('2026-06-01', 52)]
Y = lambda b: 'YES' if b else 'NO'

raw = open(DATA, 'rb').read()
rows = list(csv.reader(io.StringIO(raw.decode())))[1:]
dates = [r[0] for r in rows]
M = np.array([[int(x) for x in r[1:7]] for r in rows]); B = np.array([int(r[7]) for r in rows])
n = len(rows)
def pool_of(d):
    p = PERIODS[0][1]
    for start, size in PERIODS:
        if d >= start: p = size
    return p
POOL = np.array([pool_of(d) for d in dates]); PER = np.array([sum(d >= s for s, _ in PERIODS) - 1 for d in dates])

# --- Omega42 places -------------------------------------------------------------------------------------------
def T(s): return (s[1], (s[0] + s[1]) % 9)
BASES = {'still point': (0, 0), 'loop of 8': (0, 3), 'N+-1': (0, 1), 'N+-2 (canonical voice, seed 2,5)': (2, 5), 'N+-4': (0, 2)}
PLACE = {}
for name, b in BASES.items():
    s, k = b, 0
    while (s not in PLACE): PLACE[s] = (name, k); s = T(s); k += 1
assert len(PLACE) == 81
NAMES = list(BASES)

print('I. THE DRAW HISTORY [checked; records/construct/sa_lotto/SOURCES.txt]')
print('  draws.csv SHA-256 %s' % hashlib.sha256(raw).hexdigest())
print('  %d draws of the main game, %s to %s; %d dates, each once: %s' % (n, dates[0], dates[-1], len(set(dates)), Y(len(set(dates)) == n)))
ok = all(list(r) == sorted(r) and len(set(r)) == 6 for r in M.tolist()) and all(B[i] not in M[i] for i in range(n)) and int(M.min()) >= 1
print('  six distinct main numbers in ascending order, bonus distinct, every number within its pool: %s' % Y(ok and bool((M.max(1) <= POOL).all() and (B <= POOL).all())))
for k, (s, p) in enumerate(PERIODS):
    idx = np.where(PER == k)[0]
    print('  period %d: numbers 1 to %d, %d draws, %s to %s' % (k + 1, p, len(idx), dates[idx[0]], dates[idx[-1]]))
SECOND = ['2026-10-24,2,8,9,10,30,34,27', '2026-10-21,1,3,8,23,32,35,28', '2026-10-17,2,4,6,10,15,46,1', '2026-10-14,11,12,30,42,47,48,10',
          '2026-10-10,5,10,14,29,30,45,15', '2026-10-07,9,10,16,23,29,33,47', '2026-10-03,7,18,25,36,40,44,38', '2026-09-30,3,4,6,7,12,46,18',
          '2026-09-26,2,36,40,43,44,50,1', '2026-09-23,6,8,14,22,38,43,15', '2026-09-19,6,23,24,32,44,46,48', '2026-09-16,24,25,35,38,44,49,48',
          '2026-09-12,17,24,26,30,39,45,41', '2026-09-09,12,22,24,34,45,47,50', '2026-09-05,3,4,7,31,42,46,1', '2026-09-02,9,15,21,24,30,39,34',
          '2026-08-29,3,20,30,35,39,50,14', '2026-08-26,3,8,17,19,26,46,12', '2026-08-22,5,10,12,14,23,41,20', '2026-08-19,10,19,21,40,50,51,7']
THIRD = {'2026-10-24': '289103034', '2026-10-21': '138233235', '2026-10-17': '246101546', '2026-10-14': '111230424748',
         '2026-10-10': '51014293045', '2026-10-07': '91016232933', '2026-10-03': '71825364044', '2026-09-30': '34671246'}
have = {','.join(r) for r in rows}
print('  the last 20 draws agree with a second source (lotteryextreme.com): %s' % Y(all(s in have for s in SECOND)))
print('  the last 8 draws agree with a third source (lotteryvalley.com, digits run together): %s' % Y(all(''.join(map(str, M[dates.index(d)])) == v for d, v in THIRD.items())))
print('  known gap: no draws listed between 2007-03-31 and 2007-10-13')

R = M % 9
print('II. THE 23 ORBITS: EVERY DRAW RECONSTRUCTED EXACTLY INSIDE ITS TEMPLATES [EXACT; C-MAP-1]')
def templates():
    for t in range(n):
        for h in H:
            if t - h < 0: continue
            y, x = M[t - h], M[t]
            pl = [PLACE[(int(a) % 9, int(b) % 9)] for a, b in zip(y, x)]
            yield (t, h, dates[t - h], dates[t], y.tolist(), x.tolist(), (x - y).tolist(), pl)
count = 0; exact = True; buf = io.StringIO(); w = csv.writer(buf, lineterminator='\n')
w.writerow(['draw', 'h', 'Y_date', 'X_date', 'Y', 'X', 'DELTA', 'places (loop:step) by position'])
tally = {k: 0 for k in NAMES}
for t, h, yd, xd, y, x, d, pl in templates():
    count += 1; exact &= all(a + b == c for a, b, c in zip(y, d, x))
    for name, k in pl: tally[name] += 1
    w.writerow([t + 1, h, yd, xd, ' '.join(map(str, y)), ' '.join(map(str, x)), ' '.join(map(str, d)), ' '.join('%s:%d' % (nm.split(' ')[0], k) for nm, k in pl)])
out = buf.getvalue().encode()
print('  %d templates (each draw is the X of up to 23 templates and the Y of up to 23 more)' % count)
print('  X = Y + DELTA number by number in every template: %s' % Y(exact))
print('  the template file (python3 records/construct/sa_lotto.py --write F) has SHA-256 %s' % hashlib.sha256(out).hexdigest())
tot = sum(tally.values())
print('  the %d places of the templates, by loop: %s' % (tot, '; '.join('%s %d (%.1f%%)' % (k, v, 100 * v / tot) for k, v in tally.items())))
print('  the same places if residues were drawn uniformly from Z/9: still point 1.2%, loop of 8 9.9%, each 24-loop 29.6%')
if len(sys.argv) == 3 and sys.argv[1] == '--write':
    open(sys.argv[2], 'wb').write(out); print('  written: %s' % sys.argv[2])

print('III. WHAT THE DRAWS LOOK LIKE MOD 9 [EXACT counts; the expectation from the pool]')
for k, (s, p) in enumerate(PERIODS):
    idx = np.where(PER == k)[0]
    obs = np.bincount(R[idx].ravel(), minlength=9)
    share = np.array([len([v for v in range(1, p + 1) if v % 9 == r]) for r in range(9)]) / p
    exp = share * obs.sum(); chi = float(((obs - exp) ** 2 / exp).sum())
    crown = obs[[0, 3, 6]].sum() / obs.sum()
    print('  period %d (1 to %d): residue counts 0..8 %s; chi-square %.2f on 8 degrees of freedom (5%% point 15.51); Crown share %.4f against the pool\'s %.4f'
          % (k + 1, p, obs.tolist(), chi, crown, share[[0, 3, 6]].sum()))

print('IV. THE FORECAST TEST: DO THE TEMPLATES SEE THE NEXT DRAW? [EXACT counts; null by within-period shuffles]')
rng = random.Random(4224)
def score(Rm, Mm, Pm=None):
    Pm = POOL if Pm is None else Pm
    s = np.zeros((3, 23)); tk = np.zeros(23)
    for j, h in enumerate(H):
        y, x, z = Rm[:-2 * h], Rm[h:-h], Rm[2 * h:]
        f = [(y + x) % 9, (2 * x - y) % 9, x]
        for r in range(3): s[r, j] = (f[r] == z).sum(1).mean()
        xn, zn, pz = Mm[h:-h], Mm[2 * h:], Pm[2 * h:, None]
        dlt = ((f[0] - x + 4) % 9) - 4
        tick = xn + dlt; tick = np.where(tick < 1, tick + 9, tick); tick = np.where(tick > pz, tick - 9, tick)
        tk[j] = (tick[:, :, None] == zn[:, None, :]).any(1).sum(1).mean()
    return s, tk
obs, otk = score(R, M)
blocks = [list(np.where(PER == k)[0]) for k in range(len(PERIODS))]
null = np.zeros((SHUFFLES, 3, 23)); ntk = np.zeros((SHUFFLES, 23))
for i in range(SHUFFLES):
    order = []
    for b in blocks: c = b[:]; rng.shuffle(c); order += c
    null[i], ntk[i] = score(R[order], M[order])
mu, sd = null.mean(0), null.std(0)
z = (obs - mu) / sd; zn = (null - mu) / sd
p = (1 + (null >= obs).sum(0)) / (1 + SHUFFLES)
fam = (1 + (zn.reshape(SHUFFLES, -1).max(1) >= z.max()).sum()) / (1 + SHUFFLES)
RN = ['F1 law y+x', 'F2 step 2x-y', 'F3 echo x']
for r in range(3):
    j = int(z[r].argmax())
    print('  %s: positions matched per draw, over h = 1..23, from %.4f to %.4f; shuffles %.4f to %.4f; best h = %d (z %+.2f, p %.4f)'
          % (RN[r], obs[r].min(), obs[r].max(), mu[r].min(), mu[r].max(), j + 1, z[r, j], p[r, j]))
print('  residue tests at p < 0.05 before correction: %d of 69 (about 3.5 expected by chance alone)' % int((p < 0.05).sum()))
print('  the largest z over all 69 against the largest of the shuffles: z %+.2f, family p %.4f -- %s'
      % (z.max(), fam, 'A SIGNAL BEYOND CHANCE' if fam < 0.05 else 'NO SIGNAL BEYOND CHANCE'))
ptk = (1 + (ntk >= otk).sum(0)) / (1 + SHUFFLES); zt = (otk - ntk.mean(0)) / ntk.std(0)
famt = (1 + (((ntk - ntk.mean(0)) / ntk.std(0)).max(1) >= zt.max()).sum()) / (1 + SHUFFLES)
print('  F1 tickets: main numbers matched per ticket %.4f to %.4f over h = 1..23; shuffles %.4f to %.4f; a random ticket expects 36/N = %.4f (N = 49) to %.4f (N = 58)'
      % (otk.min(), otk.max(), ntk.mean(0).min(), ntk.mean(0).max(), 36 / 49, 36 / 58))
print('  F1 tickets, family test over the 23 intervals: largest z %+.2f, family p %.4f -- %s' % (zt.max(), famt, 'A SIGNAL BEYOND CHANCE' if famt < 0.05 else 'NO SIGNAL BEYOND CHANCE'))
def tickets(h):
    f, x, xn = (R[:-2 * h] + R[h:-h]) % 9, R[h:-h], M[h:-h]
    t = xn + ((f - x + 4) % 9) - 4; t = np.where(t < 1, t + 9, t); return np.where(t > POOL[2 * h:, None], t - 9, t)
six = sum(int(sum(sorted(set(a)) == list(b) for a, b in zip(tickets(h).tolist(), M[2 * h:].tolist()))) for h in H)
print('  six of six main numbers matched by an F1 ticket, over all intervals: %d times in %d tickets' % (six, sum(n - 2 * h for h in H)))

print('IV.b SELECT ON THE PAST, TEST ON THE FUTURE [the four modes as procedures, PROPOSED after APE-238; EXACT counts]')
tr = np.where(PER == 0)[0]; te = np.where(PER > 0)[0]
otr, _ = score(R[tr], M[tr], POOL[tr]); r0, j0 = np.unravel_index(int(otr.argmax()), otr.shape)
print('  PULSE (search) on period 1 alone, %s to %s: the strongest of the 69 is %s at h = %d, %.4f positions per draw' % (dates[tr[0]], dates[tr[-1]], RN[r0], j0 + 1, otr[r0, j0]))
ote, _ = score(R[te], M[te], POOL[te]); rng2 = random.Random(4225); nte = []
tb = [list(np.where(PER == k)[0] - te[0]) for k in range(1, len(PERIODS))]
for i in range(500):
    order = []
    for b in tb: c = b[:]; rng2.shuffle(c); order += c
    nte.append(score(R[te][order], M[te][order], POOL[te])[0][r0, j0])
nte = np.array(nte); pte = (1 + (nte >= ote[r0, j0]).sum()) / 501
print('  AMPLIFY (repeat) on periods 2 to 4, %s to %s, never seen by the search: %.4f against shuffles %.4f, p %.4f -- %s'
      % (dates[te[0]], dates[te[-1]], ote[r0, j0], nte.mean(), pte, 'IT REPEATS' if pte < 0.05 else 'IT DOES NOT REPEAT'))
print('  DAMPEN is the shuffle null of section IV; FOCUS is the single rule carried forward here, with nothing else tuned')

print('V. READING [the counts EXACT; the reading CDT-C]')
print('  the Construct maps every draw exactly, at every one of the 23 intervals: the templates are a complete record of the past')
if fam >= 0.05 and famt >= 0.05:
    print('  no frozen rule sees the next draw better than the same rule on shuffled history: the draws carry none of the')
    print('  templates\' structure forward, as a fair draw would not; the structure belongs to the frame laid over the draws')
else:
    print('  a frozen rule beats the shuffles after correction: the result stands only after a sealed prospective test (Companion 105.5)')
