#!/usr/bin/env python3
"""omega42_sdk.py -- M363 the Ω42 SDK facade (Core Part 3.75; F174 11): one importable object over the verified engine.

    from omega42_sdk import Omega42          (with tools/ on the path)
    w = Omega42(k=2)
    w.A((1, 2)); w.B((1, 2)); w.Ainv(x); w.Binv(x)        the generators and their inverses
    w.invariant(x); w.valuation(x); w.depth_class(x, r)    Q^2, the valuation, the class at depth r (MF-43)
    w.orbit(x, 'A' | 'AB'); w.reachable(x, y, 'AB')        orbits and reachability (MF-42)
    w.run('ABA', x)                                        a history, kept with its states (M349)
    w.commutator()                                         A B A^-1 B^-1 mod 3^k
    w.group_order('AB')                                    8 * 3^(3(k-1)) by the theorem; checked by enumeration for k <= 3

Module map of F174 onto the record: core, groups, orbits, invariants, history, resolution -- this file, tools/omega_kit.py
and tools/fsg.py; calibration -- tools/calibrate.py and tools/suite.py cal; experiments -- tools/suite.py protocol,
verify, design. Everything here is MODE A (Core L-559).
    python3 tools/omega42_sdk.py --selftest      validates the facade against the finite-level theorems
Standard library only.
"""
import sys


class Omega42:
    def __init__(self, k=2):
        if k < 1:
            raise ValueError('k must be positive')
        self.k = k; self.m = 3 ** k

    def norm(self, x):
        return (x[0] % self.m, x[1] % self.m)

    def A(self, x):
        a, b = self.norm(x); return (b, (a + b) % self.m)

    def Ainv(self, x):
        a, b = self.norm(x); return ((b - a) % self.m, a)

    def B(self, x):
        a, b = self.norm(x); return (a, (3 * a + b) % self.m)

    def Binv(self, x):
        a, b = self.norm(x); return (a, (b - 3 * a) % self.m)

    def invariant(self, x):
        a, b = self.norm(x); q = 2 * a * a + 2 * a * b - 2 * b * b
        return q * q % self.m

    def valuation(self, x):
        a, b = self.norm(x)
        if a == 0 and b == 0:
            return self.k
        j = 0
        while a % 3 == 0 and b % 3 == 0:
            a //= 3; b //= 3; j += 1
        return j

    def depth_class(self, x, r):
        j = self.valuation(x)
        if j == self.k:
            return ('zero',)
        a, b = self.norm(x); u = (a // 3 ** j, b // 3 ** j); e = min(r, self.k - j)
        q = 2 * u[0] * u[0] + 2 * u[0] * u[1] - 2 * u[1] * u[1]
        return (j, q * q % 3 ** e)

    def _gens(self, group):
        return [self.A, self.Ainv] + ([self.B, self.Binv] if group.upper() == 'AB' else [])

    def orbit(self, x, group='A'):
        x = self.norm(x); seen = {x}; st = [x]; gens = self._gens(group)
        while st:
            y = st.pop()
            for g in gens:
                z = g(y)
                if z not in seen:
                    seen.add(z); st.append(z)
        return seen

    def reachable(self, x, y, group='AB'):
        return self.norm(y) in self.orbit(x, group)

    def run(self, word, x):
        hist = [('start', self.norm(x))]
        for ch in word.upper():
            x = {'A': self.A, 'B': self.B}[ch](x); hist.append((ch, x))
        return hist

    def _mul(self, X, Y):
        m = self.m
        return ((X[0] * Y[0] + X[1] * Y[2]) % m, (X[0] * Y[1] + X[1] * Y[3]) % m,
                (X[2] * Y[0] + X[3] * Y[2]) % m, (X[2] * Y[1] + X[3] * Y[3]) % m)

    def commutator(self):
        m = self.m
        return self._mul(self._mul(self._mul((0, 1, 1, 1), (1, 0, 3, 1)), ((-1) % m, 1, 1, 0)), (1, 0, (-3) % m, 1))

    def group_order(self, group='AB'):
        return 8 * 27 ** (self.k - 1) if group.upper() == 'AB' else 8 * 3 ** (self.k - 1)

    def enumerate_group(self, group='AB'):
        e = (1, 0, 0, 1 % self.m); gens = [(0, 1, 1, 1)] + ([(1, 0, 3, 1)] if group.upper() == 'AB' else [])
        seen = {e}; st = [e]
        while st:
            X = st.pop()
            for g in gens:
                Y = self._mul(X, g)
                if Y not in seen:
                    seen.add(Y); st.append(Y)
        return len(seen)


def selftest():
    ok = True; cases = []
    for k in (1, 2, 3):
        w = Omega42(k)
        states = [(a, b) for a in range(w.m) for b in range(w.m)]
        orbs = set(frozenset(w.orbit(x, 'A')) for x in states)
        cases.append(('k=%d: <A> orbits number (3^k+1)/2' % k, len(orbs) == (w.m + 1) // 2))
        orbsAB = set(frozenset(w.orbit(x, 'AB')) for x in states)
        cases.append(('k=%d: <A,B> orbits number k+1 (the valuation strata)' % k, len(orbsAB) == k + 1))
        cases.append(('k=%d: |<A,B>| = 8*3^(3(k-1)) by enumeration' % k, w.enumerate_group('AB') == w.group_order('AB')))
        cases.append(('k=%d: Q^2 kept by A, valuation kept by A and B' % k,
                      all(w.invariant(w.A(x)) == w.invariant(x) and w.valuation(w.A(x)) == w.valuation(x) == w.valuation(w.B(x)) for x in states)))
        cases.append(('k=%d: inverses' % k, all(w.Ainv(w.A(x)) == x == w.Binv(w.B(x)) for x in states)))
    w = Omega42(2)
    cases.append(('F174 prototype values at (1,2) mod 9', (w.A((1, 2)), w.B((1, 2)), w.invariant((1, 2)), w.valuation((1, 2))) == ((2, 3), (1, 5), 4, 0)))
    cases.append(('the commutator mod 9 is (7,3,3,4)', w.commutator() == (7, 3, 3, 4)))
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('Ω42 SDK SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    print(__doc__)
