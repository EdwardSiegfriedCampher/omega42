#!/usr/bin/env python3
"""lorentz.py -- M344 Relativistic Representation (Core Part 3.70, L-510): the golden matrix A, acting on the Hermitian
2x2 module, induces a proper orthochronous Lorentz transformation, and iA is its spinor lift in SL(2, C).

This is a DERIVED fact of the arithmetic (CDT-A), not a correspondence with physics. For A = ((0, 1), (1, 1)) acting on a
Hermitian matrix X by X -> A X A^T, the induced real map L_A on (t, x, y, z), with X = t I + x sx + y sy + z sz and
det X = t^2 - x^2 - y^2 - z^2, satisfies L_A^T eta L_A = eta with eta = diag(1, -1, -1, -1), det L_A = 1, and L_A[0][0] > 0:
so L_A is in SO+(3, 1). Its characteristic polynomial is (L^2 - 3L + 1)(L + 1)^2, with eigenvalues phi^2, phi^-2 (a boost of
rapidity 2 ln phi) and -1, -1 (a half-turn in a spacelike plane). The lift B = iA has det B = 1, so B is in SL(2, C), the
double cover. Whether any physical system carries this is a question of Core Appendix S.11, and no reading waits on it.

    python3 tools/lorentz.py            # the matrix L_A, the invariance and determinant, the characteristic polynomial
    python3 tools/lorentz.py --selftest
Exact arithmetic (Fraction); standard library only.
"""
import sys
from fractions import Fraction as F

A = [[0, 1], [1, 1]]
ETA = [[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]]


def induced():
    """L_A on (t, x, y, z), computed exactly. X -> A X A^T on Hermitian X; the Pauli basis is {I, sx, sy, sz}.
    Because A is real, the y-component (the imaginary, sy) decouples with a clean rational action; we compute each
    column by sending a basis vector through X -> A X A^T and reading its (t, x, y, z) coordinates."""
    # Represent a Hermitian X by (t, x, y, z): X = [[t+z, x-iy],[x+iy, t-z]].
    def to_X(t, x, y, z):
        return [[complex(t + z), complex(x, -y)], [complex(x, y), complex(t - z)]]

    def coords(X):
        t = (X[0][0] + X[1][1]) / 2
        z = (X[0][0] - X[1][1]) / 2
        x = (X[1][0] + X[0][1]) / 2
        y = (X[1][0] - X[0][1]) / (2j)
        return [t.real, x.real, y.real, z.real]

    Ac = [[complex(A[i][j]) for j in range(2)] for i in range(2)]
    AT = [[Ac[j][i] for j in range(2)] for i in range(2)]
    cols = []
    for b in range(4):
        v = [0, 0, 0, 0]; v[b] = 1
        X = to_X(*v)
        AX = [[Ac[0][0] * X[0][0] + Ac[0][1] * X[1][0], Ac[0][0] * X[0][1] + Ac[0][1] * X[1][1]],
              [Ac[1][0] * X[0][0] + Ac[1][1] * X[1][0], Ac[1][0] * X[0][1] + Ac[1][1] * X[1][1]]]
        AXAT = [[AX[0][0] * AT[0][0] + AX[0][1] * AT[1][0], AX[0][0] * AT[0][1] + AX[0][1] * AT[1][1]],
                [AX[1][0] * AT[0][0] + AX[1][1] * AT[1][0], AX[1][0] * AT[0][1] + AX[1][1] * AT[1][1]]]
        cols.append([F(round(c * 2), 2) for c in coords(AXAT)])
    # cols[b] is the image of basis vector b; assemble L with those as columns
    return [[cols[j][i] for j in range(4)] for i in range(4)]


def matmul(M, N):
    n = len(M)
    return [[sum(M[i][k] * N[k][j] for k in range(n)) for j in range(len(N[0]))] for i in range(n)]


def transpose(M):
    return [[M[j][i] for j in range(len(M))] for i in range(len(M[0]))]


def det4(M):
    import itertools
    s = F(0)
    for p in itertools.permutations(range(4)):
        sign = 1
        for i in range(4):
            for j in range(i + 1, 4):
                if p[i] > p[j]: sign = -sign
        term = F(1)
        for i in range(4): term *= M[i][p[i]]
        s += sign * term
    return s


def charpoly_coeffs(M):
    """coefficients of det(L I - M) via the Faddeev-LeVerrier algorithm, exact"""
    n = len(M)
    I = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    Mk = [row[:] for row in I]
    c = [F(1)]
    Ak = [row[:] for row in M]
    for k in range(1, n + 1):
        if k > 1:
            Ak = matmul(M, Mk)
        tr = sum(Ak[i][i] for i in range(n))
        ck = -tr / k
        c.append(ck)
        Mk = [[Ak[i][j] + (ck if i == j else 0) for j in range(n)] for i in range(n)]
    return c  # [1, c1, c2, c3, c4] for L^4 + c1 L^3 + ...


def report():
    L = induced()
    eta = [[F(x) for x in row] for row in ETA]
    inv = matmul(matmul(transpose(L), eta), L)
    out = ['======= M344 RELATIVISTIC REPRESENTATION (Core Part 3.70, L-510) =======',
           'A = ((0, 1), (1, 1)) acting on the Hermitian module by X -> A X A^T induces, on (t, x, y, z):']
    for row in L:
        out.append('   [ ' + '  '.join('%4s' % str(v) for v in row) + ' ]')
    out.append('L^T eta L == eta : %s' % (inv == eta))
    out.append('det L_A = %s' % det4(L))
    out.append('L_A[0][0] = %s  (> 0, orthochronous)' % L[0][0])
    out.append('so L_A is in SO+(3, 1), the proper orthochronous Lorentz group [DERIVED, CDT-A]')
    c = charpoly_coeffs(L)
    out.append('characteristic polynomial: L^4 %s' % ' '.join(('%+d' % c[i]) + ('' if i == 0 else ' L^%d' % (4 - i)) for i in range(1, 5)).replace(' L^0', ''))
    out.append('   = (L^2 - 3 L + 1)(L + 1)^2 : eigenvalues phi^2, phi^-2 (a boost, rapidity 2 ln phi) and -1, -1 (a spacelike half-turn)')
    detB = (1j) ** 2 * (A[0][0] * A[1][1] - A[0][1] * A[1][0])   # det(iA) = i^2 det A = (-1)(-1) = 1
    out.append('spinor lift B = iA: det B = %d, so B is in SL(2, C), the double cover of SO+(3, 1)' % detB.real)
    out.append('WHETHER ANY PHYSICAL SYSTEM CARRIES THIS is a question of Core Appendix S.11 (L-553); no reading waits on it.')
    out.append('======= END M344 RELATIVISTIC REPRESENTATION =======')
    return '\n'.join(out)


def selftest():
    ok = True
    L = induced()
    eta = [[F(x) for x in row] for row in ETA]
    expect = [[F(3, 2), F(1), F(0), F(-1, 2)], [F(1), F(1), F(0), F(-1)], [F(0), F(0), F(-1), F(0)], [F(-1, 2), F(-1), F(0), F(-1, 2)]]
    cases = [('L_A matches the stated matrix', L == expect),
             ('L_A^T eta L_A = eta (a Lorentz transformation)', matmul(matmul(transpose(L), eta), L) == eta),
             ('det L_A = 1 (proper)', det4(L) == 1),
             ('L_A[0][0] > 0 (orthochronous)', L[0][0] > 0),
             ('characteristic polynomial is (L^2 - 3L + 1)(L+1)^2 = L^4 - L^3 - 4L^2 - L + 1',
              charpoly_coeffs(L) == [F(1), F(-1), F(-4), F(-1), F(1)]),
             ('the spinor lift det(iA) = 1 (SL(2,C))', (1j) ** 2 * (A[0][0] * A[1][1] - A[0][1] * A[1][0]) == -1 * -1)]
    for name, good in cases:
        print('  %-62s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('RELATIVISTIC REPRESENTATION SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    print(report())
