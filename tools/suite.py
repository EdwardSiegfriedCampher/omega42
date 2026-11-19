#!/usr/bin/env python3
"""suite.py -- the Ω42 Instrument Suite (Core Part 3.75; APE-434, F173): one mathematical engine and seven instruments.

Two modes are kept apart in every output (Core L-559):
  MODE A, mathematical exploration -- A, B and the invariants applied to the state space; no empirical statement;
  MODE B, empirical modelling      -- a transformation used on data only with interpreted variables, tested on
                                      held-out data against a baseline; never assumed.
Raw observations are kept beside every encoding; the encoding never replaces the observation.

  M352 Dynamics Lab        python3 tools/suite.py lab K WORD A B          apply a word (e.g. ABA) step by step mod 3^K
                           python3 tools/suite.py lab --commute A B K     AB against BA on a state
  M353 Invariant Inspector python3 tools/suite.py inspect A B K [C D]     invariants, orbits under <A> and <A,B>, reachability
  M354 Ω42-Cal (trials)    python3 tools/suite.py cal FILE [K]            detection trials: stimulus,response,confidence,rt
  M355 Ω42-Percept         python3 tools/suite.py percept FILE            intensity,correct: psychometric threshold and slope
  M356 Ω42-Attend          python3 tools/suite.py attend FILE [BINS]      time,target,response,rt: profile by interval
  M357 Ω42-Memory          python3 tools/suite.py memory FILE             studied,said_old,confidence,corrected: memory profile
  M358 Ω42-Context         python3 tools/suite.py context FILE1 FILE2     the same task in two contexts: what changed
  M359 Protocol Builder    python3 tools/suite.py protocol FILE.json      a study record checked; --template for a blank
  M360 Invariant Sentinel  python3 tools/suite.py sentinel FILE K GROUP   a stream of states checked against the invariants
                                                                       of the declared group (A or AB); flags violations
  M361 Model Verifier      python3 tools/suite.py verify FILE K          persistence, the canonical law and the class mean
                                                                       compared on a state series, one step ahead
  M362 Protocol Designer   python3 tools/suite.py design P1 P2 PRIOR     the experiment that best separates two models
                                                                       (expected information gain, Bernoulli outcomes)
  M352 also: python3 tools/suite.py lab --commutator K   the commutator ABA^-1B^-1 mod 3^K
  python3 tools/suite.py demo DIR      writes the ILLUSTRATIVE seeded datasets (synthetic, not observations of anyone)
  python3 tools/suite.py recover       calibrating the instruments on synthetic observers of known parameters
  python3 tools/suite.py --selftest
Standard library only; every random draw is seeded.
"""
import json, math, os, random, sys
from statistics import NormalDist, mean, pstdev

Z = NormalDist().inv_cdf
A = (0, 1, 1, 1)
B = (1, 0, 3, 1)


# ---------------------------------------------------------------- the engine (MODE A)
def app(X, v, m):
    return ((X[0] * v[0] + X[1] * v[1]) % m, (X[2] * v[0] + X[3] * v[1]) % m)


def Q(a, b):
    return 2 * (a * a + a * b - b * b)


def val(v, k):
    m = 3 ** k; a, b = v[0] % m, v[1] % m
    if a == 0 and b == 0:
        return k
    j = 0
    while a % 3 == 0 and b % 3 == 0:
        a //= 3; b //= 3; j += 1
    return j


def orbit(v, gens, m):
    seen = {v}; st = [v]
    while st:
        x = st.pop()
        for g in gens:
            y = app(g, x, m)
            if y not in seen:
                seen.add(y); st.append(y)
    return seen


def run_word(word, v, k):
    m = 3 ** k; hist = [('start', v)]
    for ch in word.upper():
        v = app({'A': A, 'B': B}[ch], v, m); hist.append((ch, v))
    return hist


def qk(u, k):
    """F173 encoding: round((3^k - 1) u) for u in [0, 1]; an ordinal level written as a residue."""
    return int(round((3 ** k - 1) * min(1.0, max(0.0, u))))


# ---------------------------------------------------------------- measures (MODE B inputs)
def rates(rows):
    s = [r for r in rows if r[0] == 1]; n = [r for r in rows if r[0] == 0]
    hits = sum(r[1] for r in s); fas = sum(r[1] for r in n)
    H = (hits + 0.5) / (len(s) + 1); F = (fas + 0.5) / (len(n) + 1)       # log-linear correction
    return H, F, Z(H) - Z(F), -(Z(H) + Z(F)) / 2


def calib(conf, correct):
    N = len(conf); bins = {}
    for c, h in zip(conf, correct):
        b = min(4, int((c - 0.5) / 0.1)) if c >= 0.5 else 0
        bins.setdefault(b, []).append((c, h))
    ece = sum(len(v) / N * abs(mean(c for c, _ in v) - mean(h for _, h in v)) for v in bins.values())
    brier = mean((c - h) ** 2 for c, h in zip(conf, correct))
    pos = [c for c, h in zip(conf, correct) if h]; neg = [c for c, h in zip(conf, correct) if not h]
    auc = None
    if pos and neg:   # type-2 AUROC: P(confidence on a right answer > on a wrong one); 0.5 = no resolution
        auc = mean((1.0 if p > q else 0.5 if p == q else 0.0) for p in pos for q in neg)
    return ece, brier, auc


def read_csv(path):
    out = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#') or line[0].isalpha():
            continue
        out.append([float(x) for x in line.split(',')])
    return out


def cal(path, k=2):
    rows = [(int(r[0]), int(r[1]), r[2], r[3]) for r in read_csv(path)]
    H, F, d, c = rates(rows)
    correct = [1 if s == r else 0 for s, r, _, _ in rows]
    ece, brier, auc = calib([r[2] for r in rows], correct)
    acc = mean(correct)
    odd = [r for i, r in enumerate(rows) if i % 2]; even = [r for i, r in enumerate(rows) if not i % 2]
    d1, d2 = rates(odd)[2], rates(even)[2]
    x = (qk(acc, k), qk(1 - min(1.0, ece), k))
    return dict(n=len(rows), hit=H, fa=F, dprime=d, criterion=c, accuracy=acc, ece=ece, brier=brier, auroc2=auc,
                split=(d1, d2), rt=mean(r[3] for r in rows), x=x, Ax=app(A, x, 3 ** k), k=k)


def fit_psychometric(rows, gamma=0.5, lam=0.02):
    """P(correct | s) = gamma + (1 - gamma - lam) / (1 + exp(-beta (s - theta))); grid maximum likelihood."""
    xs = [r[0] for r in rows]; lo, hi = min(xs), max(xs); best = None
    for i in range(201):
        th = lo + (hi - lo) * i / 200
        for j in range(1, 121):
            be = j * 0.25 / max(1e-9, (hi - lo)) * 4
            ll = 0.0
            for s, y in rows:
                p = gamma + (1 - gamma - lam) / (1 + math.exp(-be * (s - th)))
                ll += math.log(p if y else 1 - p)
            if best is None or ll > best[0]:
                best = (ll, th, be)
    return best[1], best[2]


def attend(path, bins=4):
    rows = read_csv(path); rows.sort(key=lambda r: r[0])
    T0, T1 = rows[0][0], rows[-1][0] + 1e-9; out = []
    for b in range(bins):
        seg = [r for r in rows if T0 + (T1 - T0) * b / bins <= r[0] < T0 + (T1 - T0) * (b + 1) / bins]
        tg = [r for r in seg if r[1] == 1]
        D = rates([(int(r[1]), int(r[2])) for r in seg])[2]
        rts = [r[3] for r in seg if r[2] == 1 and r[1] == 1]
        V = pstdev(rts) if len(rts) > 1 else 0.0
        O = mean(1 - r[2] for r in tg) if tg else 0.0
        R = mean(1 if r[1] == r[2] else 0 for r in seg)
        out.append(dict(interval=b + 1, D=D, V=V, O=O, R=R))
    return out


def memory(path):
    rows = [(int(r[0]), int(r[1]), r[2], int(r[3])) for r in read_csv(path)]   # studied, said_old, confidence, corrected
    H, F, d, c = rates([(s, o) for s, o, _, _ in rows])
    correct = [1 if s == o else 0 for s, o, _, _ in rows]
    ece, brier, auc = calib([r[2] for r in rows], correct)
    errs = [r for r, ok in zip(rows, correct) if not ok]
    U = mean(r[3] for r in errs) if errs else None
    return dict(recognition=mean(correct), hits=H, false_memories=F, dprime=d, ece=ece, auroc2=auc, error_recognition=U)


def context(p1, p2, k=2):
    a, b = cal(p1, k), cal(p2, k)
    delta = {key: b[key] - a[key] for key in ('accuracy', 'dprime', 'criterion', 'ece', 'rt')}
    causes = []
    if abs(delta['dprime']) > 0.3:
        causes.append('sensitivity (d\' %+.2f)' % delta['dprime'])
    if abs(delta['criterion']) > 0.2:
        causes.append('response bias (c %+.2f)' % delta['criterion'])
    if abs(delta['ece']) > 0.05:
        causes.append('confidence calibration (ECE %+.2f)' % delta['ece'])
    return a, b, delta, causes


PROTOCOL_FIELDS = ['study', 'target', 'measurements', 'encoding', 'transformation', 'mode', 'validation', 'baseline',
                   'success_criterion', 'failure_criterion', 'frozen_utc', 'raw_data_kept']


def protocol_check(d):
    P = [f for f in PROTOCOL_FIELDS if not d.get(f)]
    if d.get('mode') not in ('A', 'B'):
        P.append('mode must be A (exploration) or B (empirical modelling)')
    if d.get('mode') == 'B' and 'held-out' not in str(d.get('validation', '')).lower():
        P.append('MODE B needs held-out validation')
    if d.get('mode') == 'B' and not d.get('baseline'):
        P.append('MODE B needs a baseline')
    if d.get('raw_data_kept') not in (True, 'yes'):
        P.append('the raw data must be kept beside the encoding')
    return P


TEMPLATE = {f: '' for f in PROTOCOL_FIELDS}


# ---------------------------------------------------------------- illustrative data and recovery
def synth_detection(rng, n, dprime, crit, conf_bias=0.0):
    rows = []
    for i in range(n):
        s = 1 if rng.random() < 0.5 else 0
        e = rng.gauss(dprime / 2 if s else -dprime / 2, 1)
        r = 1 if e > crit else 0
        p_ok = NormalDist().cdf(abs(e - crit))          # an ideal observer's chance of being right
        c = min(0.99, max(0.5, p_ok + conf_bias + rng.gauss(0, 0.03)))
        rows.append((s, r, round(c, 2), round(0.35 + 0.15 * rng.random() + (0.05 if not r else 0), 3)))
    return rows


def write(path, header, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# ILLUSTRATIVE, synthetic (seeded); not an observation of anyone\n' + header + '\n')
        for r in rows:
            f.write(','.join(str(x) for x in r) + '\n')


def demo(d):
    os.makedirs(d, exist_ok=True); rng = random.Random(173)
    write(os.path.join(d, 'cal_quiet.csv'), 'stimulus,response,confidence,rt', synth_detection(rng, 200, 1.8, 0.0))
    write(os.path.join(d, 'cal_noisy.csv'), 'stimulus,response,confidence,rt', synth_detection(rng, 200, 0.9, 0.3, 0.08))
    pr = []
    for s in [i / 10 for i in range(1, 11)] * 20:
        p = 0.5 + 0.48 / (1 + math.exp(-12 * (s - 0.45)))
        pr.append((s, 1 if rng.random() < p else 0))
    write(os.path.join(d, 'percept.csv'), 'intensity,correct', pr)
    at = []
    for t in range(400):
        tg = 1 if rng.random() < 0.3 else 0
        dp = 2.2 - 1.4 * t / 400
        e = rng.gauss(dp / 2 if tg else -dp / 2, 1)
        at.append((t, tg, 1 if e > 0 else 0, round(0.4 + rng.gauss(0, 0.03 + 0.08 * t / 400), 3)))
    write(os.path.join(d, 'attend.csv'), 'time,target,response,rt', at)
    me = []
    for i in range(60):
        st = 1 if i < 30 else 0
        e = rng.gauss(0.75 if st else -0.75, 1)
        o = 1 if e > 0 else 0
        c = round(min(0.99, max(0.5, NormalDist().cdf(abs(e)) + rng.gauss(0, 0.05))), 2)
        me.append((st, o, c, 1 if (o != st and rng.random() < 0.6) else 0))
    write(os.path.join(d, 'memory.csv'), 'studied,said_old,confidence,corrected', me)
    json.dump(dict(study='Metacognitive awareness, pilot', target='confidence-accuracy correspondence',
                   measurements='detection, confidence, response time', encoding='(q_2(accuracy), q_2(1 - ECE)) in (Z/9)^2',
                   transformation='canonical A tested against persistence, not assumed', mode='B',
                   validation='held-out sessions, split-half d-prime', baseline='persistence and a linear trend',
                   success_criterion='lower held-out error than both baselines', failure_criterion='no improvement, or an unstable encoding',
                   frozen_utc='2026-11-11T13:30:00Z', raw_data_kept=True),
              open(os.path.join(d, 'protocol_pilot.json'), 'w'), indent=1)


def recover():
    rng = random.Random(7); out = []
    for dp, cr in ((0.5, 0.0), (1.5, 0.0), (1.5, 0.5), (2.5, -0.3)):
        rows = synth_detection(rng, 4000, dp, cr)
        H, F, d, c = rates(rows)
        out.append((dp, cr, d, c))
    return out


# ---------------------------------------------------------------- F174: sentinel, verifier, designer
def mat_mul(X, Y, m):
    return ((X[0] * Y[0] + X[1] * Y[2]) % m, (X[0] * Y[1] + X[1] * Y[3]) % m,
            (X[2] * Y[0] + X[3] * Y[2]) % m, (X[2] * Y[1] + X[3] * Y[3]) % m)


def commutator(k):
    m = 3 ** k; Ai = ((-1) % m, 1, 1, 0); Bi = (1, 0, (-3) % m, 1)
    return mat_mul(mat_mul(mat_mul(A, B, m), Ai, m), Bi, m)


def read_states(path):
    return [(int(r[0]), int(r[1])) for r in read_csv(path)]


def sentinel(states, k, group):
    m = 3 ** k; out = []
    for i in range(1, len(states)):
        x, y = states[i - 1], states[i]
        dv = val(x, k) != val(y, k)
        dq = Q(*x) ** 2 % m != Q(*y) ** 2 % m
        legal = y in ([app(A, x, m), app(((-1) % m, 1, 1, 0), x, m)] +
                      ([app(B, x, m), app((1, 0, (-3) % m, 1), x, m)] if group == 'AB' else []))
        if dv:
            out.append((i, 'VIOLATION: valuation changed -- impossible under either group'))
        elif dq and group == 'A':
            out.append((i, 'VIOLATION: Q^2 changed under the declared group <A>'))
        elif not legal:
            out.append((i, 'UNEXPLAINED: invariants kept but no single generator step explains it'))
    return out


def verify(states, k):
    m = 3 ** k; n = len(states) - 1; res = {}
    preds = {'persistence': lambda x, h: x, 'canonical A': lambda x, h: app(A, x, m)}
    for name, f in preds.items():
        res[name] = sum(1 for i in range(n) if f(states[i], None) == states[i + 1]) / n if n else 0.0
    # the class mean: predict the most frequent next state seen so far (a learned baseline)
    hits = 0; seen = {}
    for i in range(n):
        if seen:
            guess = max(seen, key=seen.get)
            hits += guess == states[i + 1]
        seen[states[i + 1]] = seen.get(states[i + 1], 0) + 1
    res['most frequent so far'] = hits / n if n else 0.0
    return res, n


def entropy(ps):
    return -sum(p * math.log2(p) for p in ps if p > 0)


def info_gain(p1, p2, prior=0.5):
    """two models predict success with p1 and p2 for one experiment; the expected reduction of uncertainty about the model."""
    H0 = entropy([prior, 1 - prior]); EH = 0.0
    for y in (1, 0):
        l1 = p1 if y else 1 - p1; l2 = p2 if y else 1 - p2
        py = prior * l1 + (1 - prior) * l2
        if py > 0:
            EH += py * entropy([prior * l1 / py, (1 - prior) * l2 / py])
    return H0 - EH


# ---------------------------------------------------------------- CLI
def fmt(v):
    return 'n/a' if v is None else ('%.3f' % v if isinstance(v, float) else str(v))


def main(a):
    if a[:1] == ['lab'] and a[1:2] == ['--commutator']:
        k = int(a[2]); c = commutator(k)
        print('M352 DYNAMICS LAB (MODE A): [A, B] = A B A^-1 B^-1 mod 3^%d = %s; %s; = I mod 3: %s (it lies in the congruence kernel, as MF-42 requires)' % (
            k, c, 'not the identity: A and B do not commute' if c != (1, 0, 0, 1 % 3 ** k) else 'the identity', tuple(x % 3 for x in c) == (1, 0, 0, 1)))
        return 0
    if a[:1] == ['sentinel']:
        st = read_states(a[1]); k = int(a[2]); g = a[3].upper()
        f = sentinel(st, k, g)
        print('M360 INVARIANT SENTINEL %s | %d states mod 3^%d | declared group <%s>' % (a[1].split('/')[-1], len(st), k, ','.join(g)))
        for i, msg in f:
            print('  step %d %s -> %s: %s' % (i, st[i - 1], st[i], msg))
        print('  %d flags' % len(f) if f else '  no flags: every step is a step of the declared group')
        return 0
    if a[:1] == ['verify']:
        st = read_states(a[1]); k = int(a[2]); r, n = verify(st, k)
        print('M361 MODEL VERIFIER %s | %d one-step predictions mod 3^%d (MODE B: the series is the held-out data)' % (a[1].split('/')[-1], n, k))
        for name, v in r.items():
            print('  %-22s %.3f' % (name, v))
        best = max(r, key=r.get)
        print('  READING: %s; with n = %d no model is preferred unless the difference survives a larger sample' % (
            'the canonical law does best' if best == 'canonical A' and r['canonical A'] > max(v for kk, v in r.items() if kk != 'canonical A') else 'the canonical law does not beat the baselines', n))
        return 0
    if a[:1] == ['design']:
        p1, p2 = float(a[1]), float(a[2]); pr = float(a[3]) if len(a) > 3 else 0.5
        print('M362 PROTOCOL DESIGNER: models predict %.2f and %.2f; prior %.2f; expected information gain %.4f bits per trial' % (p1, p2, pr, info_gain(p1, p2, pr)))
        return 0
    if a[:1] == ['lab'] and a[1:2] == ['--commute']:
        x, y, k = int(a[2]), int(a[3]), int(a[4]); m = 3 ** k
        ab = app(A, app(B, (x, y), m), m); ba = app(B, app(A, (x, y), m), m)
        print('M352 DYNAMICS LAB (MODE A) mod 3^%d from (%d, %d): AB -> %s, BA -> %s; %s' % (
            k, x, y, ab, ba, 'they differ: order matters' if ab != ba else 'equal on this state'))
        return 0
    if a[:1] == ['lab']:
        k, word, x, y = int(a[1]), a[2], int(a[3]), int(a[4])
        print('M352 DYNAMICS LAB (MODE A, no empirical statement) mod 3^%d; letters applied left to right (AB = A first, the matrix BA)' % k)
        for op, v in run_word(word, (x, y), k):
            print('  %-5s -> %-9s Q^2 mod 3^%d = %-3d valuation %d' % (op, v, k, Q(*v) ** 2 % 3 ** k, val(v, k)))
        return 0
    if a[:1] == ['inspect']:
        x, y, k = int(a[1]), int(a[2]), int(a[3]); m = 3 ** k; v = (x % m, y % m)
        o0, o1 = orbit(v, [A], m), orbit(v, [A, B], m)
        print('M353 INVARIANT AND REACHABILITY INSPECTOR (MODE A) state %s mod 3^%d' % (v, k))
        print('  Q^2 = %d (kept by <A>, not by <A,B>) | valuation %d (kept by both)' % (Q(*v) ** 2 % m, val(v, k)))
        print('  orbit under <A>: %d states | under <A,B>: %d states' % (len(o0), len(o1)))
        if len(a) > 5:
            t = (int(a[4]) % m, int(a[5]) % m)
            print('  target %s reachable: under <A> %s | under <A,B> %s' % (t, t in o0, t in o1))
        return 0
    if a[:1] == ['cal']:
        k = int(a[2]) if len(a) > 2 else 2; r = cal(a[1], k)
        print('M354 Ω42-CAL (trial level) %s | %d trials' % (a[1].split('/')[-1], r['n']))
        print('  LEVEL 1  hit %.3f  false alarm %.3f  d\' %.3f  criterion %+.3f  accuracy %.3f  mean RT %.3f s' % (
            r['hit'], r['fa'], r['dprime'], r['criterion'], r['accuracy'], r['rt']))
        print('  LEVEL 2  ECE %.3f  Brier %.4f  resolution (type-2 AUROC, 0.5 = none) %s' % (r['ece'], r['brier'], fmt(r['auroc2'])))
        print('  RELIABILITY  split-half d\' %.3f / %.3f' % r['split'])
        print('  Ω42 STATE (MODE A index, raw kept): x = %s mod 3^%d; A x = %s -- an index, not a prediction' % (r['x'], k, r['Ax']))
        print('  LEVEL 3  experience: not measured (L-557)')
        return 0
    if a[:1] == ['percept']:
        rows = [(r[0], int(r[1])) for r in read_csv(a[1])]
        th, be = fit_psychometric(rows)
        print('M355 Ω42-PERCEPT %s | %d trials | threshold theta %.3f | slope beta %.2f (gamma 0.5, lapse 0.02)' % (
            a[1].split('/')[-1], len(rows), th, be))
        return 0
    if a[:1] == ['attend']:
        bins = int(a[2]) if len(a) > 2 else 4
        print('M356 Ω42-ATTEND %s -- two Ω42 blocks per interval, (D, V) and (O, R), never one forced pair' % a[1].split('/')[-1])
        for r in attend(a[1], bins):
            print('  interval %d  D (d\') %.2f  V (RT sd) %.3f  O (omissions) %.2f  R (accuracy) %.2f' % (
                r['interval'], r['D'], r['V'], r['O'], r['R']))
        return 0
    if a[:1] == ['memory']:
        r = memory(a[1])
        print('M357 Ω42-MEMORY %s | recognition %.3f | hits %.3f | false memories %.3f | d\' %.3f | ECE %.3f | resolution %s | errors recognized %s' % (
            a[1].split('/')[-1], r['recognition'], r['hits'], r['false_memories'], r['dprime'], r['ece'], fmt(r['auroc2']), fmt(r['error_recognition'])))
        return 0
    if a[:1] == ['context']:
        x, y, dl, causes = context(a[1], a[2])
        print('M358 Ω42-CONTEXT %s -> %s' % (a[1].split('/')[-1], a[2].split('/')[-1]))
        print('  accuracy %+.3f | d\' %+.3f | criterion %+.3f | ECE %+.3f | RT %+.3f s' % tuple(dl[k] for k in ('accuracy', 'dprime', 'criterion', 'ece', 'rt')))
        print('  ATTRIBUTION: %s' % ('; '.join(causes) or 'no component beyond its threshold'))
        print('  READING: context is an explicit input; a deterministic model with context may explain all of this -- no nonclassical contextuality is asserted')
        return 0
    if a[:1] == ['protocol']:
        if a[1] == '--template':
            print(json.dumps(TEMPLATE, indent=1)); return 0
        P = protocol_check(json.load(open(a[1])))
        print('M359 PROTOCOL BUILDER %s: %s' % (a[1].split('/')[-1], 'PASS' if not P else 'FAIL: ' + '; '.join(P)))
        return 0 if not P else 1
    if a[:1] == ['demo']:
        demo(a[1]); print('ILLUSTRATIVE datasets written to %s' % a[1]); return 0
    if a[:1] == ['recover']:
        print('CALIBRATING THE INSTRUMENTS (seed 7, 4000 synthetic trials each)')
        for dp, cr, d, c in recover():
            print('  built-in d\' %.2f c %+.2f -> recovered d\' %.3f c %+.3f' % (dp, cr, d, c))
        return 0
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    print(__doc__); return 0


def selftest():
    import tempfile
    d = tempfile.mkdtemp(); demo(d)
    q, n = cal(os.path.join(d, 'cal_quiet.csv')), cal(os.path.join(d, 'cal_noisy.csv'))
    rec = recover()
    th, be = fit_psychometric([(r[0], int(r[1])) for r in read_csv(os.path.join(d, 'percept.csv'))])
    at = attend(os.path.join(d, 'attend.csv'))
    pc = protocol_check(json.load(open(os.path.join(d, 'protocol_pilot.json'))))
    bad = protocol_check(dict(TEMPLATE, mode='B'))
    cases = [
        ('F173 worked example corrected: from (1,1) mod 9, BA -> (1,5) and AB -> (4,5), not (5,6)',
         app(B, app(A, (1, 1), 9), 9) == (1, 5) and app(A, app(B, (1, 1), 9), 9) == (4, 5)),
        ('F173 sandbox: (0.85, 0.96) at 3^2 is (7,8); A -> (8,6); B -> (7,2); Q^2 = 1',
         (qk(.85, 2), qk(.96, 2)) == (7, 8) and app(A, (7, 8), 9) == (8, 6) and app(B, (7, 8), 9) == (7, 2) and Q(7, 8) ** 2 % 9 == 1),
        ('the inspector: (1,0) mod 9 has orbit 24 under <A> and 72 under <A,B>',
         len(orbit((1, 0), [A], 9)) == 24 and len(orbit((1, 0), [A, B], 9)) == 72),
        ('the recovery: d\' and c recovered within 0.15 at 4000 trials', all(abs(d - dp) < 0.15 and abs(c - cr) < 0.15 for dp, cr, d, c in rec)),
        ('the context comparator finds the built-in loss of sensitivity', context(os.path.join(d, 'cal_quiet.csv'), os.path.join(d, 'cal_noisy.csv'))[2]['dprime'] < -0.4),
        ('the psychometric fit finds the built-in threshold 0.45 within 0.1', abs(th - 0.45) < 0.1),
        ('the attention tracker finds the built-in decline of d\'', at[0]['D'] > at[-1]['D']),
        ('the pilot protocol passes and an empty MODE B protocol fails', not pc and len(bad) > 3),
        ('resolution is above chance for the ideal-observer data', q['auroc2'] > 0.6),
        ('F174: [A, B] mod 9 = (7, 3, 3, 4), not I, and = I mod 3', commutator(2) == (7, 3, 3, 4)),
        ('F174 prototype: (1,2) mod 9 -> A (2,3), B (1,5), Q^2 4, valuation 0; AB (5,6) vs BA (2,0)',
         app(A, (1, 2), 9) == (2, 3) and app(B, (1, 2), 9) == (1, 5) and Q(1, 2) ** 2 % 9 == 4
         and app(A, app(B, (1, 2), 9), 9) == (5, 6) and app(B, app(A, (1, 2), 9), 9) == (2, 0)),
        ('the sentinel passes a pure A stream, passes a shear step under <A,B>, flags it under <A>, and flags a valuation jump',
         not sentinel([(1, 0), (0, 1), (1, 1)], 2, 'A') and not sentinel([(1, 0), (1, 3)], 2, 'AB')
         and sentinel([(1, 0), (1, 3)], 2, 'A') and sentinel([(1, 0), (3, 0)], 2, 'AB')),
        ('the verifier scores the canonical law 1.0 on a canonical series and persistence 1.0 on a constant one',
         verify([(1, 0), (0, 1), (1, 1), (1, 2)], 2)[0]['canonical A'] == 1.0 and verify([(2, 2)] * 4, 2)[0]['persistence'] == 1.0),
        ('the designer: identical models give 0 bits; 0.9 against 0.1 gives about 0.531', info_gain(0.5, 0.5) == 0 and abs(info_gain(0.9, 0.1) - 0.531) < 0.001),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('Ω42 INSTRUMENT SUITE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
