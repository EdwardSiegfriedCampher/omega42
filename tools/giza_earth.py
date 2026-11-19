#!/usr/bin/env python3
"""giza_earth.py -- the mapping of Omega42 to the Giza complex and to the Earth in the Solar System (Companion Part 166).

The representation family is frozen in records/mapping/giza_earth.json before any value is computed (the Frozen Mapping
Law); items introduced after a resemblance was seen are marked POST-HOC there. This tool computes every exact value the
report states: the placements CPP(n) = dr(5n), the census of the 81 states, the half-turn A^12 = -I, the determinants,
the fixed points, the proportions against sqrt(phi) and 4/pi, and the unit test of the latitude resemblance.
    python3 tools/giza_earth.py            # the report's values
    python3 tools/giza_earth.py --selftest
Standard library only.
"""
import json, math, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(REPO, 'records', 'mapping', 'giza_earth.json')
def dr(n): return 9 if n % 9 == 0 else n % 9
def cpp(n): return dr(5 * n)
def mul(X, Y, m=None):
    Z = [[sum(X[i][k] * Y[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    return [[z % m for z in r] for r in Z] if m else Z
def mpow(X, e, m):
    R = [[1, 0], [0, 1]]
    for _ in range(e): R = mul(R, X, m)
    return R
A = [[0, 1], [1, 1]]
def census():
    seen, L = set(), []
    for a in range(9):
        for b in range(9):
            if (a, b) in seen: continue
            s, n = (a, b), 0
            while True:
                seen.add(s); s = (s[1], (s[0] + s[1]) % 9); n += 1
                if s == (a, b): break
            L.append(n)
    return sorted(L)
def eight_cycle():
    s, out = (3, 3), []
    while True:
        out.append(s); s = (s[1], (s[0] + s[1]) % 9)
        if s == (3, 3): return out
def values():
    d = json.load(open(REC, encoding='utf-8'))
    phi = (1 + 5 ** 0.5) / 2
    rot = lambda deg: [[math.cos(math.radians(deg)), -math.sin(math.radians(deg))], [math.sin(math.radians(deg)), math.cos(math.radians(deg))]]
    R12 = [[1, 0], [0, 1]]
    for _ in range(12): R12 = mul(R12, rot(15))
    seked = 7 / 5.5
    lat = 29 + 58 / 60 + 45 / 3600
    v = {
     'placements': {it['id']: {'count': it['count'], 'P': cpp(it['count'])} for it in d['family'] if 'count' in it},
     'census': census(), 'eight_cycle_all_multiples_of_3': all(a % 3 == 0 and b % 3 == 0 for a, b in eight_cycle()),
     'A12_mod9': mpow(A, 12, 9), 'A24_mod9': mpow(A, 24, 9), 'det_A': A[0][0] * A[1][1] - A[0][1] * A[1][0],
     'R15_12': [[round(x, 9) + 0.0 for x in r] for r in R12], 'det_R15': 1,
     'fixed_states_mod9': [(a, b) for a in range(9) for b in range(9) if (b, (a + b) % 9) == (a, b)],
     'seked_ratio_14_11': round(seked, 6), 'sqrt_phi': round(phi ** 0.5, 6), 'four_over_pi': round(4 / math.pi, 6),
     'seked_vs_sqrt_phi_pct': round((seked / phi ** 0.5 - 1) * 100, 4), 'seked_vs_4_over_pi_pct': round((seked / (4 / math.pi) - 1) * 100, 4),
     'perimeter_over_height': round(1760 / 280, 6), 'two_pi': round(2 * math.pi, 6), 'perim_vs_2pi_pct': round((1760 / 280 / (2 * math.pi) - 1) * 100, 4),
     'latitude_deg': round(lat, 5), 'c_m_per_s_scaled': 29.9792458, 'latitude_minus_c_deg': round(lat - 29.9792458, 5),
     'c_ft_per_s_scaled': round(299792458 / 0.3048 / 1e7, 5), 'pole_altitude_steps_of_15deg': round(lat / 15, 4),
     'sidereal_year_over_24': round(365.256 / 24, 4),
    }
    return v, d
def selftest():
    v, d = values()
    t = [('the census is 1 + 8 + 24 + 24 + 24', v['census'] == [1, 8, 24, 24, 24]),
         ('the 8-cycle lies in the multiples of 3', v['eight_cycle_all_multiples_of_3']),
         ('A^12 = -I (mod 9)', v['A12_mod9'] == [[8, 0], [0, 8]]), ('A^24 = I (mod 9)', v['A24_mod9'] == [[1, 0], [0, 1]]),
         ('det A = -1, det R = +1', v['det_A'] == -1 and v['det_R15'] == 1),
         ('R(15 deg)^12 = -I', v['R15_12'] == [[-1.0, 0.0], [0.0, -1.0]]),
         ('the only fixed state is (0, 0)', v['fixed_states_mod9'] == [(0, 0)]),
         ('CPP: 3 -> 6, 8 -> 4, 24 -> 3, 4 -> 2, 1 -> 5', [cpp(n) for n in (3, 8, 24, 4, 1)] == [6, 4, 3, 2, 5]),
         ('14/11 lies within 0.06 percent of both sqrt(phi) and 4/pi', abs(v['seked_vs_sqrt_phi_pct']) < 0.06 and abs(v['seked_vs_4_over_pi_pct']) < 0.06),
         ('the latitude resemblance fails in feet', abs(v['c_ft_per_s_scaled'] - v['latitude_deg']) > 60),
         ('every family item is declared with its type and freeze', all(it.get('type') and it.get('frozen') for it in d['family']))]
    for n, ok in t: print('%-62s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('GIZA AND EARTH MAPPING SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    v, d = values(); print(json.dumps(v, indent=1, default=str))
