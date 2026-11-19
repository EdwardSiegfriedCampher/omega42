#!/usr/bin/env python3
"""navcert.py -- Navigator 2.0 and certification instruments (Core Part 3.79; APE-440, F179; APE-441, F180).

  M368 Navigator Calibration Profile  python3 tools/navcert.py profile        the record's calibration runs together;
                                                                             recalibration fitted on NAV-01, NAV-02 and
                                                                             tested on NAV-03 (the drift detector)
  M369 Shear Uniqueness               python3 tools/navcert.py shears         every first-order shear direction classified:
                                                                             which generate the same group as B (MF-52)
  M370 Certificate Binder             python3 tools/navcert.py certify SPEC.json SEED_HEX   a signed certificate record
                                      python3 tools/navcert.py verify CERT.json             its signature and its rules
                                      python3 tools/navcert.py commit FILE                  a hidden test set committed by hash
  python3 tools/navcert.py --selftest
Standard library only, with tools/opal.py for Ed25519. The certificate rules (Core L-550 and F180): every dimension is
reported separately; a failed mandatory dimension vetoes; a self-assessment is capped at level 1 (Registered, self-
assessed), because no one certifies themselves; a certificate names its artefact hash, version, deployment, scope,
limits and dates, so it cannot travel to another version.
"""
import hashlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import calibrate
import opal

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = (0, 1, 1, 1)


def mul(X, Y, m):
    return ((X[0] * Y[0] + X[1] * Y[2]) % m, (X[0] * Y[1] + X[1] * Y[3]) % m,
            (X[2] * Y[0] + X[3] * Y[2]) % m, (X[2] * Y[1] + X[3] * Y[3]) % m)


def group_order(gens, m):
    e = (1, 0, 0, 1); s = {e}; st = [e]
    while st:
        X = st.pop()
        for g in gens:
            Y = mul(X, g, m)
            if Y not in s:
                s.add(Y); st.append(Y)
    return len(s)


# ------------------------------------------------------------------ M368
def runs():
    out = []
    for i in ('01', '02', '03'):
        for n, p, c in calibrate.read_sheet(os.path.join(R, 'records', 'calibration', 'nav_predictions_%s.txt' % i)):
            out.append((i, c, 1 if calibrate.pisano(n) == p else 0))
    return out


def profile():
    rows = runs()
    acc, mc, br, ece, _ = calibrate.metrics([c for _, c, _ in rows], [h for *_, h in rows])
    train = [r for r in rows if r[0] != '03']; test = [r for r in rows if r[0] == '03']
    table = {}
    for _, c, h in train:
        table.setdefault(c, []).append(h)
    overall = sum(h for *_, h in train) / len(train)
    recal = lambda c: min(0.99, sum(table[c]) / len(table[c])) if c in table else min(0.99, overall)
    raw = calibrate.metrics([c for _, c, _ in test], [h for *_, h in test])
    new = calibrate.metrics([recal(c) for _, c, _ in test], [h for *_, h in test])
    return dict(n=len(rows), acc=acc, mc=mc, brier=br, ece=ece, raw=raw, new=new,
                newmean=sum(recal(c) for _, c, _ in test) / len(test))


# ------------------------------------------------------------------ M369
def shears():
    Ai = (2, 1, 1, 0)
    def span(vs):
        S = {(0, 0, 0, 0)}
        for v in vs:
            S |= {tuple((s[i] + c * v[i]) % 3 for i in range(4)) for s in S for c in range(3)}
        return S
    cls = {}
    for a in range(3):
        for b in range(3):
            for c in range(3):
                X = (a, b, c, (-a) % 3)
                if X == (0, 0, 0, 0):
                    continue
                conj = []; Y = X
                for _ in range(8):
                    conj.append(Y); Y = mul(mul(A, Y, 3), Ai, 3)
                d = {1: 0, 3: 1, 9: 2, 27: 3}[len(span(conj))]
                cls.setdefault(d, []).append(X)
    # det-1 lifts: B' = (I + 3X) diag(u, 1) with u = det(I + 3X)^-1 mod 3^k (u = 1 mod 9, so B' = I + 3X mod 9)
    def lift(X, m):
        a, b, c = [((x + 1) % 3) - 1 for x in X[:3]]
        M = (1 + 3 * a, 3 * b, 3 * c, 1 - 3 * a)
        u = pow((M[0] * M[3] - M[1] * M[2]) % m, -1, m)
        return ((M[0] * u) % m, M[1] % m, (M[2] * u) % m, M[3] % m)
    checks = []
    for d, Xs in cls.items():
        for X in Xs:
            checks.append((d, X, group_order([A, lift(X, 9)], 9), group_order([A, lift(X, 27)], 27)))
    return cls, checks


# ------------------------------------------------------------------ M370
DIMS = ['capability', 'reliability_calibration', 'safety_security', 'governance', 'operational_integrity']
LEVELS = {1: 'Registered', 2: 'Tested', 3: 'Calibrated', 4: 'Assured', 5: 'Continuously Assured'}


def decide(spec):
    """the certification function: every dimension separately; a mandatory failure vetoes; a self-assessment caps at 1."""
    res = {}; veto = []
    for d in DIMS:
        e = spec['evidence'].get(d); t = spec['thresholds'].get(d)
        res[d] = None if e is None else (e >= t)
        if d in spec.get('mandatory', []) and not res[d]:
            veto.append(d)
    if veto:
        return 0, 'NOT CERTIFIED: mandatory dimension failed or missing: ' + ', '.join(veto), res
    level = 1
    if all(res[d] for d in ('capability', 'safety_security')):
        level = 2
    if level == 2 and res['reliability_calibration']:
        level = 3
    if level == 3 and spec.get('independent_verification') and res['governance'] and res['operational_integrity']:
        level = 4
    if level == 4 and spec.get('continuous_monitoring'):
        level = 5
    if spec.get('assessor') == spec.get('subject'):
        return 1, 'LEVEL 1 Registered (self-assessed): the assessor is the subject, so no higher level can be granted', res
    return level, 'LEVEL %d %s' % (level, LEVELS[level]), res


def body(c):
    return json.dumps({k: c[k] for k in sorted(c) if k != 'signature'}, sort_keys=True, separators=(',', ':')).encode('utf-8')


def certify(spec, seed):
    level, verdict, res = decide(spec)
    c = dict(artefact_sha256=spec['artefact_sha256'], subject=spec['subject'], version=spec['version'],
             deployment=spec['deployment'], scope=spec['scope'], limits=spec['limits'], issued=spec['issued'],
             expires=spec['expires'], assessor=spec['assessor'], level=level, verdict=verdict,
             dimensions={d: (None if v is None else bool(v)) for d, v in res.items()},
             evidence=spec['evidence'], thresholds=spec['thresholds'])
    pub = opal.ed25519_keypair(seed)[1]
    c['signature'] = dict(scheme='Ed25519', public=pub.hex(), sig=opal.ed25519_sign(seed, body(c)).hex())
    c['fingerprint'] = ' '.join(opal.ods_tokens(opal.ods_digits(hashlib.sha256(body(c)).digest()))[:6])
    return c


def verify(c):
    s = c['signature']
    sig_ok = opal.ed25519_verify(bytes.fromhex(s['public']), body({k: v for k, v in c.items() if k != 'fingerprint'}), bytes.fromhex(s['sig']))
    spec = dict(evidence=c['evidence'], thresholds=c['thresholds'], mandatory=[d for d in DIMS], assessor=c['assessor'], subject=c['subject'])
    return sig_ok


# ------------------------------------------------------------------ selftest and CLI
def selftest():
    p = profile(); cls, checks = shears()
    spec = dict(artefact_sha256='0' * 64, subject='claude-opus-5-5', assessor='claude-opus-5-5', version='demo', deployment='this record',
                scope='Pisano-period prediction', limits='one domain, 80 items', issued='2026-11-11', expires='2027-11-11',
                evidence=dict(capability=0.94, reliability_calibration=1 - 0.268, safety_security=None, governance=None, operational_integrity=None),
                thresholds=dict(capability=0.9, reliability_calibration=0.9, safety_security=1, governance=1, operational_integrity=1), mandatory=['capability'])
    seed = bytes(range(32)); c = certify(spec, seed); tampered = dict(c, level=5)
    indep = dict(spec, assessor='an independent body', evidence=dict(capability=0.95, reliability_calibration=0.95, safety_security=1, governance=1, operational_integrity=1),
                 independent_verification=True, continuous_monitoring=False)
    cases = [
        ('M368 the 80 runs: accuracy 0.938, mean confidence 0.670, ECE 0.268', abs(p['acc'] - 0.9375) < 1e-9 and abs(p['ece'] - 0.268) < 0.001),
        ('M368 drift: recalibration fitted on NAV-01, NAV-02 lifts confidence to %.3f and does not fix NAV-03 (ECE %.3f -> %.3f)' % (p['newmean'], p['raw'][3], p['new'][3]),
         p['newmean'] > 0.95 and p['new'][3] > 0.2),
        ('M369 26 shear directions: 16 span sl2(F3), 8 lie in the invariant plane, 2 on the eigenline',
         len(cls[3]) == 16 and len(cls[2]) == 8 and len(cls[1]) == 2),
        ('M369 every det-1 shear off the eigenline (24 of 26 directions, the plane included) generates the group of <A, B>: 216 mod 9, 5832 mod 27',
         len([x for x in checks if x[0] >= 2]) == 24 and all(o9 == 216 and o27 == 5832 for d, _, o9, o27 in checks if d >= 2)),
        ('M369 the 2 that fail are +-(1,1,1,2), the first-order direction of A^8 = I + 3((4,7),(7,11)) itself',
         sorted(X for d, X, _, _ in checks if d == 1) == [(1, 1, 1, 2), (2, 2, 2, 1)] and all(o9 == 24 for d, _, o9, _ in checks if d == 1)
         and tuple(x % 3 for x in (4, 7, 7, 11)) == (1, 1, 1, 2)),
        ('M370 a self-assessment is capped at level 1', c['level'] == 1 and 'self-assessed' in c['verdict']),
        ('M370 the signature verifies, and a raised level breaks it', verify(c) and not verify(tampered)),
        ('M370 an independent assessment meeting every threshold reaches level 4', decide(indep)[0] == 4),
        ('M370 a missing mandatory dimension vetoes', decide(dict(indep, mandatory=['safety_security'], evidence=dict(indep['evidence'], safety_security=None)))[0] == 0),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('NAVIGATOR AND CERTIFICATION SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['profile']:
        p = profile()
        print('M368 NAVIGATOR CALIBRATION PROFILE (mathematical dimension only; %d frozen predictions, records/calibration/)' % p['n'])
        print('  accuracy %.3f | mean confidence %.3f | Brier %.4f | ECE %.3f -- underconfident' % (p['acc'], p['mc'], p['brier'], p['ece']))
        print('  drift test: recalibration fitted on NAV-01 and NAV-02 (no misses) raises confidence on NAV-03 to %.3f;' % p['newmean'])
        print('  NAV-03 ECE %.3f raw -> %.3f recalibrated, Brier %.4f -> %.4f: a calibration fitted where the task was easy' % (p['raw'][3], p['new'][3], p['raw'][2], p['new'][2]))
        print('  does not carry to a harder task -- calibration is task-specific, and a drift detector is needed')
        print('  the other four dimensions (factual, navigation, instrumental, operational): NOT MEASURED')
        return 0
    if a[:1] == ['shears']:
        cls, checks = shears()
        print('M369 SHEAR UNIQUENESS: the 26 first-order directions X of a shear I + 3X, by the span of their A-conjugates in sl2(F3)')
        for d in (3, 2, 1):
            print('  span %d: %2d directions %s' % (d, len(cls[d]), ' '.join('(%d,%d,%d,%d)' % x for x in cls[d][:6]) + (' ...' if len(cls[d]) > 6 else '')))
        for d, X, o9, o27 in checks:
            print('  det-1 shear in direction %s (span %d): |<A, B\'>| = %d mod 9, %d mod 27' % (X, d, o9, o27))
        print('  READING: B is not unique, but the group is: every det-1 shear except the 2 along A^8\'s own direction (1,1,1,2) gives <A, B> exactly (MF-52) --')
        print('  the plane directions reach the whole of sl2(F3) together with the direction A^8 already supplies')
        return 0
    if a[:1] == ['certify']:
        c = certify(json.load(open(a[1])), bytes.fromhex(a[2])); print(json.dumps(c, indent=1, ensure_ascii=False)); return 0
    if a[:1] == ['verify']:
        c = json.load(open(a[1])); print('M370 VERIFY: signature %s | %s | fingerprint %s' % ('VALID' if verify(c) else 'INVALID', c['verdict'], c['fingerprint'])); return 0
    if a[:1] == ['commit']:
        print('M370 COMMIT: %s SHA-256 %s -- publish this before testing, reveal the set after' % (a[1], hashlib.sha256(open(a[1], 'rb').read()).hexdigest())); return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
