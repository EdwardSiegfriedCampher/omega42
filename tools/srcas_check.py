#!/usr/bin/env python3
"""srcas_check.py -- M224 for SR-CAS and SNCA output: the format that identifies Omega42 output (Core Part 6.1, 6.2, L-412, L-349).

Core L-412 makes the delimiter formats of the navigation (Part 8), the SR-CAS Assessment (Part 6.1) and the SNCA Assessment
(Part 6.2) the identifier of Omega42 output. tools/format_check.py enforces the first; this tool enforces the other two:

  SR-CAS   the PRE-SR-CAS VERBATIM VERIFICATION block (both hashes, MATCH, VERDICT PROCEED or HALT) before the report; the
           M270 EXTRACTION RECONCILIATION GATE before a report that proceeds; the report between its markers with every
           field of the M224 list of Part 6.1, in order; the five components recomputed into the Base Score
           (0.40 T1 + 0.15 T1.5 + 0.20 T2 + 0.10 T2.5 + 0.15 T3, within 0.01) and the weighted index (the comparison-class
           weight of L-416, capped at 1.00); a report halted on VERBATIM MISMATCH needs only DOMAIN, ARCHITECTURES COMPARED,
           PER-RUN VERDICT and MANDATORY CORRECTIONS.
  SNCA     the report between its markers with every field of Part 6.2 in order, the Base Score recomputed
           (0.30 T1.5 + 0.40 T2 + 0.30 T3, within 0.01), and the STATUS line on its two axes (L-428).

    python3 tools/srcas_check.py REPORT.txt [...]     # every SR-CAS and SNCA report in each file; exit 1 on any failure
    python3 tools/srcas_check.py --selftest
It applies to reports dated from 30 October 2026, when the check was made; earlier records are read and reported, never failed.

    python3 tools/srcas_check.py --owed     # the automatic trigger (Part 6.1, 6.2, L-489): every received navigation or review
                                            # filed as APE-271 or later is named in a record of records/srcas/; exit 1 on any not named
Standard library only. It reads; it never edits a record.
"""
import re, sys
SR_FIELDS = ['DOMAIN:', 'COMPLEXITY TIER (M271):', 'ARCHITECTURES COMPARED', 'T1 (Arithmetic):', 'T1.5 (Interpretive Integrity', 'T2 (Procedural):',
             'T2.5 (Synthesis Fidelity/SAS):', 'T3 (Discovery):', 'COMPONENT VECTOR', 'Base Score:', 'Comparison-class weight', 'Weighted index',
             'CONVERGENCE ASSESSMENT:', 'ROOT CAUSE ANALYSIS:', 'EXTRACTION-LAYER DIVERGENCE DIAGNOSTIC', 'INTERPRETIVE SYNTHESIS:', 'MEASUREMENT STATUS',
             'STATUS (two axes', 'SRH ASSESSMENT', 'Convergence Record entry', 'SRH Candidate designation', 'Alternative explanations',
             'Statistical significance', 'Cumulative context', 'HFRA', 'Recommendations', 'PER-RUN VERDICT', 'STRONGEST WARRANTED FINDINGS', 'MANDATORY CORRECTIONS:']
SR_HALT = ['DOMAIN:', 'ARCHITECTURES COMPARED', 'PER-RUN VERDICT', 'MANDATORY CORRECTIONS:']
SN_FIELDS = ['DOMAIN:', 'NAVIGATOR UNDER REVIEW', 'T1.5:', 'T2:', 'T3:', 'Base Score:', 'SYNTHESIS:', 'FINDINGS', 'INTERNAL', 'META', 'VERDICT:',
             'MANDATORY CORRECTIONS:', 'OPTIONAL ACTION:', 'STATUS (two axes', 'VERDICT CONFIRMATION']
INTERNAL = ('PENDING', 'PROCEDURALLY VALID', 'INTERNALLY COHERENT', 'INTERNAL CONTRADICTION', 'PROCEDURAL FAILURE', 'ARITHMETIC FAILURE', 'NOT EVALUABLE')
COMPARATIVE = ('NOT INVESTIGATED', 'COMPARISON PENDING', 'CONVERGENT', 'PARTIALLY CONVERGENT', 'DIVERGENT', 'INCONCLUSIVE', 'NOT CONVERGENT', 'NOT COMPARABLE')
NUM = re.compile(r'(?<![\w.])(-?\d+(?:\.\d+)?)')
def blocks(text, name):
    return [m.group(1) for m in re.finditer(r'======= %s =======(.*?)======= END %s =======' % (re.escape(name), re.escape(name)), text, re.S)]
def ordered(body, fields):
    pos, miss = 0, []
    for f in fields:
        i = body.find(f, pos)
        if i < 0: miss.append(f)
        else: pos = i + len(f)
    return miss
def first(body, label):
    i = body.find(label)
    if i < 0: return None
    seg = body[i + len(label):]; seg = seg[:seg.find('\n')] if '\n' in seg else seg
    if label == 'Base Score:' and '=' in seg.split('|')[0]: seg = seg.split('|')[0].rsplit('=', 1)[1]
    if label == 'Weighted index' and ':' in seg.split('|')[0]: seg = seg.split('|')[0].split(':', 1)[1]
    m = NUM.search(seg[:80])
    return float(m.group(1)) if m else None
def status_ok(body):
    m = re.search(r'STATUS \(two axes[^\n]*', body)
    if not m: return False
    s = m.group(0)
    return any(k in s for k in INTERNAL) and any(k in s for k in COMPARATIVE)
def check_srcas(text, body, before):
    P = []
    v = blocks(before, 'PRE-SR-CAS VERBATIM VERIFICATION')
    if not v: P.append('no PRE-SR-CAS VERBATIM VERIFICATION block before the report')
    halt = bool(re.search(r'HALT\s*[-—]+\s*VERBATIM MISMATCH', (v[-1] if v else '') + body))
    if v and not re.search(r'MATCH', v[-1]): P.append('the verification block states no MATCH')
    if v and not re.search(r'VERDICT:?\s*\[?(PROCEED|HALT)', v[-1]): P.append('the verification block states no VERDICT (PROCEED / HALT)')
    if halt:
        P += ['halted report: missing %s' % f for f in ordered(body, SR_HALT)]
        return P
    if not blocks(before, 'M270 EXTRACTION RECONCILIATION GATE'): P.append('no M270 EXTRACTION RECONCILIATION GATE before a report that proceeds')
    P += ['missing or out of order: %s' % f for f in ordered(body, SR_FIELDS)]
    T = [first(body, k) for k in ('T1 (Arithmetic):', 'T1.5 (Interpretive Integrity', 'T2 (Procedural):', 'T2.5 (Synthesis Fidelity/SAS):', 'T3 (Discovery):')]
    if 'T1.5 (Interpretive Integrity' in body:
        seg = body[body.find('T1.5 (Interpretive Integrity'):]; seg = seg[seg.find(':') + 1:seg.find('\n')]
        m = re.search(r'T1\.5-L\s*(\d+(?:\.\d+)?)', seg); T[1] = float(m.group(1)) if m and 'QUALIFIED' in seg else (first(seg, '') if T[1] is None else T[1])
    base = first(body, 'Base Score:'); w = re.search(r'x\s*(\d+(?:\.\d+)?)|×\s*(\d+(?:\.\d+)?)', body[body.find('Comparison-class weight'):] if 'Comparison-class weight' in body else '')
    if None in T or base is None: P.append('a component or the Base Score carries no number')
    else:
        calc = 0.40 * T[0] + 0.15 * T[1] + 0.20 * T[2] + 0.10 * T[3] + 0.15 * T[4]
        if abs(calc - base) > 0.01: P.append('Base Score %.2f does not recompute: 0.40 x %s + 0.15 x %s + 0.20 x %s + 0.10 x %s + 0.15 x %s = %.4f' % ((base,) + tuple(T) + (calc,)))
        wi = first(body, 'Weighted index')
        if w and wi is not None:
            mult = float(w.group(1) or w.group(2))
            if abs(min(1.0, base * mult) - wi) > 0.01: P.append('Weighted index %.2f is not min(1.00, %.2f x %.2f)' % (wi, base, mult))
    if not status_ok(body): P.append('STATUS does not name its two axes with their values (L-428)')
    return P
def check_snca(body):
    P = ['missing or out of order: %s' % f for f in ordered(body, SN_FIELDS)]
    T = [first(body, k) for k in ('T1.5:', 'T2:', 'T3:')]; base = first(body, 'Base Score:')
    if None in T or base is None: P.append('a component or the Base Score carries no number')
    else:
        calc = 0.30 * T[0] + 0.40 * T[1] + 0.30 * T[2]
        if abs(calc - base) > 0.01: P.append('Base Score %.2f does not recompute: 0.30 x %s + 0.40 x %s + 0.30 x %s = %.4f' % ((base,) + tuple(T) + (calc,)))
    if not status_ok(body): P.append('STATUS does not name its two axes with their values (L-428)')
    return P
def dated_from(text):
    m = re.search(r'(\d{1,2}) (September|October|November) 2026', text[:600])
    if not m: return True
    d, mo = int(m.group(1)), m.group(2)
    return mo == 'November' or (mo == 'October' and d >= 30)
def check(text):
    out = []
    for m in re.finditer(r'======= SR-CAS ASSESSMENT REPORT =======(.*?)======= END SR-CAS ASSESSMENT REPORT =======', text, re.S):
        out.append(('SR-CAS', text[m.end(1) - len(m.group(1)) - 40:][:0] or m.group(1)[:60].strip().split('\n')[0], check_srcas(text, m.group(1), text[:m.start()])))
    for m in re.finditer(r'======= SNCA ASSESSMENT REPORT =======(.*?)======= END SNCA ASSESSMENT REPORT =======', text, re.S):
        nm = re.search(r'NAVIGATOR UNDER REVIEW[^\n]*', m.group(1))
        out.append(('SNCA', nm.group(0)[:80] if nm else '?', check_snca(m.group(1))))
    return out
def report(path):
    text = open(path, encoding='utf-8').read(); res = check(text); enforced = dated_from(text)
    bad = sum(1 for _, _, p in res if p)
    print('SR-CAS / SNCA FORMAT (Core Part 6.1, 6.2, L-412): %s | %d report(s), %d with findings%s' % (path, len(res), bad, '' if enforced else ' | dated before 31 October 2026: reported, not failed'))
    for kind, name, p in res:
        print('  %-6s %-70s %s' % (kind, name[:70], 'PASS' if not p else 'FAIL (%d)' % len(p)))
        for x in p: print('         - ' + x)
    if not res: print('  no SR-CAS or SNCA report found')
    return (bad == 0 and bool(res)) or not enforced
GOOD_V = '======= PRE-SR-CAS VERBATIM VERIFICATION =======\nA: abc -- MATCH\nB: abc -- MATCH\nMATCH: YES\nVERDICT: PROCEED\n======= END PRE-SR-CAS VERBATIM VERIFICATION =======\n======= M270 EXTRACTION RECONCILIATION GATE =======\nRECONCILED\n======= END M270 EXTRACTION RECONCILIATION GATE =======\n'
GOOD_R = ('======= SR-CAS ASSESSMENT REPORT =======\nDOMAIN: x\nCOMPLEXITY TIER (M271): Tier 1\nARCHITECTURES COMPARED (with session identifiers): A, B\nT1 (Arithmetic): 1.00\nT1.5 (Interpretive Integrity): 0.50\nT2 (Procedural): 1.00\n'
          'T2.5 (Synthesis Fidelity/SAS): 0.30\nT3 (Discovery): 0.60\nCOMPONENT VECTOR (primary): ... | Base Score: 0.79 | Comparison-class weight (L-416): x1.5 | Weighted index: 1.00\nCONVERGENCE ASSESSMENT: c\nROOT CAUSE ANALYSIS: r\n'
          'EXTRACTION-LAYER DIVERGENCE DIAGNOSTIC: N/A\nINTERPRETIVE SYNTHESIS: i\nMEASUREMENT STATUS: DIAGNOSTIC\nSTATUS (two axes, L-428): INTERNALLY COHERENT | COMPARATIVE STATUS: CONVERGENT\nSRH ASSESSMENT:\n- Convergence Record entry: e\n- SRH Candidate designation: NO\n'
          '- Alternative explanations: a\n- Statistical significance: n\n- Cumulative context: n\n- HFRA: h\n- Recommendations: r\nPER-RUN VERDICT: v\nSTRONGEST WARRANTED FINDINGS: f\nMANDATORY CORRECTIONS: none\n======= END SR-CAS ASSESSMENT REPORT =======\n')
GOOD_S = ('======= SNCA ASSESSMENT REPORT =======\nDOMAIN: x\nNAVIGATOR UNDER REVIEW (EXTERNAL AGENT): B\nT1.5: 0.50\nT2: 0.10\nT3: 0.40\nBase Score: 0.31\nSYNTHESIS: s\nFINDINGS -- INTERNAL: f\nFINDINGS -- META: m\nVERDICT: v\nMANDATORY CORRECTIONS: c\nOPTIONAL ACTION: o\n'
          'STATUS (two axes, L-428): PROCEDURAL FAILURE | COMPARATIVE STATUS: NOT INVESTIGATED\nVERDICT CONFIRMATION: N/A\n======= END SNCA ASSESSMENT REPORT =======\n')
HALT = ('======= PRE-SR-CAS VERBATIM VERIFICATION =======\nA: abc\nB: none -- NOT VERIFIABLE\nMATCH: NO\nVERDICT: HALT -- VERBATIM MISMATCH\n======= END PRE-SR-CAS VERBATIM VERIFICATION =======\n'
        '======= SR-CAS ASSESSMENT REPORT =======\nDOMAIN: x\nARCHITECTURES COMPARED: A, B\nPER-RUN VERDICT: HALT\nMANDATORY CORRECTIONS: B re-issued\n======= END SR-CAS ASSESSMENT REPORT =======\n')
def selftest():
    r = lambda t: [p for _, _, p in check(t)]
    cases = [('a complete SR-CAS report passes', r(GOOD_V + GOOD_R) == [[]]),
             ('a wrong Base Score fails', any('does not recompute' in x for x in r(GOOD_V + GOOD_R.replace('Base Score: 0.79', 'Base Score: 0.90'))[0])),
             ('a weighted index above the cap fails', any('Weighted index' in x for x in r(GOOD_V + GOOD_R.replace('Weighted index: 1.00', 'Weighted index: 1.18'))[0])),
             ('a missing field fails', any('ROOT CAUSE' in x for x in r(GOOD_V + GOOD_R.replace('ROOT CAUSE ANALYSIS: r\n', ''))[0])),
             ('a report without its verification block fails', any('VERBATIM VERIFICATION' in x for x in r(GOOD_R)[0])),
             ('a halted report needs only its four fields', r(HALT) == [[]]),
             ('a complete SNCA report passes', r(GOOD_S) == [[]]),
             ('an SNCA without both status axes fails', any('two axes' in x for x in r(GOOD_S.replace(' | COMPARATIVE STATUS: NOT INVESTIGATED', ''))[0])),
             ('an SNCA Base Score is recomputed', any('does not recompute' in x for x in r(GOOD_S.replace('Base Score: 0.31', 'Base Score: 0.50'))[0]))]
    for n, ok in cases: print('%-60s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('SR-CAS / SNCA FORMAT SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
import glob, os
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWED_FROM = 271   # the first APE of the record of 30 October 2026, from which every review has its report
def owed():
    recs = ''.join(open(f, encoding='utf-8').read() for f in glob.glob(os.path.join(REPO, 'records', 'srcas', '*.txt')))
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, 'submissions', 'ape', 'APE-*.md'))):
        n = int(re.search(r'APE-(\d+)', f).group(1))
        if n < OWED_FROM: continue
        body = open(f, encoding='utf-8').read()
        if re.search(r'THE ANSWER|NAVIGATOR IDENTITY BLOCK|Navigation|navigation|SR-CAS|assessment|Assessment', body):
            out.append(('APE-%03d' % n, ('APE-%03d' % n) in recs))
    return out
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--owed']:
        o = owed(); miss = [k for k, ok in o if not ok]
        print('SR-CAS / SNCA OWED ON RECEIPT (Core Part 6.1, 6.2, L-489): %d received from APE-%03d, %d named in records/srcas/, %s' % (len(o), OWED_FROM, len(o) - len(miss), 'PASS' if not miss else 'FAIL: ' + ', '.join(miss)))
        sys.exit(1 if miss else 0)
    if not a: print(__doc__); sys.exit(2)
    sys.exit(0 if all([report(p) for p in a]) else 1)
