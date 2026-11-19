#!/usr/bin/env python3
"""timestamp_check.py -- chronology checks (CA-22).
The L-542 improvement of 19 November 2026.

Rules, for every submission under submissions/ (front matter) and every run and status change of the STP register:
  1. FORMAT     disclosed_utc and accepted_utc are present and read YYYY-MM-DDTHH:MM:SSZ (UTC, explicit Z).
  2. NOT FUTURE no time is later than the trusted clock plus the tolerance.
  3. ORDER      accepted_utc is not earlier than disclosed_utc (the event comes before its import).
The trusted clock is the clock of the machine that runs the check: in CI, the GitHub runner, never a time written by an AI
agent or a contributor. TOLERANCE is 300 seconds, for clock skew between the machine that wrote a record and the runner.
Event time and import time stay distinct: disclosed_utc is when the output was made public, accepted_utc when the record
took it in. An older time is never an error; a record is never rewritten to look current.
Legacy STP times that are not ISO (for example "2026-11-18 (first run)") are reported as legacy, not failed.

    python3 tools/timestamp_check.py              check the repository
    python3 tools/timestamp_check.py --selftest
Standard library only.
"""
import datetime as dt, glob, json, os, re, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOLERANCE = dt.timedelta(seconds=300)
KNOWN_ORDER = {'submissions/ape/APE-045.md', 'submissions/ape/APE-046.md', 'submissions/ape/APE-047.md'}   # COR-011, held for ESC
ISO_Z = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})Z$')


def parse_z(v):
    m = ISO_Z.match(v or '')
    if not m:
        return None
    try:
        return dt.datetime(*map(int, m.groups()), tzinfo=dt.timezone.utc)
    except ValueError:
        return None


def front(text):
    m = re.match(r'---\n(.*?)\n---', text, re.S)
    out = {}
    for line in (m.group(1).split('\n') if m else []):
        k, _, v = line.partition(':')
        out[k.strip()] = v.strip().strip('"')
    return out


def check_submission(name, fm, now):
    P = []
    d, a = fm.get('disclosed_utc'), fm.get('accepted_utc')
    td, ta = parse_z(d), parse_z(a)
    for k, v, t in (('disclosed_utc', d, td), ('accepted_utc', a, ta)):
        if v is None: P.append('%s: %s missing' % (name, k))
        elif t is None: P.append('%s: %s malformed: %r (want YYYY-MM-DDTHH:MM:SSZ)' % (name, k, v))
        elif t > now + TOLERANCE: P.append('%s: %s in the future: %s (clock %s)' % (name, k, v, now.strftime('%Y-%m-%dT%H:%M:%SZ')))
    if td and ta and ta < td and name not in KNOWN_ORDER:
        P.append('%s: accepted_utc %s earlier than disclosed_utc %s' % (name, a, d))
    return P


def check_stp(now):
    P, legacy = [], 0
    reg = json.load(open(os.path.join(R, 'records', 'stp', 'registry.json'), encoding='utf-8'))['entries']
    for e in reg.values():
        times = [r.get('time') for r in e.get('runs', [])] + [h.get('time') for h in e.get('status_history', [])] + [e.get('date')]
        for t in times:
            if not t: continue
            try:
                v = dt.datetime.fromisoformat(t.replace('Z', '+00:00'))
            except ValueError:
                legacy += 1; continue
            if v.tzinfo is None:
                legacy += 1; continue
            if v > now + TOLERANCE:
                P.append('%s: time in the future: %s' % (e['id'], t))
    return P, legacy


def check(now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    P, n = [], 0
    for f in sorted(glob.glob(os.path.join(R, 'submissions', '**', '*.md'), recursive=True)):
        if os.path.basename(f) == 'README.md': continue
        n += 1
        P += check_submission(os.path.relpath(f, R), front(open(f, encoding='utf-8').read()), now)
    sp, legacy = check_stp(now)
    print('  known, held for ESC (COR-011): %s' % ', '.join(sorted(os.path.basename(k)[:-3] for k in KNOWN_ORDER)))
    P += sp
    print('TIMESTAMPS (L-542, CA-22): %d submissions, STP register (%d legacy times) | clock %s, tolerance %ds | problems %d'
          % (n, legacy, now.strftime('%Y-%m-%dT%H:%M:%SZ'), TOLERANCE.seconds, len(P)))
    for p in P[:40]: print('  ' + p)
    print('RESULT:', 'PASS' if not P else 'FAIL')
    return not P


def selftest():
    now = dt.datetime(2026, 11, 19, 12, 0, tzinfo=dt.timezone.utc)
    ok_fm = {'disclosed_utc': '2026-11-19T11:00:00Z', 'accepted_utc': '2026-11-19T11:30:00Z'}
    cases = [('a well-formed past record passes', ok_fm, 0),
             ('a future accepted_utc fails', dict(ok_fm, accepted_utc='2026-11-19T15:00:00Z'), 1),
             ('a future disclosed_utc fails', dict(ok_fm, disclosed_utc='2026-11-20T00:00:00Z', accepted_utc='2026-11-20T00:00:00Z'), 2),
             ('a time within the tolerance passes', dict(ok_fm, accepted_utc='2026-11-19T12:04:00Z'), 0),
             ('reversed chronology fails', dict(ok_fm, accepted_utc='2026-11-19T10:00:00Z'), 1),
             ('a missing timestamp fails', {'disclosed_utc': '2026-11-19T11:00:00Z'}, 1),
             ('a prose date fails', dict(ok_fm, accepted_utc='7 November 2026T12:00:00Z'), 1),
             ('a time zone other than Z fails', dict(ok_fm, accepted_utc='2026-11-19T11:30:00+02:00'), 1),
             ('an impossible date fails', dict(ok_fm, accepted_utc='2026-02-30T11:30:00Z'), 1),
             ('an old record passes', {'disclosed_utc': '2024-01-01T00:00:00Z', 'accepted_utc': '2024-01-02T00:00:00Z'}, 0)]
    good = True
    for name, fm, want in cases:
        got = len(check_submission('x', fm, now)); ok = got == want; good &= ok
        print(('  ok   ' if ok else '  FAIL ') + name + ('' if ok else ' (%d problems, want %d)' % (got, want)))
    print('TIMESTAMP SELFTEST:', 'PASS' if good else 'FAIL')
    return good


if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    sys.exit(0 if check() else 1)
