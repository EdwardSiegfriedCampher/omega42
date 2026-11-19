#!/usr/bin/env python3
"""spacetime.py -- the Ω42 Spacetime Coordinate Matrix (Core Part 3.80; APE-442, F181).

  M371 Coordinate Allocator   python3 tools/spacetime.py allocate X X0 DELTA K   the address of a coordinate: the absolute
                                                                              cell n = q 3^K + r, and the 3-adic path of r
                                                                              (region -> subregion -> cell), parents by
                                                                              truncation; q is kept, so nothing aliases
  M372 Event Encoder          python3 tools/spacetime.py event CT X Y Z [K]    an event as the Hermitian matrix
                                                                              [[ct+z, x-iy], [x+iy, ct-z]]; its determinant is
                                                                              the interval c^2 t^2 - x^2 - y^2 - z^2, and A acts
                                                                              by X -> A X A^T as a Lorentz map (CERT-0009)
  M373 Registry and Reconciler python3 tools/spacetime.py reconcile            two observations of one object in two frames:
                                                                              agree within their combined uncertainty or are
                                                                              flagged; WGS84 geodetic <-> ECEF calibrated
  python3 tools/spacetime.py --selftest
Standard library only. The allocation and the encoding are MODE A (Core L-559); the physical frame, units, epoch and
metric come from the reference systems (ITRF, ICRS, the time scales), which Ω42 integrates and never replaces.
"""
import math, sys

A = (0, 1, 1, 1)


# ------------------------------------------------------------------ M371
def allocate(x, x0, delta, k):
    n = round((x - x0) / delta); m = 3 ** k
    q, r = divmod(n, m)                                   # Python floor division: r in [0, 3^k)
    digits = []; t = r
    for _ in range(k):
        digits.append(t % 3); t //= 3                     # least significant first: the coarsest cell first
    path = [r % 3 ** j for j in range(1, k + 1)]          # the cell at each level 3^j (the tower S_1 <- S_2 <- ...)
    return dict(n=n, q=q, r=r, digits=digits, path=path)


# ------------------------------------------------------------------ M372
def event_matrix(ct, x, y, z):
    return ((ct + z, complex(x, -y)), (complex(x, y), ct - z))


def det(M):
    return (M[0][0] * M[1][1] - M[0][1] * M[1][0]).real


def act(M):
    """X -> A X A^T with A = [[0,1],[1,1]] real."""
    a = [[0, 1], [1, 1]]
    P = [[sum(a[i][k] * M[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
    return tuple(tuple(sum(P[i][k] * a[j][k] for k in range(2)) for j in range(2)) for i in range(2))


def matrix_event(M):
    ct = (M[0][0] + M[1][1]).real / 2; z = (M[0][0] - M[1][1]).real / 2
    x = M[1][0].real; y = M[1][0].imag
    return (ct, x, y, z)


def interval(e):
    return e[0] ** 2 - e[1] ** 2 - e[2] ** 2 - e[3] ** 2


# ------------------------------------------------------------------ M373
WGS_A = 6378137.0; WGS_F = 1 / 298.257223563; WGS_E2 = WGS_F * (2 - WGS_F)


def geodetic_to_ecef(lat, lon, h):
    la, lo = math.radians(lat), math.radians(lon)
    N = WGS_A / math.sqrt(1 - WGS_E2 * math.sin(la) ** 2)
    return ((N + h) * math.cos(la) * math.cos(lo), (N + h) * math.cos(la) * math.sin(lo), (N * (1 - WGS_E2) + h) * math.sin(la))


def ecef_to_geodetic(x, y, z):
    lon = math.atan2(y, x); p = math.hypot(x, y); lat = math.atan2(z, p * (1 - WGS_E2)); h = 0.0
    for _ in range(10):
        N = WGS_A / math.sqrt(1 - WGS_E2 * math.sin(lat) ** 2)
        h = p / math.cos(lat) - N
        lat = math.atan2(z, p * (1 - WGS_E2 * N / (N + h)))
    return math.degrees(lat), math.degrees(lon), h


def frame(p, yaw_deg, shift):
    """a second frame: rotated about z by yaw and translated (a stand-in for a published frame transformation)."""
    c, s = math.cos(math.radians(yaw_deg)), math.sin(math.radians(yaw_deg))
    return (c * p[0] - s * p[1] + shift[0], s * p[0] + c * p[1] + shift[1], p[2] + shift[2])


def reconcile(obs1, sig1, obs2, sig2, yaw, shift):
    """map obs1 into frame 2 and test the residual against the combined uncertainty (chi-square, 3 dof, 99%: 11.345)."""
    pred = frame(obs1, yaw, shift)
    chi2 = sum((pred[i] - obs2[i]) ** 2 / (sig1 ** 2 + sig2 ** 2) for i in range(3))
    return chi2, chi2 <= 11.345


def selftest():
    a1 = allocate(1000.4, 0.0, 1.0, 3); a2 = allocate(1027.4, 0.0, 1.0, 3)
    e = (5, 3, 0, 4); M = event_matrix(*e); AM = act(M); e2 = matrix_event(AM)
    roundtrip = max(max(abs(a - b) for a, b in zip((lat, lon, h), ecef_to_geodetic(*geodetic_to_ecef(lat, lon, h))))
                    for lat in range(-89, 90, 7) for lon in range(-179, 180, 13) for h in (-400.0, 0.0, 8848.0, 400000.0))
    p = geodetic_to_ecef(-25.7479, 28.2293, 1339.0)      # a sample point on the Earth's surface (illustrative, not a station)
    ok_obs = frame(p, 0.002, (0.5, -0.3, 0.1)); off_obs = (ok_obs[0] + 5, ok_obs[1], ok_obs[2])
    cases = [
        ('M371 n = q 3^k + r: cells 1000 and 1027 share the residue %d mod 27 but keep different q (%d, %d) -- no aliasing' % (a1['r'], a1['q'], a2['q']),
         a1['r'] == a2['r'] and a1['q'] != a2['q']),
        ('M371 the address path refines: the cell at 3^j is the parent of the cell at 3^(j+1)', all(a1['path'][j + 1] % 3 ** (j + 1) == a1['path'][j] for j in range(2))),
        ('M372 det of the event matrix is the interval: (5,3,0,4) has interval 0, a light-like event', det(M) == interval(e) == 0),
        ('M372 A acts as a Lorentz map: the interval of A X A^T equals that of X, for every integer event |.| <= 3',
         all(abs(interval(matrix_event(act(event_matrix(ct, x, y, z)))) - interval((ct, x, y, z))) < 1e-9
             for ct in range(-3, 4) for x in range(-3, 4) for y in range(-3, 4) for z in range(-3, 4))),
        ('M372 the kept lattice is integer Hermitian matrices (ct+z, ct-z, x, y integers), not integer events: (5,3,0,4) goes to %s' % (e2,),
         all(abs(v.real - round(v.real)) < 1e-9 and abs(v.imag - round(v.imag)) < 1e-9 for row in AM for v in map(complex, row))
         and any(abs(c - round(c)) > 0.4 for c in e2)),
        ('M373 WGS84 geodetic -> ECEF -> geodetic round trip within 1e-6 (degrees and metres) over the globe and 400 km', roundtrip < 1e-6),
        ('M373 reconciliation: a consistent observation agrees within 0.5 m per axis; one displaced by 5 m is flagged',
         reconcile(p, 0.5, ok_obs, 0.5, 0.002, (0.5, -0.3, 0.1))[1] and not reconcile(p, 0.5, off_obs, 0.5, 0.002, (0.5, -0.3, 0.1))[1]),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('SPACETIME COORDINATE MATRIX SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['allocate']:
        x, x0, d, k = float(a[1]), float(a[2]), float(a[3]), int(a[4]); r = allocate(x, x0, d, k)
        print('M371 ALLOCATE %g (origin %g, cell %g, level 3^%d): absolute cell n = %d = %d x %d + %d' % (x, x0, d, k, r['n'], r['q'], 3 ** k, r['r']))
        print('  path (cell at 3^1, 3^2, ...): %s ; base-3 digits, coarsest first: %s' % (r['path'], r['digits']))
        return 0
    if a[:1] == ['event']:
        e = tuple(float(v) for v in a[1:5]); M = event_matrix(*e); AM = act(M); e2 = matrix_event(AM)
        print('M372 EVENT (ct, x, y, z) = %s -> Hermitian matrix %s; interval %g' % (e, M, interval(e)))
        print('  A X A^T -> event %s; interval %g (kept: a Lorentz map, CERT-0009) -- MODE A, not a physical motion' % (e2, interval(e2)))
        return 0
    if a[:1] == ['reconcile']:
        p = geodetic_to_ecef(-25.7479, 28.2293, 1339.0)
        for label, obs in (('consistent', frame(p, 0.002, (0.5, -0.3, 0.1))), ('displaced 5 m', tuple(v + d for v, d in zip(frame(p, 0.002, (0.5, -0.3, 0.1)), (5, 0, 0))))):
            chi2, ok = reconcile(p, 0.5, obs, 0.5, 0.002, (0.5, -0.3, 0.1))
            print('M373 RECONCILE %-14s chi-square %.3f (3 dof, 99%% bound 11.345): %s' % (label, chi2, 'AGREES' if ok else 'FLAGGED for investigation'))
        return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
