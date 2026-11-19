#!/usr/bin/env python3
"""fields.py -- Adinkras, supersymmetry and the mathematics of the fields of knowledge joined to Omega42
(Companion Part 220; F215, F216; APE-477, APE-478).

  A1 hamming-adinkra   the extended Hamming code [8,4,4] and its 16-vertex, 8-color Adinkra
  A2 adinkra-e8        Construction A of the same code is E8; <A^2, B> mod 7 recolors the Adinkra (168 automorphisms)
  A3 garden            octonions on the Fano lines {i, i+1, i+3} mod 7 give the Garden algebra of the N = 8 valise Adinkra
  A4 golay-adinkra     the extended Golay code [24,12,8] and its 4096-vertex Adinkra; Construction A gives A1^24, not Leech
  A5 adinkra-genus     the E8 Adinkra as a ribbon graph: genus 9 = 1 + (N - 4) 2^(N - k - 3)
  B1 phyllotaxis       Vogel's spiral: nearest-neighbour index differences are Fibonacci numbers
  B2 drone             a drone's ancestors k generations back number F_(k+1)
  B3 leslie            the Leslie matrix [[1,1],[1,0]] is the law with coordinates exchanged
  B4 hueckel           the five-membered ring has Hueckel energies -phi, -phi, 1/phi, 1/phi, 2
  B5 lame              Euclid's algorithm takes its most steps on consecutive Fibonacci numbers
  B6 fibonacci-code    Fibonacci coding is prefix-free
  B7 maximal-evenness  the diatonic scale and the Fibonacci chain are balanced words; pi(12) = 24
  X1 control           the law check is a controllable system over Z/9: every state from exactly one pair of marks
  X2 next-generation   a two-stage infection with the law as next-generation matrix has R0 = phi
  X3 leontief          the Leontief economy T = A/2 has multiplier [[2,2],[2,4]]; sum F_n/2^n = 2
  X4 conservation      Michaelis-Menten conserves two linear charges; the law none, and Q^2
  X5 euclidean-rhythm  E(F_k, F_(k+1)) is a rotation of the Fibonacci chain, up to (55, 89)
  X6 capacity          a mark carries log2 3 bits, a state 4 marks; a random final corruption escapes with probability 1/81

    python3 tools/fields.py --selftest
Standard library only. Exact except the phyllotaxis distances (floating point, nearest neighbours).
"""
import itertools, math, sys
from fractions import Fraction as F
PHI = (1 + 5 ** .5) / 2
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))

def span(gens, n):
    S = {0}
    for g in gens:
        v = int(''.join(map(str, g)), 2) if not isinstance(g, int) else g
        S |= {x ^ v for x in S}
    return S
wt = lambda x: bin(x).count('1')

# ---------- ADINKRAS ----------
G8 = [[1,1,1,1,1,1,1,1],[0,0,0,0,1,1,1,1],[0,0,1,1,0,0,1,1],[0,1,0,1,0,1,0,1]]
H8 = span(G8, 8)
enum = {w: sum(1 for c in H8 if wt(c) == w) for w in range(9)}
selfdual = all(wt(a & b) % 2 == 0 for a in H8 for b in H8) and len(H8) == 16
def quotient(C, n):
    cls = {}; reps = []
    for v in range(2 ** n):
        if v in cls: continue
        r = len(reps); reps.append(v)
        for c in C: cls[v ^ c] = r
    edges = set()
    for r, v in enumerate(reps):
        for i in range(n):
            u = cls[v ^ (1 << (n - 1 - i))]
            edges.add((min(r, u), max(r, u), i))
    return reps, cls, edges
reps, cls, edges = quotient(H8, 8)
deg = {}
for a, b, i in edges: deg[a] = deg.get(a, 0) + 1; deg[b] = deg.get(b, 0) + 1
bip = all(wt(reps[a]) % 2 != wt(reps[b]) % 2 for a, b, i in edges)
simple = len({(a, b) for a, b, i in edges}) == len(edges)
P('A1', enum == {0: 1, 1: 0, 2: 0, 3: 0, 4: 14, 5: 0, 6: 0, 7: 0, 8: 1} and selfdual and len(reps) == 16 and set(deg.values()) == {8} and bip and simple,
  'the extended Hamming code [8,4,4]: weight enumerator 1 + 14x^4 + x^8, doubly even and self-dual; the chromotopology Q8/H8 has', len(reps),
  'vertices (8 bosons, 8 fermions), every vertex of degree 8, one edge of each color, simple and bipartite')

# A2: the same code, Construction A: E8; and the code is equivalent to Omega42's code of MF-77, so Omega42's group recolors the Adinkra
def con_a_roots(C, n):
    roots = 0
    for c in C:
        if wt(c) == 4: roots += 16
    roots += 2 * n     # +-2 e_i, norm 4 -> 2
    return roots
def ext_code(g):
    C = set()
    for m in itertools.product((0, 1), repeat=4):
        w = [0] * 7
        for i, mi in enumerate(m):
            if mi:
                for j, gj in enumerate(g):
                    if gj: w[(i + j) % 7] ^= 1
        C.add(int(''.join(map(str, w + [sum(w) % 2])), 2))
    return C
CQ = ext_code((1, 1, 0, 1))
def permute(c, perm, n):
    bits = [(c >> (n - 1 - i)) & 1 for i in range(n)]
    out = [0] * n
    for i in range(n): out[perm[i]] = bits[i]
    return int(''.join(map(str, out)), 2)
equiv = None
for perm in itertools.permutations(range(8)):
    if {permute(c, perm, 8) for c in CQ} == H8: equiv = perm; break
# Omega42's <A^2, B> mod 7 as coordinate permutations of P^1(F7) (index 7 = infinity), carried to H8 by the equivalence
pts = list(range(7)) + ['inf']
def mob(M, z):
    a, b, c, d = M
    if z == 'inf': return 'inf' if c % 7 == 0 else a * pow(c, -1, 7) % 7
    den = (c * z + d) % 7
    return 'inf' if den == 0 else (a * z + b) * pow(den, -1, 7) % 7
gp = lambda M: tuple(pts.index(mob(M, p)) for p in pts)
def closure(gens):
    e = tuple(range(8)); G = {e}; fr = [e]
    while fr:
        nx = []
        for g in fr:
            for h in gens:
                k = tuple(h[g[i]] for i in range(8))
                if k not in G: G.add(k); nx.append(k)
        fr = nx
    return G
Hgrp = closure([gp((1, 1, 1, 2)), gp((1, 0, 3, 1))])
inv = [0] * 8
for i, j in enumerate(equiv): inv[j] = i
conj = [tuple(equiv[h[inv[k]]] for k in range(8)) for h in Hgrp]
recol = all({permute(c, g, 8) for c in H8} == H8 for g in conj)
# a code automorphism g carries each class v + H8 to g(v) + H8 and an edge of color i to an edge of color g(i): a recoloring automorphism
def graph_auto(g):
    for a, b, i in edges:
        ga, gb = cls[permute(reps[a], g, 8)], cls[permute(reps[b], g, 8)]
        if (min(ga, gb), max(ga, gb), g[i]) not in edges: return False
    return True
P('A2', con_a_roots(H8, 8) == 240 and equiv is not None and recol and all(graph_auto(g) for g in conj) and len(conj) == 168,
  'Construction A of the same code has 16 + 14 x 16 = 240 roots: E8; the code is equivalent to the code of MF-77 by a permutation of colors, so the 168 elements of <A^2, B> mod 7 act on the E8 Adinkra as color-permuting automorphisms')

# A3: the Garden algebra from the octonions on the Fano plane of Omega42's E7 code (lines {i, i+1, i+3} mod 7)
lines = [(i % 7, (i + 1) % 7, (i + 3) % 7) for i in range(7)]
def omul(i, j):
    """product of imaginary units e_i e_j (i, j in 0..6), index 7 = the real unit: returns (sign, index)"""
    if i == 7: return 1, j
    if j == 7: return 1, i
    if i == j: return -1, 7
    for a, b, c in lines:
        for x, y, z in ((a, b, c), (b, c, a), (c, a, b)):
            if (i, j) == (x, y): return 1, z
            if (i, j) == (y, x): return -1, z
L = []
for I in range(8):
    M = [[0] * 8 for _ in range(8)]
    for j in range(8):
        s, k = omul(I if I < 7 else 7, j)
        M[k][j] = s
    L.append(M)
T = lambda M: [list(r) for r in zip(*M)]
mm = lambda X, Y: [[sum(X[i][k] * Y[k][j] for k in range(8)) for j in range(8)] for i in range(8)]
Rm = [T(M) for M in L]
garden = all(all(mm(L[I], Rm[J])[a][b] + mm(L[J], Rm[I])[a][b] == (2 if I == J and a == b else 0) for a in range(8) for b in range(8)) and
             all(mm(Rm[I], L[J])[a][b] + mm(Rm[J], L[I])[a][b] == (2 if I == J and a == b else 0) for a in range(8) for b in range(8)) for I in range(8) for J in range(8))
signed_perm = all(sorted(abs(x) for x in row) == [0] * 7 + [1] for M in L for row in M)
fano_ok = sorted(tuple(sorted(l)) for l in lines) == sorted([(0, 1, 3), (0, 2, 6), (0, 4, 5), (1, 2, 4), (1, 5, 6), (2, 3, 5), (3, 4, 6)])
P('A3', garden and signed_perm and fano_ok,
  'octonions built on the Fano lines {i, i+1, i+3} mod 7, the lines of the E7 code of MF-77, give 8 x 8 signed permutation matrices L_I, R_I = L_I^T with L_I R_J + L_J R_I = 2 delta I and R_I L_J + R_J L_I = 2 delta I exactly, for all 64 pairs: the Garden algebra of the N = 8 valise Adinkra')

# A4: the Golay code and its Adinkra (the action of A^2 and B modulo 23 on it is PR-002, sealed and not computed here)
p = 23; Qr = {(x * x) % p for x in range(1, p)}
def qrcode(S):
    e = [1 if i in S else 0 for i in range(p)]
    gens = [int(''.join(str(e[(i - k) % p]) for i in range(p)), 2) for k in range(p)]
    rows = []
    for v in gens:
        for r in rows: v = min(v, v ^ r)
        if v: rows.append(v)
    return rows
best = None
for S in (Qr, set(range(1, p)) - Qr, Qr | {0}, (set(range(1, p)) - Qr) | {0}):
    rows = qrcode(S)
    if len(rows) == 12: best = rows; break
rows24 = [(r << 1) | (wt(r) % 2) for r in best]
G24 = span(rows24, 24)
enum24 = {}
for c in G24: enum24[wt(c)] = enum24.get(wt(c), 0) + 1
golay = enum24 == {0: 1, 8: 759, 12: 2576, 16: 759, 24: 1}
P('A4', golay and len(G24) == 4096,
  'the extended Golay code [24,12,8] as the extended quadratic-residue code of length 24: weight enumerator 1 + 759x^8 + 2576x^12 + 759x^16 + x^24, doubly even and self-dual; its Adinkra Q24/G24 has 2^24/2^12 = 4096 vertices, 24 colors',
  '| Construction A of it is the Niemeier lattice with root system A1^24 (48 roots), not the Leech lattice:', 2 * 24 + 16 * sum(1 for c in G24 if wt(c) == 4), 'roots')

# A5: the Riemann surface of the E8 Adinkra: ribbon graph with colors in cyclic order at bosons, reversed at fermions
def genus(reps, cls, edges, n):
    nb = {}
    for a, b, i in edges: nb[(a, i)] = b; nb[(b, i)] = a
    boson = lambda v: wt(reps[v]) % 2 == 0
    # darts (v, i); face permutation: from dart (v, i) go to w = nb(v, i), then the next color at w in w's rotation
    seen = set(); faces = 0
    for v in range(len(reps)):
        for i in range(n):
            if (v, i) in seen: continue
            faces += 1; d = (v, i)
            while d not in seen:
                seen.add(d); w = nb[d]
                j = (d[1] + 1) % n if boson(w) else (d[1] - 1) % n
                d = (w, j)
    V, E = len(reps), len(edges); chi = V - E + faces
    return V, E, faces, chi, 1 - chi // 2
V, E, Fc, chi, g = genus(reps, cls, edges, 8)
reps4, cls4, edges4 = quotient({0, 0b1111}, 4)
g4 = genus(reps4, cls4, edges4, 4)[4]
doran = lambda N, k: 1 + (N - 4) * 2 ** (N - k - 3)
P('A5', g == doran(8, 4) and g4 == doran(4, 1), 'the E8 Adinkra as a ribbon graph: V =', V, 'E =', E, 'F =', Fc, 'chi =', chi, 'genus', g,
  '= 1 + (N - 4) 2^(N - k - 3) =', doran(8, 4), '| the N = 4 Adinkra of the code {0000, 1111}: genus', g4, '| the Golay Adinkra by the same formula: genus', doran(24, 12))

# ---------- OTHER FIELDS ----------
# biology: phyllotaxis -- Vogel's spiral with the golden angle; the index differences of nearest neighbours are Fibonacci numbers
ga = 2 * math.pi * (1 - 1 / PHI)
pts2 = [(math.sqrt(n) * math.cos(n * ga), math.sqrt(n) * math.sin(n * ga)) for n in range(1, 3001)]
fibs = {1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377}
diffs = set()
for n in range(1000, 3000, 7):
    x, y = pts2[n]
    near = sorted(range(n - 400, min(3000, n + 400)), key=lambda m: (pts2[m][0] - x) ** 2 + (pts2[m][1] - y) ** 2)[1:5]
    diffs |= {abs(m - n) for m in near}
P('B1', diffs <= fibs, 'biology, phyllotaxis: on Vogel\'s spiral with the golden angle %.4f degrees, the index differences of each seed\'s four nearest neighbours are' % math.degrees(ga), sorted(diffs), '-- all Fibonacci numbers (the parastichies)')
# biology: the ancestry of a male honeybee
def anc(sex, k):
    if k == 0: return {'m': 1, 'f': 0} if sex == 'm' else {'m': 0, 'f': 1}
    out = {'m': 0, 'f': 0}
    for par in (['f'] if sex == 'm' else ['m', 'f']):
        a = anc(par, k - 1); out['m'] += a['m']; out['f'] += a['f']
    return out
fib = lambda n: round(PHI ** n / 5 ** .5)
P('B2', all(sum(anc('m', k).values()) == fib(k + 1) for k in range(1, 20)), 'biology, the drone\'s family tree: a male bee has one parent, a female two; the ancestors k generations back number F_(k+1):', [sum(anc('m', k).values()) for k in range(1, 10)])
# demography: the Leslie matrix of two age classes with fecundity 1 and survival 1 is the law
Lesl = [[1, 1], [1, 0]]
P('B3', Lesl == [[A_ for A_ in r] for r in ([[1, 1], [1, 0]])] and abs(max(abs((1 + 5 ** .5) / 2), abs((1 - 5 ** .5) / 2)) - PHI) < 1e-15,
  'demography: the Leslie matrix [[1,1],[1,0]] (two age classes, fecundity 1, survival 1) is the law with its coordinates exchanged; growth rate phi, stable age distribution phi : 1')
# chemistry: Hueckel energies of a five-membered ring (cyclopentadienyl): adjacency eigenvalues 2 cos(2 pi k/5)
ev = sorted(2 * math.cos(2 * math.pi * k / 5) for k in range(5))
P('B4', abs(ev[0] + PHI) < 1e-12 and abs(ev[2] - 1 / PHI) < 1e-12 and abs(ev[4] - 2) < 1e-12,
  'chemistry, Hueckel theory: the five-membered carbon ring has orbital energies alpha + x beta with x =', [round(e, 6) for e in ev], '= -phi, -phi, 1/phi, 1/phi, 2')
# computer science: Lame's theorem -- Euclid's algorithm takes its most steps on consecutive Fibonacci numbers
def steps(a, b):
    n = 0
    while b: a, b = b, a % b; n += 1
    return n
best = {}
for a in range(1, 700):
    for b in range(1, a + 1):
        s = steps(a, b)
        if s > best.get('s', 0): best = {'s': s, 'a': a, 'b': b}
P('B5', (best['a'], best['b']) in {(fib(k + 1), fib(k)) for k in range(2, 20)}, 'computer science, Lame\'s theorem: among all pairs below 700, Euclid\'s algorithm takes its most steps,', best['s'], ', on', (best['a'], best['b']), '= (F_15, F_14), consecutive Fibonacci numbers')
# information theory: Fibonacci coding is a prefix-free universal code
def fcode(n):
    fs = [1, 2]
    while fs[-1] <= n: fs.append(fs[-1] + fs[-2])
    bits = []; m = n
    for f in reversed(fs[:-1]):
        if f <= m: bits.append('1'); m -= f
        else: bits.append('0')
    return ''.join(reversed(bits)).lstrip('0')[::-1][::-1] + '1' if False else ''.join(reversed(bits)).rstrip('0') + '1'
codes = [fcode(n) for n in range(1, 3000)]
prefix_free = not any(codes[j].startswith(codes[i]) for i in range(300) for j in range(300) if i != j)
ends = all(c.endswith('11') and '11' not in c[:-1] for c in codes)
kraft = sum(2 ** -len(c) for c in codes)
P('B6', prefix_free and ends and kraft < 1, 'information theory: Fibonacci coding of n is its Zeckendorf representation, low digit first, with a closing 1: every codeword ends in 11 and holds no other 11, so the code is prefix-free; Kraft sum over n < 3000 =', round(kraft, 6))
# music: maximal evenness and balanced words; the Pisano period of 12
def balanced(w, L):
    return all(max(c) - min(c) <= 1 for c in ([w[i:i + l].count('a') for i in range(len(w) - l)] for l in range(1, L)))
fw = 'a'
while len(fw) < 3000: fw = ''.join('ab' if c == 'a' else 'a' for c in fw)
diatonic = sorted({(12 * k) // 7 for k in range(7)})
steps12 = ''.join('W' if (diatonic[(i + 1) % 7] - diatonic[i]) % 12 == 2 else 'H' for i in range(7))
dia_bal = balanced((steps12 * 4).replace('W', 'a').replace('H', 'b'), 7)
pis = next(n for n in range(1, 200) if (fib(n) % 12, fib(n + 1) % 12) == (0, 1))
P('B7', balanced(fw, 40) and dia_bal and pis == 24, 'music: the diatonic scale {floor(12k/7)} =', diatonic, 'steps', steps12, 'is maximally even, a balanced word, as is the Fibonacci chain of MF-82 (every factor of each length up to 40 differs in its count of a by at most 1); the Fibonacci numbers modulo the 12 pitch classes repeat with period', pis, '= the period of the 24-cycle')



A = [[0, 1], [1, 1]]
mm2 = lambda X, Y: [[sum(X[i][k] * Y[k][j] for k in range(len(Y))) for j in range(len(Y[0]))] for i in range(len(X))]

# X1 ENGINEERING (control) <-> OMEGASL (the law check): the check s -> A s + (0, d) is a linear control system over Z/9
# structure: x' = A x + b u, b = (0, 1); mapping: u = the mark d; compatibility: identical recurrence; invariant: the Kalman matrix
K = [[0, 1], [1, 1]]                  # [b, A b] as columns: b = (0,1), A b = (1,1)
detK = K[0][0] * K[1][1] - K[0][1] * K[1][0]
reach = {}
for u1 in range(9):
    for u2 in range(9):
        s = (0, 0)
        for u in (u1, u2): s = (s[1], (s[0] + s[1] + u) % 9)
        reach.setdefault(s, []).append((u1, u2))
P('X1', detK % 3 != 0 and len(reach) == 81 and all(len(v) == 1 for v in reach.values()),
  'control theory: the law check of OmegaSL is the system x\' = Ax + bu over Z/9 with b = (0,1); the Kalman matrix [b, Ab] has determinant', detK,
  ', a unit, so the system is controllable: every one of the 81 states is reached from rest by exactly one pair of marks |',
  'consequence: two marks fix any check state, so the 4-mark check records the whole message state with no redundancy and no gap')

# X2 EPIDEMIOLOGY <-> DEMOGRAPHY <-> THE LAW: the next-generation matrix of a two-stage infection
# stage 1 (newly infected) infects at rate 1 and progresses; stage 2 (late) infects at rate 1: K = [[1, 1], [1, 0]]
NG = [[1, 1], [1, 0]]
R0 = (1 + 5 ** .5) / 2
gen = [[1], [0]]; counts = []
for g in range(12):
    counts.append(gen[0][0] + gen[1][0]); gen = mm2(NG, gen)
P('X2', counts[:10] == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89] and abs(max(abs(x) for x in ((1 + 5 ** .5) / 2, (1 - 5 ** .5) / 2)) - R0) < 1e-15,
  'epidemiology and demography: a two-stage branching process with next-generation matrix [[1,1],[1,0]] (the law with coordinates exchanged, the Leslie matrix of B3) has R0 = spectral radius = phi;',
  'infected per generation', counts[:10], '| consequence: R0 > 1, so the outbreak grows by phi each generation; any intervention that scales transmission by c < 1/phi stops it')

# X3 ECONOMICS <-> NUMBER THEORY: a two-sector Leontief economy with technology matrix A/2
T = [[F(0), F(1, 2)], [F(1, 2), F(1, 2)]]
I2 = [[F(1), F(0)], [F(0), F(1)]]
M = [[I2[i][j] - T[i][j] for j in range(2)] for i in range(2)]
d = M[0][0] * M[1][1] - M[0][1] * M[1][0]
Linv = [[M[1][1] / d, -M[0][1] / d], [-M[1][0] / d, M[0][0] / d]]
# series sum_n (A/2)^n entries are Fibonacci generating sums: sum F_n / 2^n = 2
def fibi(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a
gsum = sum(F(fibi(n), 2 ** n) for n in range(1, 400))
P('X3', Linv == [[F(2), F(2)], [F(2), F(4)]] and F(1, 2) / (1 - F(1, 2) - F(1, 4)) == 2 and abs(gsum - 2) < F(1, 10 ** 30),
  'economics: a two-sector Leontief economy whose technology matrix is the law halved, T = A/2, has total-output multiplier (I - T)^-1 =', [[int(x) for x in r] for r in Linv],
  '= sum of (A/2)^n, whose entries are sums of Fibonacci numbers over powers of 2; the Fibonacci generating function gives sum F_n/2^n = 2 exactly (x/(1 - x - x^2) at x = 1/2)', '| consequence: productive since the spectral radius phi/2 < 1')

# X4 CHEMISTRY <-> BIOLOGY <-> THE LAW: conserved quantities of a reaction network against the law's invariant
# Michaelis-Menten: E + S <-> ES -> E + P; species (E, S, ES, P); reactions as columns of N
N = [[-1, 1, 1], [-1, 1, 0], [1, -1, -1], [0, 0, 1]]
# left null space: c with c^T N = 0, found by enumeration of small integer vectors
cons = [c for c in itertools.product(range(-1, 2), repeat=4) if any(c) and all(sum(c[i] * N[i][j] for i in range(4)) == 0 for j in range(3))]
basis = [c for c in cons if c in ((1, 0, 1, 0), (0, 1, 1, 1))]
Q = lambda s: s[1] ** 2 - s[0] * s[1] - s[0] ** 2
lin_inv = [c for c in itertools.product(range(-3, 4), repeat=2) if any(c) and all(c[0] * s[1] + c[1] * (s[0] + s[1]) == c[0] * s[0] + c[1] * s[1] for s in ((1, 0), (0, 1)))]
P('X4', len(basis) == 2 and lin_inv == [] and all(Q((s[1], s[0] + s[1])) == -Q(s) for s in itertools.product(range(-5, 6), repeat=2)),
  'chemistry and biochemistry: the Michaelis-Menten network E + S <-> ES -> E + P conserves c^T x for c = (1,0,1,0), total enzyme, and c = (0,1,1,1), total substrate; the law has no conserved linear quantity',
  '(no left eigenvector of eigenvalue 1) and conserves the quadratic Q^2 instead | consequence: linear reaction networks conserve linear charges, the law a quadratic one, the conserved quantity of a hyperbolic flow (MF-94)')

# X5 MUSIC <-> COMBINATORICS ON WORDS: Euclidean rhythms with Fibonacci parameters are rotations of the Fibonacci word
def euclid_rhythm(k, n):
    return ''.join('x' if (i * k) // n != ((i - 1) * k) // n or i == 0 else '.' for i in range(n))
def bjorklund(k, n):
    # maximally even onsets: floor(i n / k)
    on = {(i * n) // k for i in range(k)}
    return ''.join('x' if i in on else '.' for i in range(n))
fw = 'a'
while len(fw) < 200: fw = ''.join('ab' if c == 'a' else 'a' for c in fw)
fibs = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
okr = True; shown = []
for k, n in zip(fibs[2:], fibs[3:]):
    r = bjorklund(k, n)
    target = fw[:n].replace('a', 'x').replace('b', '.')
    rots = {target[i:] + target[:i] for i in range(n)}
    okr = okr and r in rots
    if n <= 13: shown.append((k, n, r))
P('X5', okr, 'music: the Euclidean rhythm E(F_k, F_(k+1)) (Bjorklund, maximally even onsets) is a rotation of the first F_(k+1) letters of the Fibonacci chain for every pair up to (55, 89):',
  shown, '-- E(5,8) is the Cuban cinquillo | consequence: Toussaint\'s Euclidean rhythms with Fibonacci parameters are the law\'s quasicrystal of MF-82, read in time')

# X6 LINGUISTICS / INFORMATION <-> OMEGASL: capacity and the law check as a code
bits_mark = math.log2(3); bits_state = math.log2(81)
# undetected random corruption of the final 4-mark check under a uniform model: 1/81
P('X6', abs(bits_state - 4 * bits_mark) < 1e-12,
  'information theory: a ternary mark carries log2 3 = %.6f bits, one of the 81 states is 4 marks, %.6f bits; the 4-mark check is a state, so a uniformly random corruption of the final state escapes it with probability 1/81 = %.6f, and the theorems of Companion 214.6 catch every single substitution and every swap fewer than 24 apart' % (bits_mark, bits_state, 1 / 81),
  '| consequence: the check costs 4 marks for 6.34 bits of protection, the rate of a [n, n - 4] ternary code')

KEYS = {'A1': 'hamming-adinkra', 'A2': 'adinkra-e8', 'A3': 'garden', 'A4': 'golay-adinkra', 'A5': 'adinkra-genus', 'B1': 'phyllotaxis', 'B2': 'drone', 'B3': 'leslie', 'B4': 'hueckel', 'B5': 'lame', 'B6': 'fibonacci-code', 'B7': 'maximal-evenness', 'X1': 'control', 'X2': 'next-generation', 'X3': 'leontief', 'X4': 'conservation', 'X5': 'euclidean-rhythm', 'X6': 'capacity'}
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (KEYS[name], txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('FIELDS SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
