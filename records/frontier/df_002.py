"""DF-002 (Discovery Bulletin): different laws, identical behavior.

Among the invertible two-term laws x(n+1) = p x(n) + q x(n-1) modulo 9 (q a unit), list the cycle type of each law as a
permutation of the 81 states (a, b), and find the laws whose cycle type equals Fibonacci's. Two linear maps with different
trace p or determinant -q cannot be linearly conjugate; laws with the same cycle type are conjugate as permutations.
Computed while exploring; not a registered STP test.
"""
from collections import Counter
from itertools import product


def cycle_type(p, q, n=9):
    seen, lengths = set(), []
    for s in product(range(n), repeat=2):
        if s in seen: continue
        x, L = s, 0
        while x not in seen:
            seen.add(x); x = (x[1], (p * x[1] + q * x[0]) % n); L += 1
        lengths.append(L)
    return tuple(sorted(Counter(lengths).items()))


if __name__ == '__main__':
    laws = [(p, q) for p in range(9) for q in range(9) if q % 3]
    types = {l: cycle_type(*l) for l in laws}
    fib = types[(1, 1)]
    same = [l for l in laws if types[l] == fib]
    print('laws:', len(laws), '| distinct cycle types:', len(set(types.values())))
    print('Fibonacci (1, 1) cycle type (length, count):', fib)
    print('laws with exactly this cycle type:', len(same), same)
    print('distinct (trace, determinant) pairs among them:', len({(p, (-q) % 9) for p, q in same}))
