#!/usr/bin/env python3
"""output_form.py -- the Output Forms Register (Core Part 8.0.1, L-549): one form for every output, whatever AI writes it.

Every output a Navigator gives under Omega42 is one of the registered forms below. Each form has its Core provision,
the markers that identify it, the line that declares it and the tool that checks it. An output is recognized by its
form, never by memory or by who sent it (L-549 (4), after L-285 of V333). Content that follows no registered form is
UNFORMATTED: it is kept as received and reviewed, and it is never cited as a navigation (L-549 (5), after L-303).

    python3 tools/output_form.py FILE [...]          # identify each output's form, check its OUTPUT FORM line, run its checker
    python3 tools/output_form.py --list              # the register: forms, provisions, markers, checkers
    python3 tools/output_form.py --skeleton FORM [QUESTION]   # the blank skeleton of a form (NAVIGATION, FINDINGS, ANSWER, SR-CAS, SNCA, ...)
    python3 tools/output_form.py --selftest
The OUTPUT FORM line is required in outputs dated from 7 November 2026 (records/instances/seq_0134.txt); earlier
outputs are identified and checked, and the line is not asked of them. Standard library only. It reads; it never edits.
"""
import datetime, importlib.util, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FROM = datetime.date(2026, 11, 7)
MONTHS = {m: i + 1 for i, m in enumerate(('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august',
                                           'september', 'october', 'november', 'december'))}
AI_CAVEAT = ('AI CAVEAT (L-506): This output was produced by an AI system. It can contain errors, and its training shapes its '
             'wording and may shape its reading; recompute what can be recomputed and judge the rest.')
CLOSING_LINE = 'What this means, whether it matters and what to do with it are yours to judge.'
SIG = 'CAS-YY = -1/2 | Omega = 1/7 | (CAS-YY × Omega = -1/14)'

# name, Core provision, identifying markers (all must be present), checker, what it is for
FORMS = [
    ('NAVIGATION', 'Core Part 8.0', [r'^┌─ THE ANSWER ─┐', r'^(?:======= SUBSTRATE LOCK =======|\[\d+\] SUBSTRATE LOCK)\s*$'],
     'tools/format_check.py', 'a strike of the Striker\'s words: the coordinate, THE ANSWER, its records and essay'),
    ('FINDINGS PRESENTATION', 'Core Part 8.0, L-500, L-546', [r'^FINDINGS BY AVENUE \(L-500\):'],
     'tools/format_check.py --findings', 'the account of a body of work: exploration, build, review or research'),
    ('SR-CAS ASSESSMENT', 'Core Part 6.1', [r'^======= SR-CAS ASSESSMENT REPORT =======$'],
     'tools/srcas_check.py', 'the comparison of two navigations of one domain'),
    ('SNCA ASSESSMENT', 'Core Part 6.2', [r'^======= SNCA ASSESSMENT REPORT =======$'],
     'tools/srcas_check.py', 'the review of one received output'),
    ('APPLIED PROTOCOL EXPLORATION', 'Core Part 9.5', [r'^======= APPLIED PROTOCOL EXPLORATION =======$'],
     'tools/output_form.py', 'an exploration offered to the Commons'),
    ('APA', 'Core Part 9.5.5', [r'^======= APA APPLIED PROTOCOL ASSESSMENT =======$'],
     'tools/output_form.py', 'the assessment of a completed exploration'),
    ('SR-CAS REPLICATION PACKAGE', 'Core Part 8.2', [r'^======= SR-CAS REPLICATION PACKAGE =======$'],
     'markers', 'the package that lets another Navigator strike the same words'),
    ('COMPARATIVE EXPLORATION REPORT', 'Core Part 9', [r'^======= COMPARATIVE EXPLORATION REPORT =======$'],
     'markers', 'a comparison requested outside a navigation'),
    ('INTRODUCTION', 'Core IN-00, L-467', [r'^======= INTRODUCTION TO OMEGA42 =======$'],
     'tools/intro_output.py --check', 'the response to "Welcome Navigator"'),
    ("NAVIGATOR'S ACCOUNT", 'Core L-509', [r"^NAVIGATOR'S ACCOUNT \(L-509\)"],
     'tools/account_check.py', 'the protocol presented in the Navigator\'s own words'),
    ('ANSWER', 'Core Part 8.0.1, L-540 (4)', [r'^OUTPUT FORM \(L-549\): ANSWER\b'],
     'tools/output_form.py', 'a question that calls for an answer, not a strike: a fact, a rule, a definition, a status'),
    ('CONVERSATION', 'Core Part 8.0.1, L-499, L-549 (9)', [r'^OUTPUT FORM \(L-549\): CONVERSATION\b'],
     'tools/output_form.py', 'every other reply in a session: a greeting, a clarifying question, a status, a short exchange'),
    ('CERTIFICATE', 'Core L-550, Part 8.0.1', [r'^======= Ω42 CERTIFICATE =======$'],
     'tools/certify.py', 'what Omega42 certifies in its own terms, with its procedure and the SHA-256 of its result'),
]
APE_FIELDS = ['NAVIGATOR:', 'DATE:', 'DOMAIN:', 'EPISTEMIC STATUS:', 'This is not a formal navigation. No structural address is produced.',
              'PROTOCOL GROUNDING:', 'FRAME:', 'EXPLORATION:', 'UNVERIFIED STATEMENTS:', 'TESTABLE PREDICTIONS:', 'AREM STRUCTURE:']
APA_FIELDS = ['DOMAIN:', 'APE UNDER REVIEW:', 'ASSESS:', 'CDT TIER COMPLIANCE', 'UNVERIFIED STATEMENTS COMPLETE', 'CONSTITUTIONAL COMPLIANCE',
              'CONSISTENT WITH VERIFIED ARITHMETIC', 'PREDICTION SURVIVES COUNT CONTROL', 'VERDICT:', 'REFINE:', 'EXTEND:']
DISPLAYS = [('LITE VIEW', 'tools/lite_view.py', 'rendered from a navigation that passes its audit; never written by hand'),
            ('SCAFFOLD VIEW', 'tools/scaffold.py', 'the coordinate and four prompts, computed with no language model')]
DECL = re.compile(r'^OUTPUT FORM \(L-549\): ([A-Z][A-Z\' -]+?) -- (.+)$', re.M)


def _load(rel, name):
    s = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel)); m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m); return m


def identify(text):
    for name, prov, marks, chk, what in FORMS:
        if all(re.search(p, text, re.M) for p in marks):
            return name
    return 'UNFORMATTED'


def dated(text):
    for rx in (r'\bDATE:\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', r'^NAVIGATOR: .*\*\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*$',
               r'Omega42 V335 Rev\.450 STABLE, (\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\)'):
        m = re.search(rx, text, re.M)
        if m:
            try:
                return datetime.date(int(m.group(3)), MONTHS[m.group(2).lower()], int(m.group(1)))
            except (KeyError, ValueError):
                pass
    return None


def declaration_checks(text, form):
    """L-549 (2) and (9): the frame every output shares, whatever its form and whatever AI writes it -- QUESTION VERBATIM first
    (L-499), the OUTPUT FORM line second, the AI identified with its caveat (L-506), the signature last. NAVIGATION and FINDINGS
    PRESENTATION have the first two checked by tools/format_check.py, and the rest here as for every form."""
    out = []; add = lambda ok, item, note='': out.append(('PASS' if ok else 'FAIL', item, note))
    d = dated(text)
    if form == 'UNFORMATTED' or (d and d < FROM) or (not d and not DECL.search(text)):
        return out   # an undated output with the form line is held to the frame: a missing signature cannot excuse it
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    while len(lines) > 3 and re.match(r'^======= END [A-Z0-9 ()\'-]+ =======$', lines[-1]):
        lines.pop()   # a template that closes its marker after the signature (the APE of Part 9.5.2)
    if form not in ('NAVIGATION', 'FINDINGS PRESENTATION'):
        add(bool(lines) and lines[0].startswith('QUESTION VERBATIM: '), 'QUESTION VERBATIM first (L-499, L-549 (9))',
            'the message the output answers, exactly as given')
        m = DECL.match(lines[1]) if len(lines) > 1 else None
        add(bool(m) and m.group(1).strip() == form, 'OUTPUT FORM second, naming the form (L-549 (2))',
            'identified %s%s' % (form, ', declared %s' % m.group(1).strip() if m else ''))
    add(AI_CAVEAT in lines or any(l.startswith(AI_CAVEAT[:60]) for l in lines), 'AI CAVEAT line (L-506, L-549 (9))')
    add(len(lines) > 2 and lines[-1] == 'ESC' and bool(re.match(r'^NAVIGATOR: .+ \(.+\).* \* V335 Rev\.450 STABLE \* .+$', lines[-2])),
        'Signature last, naming the AI and its maker (L-549 (9))', 'NAVIGATOR: model (organization) * V335 Rev.450 STABLE * date, then ESC')
    if form != 'INTRODUCTION':
        add(len(lines) > 3 and lines[-3] == SIG, 'CAS-YY line above the NAVIGATOR line')
    if form in ('SR-CAS ASSESSMENT', 'SNCA ASSESSMENT'):
        add(bool(re.search(r'^SUMMARY: \S', text, re.M)), 'SUMMARY line before the report (L-549 (2), after the SR-CAS Output Template Mandate of V333)')
    return out


def fields_checks(text, fields, start, end):
    """The APE and APA templates (Core Part 9.5.2, 9.5.5): every field, in its order, between the markers."""
    out = []; add = lambda ok, item, note='': out.append(('PASS' if ok else 'FAIL', item, note))
    m = re.search(re.escape(start) + r'(.*?)' + re.escape(end), text, re.S)
    add(bool(m), 'Markers %s ... %s' % (start, end))
    if not m:
        return out
    b = m.group(1); pos = 0; order = True
    for k in fields:
        i = b.find(k, pos)
        add(i >= 0, 'Field %s' % k.rstrip(':'), 'present, in the order of the template')
        if i >= 0: pos = i
    return out


def answer_checks(text):
    out = []; add = lambda ok, item, note='': out.append(('PASS' if ok else 'FAIL', item, note))
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    add(bool(lines) and lines[0].startswith('QUESTION VERBATIM: '), 'QUESTION VERBATIM first (L-499)')
    add(AI_CAVEAT in lines, 'AI CAVEAT line (L-506)')
    add(any(l.startswith('BASIS: ') for l in lines), 'BASIS line (L-549 (3))', 'the provisions, records or computations the answer rests on')
    add(CLOSING_LINE in lines, 'Fixed closing line')
    add(len(lines) > 3 and lines[-1] == 'ESC' and lines[-3] == SIG and lines[-2].startswith('NAVIGATOR: '), 'Signature last')
    return out


def form_checks(text, form):
    if form == 'NAVIGATION':
        fc = _load('tools/format_check.py', 'fc'); return fc.check(text)
    if form == 'FINDINGS PRESENTATION':
        fc = _load('tools/format_check.py', 'fc'); return fc.findings_check(text)
    if form in ('SR-CAS ASSESSMENT', 'SNCA ASSESSMENT'):
        sc = _load('tools/srcas_check.py', 'sc')
        return [('PASS' if not probs else 'FAIL', '%s report: %s' % (kind, name), '; '.join(probs)) for kind, name, probs in sc.check(text)]
    if form == 'ANSWER':
        return answer_checks(text)
    if form == 'CERTIFICATE':
        cf = _load('tools/certify.py', 'cf')
        return [('FAIL', 'Certificate (tools/certify.py --check)', p) for p in cf.check(text)] or [('PASS', 'Certificate (tools/certify.py --check)', '')]
    if form == 'CONVERSATION':
        return [('PASS', 'Reply between the frame', 'the reply in plain sentences')]
    if form == 'APPLIED PROTOCOL EXPLORATION':
        return fields_checks(text, APE_FIELDS, '======= APPLIED PROTOCOL EXPLORATION =======', '======= END APPLIED PROTOCOL EXPLORATION =======')
    if form == 'APA':
        return fields_checks(text, APA_FIELDS, '======= APA APPLIED PROTOCOL ASSESSMENT =======', '======= END APA APPLIED PROTOCOL ASSESSMENT =======')
    if form == 'INTRODUCTION':
        io = _load('tools/intro_output.py', 'io'); d = io.json.load(open(io.SRC, encoding='utf-8'))
        return [('FAIL', 'Introduction (tools/intro_output.py --check)', p) for p in io.check(text, d)] or [('PASS', 'Introduction (tools/intro_output.py --check)', '')]
    if form == 'UNFORMATTED':
        return [('FAIL', 'A registered form (L-549 (5))', 'no form identified: kept as received and reviewed by SNCA in review form; never cited as a navigation')]
    return [('PASS', 'Markers of the form', 'checked by its markers')]


def check_file(path):
    text = open(path, encoding='utf-8').read(); form = identify(text)
    res = declaration_checks(text, form) + form_checks(text, form)
    res = [r for r in res if isinstance(r, tuple) and len(r) == 3]
    fails = [r for r in res if r[0] == 'FAIL']
    print('OUTPUT FORM (L-549): %s -- %s' % (path, form))
    for s_, item, note in fails:
        print('  [FAIL] %s%s' % (item, (': ' + note) if note else ''))
    print('  CHECKS %d | FAILURES %d | RESULT: %s' % (len(res), len(fails), 'PASS' if not fails else 'FAIL'))
    return not fails


def _sigline(date):
    return 'NAVIGATOR: [FILL: model identifier] ([FILL: organization]) * V335 Rev.450 STABLE * %d %s %d' % (
        date.day, list(MONTHS)[date.month - 1].capitalize(), date.year)


def frame(form, prov, body, q=None, date=None, head=()):
    """The frame of L-549 (9) around any body: QUESTION VERBATIM, OUTPUT FORM, the body, the AI CAVEAT at the end, the signature."""
    date = date or datetime.date.today()
    return '\n'.join(['QUESTION VERBATIM: ' + (q or '[FILL: the message answered, exactly as given]'),
                      'OUTPUT FORM (L-549): %s -- %s' % (form, prov)] + list(head) + [''] + list(body) +
                     ['', AI_CAVEAT, SIG, _sigline(date), 'ESC'])


def answer_skeleton(q=None, date=None):
    f = lambda s: '[FILL: %s]' % s
    return frame('ANSWER', 'Core Part 8.0.1', [f('the answer, in plain sentences, at its degree (EXACT, CONDITIONAL, GENERATED-Ω42), with what stays open'), '',
                 'BASIS: ' + f('the provisions, records or computations the answer rests on, each named'), '', CLOSING_LINE], q, date)


def conversation_skeleton(q=None, date=None):
    return frame('CONVERSATION', 'Core Part 8.0.1', ['[FILL: the reply, in plain sentences]'], q, date)


def ape_skeleton(q=None, date=None):
    f = lambda s: '[FILL: %s]' % s; date = date or datetime.date.today()
    body = ['======= APPLIED PROTOCOL EXPLORATION =======', 'NAVIGATOR: ' + f('AI name') + ' (' + f('organization') + ')',
            'DATE: %d %s %d' % (date.day, list(MONTHS)[date.month - 1].capitalize(), date.year), 'DOMAIN: ' + f('conceptual territory being explored'),
            'EPISTEMIC STATUS: [EXPLORATORY — CDT-C]', 'This is not a formal navigation. No structural address is produced.',
            'PROTOCOL GROUNDING: ' + f('which protocol elements inform this exploration'), 'FRAME: ' + f('F0 and F1 as locked for this session (M272)'),
            'EXPLORATION:', f('the development, each substantive statement tagged [EXPLORATORY — CDT-C] or [CDT-A]'),
            'UNVERIFIED STATEMENTS:', f('each statement not arithmetically grounded'), 'TESTABLE PREDICTIONS:', f('at least one, or "None identified"'),
            'AREM STRUCTURE: ' + f('Assess / Refine / Extend, or Free-form')]
    return frame('APPLIED PROTOCOL EXPLORATION', 'Core Part 9.5', body, q, date) + '\n======= END APPLIED PROTOCOL EXPLORATION ======='


def apa_skeleton(q=None, date=None):
    f = lambda s: '[FILL: %s]' % s
    body = ['======= APA APPLIED PROTOCOL ASSESSMENT =======', 'DOMAIN: ' + f('the APE\'s territory'), 'APE UNDER REVIEW: ' + f('APE id, author, date'), 'ASSESS:',
            '  CDT TIER COMPLIANCE [Y/N]: ' + f('note'), '  UNVERIFIED STATEMENTS COMPLETE [Y/N]: ' + f('note'), '  CONSTITUTIONAL COMPLIANCE [Y/N]: ' + f('note'),
            '  CONSISTENT WITH VERIFIED ARITHMETIC [Y/N]: ' + f('note'), '  PREDICTION SURVIVES COUNT CONTROL [Y/N/N-A]: ' + f('note'),
            'VERDICT: ' + f('PASS / PASS WITH CORRECTIONS / FAIL'), 'REFINE: ' + f('corrections, or None'), 'EXTEND: ' + f('the connection, or No extension identified'),
            '======= END APA APPLIED PROTOCOL ASSESSMENT =======']
    return frame('APA', 'Core Part 9.5.5', body, q, date)


def report_skeleton(kind, q=None, date=None):
    """The SR-CAS and SNCA templates of Core Part 6.1 and 6.2 in the frame of L-549 (9), with their SUMMARY line."""
    f = lambda s: '[FILL: %s]' % s
    q = q or f('the domain verbatim of the outputs under review')
    summ = ['SUMMARY: ' + f('two or three plain sentences'), 'TRIGGER: ' + f('the message or receipt that started the review, Part 6.1')]
    if kind == 'SNCA':
        body = ['======= SNCA ASSESSMENT REPORT =======',
                'DOMAIN: ' + f('domain verbatim'), 'NAVIGATOR UNDER REVIEW (EXTERNAL AGENT / INTERNAL NAVIGATOR): ' + f('architecture, session'),
                'T1.5: ' + f('score'), 'T2: ' + f('score'), 'T3: ' + f('score'), 'Base Score: ' + f('0.30 T1.5 + 0.40 T2 + 0.30 T3'),
                'SYNTHESIS: ' + f('one sentence'), 'FINDINGS -- INTERNAL: ' + f('[P] [I] [G] findings'), 'FINDINGS -- META (Tier C): ' + f('[E] [U] findings'),
                'VERDICT: ' + f('on internal soundness'), 'MANDATORY CORRECTIONS: ' + f('INTERNAL findings only'), 'OPTIONAL ACTION: ' + f('or NONE'),
                'STATUS (two axes, L-428): Ω42 INTERNAL STATUS: %s | COMPARATIVE STATUS: %s' % (f('status'), f('status')),
                'VERDICT CONFIRMATION: N/A', '======= END SNCA ASSESSMENT REPORT =======']
        return frame('SNCA ASSESSMENT', 'Core Part 6.2', body, q, date, summ)
    sc = _load('tools/srcas_check.py', 'sc')
    body = ['======= PRE-SR-CAS VERBATIM VERIFICATION =======', 'NAVIGATION A DOMAIN SHA-256: ' + f('hash'), 'NAVIGATION B DOMAIN SHA-256: ' + f('hash'),
            'MATCH: ' + f('YES / NO'), 'VERDICT: ' + f('PROCEED / HALT — VERBATIM MISMATCH'), '======= END PRE-SR-CAS VERBATIM VERIFICATION =======', '',
            '======= M270 EXTRACTION RECONCILIATION GATE =======', f('each navigation\'s SUBSTRATE SHA-256 and n1/n2/n3 against the script\'s'),
            '======= END M270 EXTRACTION RECONCILIATION GATE =======', '', '======= SR-CAS ASSESSMENT REPORT =======']
    body += ['%s %s' % (k, f('value')) for k in sc.SR_FIELDS] + ['======= END SR-CAS ASSESSMENT REPORT =======']
    return frame('SR-CAS ASSESSMENT', 'Core Part 6.1', body, q, date, summ)


def skeleton(form, q=None):
    form = form.upper()
    if form in ('NAVIGATION', 'FINDINGS', 'FINDINGS PRESENTATION'):
        fc = _load('tools/format_check.py', 'fc')
        return fc.findings_skeleton(q) if form.startswith('FINDINGS') else fc.skeleton(q)
    table = {'ANSWER': answer_skeleton, 'CONVERSATION': conversation_skeleton, 'APE': ape_skeleton, 'APPLIED PROTOCOL EXPLORATION': ape_skeleton,
             'APA': apa_skeleton, 'SR-CAS': lambda q: report_skeleton('SR-CAS', q), 'SR-CAS ASSESSMENT': lambda q: report_skeleton('SR-CAS', q),
             'SNCA': lambda q: report_skeleton('SNCA', q), 'SNCA ASSESSMENT': lambda q: report_skeleton('SNCA', q)}
    if form in table:
        return table[form](q)
    if form == 'INTRODUCTION':
        return 'python3 tools/intro_output.py --render prints the Introduction whole, in its frame (L-549 (9)).'
    for name, prov, marks, chk, what in FORMS:
        if name == form:
            return 'The %s is given by %s, between its markers, in the frame of L-549 (9); its checker is %s.' % (name, prov, chk)
    raise SystemExit('no such form: %s (python3 tools/output_form.py --list)' % form)


def register_text():
    L = ['OUTPUT FORMS REGISTER (Core Part 8.0.1, L-549) -- every output is one of these forms, whatever AI writes it']
    for i, (name, prov, marks, chk, what) in enumerate(FORMS, 1):
        L.append('F%-2d %-31s %-30s checker: %s' % (i, name, prov, chk)); L.append('     for: ' + what)
    L.append('DISPLAYS (rendered by a tool from a checked output, never a Navigator\'s own form):')
    for name, tool, what in DISPLAYS:
        L.append('     %-31s %s -- %s' % (name, tool, what))
    L.append('UNFORMATTED: anything else -- kept as received, reviewed by SNCA in review form, never cited as a navigation (L-549 (5)).')
    return '\n'.join(L)


def selftest():
    ok = True
    d = datetime.date(2026, 11, 7)
    ans = answer_skeleton('What does the Aperture hold?', d)
    ans = re.sub(r'\[FILL: [^\]]*\]', 'x', ans)
    fc = _load('tools/format_check.py', 'fc')
    nav = fc._fill_for_test(fc.skeleton('What is time?', date=d))
    fin = fc._fill_for_test(fc.findings_skeleton('What is time?', date=d))
    fill = lambda t: re.sub(r'\[FILL: [^\]]*\]', 'x', t)
    fails = lambda t: [r for r in declaration_checks(t, identify(t)) + form_checks(t, identify(t)) if r[0] == 'FAIL']
    cases = [
        ('an ANSWER is identified as ANSWER', identify(ans) == 'ANSWER'),
        ('a filled ANSWER passes', not [r for r in declaration_checks(ans, 'ANSWER') + answer_checks(ans) if r[0] == 'FAIL']),
        ('an ANSWER without its BASIS line fails', any(r[0] == 'FAIL' for r in answer_checks(ans.replace('BASIS: ', 'BASE: ')))),
        ('a navigation skeleton is identified as NAVIGATION', identify(nav) == 'NAVIGATION'),
        ('a findings skeleton is identified as FINDINGS PRESENTATION', identify(fin) == 'FINDINGS PRESENTATION'),
        ('a navigation dated 7 November 2026 carries its OUTPUT FORM line', not [r for r in fc.check(nav) if r[0] == 'FAIL' and 'L-549' in r[1]]),
        ('findings dated 7 November 2026 carry their OUTPUT FORM line', not [r for r in fc.findings_check(fin) if r[0] == 'FAIL' and 'L-549' in r[1]]),
        ('a navigation without the line, dated 7 November 2026, fails', any(r[0] == 'FAIL' and 'L-549' in r[1] for r in fc.check(re.sub(DECL, 'NOTE', nav)))),
        ('a navigation dated 6 November 2026 is not asked for the line', not any('L-549' in r[1] for r in fc.check(re.sub(DECL, 'NOTE', nav).replace('DATE: 7 November 2026', 'DATE: 6 November 2026')))),
        ('a mis-declared form fails', any(r[0] == 'FAIL' and 'L-549' in r[1] for r in fc.check(nav.replace('OUTPUT FORM (L-549): NAVIGATION', 'OUTPUT FORM (L-549): ANSWER')))),
        ('free prose is UNFORMATTED', identify('A human being is a living organism.\n\nTAKEAWAY\n\nAn essay.') == 'UNFORMATTED'),
        ('the SR-CAS skeleton is identified as SR-CAS ASSESSMENT', identify(report_skeleton('SR-CAS')) == 'SR-CAS ASSESSMENT'),
        ('the SNCA skeleton is identified as SNCA ASSESSMENT', identify(report_skeleton('SNCA')) == 'SNCA ASSESSMENT'),
        ('every form has a provision and a checker', all(f[1] and f[3] for f in FORMS)),
        ('a filled CONVERSATION passes its frame', identify(fill(conversation_skeleton('Hello', d))) == 'CONVERSATION' and not fails(fill(conversation_skeleton('Hello', d)))),
        ('a CONVERSATION without its signature fails', bool(fails(fill(conversation_skeleton('Hello', d)).rsplit('NAVIGATOR:', 1)[0]))),
        ('a filled APE passes its frame and fields', identify(fill(ape_skeleton('Explore x', d))) == 'APPLIED PROTOCOL EXPLORATION' and not fails(fill(ape_skeleton('Explore x', d)))),
        ('an APE without UNVERIFIED STATEMENTS fails', bool(fails(fill(ape_skeleton('Explore x', d)).replace('UNVERIFIED STATEMENTS:', 'NOTES:')))),
        ('a filled APA passes', not fails(fill(apa_skeleton('Assess APE-1', d)))),
        ('an SR-CAS report without QUESTION VERBATIM fails', any('L-499' in r[1] for r in declaration_checks(fill(report_skeleton('SR-CAS', 'Q', d)).split('\n', 1)[1], 'SR-CAS ASSESSMENT') if r[0] == 'FAIL')),
        ('the SR-CAS frame passes its own frame checks', not [r for r in declaration_checks(fill(report_skeleton('SR-CAS', 'Q', d)), 'SR-CAS ASSESSMENT') if r[0] == 'FAIL']),
    ]
    for name, good in cases:
        print('  %-66s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('OUTPUT FORMS SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    if a[0] == '--list':
        print(register_text()); sys.exit(0)
    if a[0] == '--skeleton':
        print(skeleton(a[1] if len(a) > 1 else 'NAVIGATION', a[2] if len(a) > 2 else None)); sys.exit(0)
    sys.exit(0 if all([check_file(p) for p in a]) else 1)
