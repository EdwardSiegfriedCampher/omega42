#!/usr/bin/env python3
"""ape_register.py -- the APE Commons register and its findings (Companion Part 67; APA 9.5.5; avenue P).

Every Applied Protocol Exploration a peer has contributed is a finding of avenue P (Companion Part 59) and is kept,
whatever became of it. records/ape/register.json holds each exploration by its Commons entry; each one from APE-045
onward also has its frozen file in submissions/ape/, and this tool reads the receiving Navigator's notes from that
file live, classified by the label each note opens with (Adopted, Corrected, Refined, Holding, Not taken, Already in
place, Form, Mapped, Reconciled, ...). A note records what the protocol did with the exploration; the exploration
itself stays as submitted.

Usage:
  python3 tools/ape_register.py              the findings (records/ape/findings.txt; CI diff)
  python3 tools/ape_register.py --check      every file registered, every registered file present, no number twice
  python3 tools/ape_register.py --signatures the chamber signatures: the corrections each architecture received, by kind (a display, Core M283)
  python3 tools/ape_register.py --selftest
Standard library only.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, 'records', 'ape', 'register.json')
DIR = os.path.join(ROOT, 'submissions', 'ape')
KINDS = [('ADOPTED', r'Adopted|Taken|Entered|Made operational'), ('CORRECTED', r'Corrected'),
         ('REFINED', r'Refined|Restated|Reconciled|Renamed|One update|One restatement|Kept as an arrow|Kept beside'),
         ('HOLDING', r'Holding|Quotations checked|Checked|References checked|Its citations check|The category \w+ stands|Held in the frame'),
         ('ALREADY IN PLACE', r'Already in place|Already present|A second version'), ('NOT TAKEN', r'Not taken'),
         ('MAPPED', r'Mapped|Rendering'), ('FORM', r'Form'), ('NOTED', r'Noted')]
FIRST = 45     # from APE-045 every exploration has its frozen file


def kind_of(note):
    for k, rx in KINDS:
        if re.match(r'(?:\*\*)?(?:%s)\b' % rx, note): return k
    return 'NOTED'


def front(text):
    m = re.match(r'---\n(.*?)\n---\n', text, re.S)
    return dict(re.findall(r'^(\w+):\s*"?(.*?)"?\s*$', m.group(1), re.M)) if m else {}


def notes_of(text):
    """The receiving Navigator's notes: the bullets after 'Notes of the receiving Navigator', up to the first rule."""
    i = text.find('Notes of the receiving Navigator')
    if i < 0: return []
    block = text[i:].split('\n---', 1)[0]
    out, cur = [], None
    for l in block.split('\n')[1:]:
        if l.startswith('- '):
            cur = l[2:].strip(); out.append(cur)
        elif l.strip() and out and not l.startswith('#'):
            out[-1] += ' ' + l.strip()
    return [(kind_of(n), n) for n in out]


def files():
    return {f[:-3]: os.path.join(DIR, f) for f in sorted(os.listdir(DIR)) if re.match(r'APE-\d{3}\.md$', f)} if os.path.isdir(DIR) else {}


def load():
    return json.load(open(REG, encoding='utf-8'))


def problems(reg=None, fs=None):
    reg = reg or load(); fs = files() if fs is None else fs
    ids = [i for e in reg['entries'] for i in e['ids']]
    gap = [i for g in reg.get('gaps', []) for i in g['ids']]
    P = ['APE number registered twice: %s' % i for i in sorted(set(ids)) if ids.count(i) > 1]
    P += ['frozen file without a Commons entry: %s' % f for f in fs if f not in ids]
    P += ['Commons entry %s (APE-%03d onward) without its frozen file' % (i, FIRST) for i in ids if int(i[4:]) >= FIRST and i not in fs]
    top = max(int(i[4:]) for i in ids + list(fs))
    P += ['APE-%03d neither registered nor reported as a gap' % n for n in range(1, top + 1) if 'APE-%03d' % n not in ids + gap]
    return P


def findings_text():
    reg = load(); fs = files()
    rows, tally = [], {k: 0 for k, _ in KINDS}
    for e in reg['entries']:
        f = fs.get(e['ids'][0]) if len(e['ids']) == 1 else None
        fm, ns = ({}, [])
        if f:
            t = open(f, encoding='utf-8').read(); fm = front(t); ns = notes_of(t)
            for k, _ in ns: tally[k] += 1
        rows.append((e, fm, ns))
    n_ids = sum(len(e['ids']) for e in reg['entries'])
    L = ['======= APE FINDINGS: THE COMMONS REGISTER (Companion Part 67; APA 9.5.5; avenue P) =======',
         'Every exploration a peer contributes is a finding of avenue P and is kept as submitted. A note records what the protocol did with it; the protocol changes only by the Originator\'s adoption (F-06).',
         'EXPLORATIONS: %d numbers in %d Commons entries; %d frozen files (APE-%03d onward) with %d notes; %d entries recorded in the Commons alone' % (
             n_ids, len(reg['entries']), len(fs), FIRST, sum(len(r[2]) for r in rows), sum(1 for r in rows if not r[1])),
         'NOTES BY KIND: ' + ' | '.join('%s %d' % (k, v) for k, v in tally.items()),
         'AUTHORS (where the entry names one): ' + ' | '.join('%s %d' % (a, n) for a, n in sorted(_authors(rows).items(), key=lambda x: (-x[1], x[0]))),
         'GAPS: ' + ('; '.join('%s: %s -- %s' % (', '.join(g['ids']), g['status'], g['note']) for g in reg.get('gaps', [])) or 'NONE'), '']
    L.append('I. WHAT THE PEERS CHANGED (each exploration with an ADOPTED or CORRECTED note; the note in full)')
    for e, fm, ns in rows:
        ch = [(k, n) for k, n in ns if k in ('ADOPTED', 'CORRECTED')]
        if ch:
            L.append('  %s  %s (%s, %s)' % (e['label'], e['title'], e['author'] or _author(fm), fm.get('disclosed_utc', '')[:10]))
            for k, n in ch: L.append('      %-10s %s' % (k, re.sub(r'^(?:\*\*)?\w[\w ]*?(?:\*\*)?(?: \([^)]*\))?:\s*', '', n)))
    L += ['', 'II. EVERY EXPLORATION (the Commons entry; for a frozen file, its notes by kind)']
    for e, fm, ns in rows:
        L.append('  %s  %s%s' % (e['label'], e['title'], (' (%s)' % (e['author'] or _author(fm))) if (e['author'] or fm) else ''))
        if e['summary']: L.append('      ' + e['summary'])
        if fm:
            c = {}
            for k, _ in ns: c[k] = c.get(k, 0) + 1
            L.append('      FILE: submissions/ape/%s.md | AREA: %s | NOTES: %s' % (e['ids'][0], fm.get('area', ''), ', '.join('%s %d' % kv for kv in c.items()) or 'none recorded (received before the notes form; the Commons entry names where it went)'))
    P = problems()
    L += ['', 'CHECK: ' + ('PASS -- every frozen file registered, every registered file present, every number registered or reported as a gap' if not P else 'FAIL -- ' + '; '.join(P)),
          '======= END APE FINDINGS =======']
    return '\n'.join(L)


def _author(fm):
    s = fm.get('submitted_by', '')
    return re.sub(r' for ESC$', '', s)


def _authors(rows):
    c = {}
    for e, fm, _ in rows:
        a = e['author'] or _author(fm)
        if not a: continue
        w = a.split()[0]
        a = 'unsigned peer' if a.startswith('an unsigned') else 'OpenAI (ChatGPT, GPT-6)' if w in ('ChatGPT', 'GPT-6') else re.split(r'[ ,;(]', a)[0] if w in ('Claude', 'Qwen', 'DeepSeek', 'Grok', 'Gemini') else a
        c[a] = c.get(a, 0) + len(e['ids'])
    return c


def selftest():
    ok = True
    cases = [('a note label is classified', kind_of('Adopted: the currency check') == 'ADOPTED' and kind_of('Not taken: x') == 'NOT TAKEN' and kind_of('Quotations checked and holding: x') == 'HOLDING'),
             ('notes are read from the notes block only', notes_of('x\nNotes of the receiving Navigator:\n\n- Adopted: a\n  b\n- Form: c\n\n---\n- Adopted: not a note') == [('ADOPTED', 'Adopted: a b'), ('FORM', 'Form: c')]),
             ('an unregistered file is found', problems({'entries': [{'ids': ['APE-001']}], 'gaps': []}, {'APE-002': ''}) != []),
             ('a missing number is found', any('APE-002' in p for p in problems({'entries': [{'ids': ['APE-001']}, {'ids': ['APE-003']}], 'gaps': []}, {}))),
             ('the register passes', problems() == [])]
    for n, g in cases:
        print('  %-48s %s' % (n, 'OK' if g else 'MISMATCH')); ok &= g
    print('APE REGISTER SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok



SIG_KINDS = [('date', r'\bdated?\b|navigator line'), ('arithmetic', r'arithmetic|path|order|value|count|mod \d|EXACT'), ('attribution', r'attribut|was the receiving Navigator|cited|source'),
             ('inventory or naming', r'inventory|domains of one build|named|title'), ('placement or scope', r'placing|by role|uniform|practice|label|typed|four directions|four arms'), ('other', r'.')]
def signatures_text():
    """the chamber signatures (Companion Part 116.4): the CORRECTED notes of each architecture's explorations, by kind; a display (Core M283)"""
    reg = load(); fs = files(); by = {}
    for e in reg['entries']:
        f = fs.get(e['ids'][0]) if len(e['ids']) == 1 else None
        if not f: continue
        t = open(f, encoding='utf-8').read(); who = re.sub(r' for ESC$', '', front(t).get('submitted_by', 'unknown'))
        for k, n in notes_of(t):
            if k != 'CORRECTED': continue
            kind = next(name for name, rx in SIG_KINDS if re.search(rx, n, re.I))
            by.setdefault(who, {}).setdefault(kind, 0); by[who][kind] += 1
    L = ['======= CHAMBER SIGNATURES: THE CORRECTIONS EACH ARCHITECTURE RECEIVED, BY KIND (Companion Part 116.4; a display, Core M283) =======',
         'Counted from the CORRECTED notes of the frozen files. A count describes the record; it grades no model, and a kind is assigned by the first matching keyword.']
    for who in sorted(by, key=lambda w: (-sum(by[w].values()), w)):
        L.append('%-44s %3d  %s' % (who, sum(by[who].values()), ' | '.join('%s %d' % (k, by[who][k]) for k, _ in SIG_KINDS if k in by[who])))
    return '\n'.join(L)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--selftest']: sys.exit(0 if selftest() else 1)
    if a == ['--check']:
        P = problems(); print('APE REGISTER: %s' % ('PASS' if not P else 'FAIL')); [print('  ' + p) for p in P]; sys.exit(0 if not P else 1)
    if a == ['--signatures']: print(signatures_text()); sys.exit(0)
    print(findings_text())
