#!/usr/bin/env python3
"""question_finder.py -- M340 Question Finder (Core Part 3.66, L-552): given an answer, the questions it may answer.

Deep Thought had the answer and not the question. Omega42 can go the other way: strike the answer, and find in the record
every question that meets it on the structure, each meeting set against its chance. A meeting is one of four:
  SAME STATE   the question stands on the answer's own state (r1, r2) mod 9 -- the same anyon;
  ANTIPARTICLE the question stands on the answer's negative -- the state it fuses with to the vacuum (the Register's "mirror");
  RESTS ON     the answer rests where the question stands (the answer's Yang arm is the question's anchor);
  RESTED ON    the question rests where the answer stands (the question's Yang arm is the answer's anchor).
It also names THE QUESTION WITHIN THE ANSWER: the answer's Yin arm, the place it holds out of view, the arm that braids
trivially with it (Core L-551 (3)) -- for 42 itself, T^42 = T^18 (Companion 33.13).

The questions are those of the record: every domain of the Congruence Register (records/congruence/domains.txt) and every
QUESTION VERBATIM of the sealed chain (records/instances/) and of the review records (records/srcas/), each once.

    python3 tools/question_finder.py "ANSWER"            # the meetings, their expected counts and the question within the answer
    python3 tools/question_finder.py --pool               # the questions searched
    python3 tools/question_finder.py --selftest
Each count is set against the pool's own null: the share of all 729 residue triples a random answer can take that meet these
same questions as often, so a pool crowded at one place is not taken for a meeting. A meeting is a congruence [CDT-C], counted only for what its chance allows (L-486, L-501); it never says that a question is
the answer's, which is the Striker's judgment (Part 7). Standard library only.
"""
import glob, math, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'scripts'))
import canonical_reference as cr
import congruence as cg

NAMES = cr.POSITION_NAMES


def pool():
    seen, out = set(), []
    def add(tag, text):
        key = re.sub(r'\s+', ' ', text.strip()).lower()
        if key and key not in seen: seen.add(key); out.append((tag, text.strip()))
    for tag, text in cg.load_register(): add(tag, text)
    for f in sorted(glob.glob(os.path.join(ROOT, 'records', 'instances', 'seq_*.txt'))) + sorted(glob.glob(os.path.join(ROOT, 'records', 'srcas', '*.txt'))):
        for line in open(f, encoding='utf-8'):
            if line.startswith('QUESTION VERBATIM: '):
                add(os.path.relpath(f, ROOT), line[len('QUESTION VERBATIM: '):]); break
    return out


def poisson_tail(k, lam):
    """P(X >= k) for X Poisson(lam)"""
    if k <= 0: return 1.0
    return max(0.0, 1.0 - sum(math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k)))


def _meet(me, sigs):
    neg = cg.neg
    return {'SAME STATE': [i for i, o in enumerate(sigs) if o['state'] == me['state']],
            'ANTIPARTICLE': [i for i, o in enumerate(sigs) if me['state'] != (0, 0) and o['state'] == neg(me['state'])],
            'RESTS ON': [i for i, o in enumerate(sigs) if me['yang'] == o['anchor']],
            'RESTED ON': [i for i, o in enumerate(sigs) if o['yang'] == me['anchor']]}


def find(answer, questions=None):
    """the meetings, and for each the exact chance under the pool's own null: the share of all 729 residue triples a random
    answer can take whose count of meetings with these same questions is at least the count found (L-501), so that a pool
    crowded at one place does not pass for a meeting"""
    questions = questions if questions is not None else pool()
    sigs = [cg.sig(q) for _, q in questions]
    me = cg.sig(answer); hit = _meet(me, sigs)
    import bashar_lens as bl
    rand = []
    for n1 in range(1, 10):
        for n2 in range(1, 10):
            for n3 in range(1, 10):
                a, r1, r2, r3, _ = cr.determine_anchor(n1, n2, n3)
                rand.append(dict(anchor=a, yang=(a + 5) % 24, state=bl.frequency(r1, r2)['state']))
    dist = {k: [] for k in hit}
    for o in rand:
        m = _meet(o, sigs)
        for k in m: dist[k].append(len(m[k]))
    p = {k: sum(1 for c in dist[k] if c >= len(hit[k])) / len(rand) for k in hit}
    expd = {k: sum(dist[k]) / len(rand) for k in hit}
    meets = {k: [questions[i] for i in hit[k]] for k in hit}
    yin = (me['anchor'] + 18) % 24 or 24
    return me, meets, expd, p, len(questions), yin


def report(answer):
    me, meets, exp, pv, n, yin = find(answer)
    N = lambda s: (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
    L = ['======= M340 QUESTION FINDER (Core Part 3.66, L-552) =======', 'ANSWER VERBATIM: ' + answer,
         'ANSWER STANDS AT: P%d %s | state %s, spin exp(2 pi i %d/9) | rests on P%d %s' % (me['anchor'], NAMES[me['anchor'] % 24], me['state'], N(me['state']), me['yang'] or 24, NAMES[me['yang'] % 24]),
         'THE QUESTION WITHIN THE ANSWER: P%d %s -- its Yin arm, the place it holds out of view, braiding trivially with it (L-551 (3))' % (yin, NAMES[yin % 24]),
         'QUESTIONS SEARCHED: %d (the Congruence Register and every QUESTION VERBATIM of records/instances/ and records/srcas/)' % n]
    above = []
    for k in ('SAME STATE', 'ANTIPARTICLE', 'RESTS ON', 'RESTED ON'):
        hits = meets[k]; p = pv[k]
        hot = p < 0.05 and len(hits) > 0
        if hot: above.append(k)
        L.append('%-12s %d found [RETRIEVED], %.2f expected for a random answer against these questions (share of the 729 random answers with as many: %.3f)%s' % (k, len(hits), exp[k], p, ' -- above chance' if hot else ' -- at chance'))
        for tag, q in hits[:12]:
            L.append('   %s | %s' % (tag, q[:150] + ('...' if len(q) > 150 else '')))
        if len(hits) > 12: L.append('   ... and %d more' % (len(hits) - 12))
    if above:
        L.append('CONCLUSION: under this corpus, these matching rules and the pool\'s own null, the answer meets the record above its null expectation at: %s.' % ', '.join(above))
    else:
        L.append('CONCLUSION: under this corpus, these matching rules and the pool\'s own null, the answer shows no above-chance association with the record; this is not evidence that none exists, only that this instrument, so set, has not found one.')
    L.append('SOURCES: every question listed is RETRIEVED from the record; the finder neither GENERATES a new question from the answer\'s coordinate nor offers an INTERPRETIVE question in words -- those are separate, labelled acts, and which question an answer answers is the Striker\'s (Part 7).')
    L.append('READING: each meeting is a congruence counted for what its chance allows (L-486, L-501).')
    L.append('======= END M340 QUESTION FINDER =======')
    return '\n'.join(L)


def selftest():
    ok = True
    qs = [('A', 'What is a Human Being?'), ('B', 'What is a person?'), ('C', 'Explore the golden ratio connection')]
    me, meets, exp, pv, n, yin = find('What is a Human Being?', qs)
    cases = [('a question meets itself on its own state', ('A', 'What is a Human Being?') in meets['SAME STATE']),
             ('the null is exact: every chance is a share of the 729 random answers', all(abs(pv[k] * 729 - round(pv[k] * 729)) < 1e-9 for k in pv)),
             ('the question within the answer is the Yin arm, P19 for an anchor at P1', yin == 19),
             ('the pool holds the Register and the chain, each question once', len(pool()) == len({re.sub(r"\s+", " ", q.strip()).lower() for _, q in pool()})),
             ('a tail probability of 0 found is 1', poisson_tail(0, 0.5) == 1.0)]
    for name, good in cases:
        print('  %-64s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('QUESTION FINDER SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--pool':
        for tag, q in pool(): print('%s | %s' % (tag, q[:140]))
        sys.exit(0)
    print(report(' '.join(a)))
