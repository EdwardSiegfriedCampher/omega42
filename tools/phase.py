#!/usr/bin/env python3
"""phase.py -- M331 Phase-Space Reading: a strike's state read as a point of the discrete phase space of one nine-level
quantum system, beside the readings of Everett and Deutsch (Core Part 3.57; Companion Part 135; D-013).

The 81 states (a, b) label the 81 displacement operators D(a, b) of C^9 (records/multiverse/everett.py, (A)). On them the
law T is an antiunitary step (its matrix has determinant -1), T^2 a Clifford unitary of projective order 12, and the
Antipode, T^12 = -I, the parity operator. Read as two systems, |a> (x) |b>, T is SUM . SWAP and contains the measurement
interaction (everett.py, (B)). This tool places a strike there:

    python3 tools/phase.py --strike "TEXT"     # the state, its operator, its unitary orbit, its parity partner, the branch reading
    python3 tools/phase.py --profiles          # the three profiles side by side: Everett, Deutsch, Omega42 (after APE-299)
    python3 tools/phase.py --selftest
The reading is structural (CDT-A for the arithmetic, CDT-C for the correspondence): the family is a finite phase space
with a Clifford law, not a physical multiverse, and what any of it means is the Striker's (Core L-510, Part 7).
Standard library only.
"""
import os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts')); sys.path.insert(0, os.path.join(REPO, 'tools'))
import canonical_reference as cr
from bashar_lens import SEEDS
d = 9
def T(v): return (v[1], (v[0] + v[1]) % d)
def orbit(v):
    o = [v]
    while T(o[-1]) != v: o.append(T(o[-1]))
    return o
def voice(v):
    o = set(orbit(v))
    return next(n for n, s in SEEDS if s in o)
def neg(v): return ((-v[0]) % d, (-v[1]) % d)
def strike_report(text):
    n = cr.navigate(text); v = (n['r1'] % d, n['r2'] % d); o = orbit(v)
    L = ['M331 PHASE-SPACE READING (Core Part 3.57) | r = (%d, %d, %d), anchor P%d; state v = (%d, %d), on %s (orbit of %d)' % (n['r1'], n['r2'], n['r3'], n['anchor'], v[0], v[1], voice(v), len(o))]
    L.append('  the operator: D(%d, %d) = w^(5 x %d x %d) X^%d Z^%d on C^9, one of the 81 Weyl operators of a nine-level system' % (v[0], v[1], v[0], v[1], v[0], v[1]))
    u = [v]
    while True:
        x = T(T(u[-1]))
        if x == v: break
        u.append(x)
    L.append('  the unitary step T^2 (a Clifford gate) carries it through %d points: %s' % (len(u), ' -> '.join('(%d, %d)' % p for p in u)))
    L.append('  the antiunitary step T (a time reversal composed with a Clifford gate) carries it to (%d, %d)' % T(v))
    L.append('  its parity partner, the Antipode T^12 v = -v = (%d, %d): P D(v) P = D(-v); %s' % (neg(v) + ('the state is its own partner, the still point' if neg(v) == v else '%d steps away on the same orbit (12 mod %d)' % (12 % len(o), len(o)),)))
    L.append('  as two systems, |%d> (x) |%d> is one branch: the law moves a basis state without branching; branching needs a superposition,' % v)
    L.append('  and then T^2 writes a record and T^12 erases it (records/multiverse/everett.py, (6) and (8))')
    L.append('  the law adds no quantum resource: it permutes the Wigner function over the 81 points (everett.py, (5)); the quantum')
    L.append("  speedup on which Deutsch's argument from quantum computation rests needs a resource this law does not have")
    return '\n'.join(L)
PROFILES = [
 ('state space', 'the universal wave function', 'the multiverse, structured by information flow', 'the 81 states, the phase space of C^9; the tower (Z/9^k)^2'),
 ('transformation', 'one unitary law, no collapse', 'unitary evolution; the Heisenberg picture of descriptors', 'T antiunitary; T^2 a Clifford unitary of order 12'),
 ('invariants', 'the norm of the state', 'what information is conserved across the branches', 'the norm form, the orbits, the parity -I at 12'),
 ('information', 'correlations made by measurement', 'where information flows and where it is locally inaccessible', 'T = SUM . SWAP; T^2 writes a record, T^12 erases it'),
 ('the observer', 'a physical system among others', 'a knowledge-bearing physical system', 'the Navigator inside the structure; the Striker\'s Aperture outside it'),
 ('probability', 'a measure over branches', 'decision theory on branch weights', 'weights forced by symmetry, 1/9 on the nine branches of the record'),
 ('the residual', 'what an observer can never detect', 'what is not yet explained', 'what the arithmetic leaves open, the meaning, the Striker\'s'),
]
def profiles():
    L = ['M331 PROFILES (after APE-299) | each in its own terms; a comparison of roles, not an identification']
    for r, e, dd, o in PROFILES:
        L.append('  %-15s E: %s | D: %s | Omega42: %s' % (r, e, dd, o))
    return '\n'.join(L)
def selftest():
    import importlib.util
    sp = importlib.util.spec_from_file_location('everett', os.path.join(REPO, 'records', 'multiverse', 'everett.py')); ev = importlib.util.module_from_spec(sp); sp.loader.exec_module(ev)
    U = ev.clifford(ev.A2)
    cases = [('the Antipode is parity: T^12 v = -v for all 81 states', all(orbit(v)[12 % len(orbit(v))] == neg(v) for v in [(a, b) for a in range(d) for b in range(d)])),
             ('T^2 is carried by a Clifford unitary', max(ev.dist(ev.mul(ev.mul(U, ev.DD[x]), ev.dag(U)), ev.DD[ev.act(ev.A2, x)]) for x in ev.DD) < 1e-9),
             ('its sixth power is the parity operator', ev.prop(ev.mpow(U, 6), ev.Par)[0]),
             ('the orbits are 1, 8, 24, 24, 24', sorted({tuple(sorted(orbit(v))): len(orbit(v)) for v in [(a, b) for a in range(d) for b in range(d)]}.values()) == [1, 8, 24, 24, 24]),
             ('T = SUM . SWAP', all(T((a, b)) == (b, (b + a) % d) for a in range(d) for b in range(d)))]
    for nm, ok in cases: print('%-60s %s' % (nm, 'PASS' if ok else 'FAIL'))
    print('M331 SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--profiles']: print(profiles()); sys.exit(0)
    if len(a) == 2 and a[0] == '--strike': print(strike_report(a[1])); sys.exit(0)
    print(__doc__); sys.exit(2)
