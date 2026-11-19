#!/usr/bin/env python3
"""srcas_run.py -- the automatic trigger of SNCA and SR-CAS, run (Core Part 6.1, 6.2, L-549 (4), L-489).

On receipt of any output from another Navigator the review runs unasked. This tool runs every part of it that a script
can decide, so that no received output waits on a Navigator remembering to review it:
  1. each output's form is identified (tools/output_form.py), never assumed from who sent it;
  2. SNCA, decidable layer, for each received output: its quoted domain, DOMAIN SHA-256 and the script's coordinate;
     the values it reports, each checked against the script; its form checker; the L-418 jargon scan of its reading;
  3. SR-CAS for every pair of outputs of one domain (the Navigator's own first): the PRE-SR-CAS VERBATIM VERIFICATION,
     the M270 values, T1 computed, T2 from the form checks, T1.5-L from M225, T2.5 from each synthesis echoed by the
     script, and the Base Score of what is computed.
What a script cannot decide -- the per-relation verdicts of T1.5-S, T3, the findings' wording, the verdict -- is marked
[NAVIGATOR] and completed by the Navigator in the report filed under records/srcas/ (tools/srcas_check.py checks it).

    python3 tools/srcas_run.py OWN.txt RECEIVED.txt [...]   # OWN may be NONE when the Navigator has not navigated the domain
    python3 tools/srcas_run.py --selftest
Standard library only. It reads and prints; it never edits a record.
"""
import importlib.util, itertools, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel)); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


CR = _load('scripts/canonical_reference.py', 'cr'); OF = _load('tools/output_form.py', 'of'); MM = _load('scripts/m193_m225.py', 'mm')
KEYS = ('n1', 'n2', 'n3', 'anchor', 'yang', 'yin', '4d', 'antipode')
SKEYS = {'yang': 'yang_i', 'yin': 'yin_i', '4d': 'fourd_i', 'antipode': 'antipode_i'}


def clean(s):
    return re.sub(r'\*\*|__', '', s).strip()


def domain_of(text):
    for rx in (r'^\s*DOMAIN VERBATIM:\s*(.+)$', r'^\s*\**DOMAIN \(verbatim\):\**\s*(.+)$', r'^QUESTION VERBATIM:\s*(.+)$'):
        m = re.search(rx, text, re.M)
        if m:
            return clean(m.group(1))
    return None


def reported(text):
    t = clean(text); v = {}
    m = re.search(r'^(?:======= SUBSTRATE LOCK =======|\[\d+\] SUBSTRATE LOCK|\**LOCKED SUBSTRATE)', t, re.M)
    if m: t = t[m.start():]   # the navigation's own values, after any calibration strike (M211)
    for k in ('n1', 'n2', 'n3'):
        m = re.search(r'\b%s\s*=\s*(\d+)' % k, t)
        if m: v[k] = int(m.group(1))
    m = re.search(r'\bn = \((\d+), (\d+), (\d+)\)', t)
    if m and 'n1' not in v: v.update(n1=int(m.group(1)), n2=int(m.group(2)), n3=int(m.group(3)))
    m = re.search(r'\bANCHOR:?\s*\(?P(\d+)', t)
    if m: v['anchor'] = int(m.group(1))
    for k, w in (('yang', 'Yang'), ('yin', 'Yin'), ('4d', '4D'), ('antipode', 'Antipode')):
        m = re.search(r'\b%s\b[^P\n]{0,24}P(\d+)' % w, t)
        if m: v[k] = int(m.group(1))
    return v


def script_values(domain):
    r = CR.navigate(domain); v = dict(n1=r['n1'], n2=r['n2'], n3=r['n3'], anchor=r['anchor'])
    v.update({k: r[s] for k, s in SKEYS.items()}); return v, r


def reading_of(text):
    m = re.search(r'^┌─ THE ANSWER ─┐\s*$(.*?)^└', text, re.M | re.S)
    if m: return m.group(1).strip()
    m = re.search(r'STRUCTURAL READING[^\n]*\n(.*?)(?:\n\**NAVIGATOR INTERFERENCE|\Z)', text, re.S)
    if m: return clean(m.group(1))
    m = re.search(r'^#+\s*ANSWER\s*$(.*?)^#+\s*TAKEAWAY', text, re.M | re.S)
    return clean(m.group(1)) if m else None


def form_score(path, text, form):
    if form == 'UNFORMATTED':
        return 0.0, 0, 0
    res = [r for r in OF.form_checks(text, form) if isinstance(r, tuple) and len(r) == 3]
    n = len(res); p = sum(1 for r in res if r[0] == 'PASS')
    return (p / n if n else 0.0), p, n


def profile(path):
    text = open(path, encoding='utf-8').read(); form = OF.identify(text); dom = domain_of(text)
    P = dict(path=path, text=text, form=form, domain=dom, hash=CR.domain_sha256(dom) if dom else None, rep=reported(text))
    if dom:
        P['script'], P['nav'] = script_values(dom)
    P['t2'], P['pass'], P['checks'] = form_score(path, text, form)
    P['reading'] = reading_of(text)
    _j = MM.jargon_scan(P['reading'], CR) if P['reading'] else None
    _h = sorted(k for k, x in (_j or {}).items() if k != 'RESULT' and x)
    P['jargon'] = 'NOT RUN' if _j is None else (_j['RESULT'] + ('' if not _h else ' (' + ', '.join(_h) + ': ' + ', '.join(sorted(set(str(y) for k in _h for y in _j[k]))[:8]) + ')'))
    if P['reading'] and dom:
        e = CR.navigate(P['reading'])['anchor']; P['echo'] = e; P['sas'] = CR.sas(P['script']['anchor'], e)
    return P


def value_line(P):
    if not P.get('domain'):
        return 'NO DOMAIN QUOTED -- no value can be checked'
    out = []
    for k in KEYS:
        s = P['script'][k]; r = P['rep'].get(k)
        out.append('%s %s%s' % (k, r if r is not None else '-', '' if r == s else ' (script %s)' % s))
    return ' | '.join(out)


def t1(A, B):
    if not (A.get('domain') and B.get('domain')): return None
    s = A['script']
    return sum(1 for k in KEYS if A['rep'].get(k) == s[k] and B['rep'].get(k) == s[k]) / len(KEYS)


def snca(P, name):
    L = ['SNCA, DECIDABLE LAYER (Core Part 6.2) -- %s' % name,
         '  FORM (L-549): %s | form checks %d of %d PASS (T2 basis %.2f)' % (P['form'], P['pass'], P['checks'], P['t2']),
         '  DOMAIN QUOTED: %s' % (P['domain'] or 'NONE'),
         '  DOMAIN SHA-256: %s' % (P['hash'] or 'NOT AVAILABLE'),
         '  VALUES (reported, script where different): %s' % value_line(P),
         '  READING FOUND: %s | L-418 JARGON SCAN OF THE READING: %s' % ('YES' if P['reading'] else 'NO', P['jargon'])]
    if P.get('echo'):
        L.append('  SYNTHESIS ECHO (script): ECHO ANCHOR P%d | SAS %.4f' % (P['echo'], P['sas']))
    L.append('  [NAVIGATOR]: T1.5, T3, the findings by jurisdiction, the verdict')
    return '\n'.join(L)


def srcas(A, B, an, bn, verdicts=None):
    L = ['SR-CAS, DECIDABLE LAYER (Core Part 6.1) -- %s with %s' % (an, bn),
         '  PRE-SR-CAS VERBATIM VERIFICATION: A %s | B %s' % (A['hash'] or 'NONE', B['hash'] or 'NONE')]
    if not (A['hash'] and B['hash'] and A['hash'] == B['hash']):
        L.append('  MATCH: NO | VERDICT: HALT -- VERBATIM MISMATCH%s' % (' (a navigation that quotes no domain counts as a mismatch)' if not (A['hash'] and B['hash']) else ''))
        return '\n'.join(L), None
    L.append('  MATCH: YES | VERDICT: PROCEED')
    L.append('  M270: script n = (%d, %d, %d), SUBSTRATE SHA-256 %s; A %s; B %s' % (
        A['script']['n1'], A['script']['n2'], A['script']['n3'], CR.substrate_sha256(A['nav']['content']),
        'MATCH' if all(A['rep'].get(k) == A['script'][k] for k in ('n1', 'n2', 'n3')) else 'DIVERGES',
        'MATCH' if all(B['rep'].get(k) == B['script'][k] for k in ('n1', 'n2', 'n3')) else 'DIVERGES'))
    T1 = t1(A, B); T2 = (A['t2'] + B['t2']) / 2
    ba, bb = (A['text'], B['text']) if all('STRUCTURAL RELATIONS EXPLICIT' in x['text'] for x in (A, B)) else (None, None)
    r = MM.m225(A['reading'] or '', B['reading'] or '', CR, ba, bb, verdicts, True) if (A['reading'] and B['reading']) else None
    t15l = r['T1.5-L'] if r else None; t15 = r['T1.5'] if r else None
    T25 = (A['sas'] + B['sas']) / 2 if (A.get('sas') is not None and B.get('sas') is not None) else None
    L.append('  T1 %.2f | T2 %.2f (form checks: A %.2f, B %.2f) | T1.5-L %s | T1.5 %s%s | T2.5 %s' % (
        T1, T2, A['t2'], B['t2'], t15l, (('%s (T1.5-S %s)' % (t15, r['T1.5-S'])) if r and r['T1.5-S'] is not None else t15) if t15 is not None else 'PENDING [NAVIGATOR verdicts]',
        ' QUALIFIED' if r and r.get('qualified') else '', '%.2f' % T25 if T25 is not None else 'NOT COMPUTED'))
    L.append('  [NAVIGATOR]: the per-relation verdicts (T1.5-S), T3, the interpretive synthesis, the verdict')
    return '\n'.join(L), dict(T1=T1, T2=T2, T15L=t15l, T15=t15, T25=T25)


def run(own, received, verdicts=None):
    P = [(n, profile(n)) for n in ([own] if own and own != 'NONE' else []) + received]
    out = ['AUTOMATIC REVIEW (Core Part 6.1, 6.2; tools/srcas_run.py) -- %d outputs' % len(P)]
    for n, p in P[1 if own and own != 'NONE' else 0:]:
        out.append(snca(p, n))
    res = {}
    for (an, a), (bn, b) in itertools.combinations(P, 2):
        if not (a['domain'] or b['domain']):
            out.append('SR-CAS -- %s with %s: NOT PAIRED -- neither quotes a domain, so neither is a navigation (Part 9.5.4); each has its SNCA' % (an, bn))
            res[(an, bn)] = None; continue
        txt, v = srcas(a, b, an, bn, verdicts); out.append(txt); res[(an, bn)] = v
    return '\n'.join(out), res


def selftest():
    import tempfile
    ok = True
    d = tempfile.mkdtemp()
    a = os.path.join(d, 'a.txt'); b = os.path.join(d, 'b.txt'); c = os.path.join(d, 'c.txt')
    open(a, 'w').write('DOMAIN (verbatim): What is a Human Being?\nCounts: n1 = 2 | n2 = 9 | n3 = 3\nANCHOR: P1\nYang +5: P6\nYin +18: P19\n4D +8: P9\nAntipode +12: P13\n')
    open(b, 'w').write('DOMAIN (verbatim): What is a human being?\nCounts: n1 = 2 | n2 = 9 | n3 = 4\nANCHOR: P1\nYang: P6\nYin: P19\n4D: P9\nAntipode: P13\n')
    open(c, 'w').write('A human being is a living organism.\n')
    txt, res = run('NONE', [a, b, c])
    cases = [('two copies of one domain proceed (L-348 case-folding)', 'VERDICT: PROCEED' in txt),
             ('T1 counts the values both get right: 7 of 8', abs(res[(a, b)]['T1'] - 7 / 8) < 1e-9),
             ('an output quoting no domain halts', res[(a, c)] is None and 'HALT' in txt),
             ('free prose is identified as UNFORMATTED', 'FORM (L-549): UNFORMATTED' in txt),
             ('two outputs that quote no domain are not paired', 'NOT PAIRED' in run('NONE', [c, c])[0]),
             ('the script coordinate of the domain is P1 with arms P6, P19, P9, P13', script_values('What is a Human Being?')[0] == dict(n1=2, n2=9, n3=3, anchor=1, yang=6, yin=19, **{'4d': 9}, antipode=13))]
    for name, good in cases:
        print('  %-62s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('SR-CAS RUN SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    v = None
    if '--verdicts' in a:
        i = a.index('--verdicts'); v = dict(zip(MM.RELATION_ORDER, [x.strip().upper() for x in a[i + 1].split(',')])); a = a[:i] + a[i + 2:]
    print(run(a[0], a[1:], v)[0])
