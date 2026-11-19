#!/usr/bin/env python3
"""quantum_foundations.py -- the quantum layer of Omega42 extended: the norm-fiber theorem and the simple spectrum, the explicit
quantum cat map and its periods, the qutrit, contextuality and the golden excess, the Bell state of two nine-level systems,
relative phase, the two exponents of one matrix, and the Fibonacci quantum walk (Companion Part 230; F222, F223; APE-484, APE-485).

  N1 norm-fiber          modulo 3^k, k = 1 to 5, the orbits of A^2 on primitive vectors are exactly the fibers of the norm
                         a^2 + ab - b^2, and the orbits of A exactly the fibers of the norm up to sign; the census is 1^1, 4^2, 12^6,
                         36^18, 108^54, 324^162 with 3^k orbits in all (exact)
  N2 simple-spectrum     the commutant of the quantum cat map U_N has dimension equal to the number of orbits of A^2 on the N^2
                         Weyl labels, which is N for N = 3, 9, 27: the spectrum of U_N is simple; the eigenvalues, computed, are
                         distinct (exact count; numerical spectrum)
  N3 explicit-kernel     U_N(j, k) = w^(j^2 - jk + k^2/2) / sqrt(N) is unitary and carries D(q, p) to D(q + p, q + 2p) for every odd
                         N from 3 to 19; its projective period equals the order of A^2 modulo N, and its literal period carries the
                         lift phase, -i at N = 11 and 19 (numerical)
  N4 qutrit              U_3 squared is the parity, U_3^4 = I; modulo 3 the eight nonzero labels form two four-cycles on which
                         Q = 2(a^2 + ab - b^2) takes the values 2 and 1 (exact)
  N5 kcbs-golden         the KCBS test of contextuality on one qutrit: the classical bound is 2 (the independence number of the
                         pentagon), the quantum maximum sqrt5 = phi + 1/phi (Lovasz), and the quantum excess sqrt5 - 2 = phi^-3,
                         exact in Q(sqrt5); the pentagram vectors reach it (exact; numerical check)
  N6 bell-81             two nine-level systems: the state sum_k |k k>/3 has reduced states I/9, entanglement entropy log2 9 bits, and
                         is kept by U (x) conj(U) for the unitary U of A^2: the law moves two entangled readings together (numerical)
  N7 relative-phase      (|0> + |1>)/sqrt2 and (|0> - |1>)/sqrt2 give the same probabilities in the position basis and (2/3, 1/6,
                         1/6) against (0, 1/2, 1/2) after the qutrit Fourier transform: phase is information (exact)
  N8 two-exponents       A^2 has Lyapunov exponent 2 ln phi on phase space and its symmetric square, the Lorentz boost, has
                         rapidity 4 ln phi: eigenvalues phi^(+-2) and phi^4, 1, phi^-4, one matrix in two representations (exact)
  N9 quantum-walk        a quantum walk whose coins follow the Fibonacci word in time spreads with mean-square displacement
                         exponent 1.82 and 1.69 for two coin pairs, against 2.00 for the periodic walk: superdiffusive and
                         sub-ballistic (numerical)

    python3 tools/quantum_foundations.py --selftest
Standard library and numpy.
"""
import sys, math, cmath, itertools
from fractions import Fraction as Fr
from collections import Counter
import numpy as np
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
PHI = (1 + 5 ** .5) / 2
# N1
def norm(a, b, m): return (a * a + a * b - b * b) % m
def orbits(M, m):
    seen = set(); out = []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o = []; s = (a, b)
            while s not in seen:
                seen.add(s); o.append(s); s = ((M[0][0] * s[0] + M[0][1] * s[1]) % m, (M[1][0] * s[0] + M[1][1] * s[1]) % m)
            out.append(o)
    return out
ok1 = True; census = {}
for k in range(1, 6):
    m = 3 ** k
    O2 = orbits([[1, 1], [1, 2]], m); O1 = orbits([[0, 1], [1, 1]], m)
    prim = lambda o: o[0][0] % 3 or o[0][1] % 3
    fib2 = {}
    for o in O2:
        if prim(o):
            ns = {norm(a, b, m) for a, b in o}
            ok1 = ok1 and len(ns) == 1
            n = ns.pop(); ok1 = ok1 and n not in fib2; fib2[n] = len(o)
    nprim = sum(1 for a in range(m) for b in range(m) if a % 3 or b % 3)
    ok1 = ok1 and sum(fib2.values()) == nprim
    for o in O1:
        if prim(o):
            ns = {norm(a, b, m) for a, b in o}
            ok1 = ok1 and len({min(n, (-n) % m) for n in ns}) == 1 and len(ns) == 2
    c = Counter(len(o) for o in O2)
    census[m] = sorted(c.items())
    ok1 = ok1 and len(O2) == m and all(c[4 * 3 ** (j - 1)] == 2 * 3 ** (j - 1) for j in range(1, k + 1))
P('norm-fiber', ok1, 'modulo 3^k, k = 1 to 5, every orbit of A^2 on primitive vectors is one whole fiber of the norm a^2 + ab - b^2, and every orbit of A one fiber of the norm up to sign (TONE and VOICE of Companion 89.4);',
  'the census of A^2 (length, count):', census, '| 3^k orbits at modulus 3^k: phi^2 has order 4 x 3^(k-1), the size of the norm-one group, and generates it')
# N2, N3
def kernel(N):
    h = pow(2, -1, N); w = cmath.exp(2j * math.pi / N)
    return np.array([[w ** ((j * j - j * k + h * k * k) % N) for k in range(N)] for j in range(N)]) / math.sqrt(N)
def weyl(N, q, p):
    w = cmath.exp(2j * math.pi / N); h = pow(2, -1, N)
    X = np.roll(np.eye(N), 1, axis=0); Z = np.diag([w ** j for j in range(N)])
    return w ** ((h * q * p) % N) * np.linalg.matrix_power(X, q % N) @ np.linalg.matrix_power(Z, p % N)
def order_mod(M, m):
    R = [[1, 0], [0, 1]]
    for n in range(1, 10000):
        R = [[(R[i][0] * M[0][j] + R[i][1] * M[1][j]) % m for j in range(2)] for i in range(2)]
        if R == [[1, 0], [0, 1]]: return n
rows = []; ok3 = True
for N in range(3, 20, 2):
    U = kernel(N); err_u = np.abs(U @ U.conj().T - np.eye(N)).max()
    err_c = max(np.abs(U @ weyl(N, q, p) @ U.conj().T - weyl(N, q + p, q + 2 * p)).max() for q in range(N) for p in range(N))
    cl = order_mod([[1, 1], [1, 2]], N); R = np.eye(N, dtype=complex); proj = None
    for n in range(1, 4 * cl + 1):
        R = R @ U
        ph = R[0, 0]
        if np.allclose(R, ph * np.eye(N), atol=1e-8): proj = (n, ph); break
    lit = proj[0] * next(r for r in range(1, 13) if abs(proj[1] ** r - 1) < 1e-8)
    rows.append((N, cl, proj[0], lit))
    ok3 = ok3 and err_u < 1e-12 and err_c < 1e-10 and proj[0] == cl
ok3 = ok3 and dict((r[0], r[3]) for r in rows)[11] == 20 and dict((r[0], r[3]) for r in rows)[19] == 36
P('explicit-kernel', ok3, 'the kernel U_N(j, k) = w^(j^2 - jk + k^2/2)/sqrt(N) is unitary and carries D(q, p) to D(q + p, q + 2p) on all N^2 labels for every odd N from 3 to 19; (N, order of A^2, projective period, literal period):', rows,
  '| projective period equals the classical order everywhere (Schur\'s lemma); the literal period carries the lift phase, -i at N = 11 and 19')
ok2 = True; specs = []
for N in (3, 9, 27):
    norb = len(orbits([[1, 1], [1, 2]], N))
    ev = np.linalg.eigvals(kernel(N)); gaps = min(abs(a - b) for a, b in itertools.combinations(ev, 2))
    ok2 = ok2 and norb == N and gaps > 1e-6; specs.append((N, norb, '%.3g' % gaps))
P('simple-spectrum', ok2, 'the operators commuting with U_N are spanned by the orbit sums of the Weyl operators, so the commutant has dimension equal to the number of orbits of A^2 on the N^2 labels; (N, orbits, smallest eigenvalue gap):', specs,
  '| N orbits at N = 3^k force sum m_i^2 = N with sum m_i = N, every multiplicity 1: the spectrum of the quantum cat map is simple at every power of 3, and the computed eigenvalues are distinct')
# N4
U3 = kernel(3); par = np.zeros((3, 3)); par[0, 0] = par[1, 2] = par[2, 1] = 1
O3 = orbits([[1, 1], [1, 2]], 3)
qv = sorted((len(o), sorted({(2 * (a * a + a * b - b * b)) % 3 for a, b in o})) for o in O3)
P('qutrit', np.allclose(U3 @ U3, par) and np.allclose(np.linalg.matrix_power(U3, 4), np.eye(3)) and qv == [(1, [0]), (4, [1]), (4, [2])],
  'on the qutrit, U_3^2 is the parity |j> -> |-j> and U_3^4 = I; modulo 3, A^2 has order 4 and the eight nonzero labels form two four-cycles, (1,0) -> (1,1) -> (2,0) -> (2,2) and (0,1) -> (1,2) -> (0,2) -> (2,1),',
  'on which Q = 2(a^2 + ab - b^2) is 2 and 1: the three orbits are the three values of Q, (length, values of Q)', qv)
# N5: KCBS on a qutrit
class Q5:
    __slots__ = ('a', 'b')
    def __init__(s, a=0, b=0): s.a = Fr(a); s.b = Fr(b)
    def __add__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a + o.a, s.b + o.b)
    def __sub__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a - o.a, s.b - o.b)
    def __mul__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    def inv(s): c = Q5(s.a + s.b, -s.b); n = (s * c).a; return Q5(c.a / n, c.b / n)
    def __truediv__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s * o.inv()
    def __eq__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s.a == o.a and s.b == o.b
phi = Q5(0, 1); sqrt5 = Q5(-1, 2)                                           # sqrt5 = 2 phi - 1
cos36 = phi / Q5(2)
c2 = cos36 / (Q5(1) + cos36)                                                 # cos^2 theta of the KCBS vectors
qmax = Q5(5) * c2
indep = max(sum(s) for s in itertools.product([0, 1], repeat=5) if all(not (s[i] and s[(i + 1) % 5]) for i in range(5)))
th = math.acos(math.sqrt(float(c2.a) + float(c2.b) * PHI))
vecs = [np.array([math.cos(th), math.sin(th) * math.cos(4 * math.pi * j / 5), math.sin(th) * math.sin(4 * math.pi * j / 5)]) for j in range(5)]
orth = all(abs(vecs[j] @ vecs[(j + 1) % 5]) < 1e-12 for j in range(5))
val = sum((v @ np.array([1.0, 0, 0])) ** 2 for v in vecs)
ok5 = qmax == sqrt5 and sqrt5 * sqrt5 == Q5(5) and qmax - Q5(2) == Q5(1) / (phi * phi * phi) and indep == 2 and orth and abs(val - 5 ** .5) < 1e-12 and sqrt5 == phi + Q5(1) / phi
P('kcbs-golden', ok5, 'the KCBS test of contextuality on one qutrit, five projectors on a pentagon of exclusivity: every noncontextual assignment gives at most %d, the independence number of the pentagon; the pentagram vectors, each orthogonal to the next, give the state (1, 0, 0) the sum %.12f = sqrt5,' % (indep, val),
  'exact in Q(phi) as 5 cos 36 / (1 + cos 36) = sqrt5 = phi + 1/phi, the Lovasz number of the pentagon; the quantum excess sqrt5 - 2 = phi^-3: contextuality of the nine-level layer\'s smallest part is measured by the golden ratio')
# N6
d = 9; w9 = cmath.exp(2j * math.pi / d)
def clifford(M):
    def D(a, b): return weyl(d, a, b)
    act = lambda s: ((M[0][0] * s[0] + M[0][1] * s[1]) % d, (M[1][0] * s[0] + M[1][1] * s[1]) % d)
    U = sum(D(*act((a, b))) @ D(a, b).conj().T for a in range(d) for b in range(d))
    return U / math.sqrt(abs(np.trace(U @ U.conj().T)) / d)
U2 = clifford([[1, 1], [1, 2]])
phi_b = np.zeros(d * d, complex)
for k in range(d): phi_b[k * d + k] = 1 / 3
rho = np.outer(phi_b, phi_b.conj()).reshape(d, d, d, d)
rA = np.einsum('ijkj->ik', rho); evA = np.linalg.eigvalsh(rA)
S = float(-sum(x * math.log2(x) for x in evA if x > 1e-15))
kept = np.allclose(np.kron(U2, U2.conj()) @ phi_b, phi_b)
P('bell-81', np.allclose(rA, np.eye(d) / d) and abs(S - math.log2(9)) < 1e-12 and kept,
  'two nine-level systems, 81 x 81 phase-space points: the state sum_k |k k>/3 has each reduced state I/9, entanglement entropy %.6f = log2 9 bits, the maximum,' % S,
  'and is kept by U (x) conj(U) for the unitary U of A^2: the law acting on one reading and its mirror on the other leaves the entangled pair unchanged, the first composite state of Omega42')
# N7
wq = cmath.exp(2j * math.pi / 3)
F3 = np.array([[wq ** (j * k) for k in range(3)] for j in range(3)]) / math.sqrt(3)
pp = np.abs(F3 @ (np.array([1, 1, 0]) / math.sqrt(2))) ** 2; pm = np.abs(F3 @ (np.array([1, -1, 0]) / math.sqrt(2))) ** 2
P('relative-phase', np.allclose(sorted(pp), sorted([2 / 3, 1 / 6, 1 / 6])) and np.allclose(sorted(pm), sorted([0, 1 / 2, 1 / 2])),
  '(|0> + |1>)/sqrt2 and (|0> - |1>)/sqrt2 give (1/2, 1/2, 0) in the position basis, and after the qutrit Fourier transform', [round(float(x), 6) for x in pp], 'against', [round(float(x), 6) for x in pm],
  ': two states with one probability list are told apart by their relative phase, which a quantum reading keeps')
# N8
ev2 = sorted(np.linalg.eigvals(np.array([[1.0, 1], [1, 2]])).real)
sym2 = sorted([ev2[0] ** 2, ev2[0] * ev2[1], ev2[1] ** 2])
P('two-exponents', abs(math.log(ev2[1]) - 2 * math.log(PHI)) < 1e-12 and abs(math.log(sym2[2]) - 4 * math.log(PHI)) < 1e-12 and abs(sym2[1] - 1) < 1e-12,
  'A^2 has eigenvalues phi^(+-2) on the phase space, Lyapunov exponent 2 ln phi = %.10f, and its symmetric square, the Lorentz boost of Part 223, has eigenvalues phi^4, 1, phi^-4, rapidity 4 ln phi = %.10f:' % (2 * math.log(PHI), 4 * math.log(PHI)),
  'one matrix, two representations, the quantum exponent the half of the relativistic one')
# N9
def coin(th): return np.array([[math.cos(th), math.sin(th)], [math.sin(th), -math.cos(th)]])
def fword(n):
    s = 'a'
    while len(s) < n: s = ''.join('ab' if c == 'a' else 'a' for c in s)
    return s[:n]
def msd_exponent(T, seq, ta, tb):
    L = 2 * T + 3; psi = np.zeros((L, 2), complex); psi[T + 1] = [1 / math.sqrt(2), 1j / math.sqrt(2)]
    x = np.arange(L) - (T + 1); m = []
    for t in range(T):
        psi = psi @ coin(ta if seq[t] == 'a' else tb).T
        new = np.zeros_like(psi); new[1:, 0] = psi[:-1, 0]; new[:-1, 1] = psi[1:, 1]; psi = new
        m.append(((np.abs(psi) ** 2).sum(1) * x * x).sum())
    t = np.arange(1, T + 1); return float(np.polyfit(np.log(t[T // 10:]), np.log(np.array(m)[T // 10:]), 1)[0])
if '--selftest' in sys.argv or '--full' in sys.argv:
    T = 4000
    e0 = msd_exponent(T, 'a' * T, math.pi / 4, math.pi / 4); e1 = msd_exponent(T, fword(T), math.pi / 4, math.pi / 3); e2 = msd_exponent(T, fword(T), math.pi / 4, 0.15)
    P('quantum-walk', abs(e0 - 2) < 0.01 and 1.7 < e1 < 1.9 and 1.6 < e2 < 1.8, 'a quantum walk on a line whose coin follows the Fibonacci word in time, coins pi/4 and pi/3, and pi/4 and 0.15, over 4000 steps:',
      'mean-square displacement exponents %.3f and %.3f against %.3f for the periodic walk: superdiffusive and sub-ballistic, the spreading of the law\'s word in quantum time (Romanelli: the walk\'s trace map)' % (e1, e2, e0))
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('QUANTUM FOUNDATIONS SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    print(__doc__); sys.exit(2)
