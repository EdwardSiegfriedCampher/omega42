#!/usr/bin/env python3
"""transformability.py -- TP-01 and ME-02.
ME-02 and ME-03 recomputed, with their counterparts in the law.
Companion 233.13; APE-503 to APE-505.

Two models, kept apart:
  COARSE (ME-02, a dissipative description of a habit):  p(t+1) = s(a + beta p(t) - gamma u)
      fixed points, their stability, the bistable band of a, the tipping intervention and hysteresis.
  EXACT (the law of Omega42, conservative):  v(t+1) = T v(t) + u(t) b over (Z/3^k)^2
      controllability of a one-direction choice b (det[b, T b] = N(b)), the reachable set, the
      Transformability Profile TP-01 read in the law.
Standard library only.

    python3 tools/transformability.py --selftest
    python3 tools/transformability.py --report
"""
import itertools, json, math, sys

sig = lambda z: 1 / (1 + math.exp(-z))


# ---- COARSE: the logistic habit model of ME-02 ----
def fixed_points(a, beta, n=40000):
    f = lambda p: sig(a + beta * p) - p
    xs = [i / n for i in range(1, n)]; out = []
    for x, y in zip(xs, xs[1:]):
        if f(x) == 0: out.append(x); continue
        if f(x) * f(y) < 0:
            lo, hi = x, y
            for _ in range(60):
                mid = (lo + hi) / 2
                if f(lo) * f(mid) <= 0: hi = mid
                else: lo = mid
            out.append((lo + hi) / 2)
    return [(p, beta * p * (1 - p) < 1) for p in out]          # (fixed point, stable?)


def bistable_band(beta):
    """For beta > 4: the values of a between which three fixed points exist (saddle-node boundaries)."""
    if beta <= 4: return None
    r = math.sqrt(1 - 4 / beta)
    ps = ((1 - r) / 2, (1 + r) / 2)
    a = sorted(math.log(p / (1 - p)) - beta * p for p in ps)
    return {"p_boundaries": [round(p, 4) for p in ps], "a_band": [round(x, 4) for x in a]}


def hysteresis(a=-3.0, beta=6.0, steps=100, settle=400):
    """Ramp the intervention up from 0 to 1 and back, starting in the high state; return where the high state is lost
    and the state after the support is removed."""
    p, lost = 0.93, None
    for k in range(steps + 1):
        g = k / steps
        for _ in range(settle): p = sig(a + beta * p - g)
        if lost is None and p < 0.5: lost = g
    for k in range(steps, -1, -1):
        g = k / steps
        for _ in range(settle): p = sig(a + beta * p - g)
    return {"high_state_lost_at": lost, "after_support_removed": round(p, 4)}


# ---- EXACT: the law with a one-direction choice ----
def T(v, m): return (v[1], (v[0] + v[1]) % m)
def N(v, m): return (v[0] * v[0] + v[0] * v[1] - v[1] * v[1]) % m


def controllable(b, m):
    """A choice always made along b reaches every state iff det[b, T b] = N(b) is a unit (not divisible by 3)."""
    return N(b, m) % 3 != 0


def reachable_in_two(b, m):
    Tb = T(b, m)
    return {((u0 * Tb[0] + u1 * b[0]) % m, (u0 * Tb[1] + u1 * b[1]) % m) for u0 in range(m) for u1 in range(m)}


def history_information(m=9):
    """I(a_next; a_prev | a_now) when only the first coordinate is observed, uniform over states (bits)."""
    from collections import Counter
    c = Counter(((v[1] - v[0]) % m, v[0], v[1]) for v in itertools.product(range(m), repeat=2))
    H = lambda d: -sum(n / sum(d.values()) * math.log2(n / sum(d.values())) for n in d.values())
    marg = lambda idx: Counter({k: 0 for k in []}) or sum((Counter({tuple(key[i] for i in idx): n}) for key, n in c.items()), Counter())
    return H(marg((1, 2))) - H(marg((1,))) - (H(c) - H(marg((0, 1))))


def profile_in_the_law(m=9):
    """TP-01 (ME-03) read inside the law: each dimension kept apart, none summed."""
    dirs = [b for b in itertools.product(range(m), repeat=2) if b != (0, 0)]
    return {
        "A_accessibility": "every state is reachable: one added term changes the orbit in 0.736 to 0.990 of cases (H-029); two choices along a controlling direction reach any state",
        "C_controllability": "%d of %d one-direction choices are controlling (N(b) a unit); the rest, the multiples of 3, cannot steer every coordinate" % (sum(controllable(b, m) for b in dirs), len(dirs)),
        "P_persistence": "1 inside the law: the law conserves N^2 and the orbit, so a reached orbit is kept with no further support (233.12 M1)",
        "D_historical_decoupling": "none at the level of the state: every past choice persists in its present form (233.2); full at the level of the orbit once a new orbit is reached",
        "K_cost": "one added term to change the orbit; two to reach a chosen state along a controlling direction",
        "R_risk": "not computed (normative; Companion 233.6)",
    }


def selftest():
    ok = []
    fp = fixed_points(-3.0, 6.0)
    ok.append(("ME-02 fixed points 0.071 (stable), 0.5 (unstable), 0.929 (stable) at a = -3, beta = 6",
               [round(p, 3) for p, _ in fp] == [0.071, 0.5, 0.929] and [s for _, s in fp] == [True, False, True]))
    band = bistable_band(6.0)
    ok.append(("ME-02 bistable band: p = 0.2113, 0.7887 and a in (-3.415, -2.585)", band["p_boundaries"] == [0.2113, 0.7887] and band["a_band"] == [-3.4151, -2.5849]))
    ok.append(("ME-02 no bistability for beta <= 4", bistable_band(4.0) is None))
    h = hysteresis()
    ok.append(("ME-02 hysteresis: the high state is lost at gamma u = 0.42 and does not return when the support is removed", h["high_state_lost_at"] == 0.42 and h["after_support_removed"] < 0.1))
    for m in (9, 27):
        dirs = [b for b in itertools.product(range(m), repeat=2) if b != (0, 0)]
        good = all(((b[0] * T(b, m)[1] - b[1] * T(b, m)[0]) % m == N(b, m)) and ((len(reachable_in_two(b, m)) == m * m) == controllable(b, m)) for b in dirs)
        ok.append(("ME-03 in the law, mod %d: det[b, T b] = N(b), and two choices along b reach every state iff N(b) is a unit" % m, good))
    ok.append(("ME-01 history information with one coordinate observed is log2 9 bits", abs(history_information(9) - math.log2(9)) < 1e-9))
    for name, g in ok: print(("  ok   " if g else "  FAIL ") + name)
    good = all(g for _, g in ok); print("TRANSFORMABILITY SELFTEST:", "PASS" if good else "FAIL"); return good


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]: sys.exit(0 if selftest() else 1)
    if a == ["--report"]:
        print(json.dumps({"coarse": {"fixed_points_a-3_beta6": [[round(p, 4), s] for p, s in fixed_points(-3, 6)], "band_beta6": bistable_band(6.0), "hysteresis": hysteresis()},
                          "exact": {"history_bits_one_coordinate": round(history_information(9), 4), "profile_TP01": profile_in_the_law(9)}}, indent=1)); sys.exit(0)
    print(__doc__)
