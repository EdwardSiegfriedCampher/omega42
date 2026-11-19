#!/usr/bin/env python3
"""history.py -- How Omega42 was built: the history page for readers (Companion Part 120; Core Part 12, item 34).

The bodies of the Core Specification and the Companion Document state only current facts (Builder Rule 2). The history
they do not carry is held by the release record and the sealed instance records; this tool renders it as one page for
anyone who wants it: each closure of the release record, in order, with its date, the Originator's words where the
record gives them, what was done, and the sealed record that holds it in full.

    python3 tools/history.py            # the page (records/history/HISTORY.md; CI diff)
    python3 tools/history.py --selftest
Standard library only. It reads; it never edits a document.
"""
import os, re, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REC = os.path.join(REPO, 'records', 'release_record_Rev450.txt')
LINE = re.compile(r'^  (?P<title>.+?) \((?P<when>[^()]*?\d{4})(?:, (?P<who>[^:]+?): (?P<words>.+?))?\): DONE -- (?P<done>.+?)(?: Record: (?P<rec>records/[\w/.-]+)\.)?$')

def entries(text):
    out = []
    for l in text.split('\n'):
        if not l.startswith('  ') or ': DONE -- ' not in l: continue
        left, done = l[2:].split(': DONE -- ', 1)
        rec = None
        m = re.search(r' Record: (records/[\w/.-]+?)\.?$', done)
        if m: rec, done = m.group(1), done[:m.start()]
        title, inside = left, ''
        if left.endswith(')'):
            depth = 0
            for i in range(len(left) - 1, -1, -1):
                depth += {')': 1, '(': -1}.get(left[i], 0)
                if depth == 0: title, inside = left[:i].rstrip(), left[i + 1:-1]; break
        when, who, words = inside, None, None
        d = re.search(r'\d{1,2}(?:-\d{1,2})? (?:September|October|November) 2026', inside)
        if d and ': ' in inside:
            meta, words = inside.split(': ', 1); when, who = d.group(0), re.sub(r',?\s*' + re.escape(d.group(0)) + r',?\s*', ' ', meta).strip(' ,') or None
        elif d:
            rest = inside.replace(d.group(0), '').strip(' ,'); when, words = d.group(0), (rest or None)
        out.append({'title': title, 'when': when or 'undated', 'who': who, 'words': words, 'done': done, 'rec': rec})
    return out

def page(text):
    E = entries(text)
    L = ['# How Omega42 was built', '',
         'The Core Specification and the Companion Document state the protocol as it is. This page holds how it came to be: '
         'each step closed in the release record, in order, with the Originator\'s words where the record gives them and the sealed record that holds the step in full. '
         'It is generated from records/release_record_Rev450.txt by tools/history.py and is not part of the protocol.', '',
         '%d steps.' % len(E), '']
    for k, e in enumerate(E, 1):
        L.append('## %d. %s' % (k, e['title']))
        L.append('')
        L.append('*%s*' % e['when'] + (' — %s: %s' % (e['who'], e['words']) if e['who'] and e['words'] else ' — %s' % e['words'] if e['words'] else ''))
        L.append('')
        L.append(e['done'])
        if e['rec']: L.append(''); L.append('Record: `%s`' % e['rec'])
        L.append('')
    return '\n'.join(L).rstrip() + '\n'

def selftest():
    t = ('  A step (30 October 2026, Originator: "Do it."): DONE -- it was done. Record: records/instances/seq_0001.txt.\n'
         '  Another step (29 October 2026): DONE -- also done.\nnot a step\n')
    E = entries(t)
    cases = [('two closures read, a non-closure skipped', len(E) == 2),
             ('the Originator\'s words and the record are kept', E[0]['words'] == '"Do it."' and E[0]['who'] == 'Originator' and E[0]['rec'] == 'records/instances/seq_0001.txt'),
             ('a closure without words or record is read', E[1]['words'] is None and E[1]['done'] == 'also done.'),
             ('the page numbers the steps in order', '## 1. A step' in page(t) and '## 2. Another step' in page(t))]
    for n, ok in cases: print('%-60s %s' % (n, 'PASS' if ok else 'FAIL'))
    print('%d of %d' % (sum(ok for _, ok in cases), len(cases)))
    return all(ok for _, ok in cases)

if __name__ == '__main__':
    if sys.argv[1:] == ['--selftest']: sys.exit(0 if selftest() else 1)
    sys.stdout.write(page(open(REC, encoding='utf-8').read()))
