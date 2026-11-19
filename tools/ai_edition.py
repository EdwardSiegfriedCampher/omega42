#!/usr/bin/env python3
"""ai_edition.py -- the AI reading editions of the two documents (Core Part 2, the Navigator's reading; Companion Part 142).

The .docx pair is the release of record (L-493): self-contained, every file of the repository embedded. An AI reads
text, and the pair is large: its prose and its embedded files together run to several million tokens, far past any
context window, so a Navigator given the .docx is given more than it can read and reads what its loader keeps. This tool
renders, from the .docx and never by hand, the editions an AI reads best:

    ai/Omega42_Core_V335_Rev450.md        the Core's prose in Markdown, headings as headings, every paragraph, no embedded files
    ai/Omega42_Companion_V335_Rev450.md   the Companion's prose, likewise
    ai/Omega42_Navigator_Pack.md          what a navigation needs, within a context window: The Introduction, the foundational
                                          register, the arithmetic, the mechanism, the Aperture and the output format whole,
                                          with a one-line index of every law, instrument and MATH entry pointing to the full text
    ai/Omega42_Existential_Framework.md   the Omega42 Existential Framework as a paper of its own: Companion Parts 145, 144 and 146
    ai/manifest.json                      every section of both editions: its heading, its characters, its estimated tokens,
                                          its SHA-256, for loaders that retrieve by section
    llms.txt                              the index of the editions, at the root of the repository

    python3 tools/ai_edition.py --build   # writes the editions from docs/*.docx
    python3 tools/ai_edition.py --check   # the editions are the ones the documents give now, and the pack fits its budget
    python3 tools/ai_edition.py --sizes   # characters and estimated tokens of every rendering
    python3 tools/ai_edition.py --positions  # where each essential section stands in the .docx as a loader reads it, and that the pack holds them all
    python3 tools/ai_edition.py --selftest
Tokens are estimated as characters divided by four, a common rule for English prose; the true count depends on the
model's tokenizer, and the estimate is stated as one. The editions are renderings, made from the documents, and so stand
outside them (Core Appendix R.4). Standard library only.
"""
import hashlib, html, json, os, re, sys, zipfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = {'Core': os.path.join(REPO, 'docs', 'Omega42_Core_Specification_V335_Rev450_STABLE.docx'),
        'Companion': os.path.join(REPO, 'docs', 'Omega42_Companion_Document_V335_Rev450_STABLE.docx')}
OUT = os.path.join(REPO, 'ai')
NAMES = {'Core': 'Omega42_Core_V335_Rev450.md', 'Companion': 'Omega42_Companion_V335_Rev450.md'}
PACK = 'Omega42_Navigator_Pack.md'
OEF = 'Omega42_Existential_Framework.md'
BUDGET = 120000          # estimated tokens: the pack fits a context of 128,000 tokens with room to answer, and any larger one
PACK_PARTS = ('PART 0:', 'PART 0.0', 'PART 0.5:', 'PART 1:', 'PART 2:', 'PART 7:', 'PART 8:')
PACK_SKIP = ()   # the complete mathematics (Core Part 0.0.8, with the register of 0.0.10) is in the pack: a Navigator given the pack can recompute every result (Part 0.0.5 Rule 19)
INTRO_CUT = 'IN-00.4:'   # the pack carries The Introduction to IN-00.4; the rest of it is read in the full Core edition (PV-002)
tok = lambda s: (len(s) + 3) // 4
def paras(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    out = []
    for p in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', x, re.S):
        t = html.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', p, re.S))).strip()
        if not t: continue
        st = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        out.append((st.group(1) if st else '', t))
    return out
def heading_level(style, t):
    if t.startswith('# ===== '): return None
    m = re.match(r'(#{1,6}) (?=[A-Z0-9Ω])', t)
    if m: return len(m.group(1))
    if re.match(r'Heading(\d)', style or ''): return int(re.match(r'Heading(\d)', style).group(1))
    if re.match(r'(PART \d+(\.\d+)*:|APPENDIX [A-Z]:)', t) and len(t) < 220: return 1 if re.match(r'(PART \d+:|APPENDIX)', t) else 2
    if re.match(r'(\d+\.\d+(\.\d+)? [A-Z]|FC-\d+(\.\d+)?: )', t) and len(t) < 160: return 3
    return 0
def render(doc):
    """(markdown, sections) of a document's prose, embedded files left out"""
    L, secs, cur = [], [], None
    for style, t in paras(DOCS[doc]):
        if t.startswith('# ===== ') or t.startswith('#!/usr/bin/env'): continue
        lv = heading_level(style, t)
        if lv:
            title = re.sub(r'^#+\s*', '', t)
            L.append('\n' + '#' * min(lv, 6) + ' ' + title + '\n')
            cur = {'doc': doc, 'heading': title[:160], 'text': []}; secs.append(cur)
        else:
            L.append(('\\' + t if t.startswith('#') else t) + '\n')   # a line of text that begins with # is escaped, not read as a heading
            if cur is None: cur = {'doc': doc, 'heading': '(front matter)', 'text': []}; secs.append(cur)
            cur['text'].append(t)
    return ''.join(L).strip() + '\n', secs
def index_lines(md_core):
    """one line for every law, instrument and MATH entry of the Core, with its first sentence"""
    out = []
    for line in md_core.split('\n'):
        m = re.match(r'(L-\d+[A-Z]?|M\d{3}[A-Z]?(?:-[A-Z])?|MATH-\d+)[: ]\s*(.*)', line)
        if m and len(line) > 12:
            first = re.split(r'(?<=[.;])\s', m.group(2), maxsplit=1)[0][:140]
            out.append('- %s %s' % (m.group(1), first))
    seen, res = set(), []
    for l in out:
        k = l.split()[1]
        if k not in seen: seen.add(k); res.append(l)
    return res
def compact_register(block):
    """the register entries of Core 0.0.10 in the pack: number, status, the statement to 200 characters and the recompute line; the full
    statement, domain, derivation and dependencies of each are in the full Core edition and in tools/replication_kit.py"""
    out = []
    for l in block.split('\n'):
        m = re.match(r'(0\.0\.10\.\d+ MF-\d+ \[[^\]]+\]\. )(.*?) Domain: .*? Recompute: python3 (tools/\S+) --selftest, the line beginning "([^"]+)"\.$', l)
        if not m:
            out.append(l); continue
        st = m.group(2)
        if len(st) > 200: st = st[:200].rsplit(' ', 1)[0] + ' ...'
        out.append('%s%s Recompute: %s "%s"' % (m.group(1), st, m.group(3), m.group(4)))
    return '\n'.join(out)
def pack(md_core):
    blocks, keep, cur = [], False, []
    for line in md_core.split('\n'):
        h = re.match(r'#{1,2} (.*)', line)
        if h:
            if cur and keep: blocks.append('\n'.join(cur))
            cur = [line]; keep = any(h.group(1).startswith(p) for p in PACK_PARTS) and not any(h.group(1).startswith(p) for p in PACK_SKIP)
        else:
            cur.append(line)
    if cur and keep: blocks.append('\n'.join(cur))
    for i, b in enumerate(blocks):
        if b.startswith('# PART 0: INTRODUCTION') and ('\n' + INTRO_CUT) in b:
            blocks[i] = b[:b.index('\n' + INTRO_CUT)] + ('\n\nThe rest of The Introduction, from IN-00.4 to IN-23, is in the full Core edition, '
                                                           'ai/Omega42_Core_V335_Rev450.md; it orients a reader and no step of a navigation depends on it.\n')
    head = ('# Ω42 Navigator Pack — V335 Rev.450 STABLE\n\nRendered from the Core Specification by tools/ai_edition.py; the documents are the release of record (Core L-493), '
            'and this pack is what a navigation needs within one context window: The Introduction, the Foundational Register, the arithmetic, the navigation mechanism, '
            'the 1/7 Aperture and the output format, in full, with the complete mathematics of Core Part 0.0.8, its register (0.0.10) with the opening of every result and its recompute line, and The Introduction to IN-00.4, with a one-line index of every law, instrument and MATH entry. For the full text of an indexed entry read '
            'ai/Omega42_Core_V335_Rev450.md; for the record, ai/Omega42_Companion_V335_Rev450.md; to run a tool, the .docx pair or the repository.\n')
    blocks = [compact_register(b) for b in blocks]
    idx = '\n## Index of laws, instruments and MATH entries (first sentence; the full text in the Core)\n\n' + '\n'.join(index_lines(md_core)) + '\n'
    return head + '\n' + '\n\n'.join(blocks) + '\n' + idx
def build(write=True):
    files = {}
    secs_all = []
    md = {}
    for d in DOCS:
        md[d], secs = render(d); files[NAMES[d]] = md[d]; secs_all += secs
    files[PACK] = pack(md['Core'])
    c = md['Companion']; i4, i5, i6, i7 = (c.find('### PART %d:' % k) for k in (144, 145, 146, 147))
    if min(i4, i5, i6, i7) >= 0:
        files[OEF] = ('# The Omega42 Existential Framework (OEF)\n\nRendered from the Companion Document by tools/ai_edition.py; V335 Rev.450 STABLE. The framework itself is Part 145; '
                      'the exploration of its two founding propositions, Part 144, and the framework as the mold of the protocol, with its roadmap, Part 146, follow it. The Companion is the text of record, '
                      'and the exact facts named here are recomputed by python3 tools/oef.py --congruence.\n\n' + c[i5:i6].strip() + '\n\n' + c[i4:i5].strip() + '\n\n' + c[i6:i7].strip() + '\n')
    man = {'_about': 'The sections of the AI reading editions (Companion Part 142): heading, characters, estimated tokens (characters / 4) and SHA-256 of the section text; rendered from docs/*.docx by tools/ai_edition.py.',
           'editions': {k: {'chars': len(v), 'tokens_est': tok(v), 'sha256': hashlib.sha256(v.encode('utf-8')).hexdigest()} for k, v in files.items()},
           'sections': [{'doc': s['doc'], 'heading': s['heading'], 'chars': sum(len(t) + 1 for t in s['text']), 'tokens_est': tok('\n'.join(s['text'])), 'sha256': hashlib.sha256('\n'.join(s['text']).encode('utf-8')).hexdigest()} for s in secs_all]}
    files['manifest.json'] = json.dumps(man, indent=1, ensure_ascii=False) + '\n'
    llms = ('# Omega42\n\n> A thought experiment and a navigation protocol: one structure, any question, your judgment. The release of record is the pair of .docx documents in docs/; '
            'the editions below are renderings of them for AI readers.\n\n## Editions for AI readers\n\n'
            '- [Navigator Pack](ai/%s): what a navigation needs, about %d thousand tokens\n'
            '- [Core Specification, prose](ai/%s): about %d thousand tokens\n'
            '- [Companion Document, prose](ai/%s): about %d thousand tokens\n'
            '- [The Omega42 Existential Framework](ai/%s): the philosophical framework, Companion Part 145\n'
            '- [Section manifest](ai/manifest.json): every section with its size and hash\n\n'
            '## The release of record\n\n- [Core Specification (.docx)](docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx)\n- [Companion Document (.docx)](docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx)\n'
            % (PACK, tok(files[PACK]) // 1000, NAMES['Core'], tok(files[NAMES['Core']]) // 1000, NAMES['Companion'], tok(files[NAMES['Companion']]) // 1000, OEF))
    if write:
        os.makedirs(OUT, exist_ok=True)
        for k, v in files.items(): open(os.path.join(OUT, k), 'w', encoding='utf-8').write(v)
        open(os.path.join(REPO, 'llms.txt'), 'w', encoding='utf-8').write(llms)
    return files, llms
def sizes():
    L = ['THE RENDERINGS OF THE TWO DOCUMENTS, BY SIZE (tokens estimated as characters / 4)']
    for d, p in DOCS.items():
        x = zipfile.ZipFile(p).read('word/document.xml').decode('utf-8'); ps = paras(p)
        body = [t for _, t in ps if not t.startswith('# ===== ')]; emb = [t for _, t in ps if t.startswith('# ===== ')]
        b, e = sum(len(t) for t in body), sum(len(t) for t in emb)
        L.append('  %-9s .docx %9d bytes | XML %9d characters | prose %8d characters, ~%7d tokens | embedded files %8d characters, ~%7d tokens | all text ~%7d tokens' % (d, os.path.getsize(p), len(x), b, tok('x' * b), e, tok('x' * e), tok('x' * (b + e))))
    files, _ = build(write=False)
    for k in (PACK, NAMES['Core'], NAMES['Companion']):
        L.append('  %-38s %9d characters, ~%7d tokens' % (k, len(files[k]), tok(files[k])))
    L.append('  the pack against its budget of %d tokens: %s' % (BUDGET, 'WITHIN' if tok(files[PACK]) <= BUDGET else 'OVER'))
    return '\n'.join(L)
ESSENTIAL = [('Core', 'IN-00: The Introduction to Omega42', 'the Introduction'), ('Core', 'PART 0.0.0', 'the Foundational Register'),
             ('Core', 'PART 0.0.6: THE OMEGA42 EXISTENTIAL FRAMEWORK', 'the Existential Framework'), ('Core', 'PART 0.0.7: THE FOUNDATIONAL CONSEQUENCES', 'the foundational consequences'), ('Core', 'PART 1:', 'the arithmetic'),
             ('Core', 'PART 2:', 'the mechanism'), ('Core', 'L-490:', 'the laws from L-490'), ('Core', 'L-534:', 'the framework laws, L-534 to L-545'),
             ('Core', 'PART 7:', 'the Aperture'), ('Core', 'PART 8:', 'the output format'), ('Core', 'APPENDIX R:', 'the embedded files'),
             ('Companion', '### PART 145:', 'the framework at length')]
IN_PACK = ['IN-00: The Introduction to Omega42', 'PART 0.0.0', 'PART 0.0.6: THE OMEGA42 EXISTENTIAL FRAMEWORK', 'PART 0.0.7: THE FOUNDATIONAL CONSEQUENCES', 'PART 1: CORE ARITHMETIC', 'PART 2: NAVIGATION MECHANISM',
           'PART 7: THE 1/7 APERTURE', 'PART 8: NAVIGATOR OUTPUT FORMAT', '- L-490 ', '- L-534 ', '- L-535 ', '- L-536 ', '- L-537 ', '- L-538 ', '- L-539 ', '- L-540 ', '- L-541 ', '- L-542 ', '- L-543 ', '- L-544 ', '- L-545 ', '- M336 ', '- M338 ']
def positions():
    L = ['WHERE THE ESSENTIAL SECTIONS STAND (tokens estimated as characters / 4, counted from the start of each .docx as a loader reads it)']
    for doc in ('Core', 'Companion'):
        pos, seen, ps = 0, {}, paras(DOCS[doc])
        for _, t in ps:
            for d, k, name in ESSENTIAL:
                if d == doc and k not in seen and t.startswith(k): seen[k] = pos
            pos += len(t) + 1
        L.append('  %s: about %d thousand tokens in all' % (doc, tok('x' * pos) // 1000))
        for d, k, name in ESSENTIAL:
            if d == doc: L.append('    %-36s %s' % (name, 'at about %d thousand' % (tok('x' * seen[k]) // 1000) if k in seen else 'NOT FOUND'))
    files, _ = build(write=False); pk = files[PACK]
    miss = [k for k in IN_PACK if k not in pk]
    L.append('  the Navigator Pack, about %d thousand tokens, holds every essential section: %s' % (tok(pk) // 1000, 'YES' if not miss else 'NO, missing ' + ', '.join(miss)))
    return '\n'.join(L), miss
def check():
    files, llms = build(write=False); P = []
    for k, v in files.items():
        p = os.path.join(OUT, k)
        if not os.path.exists(p) or open(p, encoding='utf-8').read() != v: P.append('ai/%s is not the rendering of the documents as they stand' % k)
    if not os.path.exists(os.path.join(REPO, 'llms.txt')) or open(os.path.join(REPO, 'llms.txt'), encoding='utf-8').read() != llms: P.append('llms.txt is not current')
    for k in IN_PACK:
        if k not in files[PACK]: P.append('the pack lacks %s' % k)
    if tok(files[PACK]) > BUDGET: P.append('the pack is over its budget: ~%d tokens' % tok(files[PACK]))
    if OEF not in files or 'Axiom 4' not in files[OEF]: P.append('no rendering of the Existential Framework')
    for must in ('PART 0: INTRODUCTION', 'PART 1: CORE ARITHMETIC', 'PART 7: THE 1/7 APERTURE', 'PART 8: NAVIGATOR OUTPUT FORMAT', 'L-490', 'M333'):
        if must not in files[PACK]: P.append('the pack lacks %s' % must)
    return P
def selftest():
    cases = [('a Markdown heading is read as a heading', heading_level('', '### PART 135: X') == 3),
             ('a table row is not a heading', heading_level('', '# | Word | Letters') == 0),
             ('a PART line is a heading', heading_level('', 'PART 7: THE 1/7 APERTURE') == 1),
             ('an embedded block is not a heading', heading_level('', '# ===== tools/x.py BEGIN =====') is None),
             ('the pack keeps The Introduction to IN-00.4 only', 'IN-00.5' not in pack('# PART 0: INTRODUCTION TO OMEGA42 (IN)\nIN-00: a\nIN-00.4: b\nIN-00.5: c\n') and 'IN-00: a' in pack('# PART 0: INTRODUCTION TO OMEGA42 (IN)\nIN-00: a\nIN-00.4: b\nIN-00.5: c\n')),
             ('the index takes one line a law', index_lines('L-490: The law. More.\nL-490: again\nM333 Standing Record. It does.') == ['- L-490 The law.', '- M333 Standing Record.']),
             ('tokens are estimated as characters / 4', tok('x' * 400) == 100)]
    for n, ok in cases: print('%-45s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('AI EDITION SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--build']: build(); print(sizes()); sys.exit(0)
    if a == ['--sizes']: print(sizes()); sys.exit(0)
    if a == ['--positions']:
        t, miss = positions(); print(t); sys.exit(1 if miss else 0)
    if a == ['--check']:
        P = check(); print('AI EDITIONS: %s' % ('PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    print(__doc__); sys.exit(2)
