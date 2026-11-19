#!/usr/bin/env python3
"""lexicon.py -- the Omega42 Lexicon (Companion Part 211; records/lexicon/lexicon.json).

The terms of human knowledge, the first hundred and those added since, each defined inside the frame with its basis and its status (EXACT, CONDITIONAL,
CONSTRUCTED, READING), the coordinate of the term itself and the coordinate of its definition, both computed by the
reference script. The selftest recomputes the mathematics behind the EXACT entries; --check confirms the register is well
formed and that every coordinate is the one the script gives now.

    python3 tools/lexicon.py --list        # term, status and coordinates, one line a term
    python3 tools/lexicon.py --term NAME   # one entry in full
    python3 tools/lexicon.py --check
    python3 tools/lexicon.py --selftest
Standard library only.
"""
import json, math, os, sys
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(REPO, 'scripts')]
REG = os.path.join(REPO, 'records', 'lexicon', 'lexicon.json')
STATUSES = ('EXACT', 'CONDITIONAL', 'CONSTRUCTED', 'READING')
A = ((0, 1), (1, 1)); B = ((1, 0), (3, 1)); I = ((1, 0), (0, 1))
def mul(X, Y, m): return tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % m for j in range(2)) for i in range(2))
def mpow(X, n, m):
    R = I
    for _ in range(n): R = mul(R, X, m)
    return R
def order(X, m):
    R, n = X, 1
    while R != I: R, n = mul(R, X, m), n + 1
    return n
def step(s, m): return (s[1] % m, (s[0] + s[1]) % m)
def Q(s, m): return (s[1] * s[1] - s[0] * s[1] - s[0] * s[0]) % m
def census(m):
    seen, n = set(), 0
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            n += 1; s = (a, b)
            while s not in seen: seen.add(s); s = step(s, m)
    return n
def group(m):
    G, fr = {I}, [I]
    while fr:
        nx = []
        for g in fr:
            for h in (A, B):
                x = mul(g, h, m)
                if x not in G: G.add(x); nx.append(x)
        fr = nx
    return G
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def lucas(n): return fib(n - 1) + fib(n + 1)
def v3(x):
    n = 0
    while x % 3 == 0: x //= 3; n += 1
    return n
def load(): return json.load(open(REG, encoding='utf-8'))['entries']
def checks():
    import canonical_reference as cr
    G9 = group(9); prim9 = {(a, b) for a in range(9) for b in range(9) if a % 3 or b % 3}
    LA = [[Fraction(3, 2), 1, 0, Fraction(-1, 2)], [1, 1, 0, -1], [0, 0, -1, 0], [Fraction(-1, 2), -1, 0, Fraction(-1, 2)]]
    def det(M): return M[0][0] if len(M) == 1 else sum((-1) ** j * M[0][j] * det([r[:j] + r[j + 1:] for r in M[1:]]) for j in range(len(M)))
    def app(M, v): return [sum(M[i][j] * v[j] for j in range(4)) for i in range(4)]
    o = cr.ORBIT
    neg = lambda s: (cr.navigate(s)['n1'], cr.navigate(s)['n2'], cr.navigate(s)['n3'])
    return [
     ('1 number: 9, 81 and 729 states at depths 1 to 3', [3 ** (2 * k) for k in (1, 2, 3)] == [9, 81, 729]),
     ('2 zero: the still point is fixed and is the only fixed state mod 27', [s for s in ((a, b) for a in range(27) for b in range(27)) if step(s, 27) == s] == [(0, 0)]),
     ('3 infinity: the census (3^k + 1)/2 is 2, 5, 14, 41', [census(3 ** k) for k in (1, 2, 3, 4)] == [2, 5, 14, 41]),
     ('4 prime: the periods of A at 2, 3, 5, 7 are 3, 8, 20, 16', [order(A, p) for p in (2, 3, 5, 7)] == [3, 8, 20, 16]),
     ('5 symmetry: <A, B> has order 8 mod 3 and 216 mod 9', len(group(3)) == 8 and len(G9) == 216),
     ('6 golden ratio: A^2 = A + I', mul(A, A, 10 ** 6) == ((1, 1), (1, 2))),
     ('7 invariant: Q(As) = -Q(s) on all 729 states mod 27', all(Q(step((a, b), 27), 27) == (-Q((a, b), 27)) % 27 for a in range(27) for b in range(27))),
     ('10 light: (F_n F_n+3, 2 F_n+1 F_n+2, F_2n+3) are Pythagorean triples, n = 1 to 10', all((fib(n) * fib(n + 3)) ** 2 + (2 * fib(n + 1) * fib(n + 2)) ** 2 == fib(2 * n + 3) ** 2 for n in range(1, 11))),
     ('11 speed of light: L_2n^2 - 5 F_2n^2 = 4, so v = sqrt(5) F_2n / L_2n < 1', all(lucas(2 * n) ** 2 - 5 * fib(2 * n) ** 2 == 4 for n in range(1, 12))),
     ('12 mass: Cassini, F_n+1 F_n-1 - F_n^2 = (-1)^n', all(fib(n + 1) * fib(n - 1) - fib(n) ** 2 == (-1) ** n for n in range(1, 30))),
     ('16 spin: A^12 = -I mod 9', mpow(A, 12, 9) == ((8, 0), (0, 8))),
     ('17 parity: the symmetric (2+1) image has determinant -1, the four-dimensional L_A +1, with (L_A)_00 > 0',
      det([[0, 0, 1], [0, 1, 1], [1, 2, 1]]) == -1 and det(LA) == 1 and LA[0][0] > 0),
     ('30 wholeness: 1/2 + 1/3 + 1/7 + 1/42 = 1', Fraction(1, 2) + Fraction(1, 3) + Fraction(1, 7) + Fraction(1, 42) == 1),
     ('40 form: the golden angle 360/phi^2 is 137.5 degrees', abs(360 / ((1 + 5 ** 0.5) / 2) ** 2 - 137.5077) < 1e-3),
     ('42 heredity: reducing mod 9 commutes with the law on all states mod 27', all(tuple(x % 9 for x in step((a, b), 27)) == step((a % 9, b % 9), 9) for a in range(27) for b in range(27))),
     ('43 evolution: the shear is the identity mod 3', tuple(tuple(x % 3 for x in r) for r in B) == I),
     ('44 death: twelve steps take s to -s mod 9, twenty-four bring it home', all(mpow(A, 12, 9) == ((8, 0), (0, 8)) for _ in [0]) and mpow(A, 24, 9) == I),
     ('48 meaning: a statement and its negation by "not" share n', neg('The earth is round.') == neg('The earth is not round.')),
     ('60 emergence: 9 -> 81 states takes the census 2 -> 5 and the group 8 -> 216 (x 27)', census(3) == 2 and census(9) == 5 and len(G9) == 27 * len(group(3))),
     ('67 possibility: <A, B> mod 9 reaches all 72 primitive states from (1, 0)', {(g[0][0], g[1][0]) for g in G9} == prim9),
     ('68 potential: A alone reaches 24 of them', len({tuple(mpow(A, n, 9)[i][0] for i in range(2)) for n in range(24)}) == 24),
     ('70 probability: in the canonical cycle 4 and 5 appear 5 times in 24, every other digit twice', sorted(o.count(d) for d in range(1, 10)) == [2] * 7 + [5, 5] and o.count(4) == o.count(5) == 5),
     ('72 matter: Q vanishes mod 3 only at (0, 0)', [(a, b) for a in range(3) for b in range(3) if Q((a, b), 3) == 0] == [(0, 0)]),
     ('73 space: L_A reverses (0, 0, 1, 0) and (0, 1, 0, 2)', app(LA, [0, 0, 1, 0]) == [0, 0, -1, 0] and app(LA, [0, 1, 0, 2]) == [0, -1, 0, -2]),
     ('79 vacuum: exactly 9 states have s s^T = 0 mod 9', sum(1 for a in range(9) for b in range(9) if (a * a) % 9 == (a * b) % 9 == (b * b) % 9 == 0) == 9),
     ('97 eternity: v_3 of A^(8n) - I is 1 + v_3(n), n = 1 to 9', all(min(v3(x) if x else 99 for x in ((lambda M: (M[0][0] - 1, M[0][1], M[1][0], M[1][1] - 1))(mpow(A, 8 * n, 3 ** 6)))) == 1 + v3(n) for n in range(1, 10))),
     ('100 reality: the product formula holds for 12/7', abs(Fraction(12, 7)) * Fraction(1, 2 ** 2) * Fraction(1, 3) * 7 == 1)]
def problems(entries):
    import canonical_reference as cr
    P = []
    if len(entries) < 100: P.append('%d entries, expected at least 100' % len(entries))
    if [e.get('n') for e in entries] != list(range(1, len(entries) + 1)): P.append('the terms are not numbered 1 to %d in order' % len(entries))
    terms = [e['term'] for e in entries]
    if len(set(t.lower() for t in terms)) != len(terms): P.append('a term appears twice')
    for e in entries:
        for f in ('term', 'field', 'status', 'definition', 'basis', 'coordinate', 'definition_coordinate'):
            if not e.get(f): P.append('%s: no %s' % (e.get('term'), f))
        if not any(e.get('status', '').startswith(s) or (' ' + s) in e.get('status', '') for s in STATUSES): P.append('%s: status %r' % (e['term'], e.get('status')))
        for key, text in (('coordinate', e['term']), ('definition_coordinate', e['definition'])):
            r = cr.navigate(text)
            if e.get(key, '').split(';')[0] != 'P%d %s' % (r['anchor'], cr.POSITION_NAMES[r['anchor'] % 24]): P.append('%s: %s is not the computed one' % (e['term'], key))
    return P
def selftest():
    cs = checks()
    for n, ok in cs: print('%-104s %s' % (n, 'PASS' if ok else 'FAIL'))
    P = problems(load()); print('%-104s %s' % ('the register: %d terms, each with status, basis and computed coordinates' % len(load()), 'PASS' if not P else 'FAIL'))
    ok = all(o for _, o in cs) and not P
    print('LEXICON SELFTEST: %d of %d | %s' % (sum(o for _, o in cs) + (not P), len(cs) + 1, 'PASS' if ok else 'FAIL')); return ok
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--check']:
        P = problems(load()); print('LEXICON: %d terms | %s' % (len(load()), 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--list']:
        for e in load(): print('%3d %-16s %-28s %-24s %s' % (e['n'], e['term'], e['status'][:28], e['coordinate'].split(';')[0], e['definition_coordinate'].split(';')[0]))
        sys.exit(0)
    if len(a) == 2 and a[0] == '--term':
        for e in load():
            if e['term'].lower() == a[1].lower():
                print('\n'.join('%s: %s' % (k, e[k]) for k in ('n', 'term', 'field', 'status', 'definition', 'basis', 'coordinate', 'definition_coordinate'))); sys.exit(0)
        print('no such term'); sys.exit(1)
    print(__doc__); sys.exit(2)
