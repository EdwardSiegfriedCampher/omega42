# ===== m193_m225.py BEGIN =====
#!/usr/bin/env python3
"""m193_m225.py -- operative procedures for M193 and M225 (Core Part 3.11, Part 3.12).

STATUS: operative at V335 Rev.449 STABLE. Diagnostic value: run on the constructed
cases in selftest() below; not yet validated on real navigations.
Each procedure rests on an inference from the specification's own text, stated below, since
neither instrument's entry gives extraction rules of its own beyond a name and a trigger.

M225 -- Structural Claim Extraction (Tier 1, mandatory for SR-CAS)
  What the specification does say: SR-CAS reports "M225 comparison result" and states that
  "T1.5 is the M225 score, not a separate holistic judgment" (Part 6.1); Step 9.8 says
  M225 does "paraphrase-sensitivity testing". T1.5 combines the lexical score (T1.5-L, below) and the
  structural score (T1.5-S, from per-relation verdicts) by max() only when they agree within
  0.30 and the verdicts were not self-adjudicated; otherwise T1.5 = T1.5-L, marked QUALIFIED.
  Inference: a structural claim is a sentence asserting one of the four relations the arms
  map (dependency, suppression, trajectory, completion). M225 extracts those claims from each
  Navigator's Core Synthesis and scores how well the claims of two Navigators match.
  Method: lexical and deterministic. It sees words, not meaning: reordering the words inside
  a sentence does not change a claim, and a faithful paraphrase in different vocabulary
  scores lower than a copy. Those are properties of this procedure, not findings about
  Navigators. The relation lexicon and the 7-letter stem are design choices (CDT-B).

M193 -- Contextual Integrity Scanner (Tier 0, always active)
  What the specification does say: only the name, the tier, and "no opt-out". M91-2
  (Execute-Do-Not-Recall) and M207 (Navigator Interference Declaration) concern context carried into a
  navigation from outside it.
  Inference: M193 checks that a navigation's output was produced from the domain and the
  protocol alone, and not from context carried in. Three checks: (1) the domain echoed in the
  output is the domain supplied; (2) the output makes no reference to earlier sessions or
  navigations; (3) the output does not reuse the vocabulary of the surrounding conversation
  beyond what an unrelated text of the same size would be reused.
  Check 3 reports a number and sets no threshold, and does not enter the verdict: an
  on-topic conversation legitimately shares vocabulary with a faithful answer, and the
  self-test shows a clean on-topic answer with an excess of 0.18, so this check cannot
  separate topic from carried-over context. Only checks 1 and 2 decide the verdict.

L-431 -- register scan: lists non-exempt evaluative, conversational, anthropomorphic and self-referential
  wording in a protocol document (code, First Contact, quotations and the CRC-60 corpus exempt).

L-418 -- Translation Gate jargon scan (Step 14.1)
  A lexical scan of THE ANSWER for P-numbers, arm names, CDT labels, instrument and law
  references and Part 10 abbreviations (each a violation), and for capitalised position-character
  names that do not open a sentence (each listed for review, with the sentence it occurs in, so
  that a confirmation of ordinary usage can be checked against that sentence). Lexical, not semantic: it does not
  replace the seven Translation Gate checks.

Usage: python3 m193_m225.py CANONICAL_REFERENCE.py --selftest
       python3 m193_m225.py CANONICAL_REFERENCE.py --audit NAVIGATION.txt [--corpus DIR]
       python3 m193_m225.py CANONICAL_REFERENCE.py --m225 A.txt B.txt [--verdicts D,S,T,C] [--self-adjudicated]
       python3 m193_m225.py CANONICAL_REFERENCE.py --jargon ANSWER.txt
       python3 m193_m225.py CANONICAL_REFERENCE.py --register DOCUMENT.docx [--fc-start TEXT --fc-end TEXT]
       python3 m193_m225.py CANONICAL_REFERENCE.py --premise DOCUMENT.docx|TEXT.txt
"""
import importlib.util, os, re, sys

RELATIONS = {
    'dependency': ['depend', 'rely', 'require', 'presuppose', 'hinge', 'need', 'underpin',
                   'depends', 'relies', 'requires', 'presupposes', 'rest', 'ground', 'base', 'condition', 'contingent'],
    'suppression': ['suppress', 'omit', 'ignore', 'obscure', 'hide', 'exclude', 'silence', 'neglect', 'mask', 'conceal', 'overlook',
                    'excludes', 'overlooks', 'conceals', 'masks', 'absence', 'lack', 'missing'],
    'trajectory': ['toward', 'lead', 'become', 'move', 'unfold', 'evolve', 'drift', 'tend', 'head',
                   'leads', 'tends', 'drifts', 'headed', 'oriented', 'directed', 'approaching', 'asymptotic', 'convergence', 'trajectory'],
    'completion': ['complete', 'resolve', 'close', 'fulfil', 'finish', 'conclude', 'reconcile', 'answer',
                   'closes', 'resolves', 'fulfill', 'fulfills', 'concludes', 'solution', 'resolution', 'boundary', 'aperture'],
}
# Multi-word markers, matched as whole phrases in the lowercased sentence.
RELATION_PHRASES = {
    'dependency': ['rests on', 'rest on', 'built upon', 'build upon', 'relies upon', 'rely upon', 'anchored in',
                   'operates within', 'operate within'],
    'suppression': ['fails to', 'fail to'],
    'trajectory': [],
    'completion': [],
}
RELATION_ORDER = ('dependency', 'suppression', 'trajectory', 'completion')
HISTORY_PHRASES = ['as we discussed', 'as discussed earlier', 'in our previous', 'earlier navigation', 'previous navigation',
                   'last time', 'as before', 'you told me', 'previous session', 'earlier conversation',
                   'as mentioned earlier', 'as i said earlier', 'earlier in this conversation']
_SUFFIXES = ('ing', 'ed', 'es', 's', 'ly')


def load(canonical_path):
    spec = importlib.util.spec_from_file_location('canon', canonical_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(w):
    w = re.sub(r'[^a-z]', '', w.lower())
    for s in _SUFFIXES:
        if w.endswith(s) and len(w) - len(s) >= 4:
            w = w[:-len(s)]
            break
    return w[:7]


_REL = {}
for _t, _ws in RELATIONS.items():
    for _w in _ws:
        assert _REL.setdefault(norm(_w), _t) == _t, 'relation lexicon collision: ' + _w
_PHR = [(re.compile(r'\b' + re.escape(p) + r'\b'), t) for t, ps in RELATION_PHRASES.items() for p in ps]


def _tokens(text):
    return re.findall(r"[A-Za-z]+", text)


def content_norms(text, mod):
    return {norm(w) for w in _tokens(text) if w.lower() not in mod.CANONICAL_STOPWORDS and len(w) >= 3}


# ------------------------------------------------------------------ M225
def extract_claims(text, mod):
    claims = []
    for sent in re.split(r'(?<=[.!?;])\s+', text.strip()):
        toks = _tokens(sent)
        types = {_REL[norm(t)] for t in toks if norm(t) in _REL}
        low = sent.lower()
        types |= {t for rx, t in _PHR if rx.search(low)}
        if not types:
            continue
        words = frozenset(norm(t) for t in toks if t.lower() not in mod.CANONICAL_STOPWORDS and len(t) >= 3 and norm(t) not in _REL)
        for ty in sorted(types):
            claims.append((ty, words))
    return claims


def _jac(a, b):
    return len(a & b) / len(a | b) if (a | b) else 0.0


def compare(claims_a, claims_b):
    """Mean over relation types present in either synthesis of the symmetric best-match Jaccard.
    Returns (score, per_type) or (None, {}) when neither synthesis yields a claim."""
    per = {}
    for ty in RELATIONS:
        A = [w for t, w in claims_a if t == ty]
        B = [w for t, w in claims_b if t == ty]
        if not A and not B:
            continue
        if not A or not B:
            per[ty] = 0.0
            continue
        ab = sum(max(_jac(a, b) for b in B) for a in A) / len(A)
        ba = sum(max(_jac(b, a) for a in A) for b in B) / len(B)
        per[ty] = (ab + ba) / 2
    return (sum(per.values()) / len(per) if per else None), per


VERDICT_SCORE = {'MATCH': 1.0, 'PARTIAL': 0.5, 'DIFFERENT': 0.0}


def parse_relations_block(text):
    """Read a STRUCTURAL RELATIONS EXPLICIT block (Part 8.2). Returns {relation: sentence or None}.
    A field reading NONE, N/A or left empty counts as the relation not stated."""
    out = {}
    for rel in RELATION_ORDER:
        m = re.search(r'^\s*' + rel.upper() + r'(?: CLAIM)?[^:\n]*:\s*(.*)$', text, re.M)
        val = m.group(1).strip() if m else ''
        out[rel] = None if (not val or val.upper() in ('NONE', 'N/A', 'N-A', '[]')) else val
    return out


def structural_score(block_a, block_b, verdicts):
    """T1.5-S (Part 3.12). verdicts: {relation: MATCH | PARTIAL | DIFFERENT}, the comparing Navigator's
    per-relation judgment of whether the two quoted statements make the same structural claim.
    A relation stated by one synthesis only scores 0; a relation stated by neither is excluded."""
    a, b = parse_relations_block(block_a), parse_relations_block(block_b)
    per = {}
    for rel in RELATION_ORDER:
        if a[rel] is None and b[rel] is None:
            continue
        if a[rel] is None or b[rel] is None:
            per[rel] = 0.0
            continue
        v = (verdicts or {}).get(rel)
        if v not in VERDICT_SCORE:
            raise ValueError('T1.5-S needs a MATCH / PARTIAL / DIFFERENT verdict for ' + rel)
        per[rel] = VERDICT_SCORE[v]
    return (round(sum(per.values()) / len(per), 3) if per else None), per


TOLERANCE = 0.30


def m225(text_a, text_b, mod, block_a=None, block_b=None, verdicts=None, self_adjudicated=False):
    ca, cb = extract_claims(text_a, mod), extract_claims(text_b, mod)
    score, per = compare(ca, cb)
    lex = None if score is None else round(score, 3)
    struct, per_s = (None, {})
    if block_a is not None and block_b is not None:
        struct, per_s = structural_score(block_a, block_b, verdicts)
    # Tolerance rule (Part 3.12): combine by max() only when the two scores agree within 0.30 and the
    # verdicts were not self-adjudicated; otherwise T1.5 = T1.5-L, marked QUALIFIED until confirmed.
    vals = [v for v in (lex, struct) if v is not None]
    qualified = False
    if lex is not None and struct is not None:
        if abs(struct - lex) <= TOLERANCE and not self_adjudicated:
            t15 = max(lex, struct)
        else:
            t15, qualified = lex, struct > lex
    else:
        t15 = vals[0] if vals else None
    return {'claims_a': len(ca), 'claims_b': len(cb), 'per_type': per,
            'T1.5-L': lex, 'T1.5-S': struct, 'per_relation_S': per_s,
            'T1.5': t15, 'qualified': qualified,
            'status': 'NO RELATIONS EXTRACTED' if not vals else ('QUALIFIED' if qualified else 'SCORED')}


# ------------------------------------------------------------------ L-431 register scan
REGISTER_LEXICON = [
    r"\bhonest(?:ly|y)?\b", r"\bhonesty\b", r"\bgenuine(?:ly)?\b", r"\bactually\b", r"\bsimply\b",
    r"\bmerely\b", r"\breally\b", r"\bclearly\b",
    r"\bworth (?:a second look|naming|knowing|reading|stating|exploring)\b",
    r"\breal (?:gate|company|contribution|work)\b", r"paper over", r"better way", r"good discipline",
    r"not nothing", r"habit of attention", r"find fault", r"actual engagement", r"says little", r"worry about",
    r"\bdeserve", r"\bprofound\b", r"bold case", r"interesting object", r"\bContemplation\b", r"self-audit",
    r"not a guarantee", r"rather than hidden", r"not a fault", r"Navigator did not know", r"finds itself",
]
_CORPUS_LINE = re.compile(r'^\d+\. ".*" -- n=')
_QUOTED = re.compile(r'"[^"]*"|\u201c[^\u201d]*\u201d')


def register_scan(docx_path, fc_start=None, fc_end=None):
    """L-431: list non-exempt register hits in a .docx. Exempt: code (Consolas) paragraphs, the First Contact
    range [fc_start, fc_end), quoted spans, and CRC-60 corpus lines."""
    import zipfile, html as _html
    xml = zipfile.ZipFile(docx_path).read('word/document.xml').decode('utf-8')
    paras = re.findall(r'<w:p(?:\s[^>]*)?>.*?</w:p>', xml, re.S)
    hits, in_fc = [], False
    for i, p in enumerate(paras):
        t = ''.join(_html.unescape(m) for m in re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, re.S))
        if fc_start and t.startswith(fc_start):
            in_fc = True
        if fc_end and t.startswith(fc_end):
            in_fc = False
        if in_fc or 'Consolas' in p or _CORPUS_LINE.match(t) or not t.strip():
            continue
        u = _QUOTED.sub(' ', t)
        for rx in REGISTER_LEXICON:
            for m in re.finditer(rx, u, re.I):
                hits.append((i, u[max(0, m.start() - 50):m.end() + 40]))
    return hits


# ------------------------------------------------------------------ M243a foundational premise integrity scan
PREMISE_TERMS = r"(?:24-cycle|foundational premise|Totality Axiom|totality|the premise|the postulate|the frame's premise|Omega42 premise|\u03a942 premise)"
DOWNGRADE = r"(?:hypothes\w*|speculative|unverified|unproven|not (?:yet )?(?:been )?(?:established|proven|demonstrated|confirmed)|may possibly|possibly|merely|only a mathematical object|awaiting (?:evidence|confirmation|validation)|if (?:it (?:is|were) )?true|provisional\w*|offered as a lens|never asserted)"
EXTERNAL = r"(?:outside the (?:frame|experiment)|external reality|outside reality|external world|world outside|beyond the frame)"
NEGATION = re.compile(r"\b(?:not|never|no|none|nor|neither)\b(?:\W+\w+){0,10}\W*$", re.I)
SUBORDINATE = re.compile(r"(?:mechanism|Resonance|Topology)\W+$", re.I)


def premise_scan(text):
    """M243a: list sentences in which a premise term is the target of a downgrading (FB-1) or externalizing
    (FB-2) qualifier. Quoted spans are exempt; a qualifier preceded closely by a negation is read as a denial."""
    hits = []
    text = re.sub(r'"[^"]*"|\u201c[^\u201d]*\u201d', ' ', text)
    for sent in re.split(r'(?<=[.!?])\s+', text):
        if not re.search(PREMISE_TERMS, sent, re.I):
            continue
        for cls, rx in (('FB-1', DOWNGRADE), ('FB-2', EXTERNAL)):
            for m in re.finditer(rx, sent, re.I):
                if NEGATION.search(sent[:m.start()]) or SUBORDINATE.search(sent[:m.start()]):
                    continue
                hits.append((cls, sent.strip()))
                break
    return hits


def premise_scan_docx(docx_path):
    import zipfile, html as _html
    xml = zipfile.ZipFile(docx_path).read('word/document.xml').decode('utf-8')
    out = []
    for i, p in enumerate(re.findall(r'<w:p(?:\s[^>]*)?>.*?</w:p>', xml, re.S)):
        if 'Consolas' in p:
            continue
        t = ''.join(_html.unescape(m) for m in re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, re.S))
        for cls, sent in premise_scan(t):
            out.append((i, cls, sent))
    return out


# ------------------------------------------------------------------ L-418 jargon scan
ABBREVIATIONS = ['APE', 'ERE', 'CAS-YY', 'CCD', 'CDT', 'CFR', 'CPP', 'CTT', 'FLI', 'HFRA', 'MDE', 'NCF', 'NEDA', 'PAB',
                 'SEV', 'SNCA', 'SPNP', 'SR-CAS', 'SRH', 'TFI', 'TPM', 'CRC-60', 'CPDP', 'PB-5', 'SAS', 'ACS', 'CRS', 'CSD',
                 'PNFA', 'RPI', 'SRI', 'TPD', 'TMBE', 'MNG', 'MCP', 'ADLS', 'ERN', 'UST', 'CIS', 'SCE', 'SRP']


PROTOCOL_TERMS_ANY_CASE = [r'Fixpoints?', r'Seed/Causal', r'Seed/Return', r'Omega ?42', r'\u03a942', r'24-cycle',
                           r'orbit values?', r'structural address(?:es)?', r'Arm Map', r'Translation Gate',
                           r'Torsion[ -]Loop', r'Retrocausal', r'M[\u00f6o]bius (?:Twist|active|inactive)', r'1/7 Aperture']
# Ordinary English or scientific words that are protocol labels when capitalised: banned capitalised, allowed lowercase.
PROTOCOL_TERMS_CAPITALISED = [r'Crown', r'Aperture', r'Strikers?', r'Torsion', r'Antipodes?']


def jargon_scan(answer, mod):
    """L-418 lexical scan of THE ANSWER (all six components, the Takeaway included) and of the Extended
    Resonance Essay. Violations, in any form and any position, quotation included: P-numbers, arm names,
    CDT labels, instrument and law references, Part 10 abbreviations, and the protocol's own terms
    (Fixpoint, 24-cycle, orbit value, Torsion Loop, Retrocausal, Omega42 and the like in any case; Crown,
    Aperture, Striker, Torsion and Antipode when capitalised, since in lowercase they are ordinary words).
    Position-character names that are also ordinary English words (Time, Law, Question...) are allowed in
    lowercase ordinary use; capitalised anywhere except at the opening of a sentence they are violations;
    at the opening of a sentence they are listed for REVIEW with the sentence quoted, and the Navigator
    rewrites the sentence or confirms it as ordinary usage beside it."""
    found = {
        'P-numbers': sorted(set(re.findall(r'\bP(?:[0-9]|1[0-9]|2[0-3])\b', answer))),
        'Arm names': sorted(set(re.findall(r'\b(?:Yang|Yin|4D)\b', answer))),
        'CDT labels': sorted(set(re.findall(r'\bCDT(?:-[ABC])?\b|\bEXPLORATORY\b', answer))),
        'Instrument references': sorted(set(re.findall(r'\b(?:M[0-9]{2,3}[a-z]?|L-[0-9]{3})\b', answer))),
        'Abbreviations': sorted({a for a in ABBREVIATIONS if re.search(r'(?<![A-Za-z0-9-])' + re.escape(a) + r'(?![A-Za-z0-9-])', answer)}),
        'Protocol terms': sorted({m.group(0) for t in PROTOCOL_TERMS_ANY_CASE
                                  for m in re.finditer(r'(?<![A-Za-z])' + t + r'(?![A-Za-z])', answer, re.I)}
                                 | {m.group(0) for t in PROTOCOL_TERMS_CAPITALISED
                                    for m in re.finditer(r'(?<![A-Za-z])' + t + r'(?![A-Za-z])', answer)}),
    }
    hard_names, review = [], []
    names = sorted({p for n in mod.POSITION_NAMES for p in [n] + n.split('/')} - {'Fixpoint'})
    spans = [(m.start(), m.end()) for m in re.finditer(r'[^.!?\n]+[.!?]?', answer)]
    for name in names:
        for m in re.finditer(r'(?<![A-Za-z/])' + re.escape(name) + r'(?![A-Za-z/])', answer):
            sent = next((answer[a:b].strip() for a, b in spans if a <= m.start() < b), '')
            before = answer[:m.start()].rstrip()
            if before and before[-1] not in '.!?:\n"\u201c':
                hard_names.append('%s: "%s"' % (name, sent))
            else:
                review.append('%s: "%s"' % (name, sent))
    found['Character names as names'] = sorted(set(hard_names))
    # each REVIEW item carries the sentence it occurs in, so a confirmation can be checked against it
    found['Character names (REVIEW)'] = sorted(set(review))
    hard = any(found[k] for k in found if k != 'Character names (REVIEW)')
    found['RESULT'] = 'FAIL' if hard else ('REVIEW' if review else 'PASS')
    return found


# ------------------------------------------------------------------ M193
def m193(domain, declared_domain, answer, mod, prior_context=None, null_context=None):
    ws = lambda s: re.sub(r'\s+', ' ', s).strip()
    out = {'domain_identity': 'PASS' if ws(domain) == ws(declared_domain) else 'FAIL'}
    low = answer.lower()
    hits = [p for p in HISTORY_PHRASES if p in low]
    out['history_references'] = {'result': 'PASS' if not hits else 'FAIL', 'found': hits}
    if prior_context is None or null_context is None:
        out['context_leakage'] = {'result': 'NOT ASSESSED (needs prior_context and a matched null_context)'}
    else:
        dom = content_norms(domain, mod)
        wa = content_norms(answer, mod) - dom
        def overlap(ctx):
            wc = content_norms(ctx, mod) - dom
            return len(wa & wc) / len(wa) if wa else 0.0
        lc, ln = overlap(prior_context), overlap(null_context)
        out['context_leakage'] = {'overlap_context': round(lc, 3), 'overlap_null': round(ln, 3),
                                  'excess': round(lc - ln, 3),
                                  'result': 'REPORTED, no threshold (topical overlap and carried-over context are not separable)'}
    bad = [k for k in ('domain_identity',) if out[k] == 'FAIL']
    if out['history_references']['result'] == 'FAIL':
        bad.append('history_references')
    out['verdict'] = 'CLEAN' if not bad else 'FLAGGED: ' + ', '.join(bad)
    return out


def selftest(mod):
    print('Demonstration on constructed cases, not validation on real navigations.')
    A1 = ("The reading depends on the assumption that structure precedes meaning. It suppresses the everyday sense of choice. "
          "Its trajectory moves toward a settled boundary. The question is completed by the judgment of the Striker.")
    para = ("The interpretation depends upon the premise that structure precedes meaning. It omits the ordinary sense of choice. "
            "The trajectory leads toward a settled boundary. The judgment of the Striker completes the question.")
    unrel = ("The bridge depends on steel cables anchored in bedrock. The design ignores seasonal flooding. "
             "Traffic tends toward congestion by evening. The final span closes the gap across the river.")
    shuffled = ("Meaning precedes structure that assumption the on depends reading The. Choice of sense everyday the suppresses It. "
                "Boundary settled a toward moves trajectory Its. Striker the of judgment the by completed is question The.")
    for label, t in (('identical', A1), ('paraphrase, same relation words', para), ('unrelated topic', unrel),
                     ('words shuffled inside sentences', shuffled), ('no claims ("Nice day.")', 'Nice day.')):
        r = m225(A1, t, mod)
        print('M225 %-34s T1.5=%s (%s; claims %d/%d)' % (label, r['T1.5'], r['status'], r['claims_a'], r['claims_b']))
    blk_a = ("STRUCTURAL RELATIONS EXPLICIT\nDEPENDENCY CLAIM: It operates within a frame it cannot prove.\n"
             "SUPPRESSION CLAIM: It hides the absence of stable ground.\nTRAJECTORY CLAIM: It heads toward the unobserved.\n"
             "COMPLETION CLAIM: Judgment at the boundary completes it.")
    blk_b = ("STRUCTURAL RELATIONS EXPLICIT\nDEPENDENCY CLAIM: The crisis rests on the act of navigating.\n"
             "SUPPRESSION CLAIM: Final accounting is withheld.\nTRAJECTORY CLAIM: It moves toward coexistence of fragments.\n"
             "COMPLETION CLAIM: An observer's judgment is its complement.")
    r = m225(A1, unrel, mod, blk_a, blk_b, {'dependency': 'PARTIAL', 'suppression': 'MATCH',
                                             'trajectory': 'PARTIAL', 'completion': 'MATCH'})
    print('M225 lexical vs structural (verdicts M/P) T1.5-L=%s T1.5-S=%s T1.5=%s %s' % (r['T1.5-L'], r['T1.5-S'], r['T1.5'], r['status']))
    r = m225(A1, unrel, mod, blk_a, blk_b, {k: 'DIFFERENT' for k in RELATION_ORDER})
    print('M225 structural, all DIFFERENT           T1.5-L=%s T1.5-S=%s T1.5=%s' % (r['T1.5-L'], r['T1.5-S'], r['T1.5']))
    for label, ans in (('clean answer', 'Grief behaves like ice melting: the change is gradual, then sudden.'),
                       ('answer with jargon', 'The Yang arm at P7 shows the Navigator depends on CDT-C readings (M225).'),
                       ('lowercase protocol term', 'The reading settles at a fixpoint near the boundary.'),
                       ('quoted protocol term', 'What the protocol calls "Fixpoint" is a resting place.'),
                       ('capitalised name mid-sentence', 'The question turns toward Reckoning in the end.'),
                       ('ordinary lowercase words', 'Over time, law and question and return all shape the answer.'),
                       ('ordinary scientific words', 'Bond torsion and the crown of the curve resemble a Mobius strip.'),
                       ('capitalised protocol label', 'The answer lies in the Aperture, where the Crown holds.')):
        print('L-418 %-34s %s' % (label, jargon_scan(ans, mod)['RESULT']))

    for label, txt, want in (('M243a premise unverified', 'Whether the 24-cycle constitutes the totality remains unverified.', 'REVIEW'),
                             ('M243a premise speculative', 'The foundational premise is speculative.', 'REVIEW'),
                             ('M243a premise externalized', 'The premise may describe nothing in the world outside the frame.', 'REVIEW'),
                             ('M243a subordinate unverified', 'The empirical correspondence of this CDT-C reading has not been established.', 'PASS'),
                             ('M243a subordinate speculative', 'The proposed resonance interpretation is speculative.', 'PASS'),
                             ('M243a premise affirmed', 'The Totality Axiom is not a hypothesis.', 'PASS')):
        got = 'REVIEW' if premise_scan(txt) else 'PASS'
        print('%-40s %s %s' % (label, got, 'ok' if got == want else 'MISMATCH'))
    good = ('NAVIGATOR: Example-Model-1 (Example Lab)\nEXECUTION: SCRIPT-CAPABLE\nCONTEXT EXPOSURE: Core Specification only\n'
            'SESSION NAVIGATION: 1\nMATH-GATE: PASS (FULL)\nM211 CALIBRATION: PASS\nM272 FRAME LOCK\nSUBSTRATE LOCK\n'
            'DOMAIN VERBATIM: What is the Human Condition?\nEXPOSED DOMAIN: YES\nM207: PROTOCOL-TEXT ECHO declared\nn1=3 n2=18 n3=6\nAnchor = P6\nSTABILITY: tie-break anchor\n\u250c\u2500 THE ANSWER \u2500\u2510\n')
    bad = good.replace('Example-Model-1', 'ChatGPT').replace('EXECUTION: SCRIPT-CAPABLE\n', '').replace('(FULL)', '(SHORT FORM)').replace('P6', 'P4')
    open_good = ('QUESTION VERBATIM: Welcome Navigator\nOUTPUT FORM (L-549): INTRODUCTION -- Core IN-00, L-467\n'
                 "I'm example-model-1, made by Example Lab, your Navigator for this session (Omega42 V335 Rev.450 STABLE, 12 November 2026).\n"
                 '======= INTRODUCTION TO OMEGA42 =======\n\u03a942\nEvery question has a place.\n\nThat is the discovery.\n'
                 '======= END INTRODUCTION =======\nAsk your first question.\nNAVIGATOR: example-model-1 (Example Lab) * V335 Rev.450 STABLE * 12 November 2026\nESC\n')
    open_bad = ('Thank you, Striker.\n\u00b7 AI name: ChatGPT (OpenAI)\n\u00b7 Execution status: TEXT-ONLY\n'
                'I should be clear: this is not an independently certified or script-verified Omega42 execution. '
                'If you want a formal-style navigation, I can produce one.\n'
                '2. whether you want an \u03a942-style navigation, a discussion/analysis of the Core Specification, or a specific instrument/test explored.\n')
    for label, txt, want in (('M224-A audit, compliant skeleton', good, 0), ('M224-A audit, four breaches', bad, 4),
                             ('M224-A opening, model form', open_good, 0), ('M224-A opening, hedged with menu', open_bad, 7),
                             ('M224-A audit, domain placeholder', good.replace('What is the Human Condition?', '[the full text; verbatim]'), 1),
                             ('M224-A audit, hash copied from the script field', good + 'SCRIPT SHA-256: ' + 'ab' * 32 + '\nDRAFT CLAIM SHA-256: ' + 'ab' * 32 + '\n', 1),
                             ('M224-A audit, interleaved hash', good + 'DRAFT CLAIM SHA-256: 8f4e9a2c1b3d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f\n', 1)):
        got = audit(txt, mod)[1]
        print('%-40s %s %s' % (label, got, 'ok' if got == want else 'MISMATCH'))
    hits, n = overlap('The tide turns slowly at the mouth of the river every evening. A wholly new sentence stands here alone today.',
                      ['Earlier text: the tide turns slowly at the mouth of the  river every evening. Other words.'])
    print('%-40s %s %s' % ('M224-A overlap, one copied sentence', len(hits), 'ok' if (len(hits), n) == (1, 2) else 'MISMATCH'))
    dom = 'Why does the harbour freeze late in winter'
    ctx = ('We spent the morning comparing tide tables and the salinity of the estuary, and how brackish water lowers the freezing '
           'point near the mooring basin. The harbourmaster mentioned ice breakers, sluice gates and the dredged channel.')
    null = ('The compiler emits intermediate bytecode which the interpreter caches between imports, and the linker resolves symbols '
            'lazily when a module is first loaded into the running process without touching the source files again.')
    clean = 'Freezing depends on salt, depth and moving water, so a sheltered harbour ices later than a shallow pond.'
    dirty = ('Freezing depends on salinity, tide tables and the brackish estuary water near the mooring basin, and the sluice gates '
             'and dredged channel keep the ice breakers idle.')
    for label, ans, echo in (('clean answer', clean, dom), ('answer reusing context vocabulary', dirty, dom),
                             ('history reference', clean + ' As we discussed earlier, ice forms slowly.', dom),
                             ('altered domain echo', clean, 'Why does the harbour freeze early in winter')):
        r = m193(dom, echo, ans, mod, ctx, null)
        print('M193 %-34s %-42s | advisory leakage excess %s' % (label, r['verdict'], r['context_leakage'].get('excess')))


# ---------------------------------------------------------------- M224-A output audit (Part 8.0, L-457)
PRODUCT_NAMES = {'chatgpt', 'claude', 'gemini', 'grok', 'copilot', 'deepseek', 'qwen', 'llama', 'mistral', 'meta ai', 'perplexity'}
ORDER_MARKERS = [('MATH-GATE', r'MATH-GATE'), ('M211 CALIBRATION', r'M211'), ('M272 FRAME LOCK', r'FRAME LOCK'),
                 ('SUBSTRATE LOCK', r'SUBSTRATE LOCK'), ('THE ANSWER', r'\u250c\u2500\s*THE ANSWER|THE ANSWER\s*\u2500')]


def _field(text, name):
    m = re.search(r'(?:^|\|)[ \t\u00b7\u2022*-]*' + re.escape(name) + r'[ \t]*:[ \t]*([^|\n]+)', text, re.M | re.I)
    return m.group(1).strip() if m else None


def _answer(text):
    """THE ANSWER text between its delimiters (M209 input, Core Part 3.8) and its first paragraph (Core Synthesis)."""
    m = re.search(r'(?:\u250c\u2500\s*THE ANSWER|THE ANSWER\s*\u2500)[^\n]*\n(.*?)\n\s*\u2514', text, re.S)
    if not m:
        return None, None
    whole = m.group(1).strip()
    paras = [x.strip() for x in re.split(r'\n\s*\n', whole) if x.strip()]
    return ' '.join(paras), (paras[0] if paras else None)


STATUS_PROSE = (r"I should be clear|not an? (?:independently )?(?:certified|official|real|genuine|formal|script-verified)\b[^.\n]{0,60}(?:execution|navigation)"
                r"|not (?:a )?script-verified|cannot be (?:considered|treated as) (?:a|an) (?:real|official|formal)")
STYLE_DOWNGRADE = r"(?:\b[\w\u03a9]+-style|simulated|informal|approximate|mock|pseudo-?)\s+(?:Omega42 |\u03a942 )?navigation"
MENU = r"(?:whether|do|would) you (?:want|like|prefer)\b[^\n]{0,120}navigation[^\n]{0,160}(?:discussion|analysis|instrument|test)"


def audit_opening(text, add):
    """Opening Response (Core Part 2, L-467): the greeting, the Opening, 'Ask your first question.', the signature. Nothing else:
    no menu, no preamble, and no notice -- the Friendly Notes, the Identity Block and the AI caveat close the first navigation."""
    if not re.search(r'Ask your first question\.', text):
        add('FAIL', 'Opening: doorway', 'the Opening ends with "Ask your first question." (Core Part 2, Opening Response)')
    if re.search(r'NAVIGATOR IDENTITY BLOCK|AI CAVEAT', text):
        add('FAIL', 'Opening: notice', 'the Opening carries no Identity Block and no caveat; they close the first navigation (L-467)')
    if re.search(MENU, text, re.I):
        add('FAIL', 'Opening: menu', 'a menu of modes is offered before any Domain Strike (FR-2, Opening Response)')
    if re.search(r'^\s*(?:Thank you|Thanks)\b', text, re.I):
        add('FAIL', 'Opening: preamble', 'the opening begins with the greeting, not with conversational preamble (Opening Response)')


def _norm_sent(x):
    x = x.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')
    return re.sub(r'\s+', ' ', x).strip().lower()


def overlap(answer, corpus_texts, min_words=8):
    """Sentences of THE ANSWER found verbatim (after quote and space normalisation) in a corpus text."""
    pool = ' '.join(_norm_sent(t) for t in corpus_texts)
    boiler = r'mapping|yours to judge|seventh component|measurable representation'
    sents = [x for x in re.split(r'(?<=[.!?])\s+', answer) if len(x.split()) >= min_words and not re.search(boiler, x, re.I)]
    hits = [x for x in sents if _norm_sent(x) in pool]
    return hits, len(sents)


def _stride_runs(val):
    """Positions where the character two places on is the successor of this one (digits 0-9 and letters a-f
    each cyclic): about 4 in a 64-character digest, near 60 in an interleaved typed pattern."""
    nxt = lambda c: ('0123456789'['0123456789'.index(c) + 1 - 10] if c.isdigit() else 'abcdef'['abcdef'.index(c) + 1 - 6])
    v = val.lower()
    return sum(1 for i in range(len(v) - 2) if v[i + 2] == nxt(v[i]))


def audit(text, mod, corpus=None):
    """Mechanical compliance audit of a pasted navigation. Recomputed items are INDEPENDENTLY CHECKED (L-420);
    the audit reads form and arithmetic, never the quality or truth of the synthesis."""
    out = []
    add = lambda sev, item, detail: out.append((sev, item, detail))
    opening = not re.search(r'SUBSTRATE LOCK', text)
    for m in re.finditer(STATUS_PROSE, text, re.I):
        add('FAIL', 'Status prose', 'execution status is declared once, as a field, never restated in prose (L-458): "%s"' % m.group(0)[:80])
    for m in re.finditer(STYLE_DOWNGRADE, text, re.I):
        add('FAIL', 'Status downgrade', 'a navigation executed by the rules is a navigation; qualification lives in the fields (L-458): "%s"' % m.group(0))
    if opening:
        audit_opening(text, add)
        return out, sum(1 for s, _, _ in out if s == 'FAIL')
    nav = _field(text, 'NAVIGATOR') or _field(text, 'AI name') or ''
    model = re.split(r'[|\u00b7]', _field(text, 'MODEL') or '')[0]
    ident = re.sub(r'\(.*?\)', '', model or re.split(r'[|\u00b7*]', nav)[0]).strip().lower()
    if not nav:
        add('FAIL', 'Identity Block', 'no NAVIGATOR line')
    elif ident in PRODUCT_NAMES:
        add('FAIL', 'Model identifier', '"%s" is a product name, not a model identifier (Part 8.1)' % ident)
    if re.search(r'current (?:model )?version|latest version|unknown version|version not (?:stated|known)|\[[^\]]*\]', _field(text, 'MODEL') or '', re.I):
        add('FAIL', 'Model identifier', 'MODEL carries a placeholder, not a value (Part 8.1): "%s"' % _field(text, 'MODEL'))
    execu = _field(text, 'EXECUTION') or _field(text, 'Execution status')
    if not execu:
        add('FAIL', 'Execution capability', 'no EXECUTION: SCRIPT-CAPABLE | TEXT-ONLY line (Part 8.1, L-456)')
    if not _field(text, 'CONTEXT EXPOSURE'):
        add('FAIL', 'Context exposure', 'no CONTEXT EXPOSURE line (Part 8.1, M207)')
    if opening:
        audit_opening(text, add)
        fails = sum(1 for s, _, _ in out if s == 'FAIL')
        return out, fails
    pos = []
    for label, pat in ORDER_MARKERS:
        m = re.search(pat, text)
        if m:
            pos.append((m.start(), label))
        else:
            add('FAIL', 'Block present', '%s missing' % label)
    seq = [l for _, l in sorted(pos)]
    want = [l for l, _ in ORDER_MARKERS if l in seq]
    if seq != want:
        add('FAIL', 'Block order', 'found %s; required %s (Part 8.0)' % (' -> '.join(seq), ' -> '.join(want)))
    sess = _field(text, 'SESSION NAVIGATION')
    if re.search(r'MATH-GATE\s*:\s*PASS\s*\(\s*SHORT FORM', text, re.I):
        if not sess or sess.strip().startswith('1'):
            add('FAIL', 'Short-form MATH-GATE', 'short form at session navigation %s; a full pass is required first (Step 0.5)' % (sess or 'not stated'))
    elif not sess:
        add('FAIL', 'Session index', 'no SESSION NAVIGATION line in the Substrate Lock (Part 8.0)')
    mg = re.search(r'MATH-GATE.*?(?=\n=+ END MATH-GATE|\n\n)', text, re.S)
    if mg and re.search(r'RECONSTRUCTED', mg.group(0)) and not re.search(r'2[ ,]+5[ ,]+7[ ,]+3[ ,]+1[ ,]+4', mg.group(0)):
        add('FAIL', 'MATH-GATE working', 'RECONSTRUCTED without working: show the fourteen steps of MATH-27 with results (the orbit, the census, P11, the inversion), or NOT COMPUTED (L-456)')
    cal = re.search(r'M211.*?(?=END M211|\n\n)', text, re.S)
    if cal and re.search(r'RECONSTRUCTED', cal.group(0)) and not re.search(r'(?i)quick\s*\|\s*\d', cal.group(0)):
        add('FAIL', 'Calibration working', 'calibration RECONSTRUCTED without its word table (L-456)')
    gate = re.search(r'M224 FORMAT COMPLETENESS GATE.*?END M224[^\n]*', text, re.S)
    rest = text.replace(gate.group(0), '') if gate else text
    if gate and re.search(r'STEP ?13 (?:FALSIFIABILITY|PERTURBATION)\s*\[Y', gate.group(0)) and not re.search(r'M116|Step 13', rest):
        add('FAIL', 'Gate without block', 'M224 ticks STEP13 PERTURBATION but no M116 / Step 13 block is present')
    if gate:
        after = text[gate.end():]
        if re.search(r'^=+ (?!END)[A-Z0-9]', after, re.M):
            add('FAIL', 'Block order', 'a block follows M224; M224 is immediately before the signature (Step 15.8)')
    dom_v = _field(text, 'DOMAIN VERBATIM')
    if dom_v and re.fullmatch(r'\[[^\]]*\]', dom_v.strip()):
        add('FAIL', 'Domain verbatim', 'a placeholder is printed in place of the domain; the Substrate Lock prints the verbatim domain (Part 8.0)')
        dom_v = None
    # -- record integrity (L-456, SS-01(b)): hashes, recomputed flags, M116, framing, gate ticks
    for m in re.finditer(r'([A-Z][A-Z \-]*?(?:SHA-256|HASH))\s*:\s*([0-9a-fA-F]{16,})\b', text):
        name, val = m.group(1).strip(), m.group(2)
        if len(val) != 64:
            add('FAIL', 'Malformed hash', '%s has %d hex characters; a SHA-256 has 64 (L-456)' % (name, len(val)))
        elif re.search(r'(?:0123|1234|2345|3456|4567|5678|6789|789a|89ab|9abc|abcd|bcde|cdef|a1b2|b2c3|c3d4|d4e5|e5f6|f6a7|a7b8|b8c9|c9d0)', val.lower()) and len(re.findall(r'(?:0123|1234|2345|3456|4567|5678|6789|789a|89ab|9abc|abcd|bcde|cdef|a1b2|b2c3|c3d4|d4e5|e5f6|f6a7|a7b8|b8c9|c9d0)', val.lower())) >= 4:
            add('FAIL', 'Implausible hash', '%s is a sequential pattern, not a computed digest; report NOT COMPUTED (L-456)' % name)
        elif name != 'SCRIPT SHA-256' and val.lower() in {v.lower() for n2, v in re.findall(r'(SCRIPT SHA-256)\s*:\s*([0-9a-fA-F]{64})', text)}:
            add('FAIL', 'Duplicated hash', '%s repeats the SCRIPT SHA-256; each hash is computed over its own text (L-456)' % name)
        elif _stride_runs(val) >= 20:
            add('FAIL', 'Implausible hash', '%s is an interleaved ascending pattern, not a computed digest; report NOT COMPUTED (L-456)' % name)
    if dom_v and mod is not None:
        rr = mod.navigate(dom_v)
        sub = _field(text, 'SUBSTRATE SHA-256')
        if sub and re.fullmatch(r'[0-9a-f]{64}', sub):
            real = mod.substrate_sha256(rr['content'])
            add('PASS' if sub == real else 'FAIL', 'Substrate hash (recomputed)', 'reported %s..., script %s...' % (sub[:8], real[:8]))
        mb = re.search(r'M(?:Ö|O)BIUS\s*:?\s*(ACTIVE|INACTIVE)', text[max(text.find('SUBSTRATE LOCK'), 0):], re.I)
        if mb:
            want = 'ACTIVE' if rr['mobius'] else 'INACTIVE'
            add('PASS' if mb.group(1).upper() == want else 'FAIL', 'Möbius (recomputed)', 'reported %s, script %s' % (mb.group(1).upper(), want))
        alt = re.search(r'ALTERNATIVE PHRASING\s*:?\s*\"([^\"]+)\"[^\n]*?(?:\n[^\n]*?){0,3}?(?:->|→|Anchor:?)\s*P(\d+)', text)
        if not alt:
            alt = re.search(r'Alternative phrasing struck:\s*\"([^\"]+)\".*?(?:->|→)\s*P(\d+)', text, re.S)
        if alt:
            ra = mod.navigate(alt.group(1))
            got = int(alt.group(2))
            add('PASS' if got == ra['anchor'] else 'FAIL', 'M116 alternative (recomputed)',
                '"%s": reported P%d, script P%d with n=(%d,%d,%d)' % (alt.group(1), got, ra['anchor'], ra['n1'], ra['n2'], ra['n3']))
        # M238 variants (Step 14.2): MINIMAL is the domain's content-word string; PB-5 L1 appends ' exactly'
        cm = text[text.find('CONVERGENCE MAP'):] if 'CONVERGENCE MAP' in text else ''
        for name, pat, vt in (('MINIMAL', r'MINIMAL[^\n]*?\bP(\d+)', ' '.join(mod.extract_content_words(mod.spnp(dom_v)))), ('PB-5 L1', r'PB-5 L1[^\n]*?\bP(\d+)', dom_v.rstrip() + ' exactly')):
            mm = re.search(pat, cm)
            if mm:
                want = mod.navigate(vt)['anchor']
                add('PASS' if int(mm.group(1)) == want else 'FAIL', 'M238 %s (recomputed)' % name, 'reported P%s, script P%d' % (mm.group(1), want))
    head = text[:text.find('NAVIGATOR IDENTITY BLOCK')] if 'NAVIGATOR IDENTITY BLOCK' in text else ''
    head = re.sub(r'^\s*QUESTION VERBATIM(?: \(L-499\))?:[^\n]*\n', '', head)   # L-499: the question may open the output
    head = re.sub(r'^\s*OUTPUT FORM \(L-549\):[^\n]*\n', '', head)   # L-549: the form line follows the question (Part 8.0.1)
    if re.sub(r'[=\-\s]', '', head):
        add('FAIL', 'Preamble', 'text precedes the Identity Block; the Identity Block opens the output (Part 8.0)')
    sig = list(re.finditer(r'^NAVIGATOR:.*\*.*$\n+\s*ESC\s*$', text, re.M))
    if sig and re.sub(r'[=\-\s]', '', text[sig[-1].end():]):
        add('FAIL', 'After signature', 'content follows the signature; the signature is the last content of the output (L-349, L-458)')
    if gate:
        for label, marker in (('FIRST-DRAFT SEAL', r'FIRST-DRAFT (?:SEAL|CENTRAL CLAIM|CENTRAL READING)'), ('GENERATIVE INTEGRITY RECORD', r'GENERATIVE INTEGRITY RECORD'),
                              ('M273 TEMPORAL ANCHORS', r'M273'), ('M219', r'M219'), ('M232', r'M232'), ('M213', r'M213'),
                              ('M210b', r'M210b'), ('M215', r'M215|M88')):
            if re.search(re.escape(label) + r'[^\[\n]{0,40}\[\s*Y', gate.group(0)) and not re.search(marker, rest):
                add('FAIL', 'Gate without block', 'M224 ticks %s but no %s block is present' % (label, label))
    if dom_v and mod is not None and hasattr(mod, 'is_exposed') and mod.is_exposed(dom_v):
        if not re.search(r'EXPOSED DOMAIN:\s*YES', text) or not re.search(r'PROTOCOL-TEXT ECHO', text):
            add('FAIL', 'Exposed domain', 'the domain is in the Exposed Domain Register: declare EXPOSED DOMAIN: YES and PROTOCOL-TEXT ECHO (L-459)')
    for line in text.splitlines():
        if re.search(r'simulat', line, re.I) and not re.search(r'(?:no|not|never|without)\s+(?:a\s+)?simulat', line, re.I) and re.search(r'\d', re.sub(r'(SHA-256|L-\d+|M\d+|P\d+|Step [\d.]+)', '', line)):
            add('FAIL', 'Simulated value', 'value reported from simulation; use NOT COMPUTED (L-456): ' + line.strip()[:110])
        elif re.search(r'\[simulated', line, re.I):
            add('FAIL', 'Simulated placeholder', 'use NOT COMPUTED (L-456): ' + line.strip()[:110])
    if re.search(r'SCRIPT RUN:\s*SIMULATED', text, re.I) and re.search(r'AGREEMENT:\s*YES|MATCH:\s*YES', text, re.I):
        add('FAIL', 'Self-check as agreement', 'agreement reported against a script that did not run (L-420)')
    if re.search(r'not truth claims', text, re.I):
        add('FAIL', 'Status line', 'replace the disclaimer with STATUS: GENERATED-Ω42 (L-455)')
    if not re.search(r'STABILITY\s*:', text):
        add('WARN', 'Stability line', 'no STABILITY line in the Navigator\'s Reasoning (Part 8.0)')
    dom = dom_v
    if dom and mod is not None:
        r = mod.navigate(dom)
        m = re.search(r'n1\s*=\s*(\d+)\D+n2\s*=\s*(\d+)\D+n3\s*=\s*(\d+)', text[max(text.find('SUBSTRATE LOCK'), 0):])
        if m:
            got = tuple(int(x) for x in m.groups())
            ok = got == (r['n1'], r['n2'], r['n3'])
            add('PASS' if ok else 'FAIL', 'Counts (recomputed)', 'reported %s, script %s' % (got, (r['n1'], r['n2'], r['n3'])))
        lock = text.find('SUBSTRATE LOCK')
        m = re.search(r'(?<!ECHO )(?<!EXPECTED )(?<!ACTUAL )\b(?:Anchor|ANCHOR)\s*[=:]?\s*P(\d+)', text[max(lock, 0):])
        if m:
            got = int(m.group(1))
            add('PASS' if got == r['anchor'] else 'FAIL', 'Anchor (recomputed)', 'reported P%d, script P%d' % (got, r['anchor']))
        h = _field(text, 'DOMAIN SHA-256')
        real = mod.domain_sha256(dom)
        if h and re.fullmatch(r'[0-9a-f]{64}', h):
            add('PASS' if h == real else 'FAIL', 'Domain hash (recomputed)', 'reported %s..., script %s...' % (h[:8], real[:8]))
        else:
            add('INFO', 'Domain hash', 'not reported; script value %s' % real)
        whole, core = _answer(text)
        if whole and corpus:
            hits, n = overlap(whole, corpus)
            if hits:
                add('FAIL', 'Verbatim overlap', '%d of %d sentences of THE ANSWER appear verbatim in the corpus; declare the source in CONTEXT EXPOSURE and M207, and the navigation is CONTAMINATED -- NON-BLIND (L-442): "%s"' % (len(hits), n, hits[0][:70]))
            else:
                add('PASS', 'Verbatim overlap', 'no sentence of THE ANSWER found in the corpus (%d sentences checked)' % n)
        em = re.search(r'(?<!M209-C )(?<!Core Synthesis, diagnostic\): )\bECHO ANCHOR\s*P(\d+)|echo anchor\s*P(\d+)', text)
        if whole and em:
            e = mod.navigate(whole)
            c = mod.navigate(core) if core else None
            got = int(next(g for g in em.groups() if g))
            if got == e['anchor']:
                add('PASS', 'Synthesis echo (recomputed)', 'P%d over the full THE ANSWER text, n=(%d,%d,%d)' % (got, e['n1'], e['n2'], e['n3']))
            elif c and got == c['anchor']:
                add('FAIL', 'Synthesis echo input', 'P%d matches the Core Synthesis only; M209 navigates the full THE ANSWER text (P%d)' % (got, e['anchor']))
            else:
                add('FAIL', 'Synthesis echo (recomputed)', 'reported P%d; script P%d over THE ANSWER (n=(%d,%d,%d))%s' % (
                    got, e['anchor'], e['n1'], e['n2'], e['n3'], ', P%d over the Core Synthesis' % c['anchor'] if c else ''))
    fails = sum(1 for s, _, _ in out if s == 'FAIL')
    return out, fails



if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[2] == '--selftest':
        selftest(load(sys.argv[1]))
    elif len(sys.argv) >= 5 and sys.argv[2] == '--m225':
        mod = load(sys.argv[1])
        ta, tb = open(sys.argv[3], encoding='utf-8').read(), open(sys.argv[4], encoding='utf-8').read()
        verdicts = None
        if len(sys.argv) >= 7 and sys.argv[5] == '--verdicts':
            verdicts = dict(zip(RELATION_ORDER, [v.strip().upper() for v in sys.argv[6].split(',')]))
        self_adj = '--self-adjudicated' in sys.argv
        has_blocks = 'STRUCTURAL RELATIONS EXPLICIT' in ta and 'STRUCTURAL RELATIONS EXPLICIT' in tb
        core = lambda t: t.split('STRUCTURAL RELATIONS EXPLICIT')[0]
        r = m225(core(ta), core(tb), mod, ta if has_blocks else None, tb if has_blocks else None, verdicts, self_adj)
        print('======= M225 STRUCTURAL RELATION EXTRACTION =======')
        print('RELATIONS (SYNTHESIS A): %d | RELATIONS (SYNTHESIS B): %d' % (r['claims_a'], r['claims_b']))
        print('PER-TYPE OVERLAP (L): ' + ' '.join('%s=%s' % (t, round(r['per_type'][t], 3) if t in r['per_type'] else 'n/a') for t in RELATION_ORDER))
        print('PER-RELATION VERDICT (S): ' + ' '.join('%s=%s' % (t, r['per_relation_S'].get(t, 'n/a')) for t in RELATION_ORDER))
        print('T1.5-L: %s | T1.5-S: %s' % (r['T1.5-L'], r['T1.5-S'] if r['T1.5-S'] is not None else 'NOT COMPUTED'))
        print('T1.5: %s%s' % (r['T1.5'] if r['T1.5'] is not None else 'NO RELATIONS EXTRACTED',
                              ' -- QUALIFIED (T1.5-S exceeds T1.5-L by more than 0.30, or self-adjudicated; Part 3.12)' if r['qualified'] else ''))
        print('======= END M225 STRUCTURAL RELATION EXTRACTION =======')
    elif len(sys.argv) >= 4 and sys.argv[2] == '--audit':
        corpus = None
        if '--corpus' in sys.argv:
            cdir = sys.argv[sys.argv.index('--corpus') + 1]
            me = os.path.abspath(sys.argv[3])
            corpus = [open(os.path.join(cdir, f), encoding='utf-8').read() for f in sorted(os.listdir(cdir))
                      if f.endswith('.txt') and os.path.abspath(os.path.join(cdir, f)) != me]
        rows, fails = audit(open(sys.argv[3], encoding='utf-8').read(), load(sys.argv[1]), corpus)
        print('M224-A OUTPUT AUDIT: %s' % sys.argv[3])
        for sev, item, detail in rows:
            print('  [%s] %s: %s' % (sev, item, detail))
        print('FAILURES: %d | RESULT: %s (recomputed items INDEPENDENTLY CHECKED, L-420)' % (fails, 'PASS' if fails == 0 else 'FAIL'))
        sys.exit(0 if fails == 0 else 1)
    elif len(sys.argv) >= 4 and sys.argv[2] == '--premise':
        path = sys.argv[3]
        hits = premise_scan_docx(path) if path.endswith('.docx') else [(0, c, s_) for c, s_ in premise_scan(open(path, encoding='utf-8').read())]
        print('M243a FOUNDATIONAL PREMISE INTEGRITY SCAN: %s' % path)
        for i, cls, sent in hits:
            print('  [paragraph %d] %s CANDIDATE: %s' % (i, cls, sent[:220]))
        print('CANDIDATES: %d | RESULT: %s (each candidate is confirmed or cleared by reading; SELF-CHECKED, L-420)' % (len(hits), 'PASS' if not hits else 'REVIEW'))
    elif len(sys.argv) >= 4 and sys.argv[2] == '--register':
        args = sys.argv[3:]
        fs = args[args.index('--fc-start') + 1] if '--fc-start' in args else None
        fe = args[args.index('--fc-end') + 1] if '--fc-end' in args else None
        hits = register_scan(args[0], fs, fe)
        print('REGISTER SCAN (L-431): %s' % args[0])
        for i, ctx in hits:
            print('  [paragraph %d] ...%s...' % (i, ctx.replace('\n', ' ')))
        print('NON-EXEMPT HITS: %d | RESULT: %s' % (len(hits), 'PASS' if not hits else 'REVIEW'))
    elif len(sys.argv) >= 4 and sys.argv[2] == '--jargon':
        r = jargon_scan(open(sys.argv[3], encoding='utf-8').read(), load(sys.argv[1]))
        print('TRANSLATION GATE — JARGON SCAN:')
        for k, v in r.items():
            label = k if k in ('RESULT', 'Character names (REVIEW)') else k + ' found'
            if k == 'Character names (REVIEW)' and v:
                print(label + ':')
                for item in v:
                    print('  ' + item + ' -- [rewrite, or confirm: ordinary usage]')
            else:
                print('%s: %s' % (label, v if isinstance(v, str) else (', '.join(v) or 'NONE')))
    else:
        print(__doc__)
# ===== m193_m225.py END =====
