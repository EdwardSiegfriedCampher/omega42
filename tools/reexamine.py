#!/usr/bin/env python3
"""reexamine.py -- checks the re-reading of prior investigations (Core L-490, L-491, Appendix S.5).

records/reexamination/REEXAMINATION.md re-reads every recorded investigation under the question it was designed to
answer. This tool checks that the re-reading is complete and stays inside the frame:
  * every investigation record in records/ (and examples/corpus/) is named in some entry's Record line;
  * every entry carries the eight fields (Record, Question, Jurisdiction, Found, Then, Now, Does not decide, Open)
    and a jurisdiction among G, P, N, R, C;
  * no Now line uses court vocabulary (M286 VERDICT patterns) -- the re-reading describes, it never grades;
  * records/reexamination/jurisdiction_check.txt reads 0 failures (Builder Rule 14).
Frozen records are not read for vocabulary: they keep their text and hashes (L-411).

Usage:
    python3 tools/reexamine.py --check
    python3 tools/reexamine.py --selftest
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import frame_audit as fa

REX = os.path.join(ROOT, 'records', 'reexamination', 'REEXAMINATION.md')
JC = os.path.join(ROOT, 'records', 'reexamination', 'jurisdiction_check.txt')
FIELDS = ['Record', 'Question', 'Jurisdiction', 'Found', 'Then', 'Now', 'Does not decide', 'Open']
EXEMPT = {'reexamination', 'releases', 'corrections', 'frame', 'introduction', 'oef', 'release_record_Rev450.txt', 'release_documents_SHA256.txt', 'prominence', 'conformance', 'consciousness', 'utility', 'adaptors', 'sources', 'enrichment', 'ape', 'srcas', 'provenance', 'm267_pilot_01', 'navigator_accounts', 'instances', 'resonance', 'avenues', 'cymatics', 'fieldkit', 'claimcheck', 'howard', 'lynchpin', 'ffp', 'sessions', 'fc_drafts', 'tower', 'construct', 'instruments', 'history', 'discoveries', 'applied', 'tolerance', 'first_contact', 'necessity', 'wheel', 'multiverse', 'phase', 'phonetic', 'standing', 'open', 'd0', 'mapping', 'cosmology', 'foundations', 'math', 'opal', 'calibration', 'suite', 'vault', 'navcert', 'authorseal', 'pvir', 'lexicon', 'osl', 'dsi', 'physics', 'spectra', 'core', 'waves', 'exploration'}   # the register of tool roles (M313), the avenues list and offset space (Companion Part 84, recomputed in CI), the Field Kit examples (Companion Part 90, recomputed in CI), the manuscript version register and LAR-1 (Companion Parts 97 and 98: a list of texts and a frozen rule, no result yet), the FFP run (Core Part 12) and the session form of Companion Parts 73 to 99 (kept outside the prose, L-411), the conformance practice set (M314), the instance register (L-513), the Resonance Profiles (M319, recomputed in CI) and the CT-42 record (L-498, frozen under L-490 and L-491 from the start), the tower and the Construct arithmetic (records/tower/ and records/construct/, recomputed in CI), the Instrument Trigger Register (records/instruments/, checked in CI), the Discovery Register and the Applied Changes Register (records/discoveries/, records/applied/, checked in CI) and the Domain Zero lineage (records/d0/, checked in CI by tools/d0lineage.py) and the frozen mapping families (records/mapping/, checked in CI by tools/giza_earth.py) and the open register of vulnerabilities and improvements (records/pvir/, checked in CI by tools/pvir.py, L-560 (5)) the Lexicon (records/lexicon/, checked in CI by tools/lexicon.py, Companion Part 211) the OmegaSL rule frames (records/osl/, checked in CI by tools/osl.py, Companion Part 214) and the Discovery Significance Index (records/dsi/, checked in CI by tools/dsi.py, Companion Part 215) and the Physical Mapping Register (records/physics/, checked in CI by tools/physics_map.py, Core Rule 37) and the gap record (records/spectra/, written by tools/validation.py, Companion Part 227) and the Core economy baseline (records/core/, checked in CI by tools/core_economy.py, Core Rule 39) and the wave atlas records (records/waves/, written by tools/wave_atlas.py, Companion Part 228) and the Exploration Register (records/exploration/, Companion Part 234: what is being explored, not what was tested): not prior investigations


def entries(text):
    out = []
    for block in re.split(r'^### ', text, flags=re.M)[1:]:
        head = block.split('\n', 1)[0].strip()
        f = {}
        for m in re.finditer(r'^- \*\*(%s):\*\*(.*(?:\n(?!- \*\*|### |## ).*)*)' % '|'.join(map(re.escape, FIELDS)), block, re.M):
            f[m.group(1)] = ' '.join(m.group(2).split())
        out.append((head, f))
    return out


def problems(text, names):
    P = []
    es = entries(text)
    if not es: P.append('no entries')
    recorded = ' '.join(f.get('Record', '') for _, f in es)
    for n in names:
        if n not in recorded: P.append('investigation record not re-read: %s' % n)
    for head, f in es:
        miss = [k for k in FIELDS if k not in f]
        if miss: P.append('%s: missing %s' % (head, ', '.join(miss)))
        j = f.get('Jurisdiction', '')
        if not re.match(r'^[GPNRC]\b', j): P.append('%s: jurisdiction not among G, P, N, R, C' % head)
        now = f.get('Now', '')
        if fa.scan(now): P.append('%s: court vocabulary in Now' % head)
    return P, len(es)


def investigation_names():
    names = []
    rec = os.path.join(ROOT, 'records')
    for n in sorted(os.listdir(rec)):
        if n in EXEMPT or n.startswith('.'): continue
        names.append('records/' + n + ('/' if os.path.isdir(os.path.join(rec, n)) else ''))
    names.append('examples/corpus/')
    return names


def check():
    P, k = problems(open(REX, encoding='utf-8').read(), investigation_names())
    jc = open(JC, encoding='utf-8').read()
    m = re.search(r'RESULT: (\d+) of (\d+) PASS', jc)
    if not m or m.group(1) != m.group(2): P.append('jurisdiction check does not read all PASS')
    print('RE-EXAMINATION (L-490, L-491): %d entries | %d records covered | problems %d' % (k, len(investigation_names()), len(P)))
    for p in P: print('  ' + p)
    print('RESULT: %s' % ('PASS' if not P else 'FAIL'))
    return not P


def selftest():
    good = ('### RX-01 x\n- **Record:** `records/a/`\n- **Question:** q\n- **Jurisdiction:** G\n- **Found:** f\n- **Then:** t\n'
            '- **Now:** an internal result, complete by recomputation.\n- **Does not decide:** d\n- **Open:** none\n')
    cases = [('complete entry passes', good, ['records/a/'], True),
             ('uncovered record fails', good, ['records/a/', 'records/b/'], False),
             ('missing field fails', good.replace('- **Open:** none\n', ''), ['records/a/'], False),
             ('court vocabulary in Now fails', good.replace('an internal result, complete by recomputation.', 'this run supports the premise.'), ['records/a/'], False),
             ('bad jurisdiction fails', good.replace('Jurisdiction:** G', 'Jurisdiction:** Science'), ['records/a/'], False)]
    ok = True
    for name, t, n, want in cases:
        got = not problems(t, n)[0]
        print('  %-34s %s' % (name, 'OK' if got == want else 'MISMATCH')); ok &= got == want
    print('RE-EXAMINATION SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--check']: sys.exit(0 if check() else 1)
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    print(__doc__); sys.exit(2)
