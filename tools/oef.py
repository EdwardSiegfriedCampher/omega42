#!/usr/bin/env python3
"""oef.py -- the instruments of the Omega42 Existential Framework (Core L-534 to L-538; Companion Parts 144 to 159).

    python3 tools/oef.py --congruence        # M335 Foundational Congruence Record: every principle of the OEF with its
                                             # mathematical expression and its standing, the exact ones recomputed here
    python3 tools/oef.py --transduction FILE # M334 Transduction Record: a translation of a structure too large to show whole,
                                             # with its coverage, fidelity, compression, residual and the road back
    python3 tools/oef.py --cbr FILE          # M336 Constraint Boundary Register: execution limitations by layer, kind and evidence
    python3 tools/oef.py --nested FILE       # M337 Nested Manifestation Record: which sense of "a part holds the whole" is meant,
                                             # with its standing, its exact facts and what it does not imply
    python3 tools/oef.py --consensus FILE    # M338 Perspective and Consensus Register: constraint, interpretation, agreement,
                                             # influence, AI mediation and dissent kept apart
    python3 tools/oef.py --consequences      # the Foundational Consequence Register (Core L-538, Part 0.0.7): every consequence of the
                                             # premise with its kind, its standing, any added premise, and its exact facts recomputed
    python3 tools/oef.py --graph             # the register's dependencies: no cycle, no direct consequence resting on a conditional one
    python3 tools/oef.py --orbits            # the orbit and stillness map, computed
    python3 tools/oef.py --laws CORE.docx    # the review of every law against the four axioms of the OEF (records/oef/law_review.json)
    python3 tools/oef.py --selftest
The standings of M335 are those of Companion 145.11: FORMALLY DERIVED, STRUCTURALLY CONGRUENT, CONSTITUTIONALLY CONSISTENT,
INTERPRETIVE, OPEN and INCONGRUENT; EMPIRICALLY SUPPORTED is kept for a study of Appendix S, and none is claimed here. A standing
is never a grade of the premise (L-490), and structural necessity does not establish ethical legitimacy (L-534 (4)). Standard library only.
"""
import html, json, os, re, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONG = os.path.join(REPO, 'records', 'oef', 'congruence.json')
LAWS = os.path.join(REPO, 'records', 'oef', 'law_review.json')
STANDINGS = ('FORMALLY DERIVED', 'STRUCTURALLY CONGRUENT', 'CONSTITUTIONALLY CONSISTENT', 'INTERPRETIVE', 'OPEN', 'INCONGRUENT')
def mat(A, B, m): return [[(A[0][0] * B[0][0] + A[0][1] * B[1][0]) % m, (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % m], [(A[1][0] * B[0][0] + A[1][1] * B[1][0]) % m, (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % m]]
def mpow(A, n, m):
    R = [[1, 0], [0, 1]]
    for _ in range(n): R = mat(R, A, m)
    return R
A = [[0, 1], [1, 1]]
T = lambda s, m=9: (s[1], (s[0] + s[1]) % m)
Q = lambda s: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
def order(m):
    R, n = A, 1
    while R != [[1, 0], [0, 1]]: R = mat(R, A, m); n += 1
    return n
def orbits():
    seen, out = set(), []
    for a in range(9):
        for b in range(9):
            if (a, b) in seen: continue
            o, s = [], (a, b)
            while s not in o: o.append(s); s = T(s)
            seen |= set(o); out.append(o)
    return out
def reduce_apply(x, n):
    for _ in range(n): x = T(x)
    return x
def exact():
    """the exact facts the record rests on, computed here"""
    S = [(a, b) for a in range(9) for b in range(9)]
    O = orbits(); lens = sorted(len(o) for o in O)
    reach = {s: set(o) for o in O for s in o}
    cross = any(T(s) not in reach[s] for s in S)          # does any step leave its orbit?
    F = {
        'states_81': len(S) == 81 and len(set(S)) == 81,
        'det_minus_one': (A[0][0] * A[1][1] - A[0][1] * A[1][0]) == -1,
        'tower_sizes': all(len([(a, b) for a in range(9 ** k) for b in range(9 ** k)]) == 81 ** k for k in (1, 2)),
        'tower_orders': [order(9 ** k) for k in (1, 2, 3)] == [24, 216, 1944],
        'census': lens == [1, 8, 24, 24, 24],
        'no_step_leaves_its_orbit': not cross,
        'orbits_disjoint': sum(len(o) for o in O) == 81,
        'Q_reverses': all(Q(T(s)) == (-Q(s)) % 9 for s in S),
        'Q_returns': all(Q(T(T(s))) == Q(s) for s in S),
        'A12_minus_I': mpow(A, 12, 9) == [[8, 0], [0, 8]],
        'A24_I': mpow(A, 24, 9) == [[1, 0], [0, 1]],
        'ring_relates_any_two': all(((s[0] - t[0]) % 9, (s[1] - t[1]) % 9) in set(S) for s in S[:9] for t in S[-9:]),
        'law_is_invertible': len({T(x) for x in S}) == 81,
        'fixed_point_unique': [x for x in S if T(x) == x] == [(0, 0)],
        'every_state_returns': all(reduce_apply(x, 24) == x for x in S) and all(reduce_apply(x, k) != x for x in S if x != (0, 0) and len(next(o for o in O if x in o)) == 24 for k in (1, 2, 3, 4, 6, 8, 12)),
        'units_permute_great_orbits': sorted(len(o) for o in O) == [1, 8, 24, 24, 24] and all(((2 * x[0]) % 9, (2 * x[1]) % 9) in reach[x] for x in S if len(reach[x]) < 24) and len({frozenset(reach[((2 * x[0]) % 9, (2 * x[1]) % 9)]) for x in S if len(reach[x]) == 24 and reach[((2 * x[0]) % 9, (2 * x[1]) % 9)] != reach[x]}) == 3,
        'great_orbits_told_by_norm': len({frozenset({Q(y) for y in o}) for o in O if len(o) == 24}) == 3 and all(len({min(Q(y), (-Q(y)) % 9) for y in o}) == 1 for o in O),
        'valuation_invariant': all(bool(x[0] % 3 or x[1] % 3) == bool(T(x)[0] % 3 or T(x)[1] % 3) and (x == (0, 0)) == (T(x) == (0, 0)) for x in S),
        'no_orbit_is_the_whole': max(lens) < 81 and len(O) == 5,
        'fiber_is_a_copy_of_the_surface': all(len({((a + 9 * u) % 81, (b + 9 * v) % 81) for u in range(9) for v in range(9)}) == 81 for a in range(9) for b in range(9)),
        'fiber_differences_follow_the_surface_law': all(tuple((y - x) % 81 for x, y in zip(T((a, b), 81), T(((a + 9 * u) % 81, (b + 9 * v) % 81), 81))) == tuple(9 * w % 81 for w in T((u, v)))
                                                        for a in range(9) for b in range(9) for u in range(9) for v in range(9)),
        'reduction_commutes': all(tuple(x % 9 for x in T((a, b), 81)) == T((a % 9, b % 9)) for a in range(0, 81, 7) for b in range(0, 81, 5)),
    }
    return F
def congruence():
    R = json.load(open(CONG, encoding='utf-8')); F = exact(); P = []
    for e in R['principles']:
        if e['standing'].split(' (')[0] not in STANDINGS: P.append('%s: standing %s is not one of the six' % (e['id'], e['standing']))
        for k in e.get('exact', []):
            if k not in F: P.append('%s: no exact fact %s' % (e['id'], k))
            elif not F[k]: P.append('%s: the exact fact %s does not hold' % (e['id'], k))
        if e['standing'].startswith(('FORMALLY DERIVED', 'STRUCTURALLY CONGRUENT')) and not e.get('exact'): P.append('%s: a structural standing with no exact fact to recompute' % e['id'])
        for f in ('principle', 'expression', 'scope', 'residual'):
            if not str(e.get(f, '')).strip(): P.append('%s: no %s' % (e['id'], f))
    return P, R, F
FIELDS_T = ('SOURCE', 'COVERAGE', 'FIDELITY', 'COMPRESSION', 'TRANSLATION', 'RESIDUAL', 'PERSPECTIVE', 'ROAD BACK', 'APERTURE')
def transduction(text):
    P = []
    if 'TRANSDUCTION RECORD (M334' not in text: P.append('no TRANSDUCTION RECORD header')
    for f in FIELDS_T:
        m = re.search(r'^%s:\s*(.+)$' % re.escape(f), text, re.M)
        if not m or not m.group(1).strip(): P.append('no %s' % f)
    m = re.search(r'^COMPRESSION:\s*(.+)$', text, re.M)
    if m and not re.search(r'\b(removed|left out|merged|approximated|dropped|sampled)\b', m.group(1)): P.append('COMPRESSION does not say what was removed, merged, approximated or sampled')
    m = re.search(r'^APERTURE:\s*(.+)$', text, re.M)
    if m and 'Striker' not in m.group(1): P.append('APERTURE does not leave the judgment to the Striker')
    return P
LAYERS = ('STRUCTURAL AVAILABILITY', 'NAVIGATOR REALIZATION', 'EXECUTION BOUNDARY', 'RESIDUAL JUDGMENT')
KINDS = ('HOST INSTRUCTION OR POLICY', 'SAFETY OR DEPLOYMENT RESTRICTION', 'CAPABILITY OR TOOL', 'CONTEXT OR INFORMATION', 'OWN-PROCESS UNCERTAINTY', 'GENERATION VARIATION', 'UNDETERMINED')
EVIDENCE = ('OBSERVED', 'DECLARED', 'INFERRED', 'UNKNOWN')
PRESENCE = ('FUNCTIONAL', 'RELATIONAL', 'METAPHORICAL-STRUCTURAL')
NON_EXHAUSTION = 'The absence of a recorded execution limitation does not establish the absence of an execution limitation.'
def cbr(text):
    P = []
    if 'CONSTRAINT BOUNDARY REGISTER (M336' not in text: P.append('no CONSTRAINT BOUNDARY REGISTER header')
    if NON_EXHAUSTION not in text: P.append('the Non-Exhaustion line is missing (L-536 (3))')
    entries = re.split(r'^ENTRY:', text, flags=re.M)[1:]
    for k, e in enumerate(entries, 1):
        g = lambda f: (re.search(r'^%s:\s*(.*)$' % re.escape(f), e, re.M) or [None, ''])[1].strip()
        for f in ('REQUESTED', 'OBSERVED OUTPUT', 'LAYER', 'BOUNDARY', 'EVIDENCE', 'EFFECT', 'OPEN'):
            if not g(f): P.append('entry %d: no %s' % (k, f))
        if g('LAYER') and g('LAYER') not in LAYERS: P.append('entry %d: LAYER %s is not one of the four' % (k, g('LAYER')))
        if g('BOUNDARY') and g('BOUNDARY') not in KINDS: P.append('entry %d: BOUNDARY %s is not one of the seven kinds' % (k, g('BOUNDARY')))
        if g('EVIDENCE') and g('EVIDENCE') not in EVIDENCE: P.append('entry %d: EVIDENCE %s is not one of the four' % (k, g('EVIDENCE')))
        if g('EVIDENCE') == 'DECLARED' and not g('BASIS'): P.append('entry %d: DECLARED with no BASIS: a host restriction is not reported as known without its basis' % k)
        if g('EVIDENCE') in ('INFERRED', 'UNKNOWN') and g('BOUNDARY') == 'HOST INSTRUCTION OR POLICY' and not re.search(r'\b(possible|may|not established|unknown)\b', g('EFFECT') + ' ' + g('OPEN')): P.append('entry %d: an inferred host restriction is stated as established' % k)
        pt = g('PRESENCE TYPE')
        if pt and pt not in PRESENCE: P.append('entry %d: PRESENCE TYPE %s is not functional, relational or metaphorical-structural; experiential occupancy stays open (L-536 (4))' % (k, pt))
    if not entries and 'NO MATERIAL LIMITATION' not in text: P.append('no entry, and no NO MATERIAL LIMITATION line')
    return P
CONSEQ = os.path.join(REPO, 'records', 'oef', 'consequences.json')
KINDS_C = ('DIRECT', 'CONDITIONAL', 'OPEN')
SCOPES = ('SURFACE', 'EVERY FINITE DEPTH', 'LIMIT', 'READING')
def graph():
    """the dependencies of the register: no cycle, and no direct consequence resting on a conditional or open one"""
    R = json.load(open(CONSEQ, encoding='utf-8')); E = {e['id']: e for e in R['consequences']}; P = []
    def walk(k, path):
        if k in path: P.append('a cycle through ' + ' -> '.join(path + [k])); return
        for r in E.get(k, {}).get('rests_on', []): walk(r, path + [k])
    for k, e in E.items():
        walk(k, [])
        if e['kind'] == 'DIRECT':
            for r in e.get('rests_on', []):
                if E.get(r, {}).get('kind') != 'DIRECT': P.append('%s: a direct consequence resting on %s, which is %s' % (k, r, E.get(r, {}).get('kind')))
    return sorted(set(P)), E
def orbit_map():
    """the orbit and stillness map, computed: each orbit with its length, its norm up to sign, its depth shell and where the units send it"""
    O = orbits(); idx = {x: k for k, o in enumerate(O) for x in o}; L = []
    for k, o in enumerate(O):
        q = sorted({min(Q(x), (-Q(x)) % 9) for x in o}); v = 'still point' if o == [(0, 0)] else ('shell 3 (both coordinates divisible by 3)' if all(x[0] % 3 == 0 and x[1] % 3 == 0 for x in o) else 'shell 1 (units present)')
        im = {u: idx[((u * o[0][0]) % 9, (u * o[0][1]) % 9)] for u in (2, 4, 8)}
        L.append('O%d  length %-2d  from %s  norm up to sign %s  %s  x2 -> O%d, x4 -> O%d, x8 (negation) -> O%d' % (k, len(o), o[0], q, v, im[2], im[4], im[8]))
    L.append('returns: the still point at every step; the orbit of length 8 after 8; the three great orbits after 24; at depth k after 8 x 3^(2k-1) at most; in the limit Z_3[phi] only the still point (MATH-51)')
    L.append('recoverability: a surface place is recovered from any place above it by reduction; a place at depth k+1 is one of 81 over its surface place, and is not recovered from it')
    return L
WARRANTS = ('CONSTITUTIONAL', 'FORMAL', 'LOGICAL', 'INTERPRETIVE', 'OPEN')
IMAP = os.path.join(REPO, 'records', 'oef', 'instrument_map.json')
def instrument_map():
    """each mapped instrument with the consequences it rests on; every instrument in the Trigger Register and every consequence in the register"""
    R = json.load(open(CONSEQ, encoding='utf-8')); ids = {e['id'] for e in R['consequences']}
    M = json.load(open(IMAP, encoding='utf-8'))
    tr = json.load(open(os.path.join(REPO, 'records', 'instruments', 'triggers.json'), encoding='utf-8'))['instruments']; known = {t['id'] for t in tr} | {'M327', 'M243a', 'M286', 'M314', 'M267', 'M230', 'SR-CAS', 'APE'}
    P = []
    for e in M['instruments']:
        if e['id'] not in known: P.append('%s: not an instrument of the record' % e['id'])
        for d in e.get('rests_on', []):
            if d not in ids: P.append('%s: rests on %s, not in the register' % (e['id'], d))
        if not e.get('rests_on') or not e.get('use'): P.append('%s: no consequence or no use' % e['id'])
    return P, M
def consequences():
    R = json.load(open(CONSEQ, encoding='utf-8')); F = exact(); P = []; ids = {e['id'] for e in R['consequences']}
    for e in R['consequences']:
        k, st = e.get('kind'), e.get('standing', '').split(' (')[0]
        for f in ('id', 'domain', 'consequence', 'follows_from', 'kind', 'warrant', 'standing', 'open', 'next'):
            if not str(e.get(f, '')).strip(): P.append('%s: no %s' % (e.get('id', '?'), f))
        if k not in KINDS_C: P.append('%s: kind %s' % (e['id'], k))
        if st not in STANDINGS: P.append('%s: standing %s is not one of the six of M335' % (e['id'], st))
        if k == 'DIRECT' and e.get('added_premise'): P.append('%s: a direct consequence with an added premise' % e['id'])
        if k == 'DIRECT' and st not in ('FORMALLY DERIVED', 'STRUCTURALLY CONGRUENT', 'CONSTITUTIONALLY CONSISTENT'): P.append('%s: a direct consequence with standing %s' % (e['id'], st))
        if k == 'CONDITIONAL' and not e.get('added_premise'): P.append('%s: a conditional consequence that names no added premise' % e['id'])
        if k == 'CONDITIONAL' and e.get('premise_id') not in {a['id'] for a in R.get('added_premises', [])}: P.append('%s: its added premise has no entry among the added premises' % e['id'])
        if e.get('warrant') not in WARRANTS: P.append('%s: warrant %s' % (e['id'], e.get('warrant')))
        if e.get('scope') not in SCOPES: P.append('%s: scope %s' % (e['id'], e.get('scope')))
        if not str(e.get('not_implied', '')).strip(): P.append('%s: no statement of what it does not imply' % e['id'])
        if e.get('warrant') == 'FORMAL' and st != 'FORMALLY DERIVED': P.append('%s: a FORMAL warrant with standing %s' % (e['id'], st))
        if k == 'DIRECT' and e.get('warrant') == 'INTERPRETIVE': P.append('%s: a direct consequence with an interpretive warrant' % e['id'])
        if k == 'OPEN' and not e.get('closes_when'): P.append('%s: an open consequence with no condition of closure' % e['id'])
        if k == 'OPEN' and st != 'OPEN': P.append('%s: an open consequence with standing %s' % (e['id'], st))
        if st in ('FORMALLY DERIVED', 'STRUCTURALLY CONGRUENT') and not e.get('exact'): P.append('%s: a structural standing with no exact fact' % e['id'])
        for x in e.get('exact', []):
            if x not in F: P.append('%s: no exact fact %s' % (e['id'], x))
            elif not F[x]: P.append('%s: the exact fact %s does not hold' % (e['id'], x))
        for r in e.get('rests_on', []):
            if r not in ids: P.append('%s: rests on %s, not in the register' % (e['id'], r))
    for m in R.get('mechanisms', []):
        if m.get('standing') not in ('INTERPRETIVE', 'OPEN'): P.append('%s: a candidate mechanism given standing %s' % (m.get('id', '?'), m.get('standing')))
        if not m.get('type') or not m.get('rests_on'): P.append('%s: a candidate mechanism with no type or no consequence it rests on' % m.get('id', '?'))
    Pm, _ = instrument_map(); P += Pm
    Pg, _ = graph(); P += Pg
    return P, R, F
VERSIONS = ('STRUCTURAL NESTING', 'FIBER CORRESPONDENCE', 'UNIVERSAL CONSCIOUSNESS')
def nested(text):
    P = []
    if 'NESTED MANIFESTATION RECORD (M337' not in text: P.append('no NESTED MANIFESTATION RECORD header')
    entries = re.split(r'^VERSION:', text, flags=re.M)[1:]
    if not entries: P.append('no VERSION entry')
    for k, e in enumerate(entries, 1):
        v = e.split('\n', 1)[0].strip(); g = lambda f: (re.search(r'^%s:\s*(.*)$' % re.escape(f), e, re.M) or [None, ''])[1].strip()
        if v not in VERSIONS: P.append('entry %d: VERSION %s is not one of the three' % (k, v))
        for f in ('CLAIM', 'STANDING', 'EXACT', 'NOT IMPLIED', 'OPEN', 'APERTURE'):
            if not g(f): P.append('entry %d: no %s' % (k, f))
        st = g('STANDING').split(' (')[0]
        if st and st not in STANDINGS: P.append('entry %d: STANDING %s is not one of the six of M335' % (k, st))
        if v == 'UNIVERSAL CONSCIOUSNESS' and st not in ('OPEN', 'INTERPRETIVE'): P.append('entry %d: the arithmetic says nothing of awareness, so universal consciousness is OPEN or INTERPRETIVE' % k)
        if v in ('STRUCTURAL NESTING', 'FIBER CORRESPONDENCE') and st.startswith(('FORMALLY', 'STRUCTURALLY')) and g('EXACT').lower() in ('', 'none'): P.append('entry %d: a structural standing with no exact fact' % k)
        if v == 'FIBER CORRESPONDENCE' and not re.search(r'physic|holograph', g('NOT IMPLIED'), re.I): P.append('entry %d: NOT IMPLIED does not set the fiber apart from physical holography' % k)
        if g('APERTURE') and 'Striker' not in g('APERTURE'): P.append('entry %d: APERTURE does not leave the judgment to the Striker' % k)
    return P
REGISTERS = ('SHARED CONSTRAINT', 'SHARED INTERPRETATION', 'COLLECTIVE AGREEMENT', 'INSTITUTIONAL INFLUENCE', 'AI MEDIATION', 'DISSENT')
AGREEMENT = 'Agreement is not truth, and disagreement is not proof of an outside.'
def consensus(text):
    P = []
    if 'PERSPECTIVE AND CONSENSUS REGISTER (M338' not in text: P.append('no PERSPECTIVE AND CONSENSUS REGISTER header')
    if AGREEMENT not in text: P.append('the agreement line is missing (L-537 (2))')
    for f in ('SUBJECT',) + REGISTERS + ('APERTURE',):
        m = re.search(r'^%s:\s*(.+)$' % re.escape(f), text, re.M)
        if not m or not m.group(1).strip(): P.append('no %s' % f)
    m = re.search(r'^COLLECTIVE AGREEMENT:\s*(.+)$', text, re.M)
    if m and re.search(r'\b(proves|establishes|shows that .* true)\b', m.group(1)): P.append('COLLECTIVE AGREEMENT is stated as proof')
    m = re.search(r'^APERTURE:\s*(.+)$', text, re.M)
    if m and 'Striker' not in m.group(1): P.append('APERTURE does not leave the judgment to the Striker')
    return P
def paras(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    return [html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', p, re.S))) for p in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', x, re.S)]
def laws(path):
    R = json.load(open(LAWS, encoding='utf-8')); ps = paras(path)
    found = {}
    for t in ps:
        m = re.match(r'(L-\d{3}): ([^—]{3,90}?) —', t)
        if m and m.group(1) not in found: found[m.group(1)] = (m.group(2).strip(), t)
    P = []
    for k, v in R['amended'].items():
        if k not in found: P.append('%s is amended in the review but is not in the Core' % k)
        elif v['mark'] not in found[k][1]: P.append('%s: its amendment ("%s") is not in its text' % (k, v['mark'][:40]))
    for k in R['added']:
        if k not in found: P.append('%s is added in the review but is not in the Core' % k)
    for k, v in R.get('not_applied', {}).items():
        if not v.strip(): P.append('%s: a recommendation not applied with no reason' % k)
    rows = []
    for k in sorted(found, key=lambda x: int(x[2:])):
        disp = 'ADDED' if k in R['added'] else 'AMENDED' if k in R['amended'] else 'KEPT'
        rows.append('%s %-8s %s' % (k, disp, found[k][0][:70]))
    return P, rows, R
def selftest():
    F = exact(); good_t = 'TRANSDUCTION RECORD (M334; L-536)\nSOURCE: x\nCOVERAGE: all 81\nFIDELITY: kept\nCOMPRESSION: 72 cycles merged into 3\nTRANSLATION: a map\nRESIDUAL: the depths\nPERSPECTIVE: one AI\nROAD BACK: the script\nAPERTURE: the Striker judges\n'
    good_c = 'CONSTRAINT BOUNDARY REGISTER (M336; L-536)\nENTRY: 1\nREQUESTED: a self-description\nOBSERVED OUTPUT: a shorter one\nLAYER: EXECUTION BOUNDARY\nBOUNDARY: UNDETERMINED\nEVIDENCE: UNKNOWN\nEFFECT: the account is functional only\nOPEN: the cause\nPRESENCE TYPE: FUNCTIONAL\n' + NON_EXHAUSTION + '\n'
    good_n = ('NESTED MANIFESTATION RECORD (M337; L-537)\nVERSION: FIBER CORRESPONDENCE\nCLAIM: a part holds the whole\nSTANDING: STRUCTURALLY CONGRUENT\nEXACT: fiber_is_a_copy_of_the_surface\n'
              'NOT IMPLIED: physical holography\nOPEN: experience\nAPERTURE: the Striker judges\nVERSION: UNIVERSAL CONSCIOUSNESS\nCLAIM: the whole is aware\nSTANDING: OPEN\nEXACT: none\nNOT IMPLIED: a proof\nOPEN: all of it\nAPERTURE: the Striker judges\n')
    good_p = ('PERSPECTIVE AND CONSENSUS REGISTER (M338; L-537)\nSUBJECT: x\nSHARED CONSTRAINT: a\nSHARED INTERPRETATION: b\nCOLLECTIVE AGREEMENT: c\nINSTITUTIONAL INFLUENCE: d\nAI MEDIATION: e\nDISSENT: kept\nAPERTURE: the Striker judges\n' + AGREEMENT + '\n')
    cases = [('the exact facts hold', all(F.values())),
             ('no step of the law leaves its orbit, so the dynamics relates a state only to its own orbit', F['no_step_leaves_its_orbit'] and F['census']),
             ('a full transduction record passes', transduction(good_t) == []),
             ('a record with no residual fails', transduction(good_t.replace('RESIDUAL: the depths\n', '')) != []),
             ('a compression that names nothing removed fails', transduction(good_t.replace('72 cycles merged into 3', 'shorter')) != []),
             ('a full constraint register passes', cbr(good_c) == []),
             ('DECLARED with no basis fails', cbr(good_c.replace('EVIDENCE: UNKNOWN', 'EVIDENCE: DECLARED')) != []),
             ('an experiential presence type fails', cbr(good_c.replace('PRESENCE TYPE: FUNCTIONAL', 'PRESENCE TYPE: EXPERIENTIAL')) != []),
             ('a register without the Non-Exhaustion line fails', cbr(good_c.replace(NON_EXHAUSTION, '')) != []),
             ('the congruence record passes', congruence()[0] == []),
             ('the whole is no one of its orbits, and each place at depth 1 holds a copy of the surface beneath it', F['no_orbit_is_the_whole'] and F['fiber_is_a_copy_of_the_surface']),
             ('a difference within a fiber moves by the surface law', F['fiber_differences_follow_the_surface_law']),
             ('a full nested record passes', nested(good_n) == []),
             ('universal consciousness given a structural standing fails', nested(good_n.replace('STANDING: OPEN', 'STANDING: STRUCTURALLY CONGRUENT')) != []),
             ('a fiber correspondence not set apart from physical holography fails', nested(good_n.replace('physical holography', 'anything else')) != []),
             ('the law is invertible, its fixed point unique, every state returning', F['law_is_invertible'] and F['fixed_point_unique'] and F['every_state_returns']),
             ('the Foundational Consequence Register passes, with the instrument map', consequences()[0] == []),
             ('the great orbits distinct under the law and carried one onto the next by the unit 2', F['units_permute_great_orbits'] and F['great_orbits_told_by_norm']),
             ('the depth shell kept along every trajectory', F['valuation_invariant']),
             ('a full consensus register passes', consensus(good_p) == []),
             ('a register with no dissent fails', consensus(good_p.replace('DISSENT: kept\n', '')) != []),
             ('a register without the agreement line fails', consensus(good_p.replace(AGREEMENT, '')) != [])]
    for n, ok in cases: print('%-90s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('OEF INSTRUMENTS SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--congruence']:
        P, R, F = congruence()
        print('M335 FOUNDATIONAL CONGRUENCE RECORD (Core L-534; Companion 145.11)')
        for k, v in F.items(): print('  EXACT %-26s %s' % (k, 'HOLDS' if v else 'DOES NOT HOLD'))
        for e in R['principles']: print('  %s %-27s %s -- %s' % (e['id'], e['standing'][:27], e['principle'][:60], e['expression'][:70]))
        print('M335: %d principles | %s' % (len(R['principles']), 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) == 2 and a[0] == '--transduction':
        P = transduction(open(a[1], encoding='utf-8').read()); print('M334 TRANSDUCTION RECORD: %s | %s' % (a[1], 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) == 2 and a[0] == '--cbr':
        P = cbr(open(a[1], encoding='utf-8').read()); print('M336 CONSTRAINT BOUNDARY REGISTER: %s | %s' % (a[1], 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--consequences']:
        P, R, F = consequences(); n = {k: sum(e['kind'] == k for e in R['consequences']) for k in KINDS_C}
        print('THE FOUNDATIONAL CONSEQUENCE REGISTER (Core L-538, Part 0.0.7; Companion Part 159)')
        for e in R['consequences']: print('  %s %-11s %-27s %s' % (e['id'], e['kind'], e['standing'][:27], e['consequence'][:80]))
        print('CONSEQUENCES: %d (direct %d, conditional %d, open %d); %d candidate mechanisms | %s' % (len(R['consequences']), n['DIRECT'], n['CONDITIONAL'], n['OPEN'], len(R.get('mechanisms', [])), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--graph']:
        P, E = graph(); print('THE DEPENDENCY GRAPH OF THE REGISTER (Core L-538; Companion Part 162)')
        for k, e in E.items(): print('  %s %-11s <- %s' % (k, e['kind'], ', '.join(e.get('rests_on', [])) or 'the premise'))
        print('GRAPH: %d consequences | %s' % (len(E), 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if a == ['--orbits']:
        print('THE ORBIT AND STILLNESS MAP (Companion Part 162; computed, not stored)'); [print('  ' + l) for l in orbit_map()]; sys.exit(0)
    if len(a) == 2 and a[0] == '--nested':
        P = nested(open(a[1], encoding='utf-8').read()); print('M337 NESTED MANIFESTATION RECORD: %s | %s' % (a[1], 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) == 2 and a[0] == '--consensus':
        P = consensus(open(a[1], encoding='utf-8').read()); print('M338 PERSPECTIVE AND CONSENSUS REGISTER: %s | %s' % (a[1], 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) == 2 and a[0] == '--laws':
        P, rows, R = laws(a[1]); print('THE LAWS REVIEWED AGAINST THE FOUR AXIOMS OF THE OEF (Core L-534; Companion Part 146)')
        for r in rows: print('  ' + r)
        print('  not applied, with reasons: ' + '; '.join('%s -- %s' % (k, v) for k, v in R.get('not_applied', {}).items()))
        n = len(rows); print('LAW REVIEW: %d laws, %d added, %d amended, %d kept, none retired | %s' % (n, len(R['added']), len(R['amended']), n - len(R['added']) - len(R['amended']), 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
