#!/usr/bin/env python3
"""fullstatement.py -- the Full Statement Law (Core L-543; Companion Part 170).

Omega42 does not downplay or understate any reading, finding or discovery: each is stated for what it is, at its
standing, in the indicative and without hedging. This check reads a sealed output for the words that understate a
finding (merely, mere, nothing more than, only a resemblance, perhaps, possibly, might be, it seems, arguably,
somewhat, a little, not a special) outside the question verbatim and quotations. The standing tags, the AI CAVEAT and a
statement of what a finding does not imply are statements of standing and scope, not hedges, and pass.
    python3 tools/fullstatement.py --records FILE...
    python3 tools/fullstatement.py --intro CORE.docx COMPANION.docx   # the Introduction and the Companion from Part 175 (L-546 (8))
    python3 tools/fullstatement.py --selftest
Standard library only.
"""
import os, re, sys
HEDGE = re.compile(r"(?<!not )(?<!than )\b(merely|mere|nothing more than|only (a|an|as a|as an) (resemblance|coincidence|analogy|placement|count|curiosity)|"
                   r"perhaps|possibly|might be|it seems|seemingly|arguably|somewhat|a little|not a special|just a)\b", re.I)
QUOTED = re.compile(r'"[^"]{1,240}"|“[^”]{1,240}”')
def hits(text):
    out, q = [], False
    for i, line in enumerate(text.split('\n'), 1):
        if line.startswith('QUESTION VERBATIM:'): q = True; continue
        if q and re.match(r'[A-Z][A-Z ]+[:(]', line): q = False
        if q or line.startswith('AI CAVEAT'): continue
        b = QUOTED.sub(' ', line)
        for m in HEDGE.finditer(b): out.append((i, m.group(0), line.strip()[:150]))
    return out
def selftest():
    t = [('an understating word is found', [w for _, w, _ in hits('SUMMARY: It is merely a count.')] == ['merely']),
         ('a hedge is found', [w for _, w, _ in hits('SUMMARY: This is perhaps the law.')] == ['perhaps']),
         ('"only a resemblance" is found', len(hits('SUMMARY: It is only a resemblance.')) == 1),
         ('a typed statement passes', hits('SUMMARY: RESEMBLANCE: three pyramids and three 24-cycles.') == []),
         ('scope passes', hits('SUMMARY: It does not imply that a proposal is right.') == []),
         ('the AI CAVEAT passes', hits('AI CAVEAT (L-506): It can contain errors.') == []),
         ('"not merely" is a negation and passes', hits('SUMMARY: It is not merely a count.') == []),
         ('a quotation is a mention', hits('SUMMARY: The peer wrote "merely a label".') == []),
         ('the question verbatim is left out', hits('QUESTION VERBATIM: Is it merely a count?\nFRAME: x') == [])]
    for n, ok in t: print('%-40s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('FULL STATEMENT SELFTEST: %d of %d' % (sum(o for _, o in t), len(t))); return all(o for _, o in t)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if len(a) > 1 and a[0] == '--records':
        bad = 0
        for f in a[1:]:
            h = hits(open(f, encoding='utf-8').read()); bad += len(h)
            print('FULL STATEMENT (L-543): %s | %s' % (f, 'PASS' if not h else 'FAIL (%d)' % len(h)))
            for i, w, s in h: print('  line %d (%s): %s' % (i, w, s))
        sys.exit(1 if bad else 0)
    if len(a) == 3 and a[0] == '--intro':   # the Introduction (IN-00) and the Companion from Part 175 on (L-546 (8))
        import json, zipfile, html as _h
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) if 'os' in globals() else '.'
        intro = json.load(open(os.path.join(root, 'records', 'introduction', 'introduction.json'), encoding='utf-8'))
        text = 'SUMMARY: ' + '\n'.join(p['text'] for p in intro['paragraphs'] if not p['key'].startswith('w_') and p['key'] != intro['cautions'])
        x = zipfile.ZipFile(a[2]).read('word/document.xml').decode('utf8')
        ps = [_h.unescape(''.join(re.findall(r'<w:t(?: [^>]*)?>(.*?)</w:t>', q, re.S))) for q in re.findall(r'<w:p(?: [^>]*[^/>])?>.*?</w:p>', x, re.S)]
        on, comp = False, []
        for t in ps:
            m = re.match(r'### PART (\d+)', t)
            if m: on = int(m.group(1)) >= 175
            if t.startswith('### APPLIED PROTOCOL') or t.startswith('### APPENDIX'): on = False
            if on and not t.startswith('###'): comp.append(t)
        text += '\n' + '\n'.join(comp)
        h = hits(text)
        print('FULL STATEMENT (L-543, L-546 (8)): the Introduction and Companion Parts 175 onward | %s' % ('PASS' if not h else 'FAIL (%d)' % len(h)))
        for i, w, s in h: print('  line %d (%s): %s' % (i, w, s[:160]))
        sys.exit(1 if h else 0)
    print(__doc__); sys.exit(2)
