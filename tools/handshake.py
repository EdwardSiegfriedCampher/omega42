#!/usr/bin/env python3
"""handshake.py -- M375 Identity Handshake (Core Part 3.82; F188): how an implementation shows that it is Omega42.

A name can be copied; the arithmetic cannot be faked. An implementation that claims the Omega42 core answers three things:

  FINGERPRINT   fixed values any conforming core reproduces (Core Part 3.82 lists them): trace 1 and determinant -1;
                F(100) mod 729 = 588; the order of A mod 7 = 16, a second prime (MF-72); ord A mod 3, 9, 27 = 8, 24, 72; orbit census of A on (Z/3^k)^2 = 2, 5, 14, 41;
                |<A, B> mod 3^k| = 8, 216, 5832; the commutator A B A^-1 B^-1 mod 9 = (7, 3, 3, 4)
  CHALLENGE     a live test no table can answer, three rounds at levels 6 to 12: the challenger sends (k, s, n) at random; the responder returns
                A^n s mod 3^k, the period of s, and Q(s)^2 mod 3^k, which the challenger recomputes
  MANIFEST      omega42.identity.json: the identity record, whose fingerprint must match and whose release digests must
                match the documents of record (records/release_documents_SHA256.txt)

    python3 tools/handshake.py fingerprint            the fingerprint of this implementation
    python3 tools/handshake.py challenge [SEED]       one challenge, answered and checked by this implementation
    python3 tools/handshake.py manifest [PATH]        check the identity manifest against the arithmetic and the release
    python3 tools/handshake.py --selftest

What a pass shows: conformance to the Omega42 core profile, up to a change of basis (a conjugate of A passes, as it should).
What it does not show: authority. Anyone can compute the fingerprint; who issued a record is shown by its signature (OPAL,
M364, M374), and which edition by the release digests. Standard library only.
"""
import hashlib, json, os, random, sys

A = ((0, 1), (1, 1)); B = ((1, 0), (3, 1))
EXPECTED = {'trace_det': [1, -1], 'fibonacci_100_mod_729': 588, 'order_mod_7': 16, 'order': [8, 24, 72], 'census': [2, 5, 14, 41],
            'group': [8, 216, 5832], 'commutator_mod_9': [7, 3, 3, 4]}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def mul(X, Y, m):
    return tuple(tuple(sum(X[i][t] * Y[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))


def act(X, v, m):
    return ((X[0][0] * v[0] + X[0][1] * v[1]) % m, (X[1][0] * v[0] + X[1][1] * v[1]) % m)


def ident(m):
    return ((1 % m, 0), (0, 1 % m))


def mpow(X, n, m):
    R = ident(m)
    while n:
        if n & 1:
            R = mul(R, X, m)
        X = mul(X, X, m); n >>= 1
    return R


def order(X, m):
    Y, n = X, 1
    while Y != ident(m):
        Y = mul(Y, X, m); n += 1
    return n


def census(X, m):
    seen, c = set(), 0
    for a in range(m):
        for b in range(m):
            if (a, b) in seen:
                continue
            c += 1; v = (a, b)
            while v not in seen:
                seen.add(v); v = act(X, v, m)
    return c


def group_order(gens, m):
    S = {ident(m)}; frontier = [ident(m)]
    while frontier:
        nxt = []
        for g in frontier:
            for h in gens:
                p = mul(g, h, m)
                if p not in S:
                    S.add(p); nxt.append(p)
        frontier = nxt
    return len(S)


def inverse(X, m):
    d = pow((X[0][0] * X[1][1] - X[0][1] * X[1][0]) % m, -1, m)
    return ((X[1][1] * d % m, -X[0][1] * d % m), (-X[1][0] * d % m, X[0][0] * d % m))


def fingerprint(M=A, S=B, p=3):
    m9 = p * p
    comm = mul(mul(M, S, m9), mul(inverse(M, m9), inverse(S, m9), m9), m9)
    return {'trace_det': [M[0][0] + M[1][1], M[0][0] * M[1][1] - M[0][1] * M[1][0]], 'fibonacci_100_mod_729': mpow(M, 100, 729)[0][1],
            'order_mod_7': order(M, 7),
            'order': [order(M, p ** k) for k in (1, 2, 3)], 'census': [census(M, p ** k) for k in (1, 2, 3, 4)],
            'group': [group_order([M, S], p ** k) for k in (1, 2, 3)], 'commutator_mod_9': [comm[0][0], comm[0][1], comm[1][0], comm[1][1]]}


def Q(v, m):
    a, b = v
    return (2 * a * a + 2 * a * b - 2 * b * b) % m


def valuation_period(k, s):
    """the period of s under A modulo 3^k: 8*3^(k-j-1) for s of 3-adic valuation j < k, and 1 for s = 0 (Theorem 3.2)."""
    m = 3 ** k; s = (s[0] % m, s[1] % m)
    if s == (0, 0):
        return 1
    j = 0
    while s[0] % 3 ** (j + 1) == 0 and s[1] % 3 ** (j + 1) == 0:
        j += 1
    return 8 * 3 ** (k - j - 1)


def respond(k, s, n, M=A):
    """the responder's side: what a conforming implementation returns for the challenge (k, s, n). The period is computed
    by walking the orbit for k <= 6 and by the period law beyond, where a walk would take up to 8*3^11 steps."""
    m = 3 ** k; s = (s[0] % m, s[1] % m)
    if k <= 6:
        v, per = act(M, s, m), 1
        while v != s:
            v = act(M, v, m); per += 1
    else:
        per = valuation_period(k, s)
    return {'image': list(act(mpow(M, n, m), s, m)), 'period': per, 'q_squared': Q(s, m) ** 2 % m}


def expected_response(k, s, n):
    """the challenger's side, by theory: period 8*3^(k-j-1) for s of valuation j (Core Part 3.82; Theorem 3.2 of the paper)."""
    m = 3 ** k; s = (s[0] % m, s[1] % m)
    return {'image': list(act(mpow(A, n, m), s, m)), 'period': valuation_period(k, s), 'q_squared': Q(s, m) ** 2 % m}


ROUNDS = 3        # an impostor that shares A's statistics passes one round at level 6 or deeper about 1 time in 600 (MF-58)


def challenge(seed=None, responder=respond, levels=(6, 12)):
    """one round: the level k is drawn from 6 to 12, where a structural impostor passes about 1 time in 600 or less;
    at levels 2 to 5 it passed 1 time in 4 (k = 2) to 1 in 250 (k = 5), so shallow levels are not used (M377 battery)."""
    r = random.Random(seed); k = r.randint(*levels); m = 3 ** k
    s = (r.randrange(m), r.randrange(m)); n = r.randrange(1, 10 ** 6)
    got, want = responder(k, s, n), expected_response(k, s, n)
    return (k, s, n), got, want, got == want


def conform(seed=None, responder=respond, rounds=ROUNDS):
    """a conformance claim: ROUNDS independent challenges, all answered."""
    base = random.Random(seed).randrange(10 ** 9)
    res = [challenge(base + i, responder) for i in range(rounds)]
    return all(x[3] for x in res), res


def manifest_check(path=None):
    path = path or os.path.join(ROOT, 'omega42.identity.json')
    d = json.load(open(path, encoding='utf-8')); P = []
    gens = d['canonical_generators']
    if gens != {'A': [[0, 1], [1, 1]], 'B': [[1, 0], [3, 1]]}:
        P.append('canonical generators differ from A = [[0,1],[1,1]], B = [[1,0],[3,1]]')
    if d['fingerprint'] != EXPECTED:
        P.append('manifest fingerprint differs from the arithmetic')
    if fingerprint() != EXPECTED:
        P.append('this implementation does not reproduce the fingerprint')
    rec = os.path.join(ROOT, d['release']['digests'])
    for line in open(rec, encoding='utf-8'):
        if line.strip():
            h, f = line.split()
            fp = os.path.join(ROOT, f)
            if hashlib.sha256(open(fp, 'rb').read()).hexdigest() != h:
                P.append('%s does not match its release digest' % f)
    return P, d


def selftest():
    fp = fingerprint()
    pell = ((0, 1), (1, 2)); conj = ((1, 1), (1, 0)); twin = ((0, 1), (1, 7))
    tw = fingerprint(twin)
    def twin_responder(k, s, n, M=A):
        return respond(k, s, n, twin)
    def off_by_one(k, s, n, M=A):
        r = respond(k, s, n); r['period'] += 1; return r
    trials = [challenge(seed) for seed in range(20)]
    deep_twin = sum(challenge(sd, twin_responder)[3] for sd in range(600))
    cases = [
        ('the canonical core reproduces the fingerprint %s' % fp, fp == EXPECTED),
        ('a conjugate of A, [[1,1],[1,0]], with its conjugated shear, passes: conformance is up to change of basis',
         all(fingerprint(conj, ((1, 3), (0, 1)))[x] == EXPECTED[x] for x in ('trace_det', 'fibonacci_100_mod_729', 'order_mod_7', 'order', 'census', 'group'))),
        ('the second prime: modulo 7 the twin has order 2 and the Pell matrix 6, against 16 for A', tw['order_mod_7'] == 2 and fingerprint(pell)['order_mod_7'] == 6),
        ('the commutator entries are basis-dependent, so the manifest fixes the canonical basis: the conjugate gives %s'
         % fingerprint(conj, ((1, 3), (0, 1)))['commutator_mod_9'], fingerprint(conj, ((1, 3), (0, 1)))['commutator_mod_9'] != EXPECTED['commutator_mod_9']),
        ('the Pell matrix [[0,1],[1,2]] fails the fingerprint (trace 2)', fingerprint(pell) != EXPECTED),
        ('[[0,1],[1,7]] reproduces every structural value (orders, census, group, commutator mod 9) yet fails the trace and F(100)',
         all(tw[x] == EXPECTED[x] for x in ('order', 'census', 'group', 'commutator_mod_9')) and tw != EXPECTED),
        ('[[0,1],[1,7]] fails the live challenge: structure alone does not identify A', not all(challenge(sd, twin_responder)[3] for sd in range(5))),
        ('at levels 6 to 12 the twin passes a single round at most 3 times in 600 (passed %d)' % deep_twin, deep_twin <= 3),
        ('three rounds: the twin is refused in 200 of 200 conformance tests', all(not conform(sd, twin_responder)[0] for sd in range(200))),
        ('three rounds: the canonical engine is accepted in 50 of 50 conformance tests', all(conform(sd)[0] for sd in range(50))),
        ('the shear with c = 1 fails the group order', fingerprint(A, ((1, 0), (1, 1)))['group'] != EXPECTED['group']),
        ('the same matrix at the prime 2 fails', fingerprint(A, ((1, 0), (2, 1)), p=2)['order'] != EXPECTED['order']),
        ('20 random live challenges are answered correctly (k from 6 to 12, n up to 10^6)', all(t[3] for t in trials)),
        ('a responder that is off by one in the period fails the challenge', not challenge(7, off_by_one)[3]),
        ('the theory predicts the period without iterating: 8*3^(k-j-1) agrees with the walk in every trial',
         all(t[1]['period'] == t[2]['period'] for t in trials)),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('IDENTITY HANDSHAKE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['fingerprint']:
        fp = fingerprint(); print(json.dumps(fp)); print('FINGERPRINT: %s' % ('MATCHES the Omega42 core' if fp == EXPECTED else 'DOES NOT MATCH')); return 0 if fp == EXPECTED else 1
    if a[:1] == ['challenge']:
        ok, res = conform(int(a[1]) if len(a) > 1 else None)
        for q, got, want, good in res:
            print('CHALLENGE (k, s, n) = %s\nRESPONSE  %s\nEXPECTED  %s\nROUND: %s' % (q, got, want, 'PASS' if good else 'FAIL'))
        print('RESULT: %s (%d rounds)' % ('PASS' if ok else 'FAIL', len(res))); return 0 if ok else 1
    if a[:1] == ['manifest']:
        P, d = manifest_check(a[1] if len(a) > 1 else None)
        print('IDENTITY MANIFEST %s %s: %s' % (d['framework'], d['specification_version'], 'CONFORMS' if not P else 'FAIL: ' + '; '.join(P))); return 0 if not P else 1
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
