#!/usr/bin/env python3
"""continuity.py -- what the Construct left unchanged, and what it added (Companion Part 139; Core L-528).

The Construct entered the record on 28 October 2026 (SEQ 51) and was adopted as one integrated part of the system on
29 October (L-528). This script checks, from the repository alone, that it is an addition and not a revision of the
navigation that came before it:
  (1) the reference script is byte-identical to the one fixed by the release record of 9 October 2026, by file and by
      canonical form, so that every coordinate of every strike is the one it was before the Construct;
  (2) the reference script imports nothing from the Construct;
  (3) every navigation record from before the Construct that states its counts recomputes to them today;
  (4) the Construct's own results, read from their diffed outputs: the domains, the regions, the affine law, the return
      paths and the forecast test;
and it lists what a strike can now be read for that it could not before. Standard library only.
"""
import glob, hashlib, json, os, re, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, 'scripts'))
import canonical_reference as cr
def rel(*p): return os.path.join(REPO, *p)
def main():
    L = ['WHAT THE CONSTRUCT LEFT UNCHANGED, AND WHAT IT ADDED (Companion Part 139; Core L-528)', '']
    rr = open(rel('records', 'release_record_Rev450.txt'), encoding='utf-8').read()
    fh = re.search(r'([0-9a-f]{64})  scripts/canonical_reference\.py', rr).group(1)
    ch = re.search(r'SCRIPT SHA-256 \(canonical form\): ([0-9a-f]{64})', rr).group(1)
    now_f = hashlib.sha256(open(rel('scripts', 'canonical_reference.py'), 'rb').read()).hexdigest()
    out = subprocess.run([sys.executable, rel('scripts', 'canonical_reference.py'), '--version'], capture_output=True, text=True).stdout
    now_c = re.search(r'SCRIPT SHA-256: ([0-9a-f]{64})', out).group(1)
    L.append('(1) THE REFERENCE SCRIPT [EXACT]')
    L.append('  file SHA-256 now %s... and in the release record of 9 October %s...: %s' % (now_f[:16], fh[:16], 'IDENTICAL' if now_f == fh else 'DIFFERENT'))
    L.append('  canonical form now %s... and in the release record %s...: %s' % (now_c[:16], ch[:16], 'IDENTICAL' if now_c == ch else 'DIFFERENT'))
    src = open(rel('scripts', 'canonical_reference.py'), encoding='utf-8').read()
    imps = sorted(set(re.findall(r'^\s*(?:from|import)\s+([\w.]+)', src, re.M)))
    L.append('(2) WHAT IT IMPORTS: %s -- %s' % (', '.join(imps), 'nothing from the Construct' if not any('construct' in i for i in imps) else 'THE CONSTRUCT'))
    L.append('(3) NAVIGATIONS FROM BEFORE THE CONSTRUCT THAT STATE THEIR COUNTS [EXACT]')
    tot = same = 0
    for f in sorted(glob.glob(rel('submissions', 'navigations', 'NAV-2026-00*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        if d['accepted_utc'][:10] >= '2026-10-28': continue
        t = open(f[:-5] + '.txt', encoding='utf-8').read()
        m = re.search(r'n1=(\d+) words, n2=(\d+) letters, n3=(\d+)', t)
        if not m: continue
        n = cr.navigate(d['domain']); tot += 1; ok = (n['n1'], n['n2'], n['n3']) == tuple(int(x) for x in m.groups()); same += ok
        L.append('  %s (%s, %s): stated %s, recomputed (%d, %d, %d), anchor P%d: %s' % (d['id'], d['accepted_utc'][:10], d.get('execution', '?'), '(%s, %s, %s)' % m.groups(), n['n1'], n['n2'], n['n3'], n['anchor'], 'SAME' if ok else 'DIFFERENT, a count made by hand by a TEXT-ONLY Navigator' if 'TEXT' in d.get('execution', '') else 'DIFFERENT'))
    sc = [x for x in L if x.startswith('  NAV-') and 'TEXT-ONLY' not in x]
    L.append('  %d of %d recompute to their stated counts; of the counts made by the script, %d of %d' % (same, tot, sum('SAME' in x for x in sc), len(sc)))
    L.append('(4) WHAT THE CONSTRUCT ADDED, FROM ITS DIFFED OUTPUTS [EXACT]')
    po = open(rel('records', 'construct', 'primordial_output.txt'), encoding='utf-8').read()
    co = open(rel('records', 'construct', 'columns_output.txt'), encoding='utf-8').read()
    so = open(rel('records', 'construct', 'sa_lotto_output.txt'), encoding='utf-8').read()
    for pat, src_ in ((r'echo regions: .*', po), (r'the workbook\'s own 216 echo counters.*', po), (r'derived domains whose every node cell .*', co), (r'forward and return paths, by value .*', co), (r'the largest z over all 69 .*', so), (r'AMPLIFY \(repeat\).*', so)):
        m = re.search(pat, src_)
        L.append('  ' + (m.group(0).strip() if m else 'NOT FOUND: ' + pat))
    L.append('')
    L.append('WHAT A STRIKE CAN NOW BE READ FOR, BEYOND ITS COORDINATE AND ITS FOUR ARMS')
    for x in ('its value placed in all 27 domains, Domain Zero and 26 rebuilt on their seeds\' fields (M326 --places; Core MATH-55)',
              'its return as well as its forward: forward, return, stillness and turn, of one length each way (M328; D-003)',
              'the move between voices that the units of Z/9 make, apart from a step of the law (D-009)',
              'a sequence tested against shuffled history and against the latest row before any forecast is issued, a game of chance never forecast (M326 gate, M325; L-525, L-526)',
              'a run manifest with fingerprints and one status (L-528 (3))',
              'the two worlds, the units and the Crown, that the derivation of the grammar then read as the anatomy of Z/9 (D-012)'):
        L.append('  - ' + x)
    return '\n'.join(L)
if __name__ == '__main__':
    print(main())
