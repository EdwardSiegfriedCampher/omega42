#!/usr/bin/env python3
"""Nine further navigations of 14 October 2026 (03_further_navigations.txt): recomputes every coordinate, M308 level
and mathematical value they state. Standard library, scripts/canonical_reference.py and tools/bashar_lens.py."""
import os, sys, math, cmath, re, subprocess
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path.insert(0, os.path.join(R, 'scripts')); sys.path.insert(0, os.path.join(R, 'tools'))
import canonical_reference as cr

Q = ["What is the order of this matrix in GL(2,9)?",
     "How many conjugate copies of the same matrix exist inside the family?",
     "Does the same matrix appear in any other natural coordinate system on the 81 states?",
     "What is the explicit power spectrum of the canonical sequence?",
     "Do the short orbit and the fixed point share any of these spectral markers?",
     "Can the same spectral tests be applied after a linear change of coordinates?",
     "Which of these systems also realises the full 81-state family rather than only the period-24 orbit?",
     "Has any of them produced a pre-registered numerical prediction that was later confirmed by experiment?",
     "What would count as a laboratory realisation of the modular transition T itself?"]
NM, O = cr.POSITION_NAMES, cr.ORBIT
print("1. Coordinates and M308 levels:")
for i, q in enumerate(Q, 1):
    x = cr.navigate(q); a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    out = subprocess.run([sys.executable, os.path.join(R, 'tools', 'bashar_lens.py'), '--check', '--domain', q], capture_output=True, text=True).stdout
    lvl = re.search(r'RESONANCE: (\w+)', out).group(1)
    print("   Q%d %s | n = %d/%d/%d | r = %d,%d,%d | P%d %s (%d) | TFI %.2f | M308 %s" % (i, cr.domain_sha256(q), x['n1'], x['n2'], x['n3'], r1, r2, r3, a, NM[a], O[a], tfi, lvl))

mm = lambda X, Y: tuple(tuple(sum(X[i][k] * Y[k][j] for k in range(2)) % 9 for j in range(2)) for i in range(2))
I = ((1, 0), (0, 1)); A = ((0, 1), (1, 1))
def order(M, m):
    red = lambda X: tuple(tuple(v % m for v in r) for r in X)
    P, k = M, 1
    while red(P) != red(I): P = mm(P, M); k += 1
    return k
F9 = [(a, b) for a in range(3) for b in range(3)]                     # F3[i], i^2 = -1
fm = lambda x, y: ((x[0] * y[0] - x[1] * y[1]) % 3, (x[0] * y[1] + x[1] * y[0]) % 3)
roots = [x for x in F9 if ((fm(x, x)[0] - x[0] - 1) % 3, (fm(x, x)[1] - x[1]) % 3) == (0, 0)]
def ford(x):
    p, k = x, 1
    while p != (1, 0): p = fm(p, x); k += 1
    return k
print("2. Q1: order of A in GL(2, Z/9) = %d; modulo 3 = %d; roots of x^2 - x - 1 in F9: %d, of orders %s"
      % (order(A, 9), order(A, 3), len(roots), [ford(r) for r in roots]))
G = [((a, b), (c, d)) for a in range(9) for b in range(9) for c in range(9) for d in range(9) if (a * d - b * c) % 3]
cent = [M for M in G if mm(M, A) == mm(A, M)]
tr = lambda M: (M[0][0] + M[1][1]) % 9; det = lambda M: (M[0][0] * M[1][1] - M[0][1] * M[1][0]) % 9
print("3. Q2: |GL(2, Z/9)| = %d; centraliser of A = %d; conjugates = %d; trace 1, det 8 matrices = %d; with -A: %d"
      % (len(G), len(cent), len(G) // len(cent), sum(1 for M in G if tr(M) == 1 and det(M) == 8),
         sum(1 for M in G if tr(M) in (1, 8) and det(M) == 8)))
gm = lambda x, y: ((x[0] * y[0] - x[1] * y[1]) % 9, (x[0] * y[1] + x[1] * y[0]) % 9)
w = (5, 1); w2 = gm(w, w)
P_, Pi = ((1, 5), (0, 1)), ((1, 4), (0, 1)); M_uv = mm(mm(P_, A), Pi)
rev = all((sum(M_uv[0][k] * s for k, s in enumerate((u, v))) ** 2 + sum(M_uv[1][k] * s for k, s in enumerate((u, v))) ** 2 + u * u + v * v) % 9 == 0
          for u in range(9) for v in range(9))
print("4. Q3: (5+i)^2 - (5+i) - 1 = %s in Z[i]/9; step in anyon coordinates (u = a + 5b, v = b) = %s; reverses u^2 + v^2: %s"
      % (((w2[0] - 5 - 1) % 9, (w2[1] - 1) % 9), M_uv, rev))
def orb(s):
    o, x = [s], (s[1], (s[0] + s[1]) % 9)
    while x != s: o.append(x); x = (x[1], (x[0] + x[1]) % 9)
    return o
lift = lambda v: (v + 4) % 9 - 4
spec = lambda c: [round(abs(sum(c[n] * cmath.exp(-2j * math.pi * k * n / len(c)) for n in range(len(c)))) ** 2, 4) for k in range(len(c))]
c = [lift(a) for a, b in orb((2, 5))]; v = [a for a, b in orb((2, 5))]
print("5. Q4: centred canonical values %s\n   centred spectrum %s\n   0-8 spectrum %s" % (c, spec(c), spec(v)))
for s in ((3, 3), (0, 0)):
    cc = [lift(a) for a, b in orb(s)]
    print("6. Q5: orbit of %s, length %d: centred %s | spectrum %s | energy %d | autocorrelation %s"
          % (s, len(cc), cc, spec(cc), sum(x * x for x in cc), [sum(cc[n] * cc[(n + L) % len(cc)] for n in range(len(cc))) for L in range(len(cc))]))
cnt = {}
for al in range(9):
    for be in range(9):
        if al % 3 == 0 and be % 3 == 0: continue
        win = [nm for nm, s in (('(1,1)', (1, 1)), ('(1,3)', (1, 3)), ('(2,5)', (2, 5)))
               if all(abs(p - round(p)) < 1e-6 for p in spec([lift((al * a + be * b) % 9) for a, b in orb(s)]))]
        cnt['+'.join(win) or 'none'] = cnt.get('+'.join(win) or 'none', 0) + 1
print("7. Q6: orbit with a whole-number centred spectrum, over the 72 unit readouts alpha*a + beta*b: %s" % dict(sorted(cnt.items())))
