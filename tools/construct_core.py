#!/usr/bin/env python3
"""Reference implementation of the Construct mechanism (precursor of Omega42).

Layers
  1. Substrate   : Z/9 split into units U = {1,2,4,5,7,8} (Lower World) and
                   the ideal I = {0,3,6} (Higher World).
  2. Squares     : Lower World square = multiplication table of U (a 6x6 Latin square).
  3. Candidate   : block(Y) = { y - s : y in Y, s in U }  (Field Y shifted by the Torsion offsets)
  4. Coverage    : flag when at least 4 of the 6 Field X values fall in block(Y).
  5. Templates   : lag-d template learned from (t-d -> t), applied to t+1-d, for d = 1..23.

Run this file to reproduce every worked example in the formal description.
"""
import random, statistics as st

U = (1, 2, 4, 5, 7, 8)          # Torsion Loop offsets = units of Z/9
CIRCUIT = (1, 2, 4, 8, 7, 5)    # doubling circuit, powers of 2 mod 9


def lower_world_square():
    starts = (1, 5, 7, 8, 4, 2)  # row k starts at 2^(-k) mod 9
    return [[(s * c) % 9 for c in CIRCUIT] for s in starts]


def is_latin(sq):
    n = len(sq)
    return all(len(set(r)) == n for r in sq) and all(len({sq[i][j] for i in range(n)}) == n for j in range(n))


def block(Y, offsets=U):
    return {y - s for y in Y for s in offsets}


def coverage(X, Y, offsets=U):
    b = block(Y, offsets)
    return sum(x in b for x in X)


def positional_coverage(X, Y, offsets=U):
    """Adopted upgrade: x_i is tested only against y_i - offsets (catches drift)."""
    return sum((y - x) in offsets for x, y in zip(X, Y))


def flag_rate(lo, hi, trials=20000, seed=1):
    """Chance that random X (6 values in [lo,hi]) clears 4-of-6 against random Y."""
    r = random.Random(seed)
    hit = 0
    for _ in range(trials):
        Y = [r.randint(lo, hi) for _ in range(6)]
        X = [r.randint(lo, hi) for _ in range(6)]
        hit += coverage(X, Y) >= 4
    return hit / trials


def template_predict(x, t, d):
    """Lag-d template: offset learned from x[t-d] -> x[t], applied to x[t+1-d]."""
    return x[t + 1 - d] + (x[t] - x[t - d])


def lag_scan(x, lags=range(1, 24), shuffles=200, seed=7):
    """Mean absolute error of each lag template, with a shuffled-series control."""
    def mae(series, d):
        return st.mean(abs(template_predict(series, t, d) - series[t + 1])
                       for t in range(max(lags), len(series) - 1))
    real = {d: mae(x, d) for d in lags}
    r = random.Random(seed)
    best_ctrl = []
    for _ in range(shuffles):
        s = x[:]
        r.shuffle(s)
        best_ctrl.append(min(mae(s, d) for d in lags))
    d_best = min(real, key=real.get)
    p = sum(c <= real[d_best] for c in best_ctrl) / shuffles
    return d_best, real, st.mean(best_ctrl), p


if __name__ == "__main__":
    sq = lower_world_square()
    print("Lower World square:", sq, "Latin:", is_latin(sq))

    Y, X = [6, 2, 16, 5, -4, 8], [15, 14, 27, 5, 13, 22]
    b = block(Y)
    print(f"block size={len(b)} range=({min(b)},{max(b)}) coverage={coverage(X, Y)} "
          f"hits={sorted(x for x in X if x in b)}")
    for lo, hi in [(-12, 27), (1, 49), (0, 100)]:
        print(f"chance 4-of-6 flag rate, values in [{lo},{hi}]: {flag_rate(lo, hi):.4f}")

    # Example A: 26 weeks of daily sales with a weekly cycle and slow growth (synthetic)
    r = random.Random(3)
    week = [120, 95, 90, 100, 130, 180, 210]
    sales = [week[t % 7] * (1 + 0.002 * t) + r.gauss(0, 8) for t in range(182)]
    d, real, ctrl, p = lag_scan(sales)
    print(f"sales: best lag={d} MAE={real[d]:.1f} (lag 1 MAE={real[1]:.1f}) "
          f"shuffled best MAE={ctrl:.1f} p={p:.3f}  lag14={real[14]:.1f} lag21={real[21]:.1f}")

    # Example B: pure noise -> no lag should beat the shuffled control
    noise = [r.gauss(100, 10) for _ in range(182)]
    d, real, ctrl, p = lag_scan(noise)
    print(f"noise: best lag={d} MAE={real[d]:.1f} shuffled best MAE={ctrl:.1f} p={p:.3f}")
