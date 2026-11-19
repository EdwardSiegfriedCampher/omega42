#!/usr/bin/env python3
"""wave_atlas.py -- the Wave Engine resolved: the Chern number on the (k, phason) torus against the full gap label (p, q), the
golden contrast, the six-cycle record with its seeds, bands as rotations and gaps as boosts, the matrix group of each wave model,
and the free-group automorphism with its inverse (Companion Part 228; F221; APE-483).

  A1 chern-torus        the Fukui-Hatsugai-Suzuki Chern number of the filled bands on the torus of the Bloch phase k and the phason,
                        for the six widest gaps of the 89-site approximant (V = 1.5, beta = 2): C = -q exactly, where the integrated
                        density of states is p + q (55/89); p takes the values 1, 0, -1, -2, -1, 2 and carries no topology (numerical)
  A2 golden-contrast    a hopping ratio t_a/t_b = phi puts the off-diagonal chain on the surface I = 1/4 at every energy, and a
                        quarter-wave index or impedance ratio phi puts light and sound on the same surface: phi - 1/phi = 1 (exact in Q(phi))
  A3 six-cycle-record   the seeds, the six states, the return error and the invariant of the six-cycle of light, sound and the
                        off-diagonal chain; the on-site chain at E = 0 and the off-diagonal chain at E = 1 under the same procedure,
                        neither periodic; written to records/waves/six_cycle.json by --write (exact)
  A4 bands-rotations    the transfer matrix of one period of the 89-site approximant is elliptic in the bands and hyperbolic in the
                        gaps, and its Lorentz image is a rotation in the bands and a boost in the gaps: |tr| < 2 against |tr| > 2 (numerical)
  A5 matrix-groups      the electron's letter matrices lie in SL2(R); the optical and acoustic layer matrices lie in SL2(C) and are
                        carried into SL2(R) by D = diag(1, i), D^-1 M D = [[cos, -sin/n], [n sin, cos]] (exact)
  A6 free-group-inverse sigma(a) = ab, sigma(b) = a has the inverse sigma^-1(a) = b, sigma^-1(b) = b^-1 a: both compositions are the
                        identity on reduced words, and the same holds for the letter matrices (exact)

    python3 tools/wave_atlas.py --selftest
    python3 tools/wave_atlas.py --write      writes records/waves/six_cycle.json and records/waves/models.json
Standard library and numpy (A1, A4); exact arithmetic elsewhere.
"""
import sys, os, json, math, random
from fractions import Fraction as F
OUT = []
def P(name, ok, *a): OUT.append((name, ok, ' '.join(str(x) for x in a)))
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def mm(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
# A1
def chern_torus(L=89, p=55, V=1.5, beta=2.0, Nk=24, Nt=60, top=6):
    import numpy as np
    def H(k, th):
        j = np.arange(L); b = p / L
        v = V * np.tanh(beta * (np.cos(2 * np.pi * b * j + 2 * np.pi * th) - np.cos(np.pi * b))) / np.tanh(beta)
        M = np.diag(v).astype(complex) - np.eye(L, k=1) - np.eye(L, k=-1)
        M[0, L - 1] = -np.exp(-1j * k); M[L - 1, 0] = -np.exp(1j * k)
        return M
    w, _ = np.linalg.eigh(H(0.0, 0.0))
    gaps = sorted([(w[i + 1] - w[i], i + 1) for i in range(L - 1)], reverse=True)[:top]
    vecs = [[np.linalg.eigh(H(2 * np.pi * a / Nk, c / Nt))[1] for c in range(Nt)] for a in range(Nk)]
    out = []
    for g, nf in gaps:
        tot = 0.0
        for a in range(Nk):
            for c in range(Nt):
                A_ = vecs[a][c][:, :nf]; B_ = vecs[(a + 1) % Nk][c][:, :nf]; C_ = vecs[(a + 1) % Nk][(c + 1) % Nt][:, :nf]; D_ = vecs[a][(c + 1) % Nt][:, :nf]
                lnk = np.linalg.det(A_.conj().T @ B_) * np.linalg.det(B_.conj().T @ C_) * np.linalg.det(C_.conj().T @ D_) * np.linalg.det(D_.conj().T @ A_)
                tot += np.angle(lnk)
        ids = nf / L; q = min(range(-20, 21), key=lambda n: abs(((n * p / L - ids + 0.5) % 1) - 0.5)); pp = round(ids - q * p / L)
        out.append((pp, q, round(float(tot / (2 * np.pi)), 6)))
    return out
if '--selftest' in sys.argv or '--full' in sys.argv:
    ct = chern_torus()
    P('chern-torus', all(abs(c + q) < 1e-6 for _, q, c in ct) and len({p for p, _, _ in ct}) > 2,
      'the Chern number of the filled bands on the torus of the Bloch phase and the phason, by the method of Fukui, Hatsugai and Suzuki (24 x 60 plaquettes), for the six widest gaps; (p, q, C) with IDS = p + q (55/89):', ct,
      '| C = -q in every gap, while p runs over 1, 0, -1, -2, 2 with no bearing on C: the topological integer of a gap label is its coefficient q, and it agrees with the Resta winding of MF-154')
# A2: Q(phi)
class Q5:
    __slots__ = ('a', 'b')
    def __init__(s, a=0, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a + o.a, s.b + o.b)
    __radd__ = __add__
    def __neg__(s): return Q5(-s.a, -s.b)
    def __sub__(s, o): return s + (-(o if isinstance(o, Q5) else Q5(o)))
    def __mul__(s, o): o = o if isinstance(o, Q5) else Q5(o); return Q5(s.a * o.a + s.b * o.b, s.a * o.b + s.b * o.a + s.b * o.b)
    __rmul__ = __mul__
    def inv(s): c = Q5(s.a + s.b, -s.b); n = (s * c).a; return Q5(c.a / n, c.b / n)
    def __truediv__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s * o.inv()
    def __eq__(s, o): o = o if isinstance(o, Q5) else Q5(o); return s.a == o.a and s.b == o.b
PHI_ = Q5(0, 1)
def half_tr(M): return (M[0][0] + M[1][1]) * Q5(F(1, 2))
def fv(x, y, z): return x * x + y * y + z * z - Q5(2) * x * y * z - Q5(1)
ok2 = PHI_ - PHI_.inv() == Q5(1)
for E in (Q5(F(1, 3)), Q5(F(-7, 5)), Q5(0, F(1, 2)), Q5(2, -1)):
    ta, tb = PHI_, Q5(1)
    Ma = [[E / ta, -(Q5(1) / ta)], [ta, Q5(0)]]; Mb = [[E / tb, -(Q5(1) / tb)], [tb, Q5(0)]]
    S = [Mb, Ma]
    for _ in range(8): S.append(mm(S[-1], S[-2]))
    x = [half_tr(m) for m in S]
    ok2 = ok2 and all(fv(x[k + 1], x[k], x[k - 1]) == Q5(F(1, 4)) for k in range(1, 9))
# light at the quarter wave with index ratio phi: layer [[0, i/n], [i n, 0]]; half-traces of products are real, computed through the real form
def ql(n): return [[Q5(0), -(Q5(1) / n)], [n, Q5(0)]]            # D^-1 M D at the quarter wave, the real form of the layer
S = [ql(Q5(1)), ql(PHI_)]
for _ in range(8): S.append(mm(S[-1], S[-2]))
x = [half_tr(m) for m in S]
ok2 = ok2 and all(fv(x[k + 1], x[k], x[k - 1]) == Q5(F(1, 4)) for k in range(1, 9))
P('golden-contrast', ok2, 'phi - 1/phi = 1, so a hopping ratio t_a/t_b = phi puts the off-diagonal chain on the Fricke-Vogt surface I = 1/4 at four energies, two of them in Q(phi), and a quarter-wave index or impedance ratio phi puts light and sound on the same surface I = 1/4, exact in Q(phi) for eight generations:',
  'the golden contrast gives electrons, light and sound one invariant surface')
# A3
def orbit6(x0):
    f = lambda t: (2 * t[0] * t[1] - t[2], t[0], t[1])
    o = [x0]
    for _ in range(6): o.append(f(o[-1]))
    I0 = x0[0] ** 2 + x0[1] ** 2 + x0[2] ** 2 - 2 * x0[0] * x0[1] * x0[2] - 1
    I6 = o[6][0] ** 2 + o[6][1] ** 2 + o[6][2] ** 2 - 2 * o[6][0] * o[6][1] * o[6][2] - 1
    return o, I0, I6
def seed(Ma, Mb):
    """(x_(k+1), x_k, x_(k-1)) at k = 1 for the words S_0 = b, S_1 = a, S_2 = ab"""
    tr = lambda M: (M[0][0] + M[1][1]) / 2
    return (tr(mm(Ma, Mb)), tr(Ma), tr(Mb))
models = {
 'light, quarter wave, indices 2 and 3/2': ([[F(0), F(-1, 2)], [F(2), F(0)]], [[F(0), F(-2, 3)], [F(3, 2), F(0)]]),
 'sound, quarter wave, impedances 4.6 and 3.2': ([[F(0), -F(10, 46)], [F(46, 10), F(0)]], [[F(0), -F(10, 32)], [F(32, 10), F(0)]]),
 'electrons, hoppings 1 and 3, E = 0': ([[F(0), F(-1)], [F(1), F(0)]], [[F(0), F(-1, 3)], [F(3), F(0)]]),
 'electrons on-site, V = 1, E = 0': ([[F(-1), F(-1)], [F(1), F(0)]], [[F(0), F(-1)], [F(1), F(0)]]),
 'electrons, hoppings 1 and 3, E = 1': ([[F(1), F(-1)], [F(1), F(0)]], [[F(1, 3), F(-1, 3)], [F(3), F(0)]])}
rec = {}; ok3 = True
for name, (Ma, Mb) in models.items():
    o, I0, I6 = orbit6(seed(Ma, Mb))
    err = max(abs(a - b) for a, b in zip(o[6], o[0]))
    rec[name] = {'letter_matrices': [[str(v) for v in r] for r in Ma] + [[str(v) for v in r] for r in Mb], 'seed': [str(v) for v in o[0]],
                 'states': [[str(v) for v in t] for t in o[1:]], 'return_error': str(err), 'invariant_before': str(I0), 'invariant_after': str(I6), 'six_periodic': err == 0}
    want = not ('on-site' in name or 'E = 1' in name)
    ok3 = ok3 and (err == 0) == want and I0 == I6
P('six-cycle-record', ok3, 'the six-cycle with its seeds, by one procedure for five wave models: (model, seed, six-periodic, invariant)',
  [(k, v['seed'], v['six_periodic'], v['invariant_before']) for k, v in rec.items()],
  '| light and sound at the quarter wave and the off-diagonal chain at E = 0 return exactly after six steps; the on-site chain at E = 0 and the off-diagonal chain at E = 1 do not; the invariant is kept in all five')
# A4
def bands_rotations():
    import numpy as np
    L = 89
    w = 'a'
    while len(w) < L: w = ''.join('ab' if c == 'a' else 'a' for c in w)
    pot = [1.0 if c == 'a' else 0.0 for c in w]
    def T(E):
        R = np.eye(2)
        for v in pot: R = np.array([[E - v, -1.0], [1.0, 0.0]]) @ R
        return R
    def lorentz_trace(G):   # trace of the 3 x 3 image under X -> G X G^T, Sym^2: (tr G)^2 - 1 for det 1
        return np.trace(G) ** 2 - 1
    evs = []
    for sg in (1.0, -1.0):
        H = np.diag(pot) - np.eye(L, k=1) - np.eye(L, k=-1); H[0, L - 1] = H[L - 1, 0] = -sg
        evs.append(np.sort(np.linalg.eigvalsh(H)))
    ev = evs[0]
    mids = (evs[0] + evs[1]) / 2                       # the middle of each band, between its periodic and antiperiodic edges
    gaps = sorted([(ev[i + 1] - ev[i], (ev[i] + ev[i + 1]) / 2) for i in range(L - 1)], reverse=True)[:5]
    ok = True; rows = []
    for E in mids[::4]:
        t = np.trace(T(E)); ok = ok and abs(t) < 2 and -1 <= lorentz_trace(T(E)) < 3
    for g, E in gaps:
        t = np.trace(T(E)); ok = ok and abs(t) > 2 and lorentz_trace(T(E)) > 3; rows.append((round(float(E), 4), '%.3g' % abs(t)))
    return ok, rows
if '--selftest' in sys.argv or '--full' in sys.argv:
    ok4, rows4 = bands_rotations()
    P('bands-rotations', ok4, 'one period of the 89-site approximant at V = 1: at the middles of 23 of its bands, between the periodic and antiperiodic edges, the transfer matrix has |tr| < 2, elliptic, and its Lorentz image is a rotation of SO(2,1) with 3 x 3 trace in [-1, 3); at the centers of the five widest gaps (energy, |tr|)', rows4,
      ', |tr| > 2, a boost: bands are rotations and gaps are boosts, the trace classes of Part 223.6 read in the spectrum')
# A5
class G:
    __slots__ = ('a', 'b')
    def __init__(s, a, b=0): s.a = F(a); s.b = F(b)
    def __add__(s, o): return G(s.a + o.a, s.b + o.b)
    def __mul__(s, o): return G(s.a * o.a - s.b * o.b, s.a * o.b + s.b * o.a)
    def __eq__(s, o): return s.a == o.a and s.b == o.b
def gmm(X, Y): return [[X[i][0] * Y[0][j] + X[i][1] * Y[1][j] for j in range(2)] for i in range(2)]
ok5 = True
D = [[G(1), G(0)], [G(0), G(0, 1)]]; Di = [[G(1), G(0)], [G(0), G(0, -1)]]
for n, c, s in ((F(2), F(3, 5), F(4, 5)), (F(5, 4), F(5, 13), F(12, 13)), (F(3), F(0), F(1))):
    M = [[G(c), G(0, s / n)], [G(0, n * s), G(c)]]
    R = gmm(gmm(Di, M), D)
    ok5 = ok5 and R == [[G(c), G(-s / n)], [G(n * s), G(c)]] and all(v.b == 0 for r in R for v in r) and (R[0][0] * R[1][1] + G(-1) * R[0][1] * R[1][0]) == G(1)
P('matrix-groups', ok5, 'the matrix group of each wave model: electrons, SL2(R); light and sound, SL2(C) layer matrices [[cos, i sin/n], [i n sin, cos]] carried into SL2(R) by D = diag(1, i), D^-1 M D = [[cos, -sin/n], [n sin, cos]], exact at three phases and indices:',
  'one real form, SL2(R), for every model of the engine; lossy or multichannel media leave it, for SL2(C) or Sp(4, R)')
# A6
def red(w):
    out = []
    for x in w:
        if out and out[-1] == -x: out.pop()
        else: out.append(x)
    return out
A_, B_ = 1, 2
sig = {A_: [A_, B_], B_: [A_], -A_: [-B_, -A_], -B_: [-A_]}
sinv = {A_: [B_], B_: [-B_, A_], -A_: [-B_], -B_: [-A_, B_]}
app = lambda m, w: red([y for x in w for y in m[x]])
rng = random.Random(3); ok6 = True
for _ in range(200):
    w = red([rng.choice([1, 2, -1, -2]) for _ in range(rng.randint(1, 12))])
    ok6 = ok6 and app(sig, app(sinv, w)) == w and app(sinv, app(sig, w)) == w
Ma = [[F(2), F(1)], [F(1), F(1)]]; Mb = [[F(1), F(3)], [F(0), F(1)]]
inv = lambda M: [[M[1][1], -M[0][1]], [-M[1][0], M[0][0]]]
# convention: a word w = x1 x2 ... xn acts by M(w) = M_x1 M_x2 ... M_xn, so sigma(a) = ab gives M_a M_b
Ms = (mm(Ma, Mb), Ma); Msi = (Mb, mm(inv(Mb), Ma))
ok6 = ok6 and (mm(Msi[0], Msi[1]), Msi[0]) == (Ma, Mb) and (Ms[1], mm(inv(Ms[1]), Ms[0])) == (Ma, Mb)
P('free-group-inverse', ok6, 'sigma(a) = ab, sigma(b) = a is invertible in F2 with sigma^-1(a) = b, sigma^-1(b) = b^-1 a: both compositions return 200 random reduced words, and the letter matrices, under the convention M(x1 x2 ... xn) = M_x1 M_x2 ... M_xn, return (M_a, M_b):',
  'the substitution is an automorphism, so the law, the transfer products and the trace map are its images, and none of them loses information that the others hold')
def write():
    os.makedirs(os.path.join(REPO, 'records', 'waves'), exist_ok=True)
    json.dump({'_about': 'The six-cycle of the trace map in five wave models, each with its letter matrices (real form, M_a then M_b), the seed (x_2, x_1, x_0), the six states, the return error and the Fricke-Vogt invariant before and after (Companion Part 228; F221). Written by python3 tools/wave_atlas.py --write.', 'models': rec},
              open(os.path.join(REPO, 'records', 'waves', 'six_cycle.json'), 'w'), indent=1)
    mods = [
     {'model': 'electrons, on-site Fibonacci potential', 'S': 'the Fibonacci word, a -> ab, b -> a', 'H': '(H psi)_n = -psi_(n+1) - psi_(n-1) + v_n psi_n', 'T': '[[E - v, -1], [1, 0]]', 'group': 'SL2(R)', 'I': 'V^2/4 (MF-129)', 'P': 'spectrum, gap labels, scaling (MF-131, MF-132, MF-158)', 'E': 'tools/fibonacci_hamiltonian.py; tools/spectra.py; RET-001, RET-002'},
     {'model': 'electrons, off-diagonal Fibonacci hopping', 'S': 'the Fibonacci word on the bonds', 'H': 't_n psi_(n+1) + t_(n-1) psi_(n-1) = E psi_n', 'T': '[[E/t, -1/t], [t, 0]]', 'group': 'SL2(R)', 'I': '(1/4)(t_a/t_b - t_b/t_a)^2 (MF-151)', 'P': 'the six-cycle at E = 0 (MF-153)', 'E': 'tools/waves.py; tools/wave_atlas.py'},
     {'model': 'light in a dielectric multilayer', 'S': 'the Fibonacci word on the layers', 'H': 'Maxwell\'s equations at normal incidence', 'T': '[[cos d, (i/n) sin d], [i n sin d, cos d]]', 'group': 'SL2(C), real form SL2(R) by diag(1, i)', 'I': '(1/4)(nA/nB - nB/nA)^2 sin^2 dA sin^2 dB (MF-146)', 'P': 'transmittance, the six-cycle, PR-008', 'E': 'tools/optics.py; Core Appendix S.25'},
     {'model': 'sound in a layered medium', 'S': 'the Fibonacci word on the layers', 'H': 'the acoustic wave equation at normal incidence', 'T': '[[cos d, i Z sin d], [i sin d / Z, cos d]]', 'group': 'SL2(C), real form SL2(R) by diag(1, i)', 'I': 'as for light with n for 1/Z (MF-152)', 'P': 'transmittance, the six-cycle', 'E': 'tools/waves.py; Core Appendix S.26'},
     {'model': 'the phason pump', 'S': 'the Fibonacci word with its phason', 'H': 'the Kraus family of smooth potentials', 'T': 'the Bloch Hamiltonian on the torus of k and the phason', 'group': 'U(L) on the filled bands', 'I': 'the Chern number C = -q (topological, not dynamical)', 'P': 'the pumped particle number per cycle (MF-154; PR-009)', 'E': 'tools/waves.py; tools/wave_atlas.py; Core Appendix S.26'},
     {'model': 'exciton-polaritons (next construction)', 'S': 'the Fibonacci word, two letters', 'H': 'the coupled photon-exciton equations', 'T': 'to be derived; a two-component reduction to be tested', 'group': 'to be identified', 'I': 'to be computed', 'P': 'the polariton spectrum', 'E': 'Core Appendix S.23 (1)'}]
    json.dump({'_about': 'The Universal Transfer-Matrix Record of each wave model (Companion Part 228; F221): S the symbolic sequence, H the wave equation, T the transfer matrix, its matrix group, I the dynamical or topological invariant, P the predictions and observables, E the evidence.', 'models': mods},
              open(os.path.join(REPO, 'records', 'waves', 'models.json'), 'w'), indent=1)
    print('WAVE RECORDS: records/waves/six_cycle.json and records/waves/models.json written')
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt[:150], 'PASS' if ok else 'FAIL'))
        ok = all(o for _, o, _ in OUT); print('WAVE ATLAS SELFTEST: %d of %d | %s' % (sum(o for _, o, _ in OUT), len(OUT), 'PASS' if ok else 'FAIL')); sys.exit(0 if ok else 1)
    if a == ['--full']:
        for name, ok, txt in OUT: print('%s: %s %s' % (name, txt, 'PASS' if ok else 'FAIL'))
        sys.exit(0)
    if a == ['--write']: write(); sys.exit(0)
    print(__doc__); sys.exit(2)
