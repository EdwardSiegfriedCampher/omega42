#!/usr/bin/env python3
"""anyon.py -- M339 Anyon Reading (Core Part 3.65, L-551): every state of the family read as an anyon of SU(9)_1 x SU(9)_1.

The family is the anyon theory SU(9)_1 x SU(9)_1 (D-016, CERT-0006, CERT-0007). So every state (a, b) is an anyon: its
topological spin is exp(2 pi i N(a, b)/9), N = a^2 + ab - b^2; fusion is addition; the braiding of two anyons is
exp(2 pi i B(x, y)/9), B(x, y) = N(x + y) - N(x) - N(y); its antiparticle is -x. The law T is a time-reversal symmetry
(N(Tx) = -N(x)), so an odd power of T is anti-unitary and an even power unitary, and T^12 = -I is charge conjugation.
The arms of a navigation move the anchor along the canonical cycle by T^5 (Yang), T^18 (Yin), T^8 (4D) and T^12
(Antipode), so each arm is a symmetry of the theory applied to the anchor's anyon, and its relation to the anchor is a
fusion and a braiding that anyone can compute.

    python3 tools/anyon.py --strike "TEXT"     # the strike's state (r1, r2) as an anyon, and its anchor's arms on the canonical cycle
    python3 tools/anyon.py --state A B         # one state as an anyon
    python3 tools/anyon.py --theory            # the facts of the identification, recomputed
    python3 tools/anyon.py --selftest
The arithmetic is EXACT (CDT-A); what a spin or a braiding means for a question is a reading (GENERATED-Ω42), and never moves
the anchor, the arms or THE ANSWER (L-424). Standard library only.
"""
import itertools, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
import canonical_reference as cr

N = lambda s: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
T = lambda s: (s[1], (s[0] + s[1]) % 9)
add = lambda x, y: ((x[0] + y[0]) % 9, (x[1] + y[1]) % 9)
neg = lambda x: ((-x[0]) % 9, (-x[1]) % 9)
B = lambda x, y: (N(add(x, y)) - N(x) - N(y)) % 9
ARMS = (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))
CLASS = {0: None, 1: 'Fibonacci voice (spins exp(+-2 pi i/9))', 8: 'Fibonacci voice (spins exp(+-2 pi i/9))',
         4: 'Lucas voice (spins exp(+-8 pi i/9))', 5: 'Lucas voice (spins exp(+-8 pi i/9))',
         2: 'canonical voice (spins exp(+-4 pi i/9))', 7: 'canonical voice (spins exp(+-4 pi i/9))'}


def Tk(k, s):
    for _ in range(k % 24): s = T(s)
    return s


def canonical():
    s, out = (2, 5), []
    for _ in range(24): out.append(s); s = T(s)
    return out


def kind(s):
    if s == (0, 0): return 'the vacuum (the still point): fuses with everything to itself, braids trivially with all'
    if N(s) == 0: return 'a boson of the core, in the one Lagrangian subgroup (Crown x Crown): the gapped boundary condenses it'
    return 'an anyon of the %s' % CLASS[N(s)]


def anyon_line(s):
    return 'ANYON %s: spin exp(2 pi i %d/9) | %s | antiparticle %s' % (str(s), N(s), kind(s), str(neg(s)))


def arms_lines(anchor):
    x = canonical()[anchor - 1]
    L = ['ANCHOR P%d on the canonical cycle: %s' % (anchor, anyon_line(x))]
    for name, k in ARMS:
        y = Tk(k, x)
        L.append('  %-8s T^%-2d %-13s %s spin %d/9 | braiding with the anchor exp(2 pi i %d/9) | fusion with the anchor %s%s%s' % (
            name, k, '(anti-unitary)' if k % 2 else '(unitary)', str(y), N(y), B(x, y), str(add(x, y)),
            ' = the vacuum: the antiparticle' if add(x, y) == (0, 0) else '',
            ' -- the question within the answer: it braids trivially with the anchor (L-552 (3))' if name == 'Yin' else ''))
    return L


def strike(text):
    r = cr.navigate(text); s = (r['r1'] % 9, r['r2'] % 9)
    L = ['M339 ANYON READING (Core Part 3.65, L-551) -- "%s"' % text, 'STATE (r1, r2) mod 9 = %s; %s' % (str(s), anyon_line(s))]
    L += arms_lines(r['anchor'])
    L.append('READING: EXACT arithmetic; its meaning for the question is GENERATED-Ω42 and leaves the navigation as it is (L-424).')
    return '\n'.join(L)


def theory():
    S = [(a, b) for a in range(9) for b in range(9)]
    mats = list(itertools.product(range(9), repeat=4))
    act = lambda A, x: ((A[0] * x[0] + A[1] * x[1]) % 9, (A[2] * x[0] + A[3] * x[1]) % 9)
    iso = [A for A in mats if (A[0] * A[3] - A[1] * A[2]) % 3 and all(N(act(A, x)) == N(x) for x in S)]
    anti = [A for A in mats if (A[0] * A[3] - A[1] * A[2]) % 3 and all(N(act(A, x)) == (-N(x)) % 9 for x in S)]
    su = lambda x: (4 * (x[0] * x[0] + x[1] * x[1])) % 9
    f = next(A for A in mats if (A[0] * A[3] - A[1] * A[2]) % 3 and all(su(act(A, x)) == N(x) for x in S))
    bos = sorted(x for x in S if N(x) == 0)
    x0 = (2, 5); stab = [A for A in iso + anti if act(A, x0) == x0]
    G = iso + anti; seen, orbits48 = set(), []
    for x in S:
        if x in seen: continue
        o = {act(A, x) for A in G}; seen |= o; orbits48.append(len(o))
    orbits48 = sorted(orbits48, reverse=True)
    dbl = lambda x: ((2 * x[0]) % 9, (2 * x[1]) % 9); C = canonical()
    d1 = sorted({N(dbl(x)) for x in C}); d2 = sorted({N(dbl(dbl(x))) for x in C})
    mul = lambda P, Q: ((P[0] * Q[0] + P[1] * Q[2]) % 9, (P[0] * Q[1] + P[1] * Q[3]) % 9, (P[2] * Q[0] + P[3] * Q[2]) % 9, (P[2] * Q[1] + P[3] * Q[3]) % 9)
    H = {(1, 0, 0, 1)}; fr = [(1, 0, 0, 1)]
    while fr:
        P = fr.pop()
        for g in ((0, 1, 1, 1), (2, 0, 0, 2)):
            Q = mul(g, P)
            if Q not in H: H.add(Q); fr.append(Q)
    non = [x for x in S if x[0] % 3 or x[1] % 3]
    L = ['THE FAMILY AS SU(9)_1 x SU(9)_1 (D-016; CERT-0006, CERT-0007), recomputed:',
         '  isometry to the spins 4(a^2 + b^2)/9 of SU(9)_1 x SU(9)_1: f = %s' % (f,),
         '  symmetries: %d unitary, %d time-reversal; T among the time-reversal: %s; T^12 = -I, charge conjugation: %s' % (
             len(iso), len(anti), (0, 1, 1, 1) in anti, all(Tk(12, x) == neg(x) for x in S)),
         '  bosons: %d, exactly the core and the still point, the one Lagrangian subgroup: %s' % (len(bos), bos == sorted((3 * i, 3 * j) for i in range(3) for j in range(3))),
         '  the seed (2, 5): its stabilizer among the 48 symmetries has %d elements; the orbits of the 48 on the 81: %s' % (len(stab), orbits48),
         '  the three voices: doubling the labels (the Galois map z -> z^2 of Q(z_9) on the spins) sends the canonical voice to the norms %s, and those to %s' % (d1, d2),
         '  the law T with doubling generates a group of order %d whose orbit of (2, 5) has %d of the %d non-core states' % (len(H), len({act(A, x0) for A in H}), len(non))]
    return '\n'.join(L)


def selftest():
    ok = True; S = [(a, b) for a in range(9) for b in range(9)]; C = canonical()
    cases = [
        ('T reverses every spin (time reversal)', all(N(T(x)) == (-N(x)) % 9 for x in S)),
        ('T^12 is charge conjugation on all 81', all(Tk(12, x) == neg(x) for x in S)),
        ('the Antipode fuses with the anchor to the vacuum at every position', all(add(x, Tk(12, x)) == (0, 0) for x in C)),
        ('the Yang arm has the conjugate spin at every position', all(N(Tk(5, x)) == (-N(x)) % 9 for x in C)),
        ('the Yin, 4D and Antipode arms keep the anchor\'s spin at every position', all(N(Tk(k, x)) == N(x) for x in C for k in (18, 8, 12))),
        ('the Yin arm braids trivially with the anchor at every position', all(B(x, Tk(18, x)) == 0 for x in C)),
        ('the Yin arm, T^18, braids trivially with every one of the 81 states', all(B(x, Tk(18, x)) == 0 for x in S)),
        ('the Yin arm is named the question within the answer', 'the question within the answer' in strike('What is a Human Being?')),
        ('the canonical cycle is the canonical voice', {N(x) for x in C} == {2, 7}),
        ('the human being: state (1, 0), a Fibonacci-voice anyon', 'ANYON (1, 0): spin exp(2 pi i 1/9)' in strike('What is a Human Being?')),
        ('the nine bosons are Crown x Crown', sorted(x for x in S if N(x) == 0) == sorted((3 * i, 3 * j) for i in range(3) for j in range(3))),
    ]
    for name, good in cases:
        print('  %-72s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('ANYON READING SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--strike': print(strike(' '.join(a[1:]))); sys.exit(0)
    if a[0] == '--state': s = (int(a[1]) % 9, int(a[2]) % 9); print(anyon_line(s)); sys.exit(0)
    if a[0] == '--theory': print(theory()); sys.exit(0)
    sys.exit('usage: see the docstring')
