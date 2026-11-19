#!/usr/bin/env python3
"""Evidence run 02 -- computations (standard library + numpy). Run: python3 compute.py"""
import itertools, cmath, math
import numpy as np
N = 9
w = cmath.exp(2j * math.pi / N); inv2 = pow(2, -1, N)
def mmul(P, Q): return tuple(tuple(sum(P[i][t]*Q[t][j] for t in range(2)) % N for j in range(2)) for i in range(2))
def mpow(M, k):
    X = ((1, 0), (0, 1))
    for _ in range(k): X = mmul(X, M)
    return X
def order(M):
    k, X = 1, M
    while X != ((1, 0), (0, 1)): X = mmul(X, M); k += 1
    return k
I2 = ((1, 0), (0, 1)); NEG = ((N - 1, 0), (0, N - 1))
Tm = ((0, 1), (1, 1)); A = ((1, 1), (1, 2))          # A = Tm^2
print("PEER CHECK (i): Tm^2 =", mpow(Tm, 2), "= A:", mpow(Tm, 2) == A)
norm = lambda a, b: (a*a + a*b - b*b) % N
def act(M, v): return ((M[0][0]*v[0] + M[0][1]*v[1]) % N, (M[1][0]*v[0] + M[1][1]*v[1]) % N)
# T acts on states (a,b) -> (b, a+b): the row-vector convention matches Tm acting on column (a,b)
print("PEER CHECK (i): A preserves the norm a^2+ab-b^2 on all 81 states:",
      all(norm(*act(A, v)) == norm(*v) for v in itertools.product(range(N), repeat=2)),
      "| T negates it:", all(norm(*act(Tm, v)) == (-norm(*v)) % N for v in itertools.product(range(N), repeat=2)))
print("PEER CHECK (ii): order of A mod 9 = %d; order of T mod 9 = %d" % (order(A), order(Tm)))
print("PEER CHECK (iii): A has no element-power equal to T (A^k = T for some k):", any(mpow(A, k) == Tm for k in range(1, 13)))

# Quantum: Weyl displacements, Weil representation generators, complex conjugation K
X = np.roll(np.eye(N), 1, axis=0); Z = np.diag([w ** j for j in range(N)])
def D(p, q): return np.linalg.matrix_power(X, p % N) @ np.linalg.matrix_power(Z, q % N)
F = np.array([[w ** (j * k) for k in range(N)] for j in range(N)]) / math.sqrt(N)
Sh = np.diag([w ** ((inv2 * j * j) % N) for j in range(N)])
def proj_eq(P_, Q_):
    k = np.argmax(abs(Q_)); ph = P_.flat[k] / Q_.flat[k]
    return abs(abs(ph) - 1) < 1e-9 and np.allclose(P_, ph * Q_, atol=1e-9)
# find which matrices F and Sh implement (conjugation action on D)
def implemented(U):
    Ui = np.linalg.inv(U)
    for a, b, c, d in itertools.product(range(N), repeat=4):
        if (a*d - b*c) % N != 1: continue
        if proj_eq(U @ D(1, 0) @ Ui, D(a, c)) and proj_eq(U @ D(0, 1) @ Ui, D(b, d)):
            return ((a, b), (c, d))
gens = {'F': (implemented(F), F), 'S': (implemented(Sh), Sh)}
def unitary_for(M):
    for L in range(1, 10):
        for word in itertools.product('FS', repeat=L):
            P_ = I2; U = np.eye(N, dtype=complex)
            for g in word: P_ = mmul(P_, gens[g][0]); U = U @ gens[g][1]
            if P_ == M: return U, ''.join(word)
# complex conjugation K: K D(p,q) K = D(p,-q), i.e. R = diag(1,-1)
R = ((1, 0), (0, N - 1))
print("CHECK: K acts on displacements as R = diag(1,-1):", np.allclose(np.conj(D(1, 1)), D(1, -1)))
M = mmul(Tm, R)                                        # W implements M, V = W K implements M R = Tm R R = Tm
W, word = unitary_for(M)
def V_apply(psi): return W @ np.conj(psi)
def V_on_op(O): return W @ np.conj(O) @ np.linalg.inv(W)  # V O V^-1 for antiunitary V = W K
okT = all(proj_eq(V_on_op(D(p, q)), D(*act(Tm, (p, q)))) for p in range(N) for q in range(N))
print("E4: antiunitary V = W K (W from word %s) implements T on all 81 displacement operators: %s" % (word, okT))
# a unitary implementing T would have to implement a det -1 matrix: impossible, since unitary conjugation preserves the commutation form
detT = (Tm[0][0]*Tm[1][1] - Tm[0][1]*Tm[1][0]) % N
print("E4: det T mod 9 = %d (= -1): no unitary implements T, because unitary conjugation preserves the symplectic form" % detT)
V2 = W @ np.conj(W)                                    # V^2 = W K W K = W conj(W), a unitary
Ucat, _ = unitary_for(A)
print("E4: V^2 is unitary and equals the quantum cat map U(A) up to phase:", proj_eq(V2, Ucat))
P = np.zeros((N, N)); [P.__setitem__(((-j) % N, j), 1) for j in range(N)]
V12 = np.linalg.matrix_power(V2, 6); V24 = np.linalg.matrix_power(V2, 12)
print("E4: V^12 = parity up to phase: %s | V^24 = identity up to phase: %s | smallest n with V^n = identity up to phase: %d (odd powers are antiunitary)"
      % (proj_eq(V12, P), proj_eq(V24, np.eye(N)), 2 * next(n for n in range(1, 30) if proj_eq(np.linalg.matrix_power(V2, n), np.eye(N)))))
# The classical side of V: the 24-cycle on displacement labels
canon = [(2, 5)]
while True:
    nx = act(Tm, canon[-1])
    if nx == canon[0]: break
    canon.append(nx)
print("E4: V carries the displacement D(2,5) through the canonical orbit, length", len(canon),
      "| after 12 steps D(v) -> D(-v):", act(mpow(Tm, 12), (2, 5)) == ((-2) % N, (-5) % N))
# What kind of symmetry is V? V U V^-1 = U for U = V^2 (it commutes); for an antiunitary that commutes with U = exp(-iH),
# V H V^-1 = -H: the quasienergies of U = V^2 come in pairs (e, -e) about the phase fixed by V^2.
ev = np.angle(np.linalg.eigvals(V2)); ev = np.sort(np.mod(ev, 2 * math.pi))
ks = sorted(int(round(e / (2 * math.pi / 12))) % 12 for e in ev)
symmetric = sorted((-k) % 12 for k in ks) == ks
print("E4: V commutes with U = V^2: %s | the eigenphases of V^2 are closed under e -> -e: %s"
      % (np.allclose(W @ np.conj(V2) @ np.linalg.inv(W), V2), symmetric))
print("E4: V^2 needs no phase convention (V^2 = W conj(W) is unchanged when W is multiplied by a phase); its eigenvalues are exp(2 pi i k/12) for k =", ks,
      "-- every twelfth root of unity except k = 3, 6, 9, each once")
