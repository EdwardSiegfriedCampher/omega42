#!/usr/bin/env python3
"""Blind test 01, round 1 -- recomputes the statements on which the replies differ from each other or from the key."""
import itertools
from fractions import Fraction as Fr
V = list(itertools.product(range(9), repeat=2))
q = {x: (x[0] ** 2 + x[0] * x[1] - x[1] ** 2) % 9 for x in V}
print("B/C: u = a + 5b, v = b gives q = (u^2 + v^2)/9:", all(q[(a, b)] == ((a + 5 * b) ** 2 + b * b) % 9 for a, b in V))
print("D:   u = a + 5b, v = b gives q = (u^2 - v^2)/9:", all(q[(a, b)] == ((a + 5 * b) ** 2 - b * b) % 9 for a, b in V))
print("     (Z/9, x^2/9) is isometric to (Z/9, 4x^2/9) = SU(9)_1 via x -> 2x:", all((4 * x * x) % 9 == ((2 * x) ** 2) % 9 for x in range(9)),
      "and SU(9)_1 spins a(9-a)/18 = 4a^2/9:", all(Fr(a * (9 - a), 18) % 1 == Fr(4 * a * a % 9, 9) for a in range(9)))
print("B:   the Gaussian norm u^2 + v^2 reduced mod 9 is the same form (run 04 found Z[i]/9 to be the family's ring): True by the line above")
GL = [((a, b), (c, d)) for a, b, c, d in itertools.product(range(9), repeat=4) if ((a * d - b * c) % 3) != 0]
app = lambda M, x: ((M[0][0] * x[0] + M[0][1] * x[1]) % 9, (M[1][0] * x[0] + M[1][1] * x[1]) % 9)
mm = lambda X, Y: tuple(tuple(sum(X[i][t] * Y[t][j] for t in range(2)) % 9 for j in range(2)) for i in range(2))
def order(M):
    I = ((1, 0), (0, 1)); k, X = 1, M
    while X != I: X = mm(X, M); k += 1
    return k
A = [M for M in GL if all(q[app(M, x)] == (-q[x]) % 9 for x in V)]
print("B:   orders of the time-reversal symmetries (B claims they include 1, 2, 3, 6, 12):", sorted({order(M) for M in A}))
print("D:   number of unitary symmetries (D claims 8):", sum(1 for M in GL if all(q[app(M, x)] == q[x] for x in V)))
