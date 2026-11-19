#!/usr/bin/env python3
"""cmudict_compare.py -- the frozen syllable rule of Core Part 1.11 against the CMU Pronouncing Dictionary (Companion Part 138.5).

    python3 records/phonetic/cmudict_compare.py PATH/TO/cmudict.dict     # writes the comparison to standard output
The dictionary is not part of the repository (Carnegie Mellon University, BSD-style licence; github.com/cmusphinx/cmudict).
The record records/phonetic/cmudict_check.txt was made from commit 74790861f652b15e4ac49015a90074ad62a27690 (24 October 2025);
anyone with that file reruns it. A word's dictionary syllables are the stressed vowel phonemes of its pronunciation, every
listed pronunciation counted. The rule defines n3 and is not changed by this comparison. Standard library only.
"""
import os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import canonical_reference as cr
def load(path):
    D = {}
    for line in open(path, encoding='utf-8', errors='replace'):
        line = line.split('#')[0].strip()
        if not line: continue
        w, *ph = line.split()
        D.setdefault(re.sub(r'\(\d+\)$', '', w), set()).add(sum(1 for p in ph if p[-1].isdigit()))
    return D
def main(path):
    D = load(path); L = ['M332 THE SYLLABLE RULE AGAINST THE CMU PRONOUNCING DICTIONARY | %s | %d headwords' % (os.path.basename(path), len(D))]
    lst = os.path.join(REPO, 'records', 'phonetic', 'syllable_list.txt')
    mine = {l.split()[0]: {int(x) for x in l.split()[1].split('/')} for l in open(lst, encoding='utf-8') if l.strip() and not l.startswith('#')}
    present = [w for w in mine if w in D]; same = [w for w in present if mine[w] & D[w]]
    L.append('  the Navigator\'s list of %d words: %d in the dictionary, %d with a count the dictionary gives (missing: %s)' % (len(mine), len(present), len(same), ', '.join(w for w in mine if w not in D)))
    tot = agree = net = 0; by = {}
    for w, s in D.items():
        if not re.fullmatch(r'[a-z]+', w): continue
        tot += 1; c = cr.count_syllables(w)
        if c in s: agree += 1
        else:
            d = c - min(s, key=lambda x: abs(x - c)); net += d; by[d] = by.get(d, 0) + 1
    L.append('  every alphabetic headword, %d words: the rule gives a dictionary count for %d, %.4f; net %+d syllables' % (tot, agree, agree / tot, net))
    L.append('  departures by size: ' + ', '.join('%+d: %d' % (k, by[k]) for k in sorted(by)))
    return '\n'.join(L)
if __name__ == '__main__':
    if len(sys.argv) != 2: print(__doc__); sys.exit(2)
    print(main(sys.argv[1]))
