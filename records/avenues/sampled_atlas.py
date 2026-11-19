#!/usr/bin/env python3
"""sampled_atlas.py -- avenue 10, a sampled atlas, under a rule frozen before any text is chosen (23 October 2026).

FROZEN RULE:
  1. The text is a public-domain text supplied as a plain-text file, named with its source and its SHA-256 before the draw.
  2. Sentences: split at '.', '!' or '?' followed by white space; whitespace collapsed; kept if 5 to 40 words long.
  3. Draw: 13 sentences without replacement, random.Random(10) over the kept list in file order (13, the size of the
     Christian atlas and of avenue 3's atlases).
  4. Each is struck with the canonical extraction and the 13 are scored with M319's K (tools/resonance.percentile,
     conditioned null, 20,000 trials, seed 319), and reported beside avenue 3's control: gamed 100, unselected 82 (L-521).
    python3 records/avenues/sampled_atlas.py TEXT.txt "SOURCE NAME"
    python3 records/avenues/sampled_atlas.py --selftest
"""
import hashlib, os, random, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
def sentences(text):
    s = [re.sub(r'\s+', ' ', x).strip() for x in re.split(r'(?<=[.!?])\s+', text)]
    return [x for x in s if 5 <= len(x.split()) <= 40]
def draw(text):
    k = sentences(text)
    return random.Random(10).sample(k, 13) if len(k) >= 13 else None
def run(path, source):
    import framework_compare as fc, resonance as rs
    raw = open(path, 'rb').read(); text = raw.decode('utf8', 'replace')
    d = draw(text)
    print('SAMPLED ATLAS (avenue 10) -- %s | SHA-256 %s | %d kept sentences' % (source, hashlib.sha256(raw).hexdigest(), len(sentences(text))))
    if not d: print('fewer than 13 kept sentences: no draw'); return
    S = [fc.strike(t) for t in d]; K, se = rs.percentile(S)
    print('K = %.3f (se %.3f) | PROXIMITY %d | %s | beside avenue 3: gamed 100, unselected 82' % (K, se, rs.prox_figure(K), rs.band(K)))
    for t, s in zip(d, S): print('   P%-2d %-8s %s' % (s['anchor'], s['voice'], t))
def selftest():
    t = ' '.join('Sentence number %d has exactly seven words.' % i for i in range(30)) + ' Too short. ' + ' '.join(['word'] * 50) + '.'
    k = sentences(t); d = draw(t)
    ok = len(k) == 30 and d == draw(t) and len(d) == 13 and len(set(d)) == 13
    print('SAMPLED ATLAS SELFTEST: %s (30 kept of 32, the draw repeatable, 13 distinct)' % ('PASS' if ok else 'FAIL')); return ok
if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    run(a[0], a[1] if len(a) > 1 else os.path.basename(a[0]))
