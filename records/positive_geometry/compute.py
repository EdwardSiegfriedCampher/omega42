"""records/positive_geometry/compute.py -- Omega42 and positive geometry (Core 1.8.10, M230-K, L-492; Companion 50.6).
Standard library only; the Grassmannian check is exact in rational arithmetic; the
golden-arc identity (PG-01) and the twisted-shift orders are re-proved independently, in exact arithmetic over Q(sqrt 5)
and with a different method, by records/positive_geometry/independent_check.py."""
import itertools, math
from fractions import Fraction as F
phi = (1 + 5 ** 0.5) / 2
print('=== A. Over the reals the norm is a 1-dimensional positive geometry bounded by the golden directions ===')
Nr = lambda a, b: a * a + a * b - b * b
al, be = -phi, 1 / phi
print('zero locus of N on x = a/b: x = -phi = %.6f and x = 1/phi = %.6f (the two eigendirections of T)' % (al, be))
g = lambda x: 1 / (x + 1)                      # T(a, b) = (b, a + b) on x = a/b
print('fixed points of T on RP^1 are these two points:', abs(g(al) - al) < 1e-12, abs(g(be) - be) < 1e-12)
d = lambda f, x, h=1e-6: (f(x + h) - f(x - h)) / (2 * h)
print("T'(1/phi) = %.6f = -1/phi^2, T'(-phi) = %.6f = -phi^2: both negative, T reverses the orientation of RP^1" % (d(g, be), d(g, al)))
g2 = lambda x: g(g(x))
print("(T^2)'(1/phi) = %.6f, (T^2)'(-phi) = %.6f: positive, T^2 preserves orientation; 1/phi attracts, -phi repels" % (d(g2, be), d(g2, al)))
xs = [-1.5, -0.9, -0.3, 0.0, 0.4, 0.6, 0.7, 1.0, 2.5, 10.0]
print('T swaps the arc N<0 (-phi, 1/phi) with the arc N>0 through infinity:', all((Nr(x, 1) > 0) != (Nr(g(x), 1) > 0) for x in xs))
print('T^2 keeps each arc:', all((Nr(x, 1) > 0) == (Nr(g2(x), 1) > 0) for x in xs))
om = lambda x: (be - al) / ((x - al) * (be - x))  # canonical form of the arc (al, be), coefficient of dx
pb = [om(g(x)) * d(g, x) / om(x) for x in (-1.2, -0.5, 0.2, 0.5, 3.0)]
print('pullback of the arc form by T, divided by the form, at five points: %s (=+1 as a rational form)' % ['%.6f' % v for v in pb])
print('so T*Omega(image arc) = -Omega(source arc): the canonical form of the complement arc is -omega; T is orientation-reversing')
print('N(T(a,b)) = det(T) N(a,b) with det T = -1, integer check on all pairs with |a|, |b| <= 15:',
      all(Nr(b, a + b) == -Nr(a, b) for a in range(-15, 16) for b in range(-15, 16)))
print()
print('=== B. Mod 9 the golden directions do not exist; the norm-zero locus is the core, and the strata recurse to a point ===')
T = lambda s: (s[1], (s[0] + s[1]) % 9)
Nm = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
print('roots of x^2 = x + 1 mod 9:', [r for r in range(9) if (r * r - r - 1) % 9 == 0] or 'none')
S = [(i, j) for i in range(9) for j in range(9)]
units = [s for s in S if Nm(s) % 3]; zero = [s for s in S if Nm(s) == 0]
print('norm a unit on %d states, 0 mod 9 on %d, other values on %d' % (len(units), len(zero), 81 - len(units) - len(zero)))
print('norm 0 exactly on the core {0,3,6}^2:', sorted(zero) == sorted((i, j) for i in (0, 3, 6) for j in (0, 3, 6)))
N3 = lambda u: (u[0] ** 2 + u[0] * u[1] - u[1] ** 2) % 3
c8 = [s for s in zero if s != (0, 0)]
print('residual norm N(s/3) mod 3 on the 8 nonzero core states takes', sorted({N3((s[0] // 3, s[1] // 3)) for s in c8}), '- never 0')
print('T negates the residual norm on the core:', all(N3((T(s)[0] // 3, T(s)[1] // 3)) == (-N3((s[0] // 3, s[1] // 3))) % 3 for s in c8))
print('strata: 72 (norm a unit) + 8 (norm 0, residual norm a unit) + 1 (all zero) =', len(units) + len(c8) + 1, '= the orbits 24+24+24 | 8 | 1')
half = {1, 2, 4}
print('the 1/7 half {1,2,4} and the 6/7 half {8,7,5} = -{1,2,4}: each voice has one norm in each half; T exchanges halves on all 72:',
      all((Nm(s) in half) != (Nm(T(s)) in half) for s in units))
print()
print('=== C. The twisted cyclic symmetry of the positive Grassmannian G>0(2,12) (exact) ===')
t = [F(i * i - 30, 7) for i in range(12)]                  # 12 increasing rationals
M = [[F(1)] * 12, t]                                       # columns (1, t_i): every ordered 2x2 minor is t_j - t_i > 0
det2 = lambda M, i, j: M[0][i] * M[1][j] - M[0][j] * M[1][i]
pos = lambda M: all(det2(M, i, j) > 0 for i, j in itertools.combinations(range(12), 2))
tw = lambda M: [row[1:] + [-row[0]] for row in M]          # k = 2: twist (-1)^(k-1) = -1
un = lambda M: [row[1:] + [row[0]] for row in M]
print('a point of G>0(2,12): all 66 ordered minors positive:', pos(M))
P = M; ok = True; half_neg = False
for s_ in range(1, 25):
    P = tw(P); ok &= pos(P)
    if s_ == 12: half_neg = P == [[-x for x in row] for row in M]
print('every twisted shift keeps positivity: %s | 12 shifts give -I on the columns: %s | 24 give I: %s' % (ok, half_neg, P == M))
print('the untwisted shift keeps positivity:', pos(un(M)), '(the sign is required for k even)')
# the object acted on: matrix representatives (the lift) versus points of the Grassmannian (row spaces)
def pluecker(M):
    v = [det2(M, i, j) for i, j in itertools.combinations(range(12), 2)]
    f = next(x for x in v if x != 0)
    return [x / f for x in v]                          # projective normalization: a point of Gr(2,12) in Pluecker space
P = M; rep_order = pt_order = None
for s_ in range(1, 25):
    P = tw(P)
    if pt_order is None and pluecker(P) == pluecker(M): pt_order = s_
    if rep_order is None and P == M: rep_order = s_
print('ORDER ON MATRIX REPRESENTATIVES (the lift; the action on the column module): %d, with -I at 12' % rep_order)
print('ORDER ON GRASSMANNIAN POINTS (row spaces; M and -M span the same plane): %d' % pt_order)
print('so the half-period negation lives on the lift; on Gr(2,12) itself the twisted shift has order 12. FP-TwistedQuotient (part E) is a statement about the lift.')
print()
print('=== G. The positive-geometry studies PG-01 to PG-03, on the norm geometry itself ===')
v1 = (1 / phi, 1.0); v2 = (-phi, 1.0)          # eigenvectors of T on x = a/b: T v = lambda v
Tm = lambda u: (u[1], u[0] + u[1])
lam = lambda v: Tm(v)[1] / v[1]
print('PG-01 admissibility. DEFINITIONS: A(n,k,m)(Z) = {C Z : C in G>0(k,n)} in Gr(k,k+m), for Z a real n x (k+m) matrix with positive maximal minors.')
print('       Here n = 2, k = m = 1: G>0(1,2) = {[c1:c2] : c1 c2 > 0}; Gr(1,2) = RP^1 with points [a:b]; THE MAP is [c1:c2] -> [c1 Z1 + c2 Z2], with')
print('       Z1 = (1, phi) and Z2 = (-1, 1/phi), the eigenvectors of T for phi and -1/phi (x = a/b = 1/phi and -phi), ordered and signed so that det Z > 0.')
Z1 = (1.0, phi); Z2 = (-1.0, 1 / phi)
print('       det Z = %.6f = sqrt 5 > 0; N(Z1) and N(Z2) below 1e-12: %s (both vertices are null); polar coefficient of c1 c2: %.6f = -5'
      % (Z1[0] * Z2[1] - Z1[1] * Z2[0], abs(Nr(*Z1)) < 1e-12 and abs(Nr(*Z2)) < 1e-12, Nr(Z1[0] + Z2[0], Z1[1] + Z2[1]) - Nr(*Z1) - Nr(*Z2)))
print('       IDENTITY: N(c1 Z1 + c2 Z2) = -5 c1 c2, so a point lies in the image exactly when N < 0: A(2,1,1)(Z) IS the golden arc, as an equality of subsets of RP^1 in this')
print('       representation (EXACT; proved in exact arithmetic over Q(sqrt 5) by independent_check.py, which shares no code with this file). The identification with the abstract')
print('       segment is generic -- every segment of RP^1 is an A(2,1,1) for some Z; what is particular is that the data Z are the law\'s own eigenbasis.')
print('       PRESERVED STRUCTURE, in the coordinates (c1, c2): T acts as diag(phi, -1/phi) = diag(%.6f, %.6f), outside the positive torus, carrying the arc onto its complement N > 0;'
      % (lam(v1), lam(v2)))
print('       T^2 acts as diag(phi^2, 1/phi^2) = diag(%.6f, %.6f), inside it: an automorphism of the arc fixing both vertices, which preserves the canonical form d log(c2/c1)' % (lam(v1) ** 2, lam(v2) ** 2))
print('       exactly, since it multiplies c2/c1 by the constant phi^-4. Persistence (T^2) is the positivity-preserving square; manifestation (T) is the single sign flip.')
S9 = [(i, j) for i in range(9) for j in range(9)]
Nm9 = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9
print('PG-02 boundary. Over the reals the boundary of the arc is its two vertices, the golden directions; modulo 9 these have no points, and N = 0 exactly when s = 0 mod 3:',
      all((Nm9(s) == 0) == (s[0] % 3 == 0 and s[1] % 3 == 0) for s in S9))
print('       the real boundary and the modular core are the zero loci of the same algebraic expression read over two domains, R and Z/9: they do not share geometry, cardinality')
print('       (two lines; nine states) or topology, and no map carries one to the other (the vertices have no image mod 9): STRUCTURAL by the common expression only, NOT a map of boundaries.')
print('       any map from these strata to the boundary strata of an amplituhedron of higher k or m: OPEN.')
print('PG-03 structure to output. Amplituhedron: positive geometry -> canonical form (determined by its boundaries) -> amplitude (residues = factorization). Omega42: counts -> residues mod 9 (a ring homomorphism: ring relations kept, magnitude lost) -> coordinate and arms -> reading. Both outputs are fixed by residue data, but the residues are of different kinds (residues of a form; residue classes): ANALOGY, recorded as such.')
print('       a correspondence would have to name which input of one construction answers to which output of the other; none is named, so ANALOGY is the exact classification.')
print()
print('=== D. Fibonacci ratios alternate across the golden boundary and never reach it ===')
f = [0, 1]
for _ in range(20): f.append(f[-1] + f[-2])
r = [F(f[n], f[n + 1]) for n in range(1, 16)]
print('F(n)/F(n+1) - 1/phi, signs n = 1..15:', ''.join('+' if float(q) > 1 / phi else '-' for q in r))
print('N(F(n), F(n+1)) for n = 0..10:', [Nr(f[n], f[n + 1]) for n in range(11)], '(Cassini: +-1, alternating; never 0 -- no rational point on the boundary)')
print()
print('=== E. The twisted cyclic quotient of G>0(k,n): when does it carry the family? (peer test, DeepSeek APE-047) ===')
# The twisted cyclic shift on the n columns is multiplication by x in Z[x]/(x^n - s), s = (-1)^(k-1).
# Its golden quotient Z[x]/(x^n - s, 9, x^2 - x - 1) = Z[phi]/(9, phi^n - s). Compute its size and the action of x (= T).
def pmul(u, v):                       # (a + b phi)(c + d phi) mod 9, phi^2 = phi + 1
    a, b = u; c, d = v
    return ((a * c + b * d) % 9, (a * d + b * c + b * d) % 9)
def ppow(u, n):
    r = (1, 0)
    for _ in range(n): r = pmul(r, u)
    return r
R = [(a, b) for a in range(9) for b in range(9)]
def quotient_size(gen):                # |Z[phi]/9 / (gen)| = 81 / |ideal generated by gen|
    ideal = {pmul(gen, r) for r in R}
    return 81 // len(ideal)
rows = []
for k_parity, s in (('k even', -1), ('k odd', 1)):
    full = [n for n in range(1, 73) if quotient_size(((ppow((0, 1), n)[0] - s) % 9, ppow((0, 1), n)[1])) == 81]
    rows.append((k_parity, full))
    print('%s (twist %+d): the quotient is the whole 81-state family exactly for n in %s' % (k_parity, s, full))
print('so n = 12 (k even) is the smallest case; phi^12 = %s = -1 in Z[phi]/9 (144 phi + 89)' % (ppow((0, 1), 12),))
print('on that quotient x acts as multiplication by phi, i.e. as T: orbits 24+24+24+8+1, and N(phi s) = -N(s) -- the family with its law')
print('class level, not discriminating: every lattice automorphism g with g^12 = -I has the same quotient (Core run 06)')
print('over the reals the twisted shift has finite order (elliptic) while T is hyperbolic: no real conjugacy; the meeting is arithmetic')
print()
print('=== F. The core recursion: the core of the family mod 3^k is the whole family mod 3^(k-1) ===')
def fam(m):
    T = lambda s: (s[1], (s[0] + s[1]) % m)
    seen = set(); lens = []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o = [(a, b)]; s = T((a, b))
            while s != (a, b): o.append(s); s = T(s)
            seen |= set(o); lens.append(len(o))
    return sorted(lens, reverse=True)
from collections import Counter
for m in (9, 27, 81):
    T = lambda s, m=m: (s[1], (s[0] + s[1]) % m)
    core = [(a, b) for a in range(0, m, 3) for b in range(0, m, 3)]
    sub = {(a // 3, b // 3) for a, b in core}
    acts = all(((T(s)[0] // 3), (T(s)[1] // 3)) == (s[1] // 3, (s[0] // 3 + s[1] // 3) % (m // 3)) for s in core)
    print('mod %2d: orbit lengths %s | the core (multiples of 3) has %d states, is 3 x the family mod %d, and T acts on it as the law mod %d: %s'
          % (m, dict(Counter(fam(m))), len(core), m // 3, m // 3, acts))
print('3 is inert in Z[phi] (5 is not a square mod 3), so the non-units mod 3^k are exactly 3 x (Z[phi]/3^(k-1)): the still axis at one scale is the whole family at the scale below')
print()
print('=== H. PG-05 (mechanism): the halves of M312 are the two arcs, through the minimal lift ===')
# a state s mod 9 lifts to integer pairs (a, b) = s mod 9; its MINIMAL LIFT is one of least |N(a, b)| (the real norm)
def is_norm(n):                       # n is a norm of Z[phi] iff every prime = +-2 mod 5 divides it to an even power
    n = abs(n)
    if n == 0: return True
    p = 2
    while p * p <= n:
        e = 0
        while n % p == 0: n //= p; e += 1
        if p % 5 in (2, 3) and e % 2: return False
        p += 1
    return not (n > 1 and n % 5 in (2, 3))
def least_norm(res):                  # the least |n| over norms n of Z[phi] with n = res mod 9: a lower bound for any lift
    return min(abs(n) for n in range(-60, 61) if n % 9 == res and is_norm(n))
SEV = {1, 2, 4}
best = {}
for a in range(-40, 41):
    for b in range(-40, 41):
        n = Nr(a, b); s = (a % 9, b % 9)
        if s not in best or abs(n) < abs(best[s][0]): best[s] = (n, (a, b))
units9 = [s for s in S9 if Nm9(s) % 3]
attained = all(abs(best[s][0]) == least_norm(Nm9(s)) for s in units9)
vm = {d: {abs(best[s][0]) for s in units9 if Nm9(s) in (d, 9 - d)} for d in (1, 4, 2)}
print('the least |N| of a lift is attained in the search box for all 72 unit states (lower bound by the norm criterion): %s' % attained)
print('least |N| by voice: Voice A {1, 8}: %s | Voice B {4, 5}: %s | Voice C {2, 7}: %s -- the norms +-2 and +-7 do not occur in Z[phi] (2 and 7 are inert)' % (vm[1], vm[4], vm[2]))
agree = sum((Nm9(s) in SEV) == (best[s][0] > 0) for s in units9)
print('the half is the real sign of the minimal lift: SEVENTH {1,2,4} <-> N > 0 (the arc N > 0), MANIFEST {8,7,5} <-> N < 0 (the golden arc A(2,1,1)(Z)): %d of 72' % agree)
core8 = [s for s in S9 if Nm9(s) == 0 and s != (0, 0)]
ax = sum(abs(best[s][0]) == 9 and ((((s[0] // 3) ** 2 + (s[0] // 3) * (s[1] // 3) - (s[1] // 3) ** 2) % 3 == 1) == (best[s][0] > 0)) for s in core8)
print('on the core the minimal lift is 3 times a unit lift, N = +-9, and its sign is the AXIS sign (residual norm 1 -> +, 2 -> -): %d of 8 (FP-CoreRecursion, one scale down)' % ax)
print('the still point (0, 0): its least lift is (0, 0) itself, N = 0 -- the point with no direction lies on no arc: %s' % (best[(0, 0)][0] == 0))
eq = all(abs(Nr(*Tm(best[s][1]))) == abs(best[s][0]) and (Nr(*Tm(best[s][1])) > 0) != (best[s][0] > 0) for s in units9 + core8)
print('EQUIVARIANCE: T of a minimal lift is a minimal lift of T(s) with the opposite sign, so T exchanges the arcs exactly as it exchanges the halves, and T^2 keeps both: %s' % eq)
print('so under the minimal-lift rule the two halves, read from the digits of 1/7 and 6/7, are the two arcs of real positivity: the seventh {1,2,4} is the residue of positive norm (EXACT, under the stated rule)')
print()
print('=== I. What survives which operation (the survival ledger of Companion 50.15) ===')
def red(u): return (u[0] % 9, u[1] % 9)
def zmul(u, v):                       # (a + b phi)(c + d phi) in Z[phi], as pairs (a, b) = a + b phi
    a, b = u; c, d = v
    return (a * c + b * d, a * d + b * c + b * d)
ZN = lambda u: u[0] * u[0] + u[0] * u[1] - u[1] * u[1]
box = [(a, b) for a in range(-6, 7) for b in range(-6, 7)]
rel = all(red(zmul(u, v)) == pmul(red(u), red(v)) for u in box for v in box[::7])
mult = all(ZN(zmul(u, v)) == ZN(u) * ZN(v) for u in box for v in box[::7])
negid = all(Nm9(T(s)) == (-Nm9(s)) % 9 for s in S9)
o9 = next(n for n in range(1, 100) if ppow((0, 1), n) == (1, 0))
seq = [(0, 1)]
for _ in range(30): seq.append(zmul(seq[-1], (0, 1)))
print('(1) COEFFICIENT REDUCTION Z[phi] -> Z[phi]/9, a ring homomorphism: ring relations kept (phi^2 = phi + 1, products): %s | norm multiplicative over Z: %s, and so mod 9' % (rel, mult))
print('    the norm-negation identity N(phi s) = -N(s) holds over Z and survives reduction as an identity mod 9: %s -- "sign" is reserved for the real norm' % negid)
print('    magnitude and real order: LOST (residues are not ordered) | the period: CREATED -- phi has infinite order in Z[phi] (phi^30 = %s) and order %d mod 9, with phi^12 = -1 mod 9' % (seq[29], o9))
print('(2) INDUCED FINITE-STATE DYNAMICS: T on (Z/9)^2 is multiplication by phi: orbits 24+24+24 | 8 | 1, T^12 = -I, the halves exchanged (parts B, F)')
print('(3) POINTWISE MAPS from the real line to the states: only rational points lift (primitive integer pairs); the golden directions have no image (x^2 = x + 1 has no root mod 9, part B);')
print('    the zero locus of N is two lines over R and nine states over Z/9 -- one expression, not one geometry; real positivity reaches the states only through the minimal-lift rule of H')
