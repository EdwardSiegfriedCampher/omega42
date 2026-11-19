# ===== ground_challenge.py BEGIN =====
#!/usr/bin/env python3
"""ground_challenge.py -- the Alternative Ground Challenge and the Reconstruction Programme (Companion Part 37).

Computes, from definitions only, the structural profile of candidate grounds and compares them
with the Omega42 ground, Fibonacci modulo 9. Every figure is computed; nothing is scored by
judgment. The results are mathematical statements: a Navigator verifies them by running this
script, and a peer verifies them the same way (Core Part 6.3).

Usage:
    python3 ground_challenge.py            full report
    python3 ground_challenge.py --test     assert every reported result; prints PASS or FAIL
    python3 ground_challenge.py --arms A   M267-GROUND arm values for anchor index A (1-9, Core Part 2)
    python3 ground_challenge.py --reconstruction   R1-R8 reconstruction properties on all four grounds
    python3 ground_challenge.py --r6 A     the three R6 conditions for anchor index A
    python3 ground_challenge.py --m274 v1,...,v24          M274 Coordinate Integrity Check
    python3 ground_challenge.py --m275 A anchor,yang,yin,4d,antipode   M275 Arm Consistency Check
    python3 ground_challenge.py --m276 x0,x1,x2,x3         M276 Law Witness
    python3 ground_challenge.py --m277 a,b                 M277 Orbit Witness
"""
import sys
from math import gcd, lgamma, log, log2
from itertools import product, permutations

# ------------------------------------------------------------------ primitives
def orbits(states, f):
    seen, out = set(), []
    for s in states:
        if s in seen:
            continue
        path, x = [], s
        while x not in seen and x not in path:
            path.append(x); x = f(x)
        if x in path:
            out.append(path[path.index(x):])
        seen.update(path)
    return out

def is_bijection(states, f):
    return len({f(s) for s in states}) == len(states)

def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]

def pisano(m):
    a, b, n = 0, 1, 0
    while True:
        a, b = b, (a + b) % m; n += 1
        if (a, b) == (0, 1):
            return n

def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def linrec(m, p=1, q=1):
    """x(n+1) = p x(n) + q x(n-1) (mod m), acting on pairs (x(n-1), x(n))."""
    S = list(product(range(m), repeat=2))
    return S, (lambda s: (s[1], (p * s[1] + q * s[0]) % m))

def fib_norm(s):
    a, b = s
    return a * a + a * b - b * b

# ------------------------------------------------------------------ profile of a Fibonacci-type ground
def profile(m, p=1, q=1):
    S, f = linrec(m, p, q)
    orb = orbits(S, f)
    P = max(len(o) for o in orb)
    long = [o for o in orb if len(o) == P]
    cover = [len({s[1] for s in o}) == m for o in long]
    anti = [P % 2 == 0 and all((o[(i + P // 2) % P][1] + o[i][1]) % m == 0 for i in range(P)) for o in long]
    classes = [{frozenset({fib_norm(s) % m, -fib_norm(s) % m}) for s in o} for o in long]
    separates = (len(long) > 1 and all(len(c) == 1 for c in classes)
                 and len({next(iter(c)) for c in classes}) == len(long)) if (p, q) == (1, 1) else None
    return dict(m=m, states=m * m, reversible=is_bijection(S, f),
                orbit_lengths=sorted(len(o) for o in orb), period=P, long_orbits=len(long),
                all_long_cover=all(cover), long_covering=sum(cover),
                all_long_antipode=all(anti), long_antipode=sum(anti),
                invariant_separates=separates,
                period_closure=(pisano(m) == P and pisano(P) == P) if (p, q) == (1, 1) else None,
                divisors_of_period=len(divisors(P)))

# The six yield properties (G10-C). DECLARED AFTER the first computation of this challenge, and
# therefore DIAGNOSTIC for the candidates below; frozen from this revision for any new candidate.
YIELD = ('reversible', 'period_closure', 'multiple_long', 'all_long_cover', 'all_long_antipode',
         'invariant_separates')

def yield_vector(r):
    v = dict(reversible=r['reversible'], period_closure=r['period_closure'],
             multiple_long=r['long_orbits'] > 1, all_long_cover=r['all_long_cover'],
             all_long_antipode=r['all_long_antipode'],
             invariant_separates=r['invariant_separates'] if r['long_orbits'] > 1 else None)
    return v

# ------------------------------------------------------------------ completeness of the period-24 list
def period24_moduli():
    """pi(m) divides 24  <=>  T^24 = I (mod m)  <=>  m | gcd(F23 - 1, F24, F25 - 1).
    So every modulus with period 24 divides that gcd, and the list below is exhaustive."""
    g = gcd(gcd(fib(23) - 1, fib(24)), fib(25) - 1)
    return g, [d for d in divisors(g) if d > 1 and pisano(d) == 24]

# ------------------------------------------------------------------ GL(2, Z/9): ceiling and conjugacy
def mat_mul(A, B, m):
    return ((A[0] * B[0] + A[1] * B[2]) % m, (A[0] * B[1] + A[1] * B[3]) % m,
            (A[2] * B[0] + A[3] * B[2]) % m, (A[2] * B[1] + A[3] * B[3]) % m)

def mat_order(A, m):
    I, X, k = (1, 0, 0, 1), A, 1
    while X != I:
        X = mat_mul(X, A, m); k += 1
    return k

def mat_orbit_lengths(A, m):
    S = list(product(range(m), repeat=2))
    f = lambda v: ((A[0] * v[0] + A[1] * v[1]) % m, (A[2] * v[0] + A[3] * v[1]) % m)
    return sorted(len(o) for o in orbits(S, f))

def gl2_study(m=9):
    """Every invertible 2x2 matrix mod 9: the ceiling on element order, and the classes of cyclic
    subgroups of order 24 under conjugation (a change of coordinates). Two linear grounds are the
    same ground in different coordinates exactly when their subgroups are conjugate."""
    G = [A for A in product(range(m), repeat=4) if gcd((A[0] * A[3] - A[1] * A[2]) % m, m) == 1]
    inv = {}
    for A in G:
        for B in G:
            if mat_mul(A, B, m) == (1, 0, 0, 1):
                inv[A] = B; break
    orders = {A: mat_order(A, m) for A in G}
    o24 = [A for A in G if orders[A] == 24]
    same = [A for A in o24 if mat_orbit_lengths(A, m) == [1, 8, 24, 24, 24]]
    subs = set()
    for A in o24:
        X, S = A, set()
        for _ in range(24):
            S.add(X); X = mat_mul(X, A, m)
        subs.add(frozenset(S))
    classes, left = [], set(subs)
    while left:
        s = left.pop()
        c = {frozenset(mat_mul(mat_mul(g, x, m), inv[g], m) for x in s) for g in G}
        left -= c; classes.append(c)
    T = (0, 1, 1, 1)                                   # (a, b) -> (b, a + b), the transition T
    t_class = next(i for i, c in enumerate(classes) if any(T in s for s in c))
    def class_of(A):
        return next(i for i, c in enumerate(classes) if any(A in s for s in c))
    _, match = recurrences_mod9()
    rec = {}
    for x in match:
        p, q = x[0]
        rec.setdefault(class_of((0, 1, q, p)), []).append((x[5], x[0]))
    order = [t_class] + [i for i in range(len(classes)) if i != t_class]
    return dict(group_order=len(G), max_order=max(orders.values()), order24=len(o24),
                same_architecture=len(same), subgroups24=len(subs),
                subgroup_classes=[len(classes[i]) for i in order],
                recurrences_by_class=[sorted(rec.get(i, [])) for i in order])

# ------------------------------------------------------------------ designed (non-linear) rivals
def designed_rival_bits():
    """Permutations of the 81 states with the Omega42 cycle type (24, 24, 24, 8, 1):
    81! / (24^3 * 3! * 8 * 1). Bits needed to single one out, against the bits that name
    the Fibonacci rule inside the 2x2 recurrences mod 9 (81 coefficient pairs)."""
    ln = lgamma(82) - (3 * log(24) + log(6) + log(8))
    return ln / log(2), log2(81)

# ------------------------------------------------------------------ other candidate classes
def tribonacci(m):
    S = list(product(range(m), repeat=3))
    f = lambda s: (s[1], s[2], (s[0] + s[1] + s[2]) % m)
    return dict(states=len(S), reversible=is_bijection(S, f),
                cycle_lengths=sorted({len(o) for o in orbits(S, f)}))

def eca(rule, N):
    S = list(range(2 ** N))
    def f(x):
        y = 0
        for i in range(N):
            l, c, r = (x >> ((i + 1) % N)) & 1, (x >> i) & 1, (x >> ((i - 1) % N)) & 1
            y |= ((rule >> (l * 4 + c * 2 + r)) & 1) << i
        return y
    orb = orbits(S, f)
    return dict(states=len(S), reversible=is_bijection(S, f), states_on_cycles=sum(len(o) for o in orb),
                cycle_lengths=sorted({len(o) for o in orb}))

def s4_max_order():
    def order(p):
        k, q = 1, p
        while q != tuple(range(4)):
            q = tuple(p[i] for i in q); k += 1
        return k
    return max(order(p) for p in permutations(range(4)))

def recurrences_mod9():
    rows = []
    for p in range(9):
        for q in range(9):
            if gcd(q, 9) != 1:
                continue
            r = profile(9, p, q)
            size = min(p, 9 - p) + min(q, 9 - q)
            rows.append(((p, q), r['period'], r['orbit_lengths'], r['all_long_cover'], r['all_long_antipode'], size))
    match = [x for x in rows if x[1] == 24 and x[2] == [1, 8, 24, 24, 24] and x[3] and x[4]]
    return rows, match

# ------------------------------------------------------------------ complexity budget (G10)
def budget(m):
    r = profile(m)
    readings = r['long_orbits'] * r['period']        # candidate readings (orbit, starting state)
    v = yield_vector(r)
    return dict(m=m, G10A_declarations=3 if r['long_orbits'] > 1 else 2,   # modulus, rule, (orbit) + start
                G10B_selection_bits=round(log2(readings), 2),
                G10C_yield=sum(1 for k in YIELD if v[k]), G10C_applicable=sum(1 for k in YIELD if v[k] is not None),
                G10D_description_bits=round(log2(m) + log2(m * m) + log2(readings), 2))


# ------------------------------------------------------------------ reconstruction programme (Companion 37 B)
# The Omega42 Reconstruction Code C(m): the set of all P-term sequences x(0..P-1) obeying
# x(n+2) = x(n+1) + x(n) (mod m). It is a free Z/m-module of rank 2 inside (Z/m)^P, one codeword
# for each of the m*m starting states. Z/9 is a ring, not the field GF(9); every statement below
# uses only subtraction of codewords, which the module allows.

def codewords(m):
    P = pisano(m)
    out = {}
    for s in product(range(m), repeat=2):
        seq, x = [], s
        for _ in range(P):
            seq.append(x[0]); x = (x[1], (x[0] + x[1]) % m)
        out[s] = tuple(seq)
    return P, out

def r1_threshold(m):
    """R1/R2: any k positions determine the codeword iff k exceeds the most zeros a nonzero
    codeword has (two codewords agreeing on k places differ by a codeword with k zeros)."""
    P, C = codewords(m)
    zmax, witness = 0, None
    for s, w in C.items():
        if s == (0, 0): continue
        z = [i for i, v in enumerate(w) if v == 0]
        if len(z) > zmax:
            zmax, witness = len(z), (s, z)
    return P, zmax, zmax + 1, witness

def r2_profile(m):
    """R2/R5: for each separation d, how many of the long-orbit states the pair of values at
    (n, n+d) singles out, with F(d) mod m and gcd(d, P). Reconstruction is complete iff F(d) is a
    unit mod m, because x(n+d) = F(d-1) x(n) + F(d) x(n+1)."""
    P, C = codewords(m)
    S, f = linrec(m)
    long = [s for o in orbits(S, f) if len(o) == P for s in o]
    rows = []
    for d in range(1, P):
        pairs = {(C[s][0], C[s][d]) for s in long}
        rows.append((d, len(pairs), len(long), fib(d) % m, gcd(fib(d), m) == 1, gcd(d, P)))
    return P, rows

def r3_law_recovery(m):
    """R3: four consecutive values fix the recurrence among all m*m laws x+ = p x + q x- iff
    x1^2 - x0 x2 (= -N(x0, x1)) is a unit mod m."""
    S, _ = linrec(m)
    uniq, unit, agree = 0, 0, True
    for s in S:
        x0, x1 = s; x2 = (x0 + x1) % m; x3 = (x1 + x2) % m
        n = sum(1 for p in range(m) for q in range(m) if (p * x1 + q * x0) % m == x2 and (p * x2 + q * x1) % m == x3)
        u = gcd(fib_norm(s) % m, m) == 1
        uniq += n == 1; unit += u; agree &= (n == 1) == u
    return len(S), uniq, unit, agree

def r4_class_labels(m=9):
    S, f = linrec(m)
    return [(len(o), sorted({min(fib_norm(s) % m, -fib_norm(s) % m) for s in o})) for o in orbits(S, f)]

def arm_information():
    """Phases (of 24) singled out on the canonical orbit by the anchor value plus one arm value."""
    P, C = codewords(9)
    w = C[(2, 5)]
    return {name: len({(w[n], w[(n + k) % 24]) for n in range(24)})
            for name, k in (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))}

def reconstruction_report():
    print('== Omega42 Reconstruction Code: free Z/m-module of rank 2, length = period')
    for m in (9, 6, 10, 16):
        P, z, k, wit = r1_threshold(m)
        print('R1/R2 mod %-2d length %-2d: any %d positions determine the codeword (%.1f%%); %d can fail: codewords of %s and (0,0) agree on %s'
              % (m, P, k, 100.0 * k / P, z, wit[0], wit[1]))
    for m in (9, 6, 10, 16):
        P, rows = r2_profile(m)
        good = [r[0] for r in rows if r[1] == r[2]]
        print('R2 mod %-2d: complete two-point separations %d of %d; F(d) unit exactly there: %s'
              % (m, len(good), P - 1, all((r[1] == r[2]) == r[4] for r in rows)))
    P, rows = r2_profile(9)
    print('R5 reconstruction profile mod 9 (d: states singled out of 72, F(d) mod 9, gcd(d,24)):')
    print('   ' + ' | '.join('%d:%d,%d,%d' % (r[0], r[1], r[3], r[5]) for r in rows))
    for m in (9, 6, 10, 16):
        n, uniq, unit, agree = r3_law_recovery(m)
        print('R3 mod %-2d: law recovered on %d of %d states (%.1f%%); exactly the states whose norm is a unit: %s'
              % (m, uniq, n, 100.0 * uniq / n, agree))
    print('R4 orbit labels from one local step, mod 9 (length: norm class):', r4_class_labels())
    print('Arm information on the canonical orbit (phases singled out by anchor + arm, of 24):', arm_information())


# ------------------------------------------------------------------ R3 theorem, self-checking substrate, multiplicity balance, R6 apparatus
def r3_theorem(m):
    """Theorem (all m): four consecutive values fix (p, q) uniquely iff det [[x1, x0], [x2, x1]]
    = x1^2 - x0 x2 = -N(x0, x1) is a unit mod m. A square system over a commutative ring has a
    unique solution for every right-hand side iff its determinant is a unit; here a solution (the
    true law) always exists, so a non-unit determinant leaves at least two. Checked exhaustively."""
    S, _ = linrec(m)
    for x0, x1 in S:
        x2 = (x0 + x1) % m; x3 = (x1 + x2) % m
        n = sum(1 for p in range(m) for q in range(m) if (p * x1 + q * x0) % m == x2 and (p * x2 + q * x1) % m == x3)
        det = (x1 * x1 - x0 * x2) % m
        if det != (-fib_norm((x0, x1))) % m or (n == 1) != (gcd(det, m) == 1) or n < 1:
            return False
    return True

def hamming(a, b):
    return sum(1 for x, y in zip(a, b) if x != y)

def self_check(m, trials=4000, seed=42):
    """Minimum distance d of the Reconstruction Code; a full coordinate with up to d-1 wrong values
    is always detected, and with up to floor((d-1)/2) is corrected by the nearest codeword. A
    seeded random test confirms correction at the radius; an explicit word at radius + 1 is
    equidistant from two codewords."""
    import random
    P, C = codewords(m)
    words = list(C.values())
    zero = C[(0, 0)]
    d = min(hamming(w, zero) for s, w in C.items() if s != (0, 0))
    t = (d - 1) // 2
    rng = random.Random(seed)
    ok = True
    for _ in range(trials):
        c = rng.choice(words)
        pos = rng.sample(range(P), t)
        w = list(c)
        for i in pos:
            w[i] = (w[i] + rng.randrange(1, m)) % m
        best = min(words, key=lambda x: hamming(x, w))
        if best != c or sum(1 for x in words if hamming(x, w) == hamming(best, w)) != 1:
            ok = False; break
    far = next(w for s, w in C.items() if s != (0, 0) and hamming(w, zero) == d)
    nz = [i for i, v in enumerate(far) if v][: t + 1]
    mid = [far[i] if i in nz else 0 for i in range(P)]
    tie = hamming(mid, zero) == hamming(mid, far) == t + 1
    return dict(m=m, length=P, min_distance=d, detects=d - 1, corrects=t,
                corrects_fraction=round(t / P, 3), random_correction_ok=ok, tie_at_radius_plus_1=tie)

def multiplicity_balance(m=9):
    """Bits paid at selection for having k long orbits (log2 k, against a one-orbit ground of the
    same period) and bits a single state returns locally through the norm class (R4)."""
    long, _ = [o for o in orbits(*linrec(m)) if len(o) == pisano(m)], None
    k = len(long)
    labels = {frozenset({fib_norm(o[0]) % m, -fib_norm(o[0]) % m}) for o in long}
    return dict(long_orbits=k, selection_bits_paid=round(log2(k), 3),
                class_bits_returned_locally=round(log2(len(labels)), 3))

def reconstruct(v1, v2, d, m=9):
    """Every long-orbit state (a, b) whose codeword has value v1 at position 0 and v2 at d."""
    P, C = codewords(m)
    S, f = linrec(m)
    long = [s for o in orbits(S, f) if len(o) == P for s in o]
    return [s for s in long if C[s][0] == v1 % m and C[s][d] == v2 % m]

def r6_packets(anchor):
    """The three R6 conditions for an anchor index (Core Part 2). Candidate states are counted two
    ways: ON CANONICAL ORBIT (the Navigator knows the orbit, the realistic Omega42 condition) and
    ON ALL LONG ORBITS (the orbit is withheld). Values are residues (0 for 9). RECOVERABLE uses the
    Yang separation 5; NON-RECOVERABLE uses the Antipode separation 12, which never fixes the
    phase; the 4D separation 8 is an anchor-dependent middle case."""
    P, C = codewords(9)
    w = C[(2, 5)]
    v = lambda k: w[(anchor + k) % 24]
    canon = lambda d: sum(1 for n in range(24) if (w[n], w[(n + d) % 24]) == (v(0), v(d)))
    full = [w[(anchor + k) % 24] for k in range(24)]
    rec = reconstruct(v(0), v(5), 5)
    return dict(anchor=anchor, FULL=full,
                RECOVERABLE=dict(values=(v(0), v(5)), separation=5, on_canonical_orbit=canon(5), on_all_long_orbits=len(rec),
                                 rebuilt_ok=[C[s] for s in rec] == [tuple(full)]),
                NON_RECOVERABLE=dict(values=(v(0), v(12)), separation=12, on_canonical_orbit=canon(12),
                                     on_all_long_orbits=len(reconstruct(v(0), v(12), 12))),
                MIDDLE_4D=dict(values=(v(0), v(8)), separation=8, on_canonical_orbit=canon(8),
                               on_all_long_orbits=len(reconstruct(v(0), v(8), 8))))

# ------------------------------------------------------------------ Substrate Witness: M274-M277 (Core Part 3.28)
CANON = None
def _canon():
    global CANON
    if CANON is None:
        CANON = codewords(9)[1][(2, 5)]
    return CANON

def _res(v):
    return int(v) % 9                          # 9 and 0 are one residue

def voice_of(state):
    """Voice A, B or C by the dominant pair of the state's orbit (Core Part 1.8.4), or KERNEL."""
    S, f = linrec(9)
    o = next(o for o in orbits(S, f) if state in o)
    if len(o) != 24:
        return 'KERNEL (period %d)' % len(o)
    from collections import Counter
    top = tuple(sorted(v if v else 9 for v, _ in Counter(s[0] for s in o).most_common(2)))
    return {(1, 8): 'Voice A', (2, 7): 'Voice B', (4, 5): 'Voice C'}.get(top, '?')

def m274_integrity(values):
    """M274 Coordinate Integrity Check: a reported 24-value coordinate (canonical order from the
    reported start) against the 81 valid sequences. VALID, CORRECTED (up to 8 wrong values,
    unique nearest sequence), AMBIGUOUS (two or more nearest at equal distance; all listed), or
    UNCORRECTABLE (nearest sequence more than 8 away: detected, not repaired)."""
    w = [_res(v) for v in values]
    assert len(w) == 24
    P, C = codewords(9)
    dist = sorted((hamming(c, w), s) for s, c in C.items())
    d0 = dist[0][0]
    nearest = [s for d, s in dist if d == d0]
    if d0 == 0:
        status = 'VALID'
    elif len(nearest) > 1:
        status = 'AMBIGUOUS'
    elif d0 <= 8:
        status = 'CORRECTED'
    else:
        status = 'UNCORRECTABLE'
    return dict(status=status, distance=d0, nearest_start_states=nearest,
                corrected=list(C[nearest[0]]) if status in ('VALID', 'CORRECTED') else None,
                orbit=voice_of(nearest[0]) if len(nearest) == 1 else None)

def m275_arms(anchor_index, anchor, yang, yin, fourd, antipode):
    """M275 Arm Consistency Check: on the canonical orbit the anchor and Yang values fix the phase
    (24 distinct pairs). From them the Yin, 4D and Antipode values are predicted and compared with
    the reported ones, and the inferred phase with the reported anchor index."""
    w = _canon()
    a, y = _res(anchor), _res(yang)
    ph = [n for n in range(24) if w[n] == a and w[(n + 5) % 24] == y]
    if len(ph) != 1:
        return dict(status='FAIL', reason='anchor and Yang values do not occur together on the canonical orbit')
    n = ph[0]
    pred = dict(Yin=w[(n + 18) % 24], **{'4D': w[(n + 8) % 24]}, Antipode=w[(n + 12) % 24])
    rep = dict(Yin=_res(yin), **{'4D': _res(fourd)}, Antipode=_res(antipode))
    bad = [k for k in pred if pred[k] != rep[k]]
    ok = not bad and n == anchor_index % 24
    return dict(status='PASS' if ok else 'FAIL', inferred_anchor_index=n, reported_anchor_index=anchor_index,
                mismatched_arms=bad, predicted=pred)

def m276_law(x0, x1, x2, x3):
    """M276 Law Witness: every law x+ = p x + q x- (mod 9) that fits four consecutive reported
    values. PASS when the only fit is Fibonacci (1, 1); AMBIGUOUS on a kernel state (norm not a
    unit, R3); FAIL when Fibonacci does not fit."""
    x0, x1, x2, x3 = map(_res, (x0, x1, x2, x3))
    fits = [(p, q) for p in range(9) for q in range(9) if (p * x1 + q * x0) % 9 == x2 and (p * x2 + q * x1) % 9 == x3]
    status = 'PASS' if fits == [(1, 1)] else ('AMBIGUOUS' if (1, 1) in fits else 'FAIL')
    return dict(status=status, laws=fits, determinant=(x1 * x1 - x0 * x2) % 9)

def m277_orbit(a, b):
    """M277 Orbit Witness: the norm of a reported starting state names its orbit in one step. The
    canonical orbit (Voice C) carries class +/-2; the reversed seed (5, 2) lands in +/-4 (Voice B).
    A recognizer, never a selector (Core Part 1.8.3): selection stays with K."""
    s = (_res(a), _res(b))
    n = fib_norm(s) % 9
    voice = voice_of(s)
    return dict(state=s, norm=n, norm_class=min(n, 9 - n) if n else 0, orbit=voice,
                status='PASS' if voice == 'Voice C' else 'FAIL')



# ------------------------------------------------------------------ arm geometry and the existing substrate checks (Core Step 8, M88)
CROWN = (3, 7, 11, 15, 19, 23)
ARM_OFFSETS = (('Anchor', 0), ('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))

def crown_derivation():
    """The Crown positions (L-345) are exactly the positions where the canonical sequence is
    divisible by 3; they are spaced 4 apart because 3 first divides F(4)."""
    w = _canon()
    zero3 = tuple(n for n in range(24) if w[n] % 3 == 0)
    first = next(d for d in range(1, 25) if fib(d) % 3 == 0)
    return dict(mod3_zero_positions=zero3, equals_crown=zero3 == CROWN, rank_of_apparition_of_3=first)

def step8_table():
    """For anchors P1-P9: Crown arms, CCD over Anchor/Yang/Yin/4D (denominator 4, L-346), PAB
    (CCD <= 1/4), M245 triggers (an arm other than the anchor on P19 or P23), and the residue
    class modulo 4 of each arm relative to the anchor."""
    rows = []
    for a in range(1, 10):
        pos = {k: (a + v) % 24 for k, v in ARM_OFFSETS}
        crown = [k for k, p in pos.items() if p in CROWN]
        ccd = sum(1 for k in ('Anchor', 'Yang', 'Yin', '4D') if pos[k] in CROWN) / 4
        rows.append(dict(anchor=a, crown_arms=crown, ccd=ccd, pab='ACTIVE' if ccd <= 0.25 else 'INACTIVE',
                         m245=[k for k, p in pos.items() if k != 'Anchor' and p in (19, 23)],
                         classes={k: (pos[k] - a) % 4 for k in pos}))
    return rows

def m88_blindness():
    """The antipodal checksum x(n+12) = -x(n) holds on every one of the 81 sequences (T^12 = -I),
    so M88 detects corruption of the anchor or antipode entry but not a substituted table."""
    P, C = codewords(9)
    return all(all((w[(n + 12) % 24] + w[n]) % 9 == 0 for n in range(24)) for w in C.values())


# ------------------------------------------------------------------ GROUND-CHALLENGE II: non-linear and cellular-automaton rivals (Companion 37.9)
def _perm_architecture(nxt):
    """Long orbits of a permutation of the 81 states (index 9a + b) if its cycle type is
    24+24+24+8+1 and every long orbit is complete and antipodal in its first coordinate; else None."""
    seen = [False] * 81; lens = []; longs = []
    for s0 in range(81):
        if seen[s0]:
            continue
        cyc = [s0]; seen[s0] = True; x = nxt[s0]
        while x != s0:
            if seen[x]:
                return None
            cyc.append(x); seen[x] = True; x = nxt[x]
        lens.append(len(cyc))
        if len(cyc) == 24:
            longs.append(cyc)
    if sorted(lens) != [1, 8, 24, 24, 24]:
        return None
    for o in longs:
        if len({v // 9 for v in o}) != 9 or any((o[(i + 12) % 24] // 9 + o[i] // 9) % 9 for i in range(24)):
            return None
    return longs

def _value_sequences(nxt):
    out = []
    for s0 in range(81):
        x, w = s0, []
        for _ in range(24):
            w.append(x // 9); x = nxt[x]
        out.append(tuple(w))
    return out

def henon_rivals():
    """Every map (a, b) -> (b, q a + f(b)) mod 9 with q a unit and f a polynomial of degree at most 3.
    Each is reversible for any f. Counts distinct maps (as functions), those with the full Omega42
    architecture, how many are affine, whether any non-affine one is Fibonacci with its values
    relabelled, and the any-k-positions reconstruction threshold of each non-affine rival."""
    pw = [[pow(b, k, 9) for k in range(4)] for b in range(9)]
    maps = {}
    for q in (1, 2, 4, 5, 7, 8):
        for c in product(range(9), repeat=4):
            fb = tuple((c[0] + c[1] * b + c[2] * pw[b][2] + c[3] * pw[b][3]) % 9 for b in range(9))
            maps.setdefault((q, fb), c)
    build = lambda q, fb: [b * 9 + (q * a + fb[b]) % 9 for a in range(9) for b in range(9)]
    affine = lambda fb: any(all(fb[b] == (c0 + c1 * b) % 9 for b in range(9)) for c0 in range(9) for c1 in range(9))
    arch = [(q, fb, c) for (q, fb), c in maps.items() if _perm_architecture(build(q, fb))]
    nonaff = [(q, fb, c) for q, fb, c in arch if not affine(fb)]
    F = set(_value_sequences(build(1, tuple(range(9)))))
    Flong = [w for w in F if len(set(w)) == 9]
    def relabelled(R):
        r0 = next(w for w in R if len(set(w)) == 9)
        for wf in Flong:
            g = {}
            if any(g.setdefault(x, y) != y for x, y in zip(wf, r0)) or len(set(g.values())) != 9:
                continue
            if {tuple(g[v] for v in w) for w in F} == R:
                return True
        return False
    def threshold(W):
        if len(set(W)) < 81:
            return None
        return 1 + max(sum(1 for i in range(24) if W[a][i] == W[b][i]) for a in range(81) for b in range(a + 1, 81))
    thr = sorted({threshold(_value_sequences(build(q, fb))) for q, fb, c in nonaff})
    return dict(distinct_maps=len(maps), full_architecture=len(arch), affine=len(arch) - len(nonaff),
                non_affine=len(nonaff), relabellings_of_fibonacci=sum(relabelled(set(_value_sequences(build(q, fb)))) for q, fb, c in nonaff),
                non_affine_thresholds=thr, example=nonaff[0][2] if nonaff else None)

def reversible_eca(sizes=range(8, 13)):
    """Reversible elementary cellular automata on rings of N cells: count and longest cycle."""
    out = {}
    for N in sizes:
        M = (1 << N) - 1
        rl = [((x << 1) | (x >> (N - 1))) & M for x in range(1 << N)]
        rr = [((x >> 1) | ((x & 1) << (N - 1))) & M for x in range(1 << N)]
        count, longest = 0, 0
        for rule in range(256):
            img = []
            for x in range(1 << N):
                L, R, y = rl[x], rr[x], 0
                for pat in range(8):
                    if (rule >> pat) & 1:
                        y |= (L if pat & 4 else ~L) & (x if pat & 2 else ~x) & (R if pat & 1 else ~R)
                img.append(y & M)
            if len(set(img)) != (1 << N):
                continue
            count += 1
            seen = [False] * (1 << N)
            for s0 in range(1 << N):
                n, x = 0, s0
                while not seen[x]:
                    seen[x] = True; x = img[x]; n += 1
                longest = max(longest, n)
        out[N] = (count, longest)
    return out

# ------------------------------------------------------------------ M267-GROUND arm map (Companion 37.8)
GROUNDS = (('A', 'Omega42, Fibonacci mod 9 from (2,5)', 9, (2, 5)),
           ('B', 'Fibonacci mod 6 from (0,1)', 6, (0, 1)),
           ('C', 'Fibonacci mod 10 from (0,1)', 10, (0, 1)),
           ('D', 'null: Fibonacci mod 16 from (0,1)', 16, (0, 1)))
OFFSETS = (('Anchor', 0), ('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))

def ground_arms(anchor):
    """Values at the anchor and the four arms on each ground. The anchor index comes from Core
    Part 2 unchanged; offsets are the Omega42 offsets on a 24-period and are scaled to the period
    otherwise, rounding half up (60: 13, 45, 20, 30). Values are residues; position names are
    withheld on every arm, so the test varies the ground and not its vocabulary."""
    out = []
    for key, name, m, seed in GROUNDS:
        seq, x = [], seed
        P = pisano(m)
        for _ in range(P):
            seq.append(x[0]); x = (x[1], (x[0] + x[1]) % m)
        row = []
        for arm, off in OFFSETS:
            k = int(off * P / 24 + 0.5)
            row.append((arm, (anchor + k) % P, seq[(anchor + k) % P]))
        out.append((key, name, P, row))
    return out

# ------------------------------------------------------------------ report
def report():
    g, mods = period24_moduli()
    print('== Pisano fixed points pi(n) = n up to 5000:', [n for n in range(2, 5001) if pisano(n) == n])
    print('== Moduli with period 24: m | gcd(F23-1, F24, F25-1) = %d, so the list is exhaustive: %s' % (g, mods))
    print()
    print('== Fibonacci grounds: the exhaustive period-24 list, plus mod 3, 8, 10')
    for m in [3, 8, 10] + mods:
        r = profile(m)
        print('m=%-4d states=%-6d period=%-3d long orbits=%-3d covering=%-3d antipodal=%-3d invariant separates=%-5s closure=%s' %
              (m, r['states'], r['period'], r['long_orbits'], r['long_covering'], r['long_antipode'],
               r['invariant_separates'], r['period_closure']))
    print()
    S, f = linrec(9)
    long = [o for o in orbits(S, f) if len(o) == 24]
    for name, s in (('Fibonacci (0,1)', (0, 1)), ('Lucas (2,1)', (2, 1)), ('Omega42 (2,5)', (2, 5))):
        k = next(i for i, o in enumerate(long) if s in o)
        print('%-16s -> period-24 orbit %d, invariant class +/-%d' % (name, k, min(fib_norm(s) % 9, -fib_norm(s) % 9)))
    print()
    rows, match = recurrences_mod9()
    print('== Second-order recurrences mod 9 tested: %d | matching the Omega42 architecture: %d' % (len(rows), len(match)))
    print('   simplest (coefficient size): %s' % sorted((x[5], x[0]) for x in match)[:3])
    gl = gl2_study()
    print('== GL(2, Z/9): order %(group_order)d, maximum element order %(max_order)d, elements of order 24: %(order24)d, '
          'with orbit structure [1,8,24,24,24]: %(same_architecture)d' % gl)
    print('   cyclic subgroups of order 24: %d, in %d coordinate-change classes of sizes %s (Omega42 class first)' %
          (gl['subgroups24'], len(gl['subgroup_classes']), gl['subgroup_classes']))
    for i, r in enumerate(gl['recurrences_by_class']):
        print('   class %d realised by second-order recurrences (size, (p, q)): %s' % (i, r if r else 'none'))
    bits, rule_bits = designed_rival_bits()
    print('== Designed rivals: permutations of 81 states with cycle type (24,24,24,8,1) need %.0f bits to specify; '
          'the Fibonacci rule among 2x2 recurrences mod 9 needs %.2f' % (bits, rule_bits))
    print()
    print('== Tribonacci mod 9:', tribonacci(9))
    for rule in (30, 90, 110, 150):
        print('== Elementary CA rule %d, ring of 8:' % rule, eca(rule, 8))
    print('== S4: longest cycle a single element generates:', s4_max_order())
    print('== Non-linear rivals (b, q a + f(b)), f cubic:', henon_rivals())
    print('== Reversible elementary CA, rings 8-12 (N: count, longest cycle):', reversible_eca())
    print()
    print('== Complexity budget (G10; yield list declared after first computation: DIAGNOSTIC)')
    for m in (9, 6, 10, 16):
        print('  ', budget(m))

# ------------------------------------------------------------------ tests
def test():
    ok = []
    def check(name, cond):
        ok.append(cond); print('%-62s %s' % (name, 'ok' if cond else 'FAIL'))
    g, mods = period24_moduli()
    check('period-24 moduli are exactly the ten divisors of 144', g == 144 and mods == [6, 9, 12, 16, 18, 24, 36, 48, 72, 144])
    check('Pisano fixed points to 5000 are 24 * 5^k', [n for n in range(2, 5001) if pisano(n) == n] == [24, 120, 600, 3000])
    p = {m: profile(m) for m in mods}
    full = [m for m in mods if p[m]['long_orbits'] > 1 and p[m]['all_long_cover'] and p[m]['all_long_antipode'] and p[m]['invariant_separates']]
    check('mod 9 alone: several long orbits, all complete, antipodal, separated', full == [9])
    check('mod 9 state space 24+24+24+8+1', p[9]['orbit_lengths'] == [1, 8, 24, 24, 24])
    check('mod 6: one long orbit, complete and antipodal', p[6]['long_orbits'] == 1 and p[6]['all_long_cover'] and p[6]['all_long_antipode'])
    r10 = profile(10)
    check('mod 10: period 60, one long orbit, complete, antipodal, no closure', r10['period'] == 60 and r10['long_orbits'] == 1 and r10['all_long_cover'] and r10['all_long_antipode'] and not r10['period_closure'])
    S, f = linrec(9)
    long = [o for o in orbits(S, f) if len(o) == 24]
    idx = [next(i for i, o in enumerate(long) if s in o) for s in ((0, 1), (2, 1), (2, 5))]
    check('Fibonacci, Lucas and (2,5) occupy the three different orbits', len(set(idx)) == 3)
    rows, match = recurrences_mod9()
    check('12 of 54 recurrences mod 9 match; simplest have size 2', len(rows) == 54 and len(match) == 12 and min(x[5] for x in match) == 2
          and sorted(x[0] for x in match if x[5] == 2) == [(1, 1), (8, 1)])
    gl = gl2_study()
    check('GL(2,Z/9): order 3888, maximum element order 24', gl['group_order'] == 3888 and gl['max_order'] == 24)
    check('all 864 order-24 elements share the 24+24+24+8+1 architecture', gl['order24'] == 864 and gl['same_architecture'] == 864)
    check('108 cyclic order-24 subgroups in 3 coordinate classes (27, 54, 27)', gl['subgroups24'] == 108 and gl['subgroup_classes'][0] == 27 and sorted(gl['subgroup_classes']) == [27, 27, 54])
    rc = gl['recurrences_by_class']
    check('Omega42 class realised by (1,1),(2,1),(7,1),(8,1)', [x[1] for x in rc[0]] == [(1, 1), (8, 1), (2, 1), (7, 1)])
    check('one rival class: 8 recurrences, simplest size 3; one class: none', sorted(len(r) for r in rc[1:]) == [0, 8] and min(x[0] for r in rc[1:] for x in r) == 3)
    bits, _ = designed_rival_bits()
    check('a designed rival with the same cycle type needs about 382 bits', 381 < bits < 383)
    check('Tribonacci mod 9 has no even long period', all(c % 2 for c in tribonacci(9)['cycle_lengths'] if c > 1))
    check('S4 longest single-generator cycle is 4', s4_max_order() == 4)
    check('rule 110 on 8 cells is not reversible', not eca(110, 8)['reversible'])
    A = ground_arms(1)
    check('M267-GROUND arm A reproduces the canonical orbit (P1 = 5, antipode P13 = 4)', A[0][3][0][2] == 5 and A[0][3][4][1:] == (13, 4))
    check('M267-GROUND period-60 offsets are 13, 45, 20, 30', [r[1] - 1 for r in A[2][3][1:]] == [13, 45, 20, 30])
    P, z, k, wit = r1_threshold(9)
    check('R1: any 7 of 24 positions determine the codeword', (P, z, k) == (24, 6, 7))
    check('R2: six positions can fail: (0,3) and (0,0) agree on 0,4,...,20', wit == ((0, 3), [0, 4, 8, 12, 16, 20]))
    P, rows = r2_profile(9)
    good = [r[0] for r in rows if r[1] == r[2]]
    check('R2: complete two-point separations are the 18 with 4 not dividing d', good == [d for d in range(1, 24) if d % 4])
    check('R2: completeness holds exactly where F(d) is a unit mod m (9, 6, 10, 16)',
          all(all((r[1] == r[2]) == r[4] for r in r2_profile(m)[1]) for m in (9, 6, 10, 16)))
    check('R1/R2 thresholds: mod 6 -> 9, mod 10 -> 21, mod 16 -> 9', [r1_threshold(m)[2] for m in (6, 10, 16)] == [9, 21, 9])
    rec = {m: r3_law_recovery(m) for m in (9, 6, 10, 16)}
    check('R3: law recovered on 72/81, 24/36, 60/100, 192/256, exactly the unit-norm states',
          [rec[m][1] for m in (9, 6, 10, 16)] == [72, 24, 60, 192] and all(rec[m][3] for m in rec))
    check('R4: one-step norm labels the five orbits 0, 1, 4, 0, 2', sorted(l[0] for _, l in r4_class_labels()) == [0, 0, 1, 2, 4])
    check('arms: Yang and Yin single out 24 phases, 4D 20, Antipode 9', arm_information() == {'Yang': 24, 'Yin': 24, '4D': 20, 'Antipode': 9})
    check('R3 theorem: law unique iff -N is a unit (m = 6, 9, 10, 16, exhaustive)', all(r3_theorem(m) for m in (6, 9, 10, 16)))
    sc = self_check(9)
    check('R8: minimum distance 18; detects 17 wrong values, corrects 8', (sc['min_distance'], sc['detects'], sc['corrects']) == (18, 17, 8)
          and sc['random_correction_ok'] and sc['tie_at_radius_plus_1'])
    check('R8: correction radius mod 6 -> 7 of 24, mod 10 -> 19 of 60, mod 16 -> 7 of 24',
          [self_check(m, trials=300)['corrects'] for m in (6, 10, 16)] == [7, 19, 7])
    check('multiplicity balance: 1.585 bits paid, 1.585 returned by the norm', multiplicity_balance() ==
          dict(long_orbits=3, selection_bits_paid=1.585, class_bits_returned_locally=1.585))
    r6 = r6_packets(1)
    pk = [r6_packets(a) for a in range(1, 10)]
    check('R6 RECOVERABLE (Yang): 1 candidate on the canonical orbit and on all long orbits, anchors 1-9',
          all(r['RECOVERABLE']['on_canonical_orbit'] == 1 and r['RECOVERABLE']['on_all_long_orbits'] == 1 and r['RECOVERABLE']['rebuilt_ok'] for r in pk))
    check('R6 NON-RECOVERABLE (Antipode): 2 or 5 on the canonical orbit, 6 or 9 on all long orbits',
          all(r['NON_RECOVERABLE']['on_canonical_orbit'] in (2, 5) and r['NON_RECOVERABLE']['on_all_long_orbits'] in (6, 9) for r in pk))
    check('R6 MIDDLE (4D): canonical 3,1,1,1,3,1,1,1,3 for anchors 1-9; 3 on all long orbits',
          [r['MIDDLE_4D']['on_canonical_orbit'] for r in pk] == [3, 1, 1, 1, 3, 1, 1, 1, 3] and all(r['MIDDLE_4D']['on_all_long_orbits'] == 3 for r in pk))
    w = list(_canon())
    check('M274: canonical coordinate VALID, Voice C', m274_integrity(w)['status'] == 'VALID' and m274_integrity(w)['orbit'] == 'Voice C')
    bad = list(w)
    for i in (0, 3, 6, 9, 12, 15, 18, 21):
        bad[i] = (bad[i] + 1) % 9
    r = m274_integrity(bad)
    check('M274: 8 wrong values CORRECTED to the canonical coordinate', r['status'] == 'CORRECTED' and r['corrected'] == w and r['distance'] == 8)
    far = codewords(9)[1][(0, 3)]
    nz = [i for i, v in enumerate(far) if v][:9]
    check('M274: 9-error midpoint reported AMBIGUOUS with both neighbours',
          m274_integrity([far[i] if i in nz else 0 for i in range(24)])['status'] == 'AMBIGUOUS')
    check('M275: correct arms PASS; a wrong Yin value FAILS', m275_arms(1, w[1], w[6], w[19], w[9], w[13])['status'] == 'PASS'
          and m275_arms(1, w[1], w[6], (w[19] + 1) % 9, w[9], w[13])['mismatched_arms'] == ['Yin'])
    check('M276: canonical window PASS; kernel window (0,3,3,6) AMBIGUOUS; modulo-10 slip FAILS',
          m276_law(*w[:4])['status'] == 'PASS' and m276_law(0, 3, 3, 6)['status'] == 'AMBIGUOUS' and m276_law(5, 7, 12 % 10, 9)['status'] == 'FAIL')
    check('M277: (2,5) Voice C class 2 PASS; reversed seed (5,2) Voice B class 4 FAIL',
          m277_orbit(2, 5)['orbit'] == 'Voice C' and m277_orbit(2, 5)['norm_class'] == 2 and m277_orbit(5, 2)['orbit'] == 'Voice B' and m277_orbit(5, 2)['norm_class'] == 4)
    cd = crown_derivation()
    check('Crown positions are the mod-3 zeros of the canonical sequence; 3 first divides F(4)', cd['equals_crown'] and cd['rank_of_apparition_of_3'] == 4)
    check('M88 checksum holds on all 81 sequences: blind to a substituted table', m88_blindness())
    t = step8_table()
    check('Step 8: CCD 1/4,1/4,1/2,0,1/4,1/4,1/2,0,1/4; PAB INACTIVE only at P3 and P7',
          [r['ccd'] for r in t] == [0.25, 0.25, 0.5, 0.0, 0.25, 0.25, 0.5, 0.0, 0.25] and [r['anchor'] for r in t if r['pab'] == 'INACTIVE'] == [3, 7])
    check('M245 fires at P1 and P5 (Yin) and P7 (Antipode) only', [(r['anchor'], r['m245']) for r in t if r['m245']] == [(1, ['Yin']), (5, ['Yin']), (7, ['Antipode'])])
    check('arm classes mod 4: Anchor, 4D, Antipode 0; Yang 1; Yin 2; class 3 never reached',
          all(r['classes'] == {'Anchor': 0, 'Yang': 1, 'Yin': 2, '4D': 0, 'Antipode': 0} for r in t))
    hr = henon_rivals()
    check('non-linear rivals: 13122 maps; 30 with the full architecture, 12 affine, 18 non-affine',
          (hr['distinct_maps'], hr['full_architecture'], hr['affine'], hr['non_affine']) == (13122, 30, 12, 18))
    check('no non-affine rival is Fibonacci relabelled; each has the 7-position threshold',
          hr['relabellings_of_fibonacci'] == 0 and hr['non_affine_thresholds'] == [7])
    check('reversible elementary CA, rings 8-12: 8, 14, 8, 16, 6 rules; none of 81 states',
          [v[0] for v in reversible_eca().values()] == [8, 14, 8, 16, 6])
    print('GROUND CHALLENGE TEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    if '--arms' in sys.argv:
        a = int(sys.argv[sys.argv.index('--arms') + 1])
        for key, name, P, row in ground_arms(a):
            print('ARM %s  %-40s period %-3d ' % (key, name, P) + ' | '.join('%s P%d v=%d' % r for r in row))
        sys.exit(0)
    if '--reconstruction' in sys.argv:
        reconstruction_report()
        print('R3 theorem (law unique iff -N unit) holds exhaustively for m = 6, 9, 10, 16:', all(r3_theorem(m) for m in (6, 9, 10, 16)))
        for m in (9, 6, 10, 16):
            print('R8 self-checking', self_check(m))
        print('Multiplicity balance mod 9:', multiplicity_balance())
        print('Crown derivation:', crown_derivation())
        print('M88 checksum holds on all 81 sequences (blind to a substituted table):', m88_blindness())
        for r in step8_table():
            print('Step 8 table', r)
        sys.exit(0)
    for flag, fn, k in (('--m274', None, 24), ('--m276', m276_law, 4), ('--m277', m277_orbit, 2)):
        if flag in sys.argv:
            vals = [int(v) for v in sys.argv[sys.argv.index(flag) + 1].split(',')]
            print(m274_integrity(vals) if flag == '--m274' else fn(*vals)); sys.exit(0)
    if '--m275' in sys.argv:
        i = sys.argv.index('--m275')
        print(m275_arms(int(sys.argv[i + 1]), *[int(v) for v in sys.argv[i + 2].split(',')])); sys.exit(0)
    if '--r6' in sys.argv:
        a = int(sys.argv[sys.argv.index('--r6') + 1])
        for k, v in r6_packets(a).items():
            print('%-20s %s' % (k, v))
        sys.exit(0)
    if '--test' in sys.argv:
        sys.exit(0 if test() else 1)
    report()
# ===== ground_challenge.py END =====
