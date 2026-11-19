#!/usr/bin/env python3
"""omega_kit.py -- the established-mathematics kit (Core Part 3.74): four instruments built only on proved results.

  M348 Depth Dial        python3 tools/omega_kit.py dial A B K R      the class of state (A, B) mod 3^K seen at depth R
                         python3 tools/omega_kit.py dial --ladder K   how many classes survive at each depth R (MF-43)
  M349 Route Comparator  python3 tools/omega_kit.py route W1 W2 [A B K] two words in A and B (e.g. AAB, BA): same matrix,
                                                                       same state, same orbit -- three relations (F170 P3)
  M350 Prime Lens        python3 tools/omega_kit.py prime N           class, period, antipode, first-lift valuation
                         python3 tools/omega_kit.py prime --table P   the first-lift valuation of every prime <= P
                         python3 tools/omega_kit.py select            the conditional selection of (Q(sqrt5), 3), MF-49
  M351 Native Count      python3 tools/omega_kit.py native N          where N occurs in the arithmetic, with its base rate
  python3 tools/omega_kit.py --selftest

Standard library only, exact arithmetic.
"""
import sys
from math import gcd

A = (0, 1, 1, 1)


def mul(X, Y, m):
    return ((X[0] * Y[0] + X[1] * Y[2]) % m, (X[0] * Y[1] + X[1] * Y[3]) % m,
            (X[2] * Y[0] + X[3] * Y[2]) % m, (X[2] * Y[1] + X[3] * Y[3]) % m)


def mpow(X, n, m):
    R = (1 % m, 0, 0, 1 % m)
    while n:
        if n & 1:
            R = mul(R, X, m)
        X = mul(X, X, m); n >>= 1
    return R


def app(X, v, m):
    return ((X[0] * v[0] + X[1] * v[1]) % m, (X[2] * v[0] + X[3] * v[1]) % m)


def Q(a, b):
    return 2 * (a * a + a * b - b * b)


def v3(x):
    n = 0
    while x and x % 3 == 0:
        x //= 3; n += 1
    return n


# ------------------------------------------------------------------ M348 Depth Dial
def dial_class(a, b, k, r):
    m = 3 ** k; a %= m; b %= m
    if a == 0 and b == 0:
        return ('zero',)
    j = min(v3(a) if a else k, v3(b) if b else k)
    u = (a // 3 ** j, b // 3 ** j); e = min(r, k - j)
    return (j, Q(*u) ** 2 % 3 ** e)


def ladder(k):
    return [(r, 1 + sum(3 ** (min(r, mm) - 1) for mm in range(1, k + 1))) for r in range(1, k + 1)]


# ------------------------------------------------------------------ M349 Route Comparator
def word_matrix(w, m, r=1):
    B = (1, 0, 3 ** r, 1); M = (1 % m, 0, 0, 1 % m)
    for ch in w.upper():
        M = mul({'A': A, 'B': B}[ch], M, m)          # read left to right as the order of application
    return M


def route(w1, w2, s=(1, 0), k=2):
    m = 3 ** k
    M1, M2 = word_matrix(w1, m), word_matrix(w2, m)
    x1, x2 = app(M1, s, m), app(M2, s, m)
    orbA = set(); y = x1
    for _ in range(8 * 3 ** (k - 1)):
        orbA.add(y); y = app(A, y, m)
    same_orbit_AB = dial_class(*x1, k, 1) == dial_class(*x2, k, 1)
    return dict(same_matrix=M1 == M2, same_state=x1 == x2, same_orbit_A=x2 in orbA, same_orbit_AB=same_orbit_AB,
                x1=x1, x2=x2)


# ------------------------------------------------------------------ M350 Prime Lens
def is_prime(n):
    if n < 2:
        return False
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i += 1
    return True


def order(m):
    a, b, k = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; k += 1
        if (a, b) == (0, 1 % m):
            return k


def prime_class(p):
    if p == 5:
        return 'ramified'
    if p == 2:
        return 'inert'
    return 'split' if p % 5 in (1, 4) else 'inert'


def first_lift_wss(p):
    """True when A^pi(p) = I mod p^2 (first-lift valuation >= 2, a Wall-Sun-Sun prime); via the bound p-1 or 2(p+1)."""
    if p in (2, 5):
        return mpow(A, order(p), p * p) == (1, 0, 0, 1)
    bound = p - 1 if p % 5 in (1, 4) else 2 * (p + 1)
    return mpow(A, bound, p * p) == (1, 0, 0, 1)


def lens(n):
    r = order(n); half = mpow(A, r // 2, n) if r % 2 == 0 else None
    anti = half == ((-1) % n, 0, 0, (-1) % n) and (-1) % n != 1 % n
    out = dict(n=n, period=r, antipodal=anti)
    if is_prime(n):
        out['class'] = prime_class(n)
        out['first_lift'] = '>=2 (Wall-Sun-Sun)' if first_lift_wss(n) else '1'
    return out


def select():
    """conditional selection: (P1) 2x2 integer, invertible over Z; (P2) minimal hyperbolic growth; (P3) the base level is a
    field (inert prime); (P4) every nonzero state has an antipode distinct from itself at half period at the base level."""
    polys = set()
    for a in range(-3, 4):
        for b in range(-3, 4):
            for c in range(-3, 4):
                for d in range(-3, 4):
                    det = a * d - b * c
                    if det not in (1, -1):
                        continue
                    tr = a + d; disc = tr * tr - 4 * det
                    if disc <= 0 or int(disc ** 0.5) ** 2 == disc:
                        continue
                    rho = (abs(tr) + disc ** 0.5) / 2
                    polys.add((round(rho, 12), tr, det))
    rmin = min(p[0] for p in polys)
    minimal = sorted(set((tr, det) for rho, tr, det in polys if rho == rmin))
    rows = []
    for p in [q for q in range(2, 60) if is_prime(q)]:
        inert = prime_class(p) == 'inert'
        r = order(p)
        anti = r % 2 == 0 and mpow(A, r // 2, p) == ((-1) % p, 0, 0, (-1) % p) and p != 2
        rows.append((p, prime_class(p), r, anti))
    passing = [p for p, cl, r, an in rows if cl == 'inert' and an]
    return dict(rho=rmin, minimal=minimal, rows=rows, selected=passing[0], first_lift_3=first_lift_wss(3))


# ------------------------------------------------------------------ M351 Native Count
def native_table(K=3):
    T = {}
    def add(v, why):
        T.setdefault(v, []).append(why)
    for k in range(1, K + 1):
        m = 3 ** k
        add(m * m, 'states of (Z/3^%d)^2' % k)
        add(8 * 3 ** (k - 1), 'ord of A mod 3^%d (and the longest orbit)' % k)
        add(4 * 3 ** (k - 1), 'half period, |P^1(Z/3^%d)|, |SO(N)| mod 3^%d' % (k, k))
        add(8, 'the shortest nonzero orbit, at every depth (|F_9^x|)')
        add((m + 1) // 2, 'orbits of A mod 3^%d' % k)
        add(8 * 27 ** (k - 1), '|<A,B> mod 3^%d|' % k)
        add(k + 1, 'orbits of <A,B> mod 3^%d' % k)
        add(9 ** (k // 2), 'null states of N mod 3^%d' % k)
        add(3 ** (k - 1), 'primitive orbits mod 3^%d (norm classes)' % k)
    add(1, 'the fixed point'); add(2, 'the sign of Q under A'); add(3, 'the prime; norm classes mod 9')
    add(5, 'the discriminant; orbits mod 9'); add(20, 'ord of A mod 5'); add(12, 'ord of X -> AXA^T mod 9')
    return T


def native(n, K=3):
    T = native_table(K)
    hits = T.get(n, [])
    rate = sum(1 for x in range(1, 1001) if x in T) / 1000
    return hits, rate


# ------------------------------------------------------------------ selftest and CLI
def selftest():
    S = select()
    cases = [
        ('M348 dial ladder mod 3^4 at r=1..4 is 5, 11, 23, 41 classes', [c for _, c in ladder(4)] == [5, 11, 23, 41]),
        ('M348 dial r=k recovers the Fibonacci census (3^k+1)/2', all(ladder(k)[-1][1] == (3 ** k + 1) // 2 for k in range(1, 6))),
        ('M348 dial class of (1,0) and (1,3) mod 9 differ at r=2 and agree at r=1',
         dial_class(1, 0, 2, 2) != dial_class(1, 3, 2, 2) and dial_class(1, 0, 2, 1) == dial_class(1, 3, 2, 1)),
        ('M349 route: A^24 and the empty word are the same matrix mod 9', route('A' * 24, '')['same_matrix']),
        ('M349 route: B then A^n reaches another A-orbit but the same <A,B>-orbit',
         (lambda r: not r['same_orbit_A'] and r['same_orbit_AB'] and not r['same_matrix'])(route('BA', 'A'))),
        ('M350 lens: 3 inert, period 8, antipodal, first lift 1', lens(3) == dict(n=3, period=8, antipodal=True, **{'class': 'inert', 'first_lift': '1'})),
        ('M350 lens: 2 inert, period 3, no antipode', lens(2)['period'] == 3 and not lens(2)['antipodal']),
        ('M350 lens: 11 split, halfway not central', lens(11)['class'] == 'split' and not lens(11)['antipodal']),
        ('M350 no Wall-Sun-Sun prime below 20000', not any(first_lift_wss(p) for p in range(2, 20000) if is_prime(p))),
        ('MF-49 selection: minimal growth phi at trace +-1, det -1', abs(S['rho'] - (1 + 5 ** 0.5) / 2) < 1e-9 and S['minimal'] == [(-1, -1), (1, -1)]),
        ('MF-49 selection: 2 fails the antipode, 3 is the first inert prime that passes', S['selected'] == 3 and
         [row for row in S['rows'] if row[0] == 2][0][3] is False),
        ('M351 native: 24 and 81 are native, 7 is not', native(24)[0] and native(81)[0] and not native(7)[0]),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('ESTABLISHED-MATHEMATICS KIT SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:2] == ['dial', '--ladder']:
        k = int(a[2])
        print('M348 DEPTH DIAL -- classes of <A, B_r> on (Z/3^%d)^2 (MF-43)' % k)
        for r, c in ladder(k):
            print('  depth r=%d : %d classes%s' % (r, c, '  (= the Fibonacci census)' if r == k else '  (= the valuation strata)' if r == 1 else ''))
        return 0
    if a[:1] == ['dial']:
        x, y, k, r = map(int, a[1:5])
        print('M348 DEPTH DIAL: (%d, %d) mod 3^%d at depth %d -> class %s' % (x, y, k, r, dial_class(x, y, k, r)))
        return 0
    if a[:1] == ['route']:
        w1 = a[1] if a[1] != '-' else ''; w2 = a[2] if a[2] != '-' else ''
        s = (int(a[3]), int(a[4])) if len(a) > 4 else (1, 0); k = int(a[5]) if len(a) > 5 else 2
        r = route(w1, w2, s, k)
        print('M349 ROUTE COMPARATOR mod 3^%d from %s: %r -> %s, %r -> %s' % (k, s, w1, r['x1'], w2, r['x2']))
        print('  same matrix: %s | same state: %s | same A-orbit: %s | same <A,B>-orbit: %s' % (
            r['same_matrix'], r['same_state'], r['same_orbit_A'], r['same_orbit_AB']))
        return 0
    if a[:2] == ['prime', '--table']:
        P = int(a[2]); ps = [p for p in range(2, P + 1) if is_prime(p)]
        w = [p for p in ps if first_lift_wss(p)]
        print('M350 PRIME LENS -- first-lift valuation of the %d primes <= %d: Wall-Sun-Sun primes found: %s' % (len(ps), P, w or 'none'))
        return 0
    if a[:1] == ['prime']:
        print('M350 PRIME LENS: %s' % lens(int(a[1])))
        return 0
    if a[:1] == ['select']:
        S = select()
        print('MF-49 CONDITIONAL SELECTION (P1 2x2 integer invertible; P2 minimal hyperbolic growth; P3 the base level a field;')
        print('  P4 every nonzero state has an antipode distinct from itself at half period, at the base level)')
        print('  P2: minimal spectral radius %.9f at (trace, det) %s -- t^2 - t - 1 and its time-reverse t^2 + t - 1' % (S['rho'], S['minimal']))
        for p, cl, r, an in S['rows'][:10]:
            print('  p=%-3d %-8s period %-4d antipode %s' % (p, cl, r, an))
        print('  SELECTED: p = %d (2 is inert but its period 3 is odd and -1 = 1 mod 2: no antipode); first lift at 3: %s'
              % (S['selected'], 'valuation >= 2' if S['first_lift_3'] else 'valuation 1'))
        return 0
    if a[:1] == ['native']:
        n = int(a[1]); hits, rate = native(n)
        print('M351 NATIVE COUNT: %d -> %s' % (n, '; '.join(hits) if hits else 'not native at depths 1-3'))
        print('  base rate: %.1f%% of the integers 1..1000 are native at depths 1-3; a hit is necessary within Ω42 (L-556),'
              ' and says nothing of an outside structure without a map (L-510)' % (100 * rate))
        return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
