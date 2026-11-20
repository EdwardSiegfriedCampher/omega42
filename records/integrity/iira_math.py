"""iira_math.py -- O42-IIRA-MATH-01: the machine-verifiable mathematics of the Information Integrity initiative.

Every module states its definition in the docstring, implements it in plain Python (standard library only) and checks a worked
example. Any AI or person can run it, translate it into another language and compare the printed results
(docs/IIRA_MATH_01.md gives the verification contract and the three verification levels). Proposed by ChatGPT 6 (OpenAI),
relayed by the Originator, 20 November 2026; implemented and checked by the Navigator (claude-opus-5-5).

The modules are established mathematics (verification levels 1 and 2). Whether they, or Omega42's own 81-state structure,
help with real information-integrity problems is level 3 and is untested (H-IIE01 to H-IIE06).

  python3 records/integrity/iira_math.py            the verification report (every module, its inputs and its result)
  python3 records/integrity/iira_math.py --selftest the assertions only; exit status 0 when all hold
"""
import math
import sys

MODULUS = 9


# M1 -- the Omega42 law. T(a, b) = (b, a + b) mod 9, matrix A = [[0, 1], [1, 1]], det A = -1 = 8 mod 9, a unit,
# so T is invertible with T^-1(a, b) = (b - a, a) mod 9.
def transform(s):
    a, b = s
    return (b % MODULUS, (a + b) % MODULUS)


def inverse_transform(s):
    a, b = s
    return ((b - a) % MODULUS, a % MODULUS)


def cycles():
    left, out = {(a, b) for a in range(MODULUS) for b in range(MODULUS)}, []
    while left:
        c, x = [], min(left)
        while x not in c:
            c.append(x); x = transform(x)
        out.append(c); left -= set(c)
    return out


# M2 -- robust z-score. z_r(x) = 0.6745 (x - median X) / MAD X, MAD X = median |x_i - median X|.
def median(v):
    v = sorted(v); n = len(v)
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2


def robust_z(x, ref):
    m = median(ref); mad = median([abs(r - m) for r in ref])
    if mad == 0: raise ValueError('MAD is zero: the reference has no spread')
    return 0.6745 * (x - m) / mad


# M3 -- Jensen-Shannon divergence, base 2. JSD(P, Q) = 1/2 KL(P || M) + 1/2 KL(Q || M), M = (P + Q) / 2; 0 <= JSD <= 1.
def kl2(p, q):
    return sum(pi * math.log2(pi / qi) for pi, qi in zip(p, q) if pi > 0)


def jsd(p, q):
    m = [(a + b) / 2 for a, b in zip(p, q)]
    return kl2(p, m) / 2 + kl2(q, m) / 2


# M4 -- effective number of independent source groups. N_eff = 1 / sum w_k^2, w_k >= 0, sum w_k = 1.
def effective_source_count(w):
    if not w or any(x < 0 for x in w) or abs(sum(w) - 1) > 1e-12: raise ValueError('weights must be non-negative and sum to 1')
    return 1 / sum(x * x for x in w)


# M5 -- Bayesian evidence in odds form. posterior odds = prior odds x product of likelihood ratios, valid only when the
# pieces of evidence are conditionally independent given the hypothesis; probability = odds / (1 + odds).
def posterior(prior_odds, ratios):
    o = prior_odds
    for r in ratios: o *= r
    return o, o / (1 + o)


# M6 -- claim transformation. A claim is c = (assertion strength, scope, causal strength) on a 0..4 ordinal scale;
# d = Euclidean distance; D_path = sum of step distances, D_direct = d(C_0, C_n); D_path >= D_direct always
# (triangle inequality), with equality only when every step moves in the same direction.
def dist(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def path_and_direct(chain):
    return sum(dist(chain[i - 1], chain[i]) for i in range(1, len(chain))), dist(chain[0], chain[-1])


# M7 -- linear propagation. x(t+1) = W x(t), W row-stochastic (W_ij >= 0, rows sum to 1).
def step(W, x):
    return [sum(W[i][j] * x[j] for j in range(len(x))) for i in range(len(W))]


# M8 -- provenance completeness. P_c = verified applicable provenance fields / total applicable fields.
def provenance_completeness(verified, total):
    return verified / total


# M9 -- uncertainty. H(X) = -sum p_i log2 p_i over candidate explanations, in bits.
def entropy(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


# M10 -- the 81-state information map (an experimental construction, MATH-IIRA-01). Two characteristics, each graded
# on nine defined levels 0..8, give a state (a, b) in (Z/9)^2; the map reports the loop of T that holds it. The map is
# well defined; whether the loop carries any information about integrity is the open hypothesis H-IIE06.
def loop_of(state, cs):
    for k, c in enumerate(cs):
        if state in c: return k, len(c)


def run():
    R = []
    def chk(module, label, value, ok):
        R.append((module, label, value, bool(ok)))
    cs = cycles(); S = [(a, b) for a in range(9) for b in range(9)]
    chk('M1', 'states', len(S), len(S) == 81)
    chk('M1', 'T is invertible (T^-1 T = identity on all 81)', True, all(inverse_transform(transform(s)) == s for s in S))
    chk('M1', 'det A mod 9', (0 * 1 - 1 * 1) % 9, (0 * 1 - 1 * 1) % 9 == 8 and math.gcd(8, 9) == 1)
    chk('M1', 'loop lengths', sorted(len(c) for c in cs), sorted(len(c) for c in cs) == [1, 8, 24, 24, 24])
    chk('M1', 'fixed point', [c[0] for c in cs if len(c) == 1], [c[0] for c in cs if len(c) == 1] == [(0, 0)])
    o, x = [], (1, 2)
    for _ in range(5): o.append(x); x = transform(x)
    chk('M1', 'orbit from (1, 2)', o, o == [(1, 2), (2, 3), (3, 5), (5, 8), (8, 4)])
    z = robust_z(20, [8, 9, 10, 10, 11, 12, 13])
    chk('M2', 'robust z of 20 against [8..13] (median 10, MAD 1)', round(z, 4), abs(z - 6.745) < 1e-12)
    p, q = [0.5, 0.3, 0.2], [0.2, 0.3, 0.5]
    j = jsd(p, q)
    chk('M3', 'JSD([.5,.3,.2], [.2,.3,.5]) in bits', round(j, 6), 0 <= j <= 1 and abs(jsd(p, p)) < 1e-15 and abs(j - jsd(q, p)) < 1e-15)
    chk('M3', 'JSD of disjoint distributions = 1', round(jsd([1, 0], [0, 1]), 12), abs(jsd([1, 0], [0, 1]) - 1) < 1e-12)
    chk('M4', 'N_eff, one source group', effective_source_count([1.0]), effective_source_count([1.0]) == 1)
    chk('M4', 'N_eff, five equal groups', round(effective_source_count([0.2] * 5), 12), abs(effective_source_count([0.2] * 5) - 5) < 1e-12)
    chk('M4', 'N_eff, groups of 6, 2, 2 of ten', round(effective_source_count([0.6, 0.2, 0.2]), 4), abs(effective_source_count([0.6, 0.2, 0.2]) - 1 / 0.44) < 1e-12)
    po, pp = posterior(1, [3, 4])
    chk('M5', 'two independent pieces, LR 3 and 4: odds, probability', (po, round(pp, 4)), po == 12 and abs(pp - 12 / 13) < 1e-12)
    do, dp = posterior(1, [3])
    chk('M5', 'second piece only copies the first: odds, probability', (do, round(dp, 4)), do == 3 and abs(dp - 0.75) < 1e-12)
    chain = [(1, 2, 0), (2, 2, 1), (3, 3, 3), (4, 3, 4)]
    path, direct = path_and_direct(chain)
    chk('M6', 'd(C0, C3) = sqrt 26', round(direct, 4), abs(direct - math.sqrt(26)) < 1e-12)
    chk('M6', 'D_path >= D_direct (triangle inequality)', (round(path, 4), round(direct, 4)), path >= direct - 1e-12)
    straight = [(0, 0, 0), (1, 1, 1), (2, 2, 2)]
    sp, sd = path_and_direct(straight)
    chk('M6', 'equality for steps in one direction', (round(sp, 4), round(sd, 4)), abs(sp - sd) < 1e-12)
    W = [[0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5]]
    x1 = step(W, [1, 0, 0]); x2 = step(W, x1)
    chk('M7', 'x(1), x(2) from x(0) = (1, 0, 0)', (x1, x2), x1 == [0.5, 0, 0.5] and x2 == [0.25, 0.25, 0.5])
    x = [1, 0, 0]
    for _ in range(60): x = step(W, x)
    chk('M7', 'x(60): this W is doubly stochastic, so exposure evens out to 1/3', [round(v, 6) for v in x], all(abs(v - 1 / 3) < 1e-9 for v in x))
    chk('M8', 'P_c with 4 of 5 fields verified', provenance_completeness(4, 5), provenance_completeness(4, 5) == 0.8)
    h = entropy([0.5, 0.3, 0.2])
    chk('M9', 'H(0.5, 0.3, 0.2) in bits', round(h, 4), abs(h - 1.4854752972273344) < 1e-12)
    counts = {}
    for s in S: counts[loop_of(s, cs)[1]] = counts.get(loop_of(s, cs)[1], 0) + 1
    chk('M10', 'states per loop length under the information map', sorted(counts.items()), counts == {1: 1, 8: 8, 24: 72})
    chk('M10', 'example: evidence 2, independence 5 lands on', loop_of((2, 5), cs)[1], loop_of((2, 5), cs)[1] == 24)
    return R


if __name__ == '__main__':
    R = run(); bad = [r for r in R if not r[3]]
    if '--selftest' not in sys.argv:
        print('O42-IIRA-MATH-01 VERIFICATION REPORT (levels 1 and 2: arithmetic and mathematics; level 3, usefulness, is untested)')
        for m, label, value, ok in R: print('%-4s %-62s %-40s %s' % (m, label, value, 'PASS' if ok else 'FAIL'))
    print('IIRA MATH SELFTEST: %s (%d checks, %d failed)' % ('PASS' if not bad else 'FAIL', len(R), len(bad)))
    sys.exit(1 if bad else 0)
