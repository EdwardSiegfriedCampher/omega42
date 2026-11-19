#!/usr/bin/env python3
"""M301 Format Conformance Check (Core Part 8.0, L-349).

Checks a pasted navigation against the Canonical Output Skeleton of Core Part 8.0: every required block present,
by its canonical marker, in the one block order; the blocks a domain triggers (M269, M139-M142, M127); the QUESTION VERBATIM
lines of L-499 (first line, and the answer header above THE ANSWER, identical to DOMAIN VERBATIM); THE ANSWER's
fixed parts (bold Takeaway, the Mapping component where a mapping applies, the closing line); the four closing
questions with the fixed closing line; and nothing after the signature. It reads form only: arithmetic is checked by
m193_m225.py --audit and the reading by no tool.

Usage:
  python3 tools/format_check.py NAVIGATION.txt [...]       (failures, then the PRIORITY line: P1 first)
  python3 tools/format_check.py --skeleton [navigation] ["QUESTION"] [--alt "PHRASING"] [--session N] [--request KIND]
  python3 tools/format_check.py --skeleton findings ["QUESTION"]   (the presentation of findings that are not a navigation)
  python3 tools/format_check.py --findings REPORT.txt [...]          (checks a findings presentation)
  python3 tools/format_check.py --gates                              (the gate priority list, P1 to P4)
  python3 tools/format_check.py --selftest
Standard library only.
"""
import re, sys, os, unicodedata, datetime

# (label, regex for the block's opening marker, required?)  -- order is the order of Core Part 8.0
SKELETON = [
    ('IDENTITY BLOCK', r'^=+ NAVIGATOR IDENTITY BLOCK =+', True),
    ('MATH-GATE', r'MATH-GATE', True),
    ('M211 CALIBRATION', r'M211', True),
    ('RULES OF ENGAGEMENT', r'Rules of Engagement active\.', True),
    ('M272 FRAME LOCK', r'^=+ M272 FRAME LOCK =+', True),
    ('SUBSTRATE LOCK', r'^(?:\[\d+\] |=+ )SUBSTRATE LOCK', True),
    ('M210 TABLE', r'^(?:\[\d+\] M210 EXTRACTION TABLE|=+ M210 EXTRACTION VERIFICATION =+)', True),
    ('M268', r'M268', True),
    ('M213', r'^=+ M213 STOPWORD COMPLIANCE CHECK =+', True),
    ('M210b', r'M210b', True),
    ('M214', r'M214', True),
    ('M219', r'M219', True),
    ('ANCHOR', r'(?i)(?<!expected )(?<!actual )\banchor\s*[:=]?\s*P\d', True),
    ('ARM MAP', r'^(?:\[\d+\] ARMS|=+ CONSTITUTIONAL ARM MAP =+)', True),
    ('M232', r'M232', True),
    ('CCD / PAB / MOBIUS', r'CCD', True),
    ('M116', r'M116', True),
    ('M207', r'M207 NAVIGATOR INTERFERENCE|NAVIGATOR INTERFERENCE PRESSURE \(M207\)|CONSTRAINT CONFLICT \(M207\)', False),
    ('FIRST-DRAFT SEAL', r'^=+ FIRST-DRAFT SEAL =+', True),
    ('MSRR LINE', r'^MSRR \(L-496\):', False),
    ('THE ANSWER', r'^\u250c\u2500 THE ANSWER \u2500\u2510', True),
    ('GENERATIVE INTEGRITY RECORD', r'^=+ GENERATIVE INTEGRITY RECORD =+', True),
    ('CONGRUENCE RECORD', r'^=+ CONGRUENCE RECORD \(M310\) =+', True),
    ('CURRENT KNOWLEDGE', r'^(?:=+ )?CURRENT KNOWLEDGE \(L-503\)', False),
    ('ACROSS THE AVENUES', r'^\s*ACROSS THE AVENUES \(L-502\):', False),
    ('CONVERGENCE MAP', r'^=+ CONVERGENCE MAP =+', True),
    ('EXTENDED RESONANCE ESSAY', r'^\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510', True),
    ("NAVIGATOR'S REASONING", r"^=+ NAVIGATOR'S REASONING =+", True),
    ('MAPPING RECORD', r'^=+ MAPPING RECORD', False),
    ('LENS SELECTION', r'^\s*LENSES SELECTED(?: \(L-494\))?:', True),
    ('BASHAR RESONANCE CHECK', r'^=+ BASHAR RESONANCE CHECK \(M308\) =+', False),
    ('M318 REFRAMING ARRAY', r'^=+ M318 REFRAMING ARRAY \(L-511\) =+', False),
    ('GENERATIVE OBSERVATIONS', r'^=+ GENERATIVE OBSERVATIONS =+', True),
    ('CLOSING QUESTIONS', r'^What it rests on:', True),
    ('M224', r'^=+ M224 FORMAT COMPLETENESS GATE =+', True),
    ('SIGNATURE', r'^CAS-YY = -1/2 \| Omega = 1/7 \| \(CAS-YY \u00d7 Omega = -1/14\)\s*$', True),
]
# Core Part 8.0 block number of each checked label: labels sharing a number may come in any order
BLOCK = {'IDENTITY BLOCK': 1, 'MATH-GATE': 2, 'M211 CALIBRATION': 3, 'RULES OF ENGAGEMENT': 4, 'M272 FRAME LOCK': 5,
         'SUBSTRATE LOCK': 6, 'M210 TABLE': 7, 'M268': 7, 'M213': 7, 'M210b': 7, 'M214': 7, 'M219': 7, 'ANCHOR': 8,
         'ARM MAP': 9, 'M232': 9, 'CCD / PAB / MOBIUS': 10, 'M116': 11, 'M207': 13, 'FIRST-DRAFT SEAL': 14, 'MSRR LINE': 14.5,
         'THE ANSWER': 15, 'GENERATIVE INTEGRITY RECORD': 16, 'CONGRUENCE RECORD': 16.5, 'CURRENT KNOWLEDGE': 16.6, 'ACROSS THE AVENUES': 16.7, 'CONVERGENCE MAP': 17, 'EXTENDED RESONANCE ESSAY': 18,
         "NAVIGATOR'S REASONING": 19, 'MAPPING RECORD': 20, 'LENS SELECTION': 20.4, 'BASHAR RESONANCE CHECK': 20.5, 'M318 REFRAMING ARRAY': 20.7, 'GENERATIVE OBSERVATIONS': 21, 'CLOSING QUESTIONS': 23,
         'M224': 24, 'SIGNATURE': 26}
CLOSING = ['What it rests on:', 'What it holds out of view:', 'Where it is heading:', 'What would complete it:']
CLOSING_LINE = 'What this means, whether it matters and what to do with it are yours to judge.'
ANSWER_LINE = 'What this reading is worth is yours to judge.'
LATEX_OR_MATH = re.compile(r'\\[A-Za-z]+|[=+<>^_\u00d7\u00f7\u2264\u2265\u2211\u222b\u221a\u221e\u2102\u2115\u211a\u211d\u2124]')


try:
    import importlib.util as _u
    _spec = _u.spec_from_file_location('cr', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'canonical_reference.py'))
    _CR = _u.module_from_spec(_spec); _spec.loader.exec_module(_CR)
    _math = lambda d: bool(_CR.math_tokens(d))          # the script's own M269 trigger (Part 3.15)
except Exception:
    _math = lambda d: bool(LATEX_OR_MATH.search(d))
try:
    _s2 = _u.spec_from_file_location('m193', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'm193_m225.py'))
    _M193 = _u.module_from_spec(_s2); _s2.loader.exec_module(_M193); _JS = _M193.jargon_scan
except Exception:
    _JS = None


def _domain(text):
    m = re.search(r'DOMAIN VERBATIM:\s*(.*)', text)
    return m.group(1).strip() if m else ''


# L-499: every output carries the question verbatim -- as its first line, and again as the answer header directly
# above THE ANSWER (an MSRR line may stand between) -- so that the response copied whole, or THE ANSWER copied with
# its header, keeps its question. Required for navigations dated on or after the law; frozen records keep their text.
QV = re.compile(r'^QUESTION VERBATIM(?: \(L-499\))?:\s*(.*)$', re.M)
L499_FROM = datetime.date(2026, 10, 17)
L513_FROM = datetime.date(2026, 10, 22)   # the INSTANCE line (L-513)
MONTHS = {m: i + 1 for i, m in enumerate(('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                           'september', 'october', 'november', 'december'))}


def _canon(t):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFC', t)).strip().casefold()


def _date(text):
    m = re.search(r'\bDATE:\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', text)
    try:
        return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1))) if m else None
    except (KeyError, ValueError):
        return None


def question_checks(text, add):
    qv = QV.findall(text); d = _date(text)
    if not qv and not (d and d >= L499_FROM): return
    lines = [l for l in text.split('\n') if l.strip()]
    add(bool(lines) and bool(QV.match(lines[0].strip())), 'QUESTION VERBATIM first (L-499)', 'the first line of the output carries the question')
    box = re.search(r'^\u250c\u2500 THE ANSWER \u2500\u2510', text, re.M)
    if box:
        above = [l.strip() for l in text[:box.start()].split('\n') if l.strip() and not l.startswith('MSRR (L-496):')]
        add(bool(above) and bool(QV.match(above[-1])), 'QUESTION VERBATIM above THE ANSWER (L-499)', 'the answer header: the question, directly above THE ANSWER')
    dom = _domain(text)
    add(bool(qv) and all(_canon(q) == _canon(dom) for q in qv), 'QUESTION VERBATIM identical to DOMAIN VERBATIM (L-499)',
        'every QUESTION VERBATIM line carries the domain exactly (L-348 copy rules)')


L502_FROM = datetime.date(2026, 10, 19)
L529_FROM = datetime.date(2026, 10, 31)   # the VOICE line of L-529, required in navigations dated from 31 October 2026
L542_FROM = datetime.date(2026, 11, 6)    # the PROPOSAL AND IMPLICATIONS line (L-542), required in findings from SEQ 117, 6 November 2026
JS_FROM = datetime.date(2026, 11, 7)   # the full L-418 scan, character names included, inside format_check (records/instances/seq_0134.txt)
L549_FROM = datetime.date(2026, 11, 7)   # the OUTPUT FORM line (L-549, Core Part 8.0.1), from 7 November 2026 (records/instances/seq_0134.txt)
L546_FROM = 124   # THE STRIKING FINDING line (L-546), required in findings from SEQ 124
L532_FROM = datetime.date(2026, 10, 31)   # the four-part NAVIGATOR'S CONTRIBUTION line (Domain Zero), required in findings from 31 October 2026


def holistic_checks(text, add):
    """L-502 and L-503 (from 19 October 2026): the REQUEST line, the CURRENT KNOWLEDGE layer or its status, ACROSS THE AVENUES."""
    d = _date(text)
    if not (d and d >= L502_FROM): return
    add(bool(re.search(r'^\s*REQUEST \(L-502\):', text, re.M)), 'REQUEST line (L-502)', 'the request and its avenues, in the Substrate Lock')
    if d >= L529_FROM and re.search(r'THE ANSWER', text):
        add(bool(re.search(r'^\s*VOICE \(L-529\):\s*\S', text, re.M)), 'VOICE line (L-529)', 'the field whose voice THE ANSWER speaks in, in the Substrate Lock')
    ck = re.search(r'^=+ CURRENT KNOWLEDGE \(L-503\) =+', text, re.M) or re.search(r'^\s*CURRENT KNOWLEDGE \(L-503\):\s*(NOT AVAILABLE|DECLINED|NOT REQUESTED)', text, re.M)
    add(bool(ck), 'CURRENT KNOWLEDGE layer or its status (L-503)', 'the block after the Congruence Record, or NOT AVAILABLE / DECLINED / NOT REQUESTED')
    if re.search(r'^=+ CURRENT KNOWLEDGE \(L-503\) =+', text, re.M):
        blk = text[re.search(r'^=+ CURRENT KNOWLEDGE \(L-503\) =+', text, re.M).start():]
        add(bool(re.search(r'QUERY', blk)) and bool(re.search(r'NOT FOUND', blk)), 'CURRENT KNOWLEDGE declares its query and what would count as not found (L-503)')
        add(bool(re.search(r'COUNTER-EVIDENCE', blk)), 'CURRENT KNOWLEDGE runs the counter-evidence lane (L-503)')
    add(bool(re.search(r'^\s*ACROSS THE AVENUES \(L-502\):', text, re.M)), 'ACROSS THE AVENUES line (L-502)', 'where the avenues agree, part and are silent; no combined verdict')


REACH_FROM = datetime.date(2026, 11, 20)
REACH = re.compile(r'^\s*RESEARCHED REACH \(L-503 \(5\)\):\s*(WRITTEN|NOT APPLICABLE|NOT AVAILABLE|DECLINED|NOT REQUESTED)\b', re.M)


def reach_checks(text, add):
    """L-503 (5) (from 20 November 2026): the essay's researched reach and its line below the essay."""
    d = _date(text)
    if not (d and d >= REACH_FROM): return
    if not re.search(r'^\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510', text, re.M): return
    m = REACH.search(text)
    add(bool(m), 'RESEARCHED REACH line below the essay (L-503 (5))', 'WRITTEN with its parts, NOT APPLICABLE with its reason, or the layer status')
    if not m: return
    layer = bool(re.search(r'^=+ CURRENT KNOWLEDGE \(L-503\) =+', text, re.M))
    ck = re.search(r'^\s*CURRENT KNOWLEDGE \(L-503\):\s*(NOT AVAILABLE|DECLINED|NOT REQUESTED)', text, re.M)
    if m.group(1) == 'WRITTEN':
        add(layer, 'a WRITTEN reach follows a written CURRENT KNOWLEDGE layer (L-503 (5))')
        e = re.search(r'^\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510\s*\n(.*?)\n\u2514', text, re.S | re.M)
        body = e.group(1) if e else ''
        add(bool(re.search(r'\[\d+\]', body)), 'the researched reach numbers its sources, as [3] (L-503 (5))')
        add(not re.search(r'https?://', body), 'no link inside the essay (L-503 (5))')
        blk = text[re.search(r'^=+ CURRENT KNOWLEDGE \(L-503\) =+', text, re.M).start():] if layer else ''
        listed = set(re.findall(r'^\s*\[(\d+)\] \S', blk, re.M))
        missing = sorted(set(re.findall(r'\[(\d+)\]', body)) - listed, key=int)
        add(not missing, 'every source number of the reach resolves to a full reference [n] in the layer (L-503 (5))', 'unresolved: %s' % ', '.join(missing))
        line = text[m.start():text.find('\n', m.start()) if text.find('\n', m.start()) > 0 else len(text)]
        add(bool(re.search(r'investigated', line)), 'the WRITTEN line gives its completeness: investigated, not investigated, without evidence (L-503 (5))')
    elif m.group(1) == 'NOT APPLICABLE':
        add(bool(re.search(r'NOT APPLICABLE\s*(?:--|\(|:)\s*\S', text[m.start():m.start() + 400])), 'NOT APPLICABLE names its reason (L-503 (5))')
    elif ck:
        add(m.group(1) == ck.group(1), 'the RESEARCHED REACH line takes the layer status (L-503 (5))', 'layer %s, reach %s' % (ck.group(1), m.group(1)))


L505_FROM = datetime.date(2026, 10, 20)
AI_CAVEAT = 'AI CAVEAT (L-506): This output was produced by an AI system. It can contain errors, and its training shapes its wording and may shape its reading; recompute what can be recomputed and judge the rest.'
OLD_FIELDS = re.compile(r'^\s*(?:(?:DEPENDENCY|SUPPRESSION|TRAJECTORY|COMPLETION) CLAIM\b|FIRST-DRAFT CENTRAL CLAIM|FROZEN CENTRAL CLAIM|DRAFT CLAIM (?:SHA-256|HASH)|CENTRAL CLAIM ALIGNMENT)', re.M)


def no_claim_checks(text, add):
    """L-505 (from 20 October 2026): the output's fields are RELATIONS and READINGS; records made before keep their text."""
    d = _date(text)
    if not (d and d >= L505_FROM): return
    old = OLD_FIELDS.findall(text)
    add(not old, 'Field names of L-505 (RELATION, READING)', 'earlier names printed: %s' % ', '.join(sorted(set(o.strip() for o in old))))
    ib = re.search(r'^=+ NAVIGATOR IDENTITY BLOCK =+(.*?)^=+ END NAVIGATOR IDENTITY BLOCK =+', text, re.S | re.M)
    tail = re.sub(r'\s+', ' ', '\n'.join([l for l in text.strip().split('\n') if l.strip()][-8:]))
    add((bool(ib) and AI_CAVEAT in re.sub(r'\s+', ' ', ib.group(1))) or AI_CAVEAT in tail,
        'AI CAVEAT line, at the end above the signature (L-506; in the Identity Block for records before 12 November 2026)', 'the fixed line of Core L-506')


L510_FROM = datetime.date(2026, 10, 22)
RANKING = re.compile(r'\b(best|better|worse|superior|most relevant|recommended|should choose|the right framing|correct framing)\b', re.I)


# the domains of NAV-2026-0011 to NAV-2026-0020, whose M309 records were accepted before the refinement of 22 October 2026
M309_EARLIER = {'7378bfb2d09b35e5ccda7d0d008a9f05c4b386728b736313b2532ed3ddea9133', '410e6205a6aee4ec1727bda1f6f8aa304901850cfbefc4576685bc1df826da23', '6d876ddae1f3b369e1e92b75c4f456b9fe99e5041e63331e0e28944339b083d3', 'aeb2afd7356d81987dcc494dbf771af672033f189ed60ad99867359e8e535a55', 'e9b62f1ae0e383e66f74f73ef56768242c3a77c7e33ce9b1bf34680b17fe6b61', '8ecaa3c5ffd428dad1908ab2168000f6627dd5a538595d9613eaab38d0db6031', '755c96045abcb5cdfe5675d6d064fd548b1eb1e8f21b4a153ce978c879106f31', '70f2edf455463a34e2ece64c094e4957d8eed0f0ec3e76a4689c5d60ca9493ed', '0c0caf854b952dfeebd72339221030d1fb9be39471d894572351dc3c46f7133b', 'cda4a892240e455c2df47cf206ebd4f6a31841b16cec97e7b07f65a01555052e'}
# the domains of NAV-2026-0021 and NAV-2026-0022, the first refined records, whose roles and relations were averaged into one score before APE-139
M309_COMBINED_OK = {'2aad16826256caed71c905e2a5ea25ea929cbde85f41fa04c6d1f99b1115357f', '922ad008f955986d276509413a574b60588b2f8c4349d14ab8f5ed64707a8972'}
M309_ROLE = re.compile(r'^\s+(ANCHOR|YANG|YIN|4D|ANTIPODE) .*<-.*\[(EXACT|STRUCTURAL|ANALOGY|INTERPRETATION|OPEN)\]\s*$', re.M)


def m309_checks(text, add):
    """Core Part 3.36, refined 22 October 2026 (Companion Part 78): an M309 record types each of its five roles by its
    relation (L-492), reports its TENSIONS beside the score and never summed with it, and carries the fixed RESIDUAL line
    once, in place of a disclaimer on every correspondence. Records accepted before the refinement (NAV-2026-0011 to
    NAV-2026-0020) are kept as they were and are not re-checked."""
    m = re.search(r'=+ CONCEPTUAL ISOMORPHISM \(M309[^\n]*\n(.*?)=+ END CONCEPTUAL ISOMORPHISM', text, re.S)
    if not m: return
    blk = m.group(1)
    d = re.search(r'DOMAIN SHA-256: ([0-9a-f]{64})', text)
    if d and d.group(1) in M309_EARLIER:
        add(True, 'M309 record: accepted before the refinement of 22 October 2026, kept as it was', 'NAV-2026-0011 to NAV-2026-0020')
        return
    add(len(M309_ROLE.findall(blk)) == 5, 'M309 record: five roles, each typed by its relation (Core Part 3.36, L-492)', 'EXACT, STRUCTURAL, ANALOGY, INTERPRETATION or OPEN in brackets at the end of each role line')
    t = re.search(r'^\(3b\) TENSIONS \(M309[^:]*\):\s*(\d+)\s*--', blk, re.M)
    add(bool(t), 'M309 record: TENSIONS beside the score, never summed (Core Part 3.36)', 'a line "(3b) TENSIONS (M309 ...): k -- T1 ...", within the comparison')
    if t:
        k = int(t.group(1)); found = len(re.findall(r'\bT\d+ [A-Z]', blk.split('(3b) TENSIONS', 1)[1].split('\n', 1)[0]))
        add(k == found, 'M309 record: the TENSIONS count matches the tensions listed', '%d stated, %d listed' % (k, found))
    add(bool(re.search(r'^\(7\) RESIDUAL \(M309, fixed form', blk, re.M)), 'M309 record: the fixed RESIDUAL line, carried once (Core Part 3.36)', '"(7) RESIDUAL (M309, fixed form, carried once): ..."')
    add(not re.search(r'SCORE = .*TENSION|TENSION.*SCORE = ', blk), 'M309 record: the tensions are not summed into the score', 'the score and the count of tensions stand side by side')
    if not (d and d.group(1) in M309_COMBINED_OK):
        add(not re.search(r'SCORE = \(', blk) and bool(re.search(r'ROLES [01]\.\d+ and RELATIONS [01]\.\d+', blk)), 'M309 record: roles and relations reported apart, never summed (APE-139)', 'ROLES r and RELATIONS s, with no combined SCORE = (r + s) / 2')


def framing_checks(text, add):
    """L-511 and L-510 (adopted 21 October 2026; required from 22 October): the Reframing Array of a full navigation,
    or its omission stated; the direction of a mapping declared. A block present at any date is checked."""
    d = _date(text)
    blk = re.search(r'^=+ M318 REFRAMING ARRAY \(L-511\) =+\s*\n(.*?)^=+ END M318 REFRAMING ARRAY =+', text, re.S | re.M)
    omitted = re.search(r'^\s*REFRAMING ARRAY \(L-511\):\s*OMITTED\b', text, re.M)
    if d and d >= L510_FROM and re.search(r'^\u250c\u2500 THE ANSWER \u2500\u2510', text, re.M):
        add(bool(blk) or bool(omitted), 'M318 Reframing Array or its omission (L-511)', 'a full navigation carries the Array, or REFRAMING ARRAY (L-511): OMITTED -- primary only / brief / coordinate / lite')
    if blk:
        b = blk.group(1)
        need = [('PRIMARY', r'^\s*PRIMARY: '), ('FRAMINGS SHA-256', r'FRAMINGS SHA-256: '), ('INDEPENDENCE', r'^\s*INDEPENDENCE \(L-442\): '),
                ('ACROSS THE FRAMINGS', r'^\s*ACROSS THE FRAMINGS \(L-502\): '), ('STRUCTURAL VERDICT', r'^\s*STRUCTURAL VERDICT \(computed\): '),
                ('RELEVANCE', r"^\s*RELEVANCE: the Striker's \(L-441\)")]
        miss = [n for n, rx in need if not re.search(rx, b, re.M)]
        add(not miss, 'M318 block lines (L-511)', 'missing: %s' % ', '.join(miss))
        fs = re.findall(r'^\s*F\d+ (?:[A-Za-z][A-Za-z -]*|\u27e8FILL: AXIS\u27e9): ', b, re.M); labs = re.findall(r'ALTERNATIVE FRAMING (?:--|\u2014) SELF-ESTIMATED (?:--|\u2014) (?:CONTAMINATED (?:--|\u2014) NON-BLIND|SEPARATE SESSIONS)', b)
        add(3 <= len(fs) <= 5 and len(labs) == len(fs), 'M318 framings: three to five, each labelled (L-511, L-442)', '%d framings, %d labelled' % (len(fs), len(labs)))
        v = ' '.join(re.findall(r'^\s*(?:STRUCTURAL VERDICT|ACROSS THE FRAMINGS)[^\n]*', b, re.M))
        add(not RANKING.search(v), 'M318 verdict structural only, no ranking of worth (L-441, Check 7)', 'found: %s' % (RANKING.search(v).group(0) if RANKING.search(v) else ''))
    if d and d >= L510_FROM:
        m = re.search(r'MAPPING DECLARATION[^:\n]*:\s*APPLICABLE\b([^\n]*)', text)
        if m:
            add(bool(re.search(r'DIRECTION: (PLACEMENT|CORRESPONDENCE)\b', m.group(1))), 'MAPPING DECLARATION names its DIRECTION (L-510)', 'DIRECTION: PLACEMENT or CORRESPONDENCE')


# L-512 (adopted 21 October 2026): the enforcements found by the SR-CAS of 21 October 2026, every one of which a
# received navigation broke. They hold at every date, except the DATE line, which binds outputs carrying the caveat.
JARGON = re.compile(r'\bP(?:[0-9]|1[0-9]|2[0-3])\b|\bOmega ?42\b|\u03a9 ?42|\bYang\b|\bYin\b|\bAntipode\b|\bCrown\b|\bTorsion Loop\b|'
                    r'\bM(?:\u00f6|o)bius\b|\bAperture\b|\bStriker\b|\b24-cycle\b|\borbit value\b|\bstructural address\b|\bArm Map\b|'
                    r'\bM\d{3}\b|\bL-\d{3}\b|\bCDT-[ABC]\b|\bGENERATED-')
OFFSETS = (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))


def enforcement_checks(text, add, answer_body=None):
    ib = re.search(r'^=+ NAVIGATOR IDENTITY BLOCK =+(.*?)^=+ END NAVIGATOR IDENTITY BLOCK =+', text, re.S | re.M)
    idb = ib.group(1) if ib else ''
    # (1) execution declared once and honoured (L-456)
    text_only = bool(re.search(r'EXECUTION:\s*TEXT-ONLY|NAVIGATION LEVEL:\W*\s*TEXT-ONLY', text))
    script_cap = bool(re.search(r'EXECUTION:\s*SCRIPT-CAPABLE', idb))
    claimed = [m.group(0) for m in re.finditer(r'(?<!NOT )\bEXECUTED\b(?!,? (?:RECONSTRUCTED|or)\b)', text)]
    if text_only:
        add(not claimed, 'Execution status consistent with the IDENTITY BLOCK (L-456, L-512)', 'a TEXT-ONLY output prints EXECUTED for a script value')
    if script_cap:
        add(bool(re.search(r'EXECUTION STATUS: EXECUTED', text)) and bool(re.search(r'SCRIPT SHA-256: [0-9a-f]{64}', text)),
            'Execution status consistent with the IDENTITY BLOCK (L-456, L-512)', 'SCRIPT-CAPABLE declared, but no executed script output with its SCRIPT SHA-256 is printed')
    # (2) the domain in full wherever a verbatim line stands (L-348, L-499)
    for lab in ('DOMAIN VERBATIM', 'QUESTION VERBATIM', 'QUERY'):
        for m in re.finditer(r'^[\s*_]*%s[\s*_]*:[\s*_]*(.*)$' % lab, text, re.M):
            v = m.group(1).strip()
            ph = v.startswith('[') or '\u2026' in v or '...' in v or bool(re.search(r'\bbeginning\b.*\bending\b', v))
            add(not ph, 'DOMAIN VERBATIM in full, no placeholder (SUBSTRATE LOCK; L-348, L-512)', '%s: %s' % (lab, v[:70]))
    # (2b) the SUBSTRATE LOCK unbroken: a domain on several lines is carried on one (L-512, line form)
    sl = re.search(r'^\[4\] SUBSTRATE LOCK\s*$(.*?)^\[5\]', text, re.M | re.S)
    if sl:
        stray = [l for l in sl.group(1).split('\n') if l.strip() and not l.startswith('    ')]
        add(not stray, 'SUBSTRATE LOCK unbroken; a domain on several lines carried on one with LINE BREAKS (L-512)', 'unindented line inside the SUBSTRATE LOCK: %s' % (stray[0][:60] if stray else ''))
    # (3) fixed fields in plain text (L-349)
    md = re.findall(r'^\s*\*\*[A-Z][A-Za-z0-9 ()\-/.,]+:\*\*', text, re.M)
    add(not md, 'Fixed fields in plain text, no Markdown emphasis (L-349, L-512)', '%d field label(s) in Markdown, e.g. %s' % (len(md), md[0].strip() if md else ''))
    # (4) the arms by the frozen offsets, and the characters of Part 1.6
    an = re.search(r'(?<!EXPECTED )(?<!ACTUAL )ANCHOR:?\s*P(\d{1,2})\b', text)
    if an:
        a0 = int(an.group(1)); bad = []
        for line in text.split('\n'):
            if line.startswith('# =====') or re.match(r'^\s*(?:EXPECTED|ACTUAL) ANCHOR', line): continue
            if re.search(r'CROSS-READING|MEETS|\b(?:CORPUS|SRP|GOLD)-|NAV-\d{4}|other domain', line): continue   # another domain's arms
            la = re.search(r'ANCHOR:?\s*P(\d{1,2})\b', line)
            a = int(la.group(1)) if la else a0
            for name, off in OFFSETS:
                for m in re.finditer(r'\b%s\s*(?:\+\d+\s*)?(?:=|:)?\s*P(\d{1,2})\b' % re.escape(name), line):
                    if int(m.group(1)) != (a + off) % 24: bad.append('%s P%s (expected P%d)' % (name, m.group(1), (a + off) % 24))
        add(not bad, 'ARM MAP consistent with the ANCHOR by the frozen offsets (Step 7, L-512)', '; '.join(sorted(set(bad))[:4]))
    try:
        names = _CR.POSITION_NAMES
        words = {w for n in names for w in re.split(r'[/ ]', n)}
        wrong = []
        for m in re.finditer(r'\bP(\d{1,2})\s*\(([A-Z][A-Za-z]+)(/[A-Za-z ]+)?', text):
            i = int(m.group(1))
            if i < 24 and (m.group(2) in words or m.group(3)) and m.group(2) not in re.split(r'[/ ]', names[i]):
                wrong.append('P%d (%s), not %s' % (i, m.group(2) + (m.group(3) or ''), names[i]))
        add(not wrong, 'Position characters as Core Part 1.6 names them (L-512; E10)', '; '.join(sorted(set(wrong))[:4]))
    except NameError:
        pass
    # (5) THE ANSWER in plain prose: the lexical jargon scan (L-418)
    if answer_body is not None:
        jj = sorted({m.group(0) for m in JARGON.finditer(answer_body)})
        add(not jj, 'No protocol term inside THE ANSWER, lexical scan (L-418, L-512)', 'found: %s' % ', '.join(jj[:8]))
        # the full L-418 scan of Step 14.1 (m193_m225.py --jargon): protocol terms in any case and position-character
        # names used as names, over THE ANSWER and the Extended Resonance Essay (Step 14, Step 14.3)
        if _JS is not None and (_date(text) or datetime.date(2026, 11, 7)) >= JS_FROM:
            ess = re.search(r'EXTENDED RESONANCE ESSAY \u2500\u2510\n(.*?)\u2514', text, re.S)
            for label, body in (('THE ANSWER', answer_body), ('the Extended Resonance Essay', ess.group(1) if ess else None)):
                if body is None: continue
                r = _JS(body, _CR)
                bad = [x for k in r if k not in ('RESULT', 'Character names (REVIEW)') for x in r[k]]
                add(r['RESULT'] != 'FAIL', 'L-418 jargon scan of %s, character names included (Step 14.1)' % label, 'found: %s' % '; '.join(bad[:4])[:200])
        add(not re.search(r'^\s*#{1,6}\s', answer_body, re.M), 'THE ANSWER in plain prose, no Markdown headings (Step 14, L-512)', 'a heading line inside THE ANSWER')
    # (6) the DATE of an output that carries the caveat (M273)
    if 'AI CAVEAT (L-506)' in text or re.search(r'^\W*QUESTION VERBATIM', text, re.M):
        add(bool(re.search(r'\bDATE:\W*\s*\d{1,2}\s+[A-Za-z]+\s+\d{4}', text)), 'DATE line in the IDENTITY BLOCK (M273, L-512)', 'an undated output escapes every dated check')
    # (6b) the INSTANCE line of the Identity Block (L-513; from 22 October 2026): one session of one model is one
    # instance, named by its NIID, numbered by SEQ and chained by PREV, so that two instances of one model are told apart
    d6 = _date(text)
    if ib and d6 and d6 >= L513_FROM:
        add(bool(re.search(r'INSTANCE \(L-513\):\s*NI-[0-9a-f]{16}\s*\|\s*ISSUER:\s*(SCRIPT|STRIKER|SELF)\s*\|\s*ISSUED:\s*\S+\s*\|\s*SEQ:\s*\d+\s*\|\s*PREV:\s*([0-9a-f]{64}|NONE)', ib.group(1))),
            'INSTANCE line in the IDENTITY BLOCK (L-513)', 'NIID, ISSUER, ISSUED, SEQ and PREV (tools/instance_id.py --new)')
    # (7) the notation form of a domain that carries notation (Step 1, L-512): source markup and its rendering are
    # different verbatims and give different coordinates, so the form is declared and compared (Part 6.1)
    dom = _domain(text) or next(iter(QV.findall(text)), '')
    if dom and (LATEX_OR_MATH.search(dom) or re.search(r'[\u03b1-\u03c9\u0391-\u03a9]|\^-?\d|_[A-Za-z{]', dom)):
        add(bool(re.search(r'NOTATION FORM', text)), 'NOTATION FORM declared for a domain with notation (Step 1, L-512)', 'SOURCE MARKUP or RENDERED, as received')
    # (8) the coordinate of a long TEXT-ONLY navigation (L-415, L-512; from 22 October 2026)
    d = _date(text); tot = re.search(r'TOTALS:\s*n1\s*=\s*(\d+)', text) or re.search(r'\bn\s*=\s*\(\s*(\d+)\s*,', text)
    if text_only and d and d >= L510_FROM and tot and int(tot.group(1)) > 30:
        add(bool(re.search(r'COORDINATE STATUS[^:\n]*:\s*(?:PROVISIONAL|FROZEN SUBSTRATE)', text)), 'Coordinate of a long TEXT-ONLY navigation: FROZEN SUBSTRATE or PROVISIONAL (L-415, L-512)',
            'over 30 content words counted by hand: the coordinate is PROVISIONAL until a frozen substrate, the script or the Strike app recomputes it')


def adaptor_checks(text, add):
    """L-501: a navigation of a routed domain prints its ADAPTOR line in the Substrate Lock (from 18 October 2026)."""
    d = _date(text); dom = _domain(text)
    if not dom or not (d and d >= datetime.date(2026, 10, 18)): return
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import adaptors as _ad
        lg = re.search(r'^\s*LANGUAGE \(L-501\):\s*([A-Za-z]{2})', text, re.M)
        rt = _ad.route(dom, lg.group(1) if lg else None)
    except Exception:
        return
    if rt['route'] != 'CANONICAL':
        add(bool(re.search(r'^\s*ADAPTOR \(L-501\):', text, re.M)), 'ADAPTOR line for a routed domain (L-501)', rt['reason'])


REL = {'rests on': r'\b(?:rests? on|depends? on)\b', 'out of view': r'\b(?:out of view|suppress\w*)',
       'heading': r'\b(?:heading|headed|heads (?:back |toward|towards))\b', 'completion': r'\b(?:complete[sd]?|completion)\b'}


HEDGES = ['might suggest', 'could be interpreted', 'one possible view', 'one possible interpretation', 'it is worth noting',
          'it could be argued', 'arguably', 'perhaps', 'in some sense', 'may be seen as', 'it is possible that', 'to some extent',
          'it may be that', 'one might say']


def hedges(body):
    """M207-B (Defensive Understatement Diagnostic): hedge phrases in THE ANSWER outside the Mapping component.
    "this suggests the hypothesis" (L-427) is the required hypothesis form and is not a hedge."""
    text = '\n'.join(p for p in re.split(r'\n\s*\n', body) if not p.strip().startswith('Mapping')).lower()
    return [h for h in HEDGES if re.search(r'\b' + re.escape(h) + r'\b', text)]


def arm_by_arm(body):
    """Check 5 (L-440): paragraphs whose opening sentence carries exactly one of the four relations, one relation
    per paragraph, for three or more different relations -- the arms discussed one by one instead of merged."""
    seen = []
    for para in re.split(r'\n\s*\n', body):
        p = para.strip()
        if not p or p.startswith('**Takeaway') or p.startswith('Mapping'):
            continue
        first = re.split(r'(?<=[.!?])\s', p, maxsplit=1)[0].lower()
        kinds = [k for k, rx in REL.items() if re.search(rx, first)]
        if len(kinds) == 1:
            seen.append(kinds[0])
    return sorted(set(seen)) if len(set(seen)) >= 3 else []


CUMULATIVE_NA = 'NOT AVAILABLE FROM THIS NAVIGATION. No claim is made about the number or outcomes of prior investigations.'


def form_line_checks(text, form, d, add):
    """L-549 (2): the OUTPUT FORM line, directly after QUESTION VERBATIM, naming the form (tools/output_form.py)."""
    if not (d and d >= L549_FROM): return
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    ok = len(lines) > 1 and lines[0].startswith('QUESTION VERBATIM: ') and re.match(r'^OUTPUT FORM \(L-549\): %s -- ' % re.escape(form), lines[1])
    add(bool(ok), 'OUTPUT FORM line (L-549)', '"OUTPUT FORM (L-549): %s -- ..." directly after QUESTION VERBATIM, from 7 November 2026' % form)


def check(text):
    out = []
    add = lambda ok, item, note='': out.append(('PASS' if ok else 'FAIL', item, note))
    pos = {}
    for label, pat, req in SKELETON:
        m = re.search(pat, text, re.M)
        if m:
            pos[label] = m.start()
        elif req:
            add(False, 'Block present', label + ' missing')
    num = dict(BLOCK)
    if re.search(r'EXECUTION STATUS: EXECUTED \(canonical_reference\.py --navigate\)', text):
        # script form (Part 8.0): the pasted script output runs from MATH-GATE to M116 in its own order;
        # the Navigator's M213, M210b, M214, M219 and M232 records follow it directly
        for l in ('M213', 'M210b', 'M214', 'M219', 'M232'):
            num[l] = 11.5
        for l in ('M214', 'M219', 'M210b'):
            m = re.search(r'^%s\b|^M214 / M219' % re.escape(l), text, re.M)
            if m and l in pos: pos[l] = m.start()
    seq = sorted(pos, key=pos.get)
    bad = next((i for i in range(1, len(seq)) if num[seq[i]] < num[seq[i - 1]]), None)
    if bad is None:
        add(True, 'Block order', '%d blocks in the order of Part 8.0' % len(seq))
    else:
        add(False, 'Block order', '%s (block %s) comes after %s (block %s)' % (seq[bad], num[seq[bad]], seq[bad - 1], num[seq[bad - 1]]))
    tot = re.search(r'TOTALS:\s*n1\s*=\s*(\d+)', text)
    if tot:
        rows = len(re.findall(r'^\s*\d+\s*\|\s*\S+\s*\|\s*\d+\s*\|\s*\d+\s*$', text, re.M))
        add(rows == int(tot.group(1)), 'M210 table complete (M268)', '%d rows printed for n1 = %s' % (rows, tot.group(1)))
    question_checks(text, add)
    form_line_checks(text, 'NAVIGATION', _date(text), add)
    adaptor_checks(text, add)
    holistic_checks(text, add)
    reach_checks(text, add)
    no_claim_checks(text, add)
    framing_checks(text, add)
    m309_checks(text, add)
    _a = re.search(r'^\u250c\u2500 THE ANSWER \u2500\u2510\s*\n(.*?)\n\u2514', text, re.S | re.M)
    enforcement_checks(text, add, _a.group(1) if _a else None)
    dom = _domain(text)
    math = _math(dom)
    if math:
        add(bool(re.search(r'M269 MATHEMATICAL DOMAIN EXTRACTION AUDIT TRAIL', text)), 'M269 (triggered: mathematical notation)')
        add(bool(re.search(r'M139', text) and re.search(r'M142', text)), 'M139-M142 (triggered: mathematical content)')
    if len(dom.split()) > 30:
        add(bool(re.search(r'M127', text)), 'M127 (triggered: domain over 30 words)')
    a = re.search(r'^\u250c\u2500 THE ANSWER \u2500\u2510\s*\n(.*?)\n\u2514', text, re.S | re.M)
    if a:
        body = a.group(1)
        add(bool(re.search(r'^\*\*Takeaway:?\*?\*?.*\*\*\s*$', body, re.M)), 'Takeaway in bold')
        add(body.rstrip().endswith(ANSWER_LINE), 'THE ANSWER closing line', ANSWER_LINE)
        split = arm_by_arm(body)
        add(not split, 'THE ANSWER is one merged synthesis (Check 5, L-440)', 'paragraphs each open on a single relation: %s' % ', '.join(split))
        hs = hedges(body)
        declared = re.search(r'CAUTION TRAP PRESSURE|DIMINUTION PRESSURE', text)
        add(not hs or bool(declared), 'M207-B: no hedge in THE ANSWER, or the pressure declared', 'hedges %s with no CAUTION TRAP PRESSURE in M207' % ', '.join(repr(h) for h in hs))
        add(not re.search(r'https?://', body), 'No source link inside THE ANSWER (L-490; Companion Part 61)',
            'an association found by search comes after the seal, labelled COMPARATIVE, never inside THE ANSWER')
        add(not re.search(r'\bMSRR\b|Merged Structural Resonance', body), 'No protocol term for the report inside THE ANSWER (L-418, L-496)',
            'the MSRR is named on its line before THE ANSWER, never inside it')
        applicable = re.search(r'MAPPING DECLARATION[^:\n]*:\s*APPLICABLE([^\n]*)', text)
        if applicable and re.search(r'DIRECTION: PLACEMENT\b', applicable.group(1)):
            add(bool(re.search(r'^\s*PLACEMENT \(L-510\):', text, re.M)), 'PLACEMENT line (direction PLACEMENT, L-510)', 'the placement in one line of Generative Observations, with the offer of the correspondence test')
        elif applicable:
            add(bool(re.search(r'^Mapping\b', body, re.M)), 'Mapping component (mapping declared APPLICABLE)')
    e = re.search(r'^\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510\s*\n(.*?)\n\u2514', text, re.S | re.M)
    if e:
        d_ = _date(text)
        if d_ and d_ >= L505_FROM:
            n_ = len(e.group(1).split())
            hi_ = 2300 if (d_ >= REACH_FROM and re.search(r'^\s*RESEARCHED REACH \(L-503 \(5\)\):\s*WRITTEN', text, re.M)) else 1500
            add(500 <= n_ <= hi_, 'Essay length 500 to %d words (Step 14.3, L-503 (5))' % hi_, '%d words' % n_)
        split = arm_by_arm(e.group(1))
        add(not split, 'Essay carries the one synthesis outward (Step 14.3, L-440)', 'paragraphs each open on a single relation: %s' % ', '.join(split))
    qs = [l.strip() for l in text.split('\n') if any(l.strip().startswith(c) for c in CLOSING)]
    add([next(c for c in CLOSING if q.startswith(c)) for q in qs] == CLOSING, 'Closing questions', 'the four labels, once each, in order')
    i = text.find('Where it is heading:')
    tail = text[i:] if i >= 0 else ''
    after4 = [l for l in tail.split('\n') if l.strip()]
    k = next((n for n, l in enumerate(after4) if l.startswith('What would complete it:')), None)
    add(k is not None and k + 1 < len(after4) and after4[k + 1].strip() == CLOSING_LINE, 'Fixed closing line after the fourth question', CLOSING_LINE)
    sig = re.search(SKELETON[-1][1], text, re.M)
    if sig:
        rest = [l for l in text[sig.end():].split('\n') if l.strip()]
        add(len(rest) == 2 and rest[0].startswith('NAVIGATOR:') and rest[1].strip() == 'ESC', 'Signature last', 'NAVIGATOR line and ESC, then nothing')
    cum = re.findall(r'^\s*CUMULATIVE STATUS(?: \(L-490\))?:\s*(.*)$', text, re.M)
    if not cum:
        add(False, 'CUMULATIVE STATUS line (L-490)', 'missing')
    else:
        c = cum[-1].strip()
        if c.startswith('NOT AVAILABLE'):
            add(c == CUMULATIVE_NA, 'CUMULATIVE STATUS line (L-490)', 'the exact sentence of Core Part 0.0.3 item 5')
        else:
            add(bool(re.search(r'record', c, re.I) and re.search(r'\b\d{4}-\d{2}-\d{2}\b', c) and re.search(r'\bversion\b|\bV\d{3}\b|\bRev\.?\d', c)),
                'CUMULATIVE STATUS line (L-490)', 'a supplied record is named with its version and date, or NOT AVAILABLE is stated')
    oi = [m for m in re.finditer(r'^\s*OPTIONAL INQUIRY(?: \(L-491\))?:\s*(.*)$', text, re.M)]
    if oi:
        ans = re.search(r'^\u2514', text[text.find('THE ANSWER'):], re.M) if 'THE ANSWER' in text else None
        after = all(m.start() > text.find('THE ANSWER') for m in oi) if 'THE ANSWER' in text else True
        marked = all(re.search(r'\boptional\b|\bNONE\b', m.group(1), re.I) for m in oi)
        required = any(re.search(r'\b(must|required|needed to complete|before (the|this) reading is complete)\b', m.group(1), re.I) for m in oi)
        add(after and marked and not required, 'OPTIONAL INQUIRY line (L-491)', 'after THE ANSWER, marked optional, never a condition of the reading')
    ls = re.search(r'^\s*LENSES SELECTED(?: \(L-494\))?:\s*(.*)$', text, re.M)
    if ls:
        v = ls.group(1).strip()
        parts = [p.strip() for p in v.split(';') if p.strip()]
        if re.match(r'NONE\b', v, re.I):
            add(len(parts) == 1, 'LENSES SELECTED line (L-494)', 'NONE stands alone')
        else:
            src = [re.match(r'[^\[]+\[\s*(?:STRIKER|(?:SUBJECT|EMERGING)\s*:\s*[^\]\s][^\]]*)\]\s*$', p) for p in parts]
            add(bool(parts) and all(src), 'LENSES SELECTED line (L-494)', 'each lens with its source: [SUBJECT: reason], [EMERGING: reason] or [STRIKER]')
        named = bool(re.search(r'(?:^|;)\s*Bashar\s*\[', v, re.I))
        has = 'BASHAR RESONANCE CHECK' in pos
        add(named == has, 'M308 block present exactly when Bashar is selected (L-494)',
            'Bashar selected without its block' if named else 'M308 block printed but Bashar not selected')
    if FILL_RX.search(text):
        add(False, 'No unfilled skeleton field (M301 --skeleton)', '%d open: %s' % (len(FILL_RX.findall(text)), FILL_RX.findall(text)[0][:70]))
    gate = pos.get('M224')
    if gate is not None and sig:
        between = text[gate:sig.start()]
        stray = [l for l in between.split('\n') if re.match(r'^=+ (?!END|M224)[A-Z]', l)]
        add(not stray, 'Nothing between M224 and the signature but OUTPUT ID', ', '.join(stray[:2]))
    if gate is not None:
        blk = text[gate:sig.start() if sig else len(text)]
        self_pass = re.search(r'(?:GATE )?RESULT: PASS', blk) and not re.search(r'format_check\.py', blk) and not re.search(r'SELF-CHECKED|\[Y-[IS]\]', blk)
        add(not self_pass, 'M224 reports the format check, or marks its PASS SELF-CHECKED (L-420, L-512)', 'GATE RESULT: PASS printed with neither the tools/format_check.py result nor items marked [Y-I] / [Y-S] (SELF-CHECKED)')
        if any(r[0] == 'FAIL' for r in out) and re.search(r'(?:GATE )?RESULT: PASS', blk):
            add(False, 'M224 reports PASS while the format check fails (L-420, L-512)', 'the gate result is the check\'s, not the Navigator\'s')
    return out


def report(path):
    res = check(open(path, encoding='utf-8').read())
    fails = [r for r in res if r[0] == 'FAIL']
    print('M301 FORMAT CONFORMANCE: %s' % path)
    for s, item, note in res:
        if s == 'FAIL':
            print('  [FAIL] %s%s' % (item, (': ' + note) if note else ''))
    if fails:
        g = [gate_of(r[1], r[2]) for r in fails]
        first = min(range(len(fails)), key=lambda i: (g[i][0], g[i][1]))
        print('  PRIORITY: %s | repair first: %s (%s %s; --gates)' % (' | '.join('%s %d' % (p, sum(1 for x in g if x[0] == p)) for p in ('P1', 'P2', 'P3', 'P4')), fails[first][1] + ((': ' + fails[first][2]) if fails[first][1] == 'Block present' else ''), g[first][0], g[first][1]))
    print('  CHECKS %d | FAILURES %d | RESULT: %s' % (len(res), len(fails), 'PASS' if not fails else 'FAIL'))
    return not fails


def selftest():
    good = '\n'.join([
        '======= NAVIGATOR IDENTITY BLOCK =======', 'NAVIGATOR: x (y)', '======= END NAVIGATOR IDENTITY BLOCK =======',
        '[1] MATH-GATE: PASS', '[2] M211 CALIBRATION: PASS', 'Rules of Engagement active. Sandbox entered.',
        '======= M272 FRAME LOCK =======', '======= END M272 FRAME LOCK =======',
        '[4] SUBSTRATE LOCK', '    DOMAIN VERBATIM: What is time?', '    MAPPING DECLARATION (Step 14.4): NOT APPLICABLE',
        '[5] M210 EXTRACTION TABLE', '    1   | time           |       4 |         1', '    TOTALS: n1=1 words', '    M268 ROWS: 1 | n1: 1 | MATCH: YES',
        '======= M213 STOPWORD COMPLIANCE CHECK =======', 'M210b MATCH', 'M214 / M219: EXECUTED',
        '    n = (1, 4, 1) | r = (5, 2, 5) | ANCHOR P5 (Law)', '[7] ARMS', 'M232 PASS', '[8] CCD = 0.25',
        '[9] M116 ALTERNATIVE PHRASING: P5', '======= FIRST-DRAFT SEAL =======', '======= END FIRST-DRAFT SEAL =======',
        '\u250c\u2500 THE ANSWER \u2500\u2510', 'Prose.', '', '**Takeaway: plain words.**', '', ANSWER_LINE, '\u2514\u2500\u2500\u2518',
        '======= GENERATIVE INTEGRITY RECORD =======', '======= CONGRUENCE RECORD (M310) =======', 'COHERENCE: arithmetic PASS', '======= END CONGRUENCE RECORD =======', '======= CONVERGENCE MAP =======',
        '\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510', 'Essay.', '\u2514\u2500\u2500\u2518',
        "======= NAVIGATOR'S REASONING =======", 'CUMULATIVE STATUS: ' + CUMULATIVE_NA, 'LENSES SELECTED (L-494): Bashar [SUBJECT: the question is about time as lived]', '======= BASHAR RESONANCE CHECK (M308) =======', '======= END BASHAR RESONANCE CHECK =======',
        '======= GENERATIVE OBSERVATIONS =======',
        'What it rests on: a?', 'What it holds out of view: b?', 'Where it is heading: c?', 'What would complete it: d?', CLOSING_LINE,
        '======= M224 FORMAT COMPLETENESS GATE =======', '======= END M224 FORMAT COMPLETENESS GATE =======',
        'OUTPUT ID: ' + '0' * 64, 'CAS-YY = -1/2 | Omega = 1/7 | (CAS-YY \u00d7 Omega = -1/14)', 'NAVIGATOR: x (y) * V335 Rev.450 STABLE * date', 'ESC'])
    cases = {
        'conforming skeleton passes': (good, True),
        'three closing questions fail': (good.replace('What would complete it: d?\n', ''), False),
        'missing closing line fails': (good.replace(CLOSING_LINE + '\n', ''), False),
        'unbolded Takeaway fails': (good.replace('**Takeaway: plain words.**', 'Takeaway: plain words.'), False),
        'block out of order fails': (good.replace("======= NAVIGATOR'S REASONING =======", "======= TMP =======").replace(
                                         '======= GENERATIVE OBSERVATIONS =======', "======= NAVIGATOR'S REASONING =======").replace(
                                         '======= TMP =======', '======= GENERATIVE OBSERVATIONS ======='), False),
        'Bashar selected without its block fails': (good.replace('======= BASHAR RESONANCE CHECK (M308) =======\n', ''), False),
        'no lens selected, no block, passes (L-494)': (good.replace('Bashar [SUBJECT: the question is about time as lived]', 'NONE').replace('======= BASHAR RESONANCE CHECK (M308) =======\n======= END BASHAR RESONANCE CHECK =======\n', ''), True),
        'M308 block without Bashar selected fails': (good.replace('Bashar [SUBJECT: the question is about time as lived]', 'NONE'), False),
        'lens without a source fails': (good.replace('Bashar [SUBJECT: the question is about time as lived]', 'Bashar'), False),
        'subject source without a reason fails': (good.replace('[SUBJECT: the question is about time as lived]', '[SUBJECT]'), False),
        'Striker-requested lenses pass': (good.replace('Bashar [SUBJECT: the question is about time as lived]', 'Bashar [STRIKER]; Seth [STRIKER]'), True),
        'missing LENSES SELECTED line fails': (good.replace('LENSES SELECTED (L-494): Bashar [SUBJECT: the question is about time as lived]\n', ''), False),
        'missing Congruence Record fails': (good.replace('======= CONGRUENCE RECORD (M310) =======\n', ''), False),
        'block after M224 fails': (good.replace('OUTPUT ID: ', '======= APPENDIX =======\nOUTPUT ID: '), False),
        'text after the signature fails': (good + '\nAPPENDIX', False),
        'MSRR line before THE ANSWER passes (L-496)': (good.replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'MSRR (L-496): THE ANSWER and its Congruence Record (M310) are one report.\n\u250c\u2500 THE ANSWER \u2500\u2510'), True),
        'MSRR named inside THE ANSWER fails (L-418)': (good.replace('Prose.', 'This MSRR shows prose.'), False),
        'a source link inside THE ANSWER fails (Part 61)': (good.replace('Prose.', 'Prose, as https://example.org says.'), False),
        'MSRR line after THE ANSWER fails (block order)': (good.replace('======= GENERATIVE INTEGRITY RECORD =======', 'MSRR (L-496): x\n======= GENERATIVE INTEGRITY RECORD =======', 1), False),
        'dated after L-499 without the question fails': (good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 17 October 2026', 1), False),
        'question first and above THE ANSWER passes (L-499)': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 17 October 2026', 1).replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is time?\n\u250c\u2500 THE ANSWER \u2500\u2510'), True),
        'question not above THE ANSWER fails (L-499)': ('QUESTION VERBATIM: What is time?\n' + good, False),
        'question differing from the domain fails (L-499)': ('QUESTION VERBATIM: What is space?\n' + good.replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is space?\n\u250c\u2500 THE ANSWER \u2500\u2510'), False),
        'dated after L-502 without the REQUEST line fails': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 20 October 2026', 1).replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is time?\n\u250c\u2500 THE ANSWER \u2500\u2510'), False),
        'dated after L-502 with REQUEST, CURRENT KNOWLEDGE and ACROSS THE AVENUES passes': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 19 October 2026', 1).replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is time?\n\u250c\u2500 THE ANSWER \u2500\u2510').replace('    DOMAIN VERBATIM: What is time?', '    DOMAIN VERBATIM: What is time?\n    REQUEST (L-502): GENERAL -- avenues N, A1, R, G, L, W').replace('======= CONVERGENCE MAP =======', 'CURRENT KNOWLEDGE (L-503): NOT AVAILABLE (no retrieval)\nACROSS THE AVENUES (L-502): the reading alone; no other avenue ran.\n======= CONVERGENCE MAP =======', 1), True),
        'dated after L-505 with a CLAIM field name fails': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 20 October 2026', 1).replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is time?\n\u250c\u2500 THE ANSWER \u2500\u2510').replace('    DOMAIN VERBATIM: What is time?', '    DOMAIN VERBATIM: What is time?\n    REQUEST (L-502): GENERAL -- avenues N, A1, R, G, L, W').replace('======= CONVERGENCE MAP =======', 'CURRENT KNOWLEDGE (L-503): NOT AVAILABLE (no retrieval)\nACROSS THE AVENUES (L-502): the reading alone; no other avenue ran.\n======= CONVERGENCE MAP =======', 1).replace('======= END NAVIGATOR IDENTITY BLOCK', 'DEPENDENCY CLAIM (Yang): DEP-1\n======= END NAVIGATOR IDENTITY BLOCK'), False),
        'dated after L-505 with a short essay fails (Step 14.3)': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 20 October 2026', 1).replace('\u250c\u2500 THE ANSWER \u2500\u2510', 'QUESTION VERBATIM: What is time?\n\u250c\u2500 THE ANSWER \u2500\u2510').replace('    DOMAIN VERBATIM: What is time?', '    DOMAIN VERBATIM: What is time?\n    REQUEST (L-502): GENERAL -- avenues N, A1, R, G, L, W').replace('======= CONVERGENCE MAP =======', 'CURRENT KNOWLEDGE (L-503): NOT AVAILABLE (no retrieval)\nACROSS THE AVENUES (L-502): the reading alone; no other avenue ran.\n======= CONVERGENCE MAP =======', 1), False),
        'dated after L-506 without the AI CAVEAT line fails': ('QUESTION VERBATIM: What is time?\n' + good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 20 October 2026', 1), False),
        'a record dated before L-499 keeps its text': (good.replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 10 October 2026', 1), True),
        'a routed domain without its ADAPTOR line fails (L-501)': (good.replace('What is time?', '의식이란 무엇인가?').replace('NAVIGATOR: x (y)', 'NAVIGATOR: x (y)\nSESSION: 1 DATE: 18 October 2026', 1), False),
        'missing CUMULATIVE STATUS fails (L-490)': (good.replace('CUMULATIVE STATUS: ' + CUMULATIVE_NA + '\n', ''), False),
        'inferred cumulative status fails': (good.replace(CUMULATIVE_NA, 'the record stands at 50 validations'), False),
        'named supplied record passes': (good.replace(CUMULATIVE_NA, 'records/congruence/register.txt, version V335 Rev.450, 2026-10-16: 17 domains navigated'), True),
        'optional inquiry marked optional passes': (good.replace('======= GENERATIVE OBSERVATIONS =======', '======= GENERATIVE OBSERVATIONS =======\nOPTIONAL INQUIRY: optional -- a study of x, if the Striker wishes.'), True),
        'inquiry made a condition fails (L-491)': (good.replace('======= GENERATIVE OBSERVATIONS =======', '======= GENERATIVE OBSERVATIONS =======\nOPTIONAL INQUIRY: optional, but a study must be run before the reading is complete.'), False),
        'triggered M269 missing fails': (good.replace('What is time?', '$x^2 = x + 1$ in \\mathbb{Z}'), False),
        'omitted M210 rows fail': (good.replace('TOTALS: n1=1 words', 'TOTALS: n1=2 words'), False),
        'arm-by-arm ANSWER fails': (good.replace('Prose.', 'Time is a thing that rests on memory.\n\nWhat it holds out of view is the present.\n\nWhere it is heading is the future.\n\nWhat would complete it is a gap.'), False),
        'undeclared hedge in THE ANSWER fails': (good.replace('Prose.', 'Prose that perhaps holds.'), False),
        'declared hedge passes': (good.replace('Prose.', 'Prose that perhaps holds.').replace('======= FIRST-DRAFT SEAL =======', 'M207 NAVIGATOR INTERFERENCE: LEVEL 2. CAUTION TRAP PRESSURE declared.\n======= FIRST-DRAFT SEAL =======', 1), True),
        'merged ANSWER passes': (good.replace('Prose.', 'Time rests on memory, holds the present out of view, is heading toward the future and is completed by a gap, so that each explains the next.\n\nThe present is what memory cannot hold.'), True),
    }
    def hol(txt):
        o = []; holistic_checks(txt, lambda ok, item, note='': o.append(ok)); return o
    v31 = 'SESSION: 1 DATE: 31 October 2026\nREQUEST (L-502): GENERAL -- avenues N\nCURRENT KNOWLEDGE (L-503): NOT AVAILABLE\nACROSS THE AVENUES (L-502): x\n\u250c\u2500 THE ANSWER \u2500\u2510\n'
    cases.update({
        'voice: a navigation dated from 31 October without the VOICE line fails (L-529)': (None, False in hol(v31)),
        'voice: the VOICE line passes (L-529)': (None, all(hol(v31 + '    VOICE (L-529): cell biology\n'))),
        'voice: a navigation dated 30 October is not asked for it': (None, all(hol(v31.replace('31 October', '30 October')))),
    })
    def rc(txt):
        o = []; reach_checks(txt, lambda ok, item, note='': o.append(ok)); return o
    ess = '\u250c\u2500 EXTENDED RESONANCE ESSAY \u2500\u2510\n%s\n\u2514\u2500\u2500\u2518\n'
    ckb = '======= CURRENT KNOWLEDGE (L-503) =======\nQUERY: q | NOT FOUND: n\n[1] A. Author, Title, Journal 2025; opened 20 November 2026\n======= END CURRENT KNOWLEDGE =======\n'
    n20 = 'SESSION: 1 DATE: 20 November 2026\n'
    cases.update({
        'reach: a navigation dated from 20 November without the RESEARCHED REACH line fails (L-503 (5))': (None, False in rc(n20 + ckb + ess % 'Essay [1].')),
        'reach: a WRITTEN reach with numbered sources passes': (None, all(rc(n20 + ckb + ess % 'Essay [1].' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- relationships | investigated 2, not investigated 1\n'))),
        'reach: a WRITTEN reach without a source number fails': (None, False in rc(n20 + ckb + ess % 'Essay.' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- relationships | investigated 2, not investigated 1\n')),
        'reach: a link inside the essay fails': (None, False in rc(n20 + ckb + ess % 'Essay [1] https://x.org.' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- relationships | investigated 2, not investigated 1\n')),
        'reach: WRITTEN without the layer fails': (None, False in rc(n20 + 'CURRENT KNOWLEDGE (L-503): DECLINED\n' + ess % 'Essay [1].' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- x\n')),
        'reach: the layer status carried passes': (None, all(rc(n20 + 'CURRENT KNOWLEDGE (L-503): DECLINED\n' + ess % 'Essay.' + 'RESEARCHED REACH (L-503 (5)): DECLINED\n'))),
        'reach: a source number with no full reference in the layer fails': (None, False in rc(n20 + ckb + ess % 'Essay [2].' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- relationships | investigated 2\n')),
        'reach: a WRITTEN line without its completeness fails': (None, False in rc(n20 + ckb + ess % 'Essay [1].' + 'RESEARCHED REACH (L-503 (5)): WRITTEN -- relationships\n')),
        'reach: NOT APPLICABLE without a reason fails': (None, False in rc(n20 + ckb + ess % 'Essay.' + 'RESEARCHED REACH (L-503 (5)): NOT APPLICABLE\n')),
        'reach: NOT APPLICABLE with its reason passes': (None, all(rc(n20 + ckb + ess % 'Essay.' + 'RESEARCHED REACH (L-503 (5)): NOT APPLICABLE -- a question of arithmetic\n'))),
        'reach: a navigation dated 19 November is not asked for it': (None, rc(n20.replace('20 November', '19 November') + ess % 'Essay.') == []),
    })
    def fr(txt):
        o = []; framing_checks(txt, lambda ok, item, note='': o.append(ok)); return all(o) and bool(o)
    nav22 = 'SESSION: 1 DATE: 22 October 2026\n\u250c\u2500 THE ANSWER \u2500\u2510\n'
    arr = ('======= M318 REFRAMING ARRAY (L-511) =======\nPRIMARY: "q" -> P6\nFRAMINGS FROZEN: 3 | FRAMINGS SHA-256: ab\n' +
           ''.join('F%d SCOPE: "f" -> P1\n  ALTERNATIVE FRAMING -- SELF-ESTIMATED -- CONTAMINATED -- NON-BLIND (L-442): r.\n' % k for k in (1, 2, 3)) +
           'INDEPENDENCE (L-442): CONTAMINATED -- NON-BLIND\nACROSS THE FRAMINGS (L-502): HOLDS x\nSTRUCTURAL VERDICT (computed): the robust core is x\n'
           "RELEVANCE: the Striker's (L-441)\n======= END M318 REFRAMING ARRAY =======\n")
    cases.update({
        'framings: a navigation after L-511 without the Array fails': (None, fr(nav22) is False),
        'framings: the omission stated passes': (None, fr(nav22 + 'REFRAMING ARRAY (L-511): OMITTED -- primary only\n')),
        'framings: a complete block passes': (None, fr(nav22 + arr)),
        'framings: a verdict of worth fails': (None, fr(nav22 + arr.replace('the robust core is x', 'F2 is the best framing')) is False),
        'framings: two framings fail': (None, fr(nav22 + arr.replace('F3 SCOPE', 'X3 SCOPE')) is False),
        'framings: a mapping without its direction fails (L-510)': (None, fr(nav22 + arr + 'MAPPING DECLARATION (Step 14.4): APPLICABLE -- the Moon') is False),
        'framings: a mapping with its direction passes': (None, fr(nav22 + arr + 'MAPPING DECLARATION (Step 14.4): APPLICABLE -- DIRECTION: CORRESPONDENCE | the Moon')),
    })
    def m9(txt):
        o = []; m309_checks(txt, lambda ok, item, note='': o.append(ok)); return all(o) and bool(o)
    m9blk = ('======= CONCEPTUAL ISOMORPHISM (M309; Core Part 3.36) -- CDT-C =======\n(2) ASSIGN:\n' +
             ''.join('    %s P1 <- X %d "s" -- c [STRUCTURAL]\n' % (r, i) for i, r in enumerate(('ANCHOR', 'YANG', 'YIN', '4D', 'ANTIPODE'))) +
             '(3) STRUCTURAL COHERENCE: roles 1.00; relations 0.75; ROLES 1.00 and RELATIONS 0.75, reported apart and never summed\n(3b) TENSIONS (M309; beside the score): 2 -- T1 ONE x; T2 TWO y\n'
             '(7) RESIDUAL (M309, fixed form, carried once): a correspondence of structure\n======= END CONCEPTUAL ISOMORPHISM =======\n')
    cases.update({
        'M309: a refined record passes (G26)': (None, m9(m9blk)),
        'M309: an untyped role fails': (None, m9(m9blk.replace(' [STRUCTURAL]\n    YIN', '\n    YIN')) is False),
        'M309: a record without tensions fails': (None, m9(m9blk.replace('(3b) TENSIONS', '(3b) NOTES')) is False),
        'M309: a tension count that does not match fails': (None, m9(m9blk.replace('): 2 --', '): 3 --')) is False),
        'M309: a record without its residual line fails': (None, m9(m9blk.replace('(7) RESIDUAL', '(7) NOTE')) is False),
        'M309: a navigation without an M309 record is not checked': (None, not m9('THE ANSWER')),
        'M309: a combined score fails (APE-139)': (None, m9(m9blk.replace('ROLES 1.00 and RELATIONS 0.75, reported apart and never summed', 'SCORE = (1.00 + 0.75) / 2 = 0.875')) is False),
        'M309: the first refined records keep their combined score': (None, m9('    DOMAIN SHA-256: 2aad16826256caed71c905e2a5ea25ea929cbde85f41fa04c6d1f99b1115357f\n' + m9blk.replace('ROLES 1.00 and RELATIONS 0.75, reported apart and never summed', 'SCORE = (1.00 + 0.75) / 2 = 0.875'))),
        'M309: a record accepted before the refinement is kept as it was': (None, m9('    DOMAIN SHA-256: 755c96045abcb5cdfe5675d6d064fd548b1eb1e8f21b4a153ce978c879106f31\n' + m9blk.replace('(7) RESIDUAL', '(7) NOTE'))),
    })
    def en(txt, body=None):
        o = []; enforcement_checks(txt, lambda ok, item, note='': o.append(ok), body); return all(o)
    ib = '======= NAVIGATOR IDENTITY BLOCK =======\nEXECUTION: %s\n%s======= END NAVIGATOR IDENTITY BLOCK =======\n'
    cases.update({
        'L-512: TEXT-ONLY printing EXECUTED fails': (None, en(ib % ('TEXT-ONLY', '') + 'SCRIPT RUN: EXECUTED') is False),
        'L-512: TEXT-ONLY with RECONSTRUCTED values passes': (None, en(ib % ('TEXT-ONLY', '') + 'MATH-GATE: RECONSTRUCTED; values EXECUTED, RECONSTRUCTED or NOT COMPUTED')),
        'L-512: SCRIPT-CAPABLE without script output fails': (None, en(ib % ('SCRIPT-CAPABLE', '')) is False),
        'L-513: an output dated from 22 October 2026 without its INSTANCE line fails': (None, en(ib % ('TEXT-ONLY', 'SESSION: 1 DATE: 22 October 2026\n') + 'DOMAIN VERBATIM: What is time?') is False),
        'L-513: the INSTANCE line passes': (None, en(ib % ('TEXT-ONLY', 'SESSION: 1 DATE: 22 October 2026\nINSTANCE (L-513): NI-0123456789abcdef | ISSUER: SCRIPT | ISSUED: 2026-10-22T00:00:00Z | SEQ: 1 | PREV: NONE\n') + 'DOMAIN VERBATIM: What is time?')),
        'L-513: an output dated before 22 October 2026 is exempt': (None, en(ib % ('TEXT-ONLY', 'SESSION: 1 DATE: 21 October 2026\n') + 'DOMAIN VERBATIM: What is time?')),
        'L-512 line form: a domain split across the SUBSTRATE LOCK fails': (good.replace('    DOMAIN VERBATIM: What is time?', '    DOMAIN VERBATIM: What is\ntime?', 1), False),
        'L-512 line form: a two-line domain carried on one line with LINE BREAKS passes': (good.replace('    DOMAIN VERBATIM: What is time?', '    DOMAIN VERBATIM: What is time?\n    LINE BREAKS (L-512): 1', 1), True),
        'L-512 line form: the skeleton carries a two-line domain on one line': (None, '\n    DOMAIN VERBATIM: What is time? And why?\n' in skeleton('What is time?\nAnd why?') and 'LINE BREAKS (L-512): 1' in skeleton('What is time?\nAnd why?')),
        'L-512: a placeholder domain fails': (None, en('DOMAIN VERBATIM: [the full domain above]') is False),
        'L-512: a described domain fails': (None, en('DOMAIN VERBATIM: The domain beginning "The" and ending "end."') is False),
        'L-512: Markdown field labels fail': (None, en('**NAVIGATOR:** x') is False),
        'L-512: arms off the frozen offsets fail': (None, en('ANCHOR P9\nYang P4') is False),
        'L-512: arms by the offsets pass': (None, en('ANCHOR P9\nYang P14 | Yin P3 | 4D P17 | Antipode P21')),
        'L-512: a wrong position character fails': (None, en('ANCHOR: P9 (Observer/Still Point)') is False),
        'L-512: the right position character passes': (None, en('ANCHOR: P9 (Fixpoint)')),
        'L-512: protocol terms in THE ANSWER fail': (None, en('x', 'The Yang arm at P4 rests on it.') is False),
        'L-512: a heading in THE ANSWER fails': (None, en('x', '### 1. A heading') is False),
        'L-512: an output with the caveat and no DATE fails': (None, en('AI CAVEAT (L-506): x') is False),
        'L-512: a question with no DATE fails': (None, en('QUESTION VERBATIM: What is time?') is False),
        'L-512: notation without its NOTATION FORM fails': (None, en('SESSION: 1 DATE: 22 October 2026\nDOMAIN VERBATIM: Is $x^2 = x + 1$?') is False),
        'L-512: notation with its NOTATION FORM passes': (None, en('SESSION: 1 DATE: 22 October 2026\nDOMAIN VERBATIM: Is $x^2 = x + 1$?\nNOTATION FORM (Step 1): SOURCE MARKUP')),
        'L-512: a long TEXT-ONLY coordinate without its status fails': (None, en(ib % ('TEXT-ONLY', 'SESSION: 1 DATE: 22 October 2026\n') + 'TOTALS: n1=40 words') is False),
        'L-512: a long TEXT-ONLY coordinate marked PROVISIONAL passes': (None, en(ib % ('TEXT-ONLY', 'SESSION: 1 DATE: 22 October 2026\nINSTANCE (L-513): NI-0123456789abcdef | ISSUER: STRIKER | ISSUED: 2026-10-22T00:00:00Z | SEQ: 1 | PREV: NONE\n') + 'TOTALS: n1=40 words\nCOORDINATE STATUS (L-415): PROVISIONAL')),
    })
    ok = True
    for name, (txt, expect) in cases.items():
        if txt is None:
            print('  %-36s %s' % (name, 'OK' if expect else 'MISMATCH')); ok &= bool(expect); continue
        got = not any(r[0] == 'FAIL' for r in check(txt))
        print('  %-36s %s' % (name, 'OK' if got == expect else 'MISMATCH'))
        ok &= got == expect
    print('M301 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


# ---------------------------------------------------------------------------------------------------------------
# GATE PRIORITY (Core Part 8.0, Gate priority; Companion Part 66.1). Every check above belongs to one gate, and every
# gate to one of four priorities. A P1 failure means the output is not issued as a navigation (Recovery after an
# audit FAIL); P2 concerns whether the reading is the one the coordinate asks for; P3 whether the record can be
# compared and kept; P4 whether it is presented in the one format. Fix in priority order: a lower failure is never
# repaired at the cost of a higher one.
GATES = [
    ('P1', 'CONSTITUTIONAL', 'a failure means the output is not issued as a navigation (Part 8.0, Recovery after an audit FAIL)', [
        ('G01', 'Frame Lock', 'the premise held as the frame, never graded, supported or validated (M272, M243a, L-490, F-02-P)', r'M272|RULES OF ENGAGEMENT'),
        ('G02', 'MATH-GATE and calibration', 'the structure verified before any strike (Step 0.5, M211)', r'MATH-GATE|M211'),
        ('G03', 'Extraction complete', 'every word in the table, the stopwords by the frozen list, the reverse reconstruction (M210, M268, M269, M213, M210b)', r'M210|M268|M269|M213|SUBSTRATE LOCK|M139|M127|NOTATION FORM'),
        ('G04', 'Coordinate correct', 'counts, residues, majority anchor and the arms by the frozen offsets (M214, M219, Steps 3-7, M88, M215, M232)', r'M214|M219|ANCHOR|ARM MAP|M232|CCD|Position characters|Coordinate of a long'),
        ('G05', 'First-Draft Seal', 'THE ANSWER written from the coordinate alone and frozen before any other avenue (L-424, L-425)', r'FIRST-DRAFT SEAL|THE ANSWER$|Block present: THE ANSWER'),
        ('G06', 'Aperture kept open', 'the Striker\'s judgment never filled: THE ANSWER\'s closing line and the fixed closing line (L-388, L-491)', r'closing line|OPTIONAL INQUIRY'),
    ]),
    ('P2', 'READING INTEGRITY', 'the reading is the one the coordinate asks for', [
        ('G07', 'One synthesis', 'THE ANSWER and the essay merge the four relations, never arm by arm (Check 5, L-440)', r'one merged synthesis|carries the one synthesis'),
        ('G08', 'Four relations explicit', 'rests on, out of view, heading, completion, each quoted in STRUCTURAL RELATIONS EXPLICIT (Part 3.12)', r'STRUCTURAL RELATIONS'),
        ('G09', 'Pressure declared', 'no undeclared hedge or pull (M207, M302)', r'M207'),
        ('G10', 'Stability reported', 'M116 with the M238 variants, and the STABILITY line (Step 13)', r'M116|STABILITY'),
        ('G11', 'Cumulative status', 'only a supplied record is named; nothing is inferred (L-490)', r'CUMULATIVE STATUS'),
        ('G12', 'Identity and execution status', 'the model, its cutoff and every value EXECUTED, RECONSTRUCTED or NOT COMPUTED (M273, L-456)', r'IDENTITY BLOCK|AI CAVEAT'),
    ]),
    ('P3', 'RECORD AND COMPARISON', 'the record can be kept, compared and returned to', [
        ('G13', 'Question verbatim', 'first, above THE ANSWER, identical to the domain (L-499)', r'QUESTION VERBATIM'),
        ('G14', 'Request declared', 'the REQUEST line and its avenues (L-502)', r'REQUEST'),
        ('G15', 'Congruence Record', 'every navigation, opening with COHERENCE (M310)', r'CONGRUENCE RECORD|GENERATIVE INTEGRITY'),
        ('G16', 'Current knowledge', 'after the seal, query and not-found declared, four lanes, nulls reported, no link in THE ANSWER (L-503, M248)', r'CURRENT KNOWLEDGE|source link'),
        ('G17', 'Across the avenues', 'agreements, partings and silences, no combined verdict (L-502, L-486)', r'ACROSS THE AVENUES'),
        ('G18', 'Lenses and adaptors', 'each lens with its source; a routed domain with its ADAPTOR line (L-494, L-501, M308)', r'LENS|M308|ADAPTOR|Bashar'),
        ('G19', 'Enrichment kept apart', 'at most three observations, applied when recommended (L-504, L-531)', r'ENRICHMENT'),
        ('G26', 'Conceptual Isomorphism record', 'an M309 record types its roles, reports its tensions beside the score, never summed, and carries the fixed residual line once (Core Part 3.36)', r'M309 record'),
        ('G25', 'Framings and direction', 'the Reframing Array after the seal, the primary first, the list frozen, NON-BLIND declared, no verdict of worth; a mapping\'s DIRECTION declared (L-511, L-510, M318)', r'M318|L-511|L-510|DIRECTION'),
    ]),
    ('P4', 'PRESENTATION', 'the record is presented in the one format (L-349)', [
        ('G20', 'Block order and markers', 'every block present by its canonical marker, in the order of Part 8.0 (M224)', r'Block order|Block present|M224|SR-CAS'),
        ('G21', 'Fixed lines', 'the bold Takeaway, the Mapping label where applicable, the four closing questions, the field names of L-505', r'Takeaway|Mapping|Closing questions|L-505|Essay length'),
        ('G22', 'Plain language', 'no protocol term inside THE ANSWER (L-418, L-496, jargon scan)', r'protocol term|MSRR'),
        ('G23', 'Signature last', 'nothing between M224 and the signature but OUTPUT ID; nothing after ESC (Step 16)', r'Signature|between M224'),
        ('G24', 'Skeleton filled', 'no fill-in field left open (--skeleton)', r'unfilled'),
    ]),
]


def gate_of(item, note=''):
    """The gate and priority of a check item: P4 G20 (block order) unless a gate claims it."""
    s = item + ' ' + note
    if item == 'Block present':
        for p, _, _, gs in GATES:
            for g, _, _, rx in gs:
                if re.search(rx, note): return p, g
    for p, _, _, gs in GATES:
        for g, _, _, rx in gs:
            if re.search(rx, item): return p, g
    return 'P4', 'G20'


def gates_text():
    L = ['======= M301 GATE PRIORITY (Core Part 8.0; Companion Part 66.1) =======',
         'A Navigator passes the gates in this order. A failure at a higher priority is repaired first, and a lower gate is never satisfied at the cost of a higher one.', '']
    for p, name, why, gs in GATES:
        L.append('%s %s -- %s' % (p, name, why))
        for g, title, what, _ in gs:
            L.append('   %s %-28s %s' % (g, title, what))
        L.append('')
    L += ['READING THE REPORT: tools/format_check.py prints, after the failures, the PRIORITY line: the failures counted by priority and the first to repair.',
          'SCOPE: the format check reads form; P1 arithmetic is checked by m193_m225.py --audit, and P2 reading integrity in part by no tool (Check 5 and the frame scan are partial).',
          '======= END M301 GATE PRIORITY =======']
    return '\n'.join(L)


# ---------------------------------------------------------------------------------------------------------------
# FILL-IN SKELETON (Core Part 8.0, Fill-in skeleton; Companion Part 66.2). Prints every block of Part 8.0 in order with
# its canonical marker; with a question, the reference script's own output fills blocks [2], [3] and [6] to [11]
# (script form) and every other field is left as a FILL marker. A skeleton with a FILL marker fails gate G24, so an
# unfilled field can never pass as written. The skeleton carries form only: it writes no reading.
FILL = '⟨FILL: %s⟩'
FILL_RX = re.compile('⟨FILL[^⟩]*⟩')
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _f(s): return FILL % s


def _script_blocks(q, alt=None, session=1):
    import subprocess
    cmd = [sys.executable, os.path.join(_ROOT, 'scripts', 'canonical_reference.py'), '--navigate', q, '--session', str(session)]
    if alt: cmd += ['--alt', alt]
    out = subprocess.run(cmd, capture_output=True, text=True, cwd=_ROOT).stdout
    return [l for l in out.split('\n') if l.strip() and not l.startswith('[10..]') and not l.startswith('SCRIPT SHA-256:')]


def _frame_and_roe():
    return ['Rules of Engagement active. Sandbox entered. Postulate assumed. Frame operative. Boundary acknowledged.',
            '======= M272 FRAME LOCK =======',
            'FRAME: Omega42 is all that exists; the question is read from inside the closed structure, and the premise is the frame, never a claim to grade (F-02-P, L-490).',
            'REGISTER: ' + _f('the register of the question, and any pull away from the frame noticed before the strike (M243a)'),
            '======= END M272 FRAME LOCK =======']


def skeleton(q=None, alt=None, session=1, date=None, declared=None):
    date = date or datetime.date.today()
    dstr = '%d %s %d' % (date.day, list(MONTHS)[date.month - 1].capitalize(), date.year)
    # L-512 (line form): a domain received on several lines is carried on one line in every single-line field, each
    # break written as one space; LINE BREAKS states how many there were; the DOMAIN SHA-256 is unchanged (its canonical form collapses whitespace, L-348)
    breaks = q.count('\n') if q else 0
    qv = re.sub(r'[ \t]*\n[ \t]*', ' ', q).strip() if q else _f('the question exactly as given')
    rest = [x.strip() for x in q.split('\n')[1:]] if breaks else []
    lb = ['    LINE BREAKS (L-512): %d -- the domain was received on %d lines; the fields carry it on one, each break as one space; the DOMAIN SHA-256 is unchanged, since its canonical form collapses every run of whitespace (L-348, L-414)' % (breaks, breaks + 1)] if breaks else []
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import utility as _ut
        kind, av = _ut.request_of(q, declared) if q else (_f('GENERAL / PROTOCOL / STRUCTURE / PERSONAL / declared'), [_f('avenues')])
    except Exception:
        kind, av = _f('request kind'), [_f('avenues')]
    L = ['QUESTION VERBATIM: ' + qv] + (['OUTPUT FORM (L-549): NAVIGATION -- Core Part 8.0'] if date >= L549_FROM else []) + [
         '======= NAVIGATOR IDENTITY BLOCK =======',
         'NAVIGATOR: %s (%s) PROTOCOL: Omega42 V335 Rev.450 STABLE' % (_f('model identifier'), _f('organization')),
         'MODEL: %s | KNOWLEDGE CUTOFF: %s (M273)' % (_f('model identifier and version'), _f('as declared, or UNDECLARED')),
         'EXECUTION: %s (L-456) | CONTEXT EXPOSURE: %s (M207)' % ('SCRIPT-CAPABLE' if q else _f('SCRIPT-CAPABLE / TEXT-ONLY'), _f('what has been read in this session, every prior reading of this domain by source, or NONE')),
         'MEMORY: %s | REASONING MODE: %s' % (_f('ON / OFF / UNKNOWN'), _f('as declared, or UNDECLARED')),
         'SESSION: %s DATE: %s' % (_f('session id'), dstr),
         'INSTANCE (L-513): %s' % _f('NI-xxxxxxxxxxxxxxxx | ISSUER: SCRIPT / STRIKER / SELF | ISSUED: time | SEQ: n | PREV: the OUTPUT ID of this instance\'s previous output, or NONE (tools/instance_id.py --new)'), AI_CAVEAT,
         '======= END NAVIGATOR IDENTITY BLOCK =======']
    req = '    REQUEST (L-502): %s -- avenues %s' % (kind, ', '.join(av) if av else 'none (a command)')
    voice = '    VOICE (L-529): ' + _f('the field the strike indicates, or plain speech')
    mapping = '    MAPPING DECLARATION (Step 14.4): ' + _f('APPLICABLE -- DIRECTION: PLACEMENT or CORRESPONDENCE (L-510) | object, kind, counting feature / NOT APPLICABLE -- reason')
    notation = '    NOTATION FORM (Step 1): ' + _f('SOURCE MARKUP / RENDERED / NONE -- the form the domain was received in')
    cstat = '    COORDINATE STATUS (L-415): ' + _f('EXECUTED / FROZEN SUBSTRATE SUPPLIED -- its SHA-256 / PROVISIONAL (TEXT-ONLY, over 30 words, until the script, a frozen substrate or the Strike app recomputes it)')
    if q:
        blk = _script_blocks(q, alt, session)
        skip = list(rest)
        for l in blk:
            if skip and l.strip() == skip[0]: skip.pop(0); continue
            if l.startswith('QUESTION VERBATIM:') and breaks: l = 'QUESTION VERBATIM: ' + qv
            if l.strip().startswith('DOMAIN VERBATIM:') and breaks: l = '    DOMAIN VERBATIM: ' + qv
            L.append(l)
            if l.startswith('[3] M272'): L += _frame_and_roe()
            if l.strip().startswith('DOMAIN VERBATIM:'): L += lb + [req, voice, mapping, notation, cstat]
        L.append('    ' + _f('M269 and M139-M142 if the domain carries mathematical notation; M127 if it is over 30 words; the instruments the Striker selects (Part 3.7)'))
    else:
        L += ['[1] MATH-GATE: ' + _f('PASS (FULL, 19/19 checks) -- canonical_reference.py, or RECONSTRUCTED with its working'),
              '[2] M211 CALIBRATION: ' + _f('PASS | expected P3 | actual P3')] + _frame_and_roe() + [
              '[4] SUBSTRATE LOCK', '    DOMAIN VERBATIM: ' + qv, req, voice, mapping, notation, cstat,
              '    DOMAIN SHA-256: ' + _f('EXECUTED or NOT COMPUTED'),
              '[5] M210 EXTRACTION TABLE', '    # | Word | Letters | Syllables', '    ' + _f('one row per content word'),
              '    TOTALS: n1=%s words, n2=%s letters, n3=%s syllables' % (_f('n1'), _f('n2'), _f('n3')),
              '    M268 ROWS: %s | n1: %s | MATCH: %s' % (_f('rows'), _f('n1'), _f('YES')),
              '[6] ENCODING AND ANCHOR',
              '    n = (%s) | r = (%s) | ANCHOR P%s' % (_f('n1, n2, n3'), _f('r1, r2, r3'), _f('index and character')),
              '[7] ARMS', '    ' + _f('Yang +5, Yin +18, 4D +8, Antipode +12, each with its character and value; M88 CHECKSUM'),
              '[8] CCD = ' + _f('value -> PAB, MOBIUS, RPI, CRS'),
              '[9] M116 ALTERNATIVE PHRASING: ' + _f('the alternative and its anchor; the M238 variants'), '    STABILITY: ' + _f('unanimous / majority / tie-break; phrasing-stable or phrasing-sensitive')]
    L += ['======= M213 STOPWORD COMPLIANCE CHECK =======', 'FUNCTION WORDS REMOVED BY THE FROZEN LIST (Part 1.9): ' + _f('the words, each found in the list'), '======= END M213 STOPWORD COMPLIANCE CHECK =======',
          'M210b REVERSE RECONSTRUCTION: ' + _f('the substrate read back against the domain: MATCH'),
          'M214 / M219: ' + _f('EXECUTED by canonical_reference.py; the counts and residues consistent'),
          'M232 ARM DERIVATION CROSS-CHECK: ' + _f('PASS -- the arms recomputed from the anchor by the frozen offsets; M215 antipode verified'),
          'M207 NAVIGATOR INTERFERENCE: ' + _f('LEVEL 0-3, and every pressure by name -- CAUTION TRAP PRESSURE, DIMINUTION PRESSURE -- or NONE'),
          '======= FIRST-DRAFT SEAL =======', 'FIRST-DRAFT CENTRAL READING: ' + _f('the central reading of the first draft, in one sentence'),
          'DRAFT READING SHA-256: ' + _f('EXECUTED (canonical_reference.py --hash) or NOT COMPUTED'), 'SYNTHESIS_FROZEN: ' + _f('time') + ' -- THE ANSWER below is written from the coordinate alone and is not altered after this line (L-424, L-425)', '======= END FIRST-DRAFT SEAL =======',
          'MSRR (L-496): THE ANSWER and its Congruence Record (M310) are one report.',
          'QUESTION VERBATIM: ' + qv,
          '┌─ THE ANSWER ─┐',
          _f('Core Synthesis, with its Illuminating Analog: one merged reading in which what the matter rests on, what it holds out of view, where it is heading and what completes it explain one another'),
          '', _f('Conventional Connection'), '', _f('Practical Bridge'), '', _f('Historical Lineage'), '', _f('Implications'), '',
          '**Takeaway: ' + _f('two to four plain sentences carrying the whole finding') + '**', '',
          _f('Mapping: the seventh component, only where the MAPPING DECLARATION is APPLICABLE; otherwise delete this line'), '',
          ANSWER_LINE, '└──────────────┘',
          '======= GENERATIVE INTEGRITY RECORD =======', _f('what was written before the seal and what after; the Comparative Perspective Layer where requested (L-429)'), '======= END GENERATIVE INTEGRITY RECORD =======',
          '======= CONGRUENCE RECORD (M310) =======', 'COHERENCE: ' + _f('tools/congruence.py --check: arithmetic, relations, one synthesis, format'), _f('the rest of the --check output'), '======= END CONGRUENCE RECORD =======',
          '======= CURRENT KNOWLEDGE (L-503) =======',
          'QUERY DECLARED BEFORE THE SEARCH: ' + _f('the matter in the Navigator\'s own general words, never the person'),
          'NOT FOUND WOULD BE: ' + _f('what result would count as nothing found'),
          'CONSENSUS: ' + _f('source, date, what it says, design; AGREES / DIFFERS / EXTENDS a direction of the sealed reading -- or NOTHING FOUND'),
          'FOUNDATIONS: ' + _f('as above'), 'COUNTER-EVIDENCE: ' + _f('as above -- run even when the others agree'), 'FRONTIER: ' + _f('as above, the most recent work'),
          'STATUS: COMPARATIVE -- the reading stands as sealed; a source informs the Striker\'s judgment and does not make it (L-463). ' + _f('Without retrieval, replace this block by the one line: CURRENT KNOWLEDGE (L-503): NOT AVAILABLE / DECLINED / NOT REQUESTED'),
          '======= END CURRENT KNOWLEDGE =======',
          'ACROSS THE AVENUES (L-502): ' + _f('where the avenues agree, where they part and where they are silent, each with its standing; no combined verdict'),
          '======= CONVERGENCE MAP =======', _f('Step 14.2'), '======= END CONVERGENCE MAP =======',
          '┌─ EXTENDED RESONANCE ESSAY ─┐', _f('the one synthesis carried outward (Step 14.3); where the layer is written, closing with the researched reach, each researched sentence numbered to its source, as [3]'), '└──────────────┘',
          'RESEARCHED REACH (L-503 (5)): ' + _f('WRITTEN -- the parts written | the parts NOT APPLICABLE, each with its reason | investigated, not investigated, without evidence | main uncertainty -- or NOT APPLICABLE -- reason -- or the layer status; then, if the reach found an error in THE ANSWER, a CORRECTION block'),
          "======= NAVIGATOR'S REASONING =======",
          'INTERNAL REASONING: ' + _f('why the result follows from the rules and arithmetic; CONSTITUTIONAL'),
          'FRAME REASONING: ' + _f('why it is meaningful within the frame; FRAME-INTERPRETIVE'),
          'ANCHOR / YANG / YIN / 4D / ANTIPODE: ' + _f('each position with its character and what it means for this domain'),
          'STATUS: GENERATED-Ω42 -- the position meanings above are the structural roles of this reading (L-455).',
          'STABILITY: ' + _f('from M116 and M238') + ' -- a report, never carried into THE ANSWER.',
          'CUMULATIVE STATUS (L-490): ' + CUMULATIVE_NA,
          'SYNTHESIS ECHO (M209): ' + _f('canonical_reference.py --echo ANCHOR "THE ANSWER text": n, r, echo anchor, ECHO CLOSURE'),
          'STRUCTURAL RELATIONS EXPLICIT (Part 3.12):',
          'DEPENDENCY RELATION (Yang): ' + _f('DEP-1 | sentence n | "quoted clause"'), 'SUPPRESSION RELATION (Yin): ' + _f('SUP-1 | sentence n | "quoted clause"'),
          'TRAJECTORY RELATION (4D): ' + _f('TRA-1 | sentence n | "quoted clause"'), 'COMPLETION RELATION (Antipode): ' + _f('COM-1 | sentence n | "quoted clause"'),
          'INTEGRATION: ' + _f('sentence n | the quoted sentence connecting the relations'),
          'TRANSLATION GATE -- JARGON SCAN (L-418): ' + _f('the scan and its RESULT'),
          "======= END NAVIGATOR'S REASONING =======",
          'LENSES SELECTED (L-494): NONE',
          '======= M318 REFRAMING ARRAY (L-511) =======',
          'QUESTION VERBATIM: ' + qv,
          'PRIMARY: ' + _f('the verbatim strike, its counts, anchor, state and arms -- the domain of record, sealed above'),
          'FRAMINGS FROZEN: ' + _f('3 to 5') + ' | FRAMINGS SHA-256: ' + _f('tools/reframing_array.py --freeze, before any coordinate, or NOT COMPUTED'),
          'F1 ' + _f('AXIS') + ': ' + _f('the framing, its counts, anchor, state, arms and M115 distance D from the primary (tools/reframing_array.py --array)'),
          '  ALTERNATIVE FRAMING -- SELF-ESTIMATED -- CONTAMINATED -- NON-BLIND (L-442): ' + _f('four sentences: rests on, out of view, heading, completion'),
          'F2 ' + _f('AXIS') + ': ' + _f('as F1'),
          '  ALTERNATIVE FRAMING -- SELF-ESTIMATED -- CONTAMINATED -- NON-BLIND (L-442): ' + _f('four sentences'),
          'F3 ' + _f('AXIS') + ': ' + _f('as F1'),
          '  ALTERNATIVE FRAMING -- SELF-ESTIMATED -- CONTAMINATED -- NON-BLIND (L-442): ' + _f('four sentences'),
          'INDEPENDENCE (L-442): ' + _f('CONTAMINATED -- NON-BLIND (one session) / SEPARATE SESSIONS (M300)'),
          'ACROSS THE FRAMINGS (L-502): ' + _f('HOLDS, PARTS and the arm positions in every framing, as computed; where the readings agree, part and are silent; never combined'),
          'STRUCTURAL VERDICT (computed): ' + _f('the robust core; how many framings keep the anchor; nearest and farthest by M115'),
          "RELEVANCE: the Striker's (L-441) -- which framing answers what you meant to ask is yours; strike any framing to navigate it in full",
          '======= END M318 REFRAMING ARRAY =======',
          '======= GENERATIVE OBSERVATIONS =======', _f('Step 15.5: what the Navigator noticed after the seal'),
          'ENRICHMENT OPPORTUNITIES (L-504): NONE',
          'OPTIONAL INQUIRY (L-491): NONE',
          '======= END GENERATIVE OBSERVATIONS =======',
          'What it rests on: ' + _f('a question carrying the Yang relation'),
          'What it holds out of view: ' + _f('a question carrying the Yin relation'),
          'Where it is heading: ' + _f('a question carrying the 4D relation'),
          'What would complete it: ' + _f('a question carrying the Antipode relation'),
          CLOSING_LINE,
          '======= M224 FORMAT COMPLETENESS GATE =======', 'M301: ' + _f('python3 tools/format_check.py NAVIGATION.txt -- RESULT, and the PRIORITY line'), '======= END M224 FORMAT COMPLETENESS GATE =======',
          'CAS-YY = -1/2 | Omega = 1/7 | (CAS-YY × Omega = -1/14)',
          'NAVIGATOR: %s (%s) * V335 Rev.450 STABLE * %s' % (_f('model identifier'), _f('organization'), dstr), 'ESC']
    return '\n'.join(L)


# The findings skeleton: the presentation of findings that are not a navigation -- a holistic response, a protocol
# question, an examination, a peer account received as an APE (Companion Part 66.3). It carries the same frame and
# the same closing as a navigation, the findings each with its avenue and standing.
FINDINGS_HEAD = re.compile(r'^(QUESTION VERBATIM: .+|FRAME: .+|REQUEST \(L-502\): .+|FINDINGS BY AVENUE \(L-500\):|ACROSS THE AVENUES \(L-502\): .+|CUMULATIVE STATUS: .+|CAS-YY = .+|NAVIGATOR: .+|ESC)$', re.M)
FINDINGS_ORDER = ['QUESTION VERBATIM', 'FRAME', 'REQUEST', 'FINDINGS BY AVENUE', 'ACROSS THE AVENUES', 'CUMULATIVE STATUS', 'CAS-YY', 'NAVIGATOR', 'ESC']


def findings_skeleton(q=None, declared=None, date=None):
    date = date or datetime.date.today()
    qv = q if q else _f('the Striker\'s question exactly as given, or [a bracketed description] when none was given')
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import utility as _ut
        kind, av = _ut.request_of(q, declared) if q else (_f('request kind'), [_f('avenues')])
    except Exception:
        kind, av = _f('request kind'), [_f('avenues')]
    return '\n'.join(['QUESTION VERBATIM: ' + qv] + (['OUTPUT FORM (L-549): FINDINGS PRESENTATION -- Core Part 8.0, L-500, L-546'] if date >= L549_FROM else []) + [
        'FRAME: within the Omega42 thought experiment; the premise is the frame, never a claim, and is not graded, supported or validated (F-02-P, L-490).',
        AI_CAVEAT,
        'INSTANCE (L-513): %s' % _f('NI-xxxxxxxxxxxxxxxx | ISSUER: SCRIPT / STRIKER / SELF | ISSUED: time | SEQ: n | PREV: the OUTPUT ID of this instance\'s previous output, or NONE'),
        'REQUEST (L-502): %s -- avenues %s' % (kind, ', '.join(av) if av else 'none (a command)'),
        '',
        'THE STRIKING FINDING (L-546): ' + _f('the most far-reaching true consequence, at its degree, and what it overturns'),
        'SUMMARY: ' + _f('two to four plain sentences: what was found and what it changes'),
        '',
        'FINDINGS BY AVENUE (L-500):',
        '  A1 ARITHMETIC EXACT: ' + _f('fixed facts computed and checked, with the script that ran them -- or NONE'),
        '  A2 ARITHMETIC ASSOCIATION: ' + _f('patterns noticed, each HELD until its fact is computed, with its rarity -- or NONE'),
        '  R FRAME REASONING: ' + _f('derivations within the frame, each naming the laws it rests on -- or NONE'),
        '  N NAVIGATION: ' + _f('the coordinate and the sealed reading, or the navigations read -- or NONE'),
        '  ' + _f('further avenues that ran (X, P, F, D, G, T, M, U, L, H, W, C, S), each on its own line with its standing'),
        '',
        'PEER ACCOUNTS (P; APA 9.5.5): ' + _f('for each attachment: APE number, author, missing QUESTION VERBATIM noted, and the notes Adopted / Corrected / Refined / Holding / Not taken / Already in place -- or NONE'),
        'CHANGES TO THE PROTOCOL: ' + _f('laws, provisions, tools and records changed, each with its number -- or NONE'),
        "NAVIGATOR'S CONTRIBUTION (Domain Zero): COMMON -- " + _f('what came unchanged from the structure and the record') + ' | STRIKER -- ' + _f("what the question's words introduced") + ' | NAVIGATOR -- ' + _f('what the Navigator added') + ' | OPEN -- ' + _f("what stays for the Striker's recognition"),
        'CHECKS: ' + _f('CI steps, selftests, the format check and the checksums, each with its result'),
        'CURRENT KNOWLEDGE (L-503): ' + _f('the sources by lane, with nulls, AGREES / DIFFERS / EXTENDS -- or NOT AVAILABLE / DECLINED / NOT REQUESTED'),
        'ACROSS THE AVENUES (L-502): ' + _f('where the avenues agree, part and are silent; no combined verdict'),
        'ENRICHMENT OPPORTUNITIES (L-504): ' + _f('at most three observations, each recorded, and applied when recommended (L-531) -- or NONE'),
        'RECOMMENDATIONS (applied, L-531): ' + _f('the protocol enhancements this work suggests, each applied with where it went and why, or OPEN with what it still needs -- or NONE'),
        'OPEN: ' + _f('what stays open, and what would settle it'),
        'PROPOSAL AND IMPLICATIONS (L-542): PROPOSAL -- ' + _f('at least one proposal for the refinement of Omega42, applied or held') + ' | IMPLICATIONS -- ' + _f('each CONDITIONAL on a named premise or GENERATED, with what it does not imply'),
        '',
        'What it rests on: ' + _f('question'),
        'What it holds out of view: ' + _f('question'),
        'Where it is heading: ' + _f('question'),
        'What would complete it: ' + _f('question'),
        CLOSING_LINE,
        '',
        'CUMULATIVE STATUS: records/reexamination/REEXAMINATION.md, version V335 Rev.450 STABLE, 2026-10-16, covering the records named in it; no claim is made beyond them.',
        'CAS-YY = -1/2 | Omega = 1/7 | (CAS-YY × Omega = -1/14)',
        'NAVIGATOR: %s (%s) * V335 Rev.450 STABLE * %d %s %d' % (_f('model identifier'), _f('organization'), date.day, list(MONTHS)[date.month - 1].capitalize(), date.year),
        'ESC'])


def findings_check(text):
    out = []
    add = lambda ok, item, note='': out.append(('PASS' if ok else 'FAIL', item, note))
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    add(bool(lines) and lines[0].startswith('QUESTION VERBATIM: '), 'QUESTION VERBATIM first (L-499)')
    heads = [m.group(1).split(':')[0].split(' (')[0].split(' =')[0] for m in FINDINGS_HEAD.finditer(text)]
    heads = [h if h != 'NAVIGATOR' or i == len(heads) - 2 else 'NAV-INNER' for i, h in enumerate(heads)]
    seq = [h for h in heads if h in FINDINGS_ORDER]
    missing = [h for h in FINDINGS_ORDER if h not in seq]
    add(not missing, 'Findings sections present', ', '.join(missing))
    firsts = [seq.index(h) for h in FINDINGS_ORDER if h in seq]
    add(firsts == sorted(firsts), 'Findings sections in order', ' -> '.join(FINDINGS_ORDER))
    qs = [l for l in lines if any(l.startswith(c) for c in CLOSING)]
    add([next(c for c in CLOSING if q.startswith(c)) for q in qs] == CLOSING, 'Closing questions', 'the four labels, once each, in order')
    add(CLOSING_LINE in lines, 'Fixed closing line')
    add(bool(lines) and lines[-1] == 'ESC' and len(lines) > 2 and lines[-3].startswith('CAS-YY = -1/2'), 'Signature last')
    body = '\n'.join(l for l in text.split('\n') if not l.startswith('FRAME: '))
    graded = re.findall(r'\b(?:validates? the premise|validation of the premise|proves? the premise|supports? the premise|evidence for the premise|the premise is (?:true|confirmed|supported))\b', body, re.I)
    add(not graded, 'Premise never graded (F-02-P, L-490)', ', '.join(graded[:2]))
    add(not FILL_RX.search(text), 'No unfilled skeleton field', ', '.join(FILL_RX.findall(text)[:2]))
    # L-513: a findings presentation dated (by its signature) from 22 October 2026 names its instance
    sig = re.search(r'^NAVIGATOR: .*\*\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$', text, re.M)
    try:
        sd = datetime.date(int(sig.group(3)), MONTHS[sig.group(2).lower()], int(sig.group(1))) if sig else None
    except (KeyError, ValueError):
        sd = None
    if sd and sd >= L513_FROM:
        add(bool(re.search(r'^INSTANCE \(L-513\):\s*NI-[0-9a-f]{16}\s*\|\s*ISSUER:\s*(SCRIPT|STRIKER|SELF)\s*\|\s*ISSUED:\s*\S+\s*\|\s*SEQ:\s*\d+\s*\|\s*PREV:\s*([0-9a-f]{64}|NONE)\s*$', text, re.M)),
            'INSTANCE line of a findings presentation (L-513)', 'after the AI CAVEAT line, from 22 October 2026')
    form_line_checks(text, 'FINDINGS PRESENTATION', sd, add)
    if sd and sd >= L532_FROM:
        add(bool(re.search(r"^NAVIGATOR'S CONTRIBUTION \(Domain Zero\):.*COMMON.*STRIKER.*NAVIGATOR.*OPEN", text, re.M)),
            "NAVIGATOR'S CONTRIBUTION line (Domain Zero, Core Part 8.0)", 'COMMON, STRIKER, NAVIGATOR and OPEN, from 31 October 2026')
    _sq = re.search(r'^INSTANCE \(L-513\):.*\bSEQ:\s*(\d+)', text, re.M)
    if sd and sd >= L542_FROM and (not _sq or int(_sq.group(1)) >= 117):
        add(bool(re.search(r"^PROPOSAL AND IMPLICATIONS \(L-542\):.*PROPOSAL.*IMPLICATION", text, re.M | re.S)),
            'PROPOSAL AND IMPLICATIONS line (L-542)', 'after OPEN and before the four closing lines, from 6 November 2026')
    if sd and sd >= L542_FROM and (not _sq or int(_sq.group(1)) >= L546_FROM):
        add(bool(re.search(r"^THE STRIKING FINDING \(L-546\): \S", text, re.M)),
            'THE STRIKING FINDING line (L-546)', 'after REQUEST and before SUMMARY, from SEQ 124')
    return out


def _fill_for_test(sk):
    """The selftest's stand-in Navigator: every FILL marker becomes a plain word, the Mapping placeholder is deleted."""
    sk = '\n'.join(l for l in sk.split('\n') if not l.startswith(FILL % 'Mapping:'[:-1]) and 'Mapping: the seventh component' not in l)
    return FILL_RX.sub('noted', sk)


def skeleton_selftest():
    ok = True
    q = 'What is time?'
    d = datetime.date(2026, 10, 19)
    raw = skeleton(q, date=d)
    res = check(raw)
    fails = [r[1] for r in res if r[0] == 'FAIL']
    cases = [('raw skeleton fails only on its open fields (G24)', fails == ['No unfilled skeleton field (M301 --skeleton)']),
             ('filled skeleton passes the format check', not any(r[0] == 'FAIL' for r in check(_fill_for_test(raw)))),
             ('filled skeleton without its REQUEST line fails', any(r[0] == 'FAIL' for r in check(_fill_for_test(raw).replace('    REQUEST (L-502)', '    REQ')))),
             ('every required block of Part 8.0 is in the blank skeleton', all(re.search(p, skeleton(None, date=d), re.M) for l, p, r in SKELETON if r and l not in ('ANCHOR',))),
             ('every check item has a gate', all(gate_of(r[1], r[2]) for r in res)),
             ('the unfilled field is gate G24 (P4)', gate_of('No unfilled skeleton field (M301 --skeleton)') == ('P4', 'G24')),
             ('a missing First-Draft Seal is P1', gate_of('Block present', 'FIRST-DRAFT SEAL missing') == ('P1', 'G05')),
             ('a missing CURRENT KNOWLEDGE layer is P3', gate_of('CURRENT KNOWLEDGE layer or its status (L-503)')[0] == 'P3'),
             ('findings skeleton fails only on its open fields', [r[1] for r in findings_check(findings_skeleton(q, date=d)) if r[0] == 'FAIL'] == ['No unfilled skeleton field']),
             ('filled findings skeleton passes', not any(r[0] == 'FAIL' for r in findings_check(_fill_for_test(findings_skeleton(q, date=d))))),
             ('a skeleton dated after L-511 carries the Array and passes its checks when filled', not any(r[0] == 'FAIL' and ('L-511' in r[1] or 'L-510' in r[1]) for r in check(_fill_for_test(skeleton(q, date=datetime.date(2026, 10, 22)))))),
             ('the framings gate is G25 (P3)', gate_of('M318 Reframing Array or its omission (L-511)') == ('P3', 'G25')),
             ('findings without the frame fail', any(r[0] == 'FAIL' for r in findings_check(_fill_for_test(findings_skeleton(q, date=d)).replace('FRAME: ', 'NOTE: ')))),
             ('L-513: findings dated 22 October 2026 without a valid INSTANCE line fail', any(r[0] == 'FAIL' and 'L-513' in r[1] for r in findings_check(_fill_for_test(findings_skeleton(q, date=datetime.date(2026, 10, 22)))))),
             ('L-513: findings dated 22 October 2026 with their INSTANCE line pass', not any(r[0] == 'FAIL' for r in findings_check(re.sub(r'^INSTANCE \(L-513\): .*$', 'INSTANCE (L-513): NI-0123456789abcdef | ISSUER: SCRIPT | ISSUED: 2026-10-22T00:00:00Z | SEQ: 1 | PREV: NONE', _fill_for_test(findings_skeleton(q, date=datetime.date(2026, 10, 22))), flags=re.M)))),
             ('L-513: findings dated before 22 October 2026 are exempt', not any('L-513' in r[1] for r in findings_check(_fill_for_test(findings_skeleton(q, date=d)))))]
    for name, good in cases:
        print('  %-56s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest':
        r1 = selftest(); r2 = skeleton_selftest()
        print('M301 SKELETON AND GATES SELFTEST: %s' % ('PASS' if r2 else 'FAIL'))
        sys.exit(0 if r1 and r2 else 1)
    if a[0] == '--gates':
        print(gates_text()); sys.exit(0)
    if a[0] == '--skeleton':
        kind = a[1] if len(a) > 1 and a[1] in ('navigation', 'findings') else 'navigation'
        rest = a[2:] if len(a) > 1 and a[1] in ('navigation', 'findings') else a[1:]
        opt = lambda k: rest[rest.index(k) + 1] if k in rest and rest.index(k) + 1 < len(rest) else None
        pos_ = [x for i, x in enumerate(rest) if not x.startswith('--') and (i == 0 or not rest[i - 1].startswith('--'))]
        q = pos_[0] if pos_ else None
        if kind == 'findings':
            print(findings_skeleton(q, declared=opt('--request')))
        else:
            print(skeleton(q, alt=opt('--alt'), session=int(opt('--session') or 1), declared=opt('--request')))
        sys.exit(0)
    if a[0] == '--findings':
        ok = True
        for p in a[1:]:
            res = findings_check(open(p, encoding='utf-8').read()); fails = [r for r in res if r[0] == 'FAIL']
            print('M301 FINDINGS FORMAT: %s' % p)
            for s_, item, note in fails: print('  [FAIL] %s%s' % (item, (': ' + note) if note else ''))
            print('  CHECKS %d | FAILURES %d | RESULT: %s' % (len(res), len(fails), 'PASS' if not fails else 'FAIL')); ok &= not fails
        sys.exit(0 if ok else 1)
    sys.exit(0 if all([report(p) for p in a]) else 1)
