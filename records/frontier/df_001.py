"""DF-001 (Daily Frontier): does a system's history change the shape of its reachable futures?

Model: the Omega42 law with a learned move, v(t+1) = T v(t) + c(t) on (Z/9)^2, T(a, b) = (b, a + b), where each step
either adds nothing or adds the one move the system has learned (its history). Same present state, different histories.
Prints the number of states reachable after n steps. Computed while exploring; not a registered STP test.
"""
T = lambda v: (v[1] % 9, (v[0] + v[1]) % 9)


def reach(x, moves, n):
    S = {x}
    for _ in range(n):
        S = {((T(v)[0] + c[0]) % 9, (T(v)[1] + c[1]) % 9) for v in S for c in moves}
    return S


if __name__ == '__main__':
    x = (2, 5)
    fib = [0, 1]
    while len(fib) < 20: fib.append(fib[-1] + fib[-2])
    for label, m in (('no learned move', ((0, 0),)), ('learned move (0, 1), a unit', ((0, 0), (0, 1))),
                     ('learned move (1, 0), a unit', ((0, 0), (1, 0))), ('learned move (0, 3), in the 3-layer', ((0, 0), (0, 3)))):
        print('%-38s' % label, [len(reach(x, m, n)) for n in range(1, 13)])
    print('%-38s' % 'F(n+3) - 1, for comparison', [fib[n + 3] - 1 for n in range(1, 13)])
