#!/usr/bin/env python3
"""M267 pilot 01 -- the canonical coordinates of the frozen domain set, recomputed (Core Part 3.18; Companion Part 71).
Prints, for each of the twenty frozen domains, its DOMAIN SHA-256, counts, anchor and arms, by the unchanged reference
script; the decoy coordinates and the slot order are in the sealed key, which this script never reads. Run from the
repository root: python3 records/m267_pilot_01/compute.py"""
import os, sys, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import canonical_reference as cr
DOMAINS = [
    'What is courage?', 'How do musicians keep playing together without speaking during a long concert?',
    'Why do people forgive?', 'What makes a bridge beautiful?',
    'How should a river be managed?', 'Why do people collect things?',
    'How should a small coastal town prepare for rising seas and storms?', 'What should a young doctor learn from the oldest nurses on a hospital ward?',
    'Solitude', 'Gratitude',
    'What is the role of grief?', 'What is a fair wage?',
    'How does a forest recover after fire?', 'Why do people climb mountains?',
    'What makes a promise binding between two people?', 'How should teachers handle mistakes?',
    'How should parents talk with teenagers about money, work and long term choices?', 'What makes a neighbourhood feel safe to children walking home from school?',
    'Why do markets crash?', 'Why do we tell stories?']
NAMES = cr.POSITION_NAMES
if __name__ == '__main__':
    print('M267 PILOT 01 -- CANONICAL COORDINATES OF THE FROZEN DOMAIN SET')
    for i, d in enumerate(DOMAINS, 1):
        r = cr.navigate(d); a = r['anchor']; y, yi, f, an = cr.derive_arms(a)
        print('M267P1-%02d | %s | SHA-256 %s | n = (%d, %d, %d) | ANCHOR P%d %s | Yang P%d | Yin P%d | 4D P%d | Antipode P%d' % (
            i, d, cr.domain_sha256(d)[:16], r['n1'], r['n2'], r['n3'], a, NAMES[a], y, yi, f, an))
    from collections import Counter
    c = Counter(cr.navigate(d)['anchor'] for d in DOMAINS)
    print('ANCHORS: ' + ' | '.join('P%d %d' % (k, c[k]) for k in sorted(c)))
