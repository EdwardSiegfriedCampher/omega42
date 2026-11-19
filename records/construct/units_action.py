#!/usr/bin/env python3
"""units_action.py -- how the Square Reading's multiplications act on the 81 states of the law (Companion Part 129; M328, Core Part 3.54).

M328 reads one value by multiplication: FORWARD x2, RETURN x5, STILLNESS x1, TURN x4. The law T(a, b) = (b, a + b) acts on
states. Multiplication by a unit u of Z/9 acts on states too, (a, b) -> (ua, ub), and commutes with T, since T is linear. This
script computes, for each unit, what it does to the orbits of T at depths 1 and 2, and whether it is a power of T. Exact.
"""
def orbits(m):
    seen, out = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            o, s = [], (a, b)
            while s not in seen:
                seen.add(s); o.append(s); s = (s[1], (s[0] + s[1]) % m)
            out.append(o)
    return out
def power_of_T(u, m):
    """k with T^k = u I mod m, or None"""
    s, k = (1, 0, 0, 1), 0           # A^k as (p, q, r, t)
    for k in range(1, 4 * m * m):
        p, q, r, t = s; s = (q, (p + q) % m, t, (r + t) % m)      # A^k = A^(k-1) A
        if s == (u % m, 0, 0, u % m): return k
        if s == (1, 0, 0, 1): return None
    return None
for m in (9, 81):
    O = orbits(m); idx = {s: i for i, o in enumerate(O) for s in o}
    big = [i for i, o in enumerate(O) if len(o) == max(len(x) for x in O)]
    print('MODULUS %d: %d orbits, lengths %s' % (m, len(O), sorted({len(o) for o in O})))
    canon = idx[(2, 5)]
    if m == 9: print('  the three 24-cycles (the voices): %s; the canonical voice, from (2, 5): %d' % (big, canon))
    for u in ([x for x in range(1, 9) if x % 3] + ([m - 1] if m > 9 else [])):
        img = idx[((2 * u) % m, (5 * u) % m)]
        perm = {}
        for i in big[:3] if m == 9 else []: perm[i] = idx[tuple((u * c) % m for c in O[i][0])]
        k = power_of_T(u, m)
        fixed_zero = all(idx[((u * a) % m, (u * b) % m)] == idx[(a, b)] for o in O if len(o) < 24 for (a, b) in o) if m == 9 else None
        print('  x%d: canonical orbit -> orbit %s%s | a power of T: %s%s' % (u, 'itself' if img == canon else img,
              (' | the three 24-cycles %s' % perm) if perm else '', ('T^%d' % k) if k else 'no', (' | fixes every orbit of the zero layer: %s' % fixed_zero) if fixed_zero is not None else ''))
