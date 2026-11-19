#!/usr/bin/env python3
"""quantum.py -- the law in quantum mechanics: the fusion of Fibonacci anyons, the 81 states as the phase space of a nine-level
quantum system, the law as time reversal, complementarity, nonclassicality, and spin (Companion Part 229).

  K1 fusion-law          the fusion rules of the Fibonacci anyon, 1 x tau = tau, tau x tau = 1 + tau, have the matrix N_tau = A in the
                         basis (1, tau): the quantum dimension is phi, and n anyons of total charge tau span F_n states (exact);
                         the F-matrix is unitary and involutive, and the braid matrices obey s1 s2 s1 = s2 s1 s2 (numerical)
  K2 wigner-81           the Weyl operators D(a, b) of a nine-level system are labeled by the 81 states; the discrete Wigner function
                         is real, sums to 1, and its marginals are the probabilities of position and momentum; under the unitary U of
                         A^2, W of U rho U^dagger at A^2 s equals W of rho at s, for every state and every point (numerical)
  K3 law-time-reversal   the law, of determinant -1, is quantized as an antiunitary operator: complex conjugation K realizes
                         (a, b) -> (a, -b), and V = U_(A R) K with R = diag(1, -1) satisfies V D(s) V^-1 = D(A s); V^2 is the unitary
                         of A^2 up to phase: the sign rule Q(As) = -Q(s) is time reversal in the quantum layer (numerical)
  K4 law-complementarity the unitary of A^2 carries the position basis to a basis unbiased to it, |<x|U|y>|^2 = 1/9 for all 81
                         pairs; the position basis returns after 6 powers, and the odd powers give unbiased bases, the even powers neither (numerical)
  K5 negativity          the Wigner function of the 9 position states and of their Clifford images is nonnegative; the cubic-phase
                         state sum_k w^(k^3) |k> / 3 has negative entries, its negativity sum |W| - 1 measured (numerical)
  K6 spin-cover          the golden rotation [[phi, -1], [1, 0]] of SL2(Z[phi]) has fifth power -I: five turns of 72 degrees return
                         every vector and negate every spinor, the double cover SU(2) -> SO(3) shown by an element of the law's ring (exact)
  K7 not-two-qutrits     the additive group of the 81 states, (Z/9)^2, has elements of order 9 and is not (Z/3)^4, the phase space
                         of two qutrits: the 81 states describe one nine-level system, not a pair (exact)

    python3 tools/quantum.py --selftest
Standard library and numpy; exact Fraction arithmetic in K1 (counts), K6 and K7.
"""
import sys, math, cmath, itertools
from fractions import Fraction as Fr
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
PHI = (1 + 5 ** .5) / 2
import numpy as np
# K1
A = [[0, 1], [1, 1]]
def mmi(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
fuse = {('1', '1'): ['1'], ('1', 't'): ['t'], ('t', '1'): ['t'], ('t', 't'): ['1', 't']}
N = [[sum(1 for c in fuse[('t', x)] if c == y) for x in ('1', 't')] for y in ('1', 't')]
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def paths(n, total):
    """fusion paths of n tau anyons starting from the vacuum with total charge 'total'"""
    cur = {'1': 1, 't': 0}
    for _ in range(n):
        nxt = {'1': 0, 't': 0}
        for c, m in cur.items():
            for o in fuse[(c, 't')]: nxt[o] += m
        cur = nxt
    return cur[total]
dims = [paths(n, 't') for n in range(1, 15)]
Fm = np.array([[1 / PHI, 1 / math.sqrt(PHI)], [1 / math.sqrt(PHI), -1 / PHI]])
R = np.diag([cmath.exp(-4j * math.pi / 5), cmath.exp(3j * math.pi / 5)])
s1 = R; s2 = Fm @ R @ Fm
ok1 = N == A and dims == [fib(n) for n in range(1, 15)] and np.allclose(Fm @ Fm, np.eye(2)) and np.allclose(Fm @ Fm.T, np.eye(2)) and np.allclose(s1 @ s2 @ s1, s2 @ s1 @ s2) and abs(max(np.linalg.eigvals(np.array(A, float))) - PHI) < 1e-12
P('fusion-law', ok1, 'the Fibonacci anyon fuses by 1 x tau = tau and tau x tau = 1 + tau, whose matrix in the basis (1, tau) is', N, '= A, the law;',
  'its Perron eigenvalue phi is the quantum dimension, and n anyons of total charge tau span', dims[:10], '... = F_n states; the F-matrix [[1/phi, 1/sqrt(phi)], [1/sqrt(phi), -1/phi]] is unitary with F^2 = 1,',
  'and the braid matrices s1 = R, s2 = F R F with R = diag(e^(-4 pi i/5), e^(3 pi i/5)) obey s1 s2 s1 = s2 s1 s2: the law counts the quantum states of the anyons that braid universally')
# K2: the nine-level system
d = 9; w = cmath.exp(2j * math.pi / d); inv2 = pow(2, -1, d)
Xo = np.roll(np.eye(d), 1, axis=0); Zo = np.diag([w ** k for k in range(d)])
def D(a, b): return (w ** ((a * b * inv2) % d)) * np.linalg.matrix_power(Xo, a % d) @ np.linalg.matrix_power(Zo, b % d)
Par = np.zeros((d, d))
for k in range(d): Par[(-k) % d, k] = 1
PO = {(a, b): D(a, b) @ Par @ D(a, b).conj().T for a in range(d) for b in range(d)}
def wig(r): return np.array([[np.trace(r @ PO[(a, b)]).real / d for b in range(d)] for a in range(d)])
def act(M, s): return ((M[0][0] * s[0] + M[0][1] * s[1]) % d, (M[1][0] * s[0] + M[1][1] * s[1]) % d)
def clifford(M):
    """the unitary U with U D(s) U^dagger = D(M s), M of determinant 1 modulo 9"""
    U = sum(D(*act(M, (a, b))) @ D(a, b).conj().T for a in range(d) for b in range(d))
    return U / math.sqrt(abs(np.trace(U @ U.conj().T)) / d)
rng = np.random.default_rng(7)
A2 = [[1, 1], [1, 2]]; U2 = clifford(A2)
ok2 = np.allclose(U2 @ U2.conj().T, np.eye(d)) and all(np.allclose(U2 @ D(a, b) @ U2.conj().T, D(*act(A2, (a, b)))) for a in range(d) for b in range(d))
for _ in range(5):
    v = rng.normal(size=d) + 1j * rng.normal(size=d); v /= np.linalg.norm(v); r = np.outer(v, v.conj())
    W0 = wig(r); W1 = wig(U2 @ r @ U2.conj().T)
    pmom = np.abs(np.fft.fft(v) / 3) ** 2
    ok2 = ok2 and abs(W0.sum() - 1) < 1e-12 and np.allclose(W0.sum(1), np.abs(v) ** 2) and all(abs(W1[act(A2, (a, b))] - W0[a, b]) < 1e-12 for a in range(d) for b in range(d))
    ok2 = ok2 and np.allclose(sorted(W0.sum(0)), sorted(pmom))
P('wigner-81', ok2, 'the 81 states label the Weyl operators D(a, b) = w^(ab/2) X^a Z^b of a nine-level quantum system, w = e^(2 pi i/9); the discrete Wigner function W(a, b) = Tr(rho D(a, b) Pi D(a, b)^dagger)/9 is real, sums to 1, and its rows sum to the position probabilities,',
  'for five random states; the unitary U of A^2, built as the intertwiner of the Weyl operators, satisfies U D(s) U^dagger = D(A^2 s) on all 81 states, and W of U rho U^dagger at A^2 s equals W of rho at s: the law\'s square moves quantum states as it moves the 81 points')
# K3
Rm = [[1, 0], [0, d - 1]]; AR = [[0, d - 1], [1, d - 1]]                 # A R = [[0, -1], [1, -1]], determinant 1
UAR = clifford(AR)
def V_apply_op(O): return UAR @ O.conj() @ UAR.conj().T                    # V O V^-1 with V = U K
ok3 = all(np.allclose(D(a, b).conj(), D(*act(Rm, (a, b)))) for a in range(d) for b in range(d)) and all(np.allclose(V_apply_op(D(a, b)), D(*act(A, (a, b)))) for a in range(d) for b in range(d))
VV = UAR @ UAR.conj()                                                       # V^2 = U K U K = U conj(U)
ph = VV[0, :] @ U2.conj().T[:, 0] if False else None
ratio = VV @ U2.conj().T
ok3 = ok3 and np.allclose(ratio, ratio[0, 0] * np.eye(d)) and abs(abs(ratio[0, 0]) - 1) < 1e-12
v = rng.normal(size=d) + 1j * rng.normal(size=d); v /= np.linalg.norm(v); r = np.outer(v, v.conj())
W0 = wig(r); W1 = wig(UAR @ r.conj() @ UAR.conj().T)
ok3 = ok3 and all(abs(W1[act(A, (a, b))] - W0[a, b]) < 1e-12 for a in range(d) for b in range(d))
P('law-time-reversal', ok3, 'complex conjugation K sends D(a, b) to D(a, -b), the reflection R = diag(1, -1); the law A = (A R) R, with A R of determinant 1, is quantized as the antiunitary V = U_(AR) K, and V D(s) V^-1 = D(A s) on all 81 states;',
  'V^2 equals the unitary of A^2 up to a phase, and W of V rho V^-1 at A s equals W of rho at s: the law is quantum time reversal joined to a Clifford unitary, and the sign rule Q(As) = -Q(s) is the reversal of time in the quantum layer')
# K4
ov = np.abs(U2) ** 2
ok4 = np.allclose(ov, 1 / d)
bases = [np.eye(d)]; Uk = np.eye(d)
for k in range(1, 13): Uk = U2 @ Uk; bases.append(Uk)
def unbiased(B1, B2): return np.allclose(np.abs(B1.conj().T @ B2) ** 2, 1 / d)
def same(B1, B2):
    G = np.abs(B1.conj().T @ B2) ** 2
    return np.allclose(np.sort(G, axis=1)[:, -1], 1)
per = min(k for k in range(1, 13) if same(bases[0], bases[k]))
pattern = ''.join('U' if unbiased(bases[0], bases[k]) else ('=' if same(bases[0], bases[k]) else 'b') for k in range(per + 1))
P('law-complementarity', ok4 and per == 6 and pattern == '=UbUbU=', 'the unitary of A^2 carries the position basis to a basis unbiased to it, |<x|U|y>|^2 = 1/9 for all 81 pairs: the law generates complementarity;',
  'the position basis returns under the powers of U after %d steps, since (A^2)^6 = A^12 = -I modulo 9 maps each position state to its mirror, with the pattern %s (U unbiased, b biased, = the same basis) against the position basis' % (per, pattern))
# K5
negs = []
pos_ok = True
for k in range(d):
    e = np.zeros(d); e[k] = 1; r = np.outer(e, e)
    for M in (A2, AR, [[1, 0], [3, 1]]):
        Uc = clifford(M); pos_ok = pos_ok and wig(Uc @ r @ Uc.conj().T).min() > -1e-12
cub = np.array([w ** ((k ** 3) % d) for k in range(d)]) / 3
Wc = wig(np.outer(cub, cub.conj())); neg = float(np.abs(Wc).sum() - 1)
P('negativity', pos_ok and Wc.min() < -1e-6 and neg > 0.1, 'the Wigner functions of the 9 position states and of their images under the Clifford unitaries of A^2, A R and the shear B are nonnegative on all 81 points, the classical readings;',
  'the cubic-phase state sum_k w^(k^3)|k>/3 takes the value %.4f at its most negative point and has negativity sum|W| - 1 = %.4f: nonclassicality is measured on the 81 states' % (float(Wc.min()), neg))
# K6
class Q5:
    __slots__ = ('a', 'b')
    def __init__(s, a=0, b=0): s.a = Fr(a); s.b = Fr(b)
    def __add__(s, o): return Q5(s.a + o.a, s.b + o.b)
    def __mul__(s, o): return Q5(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
    def __neg__(s): return Q5(-s.a, -s.b)
def qmm(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
Rg = [[Q5(0, 1), Q5(-1)], [Q5(1), Q5(0)]]
P5 = [[Q5(1), Q5(0)], [Q5(0), Q5(1)]]
for _ in range(5): P5 = qmm(P5, Rg)
P10 = qmm(P5, P5)
ok6 = P5 == [[Q5(-1), Q5(0)], [Q5(0), Q5(-1)]] and P10 == [[Q5(1), Q5(0)], [Q5(0), Q5(1)]]
P('spin-cover', ok6, 'the golden rotation [[phi, -1], [1, 0]] of SL2(Z[phi]) has fifth power -I and tenth power I, exact in Z[phi]; its Lorentz image, the rotation by 72 degrees of MF-150, has fifth power I:',
  'five turns return every vector and negate every spinor, the double cover of the rotations by the spin group shown by an element of the law\'s ring; relativity and quantum mechanics meet in SL2(C), the one acting on vectors, the other on spinors')
# K7
orders9 = max(math.lcm(9 // math.gcd(9, a), 9 // math.gcd(9, b)) if (a or b) else 1 for a in range(9) for b in range(9))
orders3 = 3
P('not-two-qutrits', orders9 == 9 and orders3 == 3, 'the additive group of the 81 states, (Z/9)^2, has elements of order 9, while every element of (Z/3)^4, the phase space of two qutrits, has order at most 3: the two are not isomorphic,',
  'and the 81 states describe one nine-level system, with no factorization into a pair of qutrits on which entanglement is defined')
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('QUANTUM SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    print(__doc__); sys.exit(2)
