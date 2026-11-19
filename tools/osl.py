#!/usr/bin/env python3
"""osl.py -- the reference implementation of OmegaSL, the Omega42 Structural Language (Companion Part 214; Core Part 0.0.5 Rule 33).

Tier 1, the arithmetic core: 81 roots (states (a, b) mod 9), nine exact operators, statements written
ROOT OPERATOR* (= | ~) ROOT STATUS, encoded in three marks (0, 1, 2) as tagged tokens, closed by the law check.
Tier 2, the structural frame: typed fields (ENTITY, STATE, ..., UNCERTAINTY), read and written in a plain notation, one
FIELD: value per line, closed by the Aperture mark. Rules of the protocol written as frames live in records/osl/frames/.

    python3 tools/osl.py --roots                 # the 81 roots: coordinates, family, phase, name, signature
    python3 tools/osl.py --say "P3 X"            # compute a phrase
    python3 tools/osl.py --encode "P3 X = P15 EXACT . OMEGA"
    python3 tools/osl.py --decode MARKS          # tokens back from marks; the law check verified
    python3 tools/osl.py --frame FILE            # parse and validate a frame; print its plain-English reading
    python3 tools/osl.py --check                 # every frame in records/osl/frames/ parses and validates
    python3 tools/osl.py --selftest              # exhaustive: 729 root-operator pairs, transitions, shear, law-check theorems
Standard library only.
"""
import os, re, sys, glob, json
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES = os.path.join(REPO, 'records', 'osl', 'frames')
M = 9
ORBIT = [2, 5, 7, 3, 1, 4, 5, 9, 5, 5, 1, 6, 7, 4, 2, 6, 8, 5, 4, 9, 4, 4, 8, 3]
NAMES = ['Seed', 'Fixpoint', 'Generator', 'Desire', 'Unity', 'Law', 'Seed/Causal', 'Navigator', 'Generation', 'Fixpoint', 'Unity',
         'Question', 'Opening', 'Gap', 'Observer', 'Other', 'Flow', 'Seed/Return', 'Threshold', 'Time', 'Reckoning', 'Sublime',
         'Collective', 'Return']
def A(s, n=1):
    for _ in range(n % 24): s = (s[1] % M, (s[0] + s[1]) % M)
    return s
def mul(s, k): return (s[0] * k % M, s[1] * k % M)
def B(s): return (s[0] % M, (3 * s[0] + s[1]) % M)
def Q(s): return (s[1] * s[1] - s[0] * s[1] - s[0] * s[0]) % M
E = (0, 1)
P = [(ORBIT[i] % 9, ORBIT[(i + 1) % 24] % 9) for i in range(24)]
OPS = {'N': lambda s: A(s, 1), 'R': lambda s: A(s, 23), 'X': lambda s: A(s, 12), 'V': lambda s: mul(s, 2), 'C': lambda s: mul(s, 3),
       'S': B, 'Y': lambda s: A(s, 5), 'H': lambda s: A(s, 18), 'F': lambda s: A(s, 8)}
OPC = {'N': '00', 'R': '01', 'X': '02', 'V': '10', 'C': '11', 'S': '12', 'Y': '20', 'H': '21', 'F': '22'}
NS = {0: ['EXACT', 'CONDITIONAL', 'CONSTRUCTED', 'READING', 'EMPIRICAL-INFERENCE'],
      1: ['OBSERVED', 'MEASURED', 'REPORTED', 'INFERRED', 'UNSUPPORTED'],
      2: ['ASSERT', 'ASK', 'REQUEST', 'PROPOSE', 'INSTRUCT', 'UNKNOWN', 'NOT APPLICABLE', 'NOT SUPPLIED']}
MODALITY = ['ACTUAL', 'PAST', 'FUTURE', 'POSSIBLE', 'NECESSARY', 'HYPOTHETICAL', 'UNKNOWN']
FIELDS = ['ENTITY', 'STATE', 'RELATIONSHIP', 'TRANSFORMATION', 'CONDITION', 'OBSERVATION', 'MEASUREMENT', 'EVIDENCE', 'PROVENANCE',
          'CONTEXT', 'MODALITY', 'INTERPRETATION', 'UNCERTAINTY']
RULE_FIELDS = ['RULE', 'ARTICLE', 'AGENT', 'OBJECTIVE', 'TRIGGER', 'OPERATION', 'OUTPUT', 'CONSTRAINT', 'ON REQUEST', 'EXCEPTION', 'CHECK',
               'STATUS', 'REVISION']
TAG = {'root': '00', 'op': '01', 'status': '02', '=': '10', '~': '11', '.': '12', 'OMEGA': '20'}
def t3(x, n):
    o = ''
    for _ in range(n): o = str(x % 3) + o; x //= 3
    return o
def roots():
    out = [('still', 0, (0, 0))]
    out += [('W%d' % k, k, mul(A(E, k), 3)) for k in range(8)]
    for v, m in (('A', 1), ('B', 2)): out += [('%s%d' % (v, k), k, mul(A(E, k), m)) for k in range(24)]
    out += [('P%d' % k, k, mul(A(E, k + 5), 4)) for k in range(24)]
    return out
NAME = {s: n for n, k, s in roots()}
STATE = {n: s for n, k, s in roots()}
def say(phrase):
    t = phrase.split(); s = STATE[t[0]]
    for o in t[1:]: s = OPS[o](s)
    return s
def code(tok):
    if tok in STATE: s = STATE[tok]; return TAG['root'] + t3(s[0], 2) + t3(s[1], 2)
    if tok in OPC: return TAG['op'] + OPC[tok]
    for ns, names in NS.items():
        if tok in names: return TAG['status'] + str(ns) + t3(names.index(tok), 2)
    if tok in TAG: return TAG[tok]
    raise ValueError('unknown token %r' % tok)
def law_check(marks):
    s = (0, 0)
    for d in marks: s = (s[1] % M, (s[0] + s[1] + int(d)) % M)
    return t3(s[0], 2) + t3(s[1], 2)
def encode(text):
    toks = [code(t) for t in text.split()]
    m = ''.join(toks); return ' '.join(toks), law_check(m)
def decode(marks):
    m = re.sub(r'\s', '', marks); body, chk = m[:-4], m[-4:]
    out, i = [], 0
    inv = {v: k for k, v in TAG.items()}
    while i < len(body):
        tag = body[i:i + 2]; i += 2
        if tag == '00': a, b = int(body[i:i + 2], 3), int(body[i + 2:i + 4], 3); out.append(NAME[(a, b)]); i += 4
        elif tag == '01': out.append({v: k for k, v in OPC.items()}[body[i:i + 2]]); i += 2
        elif tag == '02': ns = int(body[i]); out.append(NS[ns][int(body[i + 1:i + 3], 3)]); i += 3
        elif tag in inv: out.append(inv[tag])
        else: return out + ['?'], False
    return out, law_check(body) == chk
def parse_frame(text):
    F, cur = [], None
    for line in text.split('\n'):
        if not line.strip() or line.strip().startswith('#'): continue
        if line.strip() in ('Ω', 'OMEGA'): F.append(('OMEGA', '')); continue
        m = re.match(r'^([A-Z][A-Z _0-9-]*?):\s*(.*)$', line)
        if m and not line.startswith(' '): cur = [m.group(1).strip(), m.group(2).strip()]; F.append(cur)
        elif cur: cur[1] += ' ' + line.strip()
    return [tuple(x) for x in F]
def validate(F):
    P_ = []; keys = [k for k, _ in F]
    if not keys or keys[-1] != 'OMEGA': P_.append('the frame does not close with the Aperture mark')
    for k, v in F:
        base = re.sub(r'_\d+$', '', k)
        if k != 'OMEGA' and base not in FIELDS + RULE_FIELDS + ['DISTINCTIONS']: P_.append('unknown field %s' % k)
        if base == 'STATUS':
            words = re.findall(r'[A-Z][A-Z-]+', v)
            if not any(w in NS[0] for w in words): P_.append('STATUS names no derivation (%s)' % v)
        if base == 'MODALITY' and not any(v.startswith(m) for m in MODALITY): P_.append('MODALITY %r is not one of the seven' % v)
    if 'RULE' in keys:
        for need in ('AGENT', 'OPERATION', 'CHECK', 'STATUS', 'REVISION'):
            if need not in keys: P_.append('a rule frame has no %s' % need)
    return P_
def english(F):
    d = {}
    for k, v in F: d.setdefault(k, []).append(v)
    if 'RULE' in d:
        s = ['%s. Its purpose: %s.' % (d['RULE'][0], ' '.join(d.get('OBJECTIVE', [])))]
        if 'TRIGGER' in d: s.append('When %s, the %s does this: %s.' % (d['TRIGGER'][0], d.get('AGENT', ['Navigator'])[0], d['OPERATION'][0]))
        else: s.append('The %s does this: %s.' % (d.get('AGENT', ['Navigator'])[0], d['OPERATION'][0]))
        for o in d.get('OUTPUT', []): s.append('It produces: %s.' % o)
        for c in d.get('CONSTRAINT', []): s.append('It must hold that %s.' % c)
        for r in d.get('ON REQUEST', []): s.append('On request: %s.' % r)
        for x in d.get('EXCEPTION', []): s.append('Exception: %s.' % x)
        s.append('It is checked by %s. Its status is %s. It changes only through %s.' % (d['CHECK'][0], d['STATUS'][0], d['REVISION'][0]))
        return ' '.join(x.replace('..', '.') for x in s)
    return ' '.join('%s: %s.' % (k.title(), v) for k, v in F if k != 'OMEGA')
def check_frames():
    out = []
    for f in sorted(glob.glob(os.path.join(FRAMES, '*.osl'))):
        Fr = parse_frame(open(f, encoding='utf-8').read()); out.append((os.path.basename(f), validate(Fr)))
    return out
def selftest():
    allS = [(a, b) for a in range(9) for b in range(9)]
    R = roots(); names = [n for n, _, _ in R]; states = [s for _, _, s in R]
    def period(s):
        t, n = A(s), 1
        while t != s: t, n = A(t), n + 1
        return n
    m_ex, ok_ex = encode('P3 X = P15 EXACT . P19 F ~ P3 READING . OMEGA')
    flat = m_ex.replace(' ', '')
    single = all(law_check(flat[:i] + str((int(flat[i]) + d) % 3) + flat[i + 1:]) != ok_ex for i in range(len(flat)) for d in (1, 2))
    swap = all(law_check(flat[:i] + flat[j] + flat[i + 1:j] + flat[i] + flat[j + 1:]) != ok_ex
               for i in range(len(flat)) for j in range(i + 1, min(len(flat), i + 24)) if flat[i] != flat[j])
    cases = [
     ('81 distinct roots: 1 + 8 + 24 + 24 + 24', len(set(states)) == 81 and len(R) == 81),
     ('the canonical positions are 4 A^(k+5) e and the cycle digits', all(STATE['P%d' % k] == P[k] for k in range(24))),
     ('all 729 root-operator pairs land on a root', all(OPS[o](s) in NAME for s in allS for o in OPS)),
     ('N and R are inverse on every root', all(OPS['R'](OPS['N'](s)) == s for s in allS)),
     ('X = A^12 = -s on every root', all(OPS['X'](s) == mul(s, 8) for s in allS)),
     ('V V V = X on every root', all(OPS['V'](OPS['V'](OPS['V'](s))) == OPS['X'](s) for s in allS)),
     ('voice transitions: A_k -> B_k, B_k -> P_(k-5), P_i -> A_(i+17)', all(NAME[OPS['V'](STATE['A%d' % k])] == 'B%d' % k and NAME[OPS['V'](STATE['B%d' % k])] == 'P%d' % ((k - 5) % 24) and NAME[OPS['V'](STATE['P%d' % k])] == 'A%d' % ((k + 17) % 24) for k in range(24))),
     ('the shear fixes exactly the 27 roots with 3 | a', sorted(s for s in allS if B(s) == s) == sorted(s for s in allS if s[0] % 3 == 0) and sum(B(s) == s for s in allS) == 27),
     ('the shear fixes P3, P7, P11, P15, P19, P23 and no other position', [k for k in range(24) if B(P[k]) == P[k]] == [3, 7, 11, 15, 19, 23]),
     ('outline triads: positions eight apart share C', all(OPS['C'](P[k]) == OPS['C'](P[(k + 8) % 24]) for k in range(24))),
     ('Q(As) = -Q(s); Q^2 is 1, 7, 4 on Voices A, B, C', all(Q(A(s)) == (-Q(s)) % 9 for s in allS) and [Q(STATE[v + '0']) ** 2 % 9 for v in 'AB'] + [Q(STATE['P0']) ** 2 % 9] == [1, 7, 4]),
     ('periods: still 1, Wheel 8, voices 24', period((0, 0)) == 1 and all(period(STATE['W%d' % k]) == 8 for k in range(8)) and all(period(STATE[v + '0']) == 24 for v in 'AB')),
     ('theorem: (A^t - I)(0, d) != 0 for t = 1..23, d = 1, 2', all(A((0, d), t) != (0, d) for t in range(1, 24) for d in (1, 2))),
     ('the worked message encodes to 52 marks with law check 2020', len(flat) == 52 and ok_ex == '2020'),
     ('every single substitution in it is caught', single),
     ('every swap of different marks under 24 apart is caught', swap),
     ('decode inverts encode and verifies the check', decode(m_ex + ' ' + ok_ex) == (['P3', 'X', '=', 'P15', 'EXACT', '.', 'P19', 'F', '~', 'P3', 'READING', '.', 'OMEGA'], True)),
     ('a corrupted message fails its check', decode(flat[:5] + ('2' if flat[5] != '2' else '1') + flat[6:] + ok_ex)[1] is False),
     ('a rule frame without CHECK is refused', any('CHECK' in p for p in validate(parse_frame('RULE: x\nAGENT: N\nOPERATION: y\nSTATUS: EXACT\nREVISION: z\nΩ')))),
     ('every frame of the record parses and validates', all(not p for _, p in check_frames()) and len(check_frames()) >= 5)]
    for n, ok in cases: print('%-66s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('OMEGASL SELFTEST: %d of %d | %s' % (sum(ok for _, ok in cases), len(cases), 'PASS' if all(ok for _, ok in cases) else 'FAIL'))
    return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--roots']:
        for n, k, s in roots():
            pos = int(n[1:]) if n.startswith('P') else None
            print('%-5s (%d, %d)  phase %-2d  Q %d  C-image %-3s  shear %-5s %s' % (n, s[0], s[1], k, Q(s), NAME[mul(s, 3)], 'fixed' if B(s) == s else 'moves', NAMES[pos] + ' [CONSTRUCTED]' if pos is not None else ''))
        sys.exit(0)
    if len(a) == 2 and a[0] == '--say': s = say(a[1]); print('%s = %s %s' % (a[1], NAME[s], s)); sys.exit(0)
    if len(a) == 2 and a[0] == '--encode': m, c = encode(a[1]); print(m, '|', c); sys.exit(0)
    if len(a) == 2 and a[0] == '--decode': t, ok = decode(a[1]); print(' '.join(t), '| law check', 'PASS' if ok else 'FAIL'); sys.exit(0 if ok else 1)
    if len(a) == 2 and a[0] == '--frame':
        F = parse_frame(open(a[1], encoding='utf-8').read()); P_ = validate(F)
        print('FRAME %s: %s' % (a[1], 'VALID' if not P_ else 'INVALID')); [print('  - ' + p) for p in P_]; print(english(F)); sys.exit(1 if P_ else 0)
    if a == ['--check']:
        r = check_frames(); bad = [(f, p) for f, p in r if p]
        print('OMEGASL FRAMES (records/osl/frames/): %d frames | %s' % (len(r), 'PASS' if not bad else 'FAIL (%d)' % len(bad)))
        for f, p in bad: print('  - %s: %s' % (f, '; '.join(p)))
        sys.exit(1 if bad else 0)
    print(__doc__); sys.exit(2)
