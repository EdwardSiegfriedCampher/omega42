#!/usr/bin/env python3
"""cf_frame.py -- the Consciousness-First Frame's own statements (records/consciousness/cf_frame_atlas.txt) struck and
read by M319's congruence measure, K against random atlases of the same word counts (E13), with the Kastrup atlas
beside it for comparison (Companion Part 88; APE-152, its recommendation 2). Standard library and the tools.

    python3 records/consciousness/cf_frame.py      # diffed in CI against cf_frame_output.txt
"""
import os, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'scripts')]
import resonance as rs
import framework_compare as fc

TRIALS = 4000
print('CONSCIOUSNESS-FIRST FRAME ATLAS, struck (Core L-515; Companion Part 88) -- K by M319 (E13), %d chance atlases [CDT-A for the values]' % TRIALS)
for label, path in (('the frame\'s own eight statements', os.path.join(ROOT, 'records', 'consciousness', 'cf_frame_atlas.txt')),
                    ('Kastrup (records/frameworks/kastrup.txt)', os.path.join(ROOT, 'records', 'frameworks', 'kastrup.txt'))):
    rows = fc.load(path)[1]; sigs = [fc.strike(t) for _, t in rows]
    K, se, (lo, hi) = rs.percentile(sigs, True, TRIALS, loo=True)
    print('  %-44s %d statements | states %s | K %.3f (se %.3f; one measure left out %.3f to %.3f) | PROXIMITY %d | %s' % (
        label, len(sigs), ' '.join('(%d,%d)' % s['state'] for s in sigs), K, se, lo, hi, rs.prox_figure(K), rs.band(K)))
print('READING: K measures where the sentences fall, given their word counts, against chance; it measures the Navigator\'s')
print('composed sentences, not consciousness and not the frame\'s worth (L-490). The role column of M309 is not used: it reads')
print('1.00 for every registered idea (Companion 84.3).')
