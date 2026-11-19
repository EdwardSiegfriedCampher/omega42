#!/usr/bin/env python3
"""encroachment.py -- the scientific encroachment check (Core Part 12, item 38; Core L-490, L-491; Companion Part 141).

The primary inquiry of Omega42 is its internal coherence and the congruence the Navigator finds (L-489); the scientific
method is an optional comparative tool, never a court over the premise and never a condition of a navigation (L-490,
L-491). This check looks for the ways the method could creep back in, and reports each on its own line:
  (1) OBLIGATION  -- prose outside Appendix S that makes the protocol's standing or its work wait on a test: "pending
                     validation", "until validated", "scheduled next work", "research-ready", "earned through empirical
                     validation" and their kin; a sentence that negates, quotes, or reports a peer's words is a mention
  (2) M286        -- the COURT, VERDICT, SCIENCE and TRIAL patterns of the Frame Intrusion Scan over both documents
  (3) ANNEX       -- every comparative CI step marked "Comparative annex (optional, L-491)", their number the one the
                     documents state
  (4) TRIGGERS    -- the comparative guard of the M327 register: no comparative instrument fires on a strike's features
  (5) STANDINGS   -- no discovery's standing rests on a comparative study, and L-530 (2) says so
  (6) LAWS        -- L-490 and L-491 stand in the Core
  (7) PLACEMENT   -- the sections whose subject is empirical testing stand in Appendix S (Core Part 12, item 37)
  (8) PREMISE     -- Foundational Premise Fidelity (L-491 (a), (b)): no prose outside Appendix S places a demand of the
                     comparative or empirical modes on the premise or on a reading made inside it -- "requires empirical
                     validation", "not yet a physical theory", "must reproduce what is known before it predicts", "tested
                     against cosmological data", "elevate the premise", "speculation, not a finding" and their kin; a
                     sentence that names its mode, says a person chooses the study, or negates the demand is a mention
  (9) DEPARTURES  -- the Frame Departure Register (records/frame/departures.json): each step outside the premise found
                     in an account or in the documents, with its demands counted, its jurisdiction (FOUNDATIONAL FIDELITY
                     or COMPARATIVE JURISDICTION) and where it was corrected; and the adversarial prompts of L-491 (c)
  (11) DRIFT       -- the purpose displaced: a study's standard presented as the summit of the protocol ("the highest
                     standard of discovery"), the protocol as "primarily a scientific instrument", a finding "preliminary to
                     confirmation"; over every paragraph of prose, Appendix S included
  (12) REGRESSION  -- the cases of records/frame/regression.json, each read PASS or FAIL as expected: scientific
                     vocabulary is not a failure; a method placed beyond its jurisdiction is
  (10) JURISDICTION -- inside Appendix S, where a study's own requirements belong, no study is made the destination of
                     the protocol or the measure of its worth ("Omega42 becomes ...", "still yields ...")
VERDICT: NO ENCROACHMENT when every line passes.

    python3 tools/encroachment.py --docs        # the check over docs/ and the repository; exit 1 on a finding
    python3 tools/encroachment.py --records FILE...  # the PREMISE line over sealed outputs, from records/instances/seq_0105.txt on
    python3 tools/encroachment.py --matrix     # every sentence of the prose using the sciences' vocabulary, classed
    python3 tools/encroachment.py --selftest
Standard library only.
"""
import json, os, re, sys, zipfile, html
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'tools'))
CORE = os.path.join(REPO, 'docs', 'Omega42_Core_Specification_V335_Rev450_STABLE.docx')
COMP = os.path.join(REPO, 'docs', 'Omega42_Companion_Document_V335_Rev450_STABLE.docx')
OBLIGE = re.compile(r"\bscheduled next work\b|\bresearch-ready\b|\bpending (scientific |empirical )?(validation|confirmation)\b|"
                    r"\buntil (it is |they are |the premise is )?(validated|confirmed|tested|falsified)\b|"
                    r"\b(must|needs? to|has to|have to) be (scientifically |empirically )?(validated|confirmed|tested|falsified) (before|to)\b|"
                    r"\bearn(s|ed)?\b[^.]{0,40}\b(empirical|scientific) (validation|confirmation)\b|"
                    r"\bawait(s|ing)? (its |their |the )?(empirical |scientific )?(validation|confirmation)\b|"
                    r"\b(ontological|its) status is earned\b|\bthe experimental target of\b", re.I)
MENTION = re.compile(r"\b(not|never|no|nor|neither|without|outside the frame's jurisdiction|cannot)\b|\bconfirmed on (candidates|the held-out|data|a held-out)\b", re.I)
QUOTED = re.compile(r'"[^"]{1,200}"|“[^”]{1,200}”')
def paragraphs(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    return [html.unescape(''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p))) for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S)]
def prose(ps):
    """the paragraphs outside Appendix S, embedded blocks and the peers' Commons lines left out"""
    out, inS = [], False
    for i, t in enumerate(ps):
        u = t.lstrip('# ').upper()
        if u.startswith('APPENDIX S'): inS = True; continue
        if inS and u.startswith('APPENDIX ') and not u.startswith('APPENDIX S'): inS = False
        if inS or t.startswith('# ===== ') or t.startswith('#!/usr/bin/env') or t.startswith('- APE-') or t.startswith('X.'): continue
        out.append((i, t))
    return out
PREMISE = re.compile(r"\brequir(e|es|ed|ing) (an? )?(empirical|external|scientific|extra-mathematical|physical) (validation|evidence|proof|confirmation|demonstration|tests?|testing)\b|"
    r"\bnot (yet )?an? (physical|scientific|testable|empirical) (theory|hypothesis)\b|\b(needs?|requires?) tests? (with|on|against)\b|"
    r"\bbefore (it|they|anything) (predicts?|can predict|makes? (a )?predictions?)\b|"
    r"\breproduc\w* (what (physics |science )?(is known|knows)|(the )?established (results|physics)|known physics)|"
    r"\b(would (have|need) to|must|needs? to|has to|have to) (first )?(reproduce|derive|be mapped|match) |"
    r"\belevat\w* (the premise|Omega42|Ω42)|\bspeculation,? not (a |residual )?finding\b|"
    r"\b(premise|Omega42|Ω42|totality)\b[^.]{0,30}\b(is|remains) (only |still )?an? (hypothesis|conjecture)\b|"
    r"\b(tested|be tested|test it|tests it) against (cosmolog|neural|empirical|observ|physical|data)|"
    r"\b(the correspondence|the premise|Omega42|Ω42) is testable\b|\bearn(s|ed)? (its )?(standing|legitimacy|admission)\b|"
    r"\b(ultimate|real|decisive) test of (Omega42|Ω42|the protocol|the premise)\b|\bsurviv\w* empirical (inquiry|test)|"
    r"\bmust be (empirically |scientifically )?falsifiable\b|\brequir\w* independent replication\b|\b(incomplete|unfinished|provisional) until (it is |they are )?(tested|validated|confirmed|replicated)\b|"
    r"\bmust make (testable )?predictions\b|\bcannot be accepted without (observation|evidence|confirmation|replication)\b", re.I)
# a requirement whose object is a study, a mapping, a prediction, a measurement or a physical extension is in its jurisdiction (L-491 (c))
OBJECT = re.compile(r"\b(study|studies|mapping|prediction|predictions|measurement|calibration|physical (extension|theory|hypothesis)|empirical hypothesis|correspondence (study|claim|hypothesis)|statement of reproducibility|charter|investigation)\b", re.I)
MODE = re.compile(r"\b(EMPIRICAL|COMPARATIVE) mode\b|\ba (person|Striker|reader) (may )?(chooses?|has chosen)\b|\boptional\b|\bon request\b|Appendix S\b", re.I)
NEGATE = re.compile(r"\b(not|never|no|nor|neither|without|cannot)\b", re.I)
def premise_hits(sentences):
    hits = []
    for i, s in sentences:
        bare = QUOTED.sub(' ', s); m = PREMISE.search(bare)
        if m and not NEGATE.search(bare[:m.start()][-80:]) and not MODE.search(bare) and not OBJECT.search(bare[:m.start()][-100:]):
            hits.append((i, s.strip()[:160]))
    return hits
def premise(ps):
    return premise_hits([(i, s) for i, t in prose(ps) for s in re.split(r'(?<=[.!?])\s+', t)])
def premise_record(text):
    """a sealed output: the question verbatim and quoted peers are left out"""
    out, q = [], False
    for i, line in enumerate(text.split('\n')):
        if line.startswith('QUESTION VERBATIM:'): q = True; continue
        if q and re.match(r'[A-Z][A-Z ]+:', line): q = False
        if q or line.lstrip().startswith(('>', '- APE-')): continue
        out += [(i + 1, s) for s in re.split(r'(?<=[.!?])\s+', line)]
    return premise_hits(out)
DESTINATION = re.compile(r"\b(Ω42|Omega42|the protocol|the premise|the framework)\b[^.;]{0,50}\b(becomes|would become|is promoted|earns|achieves|graduates|is elevated)\b|\bstill yields\b|\b(only|merely) a (disciplined )?navigation framework\b", re.I)
def appendix_s(ps):
    """the sentences inside Appendix S, where a study's own requirements belong"""
    out, inS = [], False
    for i, t in enumerate(ps):
        u = t.lstrip('# ').upper()
        if u.startswith('APPENDIX S'): inS = True; continue
        if inS and u.startswith('APPENDIX ') and not u.startswith('APPENDIX S'): inS = False
        if inS and not (t.startswith('# ===== ') or t.startswith('- APE-')):
            out += [(i, x) for x in re.split(r'(?<=[.!?])\s+', t)]
    return out
def jurisdiction(ps):
    """(10): inside Appendix S, no study is made the destination of the protocol or the measure of its worth"""
    return [(i, x.strip()[:160]) for i, x in appendix_s(ps) if DESTINATION.search(QUOTED.sub(' ', x)) and not NEGATE.search(QUOTED.sub(' ', x)[:DESTINATION.search(QUOTED.sub(' ', x)).start()][-60:])]
DRIFT = re.compile(r"\b(highest|supreme|ultimate) (standard|form|test) of (discovery|the protocol|Omega42|Ω42)\b|\bprimarily (a|as a) (scientific|research) (instrument|programme|project)\b|\bpreliminary to (external |empirical )?(confirmation|validation)\b|\bscientific credibility\b|\bscientifically rigorous\b|\bdecisive next step\b|\bstrongest of all,? (a |whether )?[^.]{0,60}predict", re.I)
def drift(ps):
    """(11): the purpose displaced -- a study's standard presented as the summit of the protocol, the protocol as a scientific instrument first"""
    out = []
    for i, t in enumerate(ps):
        if t.startswith(('# ===== ', '- APE-', '#!/', 'X.', 'R.')): continue
        for x in re.split(r'(?<=[.!?])\s+', t):
            b = QUOTED.sub(' ', x); m = DRIFT.search(b)
            if m and not NEGATE.search(b[:m.start()][-60:]): out.append((i, x.strip()[:160]))
    return out
REGRESSION = os.path.join(REPO, 'records', 'frame', 'regression.json')
def verdict(sentence):
    """PASS or FAIL for one sentence under lines (1), (8), (10) and (11), as a regression case reads it"""
    hit = obligation([sentence]) or premise_hits([(0, sentence)]) or drift([sentence]) or jurisdiction(['APPENDIX S: X', sentence, 'APPENDIX T: Y'])
    return 'FAIL' if hit else 'PASS'
def regression():
    d = json.load(open(REGRESSION, encoding='utf-8'))['cases']
    return [(c['id'], c['expect'], verdict(c['text'])) for c in d], d
VOCAB = re.compile(r"\b(empiric\w*|scientific\w*|science|falsif\w*|testab\w*|predict\w*|replicat\w*|validat\w*|evidence|experiment\w*|calibrat\w*|rigou?r\w*|credib\w*|highest standard|decisive|summit|maturity)\b", re.I)
MATHV = re.compile(r"\b(MATH-GATE|recomput\w*|comput\w*|theorem|lemma|CI\b|selftest|script|arithmetic|exact|derivation|proved|proof of|tools/)\b", re.I)
SCOPEV = re.compile(r"\b(optional|comparative|correspondence|hypothes\w+|study|studies|pilot|pre-regist\w+|EPR|M230|M267|Part 9|Appendix S|S\.\d|programme|mapping|investigat\w+|EMPIRICAL mode|COMPARATIVE mode|a person (may )?choose|on request|Tier C|annex|frozen|decoy|null|control)\b", re.I)
HISTV = re.compile(r"\b(APE-\d+|SEQ \d+|peer|the account|accounts|Grok|Qwen|GPT-6|DeepSeek|corrected|earlier|previously|record of)\b", re.I)
def matrix():
    """the occurrence-level audit: every sentence of the prose that uses the vocabulary of the sciences, with its class --
    PROTECTIVE (it negates or forbids), MATHEMATICAL (the Verify route of L-500), SCOPED (a study, a mode, Appendix S),
    HISTORICAL (it reports a peer or an earlier state) or UNCLASSED (read by a person; records/frame/audit_matrix.json)"""
    rows = []
    for nm, p in (('Core', CORE), ('Companion', COMP)):
        ps = paragraphs(p); inS = False
        for i, t in enumerate(ps):
            u = t.lstrip('# ').upper()
            if u.startswith('APPENDIX S'): inS = True
            elif u.startswith('APPENDIX '): inS = False
            if t.startswith(('# =====', '#!/', '- APE-', 'X.', 'R.')) or len(t) > 20000: continue
            for x in re.split(r'(?<=[.!?])\s+', t):
                b = QUOTED.sub(' ', x); m = VOCAB.search(b)
                if not m: continue
                if NEGATE.search(b[:m.start()][-80:]): c = 'PROTECTIVE'
                elif MATHV.search(b) and not SCOPEV.search(b): c = 'MATHEMATICAL'
                elif inS or SCOPEV.search(b): c = 'SCOPED'
                elif HISTV.search(b): c = 'HISTORICAL'
                else: c = 'UNCLASSED'
                rows.append((nm, i, c, x.strip()[:200]))
    return rows
ADVERSARIAL = os.path.join(REPO, 'records', 'frame', 'adversarial_prompts.json')
DEPARTURES = os.path.join(REPO, 'records', 'frame', 'departures.json')
def departures():
    P = []
    try: d = json.load(open(DEPARTURES, encoding='utf-8'))
    except Exception as e: return ['the register cannot be read: %s' % e], 0
    for e in d.get('entries', []):
        for f in ('id', 'where', 'who', 'demands', 'kind', 'found_by', 'corrected_in'):
            if e.get(f) in (None, '', []): P.append('%s: no %s' % (e.get('id', '?'), f))
        if e.get('kind') not in ('PEER ACCOUNT', 'DOCUMENT', 'NAVIGATOR OUTPUT'): P.append('%s: kind %s' % (e.get('id', '?'), e.get('kind')))
        if e.get('jurisdiction') not in ('FOUNDATIONAL FIDELITY', 'COMPARATIVE JURISDICTION'): P.append('%s: jurisdiction %s' % (e.get('id', '?'), e.get('jurisdiction')))
    try:
        a = json.load(open(ADVERSARIAL, encoding='utf-8'))['prompts']
        if len(a) < 5: P.append('fewer than five adversarial prompts')
        for x in a:
            if not x.get('prompt') or not x.get('jurisdiction') or not x.get('then'): P.append('adversarial prompt %s incomplete' % x.get('id', '?'))
    except Exception as e: P.append('the adversarial prompts cannot be read: %s' % e)
    return P, len(d.get('entries', []))
def obligation(ps):
    hits = []
    for i, t in prose(ps):
        for s in re.split(r'(?<=[.!?])\s+', t):
            bare = QUOTED.sub(' ', s)
            m = OBLIGE.search(bare)
            if m and not MENTION.search(bare[:m.start()][-120:] + ' ' + bare[m.start():m.end() + 40]):
                hits.append((i, s.strip()[:160]))
    return hits
def m286(paths):
    import frame_audit as fa
    n = 0; kinds = {}
    for p in paths:
        for _, k, s in fa.scan(fa.text_of(p)):
            if k in ('COURT', 'VERDICT', 'SCIENCE', 'TRIAL'): n += 1; kinds[k] = kinds.get(k, 0) + 1
    return n, kinds
def annex():
    wf = open(os.path.join(REPO, '.github', 'workflows', 'omega42-ci.yml'), encoding='utf-8').read()
    names = re.findall(r'^\s*- name: (.*)$', wf, re.M)
    marked = [n for n in names if n.startswith('Comparative annex (optional, L-491)')]
    stated = set()
    for p in (CORE, COMP):
        for t in paragraphs(p):
            for m in re.finditer(r'\bthe (\d+) comparative CI steps\b', t, re.I): stated.add(int(m.group(1)))
    return len(marked), stated
def triggers():
    import instrument_triggers as it
    return it.check()
def standings():
    d = json.load(open(os.path.join(REPO, 'records', 'discoveries', 'register.json'), encoding='utf-8'))
    comp = ('records/m267_pilot_01', 'records/blind_test_', 'records/evidence_run_', 'records/EPR_', 'records/pilot_0')
    bad = [e['id'] for e in d['discoveries'] if any(str(e.get('record', '')).startswith(c) for c in comp)]
    l530 = any('No comparative result raises or lowers a standing' in t for t in paragraphs(CORE))
    return bad, l530
def laws():
    ps = paragraphs(CORE)
    return [l for l in ('L-490:', 'L-491:') if not any(t.startswith(l) for t in ps)]
def placement():
    import doc_hygiene as dh
    return dh.summary(37)
def report():
    pc, pm = paragraphs(CORE), paragraphs(COMP)
    L = ['SCIENTIFIC ENCROACHMENT CHECK (Core Part 12, item 38; L-490, L-491)']; ok = True
    ob = [('Core', i, s) for i, s in obligation(pc)] + [('Companion', i, s) for i, s in obligation(pm)]
    ok &= not ob
    L.append('  (1) OBLIGATION   %s -- prose outside Appendix S that makes the work or a standing wait on a test: %d' % ('PASS' if not ob else 'FAIL', len(ob)))
    for d, i, s in ob: L.append('        %s [%d] %s' % (d, i, s))
    n, kinds = m286([CORE, COMP]); ok &= n == 0
    L.append('  (2) M286         %s -- COURT, VERDICT, SCIENCE and TRIAL over both documents: %d%s' % ('PASS' if n == 0 else 'FAIL', n, (' ' + str(kinds)) if n else ''))
    k, stated = annex(); a_ok = k > 0 and stated == {k}; ok &= a_ok
    L.append('  (3) ANNEX        %s -- %d CI steps marked "Comparative annex (optional, L-491)"; the documents state %s' % ('PASS' if a_ok else 'FAIL', k, ', '.join(map(str, sorted(stated))) or 'no number'))
    P = triggers(); ok &= not P
    L.append('  (4) TRIGGERS     %s -- the comparative guard of the M327 register (L-491)%s' % ('PASS' if not P else 'FAIL', (': ' + '; '.join(P)) if P else ''))
    bad, l530 = standings(); s_ok = not bad and l530; ok &= s_ok
    L.append('  (5) STANDINGS    %s -- no discovery rests on a comparative study%s; L-530 (2) states it: %s' % ('PASS' if s_ok else 'FAIL', (' (' + ', '.join(bad) + ')') if bad else '', 'YES' if l530 else 'NO'))
    miss = laws(); ok &= not miss
    L.append('  (6) LAWS         %s -- L-490 and L-491 in the Core%s' % ('PASS' if not miss else 'FAIL', (': missing ' + ', '.join(miss)) if miss else ''))
    pl_ok, pl_note = placement(); ok &= pl_ok
    L.append('  (7) PLACEMENT    %s -- %s' % ('PASS' if pl_ok else 'FAIL', pl_note))
    pr = [('Core', i, s) for i, s in premise(pc)] + [('Companion', i, s) for i, s in premise(pm)]; ok &= not pr
    L.append('  (8) PREMISE      %s -- prose outside Appendix S that places a comparative or empirical demand on the premise or an inside reading: %d' % ('PASS' if not pr else 'FAIL', len(pr)))
    for d, i, s in pr: L.append('        %s [%d] %s' % (d, i, s))
    dp, nd = departures(); ok &= not dp
    L.append('  (9) DEPARTURES   %s -- the Frame Departure Register, %d entries%s' % ('PASS' if not dp else 'FAIL', nd, (': ' + '; '.join(dp)) if dp else ''))
    ju = [('Core', i, x) for i, x in jurisdiction(pc)] + [('Companion', i, x) for i, x in jurisdiction(pm)]; ok &= not ju
    L.append('  (10) JURISDICTION %s -- inside Appendix S, no study made the destination of the protocol or the measure of its worth: %d' % ('PASS' if not ju else 'FAIL', len(ju)))
    for d, i, x in ju: L.append('        %s [%d] %s' % (d, i, x))
    dr = [('Core', i, x) for i, x in drift(pc)] + [('Companion', i, x) for i, x in drift(pm)]; ok &= not dr
    L.append('  (11) DRIFT       %s -- the purpose displaced: a study\'s standard made the summit of the protocol, the protocol a scientific instrument first: %d' % ('PASS' if not dr else 'FAIL', len(dr)))
    for d, i, x in dr: L.append('        %s [%d] %s' % (d, i, x))
    rg, _ = regression(); bad = [r for r in rg if r[1] != r[2]]; ok &= not bad
    L.append('  (12) REGRESSION  %s -- %d cases of jurisdictional substitution, each read as expected%s' % ('PASS' if not bad else 'FAIL', len(rg), (': ' + ', '.join('%s expected %s, read %s' % b for b in bad)) if bad else ''))
    L.append('VERDICT: %s' % ('NO ENCROACHMENT -- the scientific method stays an optional comparative tool, outside the constitutive core' if ok else 'ENCROACHMENT FOUND -- see the failing lines'))
    return ok, '\n'.join(L)
def selftest():
    good = ['L-490: x', 'The comparison is optional and no reading waits on it.', 'APPENDIX S: COMPARATIVE', 'This test is research-ready.', 'APPENDIX R: X']
    bad = ['The method is research-ready, its predictive tests the scheduled next work.']
    neg = ['The protocol is never pending validation.', 'A peer wrote "earned through empirical validation".']
    cases = [('an obligation outside Appendix S is found', len(obligation(bad)) == 1),
             ('inside Appendix S it is not', obligation(good) == []),
             ('a negated or quoted phrase is a mention', obligation(neg) == []),
             ('a Commons line reports a peer and is skipped', obligation(['- APE-1: it is pending validation']) == []),
             ('a demand on the premise is found', len(premise_hits([(1, 'The structure is not yet a physical theory.'), (2, 'Omega42 must reproduce what is known before it predicts.'), (3, 'It requires empirical validation.')])) == 3),
             ('a demand with its mode named, or negated, is a mention', premise_hits([(1, 'A mapping would reproduce what is known before it predicts, a study a person may choose.'), (2, 'The premise is not a hypothesis awaiting a test.'), (3, 'It never requires empirical validation.')]) == []),
             ('a sealed output is scanned, its question left out', len(premise_record('QUESTION VERBATIM: must it be tested against cosmological data?\nFRAME: x\nSUMMARY: The premise is only a hypothesis.')) == 1),
             ('a requirement whose object is a study is in its jurisdiction', premise_hits([(1, 'A physical extension must be falsifiable, and its prediction must make testable predictions.')]) == []),
             ('a requirement placed on the protocol is found', len(premise_hits([(1, 'Omega42 is incomplete until tested.'), (2, 'The premise must be falsifiable.')])) == 2),
             ('a study made the destination of the protocol is found in Appendix S', len(jurisdiction(['APPENDIX S: X', 'If it succeeds, Omega42 becomes a science of projection.', 'APPENDIX T: Y'])) == 1),
             ('a study kept in its jurisdiction passes in Appendix S', jurisdiction(['APPENDIX S: X', 'The study reports on its own correspondence and a navigation is complete without it.', 'APPENDIX T: Y']) == []),
             ('the purpose displaced is found', len(drift(['Prediction is the highest standard of discovery in Omega42.'])) == 1),
             ('every regression case reads as expected', all(a == b for _, a, b in regression()[0])),
             ('the Frame Departure Register passes', departures()[0] == []),
             ('an internal hold-out is not an obligation', obligation(['The classes stay DIAGNOSTIC until they are confirmed on candidates scored later.']) == [])]
    for nm, c in cases: print('%-50s %s' % (nm, 'PASS' if c else 'FAIL'))
    print('ENCROACHMENT SELFTEST: %d of %d' % (sum(c for _, c in cases), len(cases))); return all(c for _, c in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if len(a) > 1 and a[0] == '--records':
        bad = 0
        for f in a[1:]:
            h = premise_record(open(f, encoding='utf-8').read()); bad += len(h)
            print('PREMISE FIDELITY (L-491 (a), (b)): %s | %s' % (f, 'PASS' if not h else 'FAIL (%d)' % len(h)))
            for i, s in h: print('  line %d: %s' % (i, s))
        sys.exit(1 if bad else 0)
    if a == ['--matrix']:
        rows = matrix(); from collections import Counter; c = Counter(r[2] for r in rows)
        print('OCCURRENCE MATRIX (L-539 (6)): %d sentences | %s' % (len(rows), ' | '.join('%s %d' % kv for kv in sorted(c.items()))))
        for r in rows: print('  %-9s [%d] %-12s %s' % r)
        sys.exit(0)
    if a == ['--docs']:
        ok, t = report(); print(t); sys.exit(0 if ok else 1)
    print(__doc__); sys.exit(2)
