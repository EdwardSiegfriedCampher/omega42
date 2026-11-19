#!/usr/bin/env python3
"""phonetic.py -- M332 Phonetic Reading: the syllable vote in the anchor, the spoken form and the letter classes, printed beside the
canonical coordinate (Core Part 3.58; Companion Part 136).

The coordinate already reads one phonetic count: n3, the syllables of the content words by the frozen rule of Core
Part 1.11 (vowel groups in the spelling). The anchor is the majority of r1, r2, r3, or r1 when all differ, so the
syllables decide the anchor exactly when r2 = r3 != r1. This tool shows a strike's phonetic layer beside its coordinate:

    python3 tools/phonetic.py --strike "TEXT"   # each content word with its letters, vowel groups and syllables; the role
                                                # of r3 in the anchor; which change of one syllable would move it; the
                                                # spoken form (digits read as number words) beside the written; the
                                                # letter-class profile, an orthographic proxy with no meaning attached
    python3 tools/phonetic.py --law             # the exact share of the 729 triples in which the syllables decide the anchor
    python3 tools/phonetic.py --rule FILE       # the frozen syllable rule against a list of words with dictionary counts
    python3 tools/phonetic.py --selftest
Nothing here changes the canonical computation (Core L-494 (4)): the spoken form and the profile are readings beside it,
and what a sound is like to hear is the Observer's (Core Part 7, L-441). Standard library only.
"""
import os, re, sys
from fractions import Fraction as F
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import canonical_reference as cr
def anchor_of(r1, r2, r3):
    return r2 if (r2 == r3 and r2 != r1) else r1
def role(r1, r2, r3):
    if r2 == r3 != r1: return 'DECISIVE: r2 = r3 = %d outvotes r1 = %d, so the syllables set the anchor' % (r2, r1)
    if r1 == r3 != r2: return 'CONFIRMING: r3 = r1 = %d; the anchor would be r1 without it' % r1
    if r1 == r2 == r3: return 'UNANIMOUS: all three counts agree'
    return 'SILENT: the anchor is r1 = %d whatever r3 is, unless r3 came to equal r2 = %d' % (r1, r2) if r1 != r2 else 'SILENT: r1 = r2 = %d decide without it' % r1
def law():
    T = [(a, b, c) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
    dec = sum(1 for a, b, c in T if b == c != a)
    sens = F(sum(sum(1 for c2 in range(1, 10) if c2 != c and anchor_of(a, b, c2) != anchor_of(a, b, c)) for a, b, c in T), len(T) * 8)
    L = ['M332 THE LAW OF THE PHONETIC VOTE | anchor = the majority of (r1, r2, r3), r1 when all differ (Core Part 1.4)',
         '  the syllables decide the anchor in %d of 729 triples, %s = %.4f, exactly when r2 = r3 != r1; the anchor is r1 in the other %d, 73/81' % (dec, F(dec, 729), dec / 729, 729 - dec),
         '  a change of r3 alone, to any of its 8 other values, moves the anchor with probability %s = %.4f; a change of r1 alone with probability %s' % (sens, float(sens), F(sum(sum(1 for a2 in range(1, 10) if a2 != a and anchor_of(a2, b, c) != anchor_of(a, b, c)) for a, b, c in T), len(T) * 8)),
         '  one syllable more changes n3 by 1 and r3 = dr(5 n3) by 5 (mod 9): one step along the placement order 5, 1, 6, 2, 7, 3, 8, 4, 9']
    return '\n'.join(L)
UNITS = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'twenty thirty forty fifty sixty seventy eighty ninety'.split()
def say(n):
    n = int(n)
    if n < 20: return UNITS[n]
    if n < 100: return TENS[n // 10 - 2] + ('' if n % 10 == 0 else ' ' + UNITS[n % 10])
    if n < 1000: return UNITS[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' and ' + say(n % 100))
    if n < 10000: return say(n // 1000) + ' thousand' + ('' if n % 1000 == 0 else ' ' + say(n % 1000))
    return ' '.join(UNITS[int(d)] for d in str(n))
def spoken(text):
    t = re.sub(r'(?<=[A-Za-z])(?=\d)|(?<=\d)(?=[A-Za-z])', ' ', text)
    return re.sub(r'\d+', lambda m: say(m.group(0)), t)
CLASSES = (('vowel letters', 'aeiou'), ('plosive letters', 'pbtdkgcq'), ('fricative letters', 'fvszhxj'), ('nasal letters', 'mn'), ('liquid letters', 'lr'), ('glide letters', 'wy'))
def profile(words):
    s = ''.join(re.sub(r'[^a-z]', '', w.lower()) for w in words)
    return [(n, sum(ch in cs for ch in s)) for n, cs in CLASSES], len(s)
def groups(w):
    w = re.sub(r'[^a-z]', '', w.lower()); out = re.sub(r'[^aeiouyw]', '.', w)
    return out
def strike_report(text):
    nv = cr.navigate(text); content = cr.extract_content_words(cr.spnp(text))
    r1, r2, r3 = nv['r1'], nv['r2'], nv['r3']
    L = ['M332 PHONETIC READING (Core Part 3.58) | n = (%d, %d, %d), r = (%d, %d, %d), anchor P%d' % (nv['n1'], nv['n2'], nv['n3'], r1, r2, r3, nv['anchor'])]
    L.append('  the syllables of the content words (Core Part 1.11, vowel groups in the spelling):')
    L.append('    ' + ' | '.join('%s %d' % (w, cr.count_syllables(w)) for w in content))
    L.append('  r3 in the vote: ' + role(r1, r2, r3))
    moves = []
    for dn in (-2, -1, 1, 2):
        n3 = nv['n3'] + dn
        if n3 < 1: continue
        a2 = anchor_of(r1, r2, cr.cpp(n3))
        moves.append('n3 %+d -> r3 = %d, anchor P%d%s' % (dn, cr.cpp(n3), a2, '' if a2 == nv['anchor'] else ' (MOVES)'))
    L.append('  one or two syllables more or less: ' + '; '.join(moves))
    sp = spoken(text)
    if sp != text:
        ns = cr.navigate(sp)
        L.append('  the strike as spoken (digits read as words, a reading beside the coordinate, never in its place): n = (%d, %d, %d), r = (%d, %d, %d), anchor P%d%s' % (ns['n1'], ns['n2'], ns['n3'], ns['r1'], ns['r2'], ns['r3'], ns['anchor'], '' if ns['anchor'] == nv['anchor'] else ' -- the written and the spoken strike part here'))
    else:
        L.append('  the strike as spoken: no digits, so the written and the spoken strike count alike')
    prof, tot = profile(content)
    L.append('  letter classes of the content words (%d letters; an orthographic proxy for sound classes, no meaning attached): %s' % (tot, ', '.join('%s %d' % p for p in prof)))
    return '\n'.join(L)
def rule_report(path):
    rows = []
    for line in open(path, encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line: continue
        w, n = line.split(); rows.append((w, [int(x) for x in n.split('/')]))
    ok = [w for w, ns in rows if cr.count_syllables(w) in ns]
    bad = [(w, ns, cr.count_syllables(w)) for w, ns in rows if cr.count_syllables(w) not in ns]
    L = ['M332 THE SYLLABLE RULE AGAINST %d WORDS WITH DICTIONARY COUNTS | agreement %d of %d = %.3f' % (len(rows), len(ok), len(rows), len(ok) / len(rows))]
    L.append('  the full table, every word (n3 is the rule\'s count; s3 the dictionary\'s; d = n3 - s3):')
    for w, ns in rows:
        c = cr.count_syllables(w); near = min(ns, key=lambda x: abs(x - c))
        L.append('  %-18s s3 %-5s n3 %d  d %+d  %s' % (w, '/'.join(map(str, ns)), c, c - near, 'AGREE' if c in ns else 'PART  (%s)' % groups(w)))
    net = sum(c - min(ns, key=lambda x: abs(x - c)) for w, ns, c in bad)
    L.append('  net error over the list: %+d syllables; the rule is frozen and canonical (Core Part 1.11): it defines n3, and these are the places where n3 and the spoken syllables part' % net)
    return '\n'.join(L)
def selftest():
    T = [(a, b, c) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
    cases = [('the syllables decide the anchor in 72 of 729 triples', sum(1 for a, b, c in T if b == c != a) == 72),
             ('the rule here equals the canonical anchor', all(anchor_of(cr.cpp(a), cr.cpp(b), cr.cpp(c)) == cr.determine_anchor(a, b, c)[0] for a in range(1, 19) for b in range(1, 19) for c in range(1, 19))),
             ('a digit is read as a number word', spoken('Omega42') == 'Omega forty two'),
             ('one syllable more moves r3 by 5 mod 9', all((cr.cpp(n + 1) - cr.cpp(n)) % 9 == 5 for n in range(1, 200))),
             ('the profile counts every letter once at most', all(sum(n for _, n in profile([w])[0]) <= len(w) for w in ['strength', 'rhythm', 'queue']))]
    for nm, ok in cases: print('%-55s %s' % (nm, 'PASS' if ok else 'FAIL'))
    print('M332 SELFTEST: %d of %d' % (sum(ok for _, ok in cases), len(cases))); return all(ok for _, ok in cases)
if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--law']: print(law()); sys.exit(0)
    if len(a) == 2 and a[0] == '--rule': print(rule_report(a[1])); sys.exit(0)
    if len(a) == 2 and a[0] == '--strike': print(strike_report(a[1])); sys.exit(0)
    print(__doc__); sys.exit(2)
