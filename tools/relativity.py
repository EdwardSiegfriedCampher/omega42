#!/usr/bin/env python3
"""relativity.py -- the law in special relativity: the boost of A^2, its Fibonacci-Lucas family, the Doppler factor phi^4,
the anti-isometry of A, the form Q as the boost's axis, the three kinds of Lorentz transformation in <A^2, B>, the
Thomas-Wigner rotation of two golden boosts, modular aliasing, the 3 + 1 embedding, and the boosts and rotations of the golden ring
(Companion Parts 223 and 224; F217; APE-479).

  R1 mass-shell        X = [[t + x, y], [y, t - x]] -> M X M^T with M = A^2 keeps t^2 - x^2 - y^2; the induced matrix
                       t' = (7t - 3x + 6y)/2, x' = (-3t + 3x - 2y)/2, y' = 3t - x + 3y is proper and orthochronous
  R2 golden-boost      gamma = 7/2, gamma^2 beta^2 = 45/4, beta = 3 sqrt5 / 7, rapidity 4 ln phi; the Doppler factors are phi^4 and phi^-4
  R3 lucas-boosts      the n-th power: gamma_n = L_(4n)/2, gamma_n beta_n = sqrt5 F_(4n)/2, n = 1..12; composition is Einstein's addition
  R4 half-boost        A itself is an improper orthochronous Lorentz transformation, gamma = 3/2, det -1: the half golden boost with a reflection
  R5 q-axis            the vector fixed by the boost of A^2 is the law's own form Q, spacelike, and A reverses it: Q is the axis of the golden boost
  R6 three-kinds       in <A^2, B>: A^2 a boost (trace 3), B a null rotation fixing a light ray (trace 2), and a word of trace 0,
                       a half turn about a timelike axis: every kind of Lorentz transformation in Omega42's group
  R7 wigner            two golden boosts at the angle arccos(3/5) compose to a boost and a Thomas-Wigner rotation of exactly
                       arccos(4/5), the 3-4-5 angle, in agreement with the Thomas-Wigner formula
  R8 aliasing          on integer states modulo 9 the boost repeats after 6 steps, A^12 = -I, while gamma_n grows without bound:
                       the residue keeps n mod 6 and the quotient keeps the rest
  R9 spinor            the 2 x 2 law is the spinor transformation and the 3 x 3 boost its symmetric square, eigenvalues phi^4, 1, phi^-4
  R11 golden-ring-boost  over Z[phi] the half golden boost diag(phi, phi - 1) is proper: gamma = 3/2, its square the golden boost
  R12 golden-rotation  [[phi, -1], [1, 0]] in SL2(Z[phi]) is a Lorentz rotation of order 5 by 72 degrees: the crystallographic
                       restriction of SL2(Z) (rotations of order 2 and 3) broken by the law's ring
  R10 three-plus-one   on Hermitian X = [[t + z, x - iy], [x + iy, t - z]], X -> M X M^T keeps t^2 - x^2 - y^2 - z^2 and fixes y:
                       the golden boost in 3 + 1 dimensions through SL2(C)

    python3 tools/relativity.py --selftest
    python3 tools/relativity.py --boost n        gamma, gamma beta, beta and the Doppler factor of the n-th golden boost
Standard library only; exact in Fraction arithmetic except the floating-point comparison in R7 and the printed decimals.
"""
import sys, math, itertools
from fractions import Fraction as F
PHI = (1 + 5 ** .5) / 2
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
def luc(n): return fib(n - 1) + fib(n + 1) if n > 0 else 2
def mm(X, Y): return [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]
def tr(X): return [list(r) for r in zip(*X)]
A = [[0, 1], [1, 1]]; M = mm(A, A); B = [[1, 0], [3, 1]]
def lorentz(G):
    """the 3 x 3 matrix of X -> G X G^T on (t, x, y), X = [[t + x, y], [y, t - x]]"""
    cols = []
    for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        t, x, y = map(F, v); X = [[t + x, y], [y, t - x]]
        Y = mm(mm(G, X), tr(G)); cols.append(((Y[0][0] + Y[1][1]) / 2, (Y[0][0] - Y[1][1]) / 2, Y[0][1]))
    return [[cols[j][i] for j in range(3)] for i in range(3)]
ETA = [[1, 0, 0], [0, -1, 0], [0, 0, -1]]
def det3(L): return (L[0][0] * (L[1][1] * L[2][2] - L[1][2] * L[2][1]) - L[0][1] * (L[1][0] * L[2][2] - L[1][2] * L[2][0]) + L[0][2] * (L[1][0] * L[2][1] - L[1][1] * L[2][0]))
def mpow(X, n):
    R = [[int(i == j) for j in range(len(X))] for i in range(len(X))]
    for _ in range(n): R = mm(R, X)
    return R
# R1
L = lorentz(M)
iso = mm(mm(tr(L), ETA), L) == ETA
formula = L == [[F(7, 2), F(-3, 2), F(3)], [F(-3, 2), F(3, 2), F(-1)], [F(3), F(-1), F(3)]]
P('mass-shell', iso and formula and det3(L) == 1 and L[0][0] >= 1,
  'X -> M X M^T with M = A^2 keeps t^2 - x^2 - y^2; its matrix on (t, x, y) is', [[str(v) for v in r] for r in L],
  ', that is t\' = (7t - 3x + 6y)/2, x\' = (-3t + 3x - 2y)/2, y\' = 3t - x + 3y (the formulas of F217, confirmed); L^T eta L = eta, det L = 1, L_00 = 7/2 >= 1: proper and orthochronous')
# R2: the boost's gamma is the energy of a particle at rest after it: (L e_t)_t = 7/2; |gamma beta|^2 = (L e_t)_x^2 + (L e_t)_y^2
g = L[0][0]; gb2 = L[1][0] ** 2 + L[2][0] ** 2
dop_hi = (7 + 3 * 5 ** .5) / 2
P('golden-boost', g == F(7, 2) and gb2 == F(45, 4) and g * g - gb2 == 1 and abs(dop_hi - PHI ** 4) < 1e-12 and abs(math.acosh(7 / 2) - 4 * math.log(PHI)) < 1e-12,
  'gamma = 7/2 and gamma^2 beta^2 = 45/4 exactly, so beta^2 = 45/49, beta = 3 sqrt5 / 7 = %.6f, rapidity eta = arccosh(7/2) = 4 ln phi = %.6f;' % (3 * 5 ** .5 / 7, 4 * math.log(PHI)),
  'the Doppler factors e^(+-eta) = gamma (1 +- beta) are (7 +- 3 sqrt5)/2 = phi^4 and phi^-4, the eigenvalues of A^4: a light signal is shifted by the law raised to the fourth power')
# R3
okL = True; rows = []
for n in range(1, 13):
    Ln = lorentz(mpow(M, n)); gn = Ln[0][0]; gbn2 = Ln[1][0] ** 2 + Ln[2][0] ** 2
    okL = okL and gn == F(luc(4 * n), 2) and gbn2 == F(5 * fib(4 * n) ** 2, 4) and gn * gn - gbn2 == 1
    if n <= 3: rows.append('n = %d: gamma %s, (gamma beta)^2 %s' % (n, gn, gbn2))
okC = True
for m_, n in itertools.product(range(1, 7), repeat=2):
    gm, gn, gmn = F(luc(4 * m_), 2), F(luc(4 * n), 2), F(luc(4 * (m_ + n)), 2)
    okC = okC and gmn == gm * gn + F(5 * fib(4 * m_) * fib(4 * n), 4)   # cosh(a + b) = cosh a cosh b + sinh a sinh b, sinh = sqrt5 F / 2
P('lucas-boosts', okL and okC, 'the n-th power of the golden boost has gamma_n = L_(4n)/2 and gamma_n beta_n = sqrt5 F_(4n)/2 for n = 1 to 12:', rows,
  '...; and gamma_(m+n) = gamma_m gamma_n + gamma_m beta_m gamma_n beta_n for m, n = 1 to 6, the composition law that is Einstein\'s velocity addition beta_(m+n) = (beta_m + beta_n)/(1 + beta_m beta_n): rapidity adds as the exponent of the law')
# R4: A itself, det A = -1: X -> A X A^T keeps the form, and det L(A) = det(A)^3 = -1: an improper Lorentz transformation
LA = lorentz(A)
P('half-boost', mm(mm(tr(LA), ETA), LA) == ETA and det3(LA) == -1 and LA[0][0] == F(3, 2),
  'the law A itself, of determinant -1, keeps t^2 - x^2 - y^2 under X -> A X A^T with det L(A) = -1 and L(A)_00 = 3/2 = L_2/2:',
  'an improper orthochronous Lorentz transformation, the half golden boost of rapidity 2 ln phi joined to a reflection; its square is the golden boost of R1')
# R5: Q(a, b) = b^2 - ab - a^2 = s^T Fq s with Fq = [[-1, -1/2], [-1/2, 1]]; A^T Fq A = -Fq, so M Fq^-1 M^T = Fq^-1: the vector of Fq^-1
Fq = [[F(-1), F(-1, 2)], [F(-1, 2), F(1)]]
dq = Fq[0][0] * Fq[1][1] - Fq[0][1] * Fq[1][0]
Fi = [[Fq[1][1] / dq, -Fq[0][1] / dq], [-Fq[1][0] / dq, Fq[0][0] / dq]]
v = ((Fi[0][0] + Fi[1][1]) / 2, (Fi[0][0] - Fi[1][1]) / 2, Fi[0][1])
Lv = tuple(sum(L[i][j] * v[j] for j in range(3)) for i in range(3))
norm = v[0] ** 2 - v[1] ** 2 - v[2] ** 2
LAv = tuple(sum(LA[i][j] * v[j] for j in range(3)) for i in range(3))
P('q-axis', mm(mm(tr(A), Fq), A) == [[-x for x in r] for r in Fq] and Lv == v and LAv == tuple(-x for x in v) and norm < 0,
  'the law\'s form Q, matrix [[-1, -1/2], [-1/2, 1]], is fixed by the golden boost: its Minkowski vector', tuple(str(x) for x in v), 'is spacelike (norm %s), L(A^2) v = v and L(A) v = -v;' % norm,
  'the golden boost acts in the plane orthogonal to Q, and Q(As) = -Q(s) is the reflection of that axis by A: the invariant of Omega42 is the axis of its Lorentz transformation')
# R6
def lt_kind(G):
    t_ = G[0][0] + G[1][1]
    return 'boost' if abs(t_) > 2 else ('null rotation' if abs(t_) == 2 else 'rotation')
gens = [M, B, [[1, 0], [-3, 1]], [[2, -1], [-1, 1]]]
words = {}
for k in range(1, 8):
    for w in itertools.product(range(4), repeat=k):
        G = [[1, 0], [0, 1]]
        for i in w: G = mm(G, gens[i])
        t_ = G[0][0] + G[1][1]
        if abs(t_) < 2 and t_ not in words: words[t_] = (w, G)
null = [(0, 1), (1, 0)]
fixedray = [n for n in ((F(0), F(0), F(1)),)]
LB = lorentz(B)
# the light ray fixed by B: X = [[0, 0], [0, 1]], t = 1/2, x = -1/2, y = 0
ray = (F(1, 2), F(-1, 2), F(0)); LBr = tuple(sum(LB[i][j] * ray[j] for j in range(3)) for i in range(3))
ok6 = lt_kind(M) == 'boost' and lt_kind(B) == 'null rotation' and LBr == ray and sorted(words) == [0] and sum(lorentz(words[0][1])[i][i] for i in range(3)) == -1 and lorentz(mm(words[0][1], words[0][1])) == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
P('three-kinds', ok6, 'Omega42\'s group <A^2, B> holds every kind of Lorentz transformation: A^2 a boost (trace 3); B a null rotation (trace 2) fixing the light ray (t, x, y) = (1/2, -1/2, 0);',
  'and %s, of trace 0, a half turn about a timelike axis, conjugate to a spatial rotation by pi (its 3 x 3 trace -1 = 1 + 2 cos pi, its square the identity): no word of length up to 7 has trace 1 or -1' % words[0][1])
# R7: two golden boosts, M and N = [[2, 1], [1, 1]] (the boost of A^2 conjugated by the swap); directions at cos 3/5
N = [[2, 1], [1, 1]]
G = mm(M, N)   # [[3, 2], [4, 3]]
# polar decomposition G = S R, S symmetric positive, R a rotation by theta with tan theta = (c - b)/(a + d)
a_, b_, c_, d_ = G[0][0], G[0][1], G[1][0], G[1][1]
tan_half = F(c_ - b_, a_ + d_)
cos_w = (1 - tan_half ** 2) / (1 + tan_half ** 2); sin_w = 2 * tan_half / (1 + tan_half ** 2)
dirM = (F(-1), F(2)); dirN = (F(1), F(2))   # boost directions (x, y), each of length sqrt5
cosD = (dirM[0] * dirN[0] + dirM[1] * dirN[1]) / 5
coth2 = F(9, 5)   # coth^2(eta/2) = (3/2)^2 / (5/4)
sinD = F(4, 5)
tw = sinD / (coth2 + cosD)   # Thomas-Wigner: tan(w/2) = sin D / (coth(e1/2) coth(e2/2) + cos D)
# floating check from the 3 x 3 matrices: the rotation part of L(G) after removing its boost
LG = [[float(x) for x in r] for r in lorentz(G)]
gG = LG[0][0]; ux, uy = LG[1][0] / math.sqrt(gG * gG - 1), LG[2][0] / math.sqrt(gG * gG - 1)
gbG = math.sqrt(gG * gG - 1)
Binv = [[gG, -gbG * ux, -gbG * uy], [-gbG * ux, 1 + (gG - 1) * ux * ux, (gG - 1) * ux * uy], [-gbG * uy, (gG - 1) * ux * uy, 1 + (gG - 1) * uy * uy]]
Rm = [[sum(Binv[i][k] * LG[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
ok7 = G == [[3, 2], [4, 3]] and cosD == F(3, 5) and tan_half == F(1, 3) and tw == tan_half and cos_w == F(4, 5) and sin_w == F(3, 5) and abs(Rm[1][1] - 0.8) < 1e-12 and abs(abs(Rm[2][1]) - 0.6) < 1e-12
P('wigner', ok7, 'two golden boosts, M = A^2 and N = [[2,1],[1,1]], in directions at the angle arccos(3/5), compose to G = MN = [[3,2],[4,3]], a boost followed by a Thomas-Wigner rotation',
  'with tan(w/2) = 1/3, so cos w = 4/5 and sin w = 3/5 exactly: the 3-4-5 angle; the Thomas-Wigner formula tan(w/2) = sin D / (coth^2(eta/2) + cos D) = (4/5)/(9/5 + 3/5) gives the same, and the rotation block of the 3 x 3 product is', [[round(Rm[i][j], 12) for j in (1, 2)] for i in (1, 2)])
# R8
M9 = [[x % 9 for x in r] for r in mpow(M, 6)]
L6 = lorentz(mpow(M, 6))
L6int = [[x for x in r] for r in L6]
# integer light-cone coordinates (u, y, w) = (t + x, y, t - x): the action on integer symmetric matrices modulo 9
def act_mod(G, X, m): return [[x % m for x in r] for r in mm(mm(G, X), tr(G))]
cyc = None
X0 = [[2, 1], [1, 1]]
allX = [[[a, b], [b, c]] for a in range(9) for b in range(9) for c in range(9)]
per = min(k for k in range(1, 13) if all(act_mod(mpow(M, k), X, 9) == X for X in allX))
ok8 = M9 == [[8, 0], [0, 8]] and per == 6 and lorentz(mpow(M, 7))[0][0] != lorentz(M)[0][0]
P('aliasing', ok8, 'modulo 9, (A^2)^6 = A^12 = -I, so the boost acts on integer states with period 6 (on all 729 symmetric matrices modulo 9: period %d), while gamma_1 = 7/2 and gamma_7 = %s:' % (per, lorentz(mpow(M, 7))[0][0]),
  'the residue modulo 9 keeps n mod 6, the quotient keeps the rest; two boosts with the same residue are not the same boost (NE-010)')
# R9: Sym^2 of M: the 3 x 3 boost's eigenvalues are lambda^2, 1, lambda^-2 with lambda = phi^2
ch = [-det3(L), None]
trL = L[0][0] + L[1][1] + L[2][2]
# characteristic polynomial of L: x^3 - tr x^2 + s2 x - det; for Sym^2 of eigenvalues l, 1/l: tr = l^2 + 1 + l^-2 = (l + 1/l)^2 - 1 = 9 - 1 = 8
P('spinor', trL == 8 and det3(L) == 1, 'the 2 x 2 law is the spinor transformation of SL2(R) = Spin(2,1) and the 3 x 3 boost is its symmetric square: tr L = (tr A^2)^2 - 1 = 8, det L = 1,',
  'eigenvalues phi^4, 1, phi^-4; the law acts on spinors by A^2 and on vectors by its square, and the finite quantum lift is the Weil representation of MF-100')
# R10: Hermitian 3 + 1
ok10 = True
for t, x, y, z in itertools.product(range(-2, 3), repeat=4):
    # X = [[t + z, x - iy], [x + iy, t - z]]; with real M: M X M^T = M Re M^T + i M Im M^T, Im = [[0, -y], [y, 0]] = y J, M J M^T = det(M) J
    Re = [[t + z, x], [x, t - z]]; Rp = mm(mm(M, Re), tr(M)); yp = y * (M[0][0] * M[1][1] - M[0][1] * M[1][0])
    tp, zp, xp = F(Rp[0][0] + Rp[1][1], 2), F(Rp[0][0] - Rp[1][1], 2), Rp[0][1]
    ok10 = ok10 and tp * tp - xp * xp - yp * yp - zp * zp == t * t - x * x - y * y - z * z and yp == y
P('three-plus-one', ok10, 'on Hermitian matrices X = [[t + z, x - iy], [x + iy, t - z]] the map X -> M X M^T, M = A^2 in SL2(C), keeps t^2 - x^2 - y^2 - z^2 and fixes y, checked on the 625 integer states with entries -2 to 2:',
  'the golden boost of 2 + 1 dimensions is a Lorentz transformation of 3 + 1, through the double cover SL2(C) -> SO+(3,1)')
# R11, R12: the golden ring Z[phi]
# exact arithmetic in Q(phi): a + b phi, phi^2 = phi + 1
class Q5:
    __slots__ = ('a', 'b')
    def __init__(s, a=0, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __neg__(s): return Q5(-s.a, -s.b)
    def __sub__(s, o): return s + (-(o if isinstance(o, Q5) else Q5(o)))
    def __rsub__(s, o): return Q5(o) - s
    def __mul__(s, o):
        o = o if isinstance(o, Q5) else Q5(o)
        return Q5(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    __rmul__ = __mul__
    def conj(s): return Q5(s.a + s.b, -s.b)          # phi -> 1 - phi
    def norm(s): n = s * s.conj(); return n.a       # rational
    def inv(s): n = s.norm(); c = s.conj(); return Q5(c.a / n, c.b / n)
    def __truediv__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s * o.inv()
    def __eq__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s.a == o.a and s.b == o.b
    def __hash__(s): return hash((s.a, s.b))
    def __float__(s): return float(s.a) + float(s.b) * (1 + 5 ** .5) / 2
    def __repr__(s): return '%s + %s phi' % (s.a, s.b) if s.b else str(s.a)
PHI_ = Q5(0, 1)

def mmq(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
def lorentz_q(G_):
    cols = []
    for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        t, x, y = (Q5(c) for c in v); X = [[t + x, y], [y, t - x]]
        Y = mmq(mmq(G_, X), [[G_[0][0], G_[1][0]], [G_[0][1], G_[1][1]]])
        cols.append(((Y[0][0] + Y[1][1]) * Q5(F(1, 2)), (Y[0][0] - Y[1][1]) * Q5(F(1, 2)), Y[0][1]))
    return [[cols[j][i] for j in range(3)] for i in range(3)]
def det3q(L): return (L[0][0] * (L[1][1] * L[2][2] - L[1][2] * L[2][1]) - L[0][1] * (L[1][0] * L[2][2] - L[1][2] * L[2][0]) + L[0][2] * (L[1][0] * L[2][1] - L[1][1] * L[2][0]))
def iso_q(L):
    E_ = [[Q5(1), Q5(0), Q5(0)], [Q5(0), Q5(-1), Q5(0)], [Q5(0), Q5(0), Q5(-1)]]
    LT = [[L[j][i] for j in range(3)] for i in range(3)]
    R_ = [[sum((LT[i][k] * E_[k][l] * L[l][j] for k in range(3) for l in range(3)), Q5(0)) for j in range(3)] for i in range(3)]
    return R_ == E_
Dg = [[PHI_, Q5(0)], [Q5(0), PHI_ - 1]]                 # diag(phi, 1/phi), in SL2(Z[phi])
LD = lorentz_q(Dg)
LD2 = lorentz_q(mmq(Dg, Dg))
P('golden-ring-boost', (Dg[0][0] * Dg[1][1] - Dg[0][1] * Dg[1][0]) == 1 and iso_q(LD) and det3q(LD) == 1 and LD[0][0] == Q5(F(3, 2)) and LD2[0][0] == Q5(F(7, 2)),
  'over the law\'s ring the half golden boost becomes proper: diag(phi, phi - 1) lies in SL2(Z[phi]) and its Lorentz image is a proper orthochronous boost with gamma = 3/2 = L_2/2, rapidity 2 ln phi,',
  'whose square has gamma = 7/2, the golden boost; over Z the half boost carries a reflection (MF-138), over Z[phi] it stands alone')
Rg = [[PHI_, Q5(-1)], [Q5(1), Q5(0)]]                   # trace phi = 2 cos 36 degrees
pw = [[Q5(1), Q5(0)], [Q5(0), Q5(1)]]; order = None
for k in range(1, 21):
    pw = mmq(pw, Rg)
    if pw == [[Q5(1), Q5(0)], [Q5(0), Q5(1)]]: order = k; break
LR = lorentz_q(Rg)
trR = LR[0][0] + LR[1][1] + LR[2][2]
L5 = [[Q5(int(i == j)) for j in range(3)] for i in range(3)]
for _ in range(5): L5 = [[sum((L5[i][k] * LR[k][j] for k in range(3)), Q5(0)) for j in range(3)] for i in range(3)]
I3 = [[Q5(int(i == j)) for j in range(3)] for i in range(3)]
# the crystallographic restriction over Z: an elliptic element of SL2(Z) has trace 0 or +-1, so its rotation has order 2 or 3
P('golden-rotation', order == 10 and iso_q(LR) and trR == PHI_ and L5 == I3 and LR != I3,
  'the element [[phi, -1], [1, 0]] of SL2(Z[phi]), trace phi = 2 cos 36 degrees, has order 10, and its Lorentz image is a rotation of order 5 by 72 degrees about a timelike axis, 3 x 3 trace 1 + 2 cos 72 = phi:',
  'over Z the traces of rotations are 0 and +-1, rotations of order 2 and 3, the crystallographic restriction of the Lorentz group; the law\'s ring breaks it with the five-fold rotation of the icosahedron and the quasicrystal')
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('RELATIVITY SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if len(a) == 2 and a[0] == '--boost':
        n = int(a[1]); g_ = F(luc(4 * n), 2)
        print('golden boost n = %d: gamma = %s, (gamma beta)^2 = %s, beta = %.15f, Doppler factor phi^%d = %.6f' % (n, g_, F(5 * fib(4 * n) ** 2, 4), 5 ** .5 * fib(4 * n) / luc(4 * n), 4 * n, PHI ** (4 * n)))
        sys.exit(0)
    print(__doc__); sys.exit(2)
