#!/usr/bin/env python3
"""calibrate.py -- M347 Calibration Instrument (Core Part 3.73, L-553, L-557).

Calibration compares a stated confidence, or a representation, with an independent reference. This instrument
scores a frozen prediction sheet against values it computes itself, and keeps three things apart: awareness of a
state (accuracy), awareness of the reliability of that awareness (calibration), and experience itself (not
measured by anything here).

    python3 tools/calibrate.py --score FILE      score a frozen sheet "n | predicted | confidence" (task: Pisano periods)
    python3 tools/calibrate.py --registry        the calibration registry: what Ω42 maps and what it calibrates
    python3 tools/calibrate.py --instrument      calibrating the calibrator: synthetic observers of known calibration
    python3 tools/calibrate.py --encoding        the F171 encoding into F_3^2, and what the canonical law predicts of it
    python3 tools/calibrate.py --template        a blank sheet for a human run (the Originator's own calibration)
    python3 tools/calibrate.py --selftest
Standard library only; every random draw is seeded, so every output is reproducible.
"""
import hashlib, random, sys


def pisano(n):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % n; k += 1
        if (a, b) == (0, 1 % n):
            return k


def read_sheet(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        p = [x.strip() for x in line.split('|')]
        if len(p) == 3 and p[0].isdigit():
            rows.append((int(p[0]), int(p[1]), float(p[2])))
    return rows


def metrics(conf, hit):
    """accuracy, mean confidence, Brier score, expected calibration error over the distinct confidence values."""
    N = len(conf)
    acc = sum(hit) / N; mc = sum(conf) / N
    brier = sum((c - h) ** 2 for c, h in zip(conf, hit)) / N
    bins = {}
    for c, h in zip(conf, hit):
        bins.setdefault(c, []).append(h)
    ece = sum(len(v) / N * abs(c - sum(v) / len(v)) for c, v in bins.items())
    return acc, mc, brier, ece, bins


def dprime(hits, misses, fas, crs):
    """signal-detection sensitivity d' with the log-linear correction (for a human detection run)."""
    from statistics import NormalDist
    z = NormalDist().inv_cdf
    H = (hits + 0.5) / (hits + misses + 1); F = (fas + 0.5) / (fas + crs + 1)
    return z(H) - z(F)


def q3(u):
    return 0 if u < 1 / 3 else 1 if u < 2 / 3 else 2


def encode(D, ece):
    return (q3(D), q3(1 - min(1.0, ece)))


def A(x, m=3):
    return (x[1] % m, (x[0] + x[1]) % m)


def H(x, d):
    """Round half to even after removing float noise, so every Python version prints the same digits."""
    from decimal import Decimal, ROUND_HALF_EVEN
    return str(Decimal(repr(round(x, 9))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_EVEN))


def score(path):
    raw = open(path, 'rb').read()
    rows = read_sheet(path)
    conf = [c for _, _, c in rows]; truth = [pisano(n) for n, _, _ in rows]
    hit = [1 if p == t else 0 for (_, p, _), t in zip(rows, truth)]
    acc, mc, brier, ece, bins = metrics(conf, hit)
    L = ['======= M347 CALIBRATION RUN =======',
         'SHEET: %s | SHA-256 %s | %d predictions' % (path.split('/')[-1], hashlib.sha256(raw).hexdigest(), len(rows)),
         'REFERENCE: the Pisano period computed exactly by this script (independent of the sheet)', '']
    for (n, p, c), t, h in zip(rows, truth, hit):
        L.append('  n=%-3d predicted %-4d true %-4d conf %.2f  %s' % (n, p, t, c, 'RIGHT' if h else 'WRONG'))
    L += ['', 'BY CONFIDENCE (stated -> observed):']
    for c in sorted(bins):
        v = bins[c]
        L.append('  %.2f  n=%-2d  observed %.2f  gap %+.2f' % (c, len(v), sum(v) / len(v), sum(v) / len(v) - c))
    over = mc - acc
    L += ['',
          'LEVEL 1, awareness of the state (accuracy D): %s' % H(acc, 3),
          'LEVEL 2, awareness of its reliability: mean confidence %s; ECE %s; Brier %s (always 0.5 scores 0.25)' % (H(mc, 3), H(ece, 3), H(brier, 4)),
          'DIRECTION: %s by %s' % ('OVERCONFIDENT' if over > 0.005 else 'UNDERCONFIDENT' if over < -0.005 else 'CALIBRATED', H(abs(over), 3)),
          'RESOLUTION: confidence on wrong answers %s vs on right answers %s' % (
              H(sum(c for c, h in zip(conf, hit) if not h) / max(1, hit.count(0)), 3),
              H(sum(c for c, h in zip(conf, hit) if h) / max(1, hit.count(1)), 3)),
          'Ω42 ENCODING (F171, coarse, F_3^2): x = %s; the canonical law sends it to %s' % (encode(acc, ece), A(encode(acc, ece))),
          'LEVEL 3, experience: NOT MEASURED -- nothing here reaches what it is like to know (L-557).',
          '======= END M347 CALIBRATION RUN =======']
    return '\n'.join(L), dict(acc=acc, mc=mc, brier=brier, ece=ece, n=len(rows))


REGISTRY = [
    # (class, object, Ω42 representation, reference for calibration, status)
    ('A', 'integer pairs and modular states', '(a, b) in (Z/3^k)^2', 'exact arithmetic', 'E'),
    ('A', 'the Fibonacci recurrence and its powers', 'A, A^n = [[F(n-1),F(n)],[F(n),F(n+1)]]', 'exact', 'E'),
    ('A', 'Pisano periods of every modulus', 'ord_n(A)', 'computed; prime classes MF-41', 'E'),
    ('A', 'the norm and its square', 'N, Q = 2N, Q^2', 'exact (MF-39)', 'E'),
    ('A', 'divisibility depth', 'v_3(x)', 'exact', 'E'),
    ('A', 'orbit censuses at every level', '(3^k+1)/2 orbits', 'exact (MF-10)', 'E'),
    ('A', 'operation histories and the shear groups', 'words in A, B_r', 'exact (MF-42, MF-43)', 'E'),
    ('A', 'the Lorentz representation', 'X -> A X A^T on Hermitian 2x2', 'exact (CERT-0009)', 'E'),
    ('A', 'the joint space and its spectra', '(Z/m)^2 x M_2(Z/m)', 'exact (MF-46, MF-47)', 'E'),
    ('B', 'periodic and cyclic signals', 'a phase on a finite orbit', 'period and phase error against an instrument', 'C'),
    ('B', 'repeated measurements of one quantity', 'a state sequence x_n', 'repeatability, measurement error', 'C'),
    ('B', 'discrete dynamical systems', 'a transition operator', 'prediction error on held-out steps', 'C'),
    ('B', 'confidence statements of a Navigator or a person', 'confidence and outcome pairs', 'ECE, Brier, against computed truth', 'C'),
    ('B', 'predictions sealed before the outcome (Return Log, M311)', 'sealed expectation and outcome', 'hit rate, Brier', 'C'),
    ('B', 'agreement between Navigators (SR-CAS)', 'the same coordinate, two readings', 'inter-rater agreement', 'C'),
    ('C', 'perceptual detection', 'detection rate, d-prime', 'stimulus present or absent', 'P/C'),
    ('C', 'metacognitive accuracy', 'confidence against accuracy', 'ECE, meta-d-prime', 'C'),
    ('C', 'attention', 'performance under load', 'task measures', 'P'),
    ('C', 'working memory', 'recall over time', 'task measures', 'P/C'),
    ('C', 'self-monitoring', 'error detection, self-correction', 'known errors', 'P/C'),
    ('C', 'level of consciousness (clinical)', 'an ordinal scale', 'GCS, PCI, anaesthesia depth', 'P'),
    ('D', 'subjective experience', 'first-person reports kept as text', 'none independent of report', 'O'),
    ('D', 'the qualitative character of experience', 'none', 'none', 'O'),
    ('D', 'consciousness as such (ground, act, event, L-498)', 'the frame, not a measurement', 'none', 'O'),
]


def registry():
    L = ['======= M347 THE CALIBRATION REGISTRY (Core L-557) =======',
         'STATUS: E exact mathematical mapping | C calibratable against an independent reference | P proxy of the',
         'intended phenomenon | O open, no defensible correspondence. A mapping (into Ω42) is not a calibration (against a',
         'reference), and a calibration is not an explanation.']
    names = {'A': 'CLASS A -- exact objects of the arithmetic', 'B': 'CLASS B -- external objects with a reference',
             'C': 'CLASS C -- awareness-related observables', 'D': 'CLASS D -- the open targets'}
    cur = None
    for cl, obj, rep, ref, st in REGISTRY:
        if cl != cur:
            L.append(''); L.append(names[cl]); cur = cl
        L.append('  [%-3s] %-52s %s | reference: %s' % (st, obj, rep, ref))
    L.append('======= END REGISTRY =======')
    return '\n'.join(L)


def instrument():
    """synthetic observers of known calibration: does the scoring recover what was built in?"""
    rng = random.Random(42)
    L = ['======= M347 CALIBRATING THE CALIBRATOR (seed 42, 2000 trials each) =======']
    out = {}
    for name, bias in (('calibrated', 0.0), ('overconfident', 0.15), ('underconfident', -0.15)):
        conf, hit = [], []
        for _ in range(2000):
            p = rng.choice([0.55, 0.65, 0.75, 0.85, 0.95])          # the observer's true chance of being right
            c = min(0.99, max(0.5, round(p + bias, 2)))              # what it states
            conf.append(c); hit.append(1 if rng.random() < p else 0)
        acc, mc, br, ece, _ = metrics(conf, hit)
        out[name] = (mc - acc, ece)
        L.append('  %-15s built-in gap %+.2f | recovered gap %+.3f | ECE %.3f | Brier %.4f' % (name, bias, mc - acc, ece, br))
    L.append('READING: the instrument recovers the built-in direction and size within sampling error; it is fit to score a sheet.')
    L.append('======= END =======')
    return '\n'.join(L), out


def encoding():
    nz = [(a, b) for a in range(3) for b in range(3) if (a, b) != (0, 0)]
    orbit = [(2, 2)]
    while True:
        y = A(orbit[-1])
        if y == orbit[0]:
            break
        orbit.append(y)
    Q2 = sorted(set(((2 * (a * a + a * b - b * b)) ** 2) % 3 for a, b in nz))
    fixed = [x for x in nz if A(x) == x]
    L = ['======= M347 THE F171 ENCODING, EXAMINED =======',
         'ENCODING: x = (q(D), q(1 - ECE)) in F_3^2, three levels each.',
         'ORBIT OF (2,2) UNDER A: %s -- one cycle through all 8 nonzero profiles' % ' -> '.join(map(str, orbit)),
         'NONZERO FIXED PROFILES OF A: %s -- the canonical law has none, at any level' % (fixed or 'none'),
         'Q^2 MOD 3 ON NONZERO PROFILES: %s -- the invariant is constant, so at this resolution it carries no information' % Q2,
         'PREDICTION (testable): if awareness followed the canonical law, no profile would persist from one step to the next,',
         '  and every profile would return after exactly 8 steps (A^8 = I mod 3). A stable observer refutes the first at once;',
         '  the 8-step return is the signature to look for in a series of sessions.',
         'WRAP: (2,2) -> (2,1): high detection with high calibration is sent to high detection with middle calibration by the',
         '  modular sum 2 + 2 = 4 = 1 (mod 3) -- a wrap, not a decline; ordinal scales are not residues.',
         'THEREFORE: the encoding is a valid mapping (status E as arithmetic) and an untested model (status O as a law of',
         '  awareness). Persistence is the baseline any Ω42 dynamics must beat on held-out sessions (F171 Study D).',
         '======= END =======']
    return '\n'.join(L), dict(orbit_len=len(orbit), fixed=fixed, Q2=Q2)


TEMPLATE = """CALIBRATION SHEET (M347) -- a human run. Write every line BEFORE you look anything up, then seal the file
(python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest())" FILE)
and only then score it. Task: the Pisano period pi(n). Confidence from 0.50 (a guess) to 0.99.
FORMAT: n | predicted pi(n) | confidence
2 |  |
5 |  |
7 |  |
10 |  |
12 |  |
"""


def selftest():
    ok = True
    cases = [
        ('pisano(9) = 24, pisano(5) = 20, pisano(10) = 60', pisano(9) == 24 and pisano(5) == 20 and pisano(10) == 60),
        ('a perfect sheet scores ECE 0 and Brier 0', metrics([1.0, 1.0], [1, 1])[3] == 0 and metrics([1.0, 1.0], [1, 1])[2] == 0),
        ('a 0.5 sheet scores Brier 0.25', abs(metrics([0.5] * 4, [1, 0, 1, 0])[2] - 0.25) < 1e-12),
        ('ECE of 0.8 stated, 0.5 observed is 0.3', abs(metrics([0.8] * 4, [1, 0, 1, 0])[3] - 0.3) < 1e-12),
        ("d' is 0 at chance and positive above it", abs(dprime(10, 10, 10, 10)) < 1e-9 and dprime(18, 2, 2, 18) > 1.5),
        ('the encoding: D = 0.85, ECE = 0.04 gives (2, 2), and A sends it to (2, 1)', encode(0.85, 0.04) == (2, 2) and A((2, 2)) == (2, 1)),
    ]
    _, e = encoding()
    cases.append(('the canonical law has one 8-cycle on nonzero profiles and no nonzero fixed profile', e['orbit_len'] == 8 and not e['fixed']))
    cases.append(('Q^2 is constant (1) on nonzero profiles mod 3', e['Q2'] == [1]))
    _, o = instrument()
    cases.append(('the instrument recovers the three built-in directions', o['calibrated'][0] < 0.03 and abs(o['calibrated'][0]) < 0.03
                  and o['overconfident'][0] > 0.10 and o['underconfident'][0] < -0.08))
    cases.append(('the registry keeps experience OPEN', all(st == 'O' for cl, *_, st in REGISTRY if cl == 'D')))
    for name, good in cases:
        print('  %-90s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('CALIBRATION INSTRUMENT SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--score']:
        print(score(a[1])[0])
    elif a == ['--registry']:
        print(registry())
    elif a == ['--instrument']:
        print(instrument()[0])
    elif a == ['--encoding']:
        print(encoding()[0])
    elif a == ['--template']:
        print(TEMPLATE)
    elif a == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    else:
        print(__doc__)
