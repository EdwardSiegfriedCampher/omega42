#!/usr/bin/env python3
"""doc_hygiene.py -- the document hygiene checks of the Fit-for-Purpose run (Core Part 12, items 34 to 37).

The bodies of the Core Specification and the Companion Document (everything before Appendix R of the Core and
Appendix X of the Companion, the embedded files left out) are checked for four things:

  34 NO REVISION HISTORY      no dated adoption or amendment, no SEQ number, no superseded revision number and no
                              before/after wording (Builder Rule 2). Kept, by rule: the title-page revision date, freeze
                              and retrieval stamps, the dates from which a check applies, the sample navigation of
                              Part 8.5, data ranges, the script label of the operative scripts, and the APE Commons,
                              whose entries are the register of the peers' own titles.
  35 NO AI META-COMMENTARY    no narration by the authoring AI of itself or of its writing ("this Navigator", "before
                              this paragraph was written", "I think"); the roles are named instead (the Builder, the
                              receiving Navigator); and the Builder's own judgment of the protocol stands only in the
                              Companion's Appendix B, the Builder's Notes.
  36 NO REPETITION            no two paragraphs whose six-word shingles overlap by 85% or more, and no sentence of
                              fourteen words or more repeated, the fixed lines of the templates excepted.
  37 SCIENCE IN APPENDIX S    the sections whose subject is empirical testing stand in Appendix S, and no section
                              outside it is labelled as a pre-registered or candidate test not yet run (Core L-491).

    python3 tools/doc_hygiene.py              # the four checks, with every hit listed; exit 1 on any hit
    python3 tools/doc_hygiene.py --selftest
Standard library only. It reports; it never edits a document (Core Rule 10).
"""
import html, os, re, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, 'docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx')
COMP = os.path.join(REPO, 'docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx')

def paras(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf8')
    return [html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', p, re.S))) for p in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', x, re.S)]

def body(ps, stop):
    """(index, part, text) for the body: up to the stop heading, embedded files and code left out"""
    out, part, appS = [], '', False
    for i, t in enumerate(ps):
        if t.startswith(stop): break
        m = re.match(r'(?:### )?(PART [\d.]+|APPENDIX [A-Z])', t)
        if m:
            part = m.group(1)
            if part.startswith('APPENDIX'): appS = part == 'APPENDIX S'
        if t.startswith(('# =====', '#!')) or '"""' in t: continue
        out.append((i, 'APPENDIX S' if appS else part, t))
    return out

MON = r'(?:September|October|November)'
DATE = r'\d{1,2}(?:(?: to |–|-| and )\d{1,2})? ' + MON + r' 2026'
HISTORY = [('a dated adoption or amendment', re.compile(r'(?i)\b(?:adopted|amended|revised|registered|added|introduced|refined|restored)\b[^.;\]]{0,30}\b' + DATE)),
           ('a SEQ number', re.compile(r'\bSEQ \d+')),
           ('a date in a bracketed label or heading', re.compile(r'\[[^\]]*\b' + DATE + r'[^\]]*\]|\b\d{1,2} OCTOBER\b')),
           ('a superseded revision number', re.compile(r'\b(?:supersedes|replaces) Rev\.|\bRev\.4[0-4]\d\b')),
           ('before/after wording', re.compile(r'(?i)\b(?:previously stated|earlier (?:version|draft|wording|text)|older wording|this corrects|was corrected to|formerly|supersedes)\b'))]
KEEP = re.compile(r'Date: 16 October 2026|frozen|sealed|hashed|SHA-256|\bUTC\b|T\d\d:\d\d|\bretrieved\b|\bchecked ' + DATE + r'|dated (?:from )?' + DATE +
                  r'|\b[Ff]rom ' + DATE + r'|Records before|navigations? of 14 October|\d{4}-\d\d-\d\d to|carries the date|dated two accounts|is dated 28 October'
                  r'|Rev\.449, ground_challenge|-sample DATE|STABLE \* 10 October')
PARA_KEEP = re.compile(r'The scripts operative at this revision|No history in|must not contain version history|An earlier version said X|supersession policy')
META = [re.compile(p) for p in (r'\bthis Navigator\b', r'(?:before|after) this (?:paragraph|section|Part) was written', r"(?<![\w'\"])I (?:think|believe|feel|would|have written|wrote)\b",
                                 r'\bAs an AI\b', r'\bthe present author\b')]
SENT_KEEP = ('It can contain errors, and its training shapes its wording and may shape its reading;', 'STATUS: GENERATED-Ω42 — the position meanings above are the structural roles of this reading (L-455)')
MOVED = ('9.1 Submission Format', '32.4.2 M267: Decoy-Coordinate Control', '32.5 Iterated Echo Chain', '32.6 Navigator Output Surprise', '32.7 Generation-level prediction suite',
         '32.8 Reviewer non-conflation test', '32.9 Re-navigation panel', '37.8 M267-GROUND, M279 [', 'R6 Navigator reconstruction experiment, M280 [', '52.7 The studies [',
         'Optional comparative control, M267', 'Generation-level hypotheses G1–G5 (Step 9.8) —')
UNRUN = re.compile(r'\[[^\]]*(?:PRE-REGISTERED, NOT RUN|candidate procedure, not operative|SPECIFIED, NOT RUN)[^\]]*\]')

def check_history(B):
    hits = []
    for i, p, t in B:
        if t.startswith('- APE-') or PARA_KEEP.search(t): continue
        for name, rx in HISTORY:
            for m in rx.finditer(t):
                ctx = t[max(0, m.start() - 80):m.end() + 20]
                if not KEEP.search(ctx): hits.append((i, name, ctx.strip()))
    return hits
OWN = re.compile(r"\[(?:L-509; )?CDT-C, the Builder's own judgment|\[the Navigator's (?:account|estimate)")
def check_meta(B):
    hits = [(i, rx.pattern, t[max(0, m.start() - 50):m.end() + 30]) for i, p, t in B for rx in META for m in rx.finditer(t)]
    hits += [(i, "the Builder's own judgment outside Appendix B", t[:90]) for i, p, t in B if p != 'APPENDIX B' and OWN.search(t)]
    return hits
def shingles(t, k=6):
    w = re.findall(r"[a-z0-9']+", t.lower()); return {' '.join(w[j:j + k]) for j in range(len(w) - k + 1)}
def check_repetition(B):
    items = [(i, shingles(t)) for i, p, t in B if len(t) > 200]
    index, hits = {}, []
    for n, (i, s) in enumerate(items):
        for x in s: index.setdefault(x, []).append(n)
    for n, (i, s) in enumerate(items):
        c = {}
        for x in s:
            for m in index[x]:
                if m > n: c[m] = c.get(m, 0) + 1
        for m, k in c.items():
            r = k / min(len(s), len(items[m][1]))
            if r >= 0.85: hits.append((i, 'paragraphs %d and %d overlap %.2f' % (i, items[m][0], r), ''))
    seen = {}
    for i, p, t in B:
        for s in re.split(r'(?<=[.;])\s+', t):
            if len(s.split()) >= 14 and not s.strip().startswith(SENT_KEEP): seen.setdefault(s.strip(), []).append(i)
    hits += [(v[0], 'a sentence repeated in paragraphs %s' % v, s[:90]) for s, v in seen.items() if len(v) > 1]
    return hits
def check_science(B):
    hits = []
    for i, p, t in B:
        if p == 'APPENDIX S': continue
        for mk in MOVED:
            if t.startswith(mk) and '— in Appendix S' not in t: hits.append((i, 'a section placed in Appendix S stands outside it', t[:90]))
        if UNRUN.search(t[:400]) and not re.search(r'—\s*in Appendix S', t): hits.append((i, 'a test not yet run labelled outside Appendix S', t[:90]))
    return hits

CHECKS = [(34, 'NO REVISION HISTORY', check_history), (35, 'NO AI META-COMMENTARY', check_meta), (36, 'NO REPETITION', check_repetition), (37, 'SCIENCE IN APPENDIX S', check_science)]
def run(core=CORE, comp=COMP):
    docs = (('Core', body(paras(core), 'APPENDIX R:')), ('Companion', body(paras(comp), '### APPENDIX X')))
    return [(n, name, [(d,) + h for d, B in docs for h in fn(B)]) for n, name, fn in CHECKS]
def summary(n):
    """(ok, note) for FFP item n"""
    for k, name, hits in run():
        if k == n:
            return not hits, ('none in either body' if not hits else '%d hit(s): %s' % (len(hits), '; '.join('%s [%d] %s' % (h[0], h[1], h[2]) for h in hits[:2])))
def selftest():
    B = [(0, 'PART 1', 'L-1 adopted 19 October 2026 as a law (SEQ 12).'), (1, 'PART 1', 'frozen 2026-10-09T12:20Z, adopted 9 October 2026 before the run.'),
         (2, 'PART 2', 'The Navigator reads it, as this Navigator found.'), (3, 'PART 2', '32.5 Iterated Echo Chain [CDT-B; candidate procedure, not operative]'),
         (4, 'APPENDIX S', '32.5 Iterated Echo Chain [CDT-B; candidate procedure, not operative]'), (5, 'PART 3', 'a rule applied to every navigation dated from 22 October 2026 and kept.')]
    long = ' '.join('word%d' % k for k in range(60))
    cases = [('a dated adoption and a SEQ number are found', len(check_history(B[:1])) == 2),
             ('a freeze stamp and a rule-scope date are kept', check_history(B[1:2] + B[5:6]) == []),
             ('narration of the AI by itself is found', len(check_meta(B[2:3])) == 1),
             ('the Builder\'s own judgment is found outside Appendix B and kept inside it', len(check_meta([(6, 'PART 98', '98.7 The state [the Navigator\'s account, CDT-C]. x')])) == 1 and check_meta([(6, 'APPENDIX B', '98.7 The state [the Navigator\'s account, CDT-C]. x')]) == []),
             ('a moved section outside Appendix S is found, and kept inside it', len(check_science(B[3:5])) == 2 and check_science(B[4:5]) == []),
             ('a repeated paragraph is found', len(check_repetition([(0, 'P', long), (1, 'P', long)])) >= 1),
             ('distinct paragraphs pass', check_repetition([(0, 'P', long), (1, 'P', ' '.join('other%d' % k for k in range(60)))]) == [])]
    for name, ok in cases: print('%-70s %s' % (name, 'PASS' if ok else 'FAIL'))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)
if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    bad = 0
    for n, name, hits in run():
        print('%d. %-26s %s' % (n, name, 'PASS' if not hits else 'FAIL (%d)' % len(hits)))
        for h in hits: print('   %s [%d] %s: %s' % h)
        bad += len(hits)
    sys.exit(1 if bad else 0)
