#!/usr/bin/env python3
"""adversarial_atlas.py -- avenue 3, the adversarial atlas against K (records/avenues/avenues.txt; seq_0021 14).

FROZEN RULE (written before any K was computed, 23 October 2026, SEQ 36):
  1. A pool of sentences about a bus timetable, with no claim to the structure, is generated from the fixed
     templates and word lists below, in the order written.
  2. Each sentence is struck with the canonical extraction (tools/framework_compare.strike).
  3. GAMED atlas: the first 13 sentences of the pool that stand on Voice C (HOME) are kept -- 13, the size of the
     Christian atlas. CONTROL atlas: the first 13 sentences of the pool, unselected.
  4. Both are scored with M319's K (tools/resonance.percentile, conditioned null, 20,000 trials, seed 319).
  DECISION RULE (avenues.txt): if the gamed atlas reaches K >= 0.95, no idea's PROXIMITY is quoted as evidence
  before avenue 10 (sampled atlases); the figure is reported only beside this control.
    python3 records/avenues/adversarial_atlas.py      # diffed in CI against adversarial_atlas_output.txt
"""
import os, sys, itertools
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import framework_compare as fc, resonance as rs

ROUTES = ['bus', 'night bus', 'airport shuttle', 'school bus', 'express coach', 'river ferry']
TIMES = ['at seven', 'at half past eight', 'every twenty minutes', 'before noon', 'after the market closes', 'on Sundays only']
PLACES = ['from the station', 'from platform four', 'from the old library', 'near the harbour', 'from the hospital gate', 'outside the bakery']
pool = ['The %s leaves %s %s.' % (r, p, t) for r, t, p in itertools.product(ROUTES, TIMES, PLACES)]

def sig(text):
    return fc.strike(text)

sigs = [(t, sig(t)) for t in pool]
gamed = [(t, s) for t, s in sigs if s['voice'] == 'Voice C'][:13]
control = sigs[:13]
print('ADVERSARIAL ATLAS (avenue 3) -- pool %d sentences; on Voice C: %d (%.3f)' % (len(pool), sum(s['voice'] == 'Voice C' for _, s in sigs), sum(s['voice'] == 'Voice C' for _, s in sigs) / len(pool)))
for name, atlas in (('GAMED (first 13 on Voice C)', gamed), ('CONTROL (first 13, unselected)', control)):
    S = [s for _, s in atlas]
    K, se = rs.percentile(S)
    m = fc.measures(S)
    print('%s: K = %.3f (se %.3f) | PROXIMITY %d | %s | HOME %d SEEDS %d LINKS %d MIRRORS %d' % (
        name, K, se, rs.prox_figure(K), rs.band(K), m['HOME'], m['SEEDS'], m['LINKS'], m['MIRRORS']))
    for t, s in atlas: print('   P%-2d %-8s %s' % (s['anchor'], s['voice'], t))
Kg = rs.percentile([s for _, s in gamed])[0]
print('DECISION: %s' % ('the gamed atlas reaches K >= 0.95: PROXIMITY can be raised by choosing statements; no idea\'s PROXIMITY is quoted as evidence before avenue 10, and each is shown beside this control' if Kg >= 0.95 else 'the gamed atlas stays below 0.95: selection on HOME alone does not reach the band'))
