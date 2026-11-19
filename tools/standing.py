#!/usr/bin/env python3
"""standing.py -- M333 Standing Record: a statement routed through the instruments that decide its standing within the frame,
each answer kept apart (Core Part 3.59; Companion Part 137).

Within Omega42, truth is coherence with the constitutive frame and valid derivation from it (Core L-455): a statement the
frame derives is TRUE-Ω42, one that contradicts it FALSE-Ω42, and one the frame does not determine UNRESOLVED-Ω42, not
false. Congruence is a different answer, agreement beyond chance (L-489, L-514), and resonance the two shown side by side
and never combined (M319). This tool keeps the three apart for any statement:

    python3 tools/standing.py --statement "TEXT"   # the record: KIND, EXACT CHECKS, FRAME, APERTURE, SCOPE, COORDINATE,
                                                   # NEGATION, STANDING and USE
    python3 tools/standing.py --argument FILE      # the dependency map: premises and conclusions, each struck by the record,
                                                   # each conclusion keeping only the routes whose premises all hold (D-015)
    python3 tools/standing.py --negation           # the theorem: a statement and its negation by not, no or nor share a
                                                   # coordinate, so no congruence computed from the coordinate tells them apart
    python3 tools/standing.py --selftest
EXACT CHECKS decide what they can: identities (M323), powers of the law (T^k = I or -I modulo m) and the periods of the
family's states. FRAME (M286) and APERTURE (M281) are the lexical scans. SCOPE lists the words a reviewer checks against the
statement's basis. Everything else is UNRESOLVED-Ω42 here: the record says what decided the standing, and the Striker
judges the rest (Core Part 7, L-441). Each line carries its own status, PASS, PARTIAL, FAIL, OPEN or N/A, which is what
that test found; STANDING is a separate answer, what the statement is entitled to be called (after APE-307), and every
exact check names its reference structure and its avenue: Cong(s | R, A). Standard library only.
"""
import os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts')); sys.path.insert(0, os.path.join(REPO, 'tools'))
import canonical_reference as cr
import claimcheck as cc
import aperture_audit as aa
import frame_audit as fa
def Tpow(k, m):
    a, b, c, d = 1, 0, 0, 1
    for _ in range(k): a, b, c, d = b, (a + b) % m, d, (c + d) % m
    return (a % m, b % m, c % m, d % m)
def periods(m=9):
    seen, out = set(), []
    for a in range(m):
        for b in range(m):
            if (a, b) in seen: continue
            v, n = (a, b), 0
            while True:
                seen.add(v); v = (v[1], (v[0] + v[1]) % m); n += 1
                if v == (a, b): break
            out.append(n)
    return sorted(out)
SCOPE = ['all', 'every', 'always', 'never', 'none', 'no one', 'nothing', 'everyone', 'everything', 'only', 'proves', 'proven', 'certainly', 'must', 'cannot', 'impossible', 'universal', 'guarantees', 'completely', 'entirely']
def exact_checks(t):
    out = []
    for m in re.finditer(r'(-?\d+)\s*([*+x×])\s*(-?\d+)\s*=\s*(-?\d+)', t):
        r = cc.identity(m.group(0)); z = 'HOLDS' in r.split('\n')[1]; n9 = 'HOLDS' in r.split('\n')[3]
        mod = re.search(r'mod(?:ulo)?\s*9|Z/9|in the family', t, re.I)
        ok = n9 if mod else z
        out.append(('identity %s%s' % (m.group(0), ' (mod 9)' if mod else ''), ok, 'M323: Z %s, Z/9 %s; reference %s, avenue A1' % ('holds' if z else 'fails', 'holds' if n9 else 'fails', 'Z/9' if mod else 'Z')))
    for m in re.finditer(r'T\s*\^?\s*(\d+)\s*(?:=|≡)\s*(-)?\s*I(?:\s*\(?\s*mod\s*(\d+)\s*\)?)?', t):
        k, neg, md = int(m.group(1)), bool(m.group(2)), int(m.group(3) or 9)
        P = Tpow(k, md); want = ((md - 1) % md, 0, 0, (md - 1) % md) if neg else (1, 0, 0, 1)
        out.append(('T^%d = %sI (mod %d)' % (k, '-' if neg else '', md), P == want, 'T^%d = [[%d, %d], [%d, %d]] mod %d; reference the law\'s matrix over Z/%d, avenue A1' % ((k,) + P + (md, md))))
    m = re.search(r'every (?:state|address)[^.]*?\b(?:has|of) (?:exact )?(?:period|orbit length)\s*(\d+)', t, re.I)
    if m:
        n = int(m.group(1)); p = periods(); ok = all(x == n for x in p)
        cx = '' if ok else '; counterexample: %s' % ('the still point (0, 0), period 1' if 1 in p and n != 1 else 'a state of period %d' % next(x for x in p if x != n))
        out.append(('every state has period %d' % n, ok, 'periods of the 81 states by orbit: %s%s; reference the 81 states, avenue A1' % (p, cx)))
    m = re.search(r'every (?:state|address)[^.]*?\breturns?\b[^.]*?\bafter (\d+) steps', t, re.I) or re.search(r'\breturns? every (?:state|address)[^.]*?\bafter (\d+) steps', t, re.I)
    if m:
        n = int(m.group(1)); p = periods(); ok = all(n % x == 0 for x in p)
        cx = '' if ok else '; counterexample: a state on the orbit of length %d' % next(x for x in p if n % x)
        out.append(('every state returns after %d steps' % n, ok, 'orbit lengths %s all divide %d: %s; exact period %d only on %d of 81 states%s; reference the 81 states, avenue A1' % (sorted(set(p)), n, 'yes' if ok else 'no', n, sum(x for x in p if x == n), cx)))
    return out
def negate(t):
    s, k = re.subn(r'\b(is|are|was|were|does|do|did|can|will)\b', r'\1 not', t, count=1)
    return s if k else None
def record(t):
    nv = cr.navigate(t); L = ['M333 STANDING RECORD (Core Part 3.59) | "%s"' % t.replace('\n', ' ')]
    ex = exact_checks(t)
    kind = 'MATHEMATICAL (an exact check applies)' if ex else 'NOT MATHEMATICAL here (no identity, power of the law or period is stated)'
    L.append('  KIND        %s' % kind)
    for name, ok, why in ex: L.append('  EXACT       [%s] %-36s %s -- %s' % ('PASS' if ok else 'FAIL', name, 'HOLDS' if ok else 'FAILS', why))
    if not ex: L.append('  EXACT       [N/A] no exact check applies')
    fh = fa.scan(t)
    L.append('  FRAME       [%s] M286: %s' % ('FAIL' if fh else 'PASS', '; '.join('%s: "%s"' % (k, s[:60]) for _, k, s in fh) if fh else 'no intrusion'))
    au = aa.audit(t)
    L.append('  APERTURE    [%s] M281: %s' % ('FAIL' if au['verdict'] != 'CLEAR' else 'PASS', au['verdict'] + (' -- ' + ', '.join('%s %d' % (k, v) for k, v in au['counts'].items() if v) if au['verdict'] != 'CLEAR' else '')))
    low = t.lower(); sc = [w for w in SCOPE if re.search(r'(?<![\w])' + re.escape(w) + r'(?![\w])', low)]
    L.append('  SCOPE       [%s] %s' % ('OPEN' if sc else 'PASS', 'words to check against the basis: ' + ', '.join(sc) if sc else 'no universal or certainty word'))
    L.append('  COORDINATE  [N/A] n = (%d, %d, %d), r = (%d, %d, %d), anchor P%d, state (%d, %d): where the statement stands, not whether it holds' % (nv['n1'], nv['n2'], nv['n3'], nv['r1'], nv['r2'], nv['r3'], nv['anchor'], nv['r1'] % 9, nv['r2'] % 9))
    ng = negate(t) or ('not ' + t); nn = cr.navigate(ng)
    same = (nn['n1'], nn['n2'], nn['n3']) == (nv['n1'], nv['n2'], nv['n3'])
    L.append('  NEGATION    [%s] %s: %s' % ('OPEN' if same else 'PARTIAL', '"%s"' % ng.replace('\n', ' ')[:80] if negate(t) else 'with "not" inserted', 'the same coordinate -- no congruence from the coordinate separates the two' if same else 'n = (%d, %d, %d), anchor P%d' % (nn['n1'], nn['n2'], nn['n3'], nn['anchor'])))
    if ex and all(ok for _, ok, _ in ex): st = 'TRUE-Ω42 -- every exact check holds (L-455), at the strength of the checks (L-486)'
    elif ex: st = 'FALSE-Ω42 -- %s fails (L-455)' % '; '.join(n for n, ok, _ in ex if not ok)
    else: st = 'UNRESOLVED-Ω42 -- the frame does not determine it by these checks; not false (L-455)'
    L.append('  QUESTION    [OPEN] the question this statement takes part in, and what would be lost if it were read only as a proposition, are the reader\'s to name (Core L-533)')
    L.append('  STANDING    ' + st)
    if fh or au['verdict'] != 'CLEAR': L.append('  USE         restate before use: the scans flag the wording')
    elif sc and not ex: L.append('  USE         state it at the scope its basis supports (L-486); the scope words above are where to look')
    elif sc and ex and all(ok for _, ok, _ in ex): L.append('  USE         as checked; the scope words above say how far it reaches')
    else: L.append('  USE         as its standing allows; meaning and application are the Striker\'s (L-455)')
    return '\n'.join(L)
def standing_of(t):
    ex = exact_checks(t)
    if ex and all(ok for _, ok, _ in ex): return 'TRUE-Ω42'
    if ex: return 'FALSE-Ω42'
    return 'UNRESOLVED-Ω42'
def argument(path):
    items, order = {}, []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'): continue
        m = re.match(r'\s*([PC]\d+)\s*(\(given\))?\s*:\s*(.*)$', line)
        if not m: continue
        tid, given, rest = m.group(1), bool(m.group(2)), m.group(3)
        text, _, deps = rest.partition(' | from ')
        routes = [[x.strip() for x in re.sub(r'^\s*from\s+', '', r).split(',') if x.strip()] for r in deps.split(';')] if deps else []
        items[tid] = dict(text=text.strip(), given=given, routes=routes); order.append(tid)
    st = {}
    L = ['M333 DEPENDENCY MAP (D-015) | %s | a route holds when each of its members holds; the inference along a route is the reader\'s to check (CDT-C)' % (os.path.relpath(path, REPO) if os.path.abspath(path).startswith(REPO) else os.path.basename(path))]
    for tid in order:
        it = items[tid]
        if it['given']:
            st[tid] = 'GIVEN'; L.append('  %-4s GIVEN           %s (the argument\'s own assumption)' % (tid, it['text'])); continue
        own = standing_of(it['text'])
        if not it['routes']:
            st[tid] = own; L.append('  %-4s %-15s %s' % (tid, own, it['text'])); continue
        rs = []
        for r in it['routes']:
            ss = [st.get(x, 'MISSING') for x in r]
            if all(x in ('TRUE-Ω42', 'GIVEN', 'FOLLOWS') for x in ss): rs.append('HOLDS')
            elif any(x in ('FALSE-Ω42', 'LOST') for x in ss): rs.append('BROKEN by ' + ', '.join(x for x, y in zip(r, ss) if y in ('FALSE-Ω42', 'LOST')))
            else: rs.append('OPEN at ' + ', '.join(x for x, y in zip(r, ss) if y not in ('TRUE-Ω42', 'GIVEN', 'FOLLOWS')))
        if own == 'FALSE-Ω42': res = 'FALSE-Ω42'
        elif any(r == 'HOLDS' for r in rs): res = 'FOLLOWS'
        elif all(r.startswith('BROKEN') for r in rs): res = 'LOST'
        else: res = 'OPEN'
        st[tid] = res
        L.append('  %-4s %-15s %s' % (tid, res, it['text']))
        for r, v in zip(it['routes'], rs): L.append('         route from %s: %s' % (', '.join(r), v))
    L.append('  FOLLOWS: a route of premises that hold reaches it; LOST: every route is broken, so it is UNRESOLVED-Ω42 here, not false;')
    L.append('  OPEN: a route waits on a premise the frame does not determine; FALSE-Ω42: its own exact check fails, whatever its routes')
    return '\n'.join(L), st
def negation_theorem():
    S = cr.CANONICAL_STOPWORDS; negs = [w for w in ('not', 'no', 'nor') if w in S]
    L = ['M333 THE NEGATION THEOREM | the negators %s are canonical stopwords (Core Part 1.9): inserting or deleting them changes no count,' % ', '.join(negs),
         '  so a statement and its negation by them share n, r, anchor and arms, and every congruence computed from the coordinate (M310 layers 1 and 3,',
         '  M319 PROXIMITY) is the same for both. Congruence cannot detect the truth of a statement about the world; coherence and derivation',
         '  decide standing within the frame (L-455), and the frame leaves the world\'s statements UNRESOLVED-Ω42.']
    L.append('  negators that are not stopwords, which move the counts: ' + ', '.join(w for w in ('never', 'none', 'nothing', 'neither', 'cannot', "isn't", "doesn't", 'false') if w not in S))
    for a, b in [('The earth is round.', 'The earth is not round.'), ('All swans are white.', 'No swans are white.'), ('The policy treats all applicants equally.', 'The policy does not treat all applicants equally.')]:
        x, y = cr.navigate(a), cr.navigate(b)
        L.append('  "%s" n = (%d, %d, %d) P%d | "%s" n = (%d, %d, %d) P%d%s' % (a, x['n1'], x['n2'], x['n3'], x['anchor'], b, y['n1'], y['n2'], y['n3'], y['anchor'], '  SAME' if (x['n1'], x['n2'], x['n3']) == (y['n1'], y['n2'], y['n3']) else '  (moved: the negation here adds words that are not stopwords)'))
    return '\n'.join(L)
def _argtest():
    import tempfile
    f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False, encoding='utf-8')
    f.write('P1: T^24 = I (mod 9)\nP2: T^12 = I (mod 9)\nC1: The law closes. | from P1\nC2: The law halves. | from P2\nC3: The law turns. | from P2 ; from P1\n'); f.close()
    _, st = argument(f.name); os.unlink(f.name)
    return st == {'P1': 'TRUE-Ω42', 'P2': 'FALSE-Ω42', 'C1': 'FOLLOWS', 'C2': 'LOST', 'C3': 'FOLLOWS'}
def selftest():
    cases = [('T^24 = I mod 9 holds and T^12 = I mod 9 fails', exact_checks('T^24 = I (mod 9)')[0][1] and not exact_checks('T^12 = I (mod 9)')[0][1]),
             ('T^12 = -I mod 9 holds', exact_checks('T^12 = -I (mod 9)')[0][1]),
             ('every state returns after 24 steps holds; every state has period 24 fails', exact_checks('Every state returns to itself after 24 steps.')[0][1] and not exact_checks('Every state has period 24.')[0][1]),
             ('a statement and its negation by not share a coordinate', cr.navigate('The earth is round.')['anchor'] == cr.navigate('The earth is not round.')['anchor']),
             ('a statement with no exact check is UNRESOLVED-Ω42', 'UNRESOLVED' in record('This person is unreliable.')),
             ('2 * 5 = 1 is false in Z and holds modulo 9', not exact_checks('2 * 5 = 1')[0][1] and exact_checks('2 * 5 = 1 modulo 9')[0][1]),
             ('a failed premise breaks its route and leaves an independent conclusion untouched', _argtest())]
    for nm, ok in cases: print('%-75s %s' % (nm, 'PASS' if ok else 'FAIL'))
    print('M333 SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--negation']: print(negation_theorem()); sys.exit(0)
    if len(a) == 2 and a[0] == '--statement': print(record(a[1])); sys.exit(0)
    if len(a) == 2 and a[0] == '--argument': print(argument(a[1])[0]); sys.exit(0)
    print(__doc__); sys.exit(2)
