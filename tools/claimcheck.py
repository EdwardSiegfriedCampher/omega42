#!/usr/bin/env python3
"""claimcheck.py -- M323 Arithmetic Statement Check (EXACT; ADOPTED 23 October 2026 as a gate, Core Part 3.49; Companion Parts 93, 95 to 97).

A statement of generation ("one with one makes two", "two waves make a pattern") is not an identity: it is recorded by the
Relation-Generativity Register (APE-165) -- its objects, its operation, its kind (arithmetic, physical interaction, association),
its result, and its standing (an IDENTITY, checked here; a PHYSICAL RELATION; a STRUCTURAL ANALOGY; or an INTERPRETATION; APE-168)
-- and only its identities are checked. An argument that moves between multiplying, dividing, squaring and taking roots records each
step's operation, domain and inverse (the Inverse-Operation Audit, APE-168). An arithmetic statement brought into a reading, from a peer, a Striker or a public figure, is checked in every number system
the protocol uses before any reading of it is made: the integers Z, the reals R, Z/9Z (the residues), and Z[phi]/9 (the 81
states as a ring, in which the law is multiplication by phi, MATH-22). Its result is EXACT, whatever the frame (L-515: no
frame changes the arithmetic). What the statement's intuition may point to is a separate, typed reading.

    python3 tools/claimcheck.py "1*1=2"           # an identity with + or *, checked in Z, R, Z/9 and Z[phi]/9
    python3 tools/claimcheck.py --sqrt 2          # does a square root of n exist in R, Q, Z/7, Z/9 and Z[phi]/9?
    python3 tools/claimcheck.py --roots           # square roots that exist only in Z[phi]/9, and their voices
    python3 tools/claimcheck.py --polygons        # stated polygon angles: interior or exterior, and the polygon on the 24-wheel
    python3 tools/claimcheck.py --zero            # what zero does in the family
    python3 tools/claimcheck.py --pythagoras 3 4  # the Euclidean square sum beside the family's norm
    python3 tools/claimcheck.py --operation       # every operation x(*)y = a.xy + b(x+y) + c on Z/9 with 1(*)1 = 2: law, identity, isomorphism
    python3 tools/claimcheck.py --collapse        # a ring in which the identity 1 gives 1*1 = 2 has one element
    python3 tools/claimcheck.py --ring            # every multiplication distributing over the family's addition, with 1*1 = 2
    python3 tools/claimcheck.py --faces 6 5       # can F faces of k sides close into a polyhedron (Euler, degree >= 3)?
    python3 tools/claimcheck.py --selftest
Standard library only.
"""
import math, re, sys

S81 = [(a, b) for a in range(9) for b in range(9)]
def mul(x, y): a, b = x; c, d = y; return ((a * c + b * d) % 9, (a * d + b * c + b * d) % 9)
def add(x, y): return ((x[0] + y[0]) % 9, (x[1] + y[1]) % 9)
T = lambda s: (s[1], (s[0] + s[1]) % 9)
N = lambda s: (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9


def identity(text):
    m = re.fullmatch(r'\s*(-?\d+)\s*([*+x×])\s*(-?\d+)\s*=\s*(-?\d+)\s*', text)
    if not m: return 'M323: give an identity such as 1*1=2'
    a, op, b, c = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4)); times = op in '*x×'
    z = a * b if times else a + b
    r9 = (a * b) % 9 if times else (a + b) % 9
    ph = mul((a % 9, 0), (b % 9, 0)) if times else add((a % 9, 0), (b % 9, 0))
    L = ['M323 ARITHMETIC STATEMENT CHECK -- "%s" [EXACT]' % text.strip(),
         '  Z          %d %s %d = %d  -> %s' % (a, '*' if times else '+', b, z, 'HOLDS' if z == c else 'FAILS'),
         '  R          the same as Z for integers  -> %s' % ('HOLDS' if z == c else 'FAILS'),
         '  Z/9        %d  -> %s' % (r9, 'HOLDS' if r9 == c % 9 else 'FAILS'),
         '  Z[phi]/9   (%d, %d)  -> %s' % (ph[0], ph[1], 'HOLDS' if ph == (c % 9, 0) else 'FAILS')]
    if times and 1 in (a, b):
        L.append('  NOTE: 1 is the identity of every ring here; multiplying by it changes nothing, in every system and every frame')
    return '\n'.join(L)


def sqrt(n):
    sq9 = sorted({(x * x) % 9 for x in range(9)}); sq7 = sorted({(x * x) % 7 for x in range(7)})
    roots_phi = [s for s in S81 if mul(s, s) == (n % 9, 0)]
    L = ['M323 SQUARE ROOT CHECK -- does x^2 = %d have a solution? [EXACT]' % n,
         '  R          %s' % ('YES, x = %.10f%s' % (math.sqrt(n), ' (irrational)' if int(math.isqrt(n)) ** 2 != n else '') if n >= 0 else 'NO'),
         '  Q          %s' % ('YES' if n >= 0 and math.isqrt(n) ** 2 == n else 'NO'),
         '  Z/7        %s (squares mod 7: %s)' % ('YES' if n % 7 in sq7 else 'NO', sq7),
         '  Z/9        %s (squares mod 9: %s)' % ('YES' if n % 9 in sq9 else 'NO', sq9),
         '  Z[phi]/9   %s%s' % ('YES' if roots_phi else 'NO', (', the states %s' % roots_phi[:4]) if roots_phi else '')]
    return '\n'.join(L)


def zero():
    core = [s for s in S81 if s[0] % 3 == 0 and s[1] % 3 == 0]
    return '\n'.join(['M323 ZERO CHECK -- what zero does in the family [EXACT]',
                      '  the still point (0, 0) is the one state every power of the law fixes: %s' % all(T(T((0, 0))) == (0, 0) for _ in [0]),
                      '  the core squares to zero: s * s = 0 for all %d core states: %s' % (len(core), all(mul(s, s) == (0, 0) for s in core)),
                      '  3 * 3 = 0 in Z/9: %s; the residue 9 is 0, and the canonical pattern stands still at it (P7, P19)' % ((3 * 3) % 9 == 0),
                      '  without zero there is no still point, no ground and no nodal pair: the family cannot be written without it'])


def pythagoras(a, b):
    return '\n'.join(['M323 QUADRATIC FORMS -- (%d, %d) [EXACT]' % (a, b),
                      '  Euclidean  a^2 + b^2 = %d (the Pythagorean form, positive definite)' % (a * a + b * b),
                      '  the family a^2 + ab - b^2 = %d over Z, %d mod 9 (indefinite: N(0, 1) = -1; T sends N to -N, T^2 is a boost)' % (a * a + a * b - b * b, (a * a + a * b - b * b) % 9),
                      '  two forms on two geometries: the second does not refute the first; it is another geometry'])


def roots():
    """The square roots of the pure residues in Z[phi]/9: which exist only in the extension, and on which voice they lie."""
    import os
    sys.path[:0] = [os.path.dirname(os.path.abspath(__file__)), os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')]
    import manifestation as M
    sq9 = {(x * x) % 9 for x in range(9)}
    L = ['M323 ROOTS IN THE FAMILY -- x^2 = n for the residues n, solved in Z[phi]/9 [EXACT; noticed after computing, a post-selection property]']
    for n in range(9):
        r = [s for s in S81 if mul(s, s) == (n, 0)]
        tag = 'in Z/9 already' if n in sq9 else ('ONLY IN THE EXTENSION' if r else 'none')
        L.append('  n = %d  %-22s %s' % (n, tag, ', '.join('%s %s' % (s, M.classify(s)[2] or M.classify(s)[0]) for s in r) if r and n not in sq9 else ('%d roots' % len(r))))
    L.append('  the three roots the extension adds -- of 2, 5 and 8 -- lie one pair per voice; that follows from doubling: if r^2 = 2, then (2r)^2 = 8')
    L.append('  and (4r)^2 = 32 = 5, and doubling turns each voice into the next (FP-VoiceCosets)')
    units = [s for s in S81 if s[0] % 3 or s[1] % 3]
    L.append('  the coincidence: the root of 2 is +-(2, 5), the canonical seed and its antipode; %d of the %d units square to 2 (%.3f)' % (sum(1 for u in units if mul(u, u) == (2, 0)), len(units), sum(1 for u in units if mul(u, u) == (2, 0)) / len(units)))
    return '\n'.join(L)


R9 = range(9)
def _ops():
    """every operation x(*)y = (al.xy + be(x+y) + ga) mod 9 with 1(*)1 = 2 that is associative and has an identity, each with an
    explicit isomorphism to (Z/9, *) or (Z/9, +), verified on all 81 pairs"""
    out = []
    for al in R9:
        for be in R9:
            for ga in R9:
                op = lambda x, y, al=al, be=be, ga=ga: (al * x * y + be * (x + y) + ga) % 9
                if op(1, 1) != 2 or any(op(op(x, y), z) != op(x, op(y, z)) for x in R9 for y in R9 for z in R9): continue
                ids = [e for e in R9 if all(op(e, x) == x for x in R9)]
                if not ids: continue
                e = ids[0]; iso = None
                for u in (1, 2, 4, 5, 7, 8):
                    for v in R9:
                        f = [(u * x + v) % 9 for x in R9]
                        if iso is None and all(f[x * y % 9] == op(f[x], f[y]) for x in R9 for y in R9): iso = ('multiplication', 'x -> %dx%s' % (u, ' + %d' % v if v else ''), f)
                if iso is None:
                    f = [e]
                    for _ in range(8): f.append(op(f[-1], 1))
                    if sorted(f) == list(R9) and all(f[(x + y) % 9] == op(f[x], f[y]) for x in R9 for y in R9):
                        iso = ('addition', 'k -> 1(*)1(*)...(*)1, k times (1 generates all nine)', f)
                out.append((al, be, ga, e, iso))
    return out


def operation():
    rows = _ops()
    L = ['M323 OPERATION CHECK -- every operation x(*)y = a.xy + b(x+y) + c on Z/9 (729 of them) with 1(*)1 = 2 [EXACT]',
         '  associative, with an identity element: %d' % len(rows)]
    for al, be, ga, e, iso in rows:
        L.append('  x(*)y = %dxy + %d(x+y) + %d   identity %d   a copy of %s, by %s' % (al, be, ga, e, iso[0] if iso else 'NOTHING FOUND', iso[1] if iso else '-'))
    m = [r for r in rows if r[4] and r[4][0] == 'multiplication']; a = [r for r in rows if r[4] and r[4][0] == 'addition']
    L.append('  copies of multiplication: %d, identities %s (the class 2 mod 3); copies of addition: %d, identities %s (the core 3Z/9)' % (
        len(m), sorted(r[3] for r in m), len(a), sorted(r[3] for r in a)))
    L.append('  every one has an identity, and every one is an exact relabeling of x or +: 1(*)1 = 2 holds only because 1 is no longer the identity')
    L.append('  in Z[phi]/9 the same holds: x(*)y = 2xy has identity 5 = 1/2, and x -> 5x carries ordinary multiplication onto it')
    return '\n'.join(L)


def collapse():
    hit = [n for n in range(1, 82) if (1 * 1) % n == 2 % n]
    L = ['M323 COLLAPSE CHECK -- keep 1 as the identity and require 1*1 = 2 [EXACT]',
         '  then 1 = 1*1 = 2, so 1 = 2, so 0 = 1, and every x = x*1 = x*0 = 0',
         '  moduli n = 1..81 in which 1*1 = 2 holds in Z/n: %s -- only the ring with one element' % hit,
         '  in the family: the 81 states, 5 orbits, 3 voices, 24-cycle and T^24 = I all collapse to the single state (0, 0)',
         '  in the collapse the law T is the identity map, with period 1: the return to 1 coincides with the return to 0 (see --ring for relocation)']
    return '\n'.join(L)


def ring():
    """a multiplication that distributes over the family's addition is bi-additive, so x*y = xy.(1*1): it is fixed by c = 1*1"""
    L = ['M323 RING CHECK -- every multiplication on (Z/9, +) that distributes over the family\'s addition, with 1*1 = 2 [EXACT]',
         '  a distributive multiplication is bi-additive, so x*y = c.xy with c = 1*1; 1*1 = 2 fixes c = 2: x*y = 2xy, the only one']
    ok = all((2 * x * ((y + z) % 9)) % 9 == (2 * x * y + 2 * x * z) % 9 for x in R9 for y in R9 for z in R9)
    e = [u for u in R9 if all((2 * u * x) % 9 == x for x in R9)]
    iso = all((5 * ((x + y) % 9)) % 9 == (5 * x + 5 * y) % 9 and (5 * x * y) % 9 == (2 * (5 * x) * (5 * y)) % 9 for x in R9 for y in R9)
    L.append('  distributive: %s; identity %s; x -> 5x preserves both + and the product: %s -- a ring copy of Z/9' % ('YES' if ok else 'NO', e, 'YES' if iso else 'NO'))
    L.append('  the law T(a, b) = (b, a + b) uses only +, so it, the 81 states, the five orbits and the period 24 are untouched by the relabeling:')
    L.append('  the family survives relocation; it is lost only in the collapse, where the identity equals zero')
    tr = lambda x, y: min(x + y, 8)
    assoc = all(tr(tr(x, y), z) == tr(x, tr(y, z)) for x in R9 for y in R9 for z in R9)
    dist = all(tr(x, (y + z) % 9) == (tr(x, y) + tr(x, z)) % 9 for x in R9 for y in R9 for z in R9)
    units = [x for x in R9 if any(tr(x, y) == 0 for y in R9)]
    L.append('  outside rings, new structures exist: truncated addition x(*)y = min(x + y, 8) is associative (%s), has identity 0, gives 1(*)1 = %d,' % ('YES' if assoc else 'NO', tr(1, 1)))
    L.append('  and has %d unit (multiplication has 6, addition 9), so it is a copy of neither; it distributes over the family\'s addition: %s,' % (len(units), 'YES' if dist else 'NO'))
    L.append('  so it is not a multiplication of the family\'s ring; the law T, which uses only +, is unaffected by it')
    return '\n'.join(L)


def faces(F, k):
    E2 = F * k
    if E2 % 2: return 'M323 FACE CHECK -- %d faces of %d sides: %d edge-sides is odd, so they cannot all be shared in pairs [EXACT]' % (F, k, E2)
    E = E2 // 2; V = 2 - F + E
    ok = 2 * E >= 3 * V
    return '\n'.join(['M323 FACE CHECK -- can %d faces of %d sides close into a polyhedron? [EXACT]' % (F, k),
        '  every edge shared by two faces: E = %d; Euler V - E + F = 2 gives V = %d' % (E, V),
        '  each vertex meets at least three edges, so 2E >= 3V: %d >= %d -> %s' % (2 * E, 3 * V, 'POSSIBLE' if ok else 'IMPOSSIBLE'),
        ('  so a closed solid with exactly these faces cannot exist; an atlas rule must say which edges are shared, or that the faces are curved or open' if not ok else '  a closed solid is not excluded by this count')])


PATENT_ANGLES = ((3, 120, 'each equilateral triangle interior angle is one hundred and twenty degrees'),
                 (6, 60, 'the hexagon with sixty degree interior angles'),
                 (12, 30, 'a twelve-sided dodecahedron with thirty degree interior angles'),
                 (24, 15, 'a twenty-four sided icosikaitetragon with fifteen degree interior angles'))


def polygons(stated=PATENT_ANGLES):
    """M323 --polygons: a stated polygon angle checked against the interior angle 180(n - 2)/n and the exterior (turning)
    angle 360/n, and the polygon placed on the 24-position wheel: a regular n-gon is inscribed in it exactly when n divides
    24, as the rotations by 24/n steps, and it contains the 4D arm's rotation (+8 steps, 120 degrees) exactly when 3 divides n.
    The default statements are quoted from US 2015/0079872 A1 (T. Dashon Howard; granted as US 9,259,660 B2)."""
    L = ['M323 POLYGON CHECK -- stated angles against interior and exterior angles; the polygon on the 24-wheel [EXACT]']
    for n, ang, quote in stated:
        inner = 180 * (n - 2) / n; outer = 360 / n
        on = 24 % n == 0; steps = 24 // n if on else None
        L.append('  %2d sides, stated %3d deg ("%s")' % (n, ang, quote))
        L.append('      interior %.0f deg, exterior %.0f deg -> the stated angle is the %s | on the 24-wheel: %s%s' % (
            inner, outer, 'INTERIOR angle' if abs(ang - inner) < 1e-9 else ('EXTERIOR (turning) angle' if abs(ang - outer) < 1e-9 else 'neither'),
            ('YES, rotation by %d step%s (%d deg)' % (steps, '' if steps == 1 else 's', 15 * steps)) if on else 'NO',
            ('; contains the 4D arm (+8 steps, 120 deg)' if on and n % 3 == 0 else '')))
    L.append('  the n-gons on the 24-wheel are n = 1, 2, 3, 4, 6, 8, 12, 24; those with n a multiple of three -- 3, 6, 12, 24 -- are exactly')
    L.append('  the ones that contain the 4D arm\'s rotation by 8 steps; the angles stated are their turning angles, each 15 deg x 24/n')
    return '\n'.join(L)


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-76s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    i = identity('1*1=2')
    check('"1*1=2" fails in Z, R, Z/9 and Z[phi]/9', i.count('FAILS') == 4)
    check('"1+1=2" holds in all four', identity('1+1=2').count('HOLDS') == 4)
    check('"3*3=0" fails in Z and holds in Z/9 and Z[phi]/9', identity('3*3=0').count('HOLDS') == 2)
    s = sqrt(2)
    check('a square root of 2: in R yes (irrational), in Q no, in Z/7 yes, in Z/9 no', 'YES, x = 1.4142135624 (irrational)' in s and '  Q          NO' in s and 'Z/7        YES' in s and 'Z/9        NO' in s)
    check('the Fibonacci seed\'s first step: T(1, 1) = (1, 2)', T((1, 1)) == (1, 2))
    check('the law is multiplication by phi and moves every state but the still point', all(T(s) == mul((0, 1), s) for s in S81) and [s for s in S81 if T(s) == s] == [(0, 0)])
    check('the root of 2 in Z[phi]/9 is +-(2, 5), the canonical seed: (2 + 5 phi)^2 = 2', [s for s in S81 if mul(s, s) == (2, 0)] == [(2, 5), (7, 4)])
    check('the roots of 2, 5 and 8 exist only in the extension and lie one pair per voice', all(k in roots() for k in ('Voice A', 'Voice B', 'Voice C')))
    pg = polygons()
    check('the patent\'s four stated angles are the exterior angles, not the interior', pg.count('EXTERIOR (turning) angle') == 4 and 'INTERIOR angle' not in pg)
    check('the 3-, 6-, 12- and 24-gons sit on the 24-wheel and contain the 4D arm\'s rotation', pg.count('contains the 4D arm') == 4)
    o = _ops()
    check('six operations of the affine form give 1(*)1 = 2 with an identity; each is a verified copy of x or +', len(o) == 6 and all(r[4] for r in o))
    check('x(*)y = 2xy has identity 5 and x -> 5x is an isomorphism from ordinary multiplication', any(r[:4] == (2, 0, 0, 5) for r in o) and all((5 * (x * y)) % 9 == (2 * (5 * x) * (5 * y)) % 9 for x in R9 for y in R9))
    check('keeping 1 as the identity, 1*1 = 2 holds only in the one-element ring', 'only the ring with one element' in collapse() and '[1]' in collapse())
    rg = ring()
    check('on the family\'s addition, x*y = 2xy is the only distributive product with 1*1 = 2; identity 5; a ring copy of Z/9', 'identity [5]' in rg and 'preserves both + and the product: YES' in rg)
    check('truncated addition min(x+y, 8): associative, identity 0, 1(*)1 = 2, one unit, not distributive over the family\'s +', 'associative (YES)' in rg and 'has 1 unit' in rg and 'addition: NO' in rg)
    check('six pentagons cannot close into a polyhedron: E = 15, V = 11, 30 < 33', 'IMPOSSIBLE' in faces(6, 5) and 'POSSIBLE' in faces(12, 5) and 'IMPOSSIBLE' not in faces(12, 5))
    print('M323 SELFTEST: %s' % ('PASS' if ok else 'FAIL')); return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--sqrt': print(sqrt(int(a[1])))
    elif a[0] == '--zero': print(zero())
    elif a[0] == '--polygons': print(polygons())
    elif a[0] == '--operation': print(operation())
    elif a[0] == '--collapse': print(collapse())
    elif a[0] == '--ring': print(ring())
    elif a[0] == '--faces': print(faces(int(a[1]), int(a[2])))
    elif a[0] == '--roots': print(roots())
    elif a[0] == '--pythagoras': print(pythagoras(int(a[1]), int(a[2])))
    else: print(identity(' '.join(a)))
