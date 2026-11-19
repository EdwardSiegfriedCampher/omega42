#!/usr/bin/env python3
"""Construct X v2: reference implementation of the New Construct (Omega42 research instrument).

Tiers: Construct Classic (original workbook, frozen) -> Construct X (this file) -> Omega42 Discovery Operations.
Every feature carries a provenance label:
  CLASSIC-DERIVED  extracted from the original workbook
  X-CONSTRUCTED    introduced by Construct X's own mathematics
  CROSS-VALIDATED  an X property shown, by a registered test, to match a Classic property

Engines
  S  Substrate      : Z/9 (units U, ideal I); F9 = Z[phi]/3 (phi^2 = phi + 1); F27 = F3[g]/(g^3 - g + 1)
  A  Address        : 27 domains = F27 = AG(3,3); 26 seeds = g^0..g^25; 702 nodes = AGL(1,27); 13-round schedule
  C  Comparison     : pooled, positional, matching, weighted; tolerance modes units / symmetric / modular;
                      every call returns an explainable report
  T  Temporal       : lagged increment stability; scan lags 2..24 against the lag-1 (trend-only) baseline;
                      trend fitted on training data only; held-out scoring; two null models (iid and block)
  G  Group-relative : templates r = x_t * x_{t-d}^-1 over a declared group; group-axiom checks; composition test
  V  Verification   : relation checker with four outcomes; self-test suite
Run `python3 construct_x.py` for the self-test suite and the worked examples.
"""
import itertools, math, random, statistics as st
from collections import Counter

VERSION = "2.3.2"

# Omega42-T01 (Core Part 10.5): technical names; legacy names stay as aliases until the next STABLE release
TERMS = {
    "Field Y": "Reference Vector Y", "Field X": "Input Vector X", "candidate block": "Candidate Set",
    "coverage flag": "Threshold Result", "pooled": "Pooled Coverage", "positional": "Positional Coverage",
    "matching": "One-to-One Matching", "weighted": "Weighted Similarity", "Template Bank": "Lagged-Increment Library",
    "template": "Lagged-Increment Model", "lag": "Lag Interval", "Pred Sheet": "Prediction Workspace",
    "RHWS (Reversed Higher World Square)": "Reversed Higher World Array", "702-node architecture": "Relational Address space",
    "13-round schedule": "Balanced Comparison Schedule", "PROVEN": "PROVED",
}
OPERATOR_ALIASES = {"pooled_coverage": "pooled", "positional_coverage": "positional",
                    "one_to_one_matching": "matching", "weighted_similarity": "weighted"}

# ======================================================================= S: substrate
U = (1, 2, 4, 5, 7, 8)          # units of Z/9 (Lower World)            CLASSIC-DERIVED
I = (0, 3, 6)                   # ideal 3Z/9 (Higher World)              CLASSIC-DERIVED
DOUBLING = (1, 2, 4, 8, 7, 5)   # powers of 2 mod 9                      CLASSIC-DERIVED


# ---- F9 = Z[phi]/3, element a + b*phi stored as (a, b); phi^2 = phi + 1          X-CONSTRUCTED
def f9_add(x, y): return ((x[0] + y[0]) % 3, (x[1] + y[1]) % 3)


def f9_mul(x, y):
    a, b = x; c, d = y                     # (a + b phi)(c + d phi) = ac + (ad + bc) phi + bd (phi + 1)
    return ((a * c + b * d) % 3, (a * d + b * c + b * d) % 3)


F9 = list(itertools.product(range(3), repeat=2))
PHI = (0, 1)


def omega_step(v):
    """Omega42's map T(a, b) = (b, a + b) on F3^2."""
    return (v[1], (v[0] + v[1]) % 3)


# ---- F27 = F3[g]/(g^3 - g + 1), element (c0, c1, c2) = c0 + c1 g + c2 g^2        X-CONSTRUCTED
ZERO, ONE, G = (0, 0, 0), (1, 0, 0), (0, 1, 0)
POLY = (1, -1, 0, 1)                       # coefficients of 1 - g + 0 g^2 + g^3, i.e. g^3 - g + 1


def f_add(a, b): return tuple((x + y) % 3 for x, y in zip(a, b))
def f_neg(a): return tuple((-x) % 3 for x in a)
def f_sub(a, b): return f_add(a, f_neg(b))


def f_mul(a, b):
    c = [0] * 5
    for i in range(3):
        for j in range(3):
            c[i + j] += a[i] * b[j]
    for k in (4, 3):                       # g^3 = g - 1
        c[k - 2] += c[k]; c[k - 3] -= c[k]; c[k] = 0
    return tuple(x % 3 for x in c[:3])


def g_pow(n):
    r = ONE
    for _ in range(n % 26):
        r = f_mul(r, G)
    return r


FIELD = list(itertools.product(range(3), repeat=3))
SINGER = [g_pow(n) for n in range(26)]
LOG = {v: n for n, v in enumerate(SINGER)}


def f_inv(a):
    if a == ZERO:
        raise ZeroDivisionError("0 has no inverse in F27")
    return SINGER[(-LOG[a]) % 26]


def poly_irreducible_cubic_f3(p=POLY):
    """A cubic over F3 is irreducible iff it has no root in F3."""
    return all((p[0] + p[1] * x + p[2] * x * x + p[3] * x ** 3) % 3 for x in range(3))


def element_order(a):
    k, r = 1, a
    while r != ONE:
        r = f_mul(r, a); k += 1
    return k

# ======================================================================= A: address
# Seed labels. Pairing CLASSIC-DERIVED (STP H-001); field positions X-CONSTRUCTED.
WORKBOOK_PARTNER = {k: k for k in range(1, 10)} | {3: 6, 6: 3}   # P_k <-> N_partner(k)
SEED_LABELS = {}
for k in range(1, 10):
    SEED_LABELS[f"P{k}"] = k - 1
    SEED_LABELS[f"N{WORKBOOK_PARTNER[k]}"] = k - 1 + 13
for name, n in (("PU", 9), ("PD", 10), ("T1", 11), ("T2", 12),
                ("NU", 22), ("ND", 23), ("T3", 24), ("T4", 25)):
    SEED_LABELS[name] = n
LABEL_OF = {n: s for s, n in SEED_LABELS.items()}

RELATION_TYPES = {
    "EXACT_NEGATIVE": "offset vectors are exact integer negatives (Classic, H-001)",
    "MODULAR_ANTIPODE": "offsets agree mod 9 with the antipode's P-sheet (Classic, H-005)",
    "POSITIONAL": "same position in two fields or sheets",
    "NAVIGATION_PARTNER": "reached by an Omega42 arm (e.g. the Antipode arm)",
    "STRUCTURAL_ANALOGUE": "shares an invariant under a stated transformation",
    "EMPIRICAL_ASSOCIATION": "co-occurs in data; no structural claim",
}

PROVENANCE = {
    "13 exact negative seed pairs": "CLASSIC-DERIVED",
    "N_k = P_(9-k) mod 9 (Lower World)": "CLASSIC-DERIVED",
    "26 seeds as powers of g in F27": "X-CONSTRUCTED",
    "partners 13 powers apart": "CROSS-VALIDATED (encodes H-001 pairing exactly)",
    "702 nodes as AGL(1,27)": "X-CONSTRUCTED",
    "13-round Steiner schedule": "X-CONSTRUCTED",
    "pooled coverage, Lower World offsets": "CLASSIC-DERIVED",
    "positional / matching / weighted coverage": "X-CONSTRUCTED",
    "lagged template formula": "CLASSIC-DERIVED",
    "held-out temporal testing and surrogates": "X-CONSTRUCTED",
}


def seed(label): return SINGER[SEED_LABELS[label]]
def partner_label(label): return LABEL_OF[(SEED_LABELS[label] + 13) % 26]


def node(domain, seed_label):
    """Directed node: from domain p along seed v to p + v."""
    return domain, f_add(domain, seed(seed_label))


def williams_schedule(n=6):
    """Williams crossover design for an even number n of treatments (labels 1..n).
    Row i is the base sequence 0, 1, n-1, 2, n-2, ... shifted by i: each treatment once per row and column,
    and every ordered pair of distinct treatments adjacent exactly once (first-order carryover balanced)."""
    if n % 2:
        raise ValueError("this construction needs an even n")
    base, lo, hi = [0], 1, n - 1
    while len(base) < n:
        base.append(lo); lo += 1
        if len(base) < n:
            base.append(hi); hi -= 1
    return [[(b + i) % n + 1 for b in base] for i in range(n)]


# ---- Question-to-Address Mapping Rule, candidate QAM-1 (CA-14, PROPOSED; ESC ratifies or rejects)  X-CONSTRUCTED
def canonical_state(p):
    """State at position p (0..23) of the canonical orbit from (2, 5) under T(a, b) = (b, a + b) mod 9."""
    a, b = 2, 5
    for _ in range(p % 24):
        a, b = b, (a + b) % 9
    return a, b


def question_address(p, k):
    """QAM-1: from the Axis reading (coordinate position p on the canonical 24-cycle, anchor k in 1..9)
    to a Matrix node (domain, seed label, destination).
      seed   : P_k when p is even, its workbook polarity partner when p is odd (the norm reverses at every step);
      domain : (a mod 3, b mod 3, k mod 3), where (a, b) is the canonical state at p.
    A labelling convention, not a structure-preserving map (UP-04a proves none of the additive kind exists).
    Reproducible: two Navigators with the same Axis reading obtain the same node."""
    if not (0 <= p < 24 and 1 <= k <= 9):
        raise ValueError("p in 0..23 and k in 1..9 required")
    a, b = canonical_state(p)
    label = f"P{k}" if p % 2 == 0 else partner_label(f"P{k}")
    dom = (a % 3, b % 3, k % 3)
    src, dst = node(dom, label)
    return {"domain": dom, "seed": label, "destination": dst}


def seed_between(p, q):
    """The unique seed that leads from domain p to domain q (p != q)."""
    return LABEL_OF[LOG[f_sub(q, p)]]


def node_as_map(p, q):
    """The affine map z -> a z + b with 0 -> p, 1 -> q; returned as (a, b)."""
    return f_sub(q, p), p


def apply_map(m, z): return f_add(f_mul(m[0], z), m[1])
def compose_maps(m2, m1): return f_mul(m2[0], m1[0]), f_add(f_mul(m2[0], m1[1]), m2[1])   # m2 after m1


def steiner_rounds():
    """13 rounds, one per seed pair {s, -s}; 9 disjoint lines {p, p+s, p+2s} per round."""
    rounds = []
    for n in range(13):
        v, seen, rnd = SINGER[n], set(), []
        for p in FIELD:
            if p not in seen:
                line = (p, f_add(p, v), f_add(p, f_add(v, v)))
                seen.update(line); rnd.append(line)
        rounds.append(rnd)
    return rounds


def code(p): return "".join(map(str, p))

# ======================================================================= C: comparison
def _check_fields(X, Y):
    if len(X) != len(Y) or not X:
        raise ValueError("X and Y must be non-empty and of equal length")


def ok(y, x, mode="units", tau=8):
    d = y - x
    if mode == "units":     return d in U
    if mode == "symmetric": return abs(d) <= tau
    if mode == "modular":   return d % 9 in U
    raise ValueError(f"unknown tolerance mode {mode!r}")


def compare(X, Y, operator="pooled", mode="units", tau=8, threshold=4, weights=None):
    """Explainable comparison report: operator, parameters, score, threshold, flag, matches."""
    _check_fields(X, Y)
    operator = OPERATOR_ALIASES.get(operator, operator)
    if mode == "symmetric" and tau <= 0:
        raise ValueError("tau must be positive")
    rep = {"operator": operator, "mode": mode, "tau": tau if mode == "symmetric" else None,
           "threshold": threshold, "n": len(X)}
    if operator == "pooled":
        m = [(j, [i for i, y in enumerate(Y) if ok(y, x, mode, tau)]) for j, x in enumerate(X)]
        rep["matches"] = {j: refs for j, refs in m if refs}
        rep["score"] = len(rep["matches"])
    elif operator == "positional":
        rep["matches"] = {i: [i] for i, (x, y) in enumerate(zip(X, Y)) if ok(y, x, mode, tau)}
        rep["score"] = len(rep["matches"])
    elif operator == "matching":
        adj = [[i for i, y in enumerate(Y) if ok(y, x, mode, tau)] for x in X]
        owner = [-1] * len(Y)

        def aug(j, seen):
            for i in adj[j]:
                if i not in seen:
                    seen.add(i)
                    if owner[i] < 0 or aug(owner[i], seen):
                        owner[i] = j; return True
            return False
        for j in range(len(X)):
            aug(j, set())
        rep["matches"] = {owner[i]: [i] for i in range(len(Y)) if owner[i] >= 0}
        rep["score"] = len(rep["matches"])
        rep["competing_references"] = sorted({i for i in range(len(Y))
                                              if sum(i in a for a in adj) > 1})
    elif operator == "weighted":
        w = weights or [1] * len(X)
        if len(w) != len(X) or any(v < 0 for v in w) or sum(w) == 0:
            raise ValueError("weights must be non-negative, same length as X, not all zero")
        if tau <= 0:
            raise ValueError("tau must be positive")
        q = [max(0.0, 1 - abs(y - x) / tau) for x, y in zip(X, Y)]
        rep.update(mode="continuous symmetric closeness", tau=tau, weights=w,
                   quality=[round(v, 3) for v in q],
                   score=round(sum(a * b for a, b in zip(w, q)) / sum(w), 4))
        rep["flag"] = None
        return rep
    else:
        raise ValueError(f"unknown operator {operator!r}")
    rep["flag"] = rep["score"] >= threshold
    return rep

# ======================================================================= T: temporal
def lis_error(x, t, d):
    """Lagged increment stability residual (1 - B)(1 - B^d) x_{t+1}."""
    return x[t + 1] - x[t] - x[t + 1 - d] + x[t - d]


def _mae(x, d, lo, hi):
    ts = range(max(lo, d), hi - 1)
    if len(ts) == 0:
        raise ValueError(f"empty error range for lag {d} in [{lo}, {hi})")
    return st.mean(abs(lis_error(x, t, d)) for t in ts)


def _linfit(ts, xs):
    tm, xm = st.mean(ts), st.mean(xs)
    den = sum((a - tm) ** 2 for a in ts)
    slope = sum((a - tm) * (b - xm) for a, b in zip(ts, xs)) / den if den else 0.0
    return lambda t: xm + slope * (t - tm)


def _skill(x, lags, cut):
    n = len(x)
    best = min(lags, key=lambda d: _mae(x, d, 0, cut))
    test, base = _mae(x, best, cut, n), _mae(x, 1, cut, n)
    return best, (1 - test / base if base else 0.0)


def baselines(x, d, cut):
    """Held-out mean absolute errors of one-step forecasts (v2.3, review: compare with ordinary forecasters).
    lis            Lagged-Increment Model at lag d: x_{t+1} = x_t + x_{t+1-d} - x_{t-d}
    seasonal_naive x_{t+1} = x_{t+1-d}
    persistence    x_{t+1} = x_t
    drift          x_{t+1} = 2 x_t - x_{t-1}   (the lag-1 Lagged-Increment Model)
    train_mean     x_{t+1} = mean of the training part
    train_trend    x_{t+1} = linear trend fitted on the training part"""
    n = len(x); ts = range(max(cut, d + 1), n - 1)
    tr = _linfit(list(range(cut)), x[:cut]); mu = st.mean(x[:cut])
    f = {"lis": lambda t: x[t] + x[t + 1 - d] - x[t - d], "seasonal_naive": lambda t: x[t + 1 - d],
         "persistence": lambda t: x[t], "drift": lambda t: 2 * x[t] - x[t - 1],
         "train_mean": lambda t: mu, "train_trend": lambda t: tr(t + 1)}
    out = {k: round(st.mean(abs(x[t + 1] - g(t)) for t in ts), 4) for k, g in f.items()}
    out["best_forecaster"] = min(f, key=lambda k: out[k])
    out["lis_beats_all_baselines"] = all(out["lis"] < out[k] for k in f if k != "lis")
    return out


def temporal_scan(x, lags=range(2, 25), surrogates=199, seed=11, train=0.6, null="iid", family_tol=0.15,
                  block_len=None):
    """Choose a lag on the training part, judge it on the held-out part against lag 1 (trend only).
    Null models: 'iid'   residuals around a training-fitted trend, shuffled (exchangeable noise);
                 'block' circular block bootstrap of those residuals (keeps short-range order);
                 block_len defaults to the largest scanned lag (24); its calibration is test CX-012.
    Selection correction: every surrogate repeats the whole lag search on its own training part,
    so p accounts for choosing the best of the scanned lags.
    p is a tail probability under the stated null and procedure; with 199 surrogates its floor is 1/200."""
    x = [float(v) for v in x]
    n, lags = len(x), list(lags)
    cut = int(n * train)
    if cut - max(lags) < 10 or n - cut < max(lags) + 10:
        raise ValueError(f"series too short: n={n}, need at least {max(lags) + 10} points in each part")
    best, skill = _skill(x, lags, cut)
    trend = _linfit(list(range(cut)), x[:cut])          # fitted on training data only
    tr = [trend(t) for t in range(n)]
    resid = [a - b for a, b in zip(x, tr)]
    r, k, B = random.Random(seed), 0, (block_len or max(lags))
    for _ in range(surrogates):
        if null == "iid":
            rr = resid[:]; r.shuffle(rr)
        elif null == "block":
            rr = []
            while len(rr) < n:
                s0 = r.randrange(n)
                rr.extend(resid[(s0 + i) % n] for i in range(B))
            rr = rr[:n]
        else:
            raise ValueError(null)
        s = [a + b for a, b in zip(tr, rr)]
        k += _skill(s, lags, cut)[1] >= skill
    p = (k + 1) / (surrogates + 1)
    errs = {d: _mae(x, d, 0, cut) for d in lags}
    # near-optimal lag family (Omega42-T01): lags whose TRAINING error is within the pre-registered
    # tolerance family_tol of the best training error (default 15%)
    family = sorted(d for d in lags if errs[d] <= (1 + family_tol) * errs[best])
    # Candidate Base Lag (Lag-Family Common Divisor): the smallest family lag dividing every family member;
    # if none divides them all, the best lag. A summary, not a proof of the true period.
    base = next((d for d in family if all(m % d == 0 for m in family)), best)
    base_status = "common divisor" if all(m % base == 0 for m in family) else "fallback: best lag (no family member divides all)"
    # Periodicity interpretation (v2.3.1, review 2a55c661 section 4D): conservative reading of one scan.
    #   unsupported : p > 0.05 under this scan's null;
    #   supported   : p <= 0.05 and the Candidate Base Lag is a common divisor of the lag family;
    #   unresolved  : p <= 0.05 but the family has no common divisor in it (the base lag is the fallback).
    # "supported" means the lagged-increment structure repeats at the base lag; it does not name a mechanism.
    interp = "unsupported" if p > 0.05 else ("supported" if base_status == "common divisor" else "unresolved")
    return {"base_lag_status": base_status, "periodicity_interpretation": interp,
            "best": best, "family": family, "candidate_base_lag": base, "fundamental_heuristic": base,
            "family_tol": family_tol,
            "skill_vs_trend": round(skill, 3), "p": round(p, 4), "null": null,
            "train_points": cut, "test_points": n - cut, "block_len": B if null == "block" else None,
            "baselines": baselines(x, best, cut)}

# ======================================================================= G: group-relative templates
class Group:
    def __init__(self, name, elements, op, inv, identity):
        self.name, self.elements, self.op, self.inv, self.e = name, list(elements), op, inv, identity

    def axioms(self):
        E, op = self.elements, self.op
        out = {"closure": all(op(a, b) in E for a in E for b in E),
               "identity": all(op(self.e, a) == a == op(a, self.e) for a in E),
               "inverse": all(op(a, self.inv(a)) == self.e == op(self.inv(a), a) for a in E),
               "associativity": all(op(op(a, b), c) == op(a, op(b, c)) for a in E for b in E for c in E)}
        out["commutative"] = all(op(a, b) == op(b, a) for a in E for b in E)
        return out


Z12 = Group("Z/12 (pitch classes, +)", range(12), lambda a, b: (a + b) % 12, lambda a: (-a) % 12, 0)
UNITS9 = Group("(Z/9)^x (Lower World, *)", U, lambda a, b: a * b % 9,
               lambda a: next(b for b in U if a * b % 9 == 1), 1)
S3 = Group("S3 (permutations of 3, composition)", itertools.permutations(range(3)),
           lambda a, b: tuple(a[b[i]] for i in range(3)),               # a after b
           lambda a: tuple(sorted(range(3), key=lambda i: a[i])), (0, 1, 2))


def template_forecast(group, seq, t, d):
    """r = x_t * x_{t-d}^-1 (left), forecast r * x_{t+1-d}."""
    r = group.op(seq[t], group.inv(seq[t - d]))
    return group.op(r, seq[t + 1 - d])


def template_accuracy(group, seq, d):
    ts = range(d, len(seq) - 1)
    return sum(template_forecast(group, seq, t, d) == seq[t + 1] for t in ts) / len(ts)

# ======================================================================= V: verification
NO_COUNTEREXAMPLE, COUNTEREXAMPLE, INCOMPLETE, INVALID = (
    "NO COUNTEREXAMPLE ON TESTED DOMAIN", "COUNTEREXAMPLE FOUND", "TEST NOT COMPLETED", "TEST INVALID")


def check_relation(f, T, relation, domain, limit=10 ** 6):
    """Check relation(f(T(x)), f(x)) for every x in a finite domain."""
    try:
        for i, x in enumerate(domain):
            if i >= limit:
                return INCOMPLETE, None
            if not relation(f(T(x)), f(x)):
                return COUNTEREXAMPLE, x
        return NO_COUNTEREXAMPLE, None
    except Exception as e:                       # assumptions of the test not met
        return INVALID, repr(e)


def selftest():
    res = {}
    E9 = F9
    res["F9: phi has order 8 (primitive)"] = min(k for k in range(1, 9) if _f9_pow(PHI, k) == (1, 0)) == 8
    res["F9: T(a,b) = (b,a+b) is multiplication by phi"] = all(
        omega_step(v) == f9_mul(v, PHI) for v in E9)
    res["F27: g^3 - g + 1 irreducible over F3"] = poly_irreducible_cubic_f3()
    res["F27: g has order 26 (primitive)"] = element_order(G) == 26
    res["F27: field axioms (exhaustive)"] = all((
        all(f_add(a, ZERO) == a and f_mul(a, ONE) == a and f_add(a, f_neg(a)) == ZERO for a in FIELD),
        all(f_mul(a, f_inv(a)) == ONE for a in FIELD if a != ZERO),
        all(f_mul(a, f_add(b, c)) == f_add(f_mul(a, b), f_mul(a, c)) and
            f_mul(f_mul(a, b), c) == f_mul(a, f_mul(b, c)) and
            f_add(f_add(a, b), c) == f_add(a, f_add(b, c)) for a in FIELD for b in FIELD for c in FIELD),
        all(f_mul(a, b) == f_mul(b, a) and f_add(a, b) == f_add(b, a) for a in FIELD for b in FIELD)))
    res["g^(n+13) = -g^n for all n"] = all(SINGER[(n + 13) % 26] == f_neg(SINGER[n]) for n in range(26))
    res["seed labels: bijection onto 26 nonzero elements"] = (
        len(SEED_LABELS) == 26 and {seed(s) for s in SEED_LABELS} == set(FIELD) - {ZERO})
    res["workbook pairs encoded as antipodes"] = all(
        partner_label(a) == b for a, b in [("P1", "N1"), ("P2", "N2"), ("P3", "N6"), ("P4", "N4"),
                                           ("P5", "N5"), ("P6", "N3"), ("P7", "N7"), ("P8", "N8"),
                                           ("P9", "N9"), ("PU", "NU"), ("PD", "ND"), ("T1", "T3"),
                                           ("T2", "T4")])
    pairs = [(p, q) for p in FIELD for q in FIELD if p != q]
    maps = [node_as_map(p, q) for p, q in pairs]
    res["702 directed pairs <-> 702 affine maps (bijection)"] = (
        len(set(maps)) == 702 and all(apply_map(m, ZERO) == p and apply_map(m, ONE) == q
                                      for m, (p, q) in zip(maps, pairs)))
    res["every directed pair has exactly one seed"] = all(node(p, seed_between(p, q))[1] == q for p, q in pairs)
    res["affine maps closed under composition"] = all(
        compose_maps(m2, m1)[0] != ZERO for m1 in maps[::37] for m2 in maps[::41])
    rounds = steiner_rounds()
    cnt = Counter(frozenset(c) for rnd in rounds for L in rnd for c in itertools.combinations(L, 2))
    res["13 rounds x 9 triples; 351 pairs exactly once"] = (
        len(rounds) == 13 and all(len(r) == 9 and len({p for L in r for p in L}) == 27 for r in rounds)
        and len(cnt) == 351 and set(cnt.values()) == {1})
    rep = compare([15, 14, 27, 5, 13, 22], [6, 2, 16, 5, -4, 8], "matching")
    res["Classic example: pooled 3, matching 2"] = (
        compare([15, 14, 27, 5, 13, 22], [6, 2, 16, 5, -4, 8])["score"] == 3 and rep["score"] == 2)
    norm = lambda v: (v[0] ** 2 + v[0] * v[1] - v[1] ** 2) % 3
    res["N(T x) = -N(x) on F3^2 (relation checker)"] = check_relation(
        norm, omega_step, lambda a, b: a == (-b) % 3, F9)[0] == NO_COUNTEREXAMPLE
    res["N is NOT invariant (checker finds counterexample)"] = check_relation(
        norm, omega_step, lambda a, b: a == b, F9)[0] == COUNTEREXAMPLE
    res["group axioms: Z/12, (Z/9)^x, S3"] = all(
        all(v for k, v in g.axioms().items() if k != "commutative") for g in (Z12, UNITS9, S3))
    return res


def _f9_pow(a, k):
    r = (1, 0)
    for _ in range(k):
        r = f9_mul(r, a)
    return r


if __name__ == "__main__":
    t = selftest()
    for k, v in t.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    print(f"{sum(map(bool, t.values()))}/{len(t)} self-tests pass (Construct X {VERSION})")
    print(compare([15, 14, 27, 5, 13, 22], [6, 2, 16, 5, -4, 8], "matching"))
    ref = [180, 182, 175, 190, 185, 178]
    for name, day in (("normal", [176, 180, 171, 186, 190, 174]),
                      ("drift low", [168, 170, 160, 175, 172, 165]),
                      ("drift high", [192, 194, 187, 202, 197, 190])):
        print(f"oven {name:10s}", compare(day, ref, "positional", "symmetric", tau=6)["score"])
    r = random.Random(3)
    week = [120, 95, 90, 100, 130, 180, 210]
    sales = [week[t % 7] * (1 + 0.002 * t) + r.gauss(0, 8) for t in range(182)]
    for null in ("iid", "block"):
        print("sales", null, temporal_scan(sales, null=null))
    print("linear", temporal_scan([3 * t + 10 for t in range(182)]))
    motif = [0, 4, 7, 4, 2, 5, 9, 5]
    seq = [(m + 5 * (t // 8)) % 12 for t, m in enumerate(motif * 6)]
    print("melody accuracy", {d: round(template_accuracy(Z12, seq, d), 2) for d in (1, 4, 8, 16, 24)})


# ======================================================================= classification and representation (v2.1)
def display(r):
    """Workbook display convention: residue 0 is shown as 9 (CLASSIC-DERIVED)."""
    r %= 9
    return 9 if r == 0 else r


def residue(shown):
    """Inverse of display: a shown digit 1..9 back to its residue 0..8."""
    if shown not in range(1, 10):
        raise ValueError("displayed digits run 1..9")
    return shown % 9


def digital_root(n):
    return 0 if n == 0 else 1 + (n - 1) % 9


def orbits(m):
    """All orbits of T(a, b) = (b, a + b) on (Z/m)^2."""
    seen, out = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen:
                continue
            o, s = [], (a, b)
            while s not in seen:
                seen.add(s); o.append(s); s = (s[1], (s[0] + s[1]) % m)
            out.append(o)
    return out


def norm(v, m): return (v[0] * v[0] + v[0] * v[1] - v[1] * v[1]) % m


def val3(v, m):
    """3-adic valuation of a state in (Z/3^k)^2 (k = log3 m); m itself for the zero state."""
    r = 0   # v2.3.2: no depth cap (2.3.1 stopped at r = 30, wrong beyond 3^30)
    while 3 ** (r + 1) <= m and all(x % (3 ** (r + 1)) == 0 for x in v):
        r += 1
    return r


def lam(v, m):
    """Orbit address Lambda: (r, N(u)^2 mod 3^(k-r)) with v = 3^r u, k = log3 m (Core orbit address)."""
    r = val3(v, m)
    q = m // 3 ** r
    if q == 1:
        return (r, 0)
    u = (v[0] // 3 ** r % q, v[1] // 3 ** r % q)
    return (r, norm(u, q) ** 2 % q)


def is_complete_classifier(m, sig):
    obs = orbits(m)
    sigs = [{sig(s, m) for s in o} for o in obs]
    constant = all(len(x) == 1 for x in sigs)
    distinct = len({next(iter(x)) for x in sigs}) == len(obs)
    return constant and distinct, {"orbits": len(obs), "constant_on_orbits": constant, "distinct_signatures": distinct}


def quadratic_forms_up_to_sign(m=9):
    """Every form q(a,b) = c1 a^2 + c2 ab + c3 b^2 (mod m) with q(T x) = +q(x) or -q(x) for all x."""
    S = [(a, b) for a in range(m) for b in range(m)]
    inv, anti = [], []
    for c1 in range(m):
        for c2 in range(m):
            for c3 in range(m):
                q = lambda v: (c1 * v[0] * v[0] + c2 * v[0] * v[1] + c3 * v[1] * v[1]) % m
                tq = [(q((v[1], (v[0] + v[1]) % m)), q(v)) for v in S]
                if all(a == b for a, b in tq):
                    inv.append((c1, c2, c3))
                if all(a == (-b) % m for a, b in tq):
                    anti.append((c1, c2, c3))
    return inv, anti
