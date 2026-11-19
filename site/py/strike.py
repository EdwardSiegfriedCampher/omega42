"""strike.py -- the free Strike app's computation (site/strike.html). Runs the unchanged reference script
canonical_reference.py, in the browser under Pyodide or locally under CPython, and returns the coordinate as JSON."""
import json
import canonical_reference as cr
try:
    import adaptor_rules as AR          # Core L-501: a text the canonical extraction cannot see is routed to its script's adaptor
except ImportError:
    AR = None

VOICES = {1: 'A', 8: 'A', 4: 'B', 5: 'B', 2: 'C', 7: 'C'}
ROLES = (('Yang', 5, 'what it rests on'), ('Yin', 18, 'what it holds out of view'), ('4D', 8, 'where it is heading'),
         ('Antipode', 12, 'what completes it'))


def loop_of(s):
    if s == (0, 0): return 'the still point'
    q = (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
    if q == 0: return 'the eight-step loop'
    v = VOICES[q]
    return 'the canonical loop (Voice C)' if v == 'C' else 'Voice %s, a loop of twenty-four' % v


def phase_of(s):
    """M312 (Core Part 3.38): the norm half of the state; the law T flips it, its square keeps it."""
    if s == (0, 0): return 'the still point'
    q = (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9
    if q == 0: return 'the core, the still axis'
    return 'the 1/7 half (norm %d)' % q if q in (1, 2, 4) else 'the 6/7 half (norm %d)' % q


def strike(text):
    x = cr.navigate(text)
    n, counted_by, words = (x['n1'], x['n2'], x['n3']), 'EN-CANON (the canonical extraction)', x['content']
    if AR is not None:
        sc = AR.script_of(text)
        if sc and sc != 'LATIN':
            if sc not in AR.SCRIPTS:
                return json.dumps(dict(domain=text, sha256=cr.domain_sha256(text), zero=True, script=sc,
                                       reason='held ZERO-COUNT: no adaptor exists yet for %s (it needs %s); no coordinate is given (Core L-501)'
                                       % (sc, AR.OPEN_SCRIPTS.get(sc, 'an adaptor for the script'))), ensure_ascii=False)
            aid = AR.SCRIPTS[sc]; n = AR.COUNTERS[aid](text); counted_by = aid + ' (a companion adaptor, Core L-501)'; words = text.split()
    a, r1, r2, r3, tfi = cr.determine_anchor(*n)
    s = (r1 % 9, r2 % 9)
    arms = [dict(arm=n, offset=o, position=(a + o) % 24, name=cr.POSITION_NAMES[(a + o) % 24], value=cr.ORBIT[(a + o) % 24], role=r)
            for n, o, r in ROLES]
    return json.dumps(dict(domain=text, sha256=cr.domain_sha256(text), words=words, counted_by=counted_by, n=list(n), r=[r1, r2, r3],
                           anchor=a, name=cr.POSITION_NAMES[a], value=cr.ORBIT[a], tfi=round(tfi, 2), arms=arms, state=list(s),
                           loop=loop_of(s), phase=phase_of(s), mirror=[(-s[0]) % 9, (-s[1]) % 9], exposed=bool(cr.is_exposed(text))), ensure_ascii=False)
