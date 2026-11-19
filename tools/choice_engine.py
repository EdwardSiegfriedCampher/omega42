#!/usr/bin/env python3
"""choice_engine.py -- the Choice Engine.
Companion Part 233.
The two layers of existence as one affine law on (Z/m)^2.

  default layer      v -> T v,        T(a, b) = (b, a + b)       the law: it keeps every state on its orbit (Lambda fixed)
  meaningful layer   v -> T v + c     c = an added term, a choice  only an added term can move a state to another orbit
Solved:  v(t) = T^t v(0) + sum over s < t of T^(t-1-s) c(s)
  v(0)      the starting state, given (the genetic channel)
  the sum   every earlier choice, carried forward and transformed by the law (the inherited sum)
Because T is linear, the inherited sum splits exactly into one part per channel of transmission. Each channel is tracked
apart and carries its own evidence grade, so channels are never treated as interchangeable (Companion 233.3).
The engine computes historical significance only; experiential and normative significance are not computed (233.6).

    python3 tools/choice_engine.py --selftest
    python3 tools/choice_engine.py --demo
    python3 tools/choice_engine.py --orbit-change M [SAMPLES SEED]   share of single choices that change the orbit
Standard library only.
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import construct_x as cx

# Evidence grade of each channel for human transmission (Companion 233.3; sources there). Metadata, never computed.
CHANNELS = {
    "genetic": "established",
    "epigenetic": "contested for transmission across human generations (Bird 2024)",
    "behavioral": "established (social learning, developmental psychology)",
    "cultural": "established (cultural evolution, gene-culture coevolution)",
    "institutional": "established (history, economics, sociology)",
    "personal": "the agent's own choices",
}


def T(v, m): return (v[1], (v[0] + v[1]) % m)
def add(u, v, m): return ((u[0] + v[0]) % m, (u[1] + v[1]) % m)
def neg(v, m): return ((-v[0]) % m, (-v[1]) % m)


def T_pow(v, n, m):
    for _ in range(n): v = T(v, m)
    return v


def run(v0, choices, steps, m):
    """choices: {t: [(channel, c), ...]} applied after the law at step t. Returns the path, Lambda per step and channel parts."""
    v = v0; part = {ch: (0, 0) for ch in CHANNELS}; part["genetic"] = v0
    path, lams = [v0], [cx.lam(v0, m)]
    for t in range(steps):
        v = T(v, m); part = {ch: T(p, m) for ch, p in part.items()}
        for ch, c in choices.get(t, []):
            if ch not in CHANNELS: raise ValueError("unknown channel %s" % ch)
            v = add(v, c, m); part[ch] = add(part[ch], c, m)
        path.append(v); lams.append(cx.lam(v, m))
    return {"path": path, "lambda": lams, "parts": part}


def effect(c, s, t, m):
    """The effect at time t of a choice c made at step s (applied after the law at s): T^(t-1-s) c."""
    return T_pow(c, t - 1 - s, m)


def cancelling_choice(c, s, t, m):
    """The added term at step t that cancels, from t + 1 on, a choice c made at step s: minus its present form T^(t-s) c."""
    return neg(T_pow(c, t - s, m), m)


# ---- The mathematics of the meaningful layer (Companion 233.12) ----
def N(v, m): return (v[0] * v[0] + v[0] * v[1] - v[1] * v[1]) % m
def B(v, c, m): return (2 * v[0] * c[0] + v[0] * c[1] + v[1] * c[0] - 2 * v[1] * c[1]) % m


def delta_norm(v, c, m):
    """How a choice c changes the norm at state v: N(v + c) - N(v) = B(v, c) + N(c) (context term + intrinsic term)."""
    return (B(v, c, m) + N(c, m)) % m


def habit_center(c, m):
    """The centre of the constant habit v -> T v + c: v* = -T c, because (I - T)^(-1) = -T (T^2 = T + I)."""
    return neg(T(c, m), m)


def _mat_pow(p, m):
    R, M = ((1, 0), (0, 1)), ((0, 1), (1, 1))
    for _ in range(p):
        R = ((R[0][0] * M[0][0] + R[0][1] * M[1][0]) % m, (R[0][0] * M[0][1] + R[0][1] * M[1][1]) % m), \
            ((R[1][0] * M[0][0] + R[1][1] * M[1][0]) % m, (R[1][0] * M[0][1] + R[1][1] * M[1][1]) % m)
    return R


def regime(p, m):
    """What a choice repeated every p steps does: resonance (T^p = I, it accumulates), anti-resonance (T^p = -I, it
    cancels every other period), recentred (I - T^p invertible: the pattern settles round a new centre), or partial."""
    P = _mat_pow(p, m)
    if P == ((1, 0), (0, 1)): return "resonance"
    if P == ((m - 1, 0), (0, m - 1)): return "anti-resonance"
    d = ((1 - P[0][0]) * (1 - P[1][1]) - P[0][1] * P[1][0]) % m
    return "recentred" if d % 3 else "partial"


# ---- Relations and consensus (Companion 233.15) ----
def relation_step(v, w, k, m):
    """Two people under the law with symmetric scalar influence k: v' = T v + k w, w' = T w + k v."""
    return add(T(v, m), (k * w[0] % m, k * w[1] % m), m), add(T(w, m), (k * v[0] % m, k * v[1] % m), m)


def scalar_consensus_ever(m, k, steps=None):
    """Does any pair of distinct states reach agreement under symmetric scalar influence k? (exhaustive)"""
    import itertools
    steps = steps or 8 * m
    S = list(itertools.product(range(m), repeat=2))
    for v in S:
        for w in S:
            if v == w: continue
            a, b = v, w
            for _ in range(steps):
                a, b = relation_step(a, b, k, m)
                if a == b: return True
    return False


def agreeing_choice(v, w, k, m):
    """The one added term that makes v agree with w at the next step: -(T - k)(v - w)."""
    d = add(v, neg(w, m), m)
    return neg(add(T(d, m), neg((k * d[0] % m, k * d[1] % m), m), m), m)


def real_consensus_radius():
    """Over the reals, with each person following the law and pulled toward the other by a scalar a, the difference
    evolves by T - 2a; its spectral radius is at least sqrt(5)/2 for every a, so averaging never yields consensus."""
    phi = (1 + 5 ** 0.5) / 2; psi = -1 / phi
    return min(max(abs(phi - x), abs(psi - x)) for x in [i / 10000 for i in range(-30000, 30001)])


def reachable_count(dirs, steps, m):
    """States reachable from 0 in `steps` steps when choices are any multiple of a direction in `dirs` (Companion 233.17)."""
    R = {(0, 0)}
    for _ in range(steps):
        R = {add(T(v, m), (u * b[0] % m, u * b[1] % m), m) for v in R for b in dirs for u in range(m)}
    return len(R)


def reading_information(m=9):
    """Bits of the orbit address Lambda carried by one reading (one coordinate), by both, and by N (Companion 233.19)."""
    import itertools, math
    from collections import Counter
    S = list(itertools.product(range(m), repeat=2)); L = {v: cx.lam(v, m) for v in S}
    H = lambda c: -sum(n / sum(c.values()) * math.log2(n / sum(c.values())) for n in c.values())
    HL = H(Counter(L.values()))
    I = lambda f: HL + H(Counter(f(v) for v in S)) - H(Counter((L[v], f(v)) for v in S))
    return {"H_Lambda": HL, "one_reading": I(lambda v: v[0]), "both_readings": I(lambda v: v), "norm": I(lambda v: N(v, m))}


def orbit_change_share(m, samples=None, seed=29):
    S = [(a, b) for a in range(m) for b in range(m)]
    if samples is None:
        pairs = ((v, o) for v in S for o in S if o != (0, 0)); n = len(S) * (len(S) - 1)
    else:
        rng = random.Random(seed); n = samples
        pairs = (((rng.randrange(m), rng.randrange(m)), o) for o in
                 iter(lambda: (rng.randrange(m), rng.randrange(m)), None))
        pairs = ((v, o) for (v, o), _ in zip(((v, o) for v, o in pairs if o != (0, 0)), range(n)))
    ch = sum(cx.lam(add(v, o, m), m) != cx.lam(v, m) for v, o in pairs)
    return ch, n


def selftest():
    ok = []
    for m in (9, 27):
        S = [(a, b) for a in range(m) for b in range(m)]
        ok.append(("the law keeps Lambda, mod %d" % m, all(cx.lam(T(v, m), m) == cx.lam(v, m) for v in S)))
    m = 9; v0 = (1, 0)
    base = run(v0, {}, 60, m)["path"]; ch = run(v0, {3: [("cultural", (0, 1))]}, 60, m)["path"]
    gap = [add(b, neg(a, m), m) for a, b in zip(base, ch)]
    ok.append(("a one-time choice never fades", all(g != (0, 0) for g in gap[4:])))
    ok.append(("its gap returns with the period 24 (mod 9)", gap[4] == gap[28] == gap[52] and all(gap[4] != gap[4 + k] for k in range(1, 24))))
    ok.append(("effect() matches the run", all(gap[t] == effect((0, 1), 3, t, m) for t in range(4, 60))))
    c = cancelling_choice((0, 1), 3, 20, m)
    fixed = run(v0, {3: [("cultural", (0, 1))], 20: [("personal", c)]}, 60, m)["path"]
    ok.append(("the cancelling choice restores the unchosen path", fixed[21:] == base[21:] and fixed[20] != base[20]))
    r = run((2, 5), {1: [("behavioral", (1, 1))], 4: [("cultural", (0, 2)), ("epigenetic", (1, 0))], 7: [("personal", (3, 3))]}, 30, m)
    tot = (0, 0)
    for p in r["parts"].values(): tot = add(tot, p, m)
    ok.append(("the channel parts sum exactly to the state", tot == r["path"][-1]))
    try:
        run(v0, {0: [("fate", (1, 0))]}, 2, m); ok.append(("an unknown channel is refused", False))
    except ValueError:
        ok.append(("an unknown channel is refused", True))
    ch9, n9 = orbit_change_share(9); ch27, n27 = orbit_change_share(27)
    ok.append(("orbit-change share 4768/6480 (mod 9) and 482992/530712 (mod 27)", (ch9, n9, ch27, n27) == (4768, 6480, 482992, 530712)))
    S9 = [(a, b) for a in range(9) for b in range(9)]
    ok.append(("the law flips the sign of the norm, N(T v) = -N(v), so N^2 is conserved", all(N(T(v, 9), 9) == (-N(v, 9)) % 9 for v in S9)))
    ok.append(("a choice changes the norm by B(v, c) + N(c)", all(N(add(v, c, 9), 9) == (N(v, 9) + delta_norm(v, c, 9)) % 9 for v in S9 for c in S9)))
    ok.append(("the centre of a constant habit c is -T c", all(add(T(habit_center(c, 9), 9), c, 9) == habit_center(c, 9) for c in S9)))
    ok.append(("regimes mod 9: resonance at 24, anti-resonance at 12, partial at 8 and 16, recentred otherwise",
               [p for p in range(1, 25) if regime(p, 9) == "resonance"] == [24] and [p for p in range(1, 25) if regime(p, 9) == "anti-resonance"] == [12]
               and [p for p in range(1, 25) if regime(p, 9) == "partial"] == [8, 16]))
    ok.append(("no symmetric scalar influence k mod 9 ever brings two different states to agreement", not any(scalar_consensus_ever(9, k) for k in range(9))))
    ok.append(("the difference norm is scaled by k^2 - k - 1, never divisible by 3", all(N(add(T(d, 9), neg((k * d[0] % 9, k * d[1] % 9), 9), 9), 9) == ((k * k - k - 1) * N(d, 9)) % 9 for k in range(9) for d in S9) and all((k * k - k - 1) % 3 for k in range(3))))
    ok.append(("one agreeing choice makes two states equal at the next step", all((lambda vw: vw[0] == vw[1])((add(relation_step(v, w, 1, 9)[0], agreeing_choice(v, w, 1, 9), 9), relation_step(v, w, 1, 9)[1])) for v in S9[::5] for w in S9[::7])))
    ok.append(("over the reals the least spectral radius of T - 2a is sqrt(5)/2 = 1.118", abs(real_consensus_radius() - 5 ** 0.5 / 2) < 1e-4))
    ok.append(("purpose and agency: one controlling direction reaches all 81 states in 2 steps; a direction of norm 0 mod 3 stays in 9 states after 24 steps", reachable_count([(1, 0)], 2, 9) == 81 and reachable_count([(3, 0)], 24, 9) == 9))
    ri = reading_information(9)
    ok.append(("one reading carries 0.319 of the invariant's 1.968 bits; both readings carry all; one reading over two steps recovers the state",
               abs(ri["one_reading"] - 0.319) < 1e-3 and abs(ri["both_readings"] - ri["H_Lambda"]) < 1e-9 and abs(ri["H_Lambda"] - 1.968) < 1e-3
               and all((v[0], T(v, 9)[0]) == v for v in S9)))
    for name, good in ok: print(("  ok   " if good else "  FAIL ") + name)
    good = all(g for _, g in ok); print("CHOICE ENGINE SELFTEST:", "PASS" if good else "FAIL"); return good


def demo():
    m = 9; v0 = (1, 0)
    choices = {2: [("cultural", (0, 1))], 10: [("behavioral", (2, 0))], 30: [("personal", cancelling_choice((0, 1), 2, 30, m))]}
    r = run(v0, choices, 48, m)
    print(json.dumps({"lambda_path": [list(x) for x in r["lambda"][::4]], "parts_at_end": {k: list(v) for k, v in r["parts"].items()},
                      "channel_grades": CHANNELS}, indent=1))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]: sys.exit(0 if selftest() else 1)
    if a == ["--demo"]: demo(); sys.exit(0)
    if a and a[0] == "--orbit-change":
        m = int(a[1]); smp = int(a[2]) if len(a) > 2 else None; sd = int(a[3]) if len(a) > 3 else 29
        c, n = orbit_change_share(m, smp, sd); print(json.dumps({"m": m, "changed": c, "of": n, "share": round(c / n, 6)})); sys.exit(0)
    print(__doc__)
