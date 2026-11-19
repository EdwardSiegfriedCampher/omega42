#!/usr/bin/env python3
"""frame_audit.py -- M286 Frame Intrusion Scan (Core Part 3.31), the lexical layer of FB-2.

Under F-04, F-05, L-421 and L-433 there is no ontological OUTSIDE: the INSIDE is the ontological premise of the
thought experiment, and what appears exterior is a perspective within it. M286 flags sentences in which an outside is
introduced as a court (a place where the premise is judged, proven or refuted), as an independent ground (something
that holds "independently of the frame"), or as an external referent of a ray ("external counterpart", "world outside"), and sentences that treat a
perspective as a veil over something beyond the totality ("cannot bypass", "whatever lies beneath").
Under L-491 it flags the scientific method set up as a trial of the protocol's operation (TRIAL): a comparative study called
decisive or principal, a figure or reading gated on one, the protocol's potential graded by one; a sentence that states the
rule against this is not flagged.
Under L-490 it also flags court vocabulary (VERDICT): a measure said to support, validate, confirm or falsify the
premise or Omega42, a reading called "provisionally true", a comparison called a stress test, or a count called
validations of Omega42. A sentence that states the rule against such verdicts is not flagged.
A sentence labelled [COMPARATIVE] reports another perspective in its own terms (F-10) and is not flagged.

Sentences that state the frame's own rule (there is no outside; no court outside is sought) are not intrusions.
Comparative perspectives (F-10), statements about how a model was trained, and the contingency of base 10 are
perspectives inside the frame and are not flagged.

The scan is a lexical layer: it finds candidates, and the Navigator judges each one (L-378 is untouched).

Usage:
    python3 tools/frame_audit.py FILE [FILE ...]      (.txt, .md or .docx)
    python3 tools/frame_audit.py --selftest
"""
import re, sys, zipfile

PATTERNS = [
    ('COURT',       r"\boutside the frame\b[^.]{0,80}\b(judged|standards?|tested|evaluated|assessed|claim)"),
    ('COURT',       r"\b(proof|refutation|refute[sd]?|prove[sd]?|disprove[sd]?|verif(?:y|ied|ication))\b[^.]{0,40}\bof the premise\b"),
    ('COURT',       r"\bthe premise\b[^.]{0,40}\b(is|was|can be|cannot be|could be)\s+(proven|refuted|disproven|verified|falsified)\b"),
    ('COURT',       r"\bordinary standards of the field\b"),
    ('INDEPENDENT', r"\bindependent(?:ly)? of the frame\b"),
    ('INDEPENDENT', r"\b(in|of) (the )?(real|actual) world\b"),
    ('INDEPENDENT', r"\bin reality\b"),
    ('INDEPENDENT', r"\bmetaphysical(?:ly)? (claim|fact|truth|reality)\b"),
    ('INDEPENDENT', r"\bstipulated and not derived\b"),
    ('INDEPENDENT', r"\babsolute non-being\b"),
    ('EXTERNAL',    r"\bexternal (counterpart|reference|referent|reality|world|standard|ground|authority|validation)\b"),
    ('EXTERNAL',    r"\bworld outside\b"),
    ('EXTERNAL',    r"\boutside (our|the) (immediate )?(grasp|system|cycle|structure)\b"),
    ('EXTERNAL',    r"\bwe require an external\b"),
    ('VEIL',        r"\bcannot bypass\b|\bwhatever lies (beneath|behind|beyond)\b|\bdirect view of reality\b|\braw contact\b|\breality (itself|as it is)\b|\bthing[- ]in[- ]itself\b"),
    ('VEIL',        r"\bentirely mediated by\b[^.]{0,60}\b(apparatus|perception|senses)\b"),
    ('VEIL',        r"\b(world|reality|universe|manifest\w*)\b[^.]{0,30}\bas (a |its |the )?shadow\b"),
    # L-490: court vocabulary -- a measure that grades, supports, validates, confirms or falsifies the premise or Omega42
    ('VERDICT',     r"\b(support(s|ed|ing)?|validat(e|es|ed|ing)|confirm(s|ed|ing)?|corroborat(e|es|ed|ing)|falsif(y|ies|ied)|refut(e|es|ed))\b[^.]{0,30}\b(the premise|the foundational premise|\u03a9 ?42|Omega ?42)\b(?! (Protocol|is|was|generated|content|reading))"),
    ('VERDICT',     r"\bprovisionally true\b"),
    ('VERDICT',     r"\bstress[- ]test(s|ed|ing)?\b"),
    ('VERDICT',     r"\bevidence (for|of) (the premise|\u03a9 ?42|Omega ?42)\b"),
    ('VERDICT',     r"\bvalidations? of (\u03a9 ?42|Omega ?42|the premise)\b"),
    ('VERDICT',     r"\b(\u03a9 ?42|Omega ?42|the premise|the protocol)\b[^.]{0,40}\b(is|are|has been|have been|was|stands at|stands|remains|reached|reaches|now)\s+(now\s+)?(scientifically\s+)?(validated|confirmed|supported|corroborated|falsified|refuted|proven|EMERGING|SUPPORTED|WELL-SUPPORTED|CONFIRMED|REFUTED)\b"),
    ('VERDICT',     r"\bscientifically (validated|confirmed|proven|verified|supported)\b"),
    # BF-02, BF-04, L-432: the premise is the ground, not a claim, hypothesis or conjecture awaiting evidence
    ('CLAIM',       r"\b(the premise|the foundational premise|the Totality Axiom|the Projection Premise)\b[^.]{0,30}\b(is|as|remains|stands as)\s+(only\s+|merely\s+|just\s+)?(a|an)\s+(claim|hypothesis|conjecture|assumption|speculation)\b"),
    ('CLAIM',       r"\b(claims?|claimed)\b\s+(that\s+)?(what\s+)?(the premise|the architecture|the Totality Axiom)\b|\bthe Companion claims\b|\bthe premise,? if true\b"),
    # L-515 (APE-151 R4; Companion 87.8): science used as a court over a held idea or a reading, and causal primacy
    ('SCIENCE',     r"\b(close to |nearly |practically )?unfalsifiable\b|\bnot falsifiable\b|\bin a (strong|weak) position\b|\bvalidation gate\b|"
                    r"\bmust (first )?be (scientifically )?(validated|tested|replicated|verified) before\b|\bearn(s|ed)? (that |its |the )?entitlement\b"),
    ('CAUSAL',      r"\b(consciousness|the mind|thoughts?|beliefs?|intentions?|the Striker's (?:judgment|thought|belief|choice))\b[^.]{0,40}\b(caus(?:e|es|ed|ing)|creat(?:e|es|ed|ing)|alter(?:s|ed|ing)?|chang(?:e|es|ed|ing))\b[^.]{0,40}"
                    r"\b(physical (?:reality|world|matter|systems?|laws?)|the laws of physics|the cycle|the arithmetic|the counts?)\b"),
    # L-491 (24 October 2026): the scientific method as a trial of the protocol's operation -- a comparative study called
    # decisive or principal, a reading or figure gated on one, the protocol's potential graded by one
    ('TRIAL',       r"\bdecisive (test|study|control|experiment)\b|\bthe (test|study) that (would|can|could) (decide|tell|show)\b|\bwhether the coordinate (carries|contributes) anything\b|"
                    r"\bprincipal (null|decoy)( test| explanation| comparison)?\b|\b(low|modest) on the present record\b|\bevery test (so far )?that could come back negative\b|"
                    r"\bquoted as evidence\b|\bon trial\b|\bearn(s|ed)? (that|its|the) reading\b|\bavenues? that look(s)? interesting and (is|are) not\b"),
    # APE-164 R3: metaphorical literalism -- a reading's analogy stated as fact
    ('LITERAL',     r"\b(the universe|reality|everything|all matter)\s+is\s+(just |only |nothing but |fundamentally |literally |really )?(a |made of |pure )?(vibrations?|frequency|frequencies|energy|sound)\b"),
]
# a sentence that states the rule against verdicts is not itself a verdict
# an EXTERNAL or INDEPENDENT candidate that states the rule against an outside (negated, or placed within the frame) is a mention
OUTSIDE_RULE = re.compile(r"\b(not|never|no|without|rather than|nor|instead of)\b[^.]{0,50}\b(external|independent|metaphysical)|"
                          r"\bwithin (the frame|\u03a9 ?42|Omega ?42|the totality)\b", re.I)
VERDICT_RULE = re.compile(r"\b(not|never|no|nor|neither|nothing|cannot|without)\b[^.]{0,120}\b(support|validat|confirm|corroborat|falsif|refut|provisionally true|stress[- ]test|evidence)|\bcourt vocabulary\b|\bL-490\b", re.I)
RULE = re.compile(r"\[COMPARATIVE\]|\bno (ontological |independent |ontologically independent )?outside\b|"
                  r"\bno (court|reviewer|rater|tribunal|authority)\b[^.]{0,30}\boutside\b|\bnot outside the world\b|"
                  r"\bwithout any outside\b|\bno sentence\b|\bis said to\b|\bnot\b[^.]{0,40}\bexternal reality\b|\babsolute non-being is not\b|\bnever (as )?a court\b|\b(FB-2|M286|frame intrusion)\b", re.I)
SCIENCE_RULE = re.compile(r"\b(never|nor|not a|no)\b[^.]{0,80}\b(prerequisite|reason|required|gate|court|tribunal)\b|\b(L-498|L-515)\b", re.I)
TRIAL_RULE = re.compile(r"\b(never|not|no|nor|neither|none)\b[^.]{0,90}\b(trial|decisive|principal|evidence|decid\w*|wait\w*|grad\w*)\b|\bL-491\b", re.I)
CAUSAL_RULE = re.compile(r"\b(not|never|no|nor|cannot|without|rather than|does not|do not)\b|\b(Bashar|Seth|Ra|lens|atlas|teach\w*|taught|C32|CT-S6)\b|\[COMPARATIVE", re.I)
TAG_C = re.compile(r"\[(CDT-C|ANALOGY|INTERPRETATION|COMPARATIVE)|\b(as an analogy|analog\w*|metaphor\w*|reads? as|read as)\b", re.I)
QUOTED = re.compile(r'"[^"]{1,160}"|\u201c[^\u201d]{1,160}\u201d')
CODE = re.compile(r"\(\(|\bdef \w+\(|\bfor \w+, \w+ in\b|#!|\bimport \w+|=====")

def text_of(path):
    if path.endswith('.docx'):
        x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
        paras = [''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', p)) for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S)]
        # embedded files (Core Appendix R, Companion Appendices C, N and X, the frozen scripts) are code and data, not prose
        return '\n'.join('' if (t.startswith('# ===== ') or t.startswith('#!/usr/bin/env')) else t for t in paras)
    return open(path, encoding='utf-8', errors='replace').read()

def sentences(text):
    for i, para in enumerate(text.split('\n'), 1):
        for s in re.split(r'(?<=[.!?])\s+', para):
            if s.strip(): yield i, s.strip()

def scan(text):
    hits = []
    for para, s in sentences(text):
        if CODE.search(s) or s.startswith('QUESTION VERBATIM:'): continue   # the Striker's own words, quoted exactly (L-499)
        bare = QUOTED.sub(' ', s)      # a phrase quoted in order to name it is a mention, not a use
        for kind, pat in PATTERNS:
            if re.search(pat, bare, re.I):
                if RULE.search(s): break
                if kind == 'VERDICT' and VERDICT_RULE.search(bare): break
                if kind == 'SCIENCE' and SCIENCE_RULE.search(bare): break
                if kind == 'TRIAL' and TRIAL_RULE.search(bare) and not re.search(r'\bquoted as evidence before\b', bare, re.I): break
                if kind == 'CAUSAL' and CAUSAL_RULE.search(bare): break
                if kind == 'LITERAL' and (CAUSAL_RULE.search(bare) or TAG_C.search(bare)): break
                if kind == 'CLAIM' and re.search(r"\b(not|never|no|none|nor|neither)\b[^.]{0,60}\b(claim|hypothesis|conjecture|assumption|speculation|if true)", bare, re.I): break
                if kind in ('EXTERNAL', 'INDEPENDENT') and OUTSIDE_RULE.search(bare): break
                if kind == 'VEIL' and re.search(r"\bphysical reality itself\b", bare, re.I) and not re.search(r"\bbeyond\b|\bbeneath\b|\bbehind\b", bare, re.I): break
                hits.append((para, kind, s)); break
    return hits

def report(path):
    hits = scan(text_of(path))
    print('M286 FRAME INTRUSION SCAN: %s | %d candidate(s)' % (path, len(hits)))
    for para, kind, s in hits:
        print('  [para %d] %-11s %s' % (para, kind, s[:220]))
    return hits

IDENTITY = re.compile(r'(?<![\w.])(-?\d+)\s*([*+x\u00d7])\s*(-?\d+)\s*=\s*(-?\d+)(?![\w.])')
def route(text):
    """the M323 gate (seq_0031 recommendations 1 and 2, adopted 23 October 2026): every identity a x b = c or a + b = c
    found in a text is sent to M323 and checked in Z, R, Z/9 and Z[phi]/9 before any reading of it is made"""
    import claimcheck as cc
    out = []
    for m in IDENTITY.finditer(text):
        expr = '%s%s%s=%s' % (m.group(1), '*' if m.group(2) in 'x*\u00d7' else '+', m.group(3), m.group(4))
        r = cc.identity(expr); out.append((expr, 'HOLDS' if r.count('HOLDS') == 4 else ('FAILS' if r.count('FAILS') == 4 else 'MIXED')))
    return out

def selftest():
    rt = route('He wrote 1 x 1 = 2, and 1 + 1 = 2, and 3*3=0 in the residues.')
    rok = rt == [('1*1=2', 'FAILS'), ('1+1=2', 'HOLDS'), ('3*3=0', 'MIXED')]
    print('%-90s %s' % ('M323 routing: identities found in a text are checked in every ring', 'ok' if rok else 'FAIL'))
    cases = [
        ("Outside the frame it is a correspondence claim judged by the ordinary standards of the field.", True),
        ("Because the protocol cannot bypass the Human Frame of Reference, it does not try.", True),
        ("Perception gives partial access, not raw contact with whatever lies beneath it.", True),
        ("Evidence is never proof of the premise.", True),
        ("CDT-A also holds independently of the frame.", True),
        ("The Antipode is an external counterpart, a world outside our immediate grasp.", True),
        ("We require an external reference to see it.", True),
        ("There is no ontological outside; what appears exterior is a perspective within.", False),
        ("No court outside the frame is sought or required.", False),
        ("The Antipode is the position at offset +12 on the same cycle.", False),
        ("In a comparative perspective (F-10), physics reads this differently.", False),
        ("Even complete support is never proof of the premise, and outside the frame it is a claim for the field.", True),
        ("In Omega42 nothing is not outside the world but one of its states.", False),
        ('A finding is said to be a claim "judged by the ordinary standards of the field".', False),
        ("This correspondence supports the premise at tier 4.", True),
        ("The hypothesis is provisionally true at CONFIRMED.", True),
        ("Omega42 has been stress-tested by external contributors.", True),
        ("Fifty runs count as validations of Omega42.", True),
        ("Omega42 has been validated by science.", True),
        ("The Amplituhedron shows the manifested world as shadow.", True),
        ("It must not require external validation to be considered or developed.", False),
        ("The stronger metaphysical claim needs its own argument within Omega42.", False),
        ("Consciousness participates in the actualisation of physical reality itself.", False),
        ("A metaphysical truth lies behind the frame.", True),
        ("The premise is a claim the Companion defends.", True),
        ("The Companion claims what the architecture means.", True),
        ("Every Navigator output treats the premise as the ground and none presents it as a claim awaiting evidence.", False),
        ("The protocol is now WELL-SUPPORTED by fifty runs.", True),
        ("This reading is scientifically confirmed.", True),
        ("A profile neither supports nor weakens the premise, which is the ground.", False),
        ("No measure grades, supports, validates, confirms or falsifies the premise (L-490).", False),
        ("Eight Navigators converged on P3; the Convergence Record reads BROAD.", False),
        ("It is close to unfalsifiable as stated, and so not in a strong position.", True),
        ("The reading must be scientifically validated before it can proceed.", True),
        ("Lack of testing is never a reason to remove an idea (L-498).", False),
        ("Your belief changes the laws of physics.", True),
        ("Consciousness creates physical reality.", True),
        ("Bashar teaches that consciousness creates physical reality.", False),
        ("No thought changes the counts or the arithmetic.", False),
        ("The universe is fundamentally vibration.", True),
        ("Reality is nothing but frequency.", True),
        ("Read as an analogy, the universe is vibration.", False),
        ("M267 is the decisive test of whether the coordinate carries anything.", True),
        ("The potential is low on the present record.", True),
        ("No idea's PROXIMITY is quoted as evidence before the sampled atlas runs.", True),
        ("Every test so far that could come back negative has come back at chance.", True),
        ("The scores that read resonance into a synthesis earn that reading against a null.", True),
        ("It never puts the premise on trial, since there is nowhere outside to stand.", False),
        ("No comparative study is called decisive, and no navigation waits on one (L-491).", False),
    ]
    ok = [bool(scan(t)) == want for t, want in cases] + [rok]
    for (t, want), good in zip(cases, ok[:len(cases)]):
        print('%-90s %s' % (t[:88], 'ok' if good else 'FAIL'))
    print('M286 SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--route':
        for p in a[1:]:
            r = route(text_of(p)); print('M323 ROUTE (M286): %s | %d identit%s' % (p, len(r), 'y' if len(r) == 1 else 'ies'))
            for e, v in r: print('  %-12s %s in Z, R, Z/9 and Z[phi]/9 (python3 tools/claimcheck.py "%s")' % (e, v, e))
        sys.exit(0)
    for p in a: report(p)
