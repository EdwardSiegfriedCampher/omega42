#!/usr/bin/env python3
"""spectral.py -- M298 Spectral Profile (Core Part 3.32, 1.8.9): the frozen spectral definitions, computed two ways.

FROZEN DEFINITIONS (Core 1.8.9, "Spectral definitions"):
  Ground: modulus m, law T(a, b) = (b, a + b) mod m on the m^2 states.
  D. Dynamical spectrum: the operator K f = f o T on functions of the states. A cycle of length L contributes the
     eigenvalues exp(2 pi i r / L), r = 0 .. L - 1. Frequencies are indexed in turns per step, j / P with P the
     period of the law (lcm of the cycle lengths); multiplicities follow from the cycle decomposition alone, so the
     dynamical spectrum is a second description of the orbit census, not independent information.
  O. Observable spectrum: along one orbit of length L, the observable is the centred residue of the first entry,
     c(v) in (-m/2, m/2] (for odd m the representative of least absolute value; for even m the residue m/2 is
     written +m/2). X(k) = sum_n c(n) exp(-2 pi i k n / L); power |X(k)|^2; autocorrelation
     R(l) = sum_n c(n) c(n + l) (integers). Route 1: the DFT. Route 2: Wiener-Khinchin, |X(k)|^2 = sum_l R(l) cos(2 pi k l / L).
     The two routes must agree; integrality of the power is decided on route 2's exact integer autocorrelation by
     comparing the routes to 1e-9.
  The two spectra are kept apart: D belongs to the ground, O to one observable on one orbit.

Usage:
    python3 tools/spectral.py --ground M          # D and O for every orbit of modulus M
    python3 tools/spectral.py --rivals            # the comparison over the rival grounds (records/spectral_rivals/)
    python3 tools/spectral.py --selftest
"""
import cmath, math, sys
from collections import Counter
from functools import reduce

def orbits(m):
    seen, out = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o, x = [], (a, b)
            while x not in seen:
                seen.add(x); o.append(x); x = (x[1], (x[0] + x[1]) % m)
            out.append(o)
    return out

def centred(v, m):
    v %= m
    return v - m if v > m // 2 or (m % 2 == 1 and v > m // 2) else v

def dynamical(m):
    obs = orbits(m); P = reduce(lambda x, y: x * y // math.gcd(x, y), (len(o) for o in obs))
    mult = Counter()
    for o in obs:
        L = len(o)
        for r in range(L): mult[(P // L) * r % P] += 1
    return P, sorted(Counter(len(o) for o in obs).items()), mult

def observable(o, m):
    c = [centred(a, m) for a, b in o]; L = len(c)
    R = [sum(c[n] * c[(n + l) % L] for n in range(L)) for l in range(L)]
    p1 = [abs(sum(c[n] * cmath.exp(-2j * math.pi * k * n / L) for n in range(L))) ** 2 for k in range(L)]
    p2 = [sum(R[l] * math.cos(2 * math.pi * k * l / L) for l in range(L)) for k in range(L)]
    agree = all(abs(x - y) < 1e-6 for x, y in zip(p1, p2))
    integral = all(abs(x - round(x)) < 1e-6 for x in p2)
    halfneg = L % 2 == 0 and all(c[(n + L // 2) % L] == -c[n] for n in range(L))
    levels = sorted({abs(round(x, 4)) for x in p2[1:]})
    zero_lags = [l for l in range(1, L) if R[l] == 0]
    covers = len({a for a, b in o}) == m
    return dict(L=L, energy=R[0], levels=levels, integral=integral, halfneg=halfneg, routes_agree=agree,
                zero_lags=zero_lags, covers=covers, R=R)

def profile_key(d):
    return (d['L'], d['energy'], tuple(d['levels']))

def ground_report(m):
    P, census, mult = dynamical(m)
    lines = ['GROUND mod %d | period %d | cycle census %s' % (m, P, census),
             '  D: multiplicities by frequency j/%d: %s' % (P, dict(sorted(mult.items())))]
    for o in sorted(orbits(m), key=len, reverse=True):
        if len(o) < 2: continue
        d = observable(o, m)
        lines.append('  O: orbit from %s, L %d, covers all residues %s, energy %d, half-period negation %s, integral %s, routes agree %s, levels %s'
                     % (o[0], d['L'], d['covers'], d['energy'], d['halfneg'], d['integral'], d['routes_agree'], d['levels'][:6]))
    return '\n'.join(lines)

CANON = (2, 5)
def canonical_orbit():
    return next(o for o in orbits(9) if CANON in o)

def rivals():
    grounds = [6, 9, 10, 12, 16, 18, 24, 36, 48, 72, 144]
    L = ['M298 RIVAL-GROUND COMPARISON (frozen definitions D and O; Core 1.8.9)']
    canon = observable(canonical_orbit(), 9); ck = profile_key(canon)
    L.append('Omega42 canonical observable profile: L %d, energy %d, odd harmonics only %s, integral %s, levels %s'
             % (canon['L'], canon['energy'], canon['halfneg'], canon['integral'], canon['levels']))
    shared_D, shared_O, rows = [], [], []
    _, _, m9 = dynamical(9)
    for m in grounds:
        P, census, mult = dynamical(m)
        rows.append('  mod %3d: period %3d, census %s' % (m, P, census))
        if P == 24 and mult == m9 and m != 9: shared_D.append(m)
        for o in orbits(m):
            if len(o) < 2 or (m == 9 and CANON in o): continue
            d = observable(o, m)
            if profile_key(d) == ck: shared_O.append((m, o[0]))
    L += rows
    L.append('D shared with modulus 9 (same period and multiplicities): %s' % (shared_D or 'NONE'))
    L.append('O shared with the canonical orbit (same length, energy and power levels), among %d grounds: %s' % (len(grounds), shared_O or 'NONE'))
    feats = Counter()
    for m in grounds:
        for o in orbits(m):
            if len(o) < 2 or (m == 9 and CANON in o): continue
            d = observable(o, m)
            feats['period 24 + half-period negation'] += d['L'] == 24 and d['halfneg']
            feats['... + covers all residues'] += d['L'] == 24 and d['halfneg'] and d['covers']
            feats['... + integral two-level spectrum'] += d['L'] == 24 and d['halfneg'] and d['covers'] and d['integral'] and len([x for x in d['levels'] if x > 1e-6]) == 2
    L.append('Rival orbits sharing each conjunct of the canonical profile: %s' % dict(feats))
    L.append('  (the two that share period 24, half-period negation and full coverage are Voices A and B of mod 9; for even moduli the residue m/2 is its own negative, so the centred observable cannot show the half-period negation exactly when m/2 occurs)')
    # reconstruction: shortest window of consecutive centred values that singles out the ground and orbit
    seqs = []
    for m in grounds:
        for o in orbits(m):
            c = [centred(a, m) for a, b in o]
            for s in range(len(c)): seqs.append((m, o[s], c[s:] + c[:s]))
    canon_c = [centred(a, 9) for a, b in canonical_orbit()]
    worst = 0
    for s in range(24):
        target = canon_c[s:] + canon_c[:s]
        for w in range(1, 25):
            hits = {(m, tuple(sorted(o))) for m, st, c in seqs if c[:w] == target[:w] and len(c) >= w}
            hits = {(m, st) for m, st, c in seqs if len(c) >= w and c[:w] == target[:w]}
            if len(hits) == 1: worst = max(worst, w); break
    L.append('Reconstruction: a window of %d consecutive centred values, from any start of the canonical cycle, singles out the ground (mod 9) and the state, and so the whole spectrum, among all orbits of the %d grounds' % (worst, len(grounds)))
    return '\n'.join(L)

def selftest():
    ok = []
    def check(name, cond): ok.append(bool(cond)); print('%-78s %s' % (name, 'ok' if cond else 'FAIL'))
    P, census, mult = dynamical(9)
    check('D(9): period 24, census 1 + 8 + 24 + 24 + 24, multiplicities 5 / 4 / 3', P == 24 and census == [(1, 1), (8, 1), (24, 3)] and all(mult[j] == (5 if j == 0 else 4 if j % 3 == 0 else 3) for j in range(24)))
    d = observable(canonical_orbit(), 9)
    check('O(canonical): routes agree, integral, half-period negation, levels 0 / 324 / 648', d['routes_agree'] and d['integral'] and d['halfneg'] and d['levels'] == [0.0, 324.0, 648.0])
    check('O(canonical): energy 216 and autocorrelation zero off the multiples of 4', d['energy'] == 216 and all(l % 4 for l in d['zero_lags']) and len(d['zero_lags']) == 18)
    check('centred residues: odd m least absolute value; even m writes m/2 as +m/2', centred(5, 9) == -4 and centred(4, 9) == 4 and centred(3, 6) == 3 and centred(4, 6) == -2)
    check('a constant sequence has power only at k = 0', observable([(1, 0)] * 1 + [(1, 0)], 9)['levels'] == [0.0])
    print('M298 SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--ground': print(ground_report(int(a[1]))); sys.exit(0)
    if a[0] == '--rivals': print(rivals()); sys.exit(0)
