#!/usr/bin/env python3
"""construct_engine.py -- M326 Construct Engine, the Originator's Construct as a general prediction assistant (Tier 3, ADOPTED
28 October 2026; Core Part 3.52, L-526; Companion Parts 107 and 108).

The engine is the workbook PRIMORDIAL FRACTURE read exactly (records/construct/primordial/construct_frozen.json): 27 domains, 216
echo regions, 9,072 cells, each cell Y_j + K (Core MATH-55). It does three things:
  --places Y1..Y6 X1..X6   every cell, in every domain, at which each X number is recorded under the field Y
  --forecast FILE          for a sequence of six-number rows (one per line, comma separated): the Construct's echo forecast
                           of the next row -- issued only if the forecast rule, chosen on the first 60% of the sequence,
                           beats on the last 40% both shuffled history (p < 0.05, 300 shuffles) and the latest row carried
                           forward (a paired sign-flip test, p < 0.05); otherwise it says NO FORECAST. The report states the
                           intervals searched, the cut, the margin over the stronger baseline and the SHA-256 of the data:
                           an authorization holds for that data only, and lapses when the sequence is extended (L-526, L-527)
  --reconstruct a b d      every state consistent with x(n) = a and x(n+d) = b, all kept when not unique (Core MATH-53)
  --square VALUE|"TEXT"     M328 Square Reading: forward, return, stillness and turn for a value or a strike's anchor value
  --manifest               after --forecast, --reconstruct or --square: the run manifest of Core L-528 (3)
  --selftest               the workbook's own 216 echo counters; a planted sequence (a forecast must be issued, and right);
                           a sequence without memory and a slowly changing sequence (no forecast may be issued); the
                           interval chosen without the held-out part; a rule at interval 3, forecast exactly
A game of chance is the negative control and never receives a forecast it can act on (Core L-525): its history passes no
held-out test. Needs numpy.
"""
import json, os, random, sys
import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FZ = json.load(open(os.path.join(REPO, 'records', 'construct', 'primordial', 'construct_frozen.json')))
DOM = list(FZ['domains']); OFF = 18; NK = 2 * OFF + 1
REG = []
for d in DOM:
    for e in FZ['domains'][d]['echo']:
        r0, b = e['range'][1], e['block']
        REG.append((d, e, [(FZ['domains'][d]['rows']['%d.%d' % (r, b)]['K'][j], j, r, FZ['domains'][d]['rows']['%d.%d' % (r, b)]['label']) for r in range(r0, r0 + 7) for j in range(6)]))
C = np.zeros((27, 6, NK), int)
for d, e, cells in REG:
    for K, j, r, l in cells: C[DOM.index(d), j, int(round(K)) + OFF] += 1
CT = C.sum(0)

def places(Y, X):
    out = []
    for d, e, cells in REG:
        for i, x in enumerate(X):
            for K, j, r, l in cells:
                if Y[j] + K == x: out.append((i, x, d, e['block'], r, l, j + 1, K))
    return out

def score(M, h, top=False, lo=1, hi=None, rows=False):
    Yv, Xv, Z = M[:-2 * h], M[h:-h], M[2 * h:]
    k = Xv[:, :, None] - Yv[:, None, :] + OFF; ok = (k >= 0) & (k < NK)
    w = np.where(ok, CT[np.arange(6)[None, None, :], np.clip(k, 0, NK - 1)], 0)
    val = Xv[:, :, None] + Xv[:, None, :] - Yv[:, None, :]
    hi = hi or int(M.max()); good = (val >= lo) & (val <= hi); val = np.where(good, val - lo + 1, 0); w = np.where(good, w, 0)
    m = len(Z); S = np.zeros((m, hi - lo + 2)); np.add.at(S, (np.repeat(np.arange(m)[:, None], 36, 1), val.reshape(m, 36)), w.reshape(m, 36)); S[:, 0] = -1
    t = np.argsort(-S - np.arange(S.shape[1]) * 1e-9, axis=1, kind='stable')[:, :6] + lo - 1
    per = (t[:, :, None] == Z[:, None, :]).any(1).sum(1)
    return per if rows else per.mean()

def persistence(M, h):
    """the baseline: the latest row carried forward, scored on the same targets as score(M, h) -- each target row forecast by
    the row just before it"""
    X, Z = M[2 * h - 1:-1], M[2 * h:]
    return np.array([len(set(a) & set(b)) for a, b in zip(X.tolist(), Z.tolist())])

def next_forecast(M, h, lo, hi, beyond=False):
    """the next row, by the rule the gate scored: row t + 2h from rows t and t + h, so the next row from rows n - 2h and n - h.
    The forecast keeps to the range of values seen (lo to hi); with beyond=True it also returns the candidates outside that
    range that weigh at least as much as the last number kept, labelled apart, since a rising sequence leaves its range"""
    Yv, Xv = M[-2 * h], M[-h]
    S = {}
    for i in range(6):
        for j in range(6):
            kk = Xv[i] - Yv[j] + OFF
            if 0 <= kk < NK and CT[j, kk]:
                v = int(Xv[i] + Xv[j] - Yv[j]); S[v] = S.get(v, 0) + int(CT[j, kk])
    rank = sorted(S, key=lambda v: (-S[v], v))
    kept = [v for v in rank if lo <= v <= hi][:6]
    if not beyond: return sorted(kept)
    floor_w = S[kept[-1]] if len(kept) == 6 else 0
    out = [v for v in rank if not lo <= v <= hi and S[v] >= floor_w][:6 - len(kept) if len(kept) < 6 else 6]
    return sorted(kept), sorted(out)

def fingerprint(M):
    """SHA-256 of the rows as given: an authorization holds for this data only (L-526 (6))"""
    import hashlib
    return hashlib.sha256('\n'.join(','.join(str(int(v)) for v in r) for r in np.array(M).tolist()).encode()).hexdigest()

def forecast(M, shuffles=300, seed=4227):
    M = np.array(M); n = len(M); cut = int(n * 0.6); lo, hi = int(M.min()), int(M.max())
    hs = [h for h in range(1, 24) if 2 * h < cut - 2 and 2 * h < n - cut - 2]
    base = {'rows': n, 'cut': cut, 'searched': '%d to %d' % (hs[0], hs[-1]) if hs else 'none', 'data': fingerprint(M)}
    if not hs: return dict(base, issued=False, why='the sequence is too short for a held-out test')
    tr = M[:cut]; h = max(hs, key=lambda h: score(tr, h, lo=lo, hi=hi) - np.mean([score(tr[random.Random(h).sample(range(cut), cut)], h, lo=lo, hi=hi) for _ in range(3)]))
    te = M[cut:]; per = score(te, h, lo=lo, hi=hi, rows=True); o = per.mean()
    r = random.Random(seed); idx = list(range(len(te))); nl = []
    for _ in range(shuffles): r.shuffle(idx); nl.append(score(te[idx], h, lo=lo, hi=hi))
    p = (1 + sum(x >= o for x in nl)) / (1 + shuffles)
    # the persistence baseline on the same targets, and a paired sign-flip test of the difference
    d = per - persistence(te, h); dm = d.mean(); g = random.Random(seed + 1)
    flips = [np.mean([x if g.random() < 0.5 else -x for x in d]) for _ in range(shuffles)]
    pp = (1 + sum(f >= dm for f in flips)) / (1 + shuffles)
    res = dict(base, h=h, held_out=round(float(o), 4), shuffled=round(float(np.mean(nl)), 4), p=round(p, 4),
               persistence=round(float(persistence(te, h).mean()), 4), p_persistence=round(pp, 4),
               margin=round(float(o - max(np.mean(nl), persistence(te, h).mean())), 4))
    if p < 0.05 and pp < 0.05:
        f, out = next_forecast(M, h, lo, hi, beyond=True); res.update(issued=True, forecast=f, beyond=out)
    elif p >= 0.05: res.update(issued=False, why='the rule chosen on the first 60% does not beat shuffled history on the last 40%')
    else: res.update(issued=False, why='the rule chosen on the first 60% does not beat the latest row carried forward on the last 40%')
    return res

def report(res):
    tail = ' | rows %d, held out from row %d, intervals searched %s on the first part only; data SHA-256 %s' % (res['rows'], res['cut'] + 1, res['searched'], res['data'][:16])
    if 'h' in res:
        g = 'interval h = %d; held out %.4f against shuffled %.4f (p %.4f) and against the latest row carried forward %.4f (p %.4f); margin over the stronger baseline %+.4f' % (
            res['h'], res['held_out'], res['shuffled'], res['p'], res['persistence'], res['p_persistence'], res['margin'])
        if res.get('issued'): return 'M326 FORECAST ISSUED: next row %s%s (%s)%s' % (res['forecast'], '; beyond the range seen so far: %s' % res['beyond'] if res.get('beyond') else '', g, tail)
        return 'M326 NO FORECAST: %s (%s)%s' % (res['why'], g, tail)
    return 'M326 NO FORECAST: %s%s' % (res['why'], tail)


# ---------------------------------------------------------------- reconstruction (Core MATH-53; Companion 112.3)
def fib9(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, (a + b) % 9
    return a
def advance(state, d):
    x, y = state
    for _ in range(d): x, y = y, (x + y) % 9
    return x, y
def reconstruct(a, b, d):
    """every state (x(n), x(n+1)) mod 9 with x(n) = a and x(n+d) = b: x(n+d) = F(d-1) x(n) + F(d) x(n+1). One solution when F(d)
    is a unit mod 9, three or none when 3 divides it once, nine or none when 9 divides it; each solution is checked by advancing it d steps"""
    a, b = a % 9, b % 9; c1, c2 = fib9(d - 1), fib9(d)
    sols = [(a, y) for y in range(9) if (c1 * a + c2 * y) % 9 == b]
    assert all(advance(s, d)[0] == b for s in sols)
    return sols, c1, c2

# ---------------------------------------------------------------- M328 Square Reading (Core Part 3.54; records/construct/columns.py)
def square_reading(v):
    """the four directions of the Construct's squares for one value v (1 to 9, 9 the class 0): FORWARD along a row (x2 in the Lower
    World, +3 in the Higher World), RETURN down a column (x5, the inverse of 2; or +6, the inverse of +3), STILLNESS on the main
    diagonal (the value kept) and TURN on the anti-diagonal (x4, which carries each voice to the next; in the Higher World the row's cycle)"""
    r = v % 9
    disp = lambda x: 9 if x % 9 == 0 else x % 9
    if r % 3:
        fwd = [disp(r * 2 ** k) for k in range(6)]; ret = [disp(r * 5 ** k) for k in range(6)]; turn = [disp(r * 4 ** k) for k in range(3)]
        world, cls = 'Lower World (a unit)', 'its column holds the six values it is not, mod 3: %s' % sorted({disp(r - u) for u in (1, 2, 4, 5, 7, 8)})
    else:
        fwd = [disp(r + 3 * k) for k in range(3)]; ret = [disp(r + 6 * k) for k in range(3)]; turn = fwd[:]
        world, cls = 'Higher World (the Crown)', 'its column holds the three values it is, mod 3: %s' % sorted({disp(r + 3 * k) for k in range(3)})
    return dict(value=disp(r), world=world, forward=fwd, ret=ret, still=[disp(r)] * 3, turn=turn, cls=cls)
def square_report(v, label=''):
    q = square_reading(v)
    return '\n'.join(['M328 SQUARE READING%s: value %d, %s' % (label, q['value'], q['world']),
        '  FORWARD (along a row):          %s   where it is going' % ' -> '.join(map(str, q['forward'])),
        '  RETURN (down a column):         %s   where it came from: the same world going back, a path as long as the forward' % ' -> '.join(map(str, q['ret'])),
        '  STILLNESS (the main diagonal):  %s   what stays the same: forward and back cancel' % ' -> '.join(map(str, q['still'])),
        '  TURN (the anti-diagonal):       %s   which voice it moves into: %s' % (' -> '.join(map(str, q['turn'])), 'x4, from voice to voice, home in three' if q['world'].startswith('Lower') else 'the Crown turns by thirds'),
        '  ' + q['cls'],
        '  [the directions are CDT-A, read from the squares (records/construct/columns.py), and every domain carries them on its own field; what they mean for a question is CDT-C]'])

# ---------------------------------------------------------------- the run manifest (Core L-528 (3); Companion 112.3)
STATUS = {'places': 'STRUCTURAL (CDT-A)', 'reconstruct': 'STRUCTURAL (CDT-A)', 'square': 'STRUCTURAL (CDT-A) for the directions; RESIDUAL-OPEN (CDT-C) for what they mean',
          'issued': 'CORRESPONDENCE-SUPPORTED for this sequence and the next row only; a hypothesis to watch (L-526 (4), (6))', 'none': 'NO-FORECAST'}
def sha(path):
    import hashlib
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()
def manifest(kind, inputs, params, result_line, status_key):
    import hashlib
    eng = sha(os.path.abspath(__file__)); con = sha(os.path.join(REPO, 'records', 'construct', 'primordial', 'construct_frozen.json'))
    inp = hashlib.sha256(repr(inputs).encode()).hexdigest()
    rid = hashlib.sha256(('|'.join([kind, eng, con, inp, repr(sorted(params.items()))])).encode()).hexdigest()[:16]
    return '\n'.join(['CONSTRUCT RUN MANIFEST (Core L-528)', '  RUN ID: CR-%s   (the same engine, constants, input and parameters give the same ID)' % rid,
        '  KIND: %s' % kind, '  ENGINE SHA-256: %s' % eng, '  CONSTANTS SHA-256: %s (construct_frozen.json; workbook 2a96dd63...)' % con,
        '  INPUT SHA-256: %s' % inp, '  PARAMETERS: %s' % ', '.join('%s=%s' % kv for kv in sorted(params.items())),
        '  RESULT: %s' % result_line, '  STATUS: %s' % STATUS[status_key]])
def read_rows(path):
    rows, skipped = [], []
    for k, line in enumerate(open(path), 1):
        v = [int(x) for x in line.strip().split(',') if x.strip().lstrip('-').isdigit()]
        if len(v) >= 6: rows.append(v[:6])   # a leading date is skipped; a trailing bonus is ignored
        elif line.strip(): skipped.append(k)
    return rows, skipped

def selftest():
    X0, Y0 = FZ['X0'], FZ['Y0']
    cnt = sum(1 for d, e, cells in REG if [sum(1 for K, j, r, l in cells if Y0[j] + K == x) for x in X0] == e['cached'])
    g = random.Random(7); P = []
    for t in range(300):
        if t % 50 == 0: base, t0 = sorted(g.sample(range(1, 44), 6)), t
        P.append(sorted(((v - 1 + t - t0) % 49) + 1 for v in base))
    a = forecast(P, 200)
    nxt = sorted(((v - 1 + 300 - 250) % 49) + 1 for v in base)
    iid = [sorted(g.sample(range(1, 50), 6)) for _ in range(300)]; b = forecast(iid, 200)
    g2 = random.Random(11); row = sorted(g2.sample(range(1, 50), 6)); Q = []
    for t in range(300):                       # a slowly changing sequence: one number replaced each row
        i = g2.randrange(6); v = g2.randrange(1, 50)
        while v in row: v = g2.randrange(1, 50)
        row = sorted(row[:i] + row[i + 1:] + [v]); Q.append(row)
    c = forecast(Q, 200)
    P2 = [r[:] for r in P]; P2[-1][0] += 1     # one value changed in the held-out part
    a2 = forecast(P2, 200)
    g3 = random.Random(5); B3 = [sorted(g3.sample(range(1, 44), 6)) for _ in range(3)]
    row3 = lambda t: sorted(((v - 1 + t // 3) % 49) + 1 for v in B3[t % 3])   # three interleaved rotations: the rule works at interval 3
    d3 = forecast([row3(t) for t in range(240)], 200)
    cases = [('the workbook\'s own 216 echo counters reproduced', cnt == 216),
             ('a planted sequence receives a forecast', a.get('issued', False)),
             ('and the forecast is the next row of the sequence, or within one number of it', a.get('issued') and len(set(a['forecast']) & set(nxt)) >= 5),
             ('a sequence without memory receives no forecast', not b.get('issued', True)),
             ('a slowly changing sequence receives no forecast: the rule beats shuffled history but not the latest row carried forward', not c.get('issued', True) and c['p'] < 0.05 and c['p_persistence'] >= 0.05),
             ('the interval is chosen on the first part only: changing a held-out value leaves it, and changes the data fingerprint', a2['h'] == a['h'] and a2['data'] != a['data']),
             ('a rule at interval 3 is found, and the forecast is the true next row', d3.get('issued') and d3['h'] == 3 and d3['forecast'] == row3(240))]
    counts = {d: len(reconstruct(2, advance((2, 5), d)[0], d)[0]) for d in range(1, 25)}
    cases += [('reconstruction from two values at interval d: one state at 18 intervals, three at 4, 8, 16 and 20, nine at 12 and 24, each checked by advancing it',
               sorted(d for d in counts if counts[d] == 1) == [d for d in range(1, 25) if d % 4] and [d for d in counts if counts[d] == 3] == [4, 8, 16, 20] and [d for d in counts if counts[d] == 9] == [12, 24]),
              ('the Square Reading: forward x2 and return x5 are inverse, x4 turns home in three, and a Crown value turns by thirds',
               square_reading(2)['forward'][1] == 4 and square_reading(4)['ret'][1] == 2 and square_reading(1)['turn'] == [1, 4, 7] and square_reading(3)['turn'] == [3, 6, 9]),
              ('the run manifest gives the same run ID for the same run', manifest('places', [1], {'a': 1}, 'x', 'places').split('\n')[1] == manifest('places', [1], {'a': 1}, 'x', 'places').split('\n')[1])]
    for nm, ok in cases: print('%s  %s' % ('PASS' if ok else 'FAIL', nm))
    print('  planted: ' + report(a)); print('  without memory: ' + report(b)); print('  slowly changing: ' + report(c)); print('  interval 3: ' + report(d3))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a[:1] == ['--places'] and len(a) == 13:
        v = [int(x) for x in a[1:]]; Y, X = v[:6], v[6:]; pl = places(Y, X)
        print('M326 PLACES: field Y = %s, numbers X = %s: %d recordings in %d of 27 domains' % (Y, X, len(pl), len({p[2] for p in pl})))
        for i, x in enumerate(X):
            ds = sorted({p[2] for p in pl if p[0] == i}); print('  X%d = %d: %d places, %d domains: %s' % (i + 1, x, sum(1 for p in pl if p[0] == i), len(ds), ' '.join(ds)))
        sys.exit(0)
    if a[:1] == ['--forecast'] and len(a) >= 2:
        rows, skipped = read_rows(a[1]); res = forecast(rows); line = report(res)
        print(line)
        if skipped: print('  INPUT: %d line(s) without six integers were not used: %s%s' % (len(skipped), skipped[:10], ' ...' if len(skipped) > 10 else ''))
        if '--manifest' in a:
            print(manifest('forecast', rows, {'cut': '60%', 'shuffles': 300, 'seed': 4227, 'intervals': res.get('searched'), 'skipped_lines': len(skipped)}, line.split(' (')[0], 'issued' if res.get('issued') else 'none'))
        sys.exit(0)
    if a[:1] == ['--reconstruct'] and len(a) >= 4:
        x, y, d = int(a[1]), int(a[2]), int(a[3]); sols, c1, c2 = reconstruct(x, y, d)
        line = 'x(n) = %d and x(n+%d) = %d: F(%d) = %d and F(%d) = %d mod 9; %d consistent state(s) (x(n), x(n+1)): %s' % (x, d, y, d - 1, c1, d, c2, len(sols), sols)
        print('M326 RECONSTRUCT: ' + line + ('' if len(sols) <= 1 else ' -- not unique: every one is kept, none is chosen'))
        if '--manifest' in a: print(manifest('reconstruct', [x, y, d], {'d': d}, line, 'reconstruct'))
        sys.exit(0)
    if a[:1] == ['--square'] and len(a) >= 2:
        t = a[1]
        if t.isdigit(): v, lab = int(t), ''
        else:
            sys.path.insert(0, os.path.join(REPO, 'scripts')); import canonical_reference as cr
            n = cr.navigate(t); v, lab = n['anchor_value'], ' of "%s" (anchor P%d = %d)' % (t, n['anchor'], n['anchor_value'])
        print(square_report(v, lab))
        if '--manifest' in a: print(manifest('square', [t], {}, 'value %d' % v, 'square'))
        sys.exit(0)
    print(__doc__)
