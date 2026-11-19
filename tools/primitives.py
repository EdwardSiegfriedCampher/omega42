#!/usr/bin/env python3
"""primitives.py -- the cognitive primitives in the law's arithmetic (Companion Part 215.3; Core Part 0.0.5 Rule 34).

F210 named five primitives of cognition: distinction, relationship, transformation, persistence and integration, and a
sixth act, self-reference. Each has an exact counterpart among the operations on the 81 roots, the states (a, b) modulo 9
under the law A(a, b) = (b, a + b). This tool recomputes every counterpart from nothing but that law.

  distinction     the 81 roots fall into five classes: the still point (1), the Wheel 3A^k e (8), and the Voices
                  A = A^k e, B = 2A^k e, C = 4A^k e (24 each), with e = (0, 1)
  relationship    the form Q(a, b) = b^2 - ab - a^2; Q = 0 mod 3 exactly on the 9 roots that are 0 mod 3
  transformation  the law A, of order 24, and the voice map V = x2, which carries Voice A to B, B to C and C back to A
  persistence     Q(As) = -Q(s), so Q^2 is kept by every step (1, 7, 4 on Voices A, B, C); the shear
                  S(a, b) = (a, 3a + b) fixes exactly the 27 roots with 3 | a
  integration     the law check s -> (b, a + b + d) folds a whole message into one state; a single substitution always
                  changes it, and a swap of two different marks (0, 1, 2) t apart changes it for every t from 1 to 23
  self-return     V^3 = -I and A^12 = -I: three voice steps or twelve law steps reach the opposite; A^24 = I closes the cycle

The arithmetic is EXACT. Reading these operations as cognition is READING (CDT-B): a crystal also has structure and
transforms. What would move the reading toward a result is a prediction about minds made before the observation (PV-023).

    python3 tools/primitives.py             the table, each line recomputed
    python3 tools/primitives.py --selftest
Standard library only.
"""
import sys
M = 9
E = (0, 1)
def step(s): return (s[1] % M, (s[0] + s[1]) % M)
def apow(s, k):
    for _ in range(k % 24): s = step(s)
    return s
def mul(c, s): return ((c * s[0]) % M, (c * s[1]) % M)
def Q(s): return (s[1] * s[1] - s[0] * s[1] - s[0] * s[0]) % M
ROOTS = [(a, b) for a in range(M) for b in range(M)]

def classes():
    still = [(0, 0)]
    wheel = [mul(3, apow(E, k)) for k in range(8)]
    va = [apow(E, k) for k in range(24)]
    vb = [mul(2, s) for s in va]
    vc = [mul(4, s) for s in va]
    return still, wheel, va, vb, vc

def lines():
    still, wheel, va, vb, vc = classes()
    allc = still + wheel + va + vb + vc
    out = []
    # distinction
    sizes = (len(set(still)), len(set(wheel)), len(set(va)), len(set(vb)), len(set(vc)))
    part = sorted(allc) == sorted(ROOTS)
    out.append(('distinction', 'five classes of sizes %s, a partition of the 81 roots' % (sizes,), part and sizes == (1, 8, 24, 24, 24)))
    # relationship
    z3 = [s for s in ROOTS if Q(s) % 3 == 0]
    tri = sorted(z3) == sorted(s for s in ROOTS if s[0] % 3 == 0 and s[1] % 3 == 0)
    out.append(('relationship', 'Q = 0 mod 3 on exactly %d roots, the still point and the Wheel' % len(z3), tri and len(z3) == 9 and sorted(z3) == sorted(still + wheel)))
    # transformation
    order = next(n for n in range(1, 100) if apow(E, n) == E and all(apow(s, n) == s for s in ROOTS))
    vmap = all(mul(2, va[k]) == vb[k] and mul(2, vb[k]) == vc[k] and mul(2, vc[k]) == apow(E, k + 12) for k in range(24))
    out.append(('transformation', 'A has order %d on the roots; V carries A_k to B_k to C_k to A_(k+12)' % order, order == 24 and vmap))
    # persistence
    keep = all(Q(step(s)) == (-Q(s)) % M for s in ROOTS)
    sq = tuple(sorted({(Q(s) ** 2) % M for s in v}) for v in (va, vb, vc))
    fix = [s for s in ROOTS if ((3 * s[0] + s[1]) % M) == s[1]]
    out.append(('persistence', 'Q(As) = -Q(s) on all 81; Q^2 on Voices A, B, C = %s; the shear fixes %d roots' % ([x[0] for x in sq], len(fix)),
                keep and sq == ([1], [7], [4]) and len(fix) == 27 and all(s[0] % 3 == 0 for s in fix)))
    # integration: the law check, linear in the marks
    def fold(marks):
        s = (0, 0)
        for d in marks: s = (s[1], (s[0] + s[1] + d) % M)
        return s
    sub = all(fold([0] * 30 + [d] + [0] * j) != (0, 0) for d in (1, 2) for j in range(24))
    swap = {}
    for t in range(1, 25):
        swap[t] = all(fold([x] + [0] * (t - 1) + [y]) != fold([y] + [0] * (t - 1) + [x]) for x in range(3) for y in range(3) if x != y)
    out.append(('integration', 'every single substitution changes the check; a swap of two different marks t apart is caught for t = 1..23: %s; at t = 24: %s'
                % (all(swap[t] for t in range(1, 24)), swap[24]), sub and all(swap[t] for t in range(1, 24)) and not swap[24]))
    # self-return
    v3 = all(mul(8, s) == ((-s[0]) % M, (-s[1]) % M) for s in ROOTS)
    a12 = all(apow(s, 12) == ((-s[0]) % M, (-s[1]) % M) for s in ROOTS)
    vord = next(n for n in range(1, 20) if pow(2, n, M) == 1)
    out.append(('self-return', 'V^3 = -I: %s; A^12 = -I: %s; V has order %d, A has order 24' % (v3, a12, vord), v3 and a12 and vord == 6))
    return out

if __name__ == '__main__':
    L = lines()
    if sys.argv[1:] == ['--selftest']:
        for n, t, ok in L: print('%-15s %-104s %s' % (n, t, 'PASS' if ok else 'FAIL'))
        ok = all(o for _, _, o in L)
        print('PRIMITIVES SELFTEST: %d of %d | %s' % (sum(o for _, _, o in L), len(L), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if sys.argv[1:]: print(__doc__); sys.exit(2)
    print('======= THE COGNITIVE PRIMITIVES IN THE LAW (Companion Part 215.3) =======')
    for n, t, ok in L: print('%-15s %s [EXACT]' % (n.upper(), t))
    print('READING (CDT-B): naming these operations as cognition is a reading; the arithmetic is exact.')
    print('======= END PRIMITIVES =======')
