#!/usr/bin/env python3
"""beyond.py -- SEQ 123: the null embedding down the tower (H-51) and the mathematics of the places beyond the real one
(Core Part 0.0.9; Companion Part 176). Standard library only.
    python3 tools/beyond.py              # the report, as JSON
    python3 tools/beyond.py --selftest   # one PASS or FAIL a check
    python3 tools/beyond.py --state a b m  # the identity ladder of the state (a, b) mod 3^m
    python3 tools/beyond.py --places a b   # the kind of place, the period of the law and the orbit of (a, b) at the first primes (an M327 reading)
    python3 tools/beyond.py --unique a b m [c d]  # what (a, b) generates mod 3^m, and the one unit joining it to (c, d)
"""
import json, math, random, sys
R = {}
A = ((0, 1), (1, 1))
def mul(X, Y, m): return tuple(tuple(sum(X[i][t]*Y[t][j] for t in range(2)) % m for j in range(2)) for i in range(2))
def mpow(X, e, m):
    P = ((1, 0), (0, 1))
    while e:
        if e & 1: P = mul(P, X, m)
        X = mul(X, X, m); e >>= 1
    return P
def act(X, s, m): return ((X[0][0]*s[0]+X[0][1]*s[1]) % m, (X[1][0]*s[0]+X[1][1]*s[1]) % m)
def v3(n):
    if n == 0: return 99
    k = 0
    while n % 3 == 0: n //= 3; k += 1
    return k
def Q(s, m): a, b = s; return (a*a+a*b-b*b) % m
def N(s, m):  # the null embedding s -> s s^T in coordinates (t, x, y, z); 1/2 exists mod 3^m
    a, b = s; h = pow(2, -1, m); return ((a*a+b*b)*h % m, a*b % m, 0, (a*a-b*b)*h % m)
def L_act(p, m):  # L_A on (t, x, y, z), computed through X -> A X A^T on the symmetric part (y = 0 stays 0)
    t, x, y, z = p; h = pow(2, -1, m)
    X = ((t+z, x), (x, t-z)); Y = mul(mul(A, X, m), ((0, 1), (1, 1)), m)
    return ((Y[0][0]+Y[1][1])*h % m, Y[1][0] % m, 0, (Y[0][0]-Y[1][1])*h % m)

def orbits(points, f):
    seen, out = set(), {}
    for p in points:
        if p in seen: continue
        n, c = 0, p
        while True:
            seen.add(c); n += 1; c = f(c)
            if c == p: break
        out[n] = out.get(n, 0)+1
    return dict(sorted(out.items()))
def predicted_null(m):  # layers r = m - 2j: 3^(r-1) orbits of length 4*3^(r-1) for r >= 1, the origin for r <= 0
    out = {1: 1}
    for j in range(m//2+1):
        r = m-2*j
        if r >= 1: L = 4*3**(r-1); out[L] = out.get(L, 0)+3**(r-1)
    return dict(sorted(out.items()))
def predicted_states(m):  # layers r = m - j: 3^(r-1) orbits of length 8*3^(r-1)
    out = {1: 1}
    for j in range(m):
        r = m-j; L = 8*3**(r-1); out[L] = out.get(L, 0)+3**(r-1)
    return dict(sorted(out.items()))

def persistence(a, b, m):
    """the identity ladder of a state at modulus 3^m: its layer, its world, its phase, its label, its light ray, its mirror"""
    M = 3**m; s = (a % M, b % M)
    if s == (0, 0): return dict(state=s, layer='the still point', world_size=1)
    j = min(v3(s[0]), v3(s[1]))
    orb, c = [], s
    while c not in orb: orb.append(c); c = act(A, c, M)
    rep = min(orb); phase = (orb.index(s) - orb.index(rep)) % len(orb)
    neg = ((-s[0]) % M, (-s[1]) % M)
    return dict(state=s, layer=j, world_size=len(orb), world_rep=rep, phase=phase,
                label=min(Q(s, M), (-Q(s, M)) % M), light_ray=N(s, M),
                mirror=neg, steps_to_mirror=(orb.index(neg) - orb.index(s)) % len(orb) if neg in orb else None)
if '--state' in sys.argv:
    i = sys.argv.index('--state'); a, b, m = (int(x) for x in sys.argv[i+1:i+4])
    print(json.dumps(persistence(a, b, m), default=str)); sys.exit(0)

# ---- 1. H-51 by enumeration, m = 1 to 6 (depth 1/2 to depth 3)
brute = {}
for m in range(1, 7):
    M = 3**m; st = [(a, b) for a in range(M) for b in range(M)]
    eq = all(L_act(N(s, M), M) == N(act(A, s, M), M) for s in st) if m <= 4 else \
         all(L_act(N(s, M), M) == N(act(A, s, M), M) for s in random.Random(m).sample(st, 20000))
    img = {N(s, M) for s in st}
    null = all((t*t-x*x-y*y-z*z) % M == 0 for t, x, y, z in img)
    no = orbits(img, lambda p: L_act(p, M)); so = orbits(st, lambda s: act(A, s, M))
    brute[m] = dict(equivariant=eq, null=null, image=len(img), null_orbits=no, state_orbits=so,
                    null_ok=no == predicted_null(m), state_ok=so == predicted_states(m),
                    sectors=sum(so.values()), sectors_formula=(3**m+1)//2)
R['H51_enumerated'] = brute

# ---- 2. H-51 beyond enumeration: orders and orbit lengths by divisor tests, m up to 40 (depth 20)
def class_len_ok(s, m):  # the +-class of a primitive s has length exactly 4*3^(m-1)
    M = 3**m; n = 4*3**(m-1); neg = lambda v: ((-v[0]) % M, (-v[1]) % M)
    hit = lambda e: act(mpow(A, e, M), s, M) in (s, neg(s))
    return hit(n) and not hit(n//2) and (m == 1 or not hit(n//3))
deep = {}
rng = random.Random(123)
for m in range(1, 41):
    M = 3**m; o = 8*3**(m-1)
    order_ok = mpow(A, o, M) == ((1, 0), (0, 1)) and mpow(A, o//2, M) != ((1, 0), (0, 1)) and (m == 1 or mpow(A, o//3, M) != ((1, 0), (0, 1)))
    half_is_minus = mpow(A, o//2, M) == ((M-1, 0), (0, M-1))
    samples = [(rng.randrange(M), rng.randrange(1, M) * (1 if rng.random() < .5 else 3) % M) for _ in range(6)]
    samples = [s for s in samples if s[0] % 3 or s[1] % 3]
    deep[m] = dict(order_A=o if order_ok else None, half_is_minusI=half_is_minus,
                   null_class_len=4*3**(m-1), classes_ok=all(class_len_ok(s, m) for s in samples), n_samples=len(samples))
R['H51_deep_ok'] = all(d['order_A'] and d['half_is_minusI'] and d['classes_ok'] for d in deep.values())
R['H51_deep_depths'] = '1 to 20 (3^1 to 3^40)'
R['null_top_orbit_by_depth'] = {k: 4*3**(2*k-1) for k in range(1, 13)}
R['null_points_by_depth'] = {k: 1+sum(4*3**(2*(2*k-2*j)-2) for j in range(k)) for k in range(1, 7)}
R['sectors_by_depth'] = {k: (9**k+1)//2 for k in range(1, 7)}

# ---- 3. the worlds are labelled by the norm up to sign (primitive layer), m = 1 to 6
lab = {}
for m in range(1, 7):
    M = 3**m; seen = set(); labels = []; ok = True
    for a in range(M):
        for b in range(M):
            s = (a, b)
            if (a % 3 == 0 and b % 3 == 0) or s in seen: continue
            orb, c = set(), s
            while c not in orb: orb.add(c); c = act(A, c, M)
            seen |= orb
            cls = {min(Q(u, M), (-Q(u, M)) % M) for u in orb}
            ok &= len(cls) == 1; labels.append(cls.pop())
    lab[m] = dict(worlds=len(labels), distinct_labels=len(set(labels)), constant_on_orbits=ok,
                  label_classes=len({min(x, (-x) % M) for x in range(M) if x % 3}))
R['norm_labels'] = lab

# ---- 4. self-similarity: sigma(s) = 3s is an equivariant injection mod 3^(m-1) -> mod 3^m, Q(3s) = 9 Q(s)
ss = {}
for m in range(2, 6):
    M, M1 = 3**m, 3**(m-1)
    st = [(a, b) for a in range(M1) for b in range(M1)]
    img = {(3*a % M, 3*b % M) for a, b in st}
    ss[m] = dict(injective=len(img) == len(st),
                 equivariant=all(act(A, (3*a % M, 3*b % M), M) == tuple(3*x % M for x in act(A, (a, b), M1)) for a, b in st),
                 norm_scaled=all(Q((3*a, 3*b), M) == 9*Q((a, b), M1) % M for a, b in st))
R['self_similar'] = ss
# the contraction: |3^j s|_3 = 3^(-j) |s|_3 -> 0, the still point the unique fixed point of sigma
R['contraction'] = [3**-j for j in range(6)]

# ---- 5. the time average is the projector onto the sector-uniform states (depth 1)
M = 9; st = [(a, b) for a in range(M) for b in range(M)]; idx = {s: i for i, s in enumerate(st)}
perm = [idx[act(A, s, M)] for s in st]
psi = [random.Random(5).random() for _ in st]
avg = [0.0]*81; v = psi[:]
for n in range(24):
    for i in range(81): avg[i] += v[i]/24
    w = [0.0]*81
    for i in range(81): w[perm[i]] = v[i]
    v = w
orb_of = {}
for i in range(81):
    if i in orb_of: continue
    o, c = [], i
    while c not in o: o.append(c); c = perm[c]
    for c in o: orb_of[c] = tuple(o)
proj = [sum(psi[c] for c in orb_of[i])/len(orb_of[i]) for i in range(81)]
R['time_average_is_projector'] = max(abs(avg[i]-proj[i]) for i in range(81)) < 1e-12
R['time_average_keeps_sector_weight'] = all(abs(sum(avg[c] for c in o)-sum(psi[c] for c in o)) < 1e-12 for o in set(orb_of.values()))

# ---- 6. 3-adic time: v_3(phi^(8 n) - 1) = 1 + v_3(n), so n -> phi^(8n) extends to n in Z_3
def phipow_minus1_v3(e, m=30):
    P = mpow(A, e, 3**m); return min(v3(P[0][0]-1), v3(P[0][1]), v3(P[1][0]), v3(P[1][1]-1))
R['v3_phi8n_minus1'] = {n: phipow_minus1_v3(8*n) for n in (1, 2, 3, 6, 9, 27, 81, 243)}
R['three_adic_time_ok'] = all(R['v3_phi8n_minus1'][n] == 1+v3(n) for n in R['v3_phi8n_minus1'])
# a 3-adically convergent time: phi^(8 * 3^j) -> 1 while 8 * 3^j -> infinity in the reals
R['returns_to_now'] = {j: phipow_minus1_v3(8*3**j) for j in range(6)}

# ---- 7. the places of Q(sqrt 5): split, inert, ramified, and the period of the law at each prime
def pisano(p):
    a, b, n = 0, 1, 0
    while True:
        a, b = b, (a+b) % p; n += 1
        if (a, b) == (0, 1): return n
def kind(p):
    if p == 5: return 'ramified'
    return 'split' if p % 5 in (1, 4) else 'inert'
primes = [p for p in range(2, 100) if all(p % d for d in range(2, int(p**.5)+1))]
places = {p: dict(kind=kind(p), period=pisano(p)) for p in primes}
def kind_ok(p, d):
    if d['kind'] == 'split': return (p-1) % d['period'] == 0
    if d['kind'] == 'inert': return (2*(p+1)) % d['period'] == 0 and (p-1) % d['period'] != 0
    return d['period'] == 20
R['places'] = {p: '%s, period %d' % (d['kind'], d['period']) for p, d in places.items()}
R['places_ok'] = all(kind_ok(p, d) for p, d in places.items())
# eigenlines of A mod p: split -> 2 (light-like lines: a boost world), inert -> 0 (a rotation world), ramified -> 1 (a shear)
def eigenlines(p): return sum(1 for x in range(p) if (x*x-x-1) % p == 0)
R['eigenlines'] = {p: eigenlines(p) for p in (2, 3, 5, 7, 11, 13, 19, 29, 31)}
R['eigenlines_ok'] = all(eigenlines(p) == {'split': 2, 'inert': 0, 'ramified': 1}[kind(p)] for p in primes)

# ---- 8. the product formula over every place, for x = a + b phi with norm a^2 + ab - b^2
def product_formula(a, b):
    n = abs(a*a+a*b-b*b); prod = float(n)  # the two real places together give |N(x)|
    for p in range(2, n+1):
        if all(p % d for d in range(2, int(p**.5)+1)):
            while n % p == 0: n //= p; prod /= p
    return prod
R['product_formula'] = {str(x): product_formula(*x) for x in ((3, 0), (2, 1), (7, 4), (5, 3), (12, 7))}
R['product_formula_ok'] = all(abs(v-1) < 1e-12 for v in R['product_formula'].values())

# ---- 9. the class number formula: L(1, chi_5) = 2 ln(phi) / sqrt 5, the regulator ln(phi), h = 1
chi = {0: 0, 1: 1, 2: -1, 3: -1, 4: 1}
S, partial = 0.0, []
Nn = 2_000_000
for n in range(1, Nn+1):
    S += chi[n % 5]/n
    if n > Nn-5: partial.append(S)
Lval = sum(partial)/len(partial); phi = (1+5**.5)/2
R['L1_chi5'] = Lval; R['two_ln_phi_over_sqrt5'] = 2*math.log(phi)/5**.5
R['class_number_formula_ok'] = abs(Lval-R['two_ln_phi_over_sqrt5']) < 1e-6
R['regulator'] = math.log(phi); R['rapidity_A2'] = 2*math.log(phi)

# ---- 10. unique expression: every primitive state generates the whole; the units act transitively and freely
def zmul(u, s, M):
    a, b = u; c, d = s; return ((a*c+b*d) % M, (a*d+b*c+b*d) % M)
def unique(a, b, m, to=None):
    M = 3**m; s = (a % M, b % M); ring = [(x, y) for x in range(M) for y in range(M)]
    gen = {zmul(u, s, M) for u in ring}
    out = dict(state=s, generates=len(gen), of=M*M, primitive=bool(s[0] % 3 or s[1] % 3))
    if to is not None:
        t = (to[0] % M, to[1] % M); out['joining_units'] = [u for u in ring if (u[0] % 3 or u[1] % 3) and zmul(u, s, M) == t]
    return out
UQ = {}
for m in (1, 2, 3):
    M = 3**m; ring = [(x, y) for x in range(M) for y in range(M)]
    prim = [s for s in ring if s[0] % 3 or s[1] % 3]
    s0 = prim[0]
    UQ[m] = dict(primitive=len(prim),
                 every_primitive_generates_all=all(len({zmul(u, s, M) for u in ring}) == M*M for s in prim),
                 transitive=len({zmul(u, s0, M) for u in prim}) == len(prim),
                 free=all(sum(1 for u in prim if zmul(u, s0, M) == t) == 1 for t in prim))
R['unique_expression'] = UQ
if '--unique' in sys.argv:
    i = sys.argv.index('--unique'); v = [int(x) for x in sys.argv[i+1:i+6]]
    print(json.dumps(unique(v[0], v[1], v[2], (v[3], v[4]) if len(v) == 5 else None), default=str)); sys.exit(0)

if '--places' in sys.argv:
    i = sys.argv.index('--places'); a, b = int(sys.argv[i+1]), int(sys.argv[i+2])
    for p in (2, 3, 5, 7, 11, 13):
        s0 = (a % p, b % p); c, n = act(A, s0, p), 1
        while c != s0: c = act(A, c, p); n += 1
        print('p = %-2d %-9s law period %-3d orbit of (%d, %d) mod p: %d' % (p, kind(p), pisano(p), a, b, n))
    sys.exit(0)

checks = [
 ('H-51 equivariant and null at depths 1/2 to 3', all(d['equivariant'] and d['null'] for d in brute.values())),
 ('H-51 null census = layer formula, m = 1 to 6', all(d['null_ok'] for d in brute.values())),
 ('state census = layer formula, sectors (3^m + 1)/2', all(d['state_ok'] and d['sectors'] == d['sectors_formula'] for d in brute.values())),
 ('H-51 orders and class lengths to depth 20', R['H51_deep_ok']),
 ('worlds labelled by the norm up to sign', all(d['worlds'] == d['distinct_labels'] == d['label_classes'] and d['constant_on_orbits'] for d in lab.values())),
 ('sigma(s) = 3s equivariant, injective, Q scaled by 9', all(all(d.values()) for d in ss.values())),
 ('time average = projector onto sector-uniform states', R['time_average_is_projector'] and R['time_average_keeps_sector_weight']),
 ('3-adic time: v3(phi^8n - 1) = 1 + v3(n)', R['three_adic_time_ok']),
 ('places: split, inert, ramified periods and eigenlines', R['places_ok'] and R['eigenlines_ok']),
 ('product formula over every place', R['product_formula_ok']),
 ('class number formula L(1, chi5) = 2 ln phi / sqrt 5', R['class_number_formula_ok']),
 ('unique expression: each primitive state generates the whole, units transitive and free', all(all(d.values()) for d in UQ.values())),
]
R['PASS'] = '%d of %d' % (sum(1 for _, c in checks if c), len(checks))
if '--selftest' in sys.argv:
    for n, c in checks: print('%-55s %s' % (n, 'PASS' if c else 'FAIL'))
    print('BEYOND SELFTEST: ' + R['PASS']); sys.exit(0 if all(c for _, c in checks) else 1)
print(json.dumps(R, indent=1, default=str))
