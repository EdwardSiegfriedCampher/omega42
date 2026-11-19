#!/usr/bin/env python3
"""judgment.py -- the Judgment Boundary checks (Core L-541; Companion Part 164).

The Navigator may compute, derive, interpret, compare, criticise and recommend; the Striker judges meaning, significance,
desirability, acceptance and action, and the Originator adopts (L-441, F-06). Two checks keep the line visible:
    python3 tools/judgment.py --records FILE...   # a sealed output: no unlabelled ranking or value judgment -- "the most
                                                  # important", "the sharpest", "the chief risk", "the frame of" -- unless
                                                  # the sentence carries [EVALUATIVE] or states the criterion ("by the
                                                  # criterion of ..."); the question verbatim and quotations are left out
    python3 tools/judgment.py --held              # the register of recommendations the Builder declined and of choices it
                                                  # made unasked, each HELD FOR THE ORIGINATOR (records/frame/held.json)
    python3 tools/judgment.py --selftest
A value word is not itself a failure; a ranking without its label or its criterion is. Standard library only.
"""
import json, os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HELD = os.path.join(REPO, 'records', 'frame', 'held.json')
EVAL = re.compile(r"\bthe (most|least) (important|significant|consequential|valuable|exact|complete|useful|profound|interesting|likely|serious)\b|"
                  r"\bthe (sharpest|worst|best|deepest|chief|clearest|greatest|key|central) (\w+)|\bmost (important|significant|consequential|valuable|profound)\b|"
                  r"\bthe frame of (the register|L-\d+|the law)\b|\bthe source of most\b|\bcrucial\b|\bthe real (issue|point|question)\b|\bobviously\b", re.I)
LABEL = re.compile(r"\[EVALUATIVE|\bby the criterion of\b|\bthe Navigator's (evaluation|ranking|assessment)\b", re.I)
QUOTED = re.compile(r'"[^"]{1,200}"|“[^”]{1,200}”')
# "the key" is a ranking word only where no cryptographic key is in question (Core Part 3.77): a sentence that names
# keys, locks, envelopes, ciphers, signatures or rotation uses "key" as a noun of the craft, not as a ranking
CRYPTO = re.compile(r"\b(encrypt\w*|decrypt\w*|cipher\w*|keys\b|key id|master key|passphrase|password|lock\w*|unlock\w*|"
                    r"envelope\w*|signature\w*|signed|rotation|AES|HKDF|scrypt|Ed25519|fingerprint\w*|opening that only)", re.I)
def hits(text):
    out, q = [], False
    for i, line in enumerate(text.split('\n'), 1):
        if line.startswith('QUESTION VERBATIM:'): q = True; continue
        if q and re.match(r'[A-Z][A-Z ]+[:(]', line): q = False
        if q or line.lstrip().startswith('>'): continue
        for s in re.split(r'(?<=[.!?])\s+', line):
            b = QUOTED.sub(' ', s); m = EVAL.search(b)
            if m and m.group(3) and m.group(3).lower() == 'key' and CRYPTO.search(line):
                m = EVAL.search(b, m.end())
            if m and not LABEL.search(s): out.append((i, s.strip()[:160]))
    return out
def held():
    d = json.load(open(HELD, encoding='utf-8')); P = []
    for e in d['entries']:
        for f in ('id', 'item', 'source', 'kind', 'reason', 'status'):
            if not str(e.get(f, '')).strip(): P.append('%s: no %s' % (e.get('id', '?'), f))
        if e.get('kind') not in ('DECLINED', 'FOLDED', 'PARTLY APPLIED', 'CHOICE MADE UNASKED', 'APPLIED, FOR REVIEW'): P.append('%s: kind %s' % (e['id'], e.get('kind')))
        if e.get('status') != 'HELD FOR THE ORIGINATOR' and not str(e.get('status', '')).startswith('DECIDED BY THE ORIGINATOR'): P.append('%s: status %s' % (e['id'], e.get('status')))
    return P, d
def selftest():
    cases = [('an unlabelled ranking is found', len(hits('SUMMARY: The sharpest was the Introduction.')) == 1),
             ('a labelled evaluation passes', hits('SUMMARY: [EVALUATIVE] The sharpest was the Introduction.') == []),
             ('a ranking by a stated criterion passes', hits('SUMMARY: By the criterion of reach, the most consequential was L-503.') == []),
             ('the question verbatim is left out', hits('QUESTION VERBATIM: What is the most likely scenario?\nFRAME: x') == []),
             ('a quotation is a mention', hits('A peer wrote "the most important point".') == []),
             ('a plain finding passes', hits('SUMMARY: Six places were found and corrected.') == []),
             ('the held register passes', held()[0] == [])]
    for n, ok in cases: print('%-50s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('JUDGMENT BOUNDARY SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--held']:
        P, d = held(); n = len(d['entries'])
        for e in d['entries']: print('  %s %-19s %s -- %s' % (e['id'], e['kind'], e['item'][:70], e['source']))
        print('HELD FOR THE ORIGINATOR (L-541 (6)): %d entries | %s' % (n, 'PASS' if not P else 'FAIL (%d)' % len(P))); [print('  - ' + p) for p in P]; sys.exit(1 if P else 0)
    if len(a) > 1 and a[0] == '--records':
        bad = 0
        for f in a[1:]:
            h = hits(open(f, encoding='utf-8').read()); bad += len(h)
            print('JUDGMENT BOUNDARY (L-541): %s | %s' % (f, 'PASS' if not h else 'FAIL (%d)' % len(h)))
            for i, s in h: print('  line %d: %s' % (i, s))
        sys.exit(1 if bad else 0)
    print(__doc__); sys.exit(2)
