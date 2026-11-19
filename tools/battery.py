#!/usr/bin/env python3
"""battery.py -- M377 Capability Battery (Core Part 3.84; F192): tests that show at once whether Ω42's instruments work,
with their success and failure rates, run on every build.

  B1 identity handshake: canonical engine accepted; two structural impostors refused (single rounds and three-round tests)
  B2 the period and census laws at every level tested (orders k <= 8, census k <= 6, 531,441 states)
  B3 inverse reconstruction of 10,000 random states, k <= 12
  B4 Q^2 kept by A at every state mod 243; the share of states at which the shear B visibly breaks it
  B5 Author Seal: edited, dropped and reordered seals and a substituted final file, 50 random histories each
  B6 the interval kept by X -> A X A^T for 10,000 random integer events; reconciliation false alarms and detections
  B7 the paired-perturbation key: 11 canonical and perturbed items, each must flip or must stay
  B8 the Navigator's calibration on record (NAV-01 to NAV-03): accuracy, confidence, ECE, and the failure pattern

    python3 tools/battery.py            the full report
    python3 tools/battery.py --selftest each line against its threshold
Standard library only; seeded, so every run gives the same counts.
"""
import glob, json, math, os, random, re, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import handshake as h, authorseal as au, spacetime as st
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = h.A; TWIN = ((0, 1), (1, 7)); PELL = ((0, 1), (1, 2)); B = ((1, 0), (3, 1))


def run():
    R = random.Random(20261111); L = []
    def rec(name, ok, n, need):
        L.append((name, ok, n, need))
    rec('B1 canonical engine: three-round conformance tests accepted', sum(h.conform(s)[0] for s in range(300)), 300, 1.0)
    for nm, M in (('[[0,1],[1,7]]', TWIN), ('Pell [[0,1],[1,2]]', PELL)):
        resp = lambda k, s, n, M_=M: h.respond(k, s, n, M_)
        rec('B1 impostor %s: single rounds refused' % nm, sum(not h.challenge(s, resp)[3] for s in range(1000)), 1000, 0.99)
        rec('B1 impostor %s: three-round tests refused' % nm, sum(not h.conform(s, resp)[0] for s in range(300)), 300, 1.0)
    rec('B2 order of A = 8*3^(k-1), k = 1 to 8', sum(h.order(A, 3 ** k) == 8 * 3 ** (k - 1) for k in range(1, 9)), 8, 1.0)
    rec('B2 orbit census = (3^k+1)/2, k = 1 to 6', sum(h.census(A, 3 ** k) == (3 ** k + 1) // 2 for k in range(1, 7)), 6, 1.0)
    Ai = ((-1, 1), (1, 0)); ok = 0
    for _ in range(10000):
        m = 3 ** R.randint(1, 12); s = (R.randrange(m), R.randrange(m)); ok += h.act(Ai, h.act(A, s, m), m) == s
    rec('B3 inverse reconstruction, k = 1 to 12', ok, 10000, 1.0)
    m = 243; Q = lambda v: (2 * v[0] * v[0] + 2 * v[0] * v[1] - 2 * v[1] * v[1]) % m
    S = [(a, b) for a in range(m) for b in range(m)]
    rec('B4 Q^2 kept by A, every state mod 243', sum(Q(h.act(A, v, m)) ** 2 % m == Q(v) ** 2 % m for v in S), len(S), 1.0)
    rec('B4 Q^2 visibly changed by B, states mod 243 (the rest agree by chance)', sum(Q(h.act(B, v, m)) ** 2 % m != Q(v) ** 2 % m for v in S), len(S), 0.85)
    d = tempfile.mkdtemp(); det = dict(edit=0, drop=0, swap=0, final=0); N = 50
    for i in range(N):
        log = os.path.join(d, 'w%d.seal' % i); f = os.path.join(d, 'w%d.txt' % i)
        au.init(log, 'battery', seed=bytes([i]) * 32, now='2026-11-01T00:00:00Z'); txt = ''
        for j in range(4):
            txt += 'line %d %d\n' % (j, R.randrange(10 ** 6)); open(f, 'w').write(txt); au.seal(log, f, now='2026-11-0%dT00:00:00Z' % (j + 2))
        ls = open(log).read().splitlines()
        def bad(x):
            t = log + '.t'; open(t, 'w').write('\n'.join(x) + '\n'); return bool(au.verify(t)[0])
        e = json.loads(ls[2]); e['lines_added'] += 1
        det['edit'] += bad(ls[:2] + [json.dumps(e)] + ls[3:]); det['drop'] += bad(ls[:2] + ls[3:]); det['swap'] += bad(ls[:2] + [ls[3], ls[2]] + ls[4:])
        g = f + '.x'; open(g, 'w').write(txt + 'x'); det['final'] += bool(au.verify(log, final=g)[0])
    for k, v in det.items():
        rec('B5 Author Seal: %s detected' % k, v, N, 1.0)
    ok = 0
    for _ in range(10000):
        e = tuple(R.randint(-10 ** 6, 10 ** 6) for _ in range(4)); M = st.event_matrix(*e)
        ok += abs(st.det(st.act(M)) - st.det(M)) <= 1e-3 * max(1, abs(st.det(M)))
    rec('B6 interval kept by X -> A X A^T, random integer events', ok, 10000, 1.0)
    p = st.geodetic_to_ecef(-25.7479, 28.2293, 1339.0); fa = dt = 0; N = 2000; sg = 0.5 * math.sqrt(2)
    for _ in range(N):
        base = st.frame(p, 0.002, (0.5, -0.3, 0.1))
        fa += not st.reconcile(p, 0.5, tuple(v + R.gauss(0, sg) for v in base), 0.5, 0.002, (0.5, -0.3, 0.1))[1]
        dt += not st.reconcile(p, 0.5, tuple(v + R.gauss(0, sg) + (5 if i == 0 else 0) for i, v in enumerate(base)), 0.5, 0.002, (0.5, -0.3, 0.1))[1]
    rec('B6 reconcile: consistent observations accepted (99% bound)', N - fa, N, 0.98)
    rec('B6 reconcile: a 5 m displacement flagged', dt, N, 0.99)
    key = [(h.order(A, 27), 72, h.order(A, 25), 100, True), (per(A, (1, 0), 81), 216, per(A, (2, 0), 81), 216, False),
           (per(A, (1, 0), 81), 216, per(A, (3, 0), 81), 72, True), (h.census(A, 27), 14, h.census(TWIN, 27), 14, False),
           (h.census(A, 27), 14, h.census(PELL, 27), 14, False), (q(h.act(A, (1, 0), 10 ** 9)), -2, q((1, 3)), -10, True),
           (go(3), 5832, go(6), 5832, False), (go(3), 5832, go(9), 648, True), (go(3), 5832, go(1), 34992, True),
           (h.mpow(A, 100, 729)[0][1], 588, h.mpow(A, 100, 243)[0][1], 102, True), (half(7), True, half(11), False, True)]
    rec('B7 paired-perturbation key: answers and flip/stay verified', sum(a == b and c == d2 and ((a != c) == f) for a, b, c, d2, f in key), len(key), 1.0)
    rows = []
    for fp in sorted(glob.glob(os.path.join(ROOT, 'records', 'calibration', 'nav_run_0*.txt'))):
        for line in open(fp, encoding='utf-8'):
            mm = re.search(r'conf ([0-9.]+)\s+(RIGHT|WRONG)', line)
            if mm:
                rows.append((float(mm.group(1)), mm.group(2) == 'RIGHT'))
    rec('B8 Navigator answers right on record (NAV-01 to NAV-03)', sum(o for _, o in rows), len(rows), 0.9)
    return L, rows


def per(M, s, m):
    v, n = h.act(M, s, m), 1
    while v != s:
        v = h.act(M, v, m); n += 1
    return n


def q(v):
    return 2 * v[0] * v[0] + 2 * v[0] * v[1] - 2 * v[1] * v[1]


def go(c):
    return h.group_order([A, ((1, 0), (c, 1))], 27)


def half(p):
    o = h.order(A, p)
    return o % 2 == 0 and h.mpow(A, o // 2, p) == ((p - 1, 0), (0, p - 1))


def calibration(rows):
    acc = sum(o for _, o in rows) / len(rows); conf = sum(c for c, _ in rows) / len(rows); bins = {}
    for c, o in rows:
        bins.setdefault(min(int(c * 10), 9), []).append((c, o))
    ece = sum(len(b) / len(rows) * abs(sum(o for _, o in b) / len(b) - sum(c for c, _ in b) / len(b)) for b in bins.values())
    return acc, conf, ece


def main(a):
    L, rows = run(); acc, conf, ece = calibration(rows); ok = True
    for name, k, n, need in L:
        good = k / n >= need
        ok &= good
        print('%-66s %6d/%-6d %6.2f%%  %s' % (name, k, n, 100 * k / n, 'PASS' if good else 'FAIL'))
    print('%-66s %s' % ('B8 calibration: accuracy %.3f, mean confidence %.3f, ECE %.3f' % (acc, conf, ece), 'RECORDED (underconfident; agenda C-12)'))
    print('CAPABILITY BATTERY: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
