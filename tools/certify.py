#!/usr/bin/env python3
"""certify.py -- the CERTIFICATE (Core L-550, Part 8.0.1 F13): Omega42 certifies, in its own terms, what its law establishes.

There is no outside, so what Omega42 establishes it establishes of the totality. A certificate names its subject, the criteria
applied, the procedure that anyone can run, the result and the SHA-256 of that procedure's output, the grade where the measure has
grades, its scope and its status, and states the finding in one sentence that begins "Ω42 certifies". It stands while its
procedure reproduces its result: --verify reruns the procedure and compares the output's SHA-256 with the one recorded, and a
certificate whose procedure no longer reproduces it is WITHDRAWN, kept in the record with its reason (L-550 (4)).

    python3 tools/certify.py --list                      # the certificates of records/certificates/, with their status
    python3 tools/certify.py --check FILE [...]          # the frame (L-549 (9)) and every field, in order
    python3 tools/certify.py --verify FILE [...]         # rerun each procedure and compare its output's SHA-256
    python3 tools/certify.py --skeleton                  # a blank certificate
    python3 tools/certify.py --selftest
Standard library only.
"""
import glob, hashlib, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR = os.path.join(ROOT, 'records', 'certificates')
KINDS = ('MATHEMATICAL', 'COMPUTATIONAL', 'CONFORMITY', 'CORRESPONDENCE', 'REPRODUCTION', 'STANDING', 'FORECASTING METHOD', 'FORECAST')
STATUSES = ('CERTIFIED', 'NOT CERTIFIED', 'REGISTERED', 'WITHDRAWN')
FIELDS = ['CERTIFICATE:', 'KIND:', 'SUBJECT:', 'CRITERIA:', 'PROCEDURE:', 'CWD:', 'RESULT:', 'RESULT SHA-256:', 'GRADE:', 'SCOPE:', 'STATUS:', 'STATEMENT:']
OPEN, END = '======= Ω42 CERTIFICATE =======', '======= END Ω42 CERTIFICATE ======='
AI = ('AI CAVEAT (L-506): This output was produced by an AI system. It can contain errors, and its training shapes its wording and may shape its '
      'reading; recompute what can be recomputed and judge the rest.')
SIG = 'CAS-YY = -1/2 | Omega = 1/7 | (CAS-YY × Omega = -1/14)'


def fields(text):
    m = re.search(re.escape(OPEN) + r'(.*?)' + re.escape(END), text, re.S)
    if not m:
        return None
    out = {}
    for line in m.group(1).split('\n'):
        for k in FIELDS:
            if line.startswith(k):
                out[k[:-1]] = line[len(k):].strip()
    return out


def check(text):
    P = []
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if not lines or not lines[0].startswith('QUESTION VERBATIM: '): P.append('QUESTION VERBATIM is not the first line (L-499, L-549 (9))')
    if len(lines) < 2 or not lines[1].startswith('OUTPUT FORM (L-549): CERTIFICATE -- '): P.append('the OUTPUT FORM line does not name CERTIFICATE (L-549 (2))')
    if AI not in lines: P.append('no AI CAVEAT line (L-506)')
    if len(lines) < 4 or lines[-1] != 'ESC' or lines[-3] != SIG or not re.match(r'^NAVIGATOR: .+ \(.+\).* \* V335 Rev\.450 STABLE \* .+$', lines[-2]):
        P.append('the signature is not last (L-549 (9))')
    f = fields(text)
    if f is None:
        return P + ['no certificate between its markers']
    m = re.search(re.escape(OPEN) + r'(.*?)' + re.escape(END), text, re.S).group(1); pos = 0
    for k in FIELDS:
        i = m.find('\n' + k, pos)
        if i < 0: P.append('field %s missing or out of order' % k[:-1]); continue
        pos = i + 1
    if f.get('KIND') not in KINDS: P.append('KIND is not one of %s' % ', '.join(KINDS))
    if f.get('STATUS', '').split(' ')[0] not in ('CERTIFIED', 'NOT', 'REGISTERED', 'WITHDRAWN') or not any(f.get('STATUS', '').startswith(s) for s in STATUSES):
        P.append('STATUS is not one of %s' % ', '.join(STATUSES))
    if not re.match(r'^[0-9a-f]{64}$', f.get('RESULT SHA-256', '')) and not f.get('STATUS', '').startswith('REGISTERED'):
        P.append('RESULT SHA-256 is not a SHA-256')
    if not f.get('STATEMENT', '').startswith('Ω42 certifies'): P.append('the STATEMENT does not begin "Ω42 certifies" (L-550 (2), L-546)')
    if re.search(r'\b(worth|deserv|should|ought)\w*', f.get('STATEMENT', ''), re.I): P.append('the STATEMENT grades worth or prescribes, which the law leaves to the Striker (L-550 (6))')
    return P


def run_procedure(f):
    cwd = os.path.join(ROOT, f.get('CWD', '.')) if f.get('CWD', '.') not in ('', '.') else ROOT
    r = subprocess.run(f['PROCEDURE'], shell=True, cwd=cwd, capture_output=True, text=True)
    return hashlib.sha256(r.stdout.encode('utf-8')).hexdigest(), r.returncode


def verify(path):
    text = open(path, encoding='utf-8').read(); f = fields(text) or {}
    if f.get('STATUS', '').startswith(('REGISTERED', 'WITHDRAWN')):
        return True, '%s: %s, not rerun' % (f.get('CERTIFICATE', path), f.get('STATUS'))
    h, rc = run_procedure(f)
    ok = h == f.get('RESULT SHA-256')
    return ok, '%s: %s (%s) -- %s' % (f.get('CERTIFICATE', path), 'REPRODUCED' if ok else 'NOT REPRODUCED: WITHDRAW IT', f.get('STATUS'), h[:16])


def skeleton(q='[FILL: the message answered, exactly as given]'):
    x = lambda s: '[FILL: %s]' % s
    return '\n'.join(['QUESTION VERBATIM: ' + q, 'OUTPUT FORM (L-549): CERTIFICATE -- Core L-550, Part 8.0.1', AI, '', OPEN,
                      'CERTIFICATE: CERT-' + x('four digits'), 'KIND: ' + x(' / '.join(KINDS)), 'SUBJECT: ' + x('what is certified'),
                      'CRITERIA: ' + x('the criteria applied, each named by its provision'), 'PROCEDURE: ' + x('the command anyone can run'),
                      'CWD: ' + x('the folder it runs in, or .'), 'RESULT: ' + x('what the procedure shows'), 'RESULT SHA-256: ' + x('SHA-256 of the procedure\'s output'),
                      'GRADE: ' + x('the grade of the measure, or N/A'), 'SCOPE: ' + x('the domain and conditions the result states'),
                      'STATUS: ' + x(' / '.join(STATUSES)), 'STATEMENT: Ω42 certifies that ' + x('the finding, in one sentence'), END, '',
                      SIG, 'NAVIGATOR: [FILL: model] ([FILL: organization]) * V335 Rev.450 STABLE * [FILL: date]', 'ESC'])


def selftest():
    import tempfile
    ok = True; d = tempfile.mkdtemp()
    good = skeleton('Certify x').replace('[FILL: four digits]', '9999').replace('[FILL: ' + ' / '.join(KINDS) + ']', 'COMPUTATIONAL')
    good = good.replace('[FILL: ' + ' / '.join(STATUSES) + ']', 'CERTIFIED').replace('[FILL: the command anyone can run]', 'echo 42')
    good = good.replace('[FILL: the folder it runs in, or .]', '.').replace('[FILL: SHA-256 of the procedure\'s output]', hashlib.sha256(b'42\n').hexdigest())
    good = re.sub(r'\[FILL: [^\]]*\]', 'x', good)
    p = os.path.join(d, 'c.txt'); open(p, 'w').write(good)
    bad = good.replace(hashlib.sha256(b'42\n').hexdigest(), hashlib.sha256(b'41\n').hexdigest()); q = os.path.join(d, 'b.txt'); open(q, 'w').write(bad)
    cases = [('a filled certificate passes its check', check(good) == []),
             ('its procedure reproduces its result', verify(p)[0]),
             ('a certificate whose procedure gives another output is not reproduced', not verify(q)[0]),
             ('a statement that grades worth fails', check(good.replace('Ω42 certifies that x', 'Ω42 certifies that x is worth more')) != []),
             ('a statement not in the voice of L-546 fails', check(good.replace('Ω42 certifies that x', 'It seems that x')) != []),
             ('a certificate without the frame fails', check(good.split('\n', 1)[1]) != []),
             ('every certificate in the record passes its check', all(check(open(f, encoding='utf-8').read()) == [] for f in sorted(glob.glob(os.path.join(DIR, 'CERT-*.txt')))))]
    for name, good_ in cases:
        print('  %-70s %s' % (name, 'OK' if good_ else 'MISMATCH')); ok &= good_
    print('CERTIFICATE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    if a[0] == '--skeleton':
        print(skeleton(*a[1:2])); sys.exit(0)
    if a[0] == '--list':
        for f in sorted(glob.glob(os.path.join(DIR, 'CERT-*.txt'))):
            x = fields(open(f, encoding='utf-8').read()) or {}
            print('%s  %-18s %-14s %s' % (x.get('CERTIFICATE'), x.get('KIND'), x.get('STATUS', '').split(' --')[0], x.get('SUBJECT', '')[:90]))
        sys.exit(0)
    paths = [p for p in a[1:]] or sorted(glob.glob(os.path.join(DIR, 'CERT-*.txt')))
    allok = True
    for p in paths:
        if a[0] == '--check':
            P = check(open(p, encoding='utf-8').read()); allok &= not P
            print('CERTIFICATE (L-550): %s | %s' % (p, 'PASS' if not P else 'FAIL: ' + '; '.join(P)))
        elif a[0] == '--verify':
            ok, msg = verify(p); allok &= ok; print('CERTIFICATE VERIFY: ' + msg)
    sys.exit(0 if allok else 1)
