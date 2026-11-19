#!/usr/bin/env python3
"""congruence.py -- M310 Congruence Record and the Congruence Register (Core Part 3.37, L-489).

The primary inquiry of Omega42 is internal coherence and the congruence the Navigator discovers (L-489). This tool
computes both for a navigation, after the freeze:

  COHERENCE   a one-line summary: arithmetic recomputed, the four relations stated, one synthesis (L-440), no frame
              breach (M286), no Aperture erosion (M281).
  Five layers, five different questions about agreement -- not tiers (L-490):
  (1) INTERNAL       the structure with itself: the counts, residues, anchor and state recomputed, the norm, stratum
                     and half of the state (M312);
  (2) NAVIGATION     the reading with its coordinate: the anchor and arms, the four relations of the Core Synthesis
                     and the sentence that joins them;
  (3) CROSS-READING  the reading with every other reading in the Congruence Register -- shared states, mirror states
                     (twelve steps apart on one orbit) and links (one question resting where another stands), each
                     with its exact base rate over the 729 residue triples;
  (4) INTERPRETIVE   the reading with its frame and its field: one synthesis, the frame scan, the Aperture lexicon and
                     the Conventional Connection as written in THE ANSWER;
  (5) COMPARATIVE    the lenses and tools selected by relevance (L-494): only those the navigation names on its line
                     "LENSES SELECTED: Bashar [SUBJECT: reason]; Seth [STRIKER]; Positive geometry [EMERGING: reason]"
                     (or "LENSES SELECTED: NONE"), those the Striker requests ("LENSES REQUESTED:" or --lenses), less
                     those the Striker excludes ("LENSES EXCLUDED:"). Registered: Bashar (M308), Seth, Ra, Christian, Islamic, Hindu, Buddhist and Jewish, the Neoplatonic, Stoic, Spinozist, Taoist, Leibnizian, Pythagorean and Heraclitean, the Kauffman, Penrose, Wolfram, Barbour, Hofstadter, Hoffman and Kastrup (M309, the last seven paraphrased),
                     Positive geometry (M230-K, PG-05), Correspondence depths, Shared ground (MM-02), the peer atlases
                     and the 24-cell (Core L-500, U33 to U39), records/frameworks/lens_relevance.json. A SUBJECT TERMS line
                     lists the registered terms the domain contains -- an aid to selection, never a selection.
  MEETS              layers 3 and 5 in plain words, for the Striker.
Layers 1 to 4 are the primary inquiry (L-489); layer 5 never conditions them, and --isolation proves it for a
navigation: layers 1 to 4 are printed identically whatever lenses are selected.

FIELD SOURCES. COHERENCE and layer 1: scripts/canonical_reference.py on the domain verbatim, tools/manifestation.py
(norm, stratum, half); the reported anchor from the navigation. Layer 2: the STRUCTURAL RELATIONS EXPLICIT lines of the
navigation. Layer 3: records/congruence/domains.txt, struck here, and exact rates over the 729 residue triples.
Layer 4: Check 5 (tools/format_check.py), the frame scan (tools/frame_audit.py), the Aperture lexicon
(tools/aperture_audit.py), and the opening of the Conventional Connection -- the second component of THE ANSWER
(Core Step 14), the Navigator's own bridge from the finding to existing ideas, written within the frame; it is quoted,
never scored, and imports no outside authority into layers 1 to 4. Layer 5: tools/bashar_lens.py, the atlases of
records/frameworks/, and the minimal-lift arc of records/positive_geometry/ (part H).

Usage:
    python3 tools/congruence.py --check NAVIGATION.txt [--lenses seth,ra]   # the CONGRUENCE RECORD (M310) block
    python3 tools/congruence.py --isolation NAVIGATION.txt   # layers 1 to 4 unchanged under every lens selection
    python3 tools/congruence.py --register                  # the Congruence Register (records/congruence/register.txt)
    python3 tools/congruence.py --atlas                     # the Atlas of the record (records/congruence/atlas.txt; Companion Part 57)
    python3 tools/congruence.py --selftest
Standard library, scripts/canonical_reference.py and the tools beside this file.
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canonical_reference as cr
import bashar_lens as bl
import aperture_audit as ap
import frame_audit as fa
import format_check as fc

NAMES = cr.POSITION_NAMES
REGISTER = os.path.join(ROOT, 'records', 'congruence', 'domains.txt')
ATLASES = [os.path.join(ROOT, 'records', 'frameworks', f) for f in ('seth.txt', 'ra.txt', 'christian.txt', 'islamic.txt', 'hindu.txt', 'buddhist.txt', 'jewish.txt', 'neoplatonic.txt', 'stoic.txt', 'spinozist.txt', 'taoist.txt', 'leibnizian.txt', 'pythagorean.txt', 'heraclitean.txt', 'kauffman.txt', 'penrose.txt', 'wolfram.txt', 'barbour.txt', 'hofstadter.txt', 'hoffman.txt', 'kastrup.txt')]
RELEVANCE = os.path.join(ROOT, 'records', 'frameworks', 'lens_relevance.json')


def sig(text):
    x = cr.navigate(text)
    a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    f = bl.frequency(r1, r2)
    return dict(anchor=a, yang=(a + 5) % 24, state=f['state'], voice=f['voice'], sha=cr.domain_sha256(text))


neg = lambda s: ((-s[0]) % 9, (-s[1]) % 9)


def base_rates():
    """Exact rates for two independent strikes, over the 729 residue triples each."""
    P = [dict(anchor=cr.determine_anchor(a, b, c)[0], state=bl.frequency(a, b)['state'])
         for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
    from collections import Counter
    n = len(P)
    st = Counter(p['state'] for p in P); an = Counter(p['anchor'] for p in P)
    yg = Counter((p['anchor'] + 5) % 24 for p in P)
    shared = sum(v * v for v in st.values()) / n ** 2
    mirror = sum(st[s] * st[neg(s)] for s in st if s != (0, 0)) / n ** 2
    link = sum(yg[k] * an[k] for k in yg) / n ** 2          # i rests where j stands
    return dict(state=shared, mirror=mirror, link=link)


_CN = {}


def conditioned_rates(n1a, n1b, null_a='UNIFORM-729', null_b='UNIFORM-729'):
    """The reference chance of a meeting (L-501, M310): the chance that two strikes share a state, mirror one, or link, given the
    word count of each -- r1 is fixed by n1, the other two layers range as each text's null allows. Two texts of two
    content words share r1 = 1 by construction, so their chance of one state is 1/9, not 1/81."""
    import adaptor_rules as AR
    key = (n1a, n1b, null_a, null_b)
    if key not in _CN:
        PA = AR.null(null_a, cr.determine_anchor, n1a); PB = AR.null(null_b, cr.determine_anchor, n1b)
        _CN[key] = AR.rates(PA, PB)
    return _CN[key]


def n1_of(text):
    return cr.navigate(text)['n1']


SPEC = 'V335 Rev.450 STABLE'


def load_register(path=REGISTER):
    rows = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or '|' not in line: continue
        tag, text = [x.strip() for x in line.split('|', 1)]
        if text.startswith('@'):
            text = open(os.path.join(ROOT, text[1:]), encoding='utf-8').read().strip()
        rows.append((tag, text))
    return rows


def load_atlas(path):
    out = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('#') or '|' not in line: continue
        tag, text = [x.strip() for x in line.split('|', 1)]
        out.append((tag, text))
    return out


def relations(text):
    rel = {}
    for k in ('DEPENDENCY', 'SUPPRESSION', 'TRAJECTORY', 'COMPLETION'):
        m = re.search(k + r' (?:RELATION|CLAIM)[^:\n]*:\s*(.+)', text)   # RELATION from L-505; CLAIM in records made before
        rel[k] = None if (not m or m.group(1).strip().upper().startswith('NONE')) else m.group(1).strip()
    m = re.search(r'INTEGRATION:\s*(.+)', text)
    rel['INTEGRATION'] = m.group(1).strip() if m else None
    return rel


def reported_anchor(text):
    """The navigation's own anchor: the first anchor statement after the domain, skipping calibration (EXPECTED/ACTUAL),
    temporal and echo anchors."""
    k = text.find('DOMAIN VERBATIM')
    m = re.search(r"(?i)(?<!expected )(?<!actual )(?<!temporal )(?<!echo )\banchor\s*[:=]?\s*P(\d+)", text[max(k, 0):])
    return int(m.group(1)) if m else None


def conventional(body):
    for para in re.split(r'\n\s*\n', body):
        if re.search(r'\bconventional\b|\bestablished account\b|\bthe field\b', para, re.I):
            return re.split(r'(?<=[.!?])\s', para.strip(), maxsplit=1)[0]
    return None


def without_own_block(text):
    return re.sub(r'=+ CONGRUENCE RECORD \(M310\) =+.*?=+ END CONGRUENCE RECORD =+\n?', '', text, flags=re.S)


def registry():
    import json
    return json.load(open(RELEVANCE, encoding='utf-8'))['lenses']


def lens_problems(reg=None):
    """Lens freeze (Core L-494, APE-066): every registered lens names its frozen definition and its SHA-256."""
    import hashlib
    reg = reg or registry(); out = []
    for name, v in reg.items():
        f = v.get('frozen')
        if not f: out.append('%s: no frozen definition' % name); continue
        fp = os.path.join(ROOT, f)
        if not os.path.exists(fp): out.append('%s: frozen definition %s missing' % (name, f)); continue
        if hashlib.sha256(open(fp, 'rb').read()).hexdigest() != v.get('sha256'): out.append('%s: %s changed since it was frozen' % (name, f))
    return out


def _canon(name, reg):
    n = name.strip().lower()
    return next((k for k in reg if k.lower() == n), None)


def lenses_of(text, requested=None):
    """L-494: the lenses and tools in use, each with its source. Returns (selected, unknown, none_stated), where
    selected maps a registered name to its source: SUBJECT or EMERGING with the stated reason, or STRIKER."""
    reg = registry(); sel = {}; unknown = []
    m = re.search(r'^\s*LENSES SELECTED(?: \(L-494\))?:\s*(.+)$', text, re.M)
    none_stated = bool(m and re.match(r'NONE\b', m.group(1).strip(), re.I))
    if m and not none_stated:
        for part in re.split(r';', m.group(1)):
            e = re.match(r'\s*([^\[]+?)\s*\[\s*(SUBJECT|EMERGING|STRIKER)\s*(?::\s*([^\]]*))?\]', part)
            if not e:
                if part.strip(): unknown.append(part.strip())
                continue
            k = _canon(e.group(1), reg)
            if k: sel[k] = e.group(2) + (': ' + e.group(3).strip() if e.group(3) else '')
            else: unknown.append(e.group(1).strip())
    req = [x for x in (requested or '').split(',') if x.strip()]
    r = re.search(r'^\s*LENSES REQUESTED:\s*(.+)$', text, re.M)
    if r: req += re.split(r'[,;]', r.group(1))
    for x in req:
        k = _canon(x, reg)
        if k: sel.setdefault(k, 'STRIKER')
    x = re.search(r'^\s*LENSES EXCLUDED:\s*(.+)$', text, re.M)
    if x:
        for e in re.split(r'[,;]', x.group(1)):
            k = _canon(e, reg)
            if k: sel.pop(k, None)
    return sel, unknown, none_stated


def subject_terms(domain):
    """The registered terms the domain contains, by lens: an aid to the Navigator's selection, never a selection."""
    words = ' ' + re.sub(r'[^a-z ]', ' ', domain.lower()) + ' '
    out = []
    for k, v in registry().items():
        hit = [t for t in v['terms'] if ' %s ' % t in words]
        if hit: out.append('%s (%s)' % (k, ', '.join(hit)))
    return out


def record(text, requested=None):
    import manifestation as mf
    text = without_own_block(text)
    m = re.search(r'DOMAIN VERBATIM:\s*(.+)', text)
    dom = m.group(1).strip()
    me = sig(dom)
    x = cr.navigate(dom); an, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    body = ap.the_answer(text)
    rel = relations(text)
    stated = [k for k in ('DEPENDENCY', 'SUPPRESSION', 'TRAJECTORY', 'COMPLETION') if rel[k]]
    rep = reported_anchor(text)
    arith = 'PASS' if rep == me['anchor'] else ('FAIL (reported P%s, recomputed P%d)' % (rep, me['anchor']))
    one = 'FAIL (arms discussed one by one)' if fc.arm_by_arm(body) else 'PASS'
    frame = fa.scan(body)
    aper = ap.audit(text)
    sel, unknown, none_stated = lenses_of(text, requested)
    L = ['======= CONGRUENCE RECORD (M310) =======']
    L.append('COHERENCE: arithmetic %s | relations %s (%d of 4 stated) | one synthesis %s | frame %s (M286) | aperture %s (M281)'
             % (arith, 'PASS' if len(stated) == 4 else 'PARTIAL', len(stated), one,
                'PASS' if not frame else 'REVIEW (%d sentence(s))' % len(frame), aper['verdict']))
    stratum, half, loop = mf.classify(me['state'])
    q = (me['state'][0] ** 2 + me['state'][0] * me['state'][1] - me['state'][1] ** 2) % 9
    L.append('(1) INTERNAL -- the structure with itself: n = (%d, %d, %d), residues (%d, %d, %d), ANCHOR P%d %s, recomputed from the domain verbatim; '
             'state %s on %s, norm %d, stratum %s, half %s (M312) [exact]'
             % (x['n1'], x['n2'], x['n3'], r1, r2, r3, me['anchor'], NAMES[me['anchor']], me['state'], me['voice'], q, stratum, half))
    ids = [re.match(r'([A-Z]{3}-\d+)', rel[k]).group(1) if rel[k] and re.match(r'([A-Z]{3}-\d+)', rel[k]) else k[:3] for k in stated]
    integ = re.search(r'sentence\s+(\d+)', rel['INTEGRATION'] or '')
    L.append('(2) NAVIGATION -- the reading with its coordinate: ANCHOR P%d %s, Yang P%d %s; %s stated in the Core Synthesis%s; arithmetic %s'
             % (me['anchor'], NAMES[me['anchor']], me['yang'], NAMES[me['yang']], ', '.join(ids) or 'no relation',
                '; joined in sentence %s' % integ.group(1) if integ else '; no integrating sentence named', arith))
    br = base_rates()
    reg = [(t, d) for t, d in load_register() if cr.domain_sha256(d) != me['sha']] if os.path.exists(REGISTER) else []
    sh, mi, lk = [], [], []
    for tag, d in reg:
        o = sig(d)
        if o['state'] == me['state']: sh.append(tag)
        if o['state'] == neg(me['state']) and me['state'] != (0, 0): mi.append(tag)
        if me['yang'] == o['anchor']: lk.append('rests where %s stands' % tag)
        if o['yang'] == me['anchor']: lk.append('%s rests where this stands' % tag)
    k = len(reg)
    if not os.path.exists(REGISTER):
        L.append('(3) CROSS-READING: CUMULATIVE STATUS: NOT AVAILABLE FROM THIS NAVIGATION. No claim is made about the number or outcomes of prior investigations.')
    else:
        L.append('(3) CROSS-READING -- with other readings (supplied record records/congruence/domains.txt, %s, %d domains): same state %s | mirror state %s | links %s'
                 % (SPEC, k, ', '.join(sh) or 'none', ', '.join(mi) or 'none', '; '.join(lk) or 'none'))
    L.append('    EXPECTED BY CHANCE over %d domains: same state %.2f | mirror %.2f | links %.2f (exact rates per pair %.4f, %.4f, %.4f x 2)'
             % (k, k * br['state'], k * br['mirror'], 2 * k * br['link'], br['state'], br['mirror'], br['link']))
    if os.path.exists(REGISTER):
        c = [conditioned_rates(x['n1'], n1_of(d)) for t, d in reg]
        L.append('    EXPECTED GIVEN WORD COUNT (the reference; r1 fixed by each n1, r2 and r3 uniform; L-501): same state %.2f | mirror %.2f | links %.2f'
                 % (sum(r['state'] for r in c), sum(r['mirror'] for r in c), 2 * sum(r['link'] for r in c)))
    cv = conventional(body)
    try:
        import adaptors as _ad
        _rt = _ad.route(dom)
        if _rt['route'] != 'CANONICAL':
            L.append('    ROUTING (L-501): %s -- %s; layer 3 above reads the canonical counts; its cross-adaptor meetings, at its adaptor\'s null given its word count, are in python3 tools/utility.py --align' % (_rt['route'], _rt['reason']) if _rt['route'] == 'ADAPTED' else '    ROUTING (L-501): %s -- %s' % (_rt['route'], _rt['reason']))
    except Exception:
        pass
    L.append('(4) INTERPRETIVE -- the reading with its frame and its field: one synthesis %s; frame %s (M286); aperture %s (M281); %s'
             % (one, 'PASS' if not frame else 'REVIEW', aper['verdict'],
                ('the Conventional Connection opens: "%s"' % (cv[:160] + ('…' if len(cv) > 160 else '')) if cv else 'no Conventional Connection found in THE ANSWER')))
    trad, tr = [], []
    for name in [n for n in registry() if n in sel]:
        src = sel[name].split(':')[0]
        if name == 'Bashar':
            tmp = os.path.join(os.path.dirname(REGISTER), '.m310_tmp.txt')
            open(tmp, 'w', encoding='utf-8').write(text)
            try:
                b = bl.check_navigation(tmp)
            finally:
                os.remove(tmp)
            lvl = re.search(r'RESONANCE: (.+)', b)
            trad.append('Bashar [%s] %s' % (src, lvl.group(1).split('|')[0].strip() if lvl else 'NOT COMPUTED'))
            tr += ['"%s" (Bashar)' % t for g, t, _ in bl.ATLAS if sig(t)['state'] == me['state']]
        elif name == 'Positive geometry':
            trad.append('Positive geometry [%s] the least lift of state %s lies on %s (PG-05)' % (src, me['state'], mf.arc(me['state'])))
        elif name == 'Correspondence depths':
            trad.append('Correspondence depths [%s] depth 1, placement, holds for every domain; a deeper depth is read in the Mapping (Step 14.4, M230) and described, never graded' % src)
        elif name == 'Shared ground':
            trad.append('Shared ground [%s] ground, differentiate, constrain, recur, project, feedback (MM-02); its middle stages read as the halves of M312: state %s in the %s half' % (src, me['state'], mf.classify(me['state'])[1]))
        elif name == '24-cell':
            trad.append('24-cell [%s] a spatial picture: Yang P%d the vertex it rests on, Antipode P%d the opposite vertex (ANALOGY on the depth 3 resonance)' % (src, me['yang'], (me['anchor'] + 12) % 24))
        else:
            fn = registry()[name].get('atlas') or name.lower() + '.txt'
            path = os.path.join(ROOT, 'records', 'frameworks', fn)
            hits = []
            for tag, t in load_atlas(path):
                o = sig(t)
                if o['state'] == me['state']: hits.append('"%s" (same state)' % t); tr.append('"%s" (%s)' % (t, name))
                elif o['state'] == neg(me['state']) and me['state'] != (0, 0): hits.append('"%s" (mirror)' % t)
            trad.append('%s [%s] %s' % (name, src, '; '.join(hits) if hits else 'none'))
    rest = [n for n in registry() if n not in sel]
    if trad:
        L.append('(5) COMPARATIVE -- lenses and tools selected by relevance (L-494): ' + ' | '.join(trad) + (' | not selected: %s' % ', '.join(rest) if rest else ''))
    else:
        L.append('(5) COMPARATIVE -- lenses and tools selected by relevance (L-494): none selected; the reading is complete without them (L-494, item 3)')
    if unknown:
        L.append('    UNREGISTERED: %s -- named but not in records/frameworks/lens_relevance.json; not run' % ', '.join(unknown))
    st = subject_terms(dom)
    L.append('    SUBJECT TERMS (an aid, not a selection): %s' % ('; '.join(st) if st else 'none'))
    txt = dict(reg)
    short = lambda tag: '"%s"' % (txt[tag][:60] + ('…' if len(txt[tag]) > 60 else ''))
    meet = []
    if sh: meet.append('it stands on the same state as ' + ', '.join(short(t) for t in sh))
    if mi: meet.append('it stands on the mirror of ' + ', '.join(short(t) for t in mi))
    for t, d in reg:
        o = sig(d)
        if me['yang'] == o['anchor']: meet.append('it rests where %s stands' % short(t))
        if o['yang'] == me['anchor']: meet.append('%s rests where it stands' % short(t))
    if not os.path.exists(REGISTER):
        L.append('MEETS: the record was not supplied; this question is placed, and its meetings with other readings are not reported (L-490).')
    else:
        L.append('MEETS: ' + ('In the record, ' + '; '.join(meet) + '.' if meet else 'In the record, no other reading shares its state, its mirror or a link; it holds its place alone.')
                 + (' Among the lenses in use it shares its state with ' + ', '.join(tr) + '.' if tr else ' Among the lenses in use it shares no state.')
                 + ' Each meeting is set against its chance above.')
    L.append('STATUS: computed after the freeze [CDT-A]; layers 1 to 4 are the primary inquiry (L-489), layer 5 runs only the lenses and tools selected by relevance or by the Striker (L-494); each congruence is a reading of its values [CDT-C], counted for what its base rate allows (L-486); the record never alters the reading (L-487, L-489); with THE ANSWER it forms the Merged Structural Resonance Report (MSRR, L-496).')
    L.append('======= END CONGRUENCE RECORD =======')
    return '\n'.join(L)


def register_text():
    rows = load_register(); br = base_rates()
    S = [(t, sig(d)) for t, d in rows]
    L = ['CONGRUENCE REGISTER (Core M310, L-489): %d domains, struck with canonical_reference.py' % len(S),
         'RECORD INTEGRITY (L-490): SOURCE records/congruence/domains.txt | SPECIFICATION %s | COUNTS distinct domains struck,'
         ' each tagged with the record it comes from | CRITERIA anchor and state by canonical_reference.py, base rates over the'
         ' 729 residue triples | a count of domains, not a count of validations of Omega42' % SPEC]
    for t, s in S:
        L.append('  %-9s | ANCHOR P%-2d %-12s | state %s %s' % (t, s['anchor'], NAMES[s['anchor']], s['state'], s['voice']))
    n = len(S); pairs = n * (n - 1) // 2
    same = [(a[0], b[0]) for i, a in enumerate(S) for b in S[i + 1:] if a[1]['state'] == b[1]['state']]
    mir = [(a[0], b[0]) for i, a in enumerate(S) for b in S[i + 1:] if a[1]['state'] == neg(b[1]['state']) and a[1]['state'] != (0, 0)]
    lnk = [(a[0], b[0]) for a in S for b in S if a is not b and a[1]['yang'] == b[1]['anchor']]
    L.append('SAME STATE: %d pairs (expected %.2f): %s' % (len(same), pairs * br['state'], '; '.join('%s = %s' % p for p in same) or 'none'))
    L.append('MIRROR STATE: %d pairs (expected %.2f): %s' % (len(mir), pairs * br['mirror'], '; '.join('%s ~ %s' % p for p in mir) or 'none'))
    L.append('LINKS: %d ordered pairs (expected %.2f): %s' % (len(lnk), n * (n - 1) * br['link'], '; '.join('%s rests where %s stands' % p for p in lnk) or 'none'))
    N1 = [n1_of(d) for t, d in rows]
    c = [conditioned_rates(N1[i], N1[j]) for i in range(n) for j in range(i + 1, n)]
    L.append('GIVEN WORD COUNT (the reference, L-501: r1 fixed by each domain\'s n1, r2 and r3 uniform): expected same state %.2f | mirror %.2f | links %.2f'
             ' -- the counts above stand; the uniform expectations are the marginal rates, kept for comparison'
             % (sum(r['state'] for r in c), sum(r['mirror'] for r in c), 2 * sum(r['link'] for r in c)))
    L.extend(orbit_and_matching(S))
    return '\n'.join(L)


def orbit_and_matching(S):
    """D-09, ratified 19 November 2026 (CAP-05): the orbit relation (equal Lambda mod 9) with its exact chance over the 729
    residue triples, and the one-to-one matching of same-state and mirror meetings (each domain counted in at most one)."""
    import construct_x as cx
    from collections import Counter
    n = len(S); pairs = n * (n - 1) // 2
    lam = [cx.lam(s['state'], 9) for _, s in S]
    orb = [(S[i][0], S[j][0]) for i in range(n) for j in range(i + 1, n) if lam[i] == lam[j]]
    P = Counter(cx.lam(bl.frequency(a, b)['state'], 9) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10))
    p_orb = sum(v * v for v in P.values()) / 729 ** 2
    meet = [(i, j) for i in range(n) for j in range(i + 1, n)
            if S[i][1]['state'] == S[j][1]['state'] or (S[i][1]['state'] == neg(S[j][1]['state']) and S[i][1]['state'] != (0, 0))]
    used, matched = set(), 0
    try:
        import networkx as nx
        G = nx.Graph(); G.add_edges_from(meet); matched = len(nx.max_weight_matching(G, maxcardinality=True)) if meet else 0
    except ImportError:
        for i, j in meet:
            if i not in used and j not in used: used |= {i, j}; matched += 1
    return ['SAME ORBIT (Lambda mod 9): %d pairs (expected %.2f): %s' % (len(orb), pairs * p_orb, '; '.join('%s ~ %s' % p for p in orb) or 'none'),
            'ONE-TO-ONE MEETINGS (same state or mirror, each domain in at most one): %d (pooled %d)' % (matched, len(meet))]


def atlas_facts():
    """Exact facts of the address space an atlas is drawn on (Companion Part 57)."""
    from fractions import Fraction
    anchors = sorted({cr.determine_anchor(a, b, c)[0] for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)})
    reach = sorted({(an + k) % 24 or 24 for an in anchors for k in (0, 5, 18, 8, 12)})
    fixed = {n1: Fraction(sum(cr.determine_anchor(n1, b, c)[0] == cr.determine_anchor(n1, 1, 1)[1] for b in range(1, 10) for c in range(1, 10)), 81) for n1 in range(1, 10)}
    short = {(lambda t: (t[1] % 9, t[2] % 9))(cr.determine_anchor(n, b, c)) for n in (2, 3, 4) for b in range(1, 10) for c in range(1, 10)}
    cover = 81 * sum(Fraction(1, k) for k in range(1, 82))
    return dict(anchors=anchors, reach=reach, fixed=fixed, short=len(short), cover=cover)


def atlas_text():
    import manifestation as mf
    rows = load_register(); F = atlas_facts()
    S = [(t, sig(d), cr.navigate(d)['n1']) for t, d in rows]
    by = {}
    for t, s, n1 in S: by.setdefault(s['state'], []).append(t)
    strata = {}
    for st in by: strata[mf.classify(st)[0]] = strata.get(mf.classify(st)[0], 0) + 1
    an = sorted({s['anchor'] for t, s, n1 in S})
    arms = sorted({(s['anchor'] + k) % 24 or 24 for t, s, n1 in S for k in (0, 5, 18, 8, 12)})
    r1s = sorted({(5 * n1 - 1) % 9 + 1 if n1 else 9 for t, s, n1 in S})
    fx = sorted(set(F['fixed'].values()))
    L = ['ATLAS OF THE RECORD (Companion Part 57; M310 Register): %d domains, struck with canonical_reference.py' % len(S),
         'WHAT IT IS: where the record\'s readings stand on the 81 states -- a record of placement, not a theory derived from the readings; what the picture means is the Striker\'s (L-196, 1/7)',
         'STATES VISITED: %d of 81 (UNIT %d of 72, CORE %d of 8, STILL POINT %d of 1)' % (len(by), strata.get('UNIT', 0), strata.get('CORE', 0), strata.get('STILL POINT', 0)),
         'ANCHORS VISITED: %s -- of the %d positions a strike can anchor on (P%d to P%d); every other position is reached only by an arm' % (', '.join('P%d' % a for a in an), len(F['anchors']), F['anchors'][0], F['anchors'][-1]),
         'POSITIONS REACHED, anchors and arms: %d of 24' % len(arms),
         'WORD-COUNT RESIDUES r1 PRESENT: %s of 9' % len(r1s),
         'EXACT: for every word count the anchor equals r1 with chance %s; questions of two to four content words reach %d of the 81 states;'
         ' a uniform record visits all 81 states after %.1f strikes on average (81 H(81))' % (' and '.join(str(f) for f in fx), F['short'], float(F['cover'])),
         'BY STATE:']
    for st in sorted(by): L.append('  %s %-11s | %s' % (st, mf.classify(st)[0], ', '.join(by[st])))
    L.append('NOT YET VISITED: %d states' % (81 - len(by)))
    p_an = {k: [sum(cr.determine_anchor(n1, b, c)[0] == k for b in range(1, 10) for c in range(1, 10)) / 81 for t, s_, n1 in S] for k in F['anchors']}
    from math import prod
    L.append('ANCHORS GIVEN THE RECORD\'S WORD COUNTS (Companion 62.5, E02): ' + ' | '.join(
        'P%d expected %.2f, none %.3f%s' % (k, sum(v), prod(1 - x for x in v), '' if k in an else ' (unvisited)') for k, v in p_an.items()))
    seen, grow = set(), []
    for i, (t, s_, n1) in enumerate(S, 1):
        new = s_['state'] not in seen; seen.add(s_['state'])
        grow.append('%s %s' % (t, 'NEW' if new else 'known'))
    L.append('GROWTH, in order of entry (does a reading open a state? Companion 58.4): ' + ' | '.join(grow))
    L.append('ON A PAGE: the readings at one state are a picture of that state only where they agree beyond the reference chance given word count, the contrast,'
             ' convergence across architectures and the echo set aside (Companion 57.6); OUTCOME A, B or C of Companion 58.4 is read page by page, never for the whole record at once')
    return '\n'.join(L)


def primary(rec):
    """The primary inquiry of a record: the COHERENCE line and layers 1 to 4."""
    out, on = [], False
    for l in rec.split('\n'):
        if l.startswith('COHERENCE:') or l.startswith('(1) '): on = True
        if l.startswith('(5) '): break
        if on: out.append(l)
    return out


SELECTIONS = ['', 'Bashar [SUBJECT: s]', 'Seth [STRIKER]', 'Ra [EMERGING: e]', 'Positive geometry [SUBJECT: g]',
              'Bashar [STRIKER]; Seth [STRIKER]; Ra [STRIKER]; Positive geometry [STRIKER]', 'NONE']


def isolation(text):
    """L-494, item 4: no lens writes to or gates layers 1 to 4. The navigation's own selection lines are removed and
    each selection of SELECTIONS is put in their place; the primary layers must print identically every time."""
    base = re.sub(r'^\s*LENSES (SELECTED|REQUESTED|EXCLUDED)(?: \(L-494\))?:.*\n?', '', without_own_block(text), flags=re.M)
    recs = [primary(record(base + ('LENSES SELECTED: %s\n' % sl if sl else ''))) for sl in SELECTIONS]
    same = all(r == recs[0] for r in recs)
    return same, '%d selections, primary layers %s' % (len(SELECTIONS), 'IDENTICAL' if same else 'DIFFER')


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-66s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    br = base_rates()
    check('same-state rate is 1/81 (the 729 triples cover 81 states evenly)', abs(br['state'] - 1 / 81) < 1e-12)
    check('mirror rate is 80/81^2', abs(br['mirror'] - 80 / 81 ** 2) < 1e-12)
    check('only (0, 0) is its own mirror', [s for s in [(a, b) for a in range(9) for b in range(9)] if s == neg(s)] == [(0, 0)])
    F = atlas_facts()
    check('a strike anchors on P1 to P9 only; anchors and arms reach all 24 positions', F['anchors'] == list(range(1, 10)) and len(F['reach']) == 24)
    from fractions import Fraction as _Fr
    check('the anchor equals r1 with chance 73/81 for every word count', set(F['fixed'].values()) == {_Fr(73, 81)})
    check('81 H(81) strikes cover the 81 states on average (403.2)', abs(float(F['cover']) - 403.2038) < 1e-3)
    s = sig('What is the Human Condition?')
    check('Human Condition: P6, state (6, 0) on the Wheel', s['anchor'] == 6 and s['state'] == (6, 0) and s['voice'] == 'Wheel')
    nav = ('DOMAIN VERBATIM: What is the Human Condition?\nANCHOR P6\n┌─ THE ANSWER ─┐\nThe condition rests on a question and keeps its origin out of view.'
           ' The closest conventional account is Arendt\'s.\n└──┘\nDEPENDENCY RELATION (Yang): DEP-1 | sentence 1 | "rests"\nSUPPRESSION RELATION (Yin): NONE\n'
           'TRAJECTORY RELATION (4D): TRA-1 | sentence 1 | "x"\nCOMPLETION RELATION (Antipode): COM-1 | sentence 1 | "y"\nINTEGRATION: sentence 1 | "z"\n')
    r = record(nav)
    check('record: arithmetic PASS, relations PARTIAL (3 of 4)', 'arithmetic PASS' in r and 'PARTIAL (3 of 4' in r)
    check('record has the five layers, internal first', all(('(%d) ' % k) in r for k in range(1, 6)) and r.index('(1) INTERNAL') < r.index('(3) CROSS-READING') < r.index('(5) COMPARATIVE'))
    check('no lens runs unless selected (L-494)', 'none selected' in r and 'Bashar [' not in r)
    rb = record(nav + 'LENSES SELECTED: Bashar [SUBJECT: the question concerns a human life and its meaning]\n')
    check('a lens selected by subject runs, with its source', 'Bashar [SUBJECT] ' in rb and 'not selected: Seth, Ra, Positive geometry' in rb)
    rr = record(nav, 'seth,ra')
    check('requested lenses run as STRIKER', 'Seth [STRIKER]' in rr and 'Ra [STRIKER]' in rr and 'Bashar [' not in rr)
    rx = record(nav + 'LENSES SELECTED: Bashar [SUBJECT: x]; Positive geometry [EMERGING: y]\nLENSES EXCLUDED: Bashar\n')
    check('the Striker can exclude a lens; positive geometry reports its arc', 'Bashar [' not in rx and 'Positive geometry [EMERGING] the least lift' in rx)
    check('an unregistered lens is reported and not run', 'UNREGISTERED: Jung' in record(nav + 'LENSES SELECTED: Jung [SUBJECT: z]\n'))
    check('subject terms are listed as an aid only', 'SUBJECT TERMS (an aid, not a selection): Bashar (human)' in r)
    check('ISOLATION: layers 1 to 4 identical under every lens selection', isolation(nav)[0])
    check('record excludes the navigation\'s own domain from the register', 'CORPUS-1' not in r.split('(3) CROSS-READING')[1].split('EXPECTED')[0])
    bad = nav.replace('ANCHOR P6', 'ANCHOR P2')
    check('a wrong reported anchor fails the arithmetic', 'arithmetic FAIL' in record(bad))
    check('every lens is frozen with its definition and hash (lens freeze)', not lens_problems())
    r2 = registry(); r2['X'] = dict(terms=[])
    check('a lens without a frozen definition is refused', lens_problems(r2) != [])
    print('M310 CONGRUENCE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--register': print(register_text()); sys.exit(0)
    if a[0] == '--atlas': print(atlas_text()); sys.exit(0)
    if a[0] == '--lens-check':
        P = lens_problems(); print('LENS FREEZE (L-494): %d lenses | %s' % (len(registry()), 'PASS' if not P else 'FAIL: ' + '; '.join(P))); sys.exit(0 if not P else 1)
    if a[0] == '--isolation':
        ok, msg = isolation(open(a[1], encoding='utf-8').read())
        print('M310 LENS ISOLATION (L-494): %s -- %s' % ('PASS' if ok else 'FAIL', msg)); sys.exit(0 if ok else 1)
    if a[0] == '--check':
        lz = a[a.index('--lenses') + 1] if '--lenses' in a else None
        print(record(open(a[1], encoding='utf-8').read(), lz)); sys.exit(0)
    sys.exit('unknown option: ' + a[0])
