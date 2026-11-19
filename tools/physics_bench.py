#!/usr/bin/env python3
"""physics_bench.py -- the PHB-01 known-answer benchmark.
Part of the Physics Initiative (research/physics/INITIATIVE.md section 10).

Five established results reproduced by computation, each beside a control that must fail:
  B1 Noether      rotation invariance of the Lagrangian -> angular momentum conserved (control: a potential that breaks it)
  B2 Geodesic     the Euler-Lagrange equations of L = (th'^2 + sin^2 th ph'^2)/2, taken numerically from L itself,
                  vanish on a great circle (control: a circle of latitude)
  B3 Entropy      von Neumann entropy of one qubit of a Bell pair = ln 2 (control: a product state, 0)
  B4 Black hole   S = A/4 = 4 pi M^2 and T_H = 1/(8 pi M) satisfy dS/dM = 1/T_H (units G = c = hbar = k_B = 1)
                  (control: a wrong temperature 1/(4 pi M) fails)
  B5 Limit        relativistic kinetic energy -> m v^2 / 2, with the leading correction (3/4)(v/c)^2
                  (control: a wrong correction (1/2)(v/c)^2 fails)
This tests the toolkit, not the Navigator's knowledge: the code was written knowing the answers (CONSTRUCTIONAL, Core Part 3.18).
Standard library only (SymPy is not installed in this environment).

    python3 tools/physics_bench.py            JSON of all results
    python3 tools/physics_bench.py --selftest
"""
import json, math, sys


def b1_noether(steps=20000, dt=1e-3):
    def run(eps):
        x, y, vx, vy = 1.0, 0.0, 0.0, 1.1
        def acc(x, y):
            r3 = (x * x + y * y) ** 1.5
            return -x / r3 - eps, -y / r3          # V = -1/r + eps x
        ax, ay = acc(x, y); L0 = x * vy - y * vx; worst = 0.0
        for _ in range(steps):                     # velocity Verlet (symplectic)
            vx += 0.5 * dt * ax; vy += 0.5 * dt * ay
            x += dt * vx; y += dt * vy
            ax, ay = acc(x, y)
            vx += 0.5 * dt * ax; vy += 0.5 * dt * ay
            worst = max(worst, abs((x * vy - y * vx) - L0) / abs(L0))
        return worst
    inv, broken = run(0.0), run(0.1)
    return {"drift_invariant": inv, "drift_broken": broken, "pass": inv < 1e-9 and broken > 1e-3}


def _el_residual(path, t, h=1e-4):
    """Euler-Lagrange residuals d/dt dL/dq' - dL/dq for L(q, q') = (th'^2 + sin^2 th ph'^2)/2, all derivatives numerical."""
    L = lambda th, ph, dth, dph: 0.5 * (dth * dth + math.sin(th) ** 2 * dph * dph)
    def q(t): return path(t)
    def qd(t): a, b = q(t + h), q(t - h); return ((a[0] - b[0]) / (2 * h), (a[1] - b[1]) / (2 * h))
    def dL(t, i, wrt_vel):
        (th, ph), (dth, dph) = q(t), qd(t); args = [th, ph, dth, dph]; k = i + (2 if wrt_vel else 0); e = 1e-6
        up = list(args); dn = list(args); up[k] += e; dn[k] -= e
        return (L(*up) - L(*dn)) / (2 * e)
    return max(abs((dL(t + h, i, True) - dL(t - h, i, True)) / (2 * h) - dL(t, i, False)) for i in (0, 1))


def b2_geodesic():
    a = 0.7   # great circle through the equator at inclination a
    def great(s):
        x, y, z = math.cos(s), math.sin(s) * math.cos(a), math.sin(s) * math.sin(a)
        return (math.acos(z), math.atan2(y, x))
    lat = lambda s: (1.0, s)                           # circle of latitude th = 1: not a geodesic
    ts = [0.3 + 0.2 * k for k in range(8)]
    g, c = max(_el_residual(great, t) for t in ts), max(_el_residual(lat, t) for t in ts)
    return {"residual_great_circle": g, "residual_latitude": c, "pass": g < 1e-4 and c > 0.1}


def _entropy_qubit_a(psi):
    """psi = [c00, c01, c10, c11] (real); von Neumann entropy of the reduced state of qubit A, in nats."""
    r00 = psi[0] ** 2 + psi[1] ** 2; r11 = psi[2] ** 2 + psi[3] ** 2; r01 = psi[0] * psi[2] + psi[1] * psi[3]
    tr, det = r00 + r11, r00 * r11 - r01 * r01
    d = math.sqrt(max(tr * tr / 4 - det, 0.0)); ev = [tr / 2 + d, tr / 2 - d]
    return -sum(p * math.log(p) for p in ev if p > 1e-15)


def b3_entropy():
    s = 1 / math.sqrt(2)
    bell, prod = _entropy_qubit_a([s, 0, 0, s]), _entropy_qubit_a([s, s, 0, 0])
    return {"bell": bell, "ln2": math.log(2), "product": prod, "pass": abs(bell - math.log(2)) < 1e-12 and abs(prod) < 1e-12}


def b4_black_hole():
    S = lambda M: 4 * math.pi * M * M
    out = {}
    for name, T in (("hawking", lambda M: 1 / (8 * math.pi * M)), ("control", lambda M: 1 / (4 * math.pi * M))):
        out[name] = max(abs((S(M * (1 + 1e-6)) - S(M * (1 - 1e-6))) / (2e-6 * M) * T(M) - 1) for M in (1.0, 10.0, 100.0))
    return {"max_rel_err_hawking": out["hawking"], "max_rel_err_control": out["control"], "pass": out["hawking"] < 1e-6 and out["control"] > 0.5}


def b5_limit():
    def ratio_err(c):
        b2 = (1.0 / c) ** 2                           # v = 1, m = 1
        ke = math.expm1(-0.5 * math.log1p(-b2)) * c * c
        return ke / 0.5 - 1, b2
    rows = {c: ratio_err(c) for c in (10.0, 100.0, 1000.0)}
    lead = {c: e / (0.75 * b2) for c, (e, b2) in rows.items()}
    wrong = {c: e / (0.5 * b2) for c, (e, b2) in rows.items()}
    ok = all(abs(lead[c] - 1) < 1e-2 for c in (100.0, 1000.0)) and all(abs(wrong[c] - 1) > 0.4 for c in (100.0, 1000.0))
    return {"correction_over_3/4_beta2": {str(int(c)): round(v, 6) for c, v in lead.items()},
            "correction_over_1/2_beta2": {str(int(c)): round(v, 6) for c, v in wrong.items()}, "pass": ok}


def run():
    r = {"B1_noether": b1_noether(), "B2_geodesic": b2_geodesic(), "B3_entropy": b3_entropy(), "B4_black_hole": b4_black_hole(), "B5_limit": b5_limit()}
    r["passed"] = sum(v["pass"] for v in r.values() if isinstance(v, dict)); r["of"] = 5
    return r


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        r = run(); print("PHYSICS BENCH SELFTEST:", "PASS" if r["passed"] == 5 else "FAIL %s" % r); sys.exit(0 if r["passed"] == 5 else 1)
    print(json.dumps(run(), indent=1, default=float))
