"""Recomputation of arithmetic stated in archive documents (docs/ONEDRIVE_REVIEW.md, docs/PUBLIC_REPO_REVIEW.md).
Run 19 November 2026 after reading the documents, so it is a recomputation, not a registered STP test."""
import math
from collections import Counter

def dr(n):
    return 9 if n % 9 == 0 else n % 9

def orbit(a, b, n=26):
    s = [a, b]
    while len(s) < n:
        s.append(dr(s[-1] + s[-2]))
    return s

def period(a, b):
    s = orbit(a, b, 60)
    return next(t for t in range(1, 50) if s[t] == a and s[t + 1] == b)

def cycle_test():
    P = orbit(2, 5)
    crown = [P[i] for i in (3, 7, 11, 15, 19, 23)]
    same = [(a, b) for a in range(1, 10) for b in range(1, 10)
            if period(a, b) == 24 and [orbit(a, b)[i] for i in (3, 7, 11, 15, 19, 23)] == crown]
    return {"period_24": P[24:26] == [2, 5], "sum": sum(P[:24]),
            "antipodal_plain_sum_9": all(P[n] + P[n + 12] == 9 for n in range(12)),
            "antipodal_digital_root_9": all(dr(P[n] + P[n + 12]) == 9 for n in range(12)),
            "crown": crown, "encoding_values": sorted({dr(42 * n) for n in range(1, 1000)}),
            "pairs_with_same_period_and_crown": same,
            "period_counts": dict(Counter(period(a, b) for a in range(1, 10) for b in range(1, 10)))}

def circulant_702():
    N, D = 702, (81, 162, 243)
    lam = [round(sum(2 * math.cos(2 * math.pi * k * d / N) for d in D), 6) for k in range(N)]
    phi2 = (3 + 5 ** 0.5) / 2
    return {"multiplicity_of_6": lam.count(6.0), "phi_squared_is_eigenvalue": any(abs(l - phi2) < 1e-6 for l in lam),
            "components": math.gcd(math.gcd(*D), N), "fixed_points_of_351_minus_n": [n for n in range(N) if (351 - n) % N == n],
            "order_of_117": N // math.gcd(117, N), "offsets_mod_9": [d % 9 for d in D]}

def public_validator():
    phi = (1 + 5 ** 0.5) / 2
    dr12 = lambda n: [0, 1, 2, 3, 4, 5, -6, -5, -4, -3, -2, -1][n % 12]
    p = lambda n: 1 - math.exp(-(phi ** abs(dr12(n)) * math.cos(math.pi * n / 12)))
    return {"P(12)": round(p(12), 3), "example_passes_collapse_filter": p(12) > 0.42}

def cassini_is_norm():
    F = [0, 1]
    for _ in range(30):
        F.append(F[-1] + F[-2])
    return all(F[n] ** 2 + F[n] * F[n + 1] - F[n + 1] ** 2 == (-1) ** (n + 1) for n in range(30))

if __name__ == "__main__":
    for f in (cycle_test, circulant_702, public_validator, cassini_is_norm):
        print(f.__name__, f())
