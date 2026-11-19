#!/usr/bin/env python3
"""single_figure.py -- an exploration (Companion Part 82, enrichment E14): what each candidate single figure of
resonance would tell a Striker about the 22 profiled ideas. It reads the frozen inputs M319 reads and recomputes K;
nothing here is operative. Standard library and tools/resonance.py.

    python3 records/resonance/single_figure.py
"""
import os, sys, statistics, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import resonance as rs, framework_compare as fc

def of_record():
    """K of record and its robustness, read from records/resonance/profiles.txt (the M319 cards), so that every figure
    here agrees with the cards: a band is robust when neither the leave-one-measure-out range nor the statement
    jackknife carries the flag BAND NOT ROBUST."""
    import re
    t = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profiles.txt'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'^([A-Z]+)\s+\[[A-Z]+\].*?\n  4 CONGRUENCE \(computed, CDT-A\): K ([0-9.]+) (.*?)\n', t, re.M | re.S):
        out[m.group(1)] = (float(m.group(2)), 'BAND NOT ROBUST' not in m.group(3))
    return out

def main(trials=8000):
    rows = []; rec = of_record()
    for idea in rs.IDEAS:
        name, code, atlas, src, prefix, status, nav = idea
        f = rs.features(src, prefix); F = sum(f) / 6
        sigs = [fc.strike(t) for _, t in rs.rows_of(atlas)]
        null = rs._null(sigs, True, trials, 319); obs = fc.measures(sigs)
        K, robust = rec[name.upper()]
        exp = sum(statistics.fmean(n[k] for n in null) for k in rs.MEET); got = sum(obs[k] for k in rs.MEET)
        rows.append(dict(name=name, F=F, K=K, robust=robust, ratio=got / exp if exp else float('nan'), got=got, exp=exp))
    F = [r['F'] for r in rows]; K = [r['K'] for r in rows]
    L = ['SINGLE-FIGURE EXPLORATION (Companion Part 82; enrichment E14 PROPOSED) -- 22 ideas; FIT = features share (judged); K = congruence percentile given word counts, of record (records/resonance/profiles.txt); the expected meetings of candidate 3 from %d trials' % trials, '']
    L.append('CANDIDATE 1: an average of the two, w x FIT + (1 - w) x K')
    for w in (0.3, 0.5, 0.7):
        S = [w * a + (1 - w) * b for a, b in zip(F, K)]
        top = [rows[i]['name'] for i in sorted(range(len(S)), key=lambda i: -S[i])[:5]]
        L.append('  w = %.1f: correlation with K %.2f, with FIT %.2f | the five "closest": %s' % (w, rs.spearman(S, K), rs.spearman(S, F), ', '.join(top)))
    L.append('  spread: FIT runs %.2f to %.2f (sd %.2f), K runs %.3f to %.3f (sd %.2f) -- the axis with the wider spread decides an average, whatever the weight says' % (min(F), max(F), statistics.pstdev(F), min(K), max(K), statistics.pstdev(K)))
    pairs = [('Ra', 'Jewish'), ('Kauffman', 'Hoffman')]
    by = {r['name']: r for r in rows}
    for a, b in pairs:
        L.append('  example: %s (FIT %.2f, K %.3f) and %s (FIT %.2f, K %.3f) -- the average at w = 0.5 is %.2f and %.2f: the figure cannot say which kind of closeness each has' % (
            a, by[a]['F'], by[a]['K'], b, by[b]['F'], by[b]['K'], (by[a]['F'] + by[a]['K']) / 2, (by[b]['F'] + by[b]['K']) / 2))
    L.append('')
    L.append('CANDIDATE 2: a product, FIT x K -- zero whenever either is near zero; the Pythagorean atlas (K %.3f) reads as no resonance though its fit is %.2f' % (by['Pythagorean']['K'], by['Pythagorean']['F']))
    L.append('')
    L.append('CANDIDATE 3: congruence alone, as "times chance" (meetings observed / meetings expected at the same word counts)')
    for r in sorted(rows, key=lambda r: -r['ratio']):
        L.append('  %-12s %.2f x chance (%d meetings, %.1f expected)' % (r['name'], r['ratio'], r['got'], r['exp']))
    L.append('  one number, computed, with a plain meaning (1.00 = chance); it says nothing about fit')
    L.append('')
    L.append('CANDIDATE 4: one two-part sign (the Resonance Sign) -- a letter for fit, a mark for congruence: A FIT >= 0.75, B 0.50 to 0.74, C below 0.50; + ABOVE CHANCE, 0 AT CHANCE, - BELOW CHANCE; a band that the robustness tests can move is written in lower case')
    for idea, r in zip(rs.IDEAS, rows):
        letter = 'A' if r['F'] >= 0.75 - 1e-9 else ('B' if r['F'] >= 0.5 - 1e-9 else 'C')
        mark = {'ABOVE CHANCE': '+', 'AT CHANCE': '0', 'BELOW CHANCE': '-'}[rs.band(r['K'])]
        r['sign'] = letter + mark if r['robust'] else letter.lower() + mark
    counts = {}
    for r in rows: counts.setdefault(r['sign'], []).append(r['name'])
    for s in sorted(counts): L.append('  %s  %s' % (s, ', '.join(counts[s])))
    L.append('  one sign, read at once, that keeps both answers: A0 = fits the frame well, its statements meet the structure at chance; a0 = the same, and one statement or one measure can move the band')
    L.append('  the four signs off the middle row are all in lower case: no band outside chance in the record is robust')
    L.append('')
    L.append('THE TWO AXES: Spearman %.2f over the 22 -- with independent axes, any single number either drops one answer or lets the wider one decide' % rs.spearman(F, K))
    return '\n'.join(L)

if __name__ == '__main__':
    print(main())
