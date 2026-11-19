#!/usr/bin/env python3
"""fieldkit.py -- M321 Field Kit (SPECULATIVE, ADOPTED 23 October 2026; Companion Part 90), an instrument for real-world situations,
cognitive and physical, built only from what Omega42 computes exactly.

Four uses, each deterministic, each ending at the Aperture:
    python3 tools/fieldkit.py decide "SITUATION" [--expect "WHAT I EXPECT"] [--frame cf]
        a situation struck; its arms as four working prompts; its classification (level, voice, tone, half, phase);
        under F0-CF its M320 elements; the Striker's expectation sealed by SHA-256 for the Return Log (M311);
        a Consequence Alert line when the situation touches health, safety, law, money or livelihood (F-11)
    python3 tools/fieldkit.py feel "SITUATION" "FELT STATE IN YOUR OWN WORDS" [--profile "valence=-1, activation=2, ..."] [--category C3]
        both struck in their own words -- no lexicon assigns a feeling a place -- and their relations, each with its base rate;
        your own profile (valence, activation, orientation, clarity, relation, each -2 to +2) and descriptive category (C0 to C5)
        printed and sealed beside them, never fed into the arithmetic (APE-159)
    python3 tools/fieldkit.py detect "x1, x2, x3, ..." [--source "QUANTITY, UNIT, PROCEDURE, RULE TO INTEGERS"]
        a measured integer sequence tested for the law itself, x(n+2) = x(n+1) + x(n) mod 9, against shuffles of the same
        values (frozen seed); its Margin, permutation p and band (M319's measures)
    python3 tools/fieldkit.py rhythm HH:MM
        the 24-hour day as a planning wheel: the hour's arms at +5, +18, +8 and +12 hours -- a scaffold, not a correspondence
        (the 24-hour day reads PROXIMITY 50 against its look-alikes, Panel 2)
    python3 tools/fieldkit.py --selftest

What it never does: score consciousness or an emotion, take physiological or wearable data into the arithmetic, diagnose,
predict an outcome, or tell the Striker what to do (L-441, L-515, M281). Its numbers are the arithmetic's; its prompts are
questions; the synthesis and the decision are the Striker's. Standard library and the tools beside this file.
"""
import hashlib, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, 'scripts')]
import canonical_reference as cr
import consciousness as cs
import manifestation as M
from resonance import margin, p_perm, margin_band

NAMES = cr.POSITION_NAMES
ARMS = (('Yang', 'yang_i', 'DEPENDENCY', 'What does this rest on -- an assumption, a resource, a past condition -- read through %s?'),
        ('Yin', 'yin_i', 'SUPPRESSION', 'What is being left out of view -- an alternative, a risk, an uncomfortable fact -- read through %s?'),
        ('4D', 'fourd_i', 'TRAJECTORY', 'If this goes ahead exactly as framed, where does it lead -- read through %s?'),
        ('Antipode', 'antipode_i', 'COMPLETION', 'What missing perspective or condition would make it whole -- read through %s?'))
ALERT = re.compile(r"\b(health|illness|ill|sick|symptom\w*|diagnos\w*|medic\w*|medication|pain|surgery|pregnan\w*|suicid\w*|self-harm|"
                   r"safety|danger\w*|law|legal|lawsuit|court|contract|custody|divorce|money|debt|loan|invest\w*|mortgage|savings|"
                   r"job|career|livelihood|fired|resign\w*)\b", re.I)
M320_OF = {'STILL POINT': ('WHOLE', 'GROUND', 'RETURN'), 'CORE': ('GROUND', 'RETURN'),
           'UNIT': ('DIFFERENTIATION', 'TRANSFORMATION', 'PERSPECTIVE', 'POLARITY', 'RETURN')}


def N(s): return (s[0] ** 2 + s[0] * s[1] - s[1] ** 2) % 9


def classify(s):
    """LEVEL, VOICE, TONE, HALF, PHASE at mod 9 (Companion 89.4)."""
    stratum, half, loop = M.classify(s)
    level = 2 if s == (0, 0) else (1 if stratum == 'CORE' else 0)
    shared, own = cs.perspective_address(s)
    phase = own.split(',')[0]
    voice = loop if stratum == 'UNIT' else ('the eight-step loop' if stratum == 'CORE' else 'none (still)')
    tone = N(s) if stratum == 'UNIT' else 0
    return dict(stratum=stratum, level=level, voice=voice, tone=tone, half=half, phase=phase)


def decide(situation, expect=None, frame=None):
    r = cr.navigate(situation); s = cs.state(situation); c = classify(s)
    L = ['======= M321 FIELD KIT -- DECIDE (SPECULATIVE, ADOPTED 23 October 2026) =======',
         'SITUATION VERBATIM: %s' % ' '.join(situation.split()),
         'META-FRAME: %s (L-515)' % ('F0-CF, consciousness-first' if frame == 'cf' else 'F0, default'),
         'COORDINATE: P%d %s | n = (%d, %d, %d) | state %s [EXACT]' % (r['anchor'], NAMES[r['anchor'] % 24], r['n1'], r['n2'], r['n3'], s),
         'CLASSIFICATION: level %d | voice %s | tone %d | half %s | %s [EXACT; Companion 89.4]' % (c['level'], c['voice'], c['tone'], c['half'], c['phase']),
         'FOUR WORKING PROMPTS (questions only; the answers are yours):']
    for name, key, rel, q in ARMS:
        i = r[key]; L.append('  %-8s %-11s P%-2d %-12s %s' % (name, rel, i, NAMES[i % 24], q % NAMES[i % 24]))
    if frame == 'cf':
        L.append('M320 ELEMENTS this state stands in: %s; read under F0-CF as a perspective of the one consciousness (C64)' % ', '.join(M320_OF[c['stratum']]))
    if ALERT.search(situation):
        L.append('CONSEQUENCE ALERT (F-11): this touches a matter with real consequences; the professional who addresses it -- a clinician, '
                 'a lawyer, a financial adviser, a trusted person -- weighs it, not this instrument')
    if expect:
        h = hashlib.sha256(('%s\n%s' % (' '.join(situation.split()), ' '.join(expect.split()))).encode('utf-8')).hexdigest()
        L.append('EXPECTATION SEALED: SHA-256 %s -- record the outcome in the Return Log (M311) and compare' % h[:16])
    L += ['READING: the coordinate comes from your words, not from the situation; the prompts widen the view and settle nothing.',
          'APERTURE (1/7): what this means and what you do are yours (Core Part 7).', '======= END DECIDE =======']
    return '\n'.join(L)


DIMS = ('valence', 'activation', 'orientation', 'clarity', 'relation')
POLES = {'valence': ('unpleasant', 'pleasant'), 'activation': ('quiet', 'intense'), 'orientation': ('withdrawal', 'engagement'),
         'clarity': ('diffuse', 'distinct'), 'relation': ('separation', 'connection')}
CATS = {'C0': 'unspecified', 'C1': 'sensory or affective', 'C2': 'attentional', 'C3': 'reflective', 'C4': 'integrative', 'C5': 'non-separate or unitive'}


def profile_lines(profile=None, category=None):
    """The Striker's own report (APE-159): five dimensions from -2 to +2 and a descriptive category C0 to C5. Recorded and
    sealed beside the arithmetic, never fed into it; a report, not a measurement (R_C)."""
    L = []
    if profile:
        vals = dict((k.strip().lower(), int(v)) for k, v in (kv.split('=') for kv in profile.split(',')))
        bad = [k for k in vals if k not in DIMS or not -2 <= vals[k] <= 2]
        if bad: return ['PROFILE REFUSED: %s -- the dimensions are %s, each from -2 to +2' % (', '.join(bad), ', '.join(DIMS))]
        L.append('YOUR PROFILE (your report, never an input to the arithmetic): ' + ' | '.join(
            '%s %+d (%s <-> %s)' % (k, vals[k], *POLES[k]) for k in DIMS if k in vals))
    if category:
        L.append('YOUR CATEGORY (descriptive, chosen by you): %s %s -- not the arithmetic\'s level, which is computed' % (category, CATS.get(category, 'unknown')))
    if L:
        h = hashlib.sha256('\n'.join(L).encode('utf-8')).hexdigest()
        L.append('REPORT SEALED: SHA-256 %s -- for your own log over time (M311)' % h[:16])
    return L


def feel(situation, felt, profile=None, category=None):
    P = cs.partition_text(situation, felt).split('\n')
    cs_, cf_ = classify(cs.state(situation)), classify(cs.state(felt))
    L = ['======= M321 FIELD KIT -- FEEL (SPECULATIVE, ADOPTED 23 October 2026) =======',
         'The felt state is struck in your own words. No lexicon gives a feeling a place, and nothing measures the feeling (R_C).',
         'SITUATION: %s -> level %d, voice %s, tone %d, half %s' % (' '.join(situation.split()), cs_['level'], cs_['voice'], cs_['tone'], cs_['half']),
         'FELT STATE: %s -> level %d, voice %s, tone %d, half %s' % (' '.join(felt.split()), cf_['level'], cf_['voice'], cf_['tone'], cf_['half'])]
    L += [p for p in P[3:9]]
    L += profile_lines(profile, category)
    L += ['READING: a placement, not a finding (L-510); the same feeling in other words stands elsewhere (NRR-C18).',
          'APERTURE (1/7): whether the relation means anything to you is yours.', '======= END FEEL =======']
    return '\n'.join(L)


def law_share(x):
    t = [(x[i] + x[i + 1] - x[i + 2]) % 9 == 0 for i in range(len(x) - 2)]
    return sum(t) / len(t)


def detect(seq, shuffles=2000, seed=321, source=None):
    x = [int(v) for v in re.findall(r'-?\d+', seq)]
    if len(x) < 5: return 'M321 DETECT: give at least five values'
    s = law_share(x); rng = random.Random(seed + len(x)); nulls = []
    for _ in range(shuffles):
        y = x[:]; rng.shuffle(y); nulls.append(law_share(y))
    Mg, status = margin(s, nulls); p = p_perm(s, nulls); band = margin_band(Mg, status, p, len(nulls))
    res = [v % 9 for v in x]
    L = ['======= M321 FIELD KIT -- DETECT (SPECULATIVE, ADOPTED 23 October 2026) =======',
         'SOURCE AND MAPPING RULE (APE-159; Appendix S): %s' % (source or 'NOT STATED -- name the quantity, its unit, how it was measured and how it became integers before reading the band'),
         'SEQUENCE: %s' % ', '.join(map(str, x)), 'RESIDUES MOD 9: %s' % ', '.join(map(str, res)),
         'LAW x(n+2) = x(n+1) + x(n) mod 9: holds on %d of %d steps (%.3f) [EXACT]' % (round(s * (len(x) - 2)), len(x) - 2, s),
         'AGAINST %d SHUFFLES OF THE SAME VALUES: null mean %.3f | MARGIN %s | p %.4f | %s' % (
             shuffles, sum(nulls) / len(nulls), ('%.3f' % Mg) if Mg is not None else 'NONE', p, band)]
    if s == 1.0 and len(x) >= 26:
        L.append('PERIOD: the residues repeat with period %d' % next(k for k in range(1, 25) if all(res[i] == res[i + k] for i in range(len(res) - k))))
    L += ['READING: the band says how far the sequence follows the law beyond its own values shuffled; it does not say the cycle',
          'produces the system (L-480), and a sequence that follows the law has met the law, not the premise (L-490). A sequence that',
          'already obeys x(n+2) = x(n+1) + x(n) as integers passes mod 9 by that alone; the test tells most on noisy counts and residues.',
          '======= END DETECT =======']
    return '\n'.join(L)


def rhythm(hhmm):
    h = int(hhmm.split(':')[0]) % 24; mm = hhmm.split(':')[1] if ':' in hhmm else '00'
    L = ['======= M321 FIELD KIT -- RHYTHM (SPECULATIVE, ADOPTED 23 October 2026) =======',
         'HOUR %02d:%s stands at P%d %s on the 24-hour wheel' % (h, mm, h, NAMES[h])]
    for name, off, rel in (('Yang', 5, 'rests on'), ('Yin', 18, 'holds out of view'), ('4D', 8, 'heads toward'), ('Antipode', 12, 'completes in')):
        k = (h + off) % 24; L.append('  %-8s +%-2d h  %02d:%s  P%-2d %-12s what the %02d:%s commitment %s' % (name, off, k, mm, k, NAMES[k], h, mm, rel))
    L += ['READING: a planning scaffold; the 24-hour day is NONDISCRIMINATING against its look-alikes (PROXIMITY 50, Panel 2).',
          '======= END RHYTHM =======']
    return '\n'.join(L)


def selftest():
    ok = True
    def check(label, c):
        nonlocal ok; print('%-80s %s' % (label, 'PASS' if c else 'FAIL')); ok &= bool(c)
    d = decide('Should we spend six months rebuilding the legacy system from scratch?', 'We expect to ship in seven months.')
    check('decide: the legacy question stands at P4 Unity with Yang P9, Yin P22, 4D P12, Antipode P16', all(k in d for k in ('P4 Unity', 'P9 ', 'P22', 'P12', 'P16')))
    check('decide: an expectation is sealed by SHA-256', 'EXPECTATION SEALED' in d)
    check('decide: a job question raises the Consequence Alert (F-11)', 'CONSEQUENCE ALERT' in decide('I have to decide whether to leave this job'))
    check('decide: no directive, score or promise in its output (M281)', not re.search(r'\byou should\b|\bscore\b|\bwill succeed\b', d, re.I))
    check('decide under F0-CF names the M320 elements', 'M320 ELEMENTS' in decide('What is love?', frame='cf'))
    check('feel: the felt state is struck, not looked up', 'No lexicon' in feel('I have to decide whether to leave this job', 'I feel anxious about leaving.'))
    f = feel('I have to decide whether to leave this job', 'I feel anxious about leaving.', 'valence=-1, activation=2, clarity=-1', 'C3')
    check('feel: the profile is printed as your report, sealed, and the placement is unchanged by it',
          'YOUR PROFILE' in f and 'REPORT SEALED' in f and feel('I have to decide whether to leave this job', 'I feel anxious about leaving.').split('\n')[3] == f.split('\n')[3])
    check('feel: a value outside -2 to +2 is refused', 'PROFILE REFUSED' in feel('a', 'b', 'valence=5'))
    check('detect: the Fibonacci numbers meet the law on every step, DISCRIMINATING', 'holds on 9 of 9' in detect('1,1,2,3,5,8,13,21,34,55,89') and 'DISCRIMINATING' in detect('1,1,2,3,5,8,13,21,34,55,89'))
    check('detect: a Lucas sequence meets the same law', 'holds on 8 of 8' in detect('2,1,3,4,7,11,18,29,47,76'))
    check('detect: an unrelated series does not discriminate', 'DISCRIMINATING' not in detect('12,15,11,14,13,16,12,15,14,13,12,16').replace('NONDISCRIMINATING', ''))
    check('detect: a sequence given without its source and mapping rule says so', 'NOT STATED' in detect('1,1,2,3,5,8'))
    check('rhythm: 08:00 has its antipode at 20:00, P20 Reckoning', '20:00  P20 Reckoning' in rhythm('08:00'))
    print('M321 SELFTEST: %s' % ('PASS' if ok else 'FAIL')); return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == 'decide':
        exp = a[a.index('--expect') + 1] if '--expect' in a else None
        fr = a[a.index('--frame') + 1] if '--frame' in a else None
        print(decide(a[1], exp, fr))
    elif a[0] == 'feel':
        print(feel(a[1], a[2], a[a.index('--profile') + 1] if '--profile' in a else None, a[a.index('--category') + 1] if '--category' in a else None))
    elif a[0] == 'detect': print(detect(a[1], source=a[a.index('--source') + 1] if '--source' in a else None))
    elif a[0] == 'rhythm': print(rhythm(a[1]))
    else: print(__doc__)
