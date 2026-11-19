#!/usr/bin/env python3
"""account_check.py -- checks a Navigator's Account against Core L-509 (Companion Part 72).

A Navigator's Account presents the protocol in the Navigator's own words: exposition, not a navigation and not
promotion. This tool checks what can be checked by rule; whether the Account is fair is the reader's to judge.

    python3 tools/account_check.py ACCOUNT.md [...]    # check one or more Accounts
    python3 tools/account_check.py --register          # every Account in records/navigator_accounts/register.json:
                                                       # present, hash as registered, checks passing
    python3 tools/account_check.py --selftest

Checks: the QUESTION VERBATIM line (L-499) and the AI CAVEAT line (L-506) open it; a declared pressure (M207); the
Navigator's own view labelled SELF-ESTIMATED; the comparative studies' status stated (M267 among them; optional, Appendix S); what is new and what is not (L-508, Companion
Part 71); every comparison with another position carries its relation type (AGREES, DIFFERS, EXTENDS); every body
paragraph names a provision; no persuasion wording (Rule 11), no affirmative "claim" and no assertion about the
world (L-505), no directive to believe or conclude (Check 7); 400 to 1000 words of body; the fixed closing line and
the signature last. Standard library only.
"""
import hashlib, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.path.join(ROOT, 'records', 'navigator_accounts', 'register.json')
CAVEAT = 'AI CAVEAT (L-506): This output was produced by an AI system. It can contain errors, and its training shapes its wording and may shape its reading; recompute what can be recomputed and judge the rest.'
CLOSE = 'What this means, whether it matters and what to do with it are yours to judge.'
PERS = re.compile(r"\b(very|truly|deeply|deepest|remarkabl[ey]|powerful(?:ly)?|beautiful(?:ly)?|extraordinar(?:y|ily)|crucial(?:ly)?|absolutely|perfectly|brilliant|revolutionary|unprecedented|groundbreaking|breakthrough|transformative|fascinating|exciting|stunning|amazing|incredibl[ey]|obviously|interestingly|surprisingly|magnificent|dramatic(?:ally)?|game-chang\w*|must-read|unique(?:ly)?)\b", re.I)
CNEG = re.compile(r"\b(not|no|never|nor|without|none|nothing|neither|cannot|isn't|doesn't)\b", re.I)
WORLD = re.compile(r"\b(proves?|demonstrates?|establishes?|shows?) that (the universe|reality|the world|everything is)\b", re.I)
DIRECT = re.compile(r"\byou (should|must|need to|ought to) (believe|accept|conclude|trust|agree|adopt)\b", re.I)
PROV = re.compile(r"\b(L-\d{3}|M\d{3}|F-\d{2}|FC-\d{2}|Part \d|Step \d|Companion|MATH-GATE|S\d{2})\b")
NAMES = re.compile(r"\b(Tegmark|Wolfram|ruliad|Pythagoras|Plato|Spinoza|I Ching|tarot|Oulipo|Oblique Strategies)\b")


def check(text):
    R = []
    def add(ok, item): R.append((bool(ok), item))
    lines = [l for l in text.split('\n')]
    nonblank = [l for l in lines if l.strip()]
    add(nonblank and nonblank[0].startswith('QUESTION VERBATIM: '), 'QUESTION VERBATIM line first (L-499)')
    add(CAVEAT in text, 'AI CAVEAT line (L-506)')
    add(re.search(r'DECLARED PRESSURE \(M207\):', text), 'declared pressure (M207)')
    add('SELF-ESTIMATED' in text, "the Navigator's own view labelled SELF-ESTIMATED")
    add(re.search(r'M267|Appendix S|comparative (studies|study|register)', text, re.I) and re.search(r'not yet run|NOT RUN|\bRUN\b|was run|optional|waits?', text), 'the comparative studies\' status stated (Appendix S; L-491)')
    add(re.search(r'not new', text, re.I) and re.search(r'L-508|Part 71', text), 'what is new and what is not (L-508, Part 71)')
    head_end = next((i for i, l in enumerate(lines) if l.startswith('DECLARED PRESSURE')), 4)
    body = [l for l in lines[head_end + 1:] if l.strip() and not l.startswith(('NAVIGATOR:', 'ESC', CLOSE))]
    words = sum(len(re.findall(r"[A-Za-z0-9'-]+", l)) for l in body)
    add(400 <= words <= 1000, 'body length 400-1000 words (%d)' % words)
    unref = [l[:50] for l in body if not PROV.search(l)]
    add(not unref, 'every body paragraph names a provision' + (' -- not: %s' % unref if unref else ''))
    comp = [l[:50] for l in body if NAMES.search(l) and not re.search(r'\b(AGREES|DIFFERS|EXTENDS)\b', l)]
    add(not comp, 'every comparison carries its relation type' + (' -- not: %s' % comp if comp else ''))
    u = re.sub(r'"[^"]*"', ' ', '\n'.join(body))
    p = sorted({m.group(0).lower() for m in PERS.finditer(u)})
    add(not p, 'no persuasion wording (Rule 11)' + (' -- found: %s' % ', '.join(p) if p else ''))
    sents = re.split(r'(?<=[.!?])\s+', u)
    cl = [s[:60] for s in sents if re.search(r'\bclaim(s|ed|ing)?\b', s, re.I) and not CNEG.search(s)]
    wd = [s[:60] for s in sents if WORLD.search(s) and not CNEG.search(s)]
    add(not cl and not wd, 'no affirmative claim and no assertion about the world (L-505)' + (' -- %s' % (cl + wd) if cl or wd else ''))
    add(not DIRECT.search(u), 'no directive to believe or conclude (Check 7)')
    add(len(nonblank) >= 3 and nonblank[-3] == CLOSE and nonblank[-2].startswith('NAVIGATOR: ') and nonblank[-1] == 'ESC', 'closing line, then the signature, last')
    return R


def report(path, quiet=False):
    R = check(open(path, encoding='utf-8').read())
    if not quiet:
        print('======= NAVIGATOR\'S ACCOUNT CHECK (Core L-509): %s =======' % (os.path.relpath(path, ROOT) if os.path.abspath(path).startswith(ROOT) else path))
        for ok, item in R: print('  [%s] %s' % ('PASS' if ok else 'FAIL', item))
        print('  RESULT: %s' % ('PASS' if all(o for o, _ in R) else 'FAIL'))
    return all(o for o, _ in R)


def register():
    reg = json.load(open(REG, encoding='utf-8'))
    ok = True
    for e in reg['entries']:
        p = os.path.join(ROOT, e['path'])
        if not os.path.exists(p): print('MISSING %s' % e['path']); ok = False; continue
        h = hashlib.sha256(open(p, 'rb').read()).hexdigest()
        good = h == e['sha256']; ok &= good
        print('%s  %s  %s  %s  hash %s' % (e['id'], e['status'], e['navigator'], e['date'], 'OK' if good else 'DIFFERS (%s)' % h))
        ok &= report(p, quiet=True)
    listed = {e['path'] for e in reg['entries']}
    for f in sorted(os.listdir(os.path.dirname(REG))):
        if f.startswith('ACCOUNT-') and 'records/navigator_accounts/' + f not in listed: print('UNREGISTERED %s' % f); ok = False
    print('ACCOUNT REGISTER: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def selftest():
    good = os.path.join(ROOT, 'records', 'navigator_accounts', 'ACCOUNT-0001.md')
    t = open(good, encoding='utf-8').read()
    cases = [('the first Account passes', all(o for o, _ in check(t)), True),
             ('promotion fails', all(o for o, _ in check(t.replace('What is not new', 'What is revolutionary and not new'))), False),
             ('a claim about the world fails', all(o for o, _ in check(t.replace('That supposition is the frame', 'This proves that the universe is the cycle. That supposition is the frame'))), False),
             ('a directive fails', all(o for o, _ in check(t.replace('Weigh the rest yourself.', 'You should believe the reading.'))), False),
             ('a comparison without its relation type fails', all(o for o, _ in check(t.replace('(sources register S05 and S06: DIFFERS)', '(sources register S05 and S06)'))), False),
             ('a missing caveat fails', all(o for o, _ in check(t.replace(CAVEAT, ''))), False),
             ('an unlabelled own view fails', all(o for o, _ in check(t.replace('SELF-ESTIMATED, ', ''))), False)]
    n = 0
    for name, got, want in cases:
        ok = got == want; n += ok; print(('PASS ' if ok else 'FAIL ') + name)
    print('SELFTEST: %d/%d PASS' % (n, len(cases)))
    return n == len(cases)


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'): print(__doc__); sys.exit(0)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--register': sys.exit(0 if register() else 1)
    sys.exit(0 if all([report(p) for p in a]) else 1)
