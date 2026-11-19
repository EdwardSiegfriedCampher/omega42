#!/usr/bin/env python3
"""Evidence run 01 -- computations (standard library + numpy). Run: python3 compute.py"""
import itertools, cmath, math
import numpy as np

N = 9
def T(s, m=N): a, b = s; return (b, (a + b) % m)
def orbit(s, f, m=N):
    o = [s]; x = f(s, m)
    while x != s: o.append(x); x = f(x, m)
    return o
def orbits(f, m=N):
    seen, out = set(), []
    for s in itertools.product(range(m), repeat=2):
        if s not in seen:
            o = orbit(s, f, m); seen |= set(o); out.append(o)
    return out
norm = lambda s: (s[0]*s[0] + s[0]*s[1] - s[1]*s[1]) % N
canon = orbit((2, 5), T)
print("CANONICAL ORBIT (Voice C) first terms:", [s[0] for s in canon])

# E2: which orbit do consecutive Fibonacci and Lucas parastichy pairs lie on?
fib = [0, 1]; luc = [2, 1]
for _ in range(15): fib.append(fib[-1] + fib[-2]); luc.append(luc[-1] + luc[-2])
pairs = {'Fibonacci (21,34)': (21, 34), 'Fibonacci (34,55)': (34, 55), 'Fibonacci (55,89)': (55, 89), 'Fibonacci (89,144)': (89, 144),
         'Lucas (29,47)': (29, 47), 'Lucas (47,76)': (47, 76), 'double Fibonacci (68,110)': (68, 110)}
cset = set(canon)
for k, (a, b) in pairs.items():
    s = (a % N, b % N)
    print("E2 %-28s state mod 9 %s | norm %d | on canonical orbit: %s" % (k, s, norm(s), 'YES' if s in cset else 'NO'))

# E3: the Arnold cat map A = [[2,1],[1,1]] = T^2 on (Z/9)^2
def A(s, m=N): a, b = s; return ((2*a + b) % m, (a + b) % m)
def T2(s, m=N): return T(T(s, m), m)
# T^2(a,b) = (a+b, a+2b); A(a,b) = (2a+b, a+b): A equals T^2 up to swapping coordinates (conjugate by the swap J)
J = lambda s: (s[1], s[0])
conj = all(J(A(J(s))) == T2(s) for s in itertools.product(range(N), repeat=2))
print("E3 cat map A is conjugate to T^2 by the coordinate swap on all 81 states:", conj)
sizes = sorted(len(o) for o in orbits(A))
print("E3 cat map orbit sizes on (Z/9)^2:", sizes)
def mat_pow_order(M, m):
    I = ((1, 0), (0, 1)); X = M; k = 1
    mul = lambda P, Q: tuple(tuple(sum(P[i][t]*Q[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
    while X != tuple(tuple(v % m for v in r) for r in I): X = mul(X, M); k += 1
    return k, X, mul
def half_negation(M, m):
    k, _, mul = mat_pow_order(M, m)
    if k % 2: return k, False
    X = ((1, 0), (0, 1))
    for _ in range(k // 2): X = mul(X, M)
    return k, X == (((m - 1) % m, 0), (0, (m - 1) % m))
k9, neg9 = half_negation(((2, 1), (1, 1)), 9)
print("E3 order of A mod 9: %d | A^(order/2) = -I: %s" % (k9, neg9))
# Null control: A mod N, N = 2..30
rows = []
for m in range(2, 31):
    k, ng = half_negation(((2, 1), (1, 1)), m)
    rows.append((m, k, ng))
print("E3 NULL (A mod N): N:order:half-negation ->", ' '.join('%d:%d:%s' % (m, k, 'Y' if ng else 'n') for m, k, ng in rows))
print("E3 NULL share of N in 3..30 with half-period negation: %d/28" % sum(1 for m, k, ng in rows if m >= 3 and ng))

# E3 quantum: Weil representation of SL(2, Z/9) (N odd: a genuine representation). Build U(A) from generators.
w = cmath.exp(2j * math.pi / N); inv2 = pow(2, -1, N)
F = np.array([[w ** (j * k) for k in range(N)] for j in range(N)]) / math.sqrt(N)        # Fourier: image of S = [[0,-1],[1,0]] up to phase
D = np.diag([w ** ((inv2 * j * j) % N) for j in range(N)])                              # image of the shear [[1,0],[1,1]] (lower) up to phase
# A = [[2,1],[1,1]] factored as L * S * L^-? -- verify by matrices, then use a direct product of generators found by search
G = {'S': (((0, N - 1), (1, 0)), F), 'L': (((1, 0), (1, 1)), D)}
def mmul(P, Q): return tuple(tuple(sum(P[i][t]*Q[t][j] for t in range(2)) % N for j in range(2)) for i in range(2))
target = ((2, 1), (1, 1)); word = None
for L in range(1, 9):
    for w_ in itertools.product('SL', repeat=L):
        M = ((1, 0), (0, 1))
        for g in w_: M = mmul(M, G[g][0])
        if M == target: word = w_; break
    if word: break
U = np.eye(N, dtype=complex)
for g in word: U = U @ G[g][1]
def proj_eq(X, Y):  # X equals Y up to a global phase
    k = np.argmax(abs(Y)); ph = X.flat[k] / Y.flat[k]
    return abs(abs(ph) - 1) < 1e-9 and np.allclose(X, ph * Y, atol=1e-9)
P = np.zeros((N, N)); [P.__setitem__(((-j) % N, j), 1) for j in range(N)]                # parity |j> -> |-j>
U6 = np.linalg.matrix_power(U, 6); U12 = np.linalg.matrix_power(U, 12)
first = next(n for n in range(1, 50) if proj_eq(np.linalg.matrix_power(U, n), np.eye(N)))
print("E3 quantum cat map at N = 9 (Weil representation, word %s): U^6 = parity up to phase: %s | U^12 = identity up to phase: %s | quantum period: %d"
      % (''.join(word), proj_eq(U6, P), proj_eq(U12, np.eye(N)), first))

# Check that U really implements a linear symplectic map: U D(v) U^-1 = phase * D(M v) for every v in (Z/9)^2.
X = np.roll(np.eye(N), 1, axis=0); Zm = np.diag([w ** j for j in range(N)])
def Dop(p, q): return np.linalg.matrix_power(X, p % N) @ np.linalg.matrix_power(Zm, q % N)
Uinv = np.linalg.inv(U)
found = []
for M in itertools.product(range(N), repeat=4):
    a, b, c, d = M
    if (a * d - b * c) % N != 1: continue
    if all(proj_eq(U @ Dop(p, q) @ Uinv, Dop(a*p + b*q, c*p + d*q)) for p, q in [(1, 0), (0, 1)]):
        found.append(((a, b), (c, d)))
Mq = found[0]
ok_all = all(proj_eq(U @ Dop(p, q) @ Uinv, Dop(Mq[0][0]*p + Mq[0][1]*q, Mq[1][0]*p + Mq[1][1]*q)) for p in range(N) for q in range(N))
def order(M):
    I = ((1, 0), (0, 1)); Y = M; k = 1
    while Y != I: Y = mmul(Y, M); k += 1
    return k
print("E3 check: U acts on the Weyl displacements as the matrix %s (det 1 mod 9), on all 81 displacements: %s | its order mod 9: %d | trace %d (A has trace 3)"
      % (Mq, ok_all, order(Mq), (Mq[0][0] + Mq[1][1]) % N))
