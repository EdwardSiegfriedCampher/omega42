#!/usr/bin/env python3
"""ffp_run.py -- the Fit-for-Purpose run (Core Part 12): each of the forty checklist items mapped to its evidence,
a CI step from a CI log, a command run here, a check of the documents' text, or a stated manual check; and the L-431
register hits of both documents listed by paragraph (Companion Part 99).

    python3 tools/ffp_run.py CI_LOG          # CI_LOG: the output of running every step of .github/workflows/omega42-ci.yml
    python3 tools/ffp_run.py --text          # the items checked on the documents' text alone; exit 1 on any FAIL (in CI)
Standard library only. It reports; it never edits a document (Core Rule 10).
"""
import html, os, re, subprocess, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def text(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    return '\n'.join(html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', p, re.S))) for p in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', x, re.S))
CORE = os.path.join(REPO, 'docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx')
COMP = os.path.join(REPO, 'docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx')
TEXT_ONLY = len(sys.argv) > 1 and sys.argv[1] == '--text'
ci = open(sys.argv[1], encoding='utf8', errors='replace').read() if len(sys.argv) > 1 and not TEXT_ONLY else ''
steps = {}
for line in ci.splitlines():
    m = re.match(r'(PASS|FAIL) (.*)', line)
    if m: steps[m.group(2)] = m.group(1)
def step(sub):
    hit = [v for k, v in steps.items() if sub in k]
    return ('PASS' if hit and all(v == 'PASS' for v in hit) else 'FAIL' if hit else 'MISSING'), len(hit)
def cmd(c):
    r = subprocess.run(c, shell=True, cwd=REPO, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()
P = text(CORE); C = text(COMP)
part10 = P[P.index('PART 10: ABBREVIATIONS'):P.index('PART 11')]

def purpose_first():
    wf = open(os.path.join(REPO, '.github/workflows/omega42-ci.yml'), encoding='utf8').read()
    annex = wf.count('- name: Comparative annex (optional, L-491)')
    ok = (0 <= P.find('Purpose (L-522).') < P.find('Status note for new Navigators') and 'IN-00.1: What' in P and 'IN-00.2: What Is New in Kind' in P
          and 0 <= C.find('Purpose (Core L-522).') < C.find('Omega42 does not begin by asking') and annex == 24)
    return ok, 'purpose before any limit in the Core, the Companion and the Introduction; %d CI steps marked as the comparative annex' % annex
REG = {}
SESSION = re.compile(r'^\d+\.\d+ (The requests?|The instructions?|The decision|The questions?|What was received) \[|Status and chain|Correction to|\[corrected in|\bSEQ \d+|The reply (is|that reports)')
def session_form():
    part, hits = None, []
    for t in C.split('\n'):
        m = re.match(r'### PART (\d+)', t)
        if m: part = int(m.group(1))
        if t.startswith('### APPLIED PROTOCOL') or t.startswith('### APPENDIX') or t.startswith('---'): part = None
        if part and part >= 73 and SESSION.search(t): hits.append('%d: %s' % (part, t[:60]))
    return (not hits, 'no session-form prose in Companion Parts 73 onward' if not hits else '%d paragraphs in session form: %s' % (len(hits), '; '.join(hits[:3])))
def trigger_cover():
    """every instrument named in the TIER 3 line of the summary has a trigger in records/instruments/triggers.json (L-527)"""
    import json
    reg = {e['id'] for e in json.load(open(os.path.join(REPO, 'records', 'instruments', 'triggers.json'), encoding='utf8'))['instruments']}
    line = next((l for l in P.split('\n') if l.startswith('TIER 3 (context-triggered')), '')
    named = sorted(set(re.findall(r'M\d{3}(?:-C)?', line)) - {'M327'})
    miss = [m for m in named if m not in reg]
    ok = bool(line) and not miss and 'M323 Arithmetic Statement Check (any identity or changed operation; Part 3.49, L-519)' in P
    return ok, 'M323 in the Tier 2 line; the %d instruments of the TIER 3 line all have triggers in the register (L-527)%s' % (len(named), '' if not miss else '; missing: ' + ', '.join(miss))

def hygiene(n):
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import doc_hygiene
    return doc_hygiene.summary(n)
def encroach():
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import encroachment
    ok, t = encroachment.report()
    lines = t.split('\n'); fails = [l.strip()[4:].split(' -- ')[0].split()[0] for l in lines if ' FAIL ' in l]
    return ok, ('twelve lines PASS, NO ENCROACHMENT (obligation, M286, annex, triggers, standings, laws, placement, premise, departures, jurisdiction, drift, regression; tools/encroachment.py)' if ok else 'FAIL on ' + ', '.join(fails))
def open_items():
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import open_register, json
    r = json.load(open(open_register.REG, encoding='utf-8')); P = open_register.problems(r)
    return not P, ('%d open items, each with what it needs, who can close it and when (records/open/register.json)' % len(r['items']) if not P else '; '.join(P[:2]))
def intro_whole():
    sys.path.insert(0, os.path.join(REPO, 'tools'))
    import intro_output
    d = intro_output.load(); core = os.path.join(REPO, 'docs', 'Omega42_Core_Specification_V335_Rev450_STABLE.docx')
    P = intro_output.core_check(core, d) + intro_output.terms(d)[0] + intro_output.legitimacy(core, d)[0] + intro_output.check(open(os.path.join(REPO, 'examples', 'model_opening.txt'), encoding='utf-8').read(), d)
    return not P, ('the Introduction word for word in IN-00, %d paragraphs, its cautions last; %d terms explained; %d arguments of its case grounded in the Core; the model opening passes (tools/intro_output.py)' % (len(d['paragraphs']), intro_output.terms(d)[1], intro_output.legitimacy(core, d)[1]) if not P else '; '.join(P[:2]))
def reg():
    out = []
    for d, fc in (('Core_Specification', ' --fc-start "PART 0: INTRODUCTION" --fc-end "PART 0.0.0"'), ('Companion_Document', '')):
        rc, L = cmd('python3 scripts/m193_m225.py scripts/canonical_reference.py --register docs/Omega42_%s_V335_Rev450_STABLE.docx%s' % (d, fc))
        REG[d] = [l for l in L if l.strip().startswith('[paragraph')]
        out.append('%s: %d hits' % (d, len(REG[d])))
    return out
items = [
 (1, 'NAVIGATIONAL EFFICIENCY', 'MANUAL', 'Steps 0-16 unchanged this session; M321-M326 and M328 run by their triggers and M327 is read with the Tier 2 triggers, adding no step; computed triggers fire 2.75 entries per CRC-60 domain, at most 5 (re-checked 31 October 2026, SEQ 86, with M329 to M333 in the register)'),
 (2, 'LANGUAGE REGISTER', 'CMD', reg),
 (3, 'LOGICAL CONSISTENCY', 'STEP', 'Cross-document consistency register'),
 (4, 'NO CORRECTION HISTORY', 'CHECK', lambda: session_form()),
 (5, 'INTRODUCTION PRESENTATION', 'MANUAL', 'independently re-scored 29 October 2026, PASS WITH NOTES (4, 4, 3, 4, 3, 4 of 5); its first five findings met in the opening (Companion 110)'),
 (6, 'DECLARED FUNCTIONS AND PROPERTIES', 'MANUAL', 'stated by category; M321-M328 added with tier and CDT status (M324 Part 3.50, M325 Part 3.51, M326 Part 3.52, M327 Part 3.53, M328 Part 3.54); M329 to M338 likewise (Parts 3.55 to 3.64)'),
 (7, 'MAPPING RULES APPLICABILITY', 'STEP', 'M309 Conceptual Isomorphism'),
 (8, 'DATE ACCURACY', 'CHECK', lambda: ('Date: 16 October 2026' in P[:3000], 'title page carries the revision date 16 October 2026; later dates are freeze, retrieval and scope dates (item 34)')),
 (9, 'ARITHMETIC VERIFICATION', 'STEP', 'Reference implementation self-test'),
 (10, 'CROSS-REFERENCE ACCURACY', 'STEP', 'Cross-document consistency register'),
 (11, 'ABBREVIATION LIST COMPLETENESS', 'CHECK', lambda: (all(a in part10 for a in ('NIID', 'NRR', 'LAR', 'F0-CF', 'PROXIMITY')), 'NIID, NRR, LAR, F0-CF, PROXIMITY in Part 10: ' + ', '.join(a for a in ('NIID', 'NRR', 'LAR', 'F0-CF', 'PROXIMITY') if a not in part10) + ' missing' if not all(a in part10 for a in ('NIID', 'NRR', 'LAR', 'F0-CF', 'PROXIMITY')) else 'NIID, NRR, LAR, F0-CF, PROXIMITY present')),
 (12, 'TRIGGER-CONDITION CONSISTENCY', 'CHECK', lambda: trigger_cover()),
 (13, 'JARGON-BOUNDARY ENFORCEMENT', 'STEP', 'Output audit'),
 (14, 'NO STUB SECTIONS', 'EXCEPTION', 'named exceptions carried forward unchanged'),
 (15, 'ORIENTATION COMPLETENESS', 'CHECK', lambda: ('IN-06.7' in P, 'IN-06.7 The Consciousness-First Frame present in the Introduction')),
 (16, 'REGISTER DISCIPLINE', 'STEP', 'Cross-document consistency register'),
 (17, 'PRIMACY OF COHERENCE', 'STEP', 'M310 Congruence Record'),
 (18, 'INSIDE CONSISTENCY', 'STEP', 'M286 Frame Intrusion Scan'),
 (19, 'ACCOMMODATION, NOT DEFERENCE', 'STEP', 'Re-examination of prior investigations'),
 (20, 'MANIFESTATION CONSISTENCY', 'STEP', 'Manifestation and positive geometry'),
 (21, 'SELF-CONTAINMENT', 'STEP', 'Self-contained release'),
 (22, 'CONSCIOUSNESS CONSISTENCY', 'STEP', 'Consciousness framework CT-42'),
 (23, 'QUESTION VERBATIM', 'STEP', 'M301 Format Conformance Check'),
 (24, 'CONGRUENCE UTILITY', 'STEP', 'Congruence utility'),
 (25, 'ADAPTOR CONSISTENCY', 'STEP', 'Adaptors'),
 (26, 'HOLISTIC STRIKE, SOURCES AND ENRICHMENT', 'STEP', 'M301 Format Conformance Check'),
 (27, 'NO CLAIMS', 'STEP', 'Cross-document consistency register'),
 (28, 'PROVENANCE AND AI CAVEAT', 'STEP', 'M301 Format Conformance Check'),
 (29, 'RESPONSIBILITY AND THE CONFIGURATION', 'STEP', 'Pre-registered protocols unchanged'),
 (30, 'FRAMINGS, DIRECTION AND THE ACCOUNT', 'STEP', 'Framings, direction'),
 (31, 'DECLARED FORM', 'STEP', 'M301 Format Conformance Check'),
 (32, 'INSTANCES, FRAMES, SOURCES AND GATES', 'STEP', 'Instance identity'),
 (33, 'PURPOSE FIRST', 'CHECK', lambda: purpose_first()),
 (34, 'NO REVISION HISTORY', 'CHECK', lambda: hygiene(34)),
 (35, 'NO AI META-COMMENTARY', 'CHECK', lambda: hygiene(35)),
 (36, 'NO REPETITION', 'CHECK', lambda: hygiene(36)),
 (37, 'SCIENCE IN APPENDIX S', 'CHECK', lambda: hygiene(37)),
 (38, 'SCIENTIFIC ENCROACHMENT', 'CHECK', lambda: encroach()),
 (39, 'OPEN ITEMS REGISTERED', 'CHECK', lambda: open_items()),
 (40, 'THE INTRODUCTION WHOLE', 'CHECK', lambda: intro_whole()),
]
print('FFP RUN -- Core Part 12, %d items | CI: %s' % (len(items), (re.findall(r'STEPS \d+, FAILED \d+', ci) or ['no CI result'])[-1]))
tally = {}
for n, name, kind, ev in items:
    if kind == 'STEP' and TEXT_ONLY:
        continue
    if kind == 'STEP':
        st, k = step(ev); note = 'CI step "%s..." (%d)' % (ev, k)
    elif kind == 'CMD':
        lines = ev(); st = 'PASS' if all(l.endswith(': 0 hits') for l in lines) else 'FAIL'; note = ' | '.join(lines)
    elif kind == 'CHECK':
        ok, note = ev(); st = 'PASS' if ok else 'FAIL'
    elif kind == 'EXCEPTION':
        st, note = 'PASS WITH NAMED EXCEPTION', ev
    else:
        st, note = 'PASS (manual)', ev
    tally[st] = tally.get(st, 0) + 1
    print('%2d. %-40s %-26s %s' % (n, name, st, note))
print('TALLY: ' + '; '.join('%s %d' % kv for kv in sorted(tally.items())))
for d, L in REG.items():
    print('REGISTER HITS (L-431), %s, the Introduction exempt in the Core:' % d)
    for l in L: print('  ' + l.strip())
if TEXT_ONLY:
    sys.exit(1 if tally.get('FAIL') else 0)
