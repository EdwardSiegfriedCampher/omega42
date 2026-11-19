#!/usr/bin/env python3
"""dsi.py -- the Discovery Significance Index (Companion Part 215.6, 215.7; Core Part 0.0.5 Rule 34; F210, APE-472).

Each result of the mathematical register (records/math/results.json) is scored one at a time, never Omega42 as a whole, on
six dimensions, 0 to 3, each score with its status and its reason:

  originality   is the result new, or a new arrangement of known mathematics
  rigor         is it established; 3 only when an exhaustive check or a proof runs in a tool
  unification   how many independent domains it connects
  explanation   does it say why the relationship holds
  prediction    did it anticipate a result before the result was computed (counts only flagged predictions)
  foundation    does it change the understanding of existence

and placed on one of six significance rungs: 1 a useful result, 2 a new framework or method, 3 a cross-domain
unification, 4 a new physical theory, 5 an architecture of existence, 6 a cognitive architecture of existence.

Five further fields (F213, F214): disciplines joined (counted only through an explicit map, theorem or construction),
connection depth, novelty, proof completeness and the structural mechanism that joins the disciplines.

Three further fields for each bridge from F216: the explicit mapping, the preserved properties and the predictive value. The
non-equivalence register records maps that fail, each with the results it rests on (F216; Companion Part 220).

Predicted before computed: a result counts as predicted only when its statement was sealed in an earlier record than its
check. Sealed predictions wait in the register, unchecked, until a later record runs --test on them.

The scores are ordinal judgments (CONSTRUCTED), uncalibrated against historical discoveries until PV-025 is closed;
rigor is EXACT when it rests on a tool's exhaustive check.

    python3 tools/dsi.py --list             the scored results and the sealed predictions
    python3 tools/dsi.py --check            every entry well formed; every flag agrees with the record
    python3 tools/dsi.py --test PR-NNN      check a sealed prediction (run only in a record later than its seal)
    python3 tools/dsi.py --maturity         the stages of maturity, proof completeness, novelty and depth, counted from the register
    python3 tools/dsi.py --selftest
Standard library only.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
REG = os.path.join(REPO, 'records', 'dsi', 'register.json')
MATH = os.path.join(REPO, 'records', 'math', 'results.json')
DIMS = ('originality', 'rigor', 'unification', 'explanation', 'prediction', 'foundation')
STAT = ('EXACT', 'CONDITIONAL', 'CONSTRUCTED', 'READING', 'REPORTED')
DEPTHS = ('shared constant', 'shared algebraic relation', 'equivalent transformation', 'structure-preserving map', 'theorem connecting the structures', 'new consequence or prediction')
NOVELTY = ('classical result reproduced', 'new Omega42 representation of a known result', 'new connection between known results', 'new theorem', 'new prediction', 'empirically supported prediction')
DISCIPLINE = ('model', 'parameters', 'expected', 'uncertainty', 'failure')   # Core Part 0.0.5 Rule 38, from PR-012
DISCIPLINE14 = ('convergence', 'verification')   # Companion 228.10, from PR-014
RETURN = ('REPRODUCED', 'NOT REPRODUCED', 'NOT ATTEMPTED', 'REPRODUCED IN PART')
PROOF = ('exact symbolic derivation', 'exhaustive finite verification', 'numerical approximation', 'independent implementation', 'external mathematical review')
MECHANISM = ('common eigenvalue', 'conjugate transformation', 'invariant-preserving map', 'representation embedding', 'group homomorphism', 'spectral decomposition', 'recurrence identity', 'dynamical conjugacy', 'geometric projection')
RUNGS = {1: 'a useful result', 2: 'a new framework or method', 3: 'a cross-domain unification', 4: 'a new physical theory',
         5: 'an architecture of existence', 6: 'a cognitive architecture of existence'}

def seqn(x): return int(re.match(r'seq_(\d{4})$', x).group(1)) if x and re.match(r'seq_(\d{4})$', x) else None
def load(path=REG): return json.load(open(path, encoding='utf-8'))
def mf_ids():
    try: return {r['id'] for r in json.load(open(MATH, encoding='utf-8'))['results']}
    except Exception: return set()

def problems(d, ids=None):
    ids = mf_ids() if ids is None else ids; P = []
    seen = set()
    for e in d.get('scores', []):
        tag = e.get('mf', '?')
        if tag in seen: P.append('%s scored twice' % tag)
        seen.add(tag)
        if ids and tag not in ids: P.append('%s is not in the mathematical register' % tag)
        if e.get('rung') not in RUNGS: P.append('%s: rung %r' % (tag, e.get('rung')))
        for k in DIMS:
            s = e.get('dims', {}).get(k)
            if not s or s.get('score') not in (0, 1, 2, 3): P.append('%s: %s has no score 0 to 3' % (tag, k)); continue
            if s.get('status') not in STAT: P.append('%s: %s status %r' % (tag, k, s.get('status')))
            if not s.get('reason'): P.append('%s: %s has no reason' % (tag, k))
        if not isinstance(e.get('disciplines'), int) or e['disciplines'] < 1: P.append('%s: disciplines joined' % tag)
        if e.get('depth') not in DEPTHS: P.append('%s: connection depth %r' % (tag, e.get('depth')))
        if e.get('novelty') not in NOVELTY: P.append('%s: novelty %r' % (tag, e.get('novelty')))
        if not e.get('proof') or any(x not in PROOF for x in e.get('proof', [])): P.append('%s: proof completeness %r' % (tag, e.get('proof')))
        if e.get('mechanism') not in MECHANISM: P.append('%s: structural mechanism %r' % (tag, e.get('mechanism')))
        if any(k in e for k in ('mapping', 'preserved', 'predictive')) and not all(isinstance(e.get(k), str) and e.get(k) for k in ('mapping', 'preserved', 'predictive')):
            P.append('%s: the mapping, the preserved properties and the predictive value go together' % tag)
        f = e.get('predicted_before_computed', {})
        a, b = seqn(f.get('predicted_in')), seqn(f.get('checked_in'))
        if f.get('checked_in') and b is None: P.append('%s: checked_in %r' % (tag, f.get('checked_in')))
        if f.get('flag') != (a is not None and b is not None and a < b): P.append('%s: the prediction flag disagrees with the records' % tag)
        if e.get('dims', {}).get('prediction', {}).get('score', 0) > 0 and not f.get('flag'): P.append('%s: a prediction score without a flagged prediction' % tag)
    nids = set()
    for n in d.get('non_equivalences', []):
        if not re.match(r'NE-\d{3}$', n.get('id', '')) or n['id'] in nids: P.append('non-equivalence id %r' % n.get('id'))
        nids.add(n.get('id'))
        if not n.get('statement') or not n.get('refs'): P.append('%s: statement and refs' % n.get('id'))
        for r in n.get('refs', []):
            if ids and r not in ids: P.append('%s: %s is not in the mathematical register' % (n.get('id'), r))
    pids = set()
    for p in d.get('predictions', []):
        if p.get('id') in pids: P.append('%s twice' % p.get('id'))
        pids.add(p.get('id'))
        if not re.match(r'PR-\d{3}$', p.get('id', '')): P.append('prediction id %r' % p.get('id'))
        if seqn(p.get('sealed_in')) is None: P.append('%s: sealed_in %r' % (p.get('id'), p.get('sealed_in')))
        if p.get('result') not in ('UNCHECKED', 'PASS', 'FAIL'): P.append('%s: result %r' % (p.get('id'), p.get('result')))
        if p.get('result') != 'UNCHECKED':
            c = seqn(p.get('checked_in'))
            if c is None or c <= seqn(p.get('sealed_in')): P.append('%s: checked in a record not later than its seal' % p.get('id'))
        if p.get('id') not in TESTS: P.append('%s: no test in this tool' % p.get('id'))
        if re.match(r'PR-\d{3}$', p.get('id', '')) and int(p['id'][3:]) >= 12 and not all(p.get(k) for k in DISCIPLINE):
            P.append('%s: the prediction discipline asks for %s' % (p.get('id'), ', '.join(DISCIPLINE)))
        if re.match(r'PR-\d{3}$', p.get('id', '')) and int(p['id'][3:]) >= 14 and not all(p.get(k) for k in DISCIPLINE14):
            P.append('%s: from PR-014 the discipline also asks for %s' % (p.get('id'), ', '.join(DISCIPLINE14)))
    rids = set(); reproduced = set()
    for r in d.get('replication_returns', []):
        if not re.match(r'RET-\d{3}$', r.get('id', '')) or r['id'] in rids: P.append('return id %r' % r.get('id'))
        rids.add(r.get('id'))
        if not r.get('implementer') or not r.get('date') or not isinstance(r.get('outcomes'), dict): P.append('%s: implementer, date and outcomes' % r.get('id'))
        for mf, o in (r.get('outcomes') or {}).items():
            if ids and mf not in ids: P.append('%s: %s is not in the mathematical register' % (r.get('id'), mf))
            if o not in RETURN: P.append('%s: %s outcome %r' % (r.get('id'), mf, o))
            if o == RETURN[0]: reproduced.add(mf)
    for e in d.get('scores', []):
        if (PROOF[3] in e.get('proof', [])) != (e.get('mf') in reproduced):
            P.append('%s: independent implementation stands in its proof exactly when a return reproduces it' % e.get('mf'))
    return P

# --- the tests of sealed predictions. A test is run in a record later than the prediction's seal. ---
def gen_full(p):
    """|<A, B>| mod p against 2p(p^2 - 1), the order of every matrix of determinant +-1."""
    A = (0, 1, 1, 1); B = (1, 0, 3 % p, 1)
    def m(X, Y): return ((X[0]*Y[0]+X[1]*Y[2]) % p, (X[0]*Y[1]+X[1]*Y[3]) % p, (X[2]*Y[0]+X[3]*Y[2]) % p, (X[2]*Y[1]+X[3]*Y[3]) % p)
    seen = {(1, 0, 0, 1)}; fr = [(1, 0, 0, 1)]
    while fr:
        nx = []
        for X in fr:
            for G in (A, B):
                Y = m(X, G)
                if Y not in seen: seen.add(Y); nx.append(Y)
        fr = nx
    return len(seen), 2 * p * (p * p - 1)
def pr001():
    primes = [q for q in range(23, 98) if all(q % r for r in range(2, int(q ** 0.5) + 1))]
    out = [(q,) + gen_full(q) for q in primes]
    return all(a == b for _, a, b in out), ['p = %d: |<A, B>| = %d, every determinant +-1 = %d' % x for x in out]
def qr_code_ext(p):
    """the extended binary quadratic-residue code of length p + 1, coordinates 0..p-1 and infinity (index p)"""
    Q = {(x * x) % p for x in range(1, p)}
    cands = []
    for S in (Q, set(range(1, p)) - Q, Q | {0}, (set(range(1, p)) - Q) | {0}):
        e = [1 if i in S else 0 for i in range(p)]
        rows = []
        for k in range(p):
            v = int(''.join(str(e[(i - k) % p]) for i in range(p)), 2)
            for r in rows: v = min(v, v ^ r)
            if v: rows.append(v)
        span = {0}
        for r in rows: span |= {x ^ r for x in span}
        words = [tuple(int(c) for c in format(x, '0%db' % p)) for x in span]
        cands.append([w + (sum(w) % 2,) for w in words])
    want = (p + 1) // 2
    good = [set(c) for c in cands if len(c) == 2 ** want]
    return good[0] if good else set()
def keeps_qr(p):
    """does <A^2, B> mod p, acting on the projective line, keep the extended QR code of length p + 1?"""
    C = qr_code_ext(p)
    def mob(M, z):
        a, b, c, d = M
        if z == p: return p if c % p == 0 else a * pow(c, -1, p) % p
        den = (c * z + d) % p
        return p if den == 0 else (a * z + b) * pow(den, -1, p) % p
    A2 = (1, 1, 1, 2); B = (1, 0, 3 % p, 1)
    ok = True
    for M in (A2, B):
        perm = [mob(M, z) for z in range(p + 1)]
        img = set()
        for w in C:
            v = [0] * (p + 1)
            for i in range(p + 1):
                if w[i]: v[perm[i]] = 1
            img.add(tuple(v))
        ok = ok and img == C
    return ok, C
def pr002():
    ok, C = keeps_qr(23)
    mw = min(sum(w) for w in C if any(w)) if C else 0
    return ok and len(C) == 4096 and mw == 8, ['the extended QR code of length 24: %d words, minimum weight %d (the extended Golay code is 4096 words, minimum weight 8)' % (len(C), mw),
                                              '<A^2, B> mod 23 keeps it: %s' % ok]
def gen_group(gens, p):
    e = (1, 0, 0, 1); G = {e}; fr = [e]
    m = lambda X, Y: ((X[0]*Y[0]+X[1]*Y[2]) % p, (X[0]*Y[1]+X[1]*Y[3]) % p, (X[2]*Y[0]+X[3]*Y[2]) % p, (X[2]*Y[1]+X[3]*Y[3]) % p)
    while fr:
        nx = []
        for X in fr:
            for g in gens:
                Y = m(X, g)
                if Y not in G: G.add(Y); nx.append(Y)
        fr = nx
    return G
def pr003():
    """the Fibonacci braid generators reduced at the prime above 11 (zeta_10 -> 2): s1 = [[9,0],[0,8]], s2 = [[2,5],[7,4]]"""
    G = gen_group([(9, 0, 0, 8), (2, 5, 7, 4)], 11)
    sl = sum(1 for X in G if (X[0] * X[3] - X[1] * X[2]) % 11 == 1)
    return sl == 1320, ['|<s1, s2>| = %d in GL2(F11); elements of determinant 1: %d (SL2(F11) has 1320)' % (len(G), sl)]
def pr004():
    """the quantized cat map: for every odd N from 27 to 51 the Weil operator of A^2 has period up to phase equal to the order of A^2 mod N"""
    import constructions as c
    A2 = [[1, 1], [1, 2]]; out = []; ok = True
    for N in range(27, 52, 2):
        q, k = c.proj_order(c.weil(A2, N), cap=2000), c.mat_order(A2, N)
        out.append('N = %d: quantum %s, classical %d' % (N, q, k)); ok = ok and q == k
    return ok, out
def pr005():
    """for every prime p from 101 to 499 other than 5: the order of A^2 modulo p divides (p - 1)/2 when p = +-1 mod 5, and divides p + 1 but not (p + 1)/2 when p = +-2 mod 5"""
    def order(M, p):
        X, k = M, 1
        while X != [[1, 0], [0, 1]]:
            X = [[(X[i][0] * M[0][j] + X[i][1] * M[1][j]) % p for j in range(2)] for i in range(2)]; k += 1
        return k
    ok = True; out = []; n = [0, 0]
    for p in range(101, 500):
        if any(p % q == 0 for q in range(2, int(p ** .5) + 1)): continue
        k = order([[1, 1], [1, 2]], p)
        if p % 5 in (1, 4): good = ((p - 1) // 2) % k == 0; n[0] += 1
        else: good = (p + 1) % k == 0 and ((p + 1) // 2) % k != 0; n[1] += 1
        ok = ok and good
        if not good: out.append('p = %d: order %d breaks it' % (p, k))
    out.append('%d primes with p = +-1 mod 5 and %d with p = +-2 mod 5 checked from 101 to 499' % tuple(n))
    return ok, out
def pr006():
    """the gap labels of the Fibonacci Hamiltonian at a new approximant and potential: length 987, V = 2"""
    import fibonacci_hamiltonian as fh
    gl, _ = fh.gaps(987, 2.0, 12)
    ok = len(gl) == 12 and all(err < 1.5 / 987 and abs(n) <= 20 for _, _, n, err in gl)
    return ok, ['gap of width %.4f: IDS %.6f, label n = %d, |IDS - frac(n/phi)| = %.2e' % g for g in gl]
def pr007():
    """the Thomas-Wigner angle of A^(2m) composed with S A^(2n) S, m, n = 1 to 4: rational cos w and sin w, w never zero"""
    from fractions import Fraction as F
    mm = lambda X, Y: [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
    def pw(X, n):
        R = [[1, 0], [0, 1]]
        for _ in range(n): R = mm(R, X)
        return R
    M = [[1, 1], [1, 2]]; N = [[2, 1], [1, 1]]; ok = True; out = []
    for m in range(1, 5):
        for n in range(1, 5):
            G = pw(M, m); H = pw(N, n); P_ = mm(G, H)
            th = F(P_[1][0] - P_[0][1], P_[0][0] + P_[1][1])
            c, s_ = (1 - th * th) / (1 + th * th), 2 * th / (1 + th * th)
            ok = ok and th != 0 and c * c + s_ * s_ == 1
            out.append('m = %d, n = %d: cos w = %s, sin w = %s' % (m, n, c, s_))
    return ok, out
def pr008():
    """the quarter-wave transmittance of Fibonacci stacks: T_(k+6) = T_k for k = 0 to 30, T_1 = T_4, T_2 = T_5, for every ordered pair of distinct indices from 4/3, 3/2, 2, 5/2, 3"""
    from fractions import Fraction as F
    import itertools, optics as o
    ok = True; out = []
    for nA, nB in itertools.permutations([F(4, 3), F(3, 2), F(2), F(5, 2), F(3)], 2):
        T = [o.trans(m) for m in o.stacks(o.qw_layer(nA), o.qw_layer(nB), 36)]
        good = all(T[k + 6] == T[k] for k in range(31)) and T[1] == T[4] and T[2] == T[5]
        ok = ok and good
        if not good: out.append('nA = %s, nB = %s breaks it' % (nA, nB))
    out.append('20 ordered pairs checked')
    return ok, out
def pr009():
    """the phason pump on 144 sites, approximant 89/144, V = 3, beta = 4: across each of the eight widest gaps the pumped charge is minus the gap label"""
    import waves
    res = waves.pump(3.0, L=144, p=89, betas=(4.0,), N=600, top=8)
    ok = len(res) == 8 and all(abs(tot + lab) < 1e-6 and big < 0.05 for _, _, _, lab, tot, big in res)
    return ok, ['gap width %.3f, states below %d: label %d, pumped charge %.6f' % (g, nf, lab, tot) for _, g, nf, lab, tot, _ in res]
def pr010():
    """the gap labels at V = 1.5 on the approximants of lengths 1597 and 2584: the same 24 labels, each by the congruence, and the gaps 1, -1, 2, -2 within 3 x 10^-4 of their width and center at 987"""
    import spectra as sp
    PHI = (1 + 5 ** .5) / 2
    want = [-17, -12, -11, -10, -9, -7, -6, -5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 17]
    def gaps(L, fprev):
        lo, hi = sp.spectrum(L, 1.5); out = {}; cong = True
        for i in range(L - 1):
            if lo[i + 1] - hi[i] >= 0.02:
                ids = (i + 1) / L
                n = min(range(-60, 61), key=lambda n: abs(((n / PHI - ids + 0.5) % 1) - 0.5))
                cong = cong and (i + 1 - n * fprev) % L == 0
                out[n] = (float(lo[i + 1] - hi[i]), float((lo[i + 1] + hi[i]) / 2))
        return out, cong
    ref, _ = gaps(987, 610); ok = True; L_ = []
    for L, fp in ((1597, 987), (2584, 1597)):
        g, cong = gaps(L, fp)
        good = sorted(g) == want and cong and all(abs(g[n][0] - ref[n][0]) < 3e-4 and abs(g[n][1] - ref[n][1]) < 3e-4 for n in (1, -1, 2, -2))
        ok = ok and good; L_.append('L = %d: %d gaps, labels %s, congruence %s' % (L, len(g), 'as at 987' if sorted(g) == want else sorted(g), cong))
    return ok, L_
def pr011():
    """the trace map modulo 64 and 128: bijections of period 96 and 192, the Pisano periods of the law"""
    import numpy as np, spectra as sp
    out = []; ok = True
    for m, want in ((64, 96), (128, 192)):
        s = np.arange(m ** 3, dtype=np.int64); x, y, z = s // (m * m), (s // m) % m, s % m
        T = ((2 * x * y - z) % m) * m * m + x * m + y
        bij = len(np.unique(T)) == m ** 3
        def power(n):
            R = np.arange(m ** 3, dtype=np.int64); B = T.copy()
            while n:
                if n & 1: R = B[R]
                B = B[B]; n >>= 1
            return R
        ident = np.arange(m ** 3, dtype=np.int64)
        per = min(d for d in range(1, 2 * want + 1) if (2 * want) % d == 0 and (power(d) == ident).all())
        ok = ok and bij and per == want == sp.pisano(m)
        out.append('modulo %d: bijection %s, period %d, Pisano period %d' % (m, bij, per, sp.pisano(m)))
    return ok, out
def pr012():
    """the weak-coupling gaps at V = 0.01 on length 1597, labels 1 to 6"""
    import spectra as sp, math
    PHI = (1 + 5 ** .5) / 2; V = 0.01; L = 1597; fprev = 987
    lo, hi = sp.spectrum(L, V); g = {}
    for i in range(L - 1):
        w = lo[i + 1] - hi[i]
        if w > 1e-5:
            n = min((n for n in range(-40, 41) if n and (i + 1 - n * fprev) % L == 0), key=abs, default=None)
            if n is not None and abs(n) <= 6: g[n] = float(w)
    ok = all(n in g and -n in g for n in range(1, 7)); out = []
    for n in range(1, 7):
        if not ok: break
        pred = 2 * V * abs(math.sin(math.pi * n / PHI)) / (math.pi * n); mean = (g[n] + g[-n]) / 2
        good = abs(mean / pred - 1) < 5e-4 and abs(g[n] / pred - 1) < 3e-3 and abs(g[-n] / pred - 1) < 3e-3
        ok = ok and good; out.append('n = %d: %.5f, %.5f, mean %.6f of the prediction' % (n, g[n] / pred, g[-n] / pred, mean / pred))
    return ok, out
def pr013():
    """the twelve strongest Fourier amplitudes of the Fibonacci chain at length 1597"""
    import numpy as np, math
    PHI = (1 + 5 ** .5) / 2
    w = 'a'
    while len(w) < 1597: w = ''.join('ab' if c == 'a' else 'a' for c in w)
    L = len(w); seq = np.array([1.0 if c == 'a' else 0.0 for c in w]); amp = np.abs(np.fft.fft(seq) / L); fprev = 987
    peaks = sorted(range(1, L // 2), key=lambda q: -amp[q])[:12]; labs = []; ok = L == 1597; out = []
    for q in peaks:
        n = min((n for n in range(-60, 61) if n and ((n * fprev - q) % L == 0 or (n * fprev + q) % L == 0)), key=abs)
        pred = abs(math.sin(math.pi * n / PHI)) / (math.pi * abs(n)); labs.append(abs(n))
        ok = ok and abs(amp[q] - pred) < 1e-5; out.append('|n| = %d: amplitude %.6f, formula %.6f' % (abs(n), amp[q], pred))
    ok = ok and sorted(labs) == [1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 14, 17]
    return ok, out
def pr014():
    """the Chern numbers on the torus of the Bloch phase and the phason: 233 sites, 144/233, V = 2, beta = 3, the eight widest gaps, C = -q within 10^-6"""
    import wave_atlas as wa
    res = wa.chern_torus(L=233, p=144, V=2.0, beta=3.0, top=8)
    ok = len(res) == 8 and all(abs(c + q) < 1e-6 for _, q, c in res)
    return ok, ['p = %d, q = %d: C = %.6f' % r for r in res]
def pr015():
    """the Wigner negativity of the nine cubic-phase states sum_k w^(c k^3)|k>/3, c = 0 to 8"""
    import quantum as qm, numpy as np, cmath, math
    neg = []
    for c in range(9):
        v = np.array([qm.w ** ((c * k ** 3) % 9) for k in range(9)]) / 3
        neg.append(float(np.abs(qm.wig(np.outer(v, v.conj()))).sum() - 1))
    units = [neg[c] for c in (1, 2, 4, 5, 7, 8)]
    ok = abs(neg[0]) < 1e-9 and all(abs(neg[c] - neg[9 - c]) < 1e-9 for c in range(1, 9)) and max(units) - min(units) < 1e-9
    return ok, ['c = %d: negativity %.6f' % (c, n) for c, n in enumerate(neg)]
def pr016():
    """the quantum cat map at N = 81: 81 distinct eigenvalues, each a root of unity of order dividing 108, literal period 108"""
    import quantum_foundations as qf, numpy as np, cmath, math
    U = qf.kernel(81); ev = np.linalg.eigvals(U)
    gap = min(abs(a - b) for i, a in enumerate(ev) for b in ev[i + 1:])
    roots = all(abs(e ** 108 - 1) < 1e-6 for e in ev)
    R = np.linalg.matrix_power(U, 108); lit = np.allclose(R, np.eye(81), atol=1e-6)
    smaller = [d for d in range(1, 108) if 108 % d == 0 and np.allclose(np.linalg.matrix_power(U, d), np.eye(81), atol=1e-6)]
    ok = gap > 1e-6 and roots and lit and not smaller
    return ok, ['smallest eigenvalue gap %.3g' % gap, 'every eigenvalue a 108th root of unity: %s' % roots, 'U^108 = I: %s; a smaller literal period: %s' % (lit, smaller or 'none')]
TESTS = {'PR-001': pr001, 'PR-002': pr002, 'PR-003': pr003, 'PR-004': pr004, 'PR-005': pr005, 'PR-006': pr006, 'PR-007': pr007, 'PR-008': pr008, 'PR-009': pr009, 'PR-010': pr010, 'PR-011': pr011, 'PR-012': pr012, 'PR-013': pr013, 'PR-014': pr014, 'PR-015': pr015, 'PR-016': pr016}

def maturity(d):
    from collections import Counter
    S = d['scores']; n = len(S)
    pc = Counter(p for e in S for p in e.get('proof', []))
    print('======= MATURITY OF THE MATHEMATICAL REGISTER (Companion Parts 220.11 and 227.9) =======')
    print('results scored: %d | rungs: %s' % (n, ', '.join('%d at %d' % (c, r) for r, c in sorted(Counter(e['rung'] for e in S).items()))))
    for f, vals in (('proof completeness', PROOF), ('novelty', NOVELTY), ('connection depth', DEPTHS)):
        C = pc if f == 'proof completeness' else Counter(e.get('depth' if f == 'connection depth' else 'novelty') for e in S)
        print('%s: %s' % (f, '; '.join('%s %d' % (v, C.get(v, 0)) for v in vals)))
    pr = d.get('predictions', [])
    print('predictions: %d sealed; %s' % (len(pr), ', '.join('%s %s' % (p['id'], p['result']) for p in pr)))
    print('predicted before computed: %d of %d scored results' % (sum(1 for e in S if e['predicted_before_computed']['flag']), n))
    print('non-equivalences recorded: %d' % len(d.get('non_equivalences', [])))
    rr = d.get('replication_returns', [])
    print('replication returns: %d; results reproduced independently: %d' % (len(rr), len({m for r in rr for m, o in r.get('outcomes', {}).items() if o == RETURN[0]})))
    stages = [('1 computation', True), ('2 exact register', True), ('3 symbolic proof', pc.get(PROOF[0], 0) > 0), ('4 prediction', any(p['result'] == 'PASS' for p in pr)),
              ('5 independent replication', pc.get(PROOF[3], 0) > 0), ('6 external review', pc.get(PROOF[4], 0) > 0), ('7 machine-checked proof', False)]
    print('stages: ' + '; '.join('%s %s' % (s_, 'REACHED' if ok else 'NEXT') for s_, ok in stages))
    print('======= END MATURITY =======')

def selftest():
    good = {'scores': [{'mf': 'MF-1', 'rung': 1, 'disciplines': 2, 'depth': DEPTHS[3], 'novelty': NOVELTY[0], 'proof': [PROOF[0]], 'mechanism': MECHANISM[0],
                        'dims': {k: {'score': 1, 'status': 'CONSTRUCTED', 'reason': 'r'} for k in DIMS},
                        'predicted_before_computed': {'flag': True, 'predicted_in': 'seq_0001', 'checked_in': 'seq_0002'}}],
            'predictions': [{'id': 'PR-001', 'sealed_in': 'seq_0170', 'result': 'UNCHECKED'}]}
    def var(f):
        d = json.loads(json.dumps(good)); f(d); return problems(d, {'MF-1'})
    cs = [('a well-formed entry passes', problems(good, {'MF-1'}) == []),
          ('a score of 4 is refused', var(lambda d: d['scores'][0]['dims']['rigor'].update(score=4)) != []),
          ('a rung of 7 is refused', var(lambda d: d['scores'][0].update(rung=7)) != []),
          ('a flag with the prediction sealed after its check is refused',
           var(lambda d: d['scores'][0]['predicted_before_computed'].update(predicted_in='seq_0003')) != []),
          ('a prediction score with no flagged prediction is refused',
           var(lambda d: d['scores'][0]['predicted_before_computed'].update(flag=False, predicted_in=None)) != []),
          ('a result unknown to the mathematical register is refused', problems(good, {'MF-2'}) != []),
          ('a prediction checked in its own sealing record is refused',
           var(lambda d: d['predictions'][0].update(result='PASS', checked_in='seq_0170')) != []),
          ('the generation test is right at p = 5 and 7 (MF-71)', gen_full(5)[0] == gen_full(5)[1] and gen_full(7) == (672, 672)),
          ('the code test is right at p = 7: the extended Hamming code [8,4,4], kept (MF-77)', keeps_qr(7)[0] and len(keeps_qr(7)[1]) == 16 and min(sum(w) for w in keeps_qr(7)[1] if any(w)) == 4),
          ('the group generator is right on SL2(F5) from the two elementary shears (order 120)', len(gen_group([(1, 1, 0, 1), (1, 0, 1, 1)], 5)) == 120),
          ('a non-equivalence that cites no result is refused', var(lambda d: d.update(non_equivalences=[{'id': 'NE-001', 'statement': 's', 'refs': []}])) != []),
          ('a return with an unknown outcome is refused', var(lambda d: d.update(replication_returns=[{'id': 'RET-001', 'implementer': 'x', 'date': 'd', 'outcomes': {'MF-1': 'DONE'}}])) != []),
          ('a reproduced result without independent implementation in its proof is refused', var(lambda d: d.update(replication_returns=[{'id': 'RET-001', 'implementer': 'x', 'date': 'd', 'outcomes': {'MF-1': 'REPRODUCED'}}])) != []),
          ('a prediction from PR-012 without its failure condition is refused', var(lambda d: d.update(predictions=[{'id': 'PR-012', 'sealed_in': 'seq_0170', 'result': 'UNCHECKED', 'model': 'm', 'parameters': 'p', 'expected': 'e', 'uncertainty': 'u'}])) != []),
          ('the register in the repository is well formed', problems(load()) == [])]
    for n, ok in cs: print('%-100s %s' % (n, 'PASS' if ok else 'FAIL'))
    ok = all(o for _, o in cs); print('DSI SELFTEST: %d of %d | %s' % (sum(o for _, o in cs), len(cs), 'PASS' if ok else 'FAIL')); return ok

def listing(d):
    print('======= DISCOVERY SIGNIFICANCE INDEX (Companion Part 215.6) =======')
    print('%-6s %-4s %s' % ('RESULT', 'RUNG', '  '.join('%-11s' % k[:11] for k in DIMS)))
    for e in d['scores']:
        print('%-6s %-4d %s' % (e['mf'], e['rung'], '  '.join('%-11s' % ('%d %s' % (e['dims'][k]['score'], e['dims'][k]['status'][:5])) for k in DIMS)))
    n = len(d['scores']); f = sum(1 for e in d['scores'] if e['predicted_before_computed']['flag'])
    print('PREDICTED BEFORE COMPUTED: %d of %d scored results' % (f, n))
    for p in d.get('predictions', []): print('%s sealed in %s, %s: %s' % (p['id'], p['sealed_in'], p['result'], p['statement']))
    for n in d.get('non_equivalences', []): print('%s %s (%s)' % (n['id'], n['statement'], ', '.join(n['refs'])))
    print('UNCALIBRATED: ordinal scores, one result at a time; not comparable with historical discoveries until PV-025 is closed.')
    print('======= END DSI =======')

if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--check']:
        d = load(); P = problems(d)
        print('DSI: %d scored | %d predictions sealed | %s' % (len(d['scores']), len(d.get('predictions', [])), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--list']: listing(load()); sys.exit(0)
    if a == ['--maturity']: maturity(load()); sys.exit(0)
    if len(a) == 2 and a[0] == '--test' and a[1] in TESTS:
        ok, L = TESTS[a[1]](); [print(x) for x in L]; print('%s: %s' % (a[1], 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
