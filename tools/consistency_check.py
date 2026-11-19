#!/usr/bin/env python3
"""consistency_check.py -- release-time cross-document consistency register for the Core
Specification and the Companion Document (Core Rule 10, Editorial Neutrality and Precision).

It REPORTS conflicts with their location and never rewrites a document or chooses which of two
statements is correct; resolution belongs to a formal revision (F-06).

Usage:
    python3 tools/consistency_check.py CORE.docx COMPANION.docx [--scripts DIR] [--ground-test N] [--ref-test N]

Checks:
  VERSION      every 'V335 Rev.NNN' identifier names the current revision (the Core title's), except the frozen
               script label Rev.449 in embedded code, the script-label statement and records dated before the revision,
               and an earlier revision named inside an embedded frozen record (a submission keeps its own text)
  XREF-LAW     every L-number cited is defined (as 'L-NNN:') exactly once
  XREF-PART    every 'Part N.N' / 'Companion N.N' / 'Core Part N.N' resolves to a section heading
  STATUS       instruments recorded as NOT RUN are nowhere described as run or validated
  VALIDATED    'validated' is never applied affirmatively while no measurement reads ROBUST
  HASH         every SCRIPT SHA-256 stated equals the hash of the embedded canonical_reference.py
  COUNT        stated check counts equal the tests' own counts (ground_challenge.py, canonical_reference.py)
  PERSUASION   intensifiers and promotional wording outside the Introduction (Rule 11); defined names exempt
  TYPOGRAPHY   doubled punctuation and empty brackets outside code
  CLAIM        an affirmative use of "claim" in prose, or an assertion verb aimed at the world (Core L-505)
  OBSOLETE     no retired formulation survives an amendment
  SPELLING     one spelling per word (American -ize / -or / -er forms)
  DUPLICATE    a normative sentence of 14 or more words stated twice in the Core (8-word shingles,
               overlap 0.6 or more), counted on sentences at least half prose, so that a shared equation,
               formula or definition in symbols is not read as a repetition; deliberate restatements are listed in ALLOWED_RESTATEMENTS
Exit status 0 when no CONFLICT is found, 1 otherwise. INFO lines are not conflicts.
"""
import hashlib, html, re, sys, zipfile

def paragraphs(path):
    xml = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    out = []
    sample = False   # the format sample of Core Part 8.5 is a record, read like code: it restates its own claims by design
    for i, p in enumerate(re.findall(r'<w:p(?:\s[^>]*)?>.*?</w:p>', xml, re.S)):
        t = html.unescape(''.join(re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>', p, re.S)))
        if t == '======= BEGIN SAMPLE NAVIGATION =======': sample = True
        code = 'Consolas' in p or sample
        if t == '======= END SAMPLE NAVIGATION =======': sample = False
        if code and 'Consolas' in p:
            t = re.sub(r'<w:br/>', '\n', p)
            t = html.unescape(''.join(a or b for a, b in re.findall(r'<w:t(?:\s[^>]*)?>(.*?)</w:t>|(\n)', t, re.S)))
        out.append((i, t, code))
    return out

def sentences(t):
    return re.split(r'(?<=[.;])\s+', t)

RETIRED = [
    'the canonical 24-cycle is ALL THAT EXISTS',
    'the 24-cycle is ALL THAT EXISTS',
    'Ω42₂₄ ≡ ALL THAT EXISTS',
    'structural compliance check, not domain-expert peer review',
    'domain-expert validation',
    'EXTERNAL RECORD',
    'an author never adjudicates',
    'universal reconstruction threshold',
    'repaid in equal bits',
    'Lean Specification',
    'simplest of its class',
    'domain-competent raters',
]
SPELLING = {r'\brecognis(e|ed|es|ing|er|ers)\b': 'recogniz-', r'\borganis(ation|ations|ed|es|e)\b': 'organiz-',
            r'\breorganisation\b': 'reorganization', r'\bbehaviours?\b': 'behavior', r'\bcolours?\b': 'color',
            r'\banalyse\b': 'analyze', r'\bcentre\b': 'center', r'\bfree will\b': 'freewill'}
# Deliberate restatements: a checklist or template reproduces a rule in order to verify it, or a law
# summarizes the mathematics it governs. Each entry is a phrase that identifies the restating sentence.
ALLOWED_RESTATEMENTS = (
    'offered as a fun, new method for discovering new information',   # L-522 is restated as the purpose that opens both documents (Core Part 12 item 33)
    'and its training shapes its wording and may shape its reading',   # the fixed AI CAVEAT line of L-506, restated in each template
    'kept outside both documents',          # Part 12 checklist items verify L-411
    'SCRIPT SHA-256 is re-derived',          # Part 12 checklist verifies L-417
    "uniqueness is that of the canonical structure",  # L-452 summarizes MATH-15
    'NAVIGATOR IDENTITY BLOCK',              # the template reproduces the Introduction's opening line
    'NAVIGATOR: [model identifier]',
)
NOT_RUN = ('M267', 'M279', 'M280', 'M267-GROUND', 'R6')
RUN_WORDS = re.compile(r'\b(has been run|was run|were run|results show|validated|demonstrated that|confirmed by the panel)\b', re.I)
NEG = re.compile(r"\b(not|never|no|until|before|awaits|awaiting|unrun|if|whether|once|when)\b", re.I)

def main():
    args = sys.argv[1:]
    if len(args) < 2:
        print(__doc__); sys.exit(2)
    core, comp = args[0], args[1]
    scripts = args[args.index('--scripts') + 1] if '--scripts' in args else None
    gtest = int(args[args.index('--ground-test') + 1]) if '--ground-test' in args else None
    rtest = int(args[args.index('--ref-test') + 1]) if '--ref-test' in args else None
    D = {'Core': paragraphs(core), 'Companion': paragraphs(comp)}
    conflicts, infos = [], []
    def conflict(kind, doc, i, msg):
        conflicts.append('CONFLICT %-10s %s [%d] %s' % (kind, doc, i, msg))
    def info(msg):
        infos.append('INFO     ' + msg)

    # VERSION
    # The current revision is the one in the Core's title line. The scripts are frozen at SCRIPT_REV (L-417) and keep
    # that label: it may appear in embedded code, in the script-label statement, and in records dated before the revision.
    SCRIPT_REV = '449'
    cur = next((m.group(1) for i, t, code in D['Core'] for m in [re.search(r'V335 Rev\.(\d+) STABLE', t)] if m), SCRIPT_REV)
    for doc, ps in D.items():
        for i, t, code in ps:
            for r in re.findall(r'V335 Rev\.(\d+)', t):
                if r == cur:
                    continue
                if r == SCRIPT_REV and (code or t.startswith('Script label.') or re.search(r'\b[1-8] October 2026|September 2026', t)):
                    continue
                if code and not re.match(r'# ===== (?:tools|scripts)/', t) and int(r) < int(cur):
                    continue    # a frozen record embedded verbatim keeps the revision it was made under (Companion Appendix X)
                conflict('VERSION', doc, i, 'names Rev.%s (current Rev.%s)' % (r, cur))
    # section index
    heads = {}
    for doc, ps in D.items():
        idx = set()
        for i, t, code in ps:
            if code:
                continue
            m = re.match(r'^(?:#+\s*)?(?:PART\s+)?(\d+(?:\.\d+)*)[\s:.]', t)
            if m:
                idx.add(m.group(1))
        heads[doc] = idx
    def resolves(doc, num):
        return num in heads[doc] or any(h.startswith(num + '.') for h in heads[doc])
    # XREF-LAW
    defined = {}
    for i, t, code in D['Core']:
        if code:
            continue
        for n in re.findall(r'(?:^|\.\s)L-(\d{3}): [A-Z]', t):
            defined.setdefault(n, []).append(i)
    for n, where in defined.items():
        if len(where) > 1:
            conflict('XREF-LAW', 'Core', where[1], 'L-%s defined more than once (paragraphs %s)' % (n, where))
    for doc, ps in D.items():
        for i, t, code in ps:
            if code:
                continue
            for n in sorted(set(re.findall(r'\bL-(\d{3})\b', t))):
                if n not in defined:
                    conflict('XREF-LAW', doc, i, 'cites L-%s, which is not defined' % n)
    # XREF-PART
    for doc, ps in D.items():
        other = 'Companion' if doc == 'Core' else 'Core'
        for i, t, code in ps:
            if code:
                continue
            for m in re.finditer(r'\b(?:(Core|Companion)(?: Specification| Document)?,?\s+)?(Parts?\s+)?(\d+\.\d+(?:\.\d+)?)\b', t):
                who, part, num = m.group(1), m.group(2), m.group(3)
                after = t[m.end():m.end() + 30]
                before = t[max(0, m.start() - 30):m.start()]
                if re.search(r'Step\s*$', before):
                    continue                      # Step 9.8 is a step, not a part
                if re.match(r'\s+of the Core', after) or re.search(r"Core Specification(?:'s(?: own)?)?[^.;]{0,6}\(?$", before):
                    who = 'Core'
                elif re.match(r'\s+of the Companion', after) or re.search(r'Companion(?: Document)?[^.;]{0,6}\($', before):
                    who = 'Companion'
                if not who and not part:
                    continue                      # a bare number such as 0.25 is not a reference
                target = doc if not who else ('Core' if who == 'Core' else 'Companion')
                if not resolves(target, num):
                    conflict('XREF-PART', doc, i, 'reference to %s %s does not resolve%s' % (
                        target, num, ' (it exists in the %s: name that document)' % other if resolves(other, num) and target == doc else ''))
    # STATUS and VALIDATED
    for doc, ps in D.items():
        for i, t, code in ps:
            if code:
                continue
            for s in sentences(t):
                if any(re.search(r'\b%s\b' % re.escape(x), s) for x in NOT_RUN) and RUN_WORDS.search(s) and not NEG.search(s):
                    conflict('STATUS', doc, i, 'an unrun test described as run or validated: "%s"' % s[:120])
                if re.search(r'\bvalidated\b', s) and not NEG.search(s) and not re.search(r'validated for stated use|VALIDATED FOR STATED USE', s):
                    conflict('VALIDATED', doc, i, '"validated" used affirmatively: "%s"' % s[:120])
    # HASH
    if scripts:
        src = open(scripts + '/canonical_reference.py', encoding='utf-8').read()
        lines = [ln.rstrip() for ln in src.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
        while lines and not lines[-1]:
            lines.pop()
        real = hashlib.sha256('\n'.join(lines).encode('utf-8')).hexdigest()   # canonical form, as L-417
        stated = set()
        for doc, ps in D.items():
            for i, t, code in ps:
                if code:
                    continue
                for h in re.findall(r'SCRIPT SHA-256[^0-9]{0,40}?([0-9a-f]{64})', t):
                    stated.add(h)
                    if h != real:
                        conflict('HASH', doc, i, 'SCRIPT SHA-256 %s... differs from the script %s...' % (h[:12], real[:12]))
        info('SCRIPT SHA-256 of canonical_reference.py: %s (%d stated value(s) checked)' % (real, len(stated)))
    # COUNT
    if gtest is not None:
        for doc, ps in D.items():
            for i, t, code in ps:
                if code:
                    continue
                for n in re.findall(r'(\d+) checks', t):
                    if 'ground_challenge' in t or '--test' in t and doc == 'Companion':
                        if int(n) != gtest:
                            conflict('COUNT', doc, i, 'states %s checks; the test runs %d' % (n, gtest))
    if rtest is not None:
        for doc, ps in D.items():
            for i, t, code in ps:
                if code:
                    continue
                for m in re.finditer(r'canonical_reference\.py[^.;]{0,80}?\ball (\d+) --test checks', t):
                    if int(m.group(1)) != rtest:
                        conflict('COUNT', doc, i, 'states %s canonical_reference.py checks; the test runs %d' % (m.group(1), rtest))
    # PERSUASION and TYPOGRAPHY (the Introduction is public-facing and exempt, Rule 11)
    PERS = re.compile(r"\b(very|truly|deeply|deepest|remarkabl[ey]|powerful(?:ly)?|beautiful(?:ly)?|extraordinar(?:y|ily)|crucial(?:ly)?|absolutely|perfectly|brilliant|revolutionary|unprecedented|groundbreaking|breakthrough|transformative|fascinating|exciting|stunning|amazing|incredibl[ey]|obviously|interestingly|surprisingly|magnificent|dramatic(?:ally)?)\b", re.I)
    PERS_EXEMPT = ('strong/powerful', 'not, very, just', 'strikingly apt')
    for doc, ps in D.items():
        in_fc = False
        for i, t, code in ps:
            if doc == 'Core' and t.startswith('PART 0: INTRODUCTION'):
                in_fc = True
            if doc == 'Core' and t.startswith('PART 0.0.0: THE FOUNDATIONAL REGISTER'):
                in_fc = False
            if code or in_fc:
                continue
            u = re.sub(r'"[^"]*"|\u201c[^\u201d]*\u201d', ' ', t)
            for m in PERS.finditer(u):
                ctx = u[max(0, m.start() - 20):m.end() + 20]
                if not any(x in ctx for x in PERS_EXEMPT):
                    conflict('PERSUASION', doc, i, '"%s" in: ...%s...' % (m.group(0), ctx))
            for m in re.finditer(r',,|;;|(?<!\w)\(\s*\)', t):
                conflict('TYPOGRAPHY', doc, i, '"%s" in: ...%s...' % (m.group(0), t[max(0, m.start() - 30):m.end() + 20]))
    # CLAIM (Core L-505): the word names only what the protocol does not make. An affirmative use in prose is listed;
    # a sentence that negates, asks, quotes, names a forbidden act or reports a peer's text is not. Assertion verbs
    # aimed at the world ("proves that the universe ...") are listed with it.
    CNEG = re.compile(r"\b(not|no|never|nor|without|none|nothing|neither|cannot|isn't|doesn't|disclaims?|any)\b", re.I)
    ALLOW = re.compile(r"authority claims?|claims? the Navigator|claimed from|claims? rather than|as a claim\b|up as a claim|differs from a claim|skeptic|\?|claims? authority|what authority it claims", re.I)
    WORLD = re.compile(r"\b(proves?|demonstrates?|establishes?|shows?) that (the universe|reality|the world|everything is)\b", re.I)
    for doc, ps in D.items():
        for i, t, code in ps:
            if code or t.startswith('# =====') or t.startswith('- APE-') or re.match(r'^[A-Z](\.\d+)+ \S+/', t):
                continue
            u = re.sub(r'"[^"]*"|\u201c[^\u201d]*\u201d|\u2018[^\u2019]*\u2019', ' ', t)
            for s_ in sentences(u):
                if re.search(r'\bclaim(s|ed|ing)?\b', s_, re.I) and not CNEG.search(s_) and not ALLOW.search(s_):
                    conflict('CLAIM', doc, i, 'affirmative "claim" (L-505): "%s"' % s_.strip()[:140])
                m = WORLD.search(s_)
                if m and not CNEG.search(s_):
                    conflict('CLAIM', doc, i, 'an assertion about the world (L-505): "%s"' % s_.strip()[:140])
    # OBSOLETE
    for doc, ps in D.items():
        for i, t, code in ps:
            if code:
                continue
            for r in RETIRED:
                if r in t:
                    conflict('OBSOLETE', doc, i, 'retired formulation survives: "%s"' % r)
    # SPELLING
    for doc, ps in D.items():
        for i, t, code in ps:
            if code:
                continue
            for rx, std in SPELLING.items():
                for m in re.finditer(rx, t, re.I):
                    conflict('SPELLING', doc, i, '"%s" (standard: %s)' % (m.group(0), std))
    # DUPLICATE
    from collections import defaultdict
    sents = []
    for i, t, code in D['Core']:
        if code or t.startswith('0.0.10.'):   # Part 0.0.10 is written from the register by tools/core_math.py and restates it by design (Rule 19)
            continue
        for snt in sentences(t):
            w = re.findall(r"[a-z0-9\-]+", snt.lower())
            prose = [x for x in w if re.fullmatch(r'[a-z][a-z\-]*', x) and len(x) > 1]
            if len(w) >= 14 and 2 * len(prose) >= len(w):   # a sentence that is mostly an equation or a formula, shared by two passages, is a shared definition, not a repetition
                sents.append((i, snt, w))
    shingles = defaultdict(set)
    for k, (i, snt, w) in enumerate(sents):
        for j in range(len(w) - 7):
            shingles[tuple(w[j:j + 8])].add(k)
    shared = defaultdict(int)
    for ks in shingles.values():
        ks = sorted(ks)
        if len(ks) > 6:
            continue
        for a in range(len(ks)):
            for b in range(a + 1, len(ks)):
                if sents[ks[a]][0] != sents[ks[b]][0]:
                    shared[(ks[a], ks[b])] += 1
    for (a, b), n in sorted(shared.items()):
        if n / max(1, min(len(sents[a][2]), len(sents[b][2])) - 7) < 0.6:
            continue
        txt = sents[a][1] + ' ' + sents[b][1]
        if any(x in txt for x in ALLOWED_RESTATEMENTS):
            continue
        conflict('DUPLICATE', 'Core', sents[b][0], 'restates paragraph [%d]: "%s"' % (sents[a][0], sents[b][1][:100]))
    for c in conflicts:
        print(c)
    for x in infos:
        print(x)
    print('CONSISTENCY REGISTER: %d conflict(s) | RESULT: %s' % (len(conflicts), 'PASS' if not conflicts else 'REVIEW'))
    sys.exit(0 if not conflicts else 1)

if __name__ == '__main__':
    main()
