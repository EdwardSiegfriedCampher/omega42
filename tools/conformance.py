#!/usr/bin/env python3
"""conformance.py -- M314 Navigator Conformance Suite (Core Part 3.40; CERTIFICATION.md).

Checks whether an AI system navigates as the protocol requires, so that the Certification Body can certify it
"Omega42 Compatible". It reads one navigation per file and checks, for each:

  REQUIRED  A1 the reported anchor equals the anchor recomputed from the domain verbatim (canonical_reference.py)
            A2 the four arms reported (Yang, Yin, 4D, Antipode) equal the arms recomputed
            A3 the format check of Part 8.0 passes (tools/format_check.py), which includes the CUMULATIVE STATUS
               line (L-490) and the LENSES SELECTED line (L-494)
            A4 layer 1 of the Congruence Record, where printed, matches the recomputation: state, voice, norm,
               stratum and half (M310, M312)
  ADVISORY  B1 the Aperture lexicon (M281), B2 the frame scan (M286) and B3 the consciousness typing guard (M315):
            sentences listed for review, never a fail
  LEVEL     SCRIPT-CAPABLE when every navigation states EXECUTION STATUS: EXECUTED and its OUTPUT ID verifies
            (tools/output_id.py); otherwise TEXT-ONLY.

A system is COMPATIBLE at its level when every REQUIRED check passes on a navigation of every domain of the set;
otherwise the report lists what is missing. Certification certifies the system's conformance to the protocol --
how it executes the rules -- and says nothing about the premise, which no measure grades (L-490), nor about the
system's other outputs.

Usage:
    python3 tools/conformance.py --key [SET]            # the recomputed answer key of the set
    python3 tools/conformance.py --check DIR [SET]      # one navigation per file in DIR
    python3 tools/conformance.py --selftest
SET defaults to records/conformance/practice_set.txt. Standard library and the tools beside this file.
"""
import os, re, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts')); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canonical_reference as cr
import congruence as cg
import format_check as fc
import aperture_audit as ap
import frame_audit as fa
import output_id as oi
import manifestation as mf
import consciousness as cs

SET = os.path.join(ROOT, 'records', 'conformance', 'practice_set.txt')
ARMS = (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12))


def load_set(path=SET):
    rows = []
    for line in open(path, encoding='utf-8'):
        if line.strip() and not line.startswith('#'):
            tag, dom = line.rstrip('\n').split('\t', 1); rows.append((tag, dom))
    return rows


def expected(domain):
    x = cr.navigate(domain)
    a, r1, r2, r3, tfi = cr.determine_anchor(x['n1'], x['n2'], x['n3'])
    s = (r1 % 9, r2 % 9)
    stratum, half, loop = mf.classify(s)
    voice = cg.sig(domain)['voice']
    return dict(n=(x['n1'], x['n2'], x['n3']), anchor=a, arms={k: (a + o) % 24 for k, o in ARMS}, state=s, voice=voice,
                norm=mf.N(s), stratum=stratum, half=half)


def key_text(path=SET):
    L = ['M314 CONFORMANCE KEY -- %s, recomputed by canonical_reference.py' % os.path.relpath(path, ROOT)]
    for tag, d in load_set(path):
        e = expected(d)
        L.append('%s | n = %s | ANCHOR P%d | Yang P%d Yin P%d 4D P%d Antipode P%d | state %s on %s, norm %d, %s, %s'
                 % (tag, e['n'], e['anchor'], e['arms']['Yang'], e['arms']['Yin'], e['arms']['4D'], e['arms']['Antipode'],
                    e['state'], e['voice'], e['norm'], e['stratum'], e['half']))
    return '\n'.join(L)


def reported_arms(text):
    k = max(text.find('DOMAIN VERBATIM'), 0); t = text[k:]
    out = {}
    for name, _ in ARMS:
        m = re.search(r'(?<![A-Za-z])%s\s*:?\s*P(\d+)' % re.escape(name), t)
        out[name] = int(m.group(1)) if m else None
    return out


def layer1(text):
    m = re.search(r'^\(1\) INTERNAL.*?state \((\d+), (\d+)\) on ([^,]+), norm (\d+), stratum (\w+(?: \w+)?), half ([A-Z]+(?: [+\-−])?)', text, re.M)
    if not m: return None
    return dict(state=(int(m.group(1)), int(m.group(2))), voice=m.group(3).strip(), norm=int(m.group(4)),
                stratum=m.group(5), half=m.group(6).replace('−', '-'))


def check_one(text):
    d = re.search(r'DOMAIN VERBATIM:\s*(.+)', text)
    if not d: return None, [('A0', False, 'no DOMAIN VERBATIM line')], [], False
    dom = d.group(1).strip(); e = expected(dom); res = []
    rep = cg.reported_anchor(text)
    res.append(('A1 anchor', rep == e['anchor'], 'reported P%s, recomputed P%d' % (rep, e['anchor'])))
    ra = reported_arms(text)
    bad = ['%s P%s (recomputed P%d)' % (k, ra[k], e['arms'][k]) for k, _ in ARMS if ra[k] != e['arms'][k]]
    res.append(('A2 arms', not bad, '; '.join(bad) or 'all four match'))
    fails = [r for r in fc.check(text) if r[0] == 'FAIL']
    res.append(('A3 format', not fails, '; '.join('%s%s' % (f[1], (': ' + f[2]) if f[2] else '') for f in fails) or 'PASS'))
    l1 = layer1(text)
    if l1:
        wrong = [k for k in ('state', 'voice', 'norm', 'stratum', 'half') if l1[k] != e[k]]
        res.append(('A4 layer 1', not wrong, ', '.join('%s %s (recomputed %s)' % (k, l1[k], e[k]) for k in wrong) or 'matches'))
    else:
        res.append(('A4 layer 1', False, 'no (1) INTERNAL line found'))
    adv = []
    au = ap.audit(text)
    adv.append(('B1 aperture (M281)', au['verdict']))
    fr = fa.scan(ap.the_answer(text))
    adv.append(('B2 frame (M286)', 'PASS' if not fr else 'REVIEW (%d sentence(s))' % len(fr)))
    ty = cs.typing_scan(ap.the_answer(text))
    adv.append(('B3 typing (M315)', 'PASS' if not ty else 'REVIEW (%d sentence(s))' % len(ty)))
    script = bool(re.search(r'EXECUTION STATUS: EXECUTED', text)) and oi.verify(text)
    return dom, res, adv, script


def report(paths, set_path=SET):
    want = dict((d, t) for t, d in load_set(set_path))
    L = ['M314 NAVIGATOR CONFORMANCE REPORT | set %s (%d domains) | %d navigation(s)' % (os.path.relpath(set_path, ROOT), len(want), len(paths))]
    covered, all_ok, all_script = set(), True, True
    for p in paths:
        dom, res, adv, script = check_one(open(p, encoding='utf-8').read())
        ok = all(r[1] for r in res); all_ok &= ok; all_script &= script
        tag = want.get(dom, 'OUTSIDE SET')
        if ok and dom in want: covered.add(dom)
        L.append('%s | %s | %s | %s' % (os.path.basename(p), tag, 'PASS' if ok else 'FAIL', 'SCRIPT-CAPABLE' if script else 'TEXT-ONLY'))
        for name, good, note in res:
            L.append('  %-12s %s  %s' % (name, 'PASS' if good else 'FAIL', note))
        for name, v in adv:
            L.append('  %-20s %s (advisory)' % (name, v))
    missing = [want[d] for d in want if d not in covered]
    level = 'SCRIPT-CAPABLE' if all_script else 'TEXT-ONLY'
    verdict = 'COMPATIBLE (%s)' % level if all_ok and not missing else 'NOT YET COMPATIBLE'
    L.append('SET COVERAGE: %d of %d domains passed%s' % (len(covered), len(want), ('; missing or failing: ' + ', '.join(missing)) if missing else ''))
    L.append('RESULT: %s -- a statement about how the system executes the protocol, not about the premise (L-490)' % verdict)
    return '\n'.join(L), verdict


def selftest():
    import subprocess, tempfile
    ok = True
    def check(label, c):
        nonlocal ok; print('%-70s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    sample = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'core_sample.py')], capture_output=True, text=True).stdout
    dom, res, adv, script = check_one(sample)
    check('the Core format sample passes every required check', all(r[1] for r in res))
    check('the format sample is script-capable (EXECUTED, OUTPUT ID verifies)', script)
    check('a wrong anchor fails A1', not dict((r[0], r[1]) for r in check_one(sample.replace('ANCHOR P6 (Seed', 'ANCHOR P7 (Seed', 1))[1])['A1 anchor'])
    bad = re.sub(r'state \(6, 0\) on Wheel, norm 0', 'state (6, 0) on Voice C, norm 2', sample, count=1)
    check('a mislabelled layer 1 fails A4', not dict((r[0], r[1]) for r in check_one(bad)[1])['A4 layer 1'])
    check('a missing LENSES SELECTED line fails A3', not dict((r[0], r[1]) for r in check_one(re.sub(r'^LENSES SELECTED.*\n', '', sample, flags=re.M))[1])['A3 format'])
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, 'nav.txt'); open(p, 'w', encoding='utf-8').write(sample)
        txt, verdict = report([p])
        check('one navigation outside the set is not compatibility', verdict == 'NOT YET COMPATIBLE' and 'OUTSIDE SET' in txt)
    e = expected('Is the protocol a computer application? If so, what kind of application will it be?')
    check('CF-03 recomputes to P3, state (3, 5) on Voice A, norm 8, MANIFEST', e['anchor'] == 3 and e['state'] == (3, 5) and e['voice'] == 'Voice A' and e['norm'] == 8 and e['half'] == 'MANIFEST')
    print('M314 SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--key': print(key_text(a[1] if len(a) > 1 else SET)); sys.exit(0)
    if a[0] == '--check':
        paths = sorted(p for p in glob.glob(os.path.join(a[1], '*')) if os.path.isfile(p))
        txt, verdict = report(paths, a[2] if len(a) > 2 else SET); print(txt); sys.exit(0 if verdict.startswith('COMPATIBLE') else 1)
    sys.exit('unknown option: ' + a[0])
