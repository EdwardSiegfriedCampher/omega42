#!/usr/bin/env python3
"""core_economy.py -- the Core grows only by what Omega42 is and does (Core Part 0.0.5 Rule 39; Companion Part 228).

Every paragraph of the Core prose, as rendered in ai/, apart from the embedded files, is fingerprinted in records/core/economy.json,
the baseline accepted at the last sealed record. A record may add to the Core only:
  register entries   0.0.10.n MF-n, written from records/math/results.json by tools/core_math.py
  laws, rules and instruments   L-n:, Rule n --, Mnnn, each in one paragraph of at most 220 words
  numbered sections  n.n of the Parts (at most 220 words); checklist items n. of Part 12 (at most 80 words)
  appendix entries   S.n (at most 260 words), R.n and X.n listings (at most 80 words)
  headings           # and PART lines
and every added or edited paragraph, the register excepted, is free of builder's narration, record-keeping and self-critique:
  the narration of a record or session; revision history; concessions of weakness, flaw or overstatement; statements of what is
  not yet proved, verified or established; caveats, disclaimers and limitations; contrastive hedges. These belong in the
  Companion (Part 216 for scopes and limits), in the sealed records, and with the examiners (APE, PVIR, SNCA).
The prose a record adds beyond the register stays within 900 words. A paragraph edited in place (the same opening of 60
characters) is read for the markers and not for its kind. An appendix listing is compared without its number, so a listing renumbered by an insertion
is not new prose.

    python3 tools/core_economy.py --check     against the baseline; exit 1 on a finding
    python3 tools/core_economy.py --accept    the Core as it stands becomes the baseline (at the seal of a record)
    python3 tools/core_economy.py --selftest
Standard library only.
"""
import hashlib, json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(REPO, 'ai', 'Omega42_Core_V335_Rev450.md')
BASE = os.path.join(REPO, 'records', 'core', 'economy.json')
KINDS = [(re.compile(r'^0\.0\.10\.\d+ MF-\d+ '), 'register', None), (re.compile(r'^(Rule \d+ — |L-\d+[A-Z]?: |M\d{3}[a-z]?\b)'), 'law, rule or instrument', 220),
         (re.compile(r'^S\.\d+ '), 'appendix S entry', 260), (re.compile(r'^\d+(\.\d+)+ [A-Z]'), 'numbered section', 220), (re.compile(r'^\d+\. [A-Z]'), 'checklist item', 80), (re.compile(r'^(R|X)\.(\d+|n)(\.\d+)* '), 'appendix listing', 80), (re.compile(r'^(#+ |PART |APPENDIX )'), 'heading', 40)]
MARKERS = [('the narration of a record or session', r'\bthis (record|session|build|release|seq)\b|\bSEQ \d|\b(we|I) (found|noted?|noticed|realized|decided)\b'),
           ('revision history', r'\b(formerly|previously stated|was corrected|has been revised|no longer holds|used to read)\b'),
           ('a concession of weakness', r'\b(weakness(es)?|shortcomings?|flaws?|overclaim\w*|overstat\w*)\b'),
           ('a statement of what is not yet done', r'\bnot yet (proved|proven|established|verified|tested|shown|demonstrated)\b|\bunverified\b'),
           ('a caveat, disclaimer or limitation', r'\b(caveats?|disclaimers?|limitations?)\b|\bit should be noted\b'),
           ('a contrastive hedge', r'\bhowever\b')]
EXEMPT_MARK = re.compile(r'AI CAVEAT|L-506')
def norm(line):
    """an appendix listing is read without its number: inserting a listing renumbers those after it, and a renumbered listing is not new prose"""
    return re.sub(r'^(R|X)\.\d+(\.\d+)* ', r'\1.n ', line)
def lines(text):
    out, skip = [], False
    for line in text.split('\n'):
        if re.match(r'^# ===== \S+ BEGIN =====', line): skip = True
        if not skip and line.strip(): out.append(norm(line.strip()))
        if re.match(r'^# ===== \S+ END =====', line): skip = False
    return out
h = lambda s: hashlib.sha256(s.encode('utf-8')).hexdigest()[:20]
def kind(line):
    for rx, name, limit in KINDS:
        if rx.search(line): return name, limit
    return None, None
def problems(cur, base):
    hashes = set(base.get('hashes', [])); prefixes = set(base.get('prefixes', []))
    P = []; added_words = 0
    for line in cur:
        if h(line) in hashes: continue
        k, limit = kind(line)
        edited = line[:60] in prefixes
        if k == 'register': continue
        if not edited:
            if k is None: P.append('a paragraph of no allowed kind: %s' % line[:100]); continue
            n = len(line.split())
            if limit and n > limit: P.append('%s of %d words, over %d: %s' % (k, n, limit, line[:80]))
            if k != 'heading': added_words += n
        if EXEMPT_MARK.search(line): continue
        for name, rx in MARKERS:
            m = re.search(rx, line, re.I)
            if m: P.append('%s ("%s"): %s' % (name, m.group(0), line[:100])); break
    if added_words > 900: P.append('the record adds %d words of prose beyond the register, over 900' % added_words)
    return P, added_words
def baseline_of(cur, record):
    return {'_about': 'The fingerprint of the Core prose at the last sealed record (Core Part 0.0.5 Rule 39): a hash of every paragraph and its opening of 60 characters. Written by python3 tools/core_economy.py --accept.',
            'record': record, 'paragraphs': len(cur), 'hashes': sorted(h(l) for l in cur), 'prefixes': sorted(set(l[:60] for l in cur))}
def selftest():
    base = baseline_of(['Rule 1 — One.', 'L-1: A law.', 'PART 1: X'], 'test')
    cases = [('an unchanged Core passes', problems(['Rule 1 — One.', 'L-1: A law.', 'PART 1: X'], base)[0] == []),
             ('a new rule passes', problems(['Rule 1 — One.', 'Rule 2 — Two rules the Core.'], base)[0] == []),
             ('a register entry passes', problems(['0.0.10.9 MF-9 [EXACT]. However this record found a weakness.'], base)[0] == []),
             ('a paragraph of no allowed kind fails', problems(['A note on how the build went.'], base)[0] != []),
             ('narration fails', problems(['Rule 3 — In this record the Builder decided.'], base)[0] != []),
             ('a concession of weakness fails', problems(['L-9: A weakness of the method.'], base)[0] != []),
             ('a statement of what is not yet done fails', problems(['M999 Tool. Its output is not yet verified.'], base)[0] != []),
             ('an over-long rule fails', problems(['Rule 4 — ' + 'word ' * 230], base)[0] != []),
             ('an edit in place is read for markers only', problems(['Rule 1 — One, and two.'], base)[0] == [] and problems(['Rule 1 — One, however.'], base)[0] != []),
             ('the AI caveat stays', problems(['L-506: The AI caveat law.'], base)[0] == []),
             ('a renumbered listing is not new', problems(lines('R.1.7 tools/a.py — a tool.'), baseline_of(lines('R.1.6 tools/a.py — a tool.'), 't'))[0] == [] and norm('R.1.7 x') == 'R.n x')]
    for n, ok in cases: print('%-60s %s' % (n, 'PASS' if ok else 'FAIL'))
    ok = all(o for _, o in cases); print('CORE ECONOMY SELFTEST: %d of %d | %s' % (sum(o for _, o in cases), len(cases), 'PASS' if ok else 'FAIL')); return ok
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    cur = lines(open(CORE, encoding='utf-8').read())
    if a and a[0] == '--accept':
        os.makedirs(os.path.dirname(BASE), exist_ok=True)
        json.dump(baseline_of(cur, a[1] if len(a) > 1 else ''), open(BASE, 'w'), indent=0)
        print('CORE ECONOMY: baseline accepted, %d paragraphs' % len(cur)); sys.exit(0)
    if a == ['--check']:
        base = json.load(open(BASE)); P, w = problems(cur, base)
        print('CORE ECONOMY (Rule 39): %d paragraphs; %d words added beyond the register since %s | %s' % (len(cur), w, base.get('record', '?'), 'PASS' if not P else 'FAIL (%d)' % len(P)))
        [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
