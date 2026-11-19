#!/usr/bin/env python3
"""everett.py -- the family read as quantum structure: what of Everett's and Deutsch's multiverse it carries, computed
(Companion Part 135; Core MATH-18; D-013).

Two exact readings of the 81 states, and what each carries:
  (A) THE PHASE SPACE OF ONE NINE-LEVEL SYSTEM. The 81 pairs (p, q) label the 81 displacement (Weyl) operators
      D(p, q) = w^(5pq) X^p Z^q on C^9, w = exp(2 pi i / 9), 5 = 1/2 mod 9; they form the discrete phase space of Wootters
      and Gross. A matrix of determinant 1 is carried by a unitary U with U D(v) U* = D(Mv) (a Clifford unitary); a matrix
      of determinant -1 by an antiunitary. The law's matrix A = [[0, 1], [1, 1]] has determinant -1, so T is an antiunitary
      (A = (AJ)J, J = diag(1, -1), J being complex conjugation); T^2, matrix [[1, 1], [1, 2]], is a Clifford unitary.
      Computed: (1) the covariance for all 81 points; (2) the projective order of the unitary for T^2, 12; (3) its sixth power,
      the mirror T^12 = -I, is the parity operator P|x> = |-x>; (4) T itself as V K, K complex conjugation; (5) the law moves
      the discrete Wigner function of every state as a permutation of the 81 points, so it creates no negativity: it lies in
      the stabilizer fragment, which a single classical history simulates (Gottesman-Knill; Gross 2006 for odd dimension);
      a state with negativity, W(0, 0) = -1/9, keeps exactly its negativity under the law.
  (B) TWO NINE-LEVEL SYSTEMS, |a> (x) |b>. T is the permutation |a, b> -> |b, a + b>, a unitary on C^81, and T = SUM . SWAP,
      SUM|a, b> = |a, a + b> being the von Neumann measurement interaction. Computed: (6) from a system in superposition and a
      pointer at 0, T^2 writes the record: (1/3) sum |a, a>, maximally entangled (Schmidt rank 9, entropy log 9 = 2 trits),
      each branch with the pointer reading the system (Everett's relative state); (7) the branch weights forced by symmetry,
      1/9 each (the structure of Deutsch's 1999 argument); (8) the entanglement along the period, in trits:
      0 0 2 2 1 1 2 2 1 1 2 2 0, repeated, so the record is erased at the Antipode and the branches recombine: in a finite
      reversible law branching recurs; (9) the drop to one trit falls exactly where a Fibonacci number lies in the Crown;
      (10) the tasks the law alone can perform, (a, b) -> (c, d) in one orbit: 1793 of 6561 (Deutsch and Marletto's
      possible tasks, for this substrate).
Exact where integers; the unitary checks to 1e-9. Standard library only.
"""
import cmath, math
d = 9; w = cmath.exp(2j * math.pi / d)
def mat(f): return [[f(i, j) for j in range(d)] for i in range(d)]
def mul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(d)) for j in range(d)] for i in range(d)]
def dag(A): return [[A[j][i].conjugate() for j in range(d)] for i in range(d)]
def conj(A): return [[A[i][j].conjugate() for j in range(d)] for i in range(d)]
def add(A, B): return [[A[i][j] + B[i][j] for j in range(d)] for i in range(d)]
def scal(c, A): return [[c * A[i][j] for j in range(d)] for i in range(d)]
I = mat(lambda i, j: 1 + 0j if i == j else 0j)
X = mat(lambda i, j: 1 + 0j if i == (j + 1) % d else 0j)
Z = mat(lambda i, j: w ** i if i == j else 0j)
Par = mat(lambda i, j: 1 + 0j if i == (-j) % d else 0j)
def mpow(A, n):
    R = I
    for _ in range(n): R = mul(R, A)
    return R
Xp = [mpow(X, k) for k in range(d)]; Zp = [mpow(Z, k) for k in range(d)]
def D(p, q): return scal(w ** ((5 * p * q) % d), mul(Xp[p % d], Zp[q % d]))
DD = {(p, q): D(p, q) for p in range(d) for q in range(d)}
def act(M, v): return ((M[0][0] * v[0] + M[0][1] * v[1]) % d, (M[1][0] * v[0] + M[1][1] * v[1]) % d)
def dist(A, B): return max(abs(A[i][j] - B[i][j]) for i in range(d) for j in range(d))
def prop(A, B):
    """A = c B for a scalar c? returns (True, c) or (False, None)"""
    i, j = max(((i, j) for i in range(d) for j in range(d)), key=lambda t: abs(B[t[0]][t[1]]))
    c = A[i][j] / B[i][j]
    return (dist(A, scal(c, B)) < 1e-9, c)
SEED = mat(lambda i, j: complex(math.sin(1 + 3 * i + 7 * j), math.cos(2 + 5 * i - j)))
def clifford(M):
    """the unitary carrying D(v) to D(Mv), by the twirl sum_v D(Mv) R D(v)*; normalized"""
    U = mat(lambda i, j: 0j)
    for v, Dv in DD.items(): U = add(U, mul(mul(DD[act(M, v)], SEED), dag(Dv)))
    n = math.sqrt(sum(abs(U[i][0]) ** 2 for i in range(d)))
    return scal(1 / n, U)
A = [[0, 1], [1, 1]]; A2 = [[1, 1], [1, 2]]; AJ = [[0, -1], [1, -1]]
def section_A():
    L = ['(A) THE 81 STATES AS THE PHASE SPACE OF ONE NINE-LEVEL SYSTEM (D(p, q) = w^(5pq) X^p Z^q on C^9)']
    U = clifford(A2)
    un = dist(mul(U, dag(U)), I)
    cov = max(dist(mul(mul(U, DD[v]), dag(U)), DD[act(A2, v)]) for v in DD)
    L.append('  (1) T^2, matrix [[1, 1], [1, 2]], determinant 1: a Clifford unitary U, |UU* - I| = %.1e; U D(v) U* = D(T^2 v) for all 81 points, max error %.1e' % (un, cov))
    k = next(k for k in range(1, 100) if prop(mpow(U, k), I)[0])
    L.append('  (2) the projective order of U (smallest k with U^k a multiple of I): %d, the order of T^2, half the 24-cycle' % k)
    ok6, _ = prop(mpow(U, 6), Par)
    L.append('  (3) U^6, the mirror T^12 = -I, is the parity operator P|x> = |-x>: %s' % ('YES (up to a phase)' if ok6 else 'NO'))
    V = clifford(AJ)
    cov2 = max(dist(mul(mul(V, conj(DD[v])), dag(V)), DD[act(A, v)]) for v in DD)
    L.append('  (4) T, determinant -1, is antiunitary: with K complex conjugation (K D(p, q) K = D(p, -q)) and V the Clifford unitary of')
    L.append('      [[0, -1], [1, -1]], V K D(v) K V* = D(T v) for all 81 points, max error %.1e; the law is a time reversal, its square a unitary step' % cov2)
    Av = {v: mul(mul(DD[v], Par), dag(DD[v])) for v in DD}
    psi = [0j] * d; psi[1] = 1 / math.sqrt(2); psi[8] = -1 / math.sqrt(2)
    def W(state):
        return {v: sum(state[i].conjugate() * sum(Av[v][i][j] * state[j] for j in range(d)) for i in range(d)).real / d for v in DD}
    W0 = W(psi); Upsi = [sum(U[i][j] * psi[j] for j in range(d)) for i in range(d)]; W1 = W(Upsi)
    perm = max(abs(W1[act(A2, v)] - W0[v]) for v in DD)
    neg0 = sum(abs(x) for x in W0.values()); neg1 = sum(abs(x) for x in W1.values())
    stab = [0j] * d; stab[0] = 1 + 0j; Ws = W(stab)
    L.append('  (5) the discrete Wigner function W(v) = Tr(rho A(v)) / 9, A(v) = D(v) P D(v)*, moves as a permutation of the 81 points:')
    L.append('      W of U psi at T^2 v equals W of psi at v, max error %.1e; for psi = (|1> - |8>)/sqrt 2, W(0, 0) = %.4f = -1/9, and the' % (perm, W0[(0, 0)]))
    L.append('      sum of |W| is %.4f before and %.4f after: the law creates no negativity; |0>, a stabilizer state, has min W = %.4f >= 0' % (neg0, neg1, min(Ws.values())))
    return L
def F(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def T(v): return (v[1], (v[0] + v[1]) % d)
def Tk(v, k):
    for _ in range(k): v = T(v)
    return v
def size(H, axis):
    return sum(1 for h in H if h[1 - axis] == 0)
def section_B():
    L = ['(B) TWO NINE-LEVEL SYSTEMS |a> (x) |b>: T is the permutation |a, b> -> |b, a + b> = SUM . SWAP']
    ok = all(T((a, b)) == ((b), (b + a) % d) for a in range(d) for b in range(d))
    sumswap = all(T((a, b)) == (lambda s: (s[0], (s[0] + s[1]) % d))((b, a)) for a in range(d) for b in range(d))
    L.append('  T = SUM . SWAP, SUM|a, b> = |a, a + b> (the von Neumann measurement interaction): %s' % ('YES' if ok and sumswap else 'NO'))
    H2 = sorted(set(Tk((a, 0), 2) for a in range(d)))
    L.append('  (6) system (1/3) sum_a |a>, pointer |0>; after T^2 the support is %s: (1/3) sum |a, a>, every branch' % ('{(a, a)}' if H2 == [(a, a) for a in range(d)] else H2))
    L.append('      the pointer reading the system; Schmidt rank 9, entropy log 9 = 2 trits (Everett\'s relative state of the system, given pointer b, is |b>)')
    shift = set(((a + 1) % d, (b + 1) % d) for a, b in H2) == set(H2)
    L.append('  (7) X (x) X shifts every branch to the next and leaves the state unchanged; a weighting invariant under a transitive')
    L.append('      permutation of the branches is uniform: 1/9 each, the Born weights |1/3|^2, forced by the symmetry alone (support invariant: %s)' % ('YES' if shift else 'NO'))
    ent = []
    for k in range(25):
        H = set(Tk((a, 0), k) for a in range(d))
        s = math.log(len(H) / (size(H, 0) * size(H, 1)), 3)
        ent.append(round(s))
        rho = [[sum(1 for y in range(d) if (x, y) in H and (x2, y) in H) / len(H) for x2 in range(d)] for x in range(d)]
        pur = sum(rho[i][j] * rho[j][i] for i in range(d) for j in range(d))
        assert abs(pur - 3 ** (-round(s))) < 1e-12, (k, pur, s)
    L.append('  (8) the entanglement of T^k((1/3) sum |a, 0>), k = 0 to 24, in trits: ' + ' '.join(map(str, ent)) + ' (each checked by the purity of the reduced state, 3^-S)')
    L.append('      zero again at k = 12, the Antipode (the record erased; the state there is the starting state, as it is parity-symmetric) and at 24')
    one = [k for k in range(25) if ent[k] == 1]
    crown = [k for k in range(25) if (F(k) % d in (3, 6)) or (F(k - 1) % d in (3, 6) if k else False)]
    L.append('  (9) one trit at k = %s; a Fibonacci number of the pair (F(k-1), F(k)) lies in the Crown {3, 6} at k = %s: %s' % (one, crown, 'THE SAME' if one == crown else 'DIFFERENT'))
    orbits = []; seen = set()
    for a in range(d):
        for b in range(d):
            if (a, b) in seen: continue
            o = []; v = (a, b)
            while v not in o: o.append(v); v = T(v)
            seen |= set(o); orbits.append(len(o))
    L.append('  (10) orbits %s; the tasks (a, b) -> (c, d) the law alone performs, in one orbit: %d of %d' % (sorted(orbits), sum(n * n for n in orbits), 81 * 81))
    return L
if __name__ == '__main__':
    print('\n'.join(section_A() + section_B()))
