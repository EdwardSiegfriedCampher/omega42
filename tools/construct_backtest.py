#!/usr/bin/env python3
"""Construct template backtest with a chance-level control (Appendix S, CA-04).

The Construct's prediction mechanism, as the Originator describes it:
  * a "distance" template is learned between a past draw and a later draw,
    one template per lag d = 1..23 (the 24-orbit split into 23 gaps);
  * to predict, the past draw at lag d is fed into Field Y, and the
    template's copy-linked Field X is read as the next draw.

This harness reproduces that loop in the abstract form below and scores it
against the exact chance baseline. For a k-of-N draw with uniform,
independent draws, ANY prediction rule built from past draws matches the
next draw in k*k/N numbers on average (hypergeometric mean).

Usage:
  python3 construct_backtest.py                 # simulated 6-of-49 draws
  python3 construct_backtest.py draws.csv N     # real history, one draw per row
"""
import csv, math, random, sys

LAGS = range(1, 24)  # 23 templates


def wrap(v, n):
    return (v - 1) % n + 1


def learn(draws, t, d):
    """Template for lag d: per-position offsets from draw t-d to draw t."""
    a, b = sorted(draws[t - d]), sorted(draws[t])
    return [y - x for x, y in zip(a, b)]


def predict(draws, t, d, n):
    """Apply the lag-d template to the draw that sits d-1 steps back of t."""
    delta = learn(draws, t, d)
    src = sorted(draws[t + 1 - d])
    out, seen = [], set()
    for x, dx in zip(src, delta):
        v = wrap(x + dx, n)
        while v in seen:          # keep k distinct numbers
            v = wrap(v + 1, n)
        seen.add(v)
        out.append(v)
    return out


def run(draws, n):
    k = len(draws[0])
    base = k * k / n
    print(f"draws={len(draws)}  k={k}  N={n}  chance mean matches={base:.4f}")
    best = None
    for d in LAGS:
        hits = []
        for t in range(d, len(draws) - 1):
            p = set(predict(draws, t, d, n))
            hits.append(len(p & set(draws[t + 1])))
        m = sum(hits) / len(hits)
        var = k * (k / n) * ((n - k) / n) * ((n - k) / (n - 1))
        z = (m - base) / math.sqrt(var / len(hits))
        print(f"  template lag {d:2d}: mean={m:.4f}  z={z:+.2f}")
        if best is None or m > best[1]:
            best = (d, m, z)
    d, m, z = best
    # 23 templates tested: a Bonferroni-corrected two-sided 5% bar is |z| > 3.06
    print(f"best template: lag {d}  mean={m:.4f}  z={z:+.2f}  "
          f"(needs z > 3.06 after correcting for 23 templates)")


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        with open(sys.argv[1]) as f:
            draws = [[int(x) for x in row if x.strip()] for row in csv.reader(f) if row]
        run(draws, int(sys.argv[2]))
    else:
        rng = random.Random(42)
        run([rng.sample(range(1, 50), 6) for _ in range(3000)], 49)
