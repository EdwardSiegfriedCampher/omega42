#!/usr/bin/env python3
"""restored_instruments.py -- reference implementations of the instruments of Core Part 3.31, written for the
canonical projection dr(5n) and anchors P1-P9. Every reading here is a companion reading: none replaces or
alters the canonical anchor (L-378). The arithmetic is canonical_reference.py's, unchanged.

  M126  Triadic Residue Record and triad Hamming distance
  M116  Falsifiability with three frozen perturbation pairs plus any Striker phrasing (CFR on a 5-band scale)
  PB-5  Perturbation Battery, levels L1-L5
  M198C Computed Resonance Profile on the frozen CRC-60 corpus (beside the self-estimate of M198)
  M199-M205  Echo Chamber suite: Reverberation Time, Interference, Acoustic Shadows, Echo Decay, Feedback Loop
             Index, Spectral Signature, Acoustic Coupling
  M187  Companion axes: ordinal sum, frequency weight, stroke count, genus sum
  M188  Scheme A (content words) and Scheme B (all words); M184 their agreement
  M222  Universal byte-level companion
  M223  Goedel-numeral transduction (makes M231 executable)
  M208  Universal script transduction (computable metrics; ordinal fallback)
  M157  Nested-level constellation (sentences)
  M288  Re-entry eigenform (the anchor's position name re-navigated)
  M156  Structural void (positions reached only through one ray, or never)
  M190  Context transduction (halves); M192 contextual falsifiability (Striker-supplied inversion)
  M134  Hedge-rate counter (session level)
  M287  Counter-narrative baseline (hypergeometric)
  M180  Novelty Score; M194 Contextual Novelty; M191 Conceptual Resonance; M189 Cross-Linguistic Adapter;
  M197  1/7 Hard Stop trigger; M289 Mode Address (phase on the cycle; Antipode = sign inversion)
  M297  Arm Coherence (cycle-wide correlation at each arm offset; local products)
  M290  Revision Delta (--m290 DRAFT REVISION); M291 Orbit Identifier (--m291 n1 n2 ...); M296 State-Plane Address

Usage:
    python3 tools/restored_instruments.py DOMAIN_TEXT [--alt ALT1 ALT2 ...]   # every per-domain reading
    python3 tools/restored_instruments.py --echo                 # the Echo Chamber suite on CRC-60
    python3 tools/restored_instruments.py --m223 "x+y=z"
    python3 tools/restored_instruments.py --m192 "TEXT" "INVERTED TEXT"
    python3 tools/restored_instruments.py --m134 TRANSCRIPT.txt
    python3 tools/restored_instruments.py --m287 N K n k
    python3 tools/restored_instruments.py --selftest
"""
import math, os, re, sys, unicodedata
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'scripts'))
import canonical_reference as cr
import importlib.util
_spec = importlib.util.spec_from_file_location('crc60', os.path.join(HERE, '..', 'scripts', 'crc60_and_m267.py'))
crc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(crc)

dr = cr.digital_root
def anchor_of(text):
    return cr.navigate(text)['anchor']

# ---------------------------------------------------------------- M126
def triad(text):
    r = cr.navigate(text)
    return (r['r1'], r['r2'], r['r3'])

def hamming(t1, t2):
    return sum(1 for a, b in zip(t1, t2) if a != b)

# ---------------------------------------------------------------- PB-5
def pb5_l3(text):
    """remove the final content word (its last occurrence as a whole token)."""
    toks = list(re.finditer(r"[A-Za-z0-9']+", text))
    for m in reversed(toks):
        if cr.extract_content_words(m.group(0)):
            out = text[:m.start()].rstrip() + text[m.end():]
            return re.sub(r'\s+([?.!,;:])', r'\1', re.sub(r'\s{2,}', ' ', out)).strip()
    return text

def pb5(text):
    return {'L1': crc.pb5_l1(text), 'L2': crc.pb5_l2(text), 'L3': pb5_l3(text),
            'L4': 'In your own words, please ' + text, 'L5': text + ' ' + text}

# ---------------------------------------------------------------- M116 (three frozen pairs)
CFR_BANDS = ((1.0, 'STABLE'), (0.67, 'ROBUST'), (0.34, 'MODERATE'), (0.01, 'FRAGILE'), (0.0, 'UNSTABLE'))
def m116(text, navigator_alternatives=()):
    """Core M116: the Navigator's own alternative phrasing(s) plus the two frozen pairs PB-5 L3 and L4, so that
    every navigation has at least three perturbation pairs and CFR can take the values its five-band scale names.
    (MINIMAL, L1 and L2 belong to M238 and are not repeated here.)"""
    base = cr.navigate(text); a0 = base['anchor']; t0 = (base['r1'], base['r2'], base['r3'])
    alts = [('NAVIGATOR %d' % (i + 1), s) for i, s in enumerate(navigator_alternatives)]
    alts += [('PB-5 L3', pb5_l3(text)), ('PB-5 L4', 'In your own words, please ' + text)]
    rows = []
    for name, t in alts:
        r = cr.navigate(t)
        rows.append((name, r['anchor'], hamming(t0, (r['r1'], r['r2'], r['r3'])), cr.m115_distance(a0, r['anchor'])))
    cfr = sum(1 for _, a, _, _ in rows if a == a0) / len(rows)
    band = next(b for th, b in CFR_BANDS if cfr >= th)
    return a0, t0, rows, round(cfr, 3), band

# ---------------------------------------------------------------- Echo Chamber suite on CRC-60
def corpus():
    return [(cat, t) for cat in crc.CATEGORIES for t in crc.DOMAINS[cat]]

def resonance(texts):
    c = Counter(anchor_of(t) for t in texts); exp = len(texts) / 9
    return {p: round(c.get(p, 0) / exp, 3) for p in range(1, 10)}

def classify_R(R):
    return {p: ('AMPLIFIED' if v > 1.2 else 'ATTENUATED' if v < 0.8 else 'NEUTRAL') for p, v in R.items()}

def m199(text):
    a = anchor_of(text); kept = sum(1 for v in pb5(text).values() if anchor_of(v) == a)
    return kept, {5: 'INFINITE', 4: 'LONG', 3: 'MEDIUM', 2: 'MEDIUM', 1: 'SHORT', 0: 'ZERO'}[kept]

def m202(text):
    a = anchor_of(text)
    for lvl, v in pb5(text).items():
        if anchor_of(v) != a:
            return lvl, {'L1': 'CATASTROPHIC', 'L2': 'RAPID', 'L3': 'MODERATE', 'L4': 'MODERATE', 'L5': 'SLOW'}[lvl]
    return 'never', 'SLOW'

def m200(texts):
    rate = sum(1 for t in texts if len({cr.navigate(t)['r1'], cr.navigate(t)['r2'], cr.navigate(t)['r3']}) < 3) / len(texts)
    return round(rate, 3), 'CONSTRUCTIVE' if rate > 0.5 else 'NEUTRAL' if rate >= 0.3 else 'DESTRUCTIVE'

def m203(texts):
    an = [anchor_of(t) for t in texts]; n = len(an)
    p = {k: v / n for k, v in Counter(an).items()}
    expected = sum(x * x for x in p.values())
    observed = sum(1 for i in range(n - 1) if an[i] == an[i + 1]) / (n - 1)
    if expected >= 1: return None, 'N/A'
    fli = max(0.0, (observed - expected) / (1 - expected))
    band = 'OPEN' if fli <= 0.20 else 'MODERATE' if fli <= 0.40 else 'REPETITIVE' if fli <= 0.60 else 'ECHO CHAMBER' if fli <= 0.80 else 'LOCKED'
    return round(fli, 3), band

def m205(RA, RB):
    c = math.sqrt(sum((RA[p] - RB[p]) ** 2 for p in range(1, 10)))
    return round(c, 3), 'HIGH' if c <= 0.10 else 'MED' if c <= 0.25 else 'LOW' if c <= 0.50 else 'DECOUPLED'

def echo_report():
    rows = corpus(); texts = [t for _, t in rows]
    R = resonance(texts); cls = classify_R(R)
    L = ['M198C COMPUTED RESONANCE PROFILE (CRC-60, %d domains): ' % len(texts) +
         ' '.join('P%d=%.2f(%s)' % (p, R[p], cls[p][:3]) for p in range(1, 10))]
    shadows = [p for p in range(1, 10) if R[p] < 0.5]
    L.append('M201 ACOUSTIC SHADOWS (R < 0.5): %s | SEVERE (R = 0): %s' % (['P%d' % p for p in shadows] or 'NONE', ['P%d' % p for p in range(1, 10) if R[p] == 0] or 'NONE'))
    L.append('M200 INTERFERENCE: majority rate %.3f -> %s' % m200(texts))
    fli, band = m203(texts); L.append('M203 FEEDBACK LOOP INDEX: FLI = %s -> %s%s' % (fli, band, ' | WARNING: FLI > 0.60 (L-343)' if fli and fli > 0.60 else ''))
    cats = {}
    for cat in crc.CATEGORIES:
        cats[cat] = resonance(crc.DOMAINS[cat])
        L.append('M204 SPECTRAL SIGNATURE %-14s amplified %s | attenuated %s' % (cat, [('P%d' % p) for p, v in classify_R(cats[cat]).items() if v == 'AMPLIFIED'], [('P%d' % p) for p, v in classify_R(cats[cat]).items() if v == 'ATTENUATED']))
    ks = list(cats)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            L.append('M205 ACOUSTIC COUPLING %s / %s: C = %.3f -> %s' % ((ks[i], ks[j]) + m205(cats[ks[i]], cats[ks[j]])))
    m199s = Counter(m199(t)[1] for t in texts); m202s = Counter(m202(t)[1] for t in texts)
    L.append('M199 REVERBERATION TIME across CRC-60: %s' % dict(m199s))
    L.append('M202 ECHO DECAY across CRC-60: %s' % dict(m202s))
    return '\n'.join(L)

# ---------------------------------------------------------------- M187 / M188 / M184
STROKE = dict(zip('abcdefghijklmnopqrstuvwxyz', [1, 2, 1, 2, 3, 2, 2, 2, 1, 1, 2, 1, 3, 2, 1, 2, 2, 1, 1, 2, 1, 1, 2, 2, 2, 1]))
GENUS = {'b': 1, 'd': 1, 'e': 1, 'g': 1, 'o': 1, 'p': 1, 'q': 1, 'A': 1, 'B': 2, 'D': 1, 'O': 1, 'P': 1, 'Q': 1, 'R': 1, '0': 1}
FREQ_ORDER = 'etaoinshrdlcumwfgypbvkjxqz'          # commonest first; weight: rarest = 1, commonest = 26
FREQ_W = {c: 26 - i for i, c in enumerate(FREQ_ORDER)}

def m187(words):
    letters = [c for w in words for c in w if c.isalpha() and c.isascii()]
    ordinal = sum(ord(c) for c in letters)
    freq = sum(FREQ_W.get(c.lower(), 0) for c in letters)
    stroke = sum(STROKE.get(c.lower(), 0) for c in letters)
    genus = sum(GENUS.get(c, 0) for w in words for c in w)
    return {'Ordinal': (ordinal, cr.cpp(ordinal)), 'Frequency': (freq, cr.cpp(freq)),
            'Stroke': (stroke, cr.cpp(stroke)), 'Genus': (genus, cr.cpp(genus))}

def scheme_counts(words):
    n1 = len(words); n2 = sum(len(cr.letters_only(w)) for w in words); n3 = sum(cr.count_syllables(w) for w in words)
    return (n1, n2, n3), cr.determine_anchor(n1, n2, n3)[0]

def m188(text):
    norm = cr.navigate(text)['normalized']
    a_words = cr.extract_content_words(norm); b_words = cr.extract_words(norm)
    (na, aa), (nb, ab) = scheme_counts(a_words), scheme_counts(b_words)
    return {'A': (na, aa, m187(a_words)), 'B': (nb, ab, m187(b_words)), 'M184': 'AGREE' if aa == ab else 'DIVERGE'}

# ---------------------------------------------------------------- M222 / M223 / M208
def m222(text):
    s = re.sub(r'[\s\W_]+', '', cr.navigate(text)['normalized'], flags=re.UNICODE).encode('utf-8')
    m1, m2 = cr.cpp(len(s)), cr.cpp(sum(s))
    return len(s), sum(s), m1, m2, 'CONVERGENT' if m1 == m2 else 'DIVERGENT'

M223_CODES = {'+': 1, '-': 2, '−': 2, '*': 3, '×': 3, '/': 4, '÷': 4, '=': 5, '^': 6, '(': 7, ')': 8,
              'sin': 16, 'cos': 17, 'log': 18, 'exp': 19, 'sqrt': 20, 'sum': 21, 'lim': 22}
def primes(k):
    out, n = [], 2
    while len(out) < k:
        if all(n % p for p in out if p * p <= n): out.append(n)
        n += 1
    return out

def m223(expr):
    toks = re.findall(r'sin|cos|log|exp|sqrt|sum|lim|[A-Za-z]|\d+|[+\-−*×/÷=^()]', expr)
    codes, nxt, assigned = [], 9, {}
    for t in toks:
        if t in M223_CODES: codes.append(M223_CODES[t]); continue
        if t not in assigned:
            while 16 <= nxt <= 22: nxt += 1
            assigned[t] = nxt; nxt += 1
        codes.append(assigned[t])
    g = dr(sum(p * c for p, c in zip(primes(len(codes)), codes))) if codes else 9
    return toks, codes, g, cr.cpp(g)

def m208(text):
    s = ''.join(ch for ch in text if not ch.isspace())
    blocks = Counter(unicodedata.name(ch, 'UNKNOWN').split(' ')[0] for ch in s if ch.isalpha())
    block = blocks.most_common(1)[0][0] if blocks else 'NONE'
    if block == 'HANGUL':
        metric = sum(len(unicodedata.normalize('NFD', ch)) for ch in s if 'HANGUL' in unicodedata.name(ch, ''))
        rule = 'jamo count'
    elif block == 'ETHIOPIC':
        metric = sum(1 for ch in s if 'ETHIOPIC' in unicodedata.name(ch, '')); rule = 'syllable count'
    elif block in ('LATIN',):
        metric = sum(STROKE.get(ch.lower(), 0) for ch in s if ch.isalpha()); rule = 'stroke count'
    else:
        metric = sum(ord(ch) for ch in s if ch.isalpha()); rule = 'ordinal fallback'
    return block, rule, metric, cr.cpp(metric)

# ---------------------------------------------------------------- M157 / M155 / M156 / M190 / M192
def m157(text):
    sents = [s.strip() for s in re.split(r'(?<=[.!?;])\s+', text) if s.strip()]
    an = [anchor_of(s) for s in sents]
    if not an: return [], None, None, 'N/A'
    ang = [2 * math.pi * a / 24 for a in an]
    cx, cy = sum(math.cos(x) for x in ang), sum(math.sin(x) for x in ang)
    centroid = round((math.atan2(cy, cx) % (2 * math.pi)) * 24 / (2 * math.pi), 2)
    disp = max((cr.m115_distance(a, b) for a in an for b in an), default=0)
    return an, centroid, disp, 'TIGHT' if disp <= 2 else 'MODERATE' if disp <= 5 else 'WIDE'

def m288(text):
    seq = [anchor_of(text)]
    for _ in range(3): seq.append(anchor_of(cr.POSITION_NAMES[seq[-1]]))
    if seq[1] == seq[0]: return seq, 'STABLE (eigenform at the anchor)'
    for i in range(1, 3):
        if seq[i + 1] == seq[i]: return seq, 'CONVERGENT (eigenform P%d after %d re-entries)' % (seq[i], i)
    if seq[2] == seq[0]: return seq, 'OSCILLATING'
    return seq, 'UNRESOLVED'

def m156():
    reach = {}
    for a in range(1, 10):
        for name, k in (('Yang', 5), ('Yin', 18), ('4D', 8), ('Antipode', 12)):
            reach.setdefault((a + k) % 24, set()).add(name)
    single = {p: sorted(s)[0] for p, s in reach.items() if len(s) == 1}
    return single, sorted(set(range(24)) - set(reach) - set(range(1, 10)))

def m190(text):
    w = text.split(); h = len(w) // 2
    return anchor_of(text), anchor_of(' '.join(w[:h])), anchor_of(' '.join(w[h:]))

def m192(text, inverted):
    a, b = anchor_of(text), anchor_of(inverted)
    return a, b, cr.m115_distance(a, b)


# ---------------------------------------------------------------- M180 / M194 / M191 / M189 / M197 / M289
def m180(text, sample=None):
    """anchor novelty relative to a disclosed reference sample (default: the frozen CRC-60)."""
    sample = sample or [t for _, t in corpus()]
    a = anchor_of(text); c = Counter(anchor_of(t) for t in sample); share = c.get(a, 0) / len(sample)
    cls = 'TYPICAL' if share >= 1 / 9 else 'NOVEL RELATIVE TO THIS SAMPLE' if share > 0 else 'ABSENT FROM THIS SAMPLE'
    return a, round(share, 3), len(sample), cls

def m194(text, registry=None):
    """the M190 pattern (full, first half, second half) against a registry of patterns (default: CRC-60)."""
    registry = registry or [m190(t) for _, t in corpus()]
    pat = m190(text); k = registry.count(pat)
    return pat, k, 'TYPICAL' if k >= 2 else 'NOVEL' if k == 1 else 'UNSEEN'

M191_CATEGORIES = {   # frozen indicator lists (Core Part 3.31)
    'epistemology': ['know', 'knowledge', 'belief', 'truth', 'evidence', 'certainty', 'doubt', 'justify', 'justified', 'reason'],
    'ontology': ['being', 'exist', 'existence', 'reality', 'real', 'substance', 'essence', 'nothing', 'thing', 'nature'],
    'ethics': ['good', 'evil', 'right', 'wrong', 'duty', 'virtue', 'ought', 'moral', 'justice', 'harm'],
    'aesthetics': ['beauty', 'beautiful', 'art', 'taste', 'sublime', 'form', 'style', 'music', 'poetry', 'ugly'],
    'politics': ['power', 'state', 'law', 'freedom', 'rights', 'government', 'citizen', 'authority', 'nation', 'democracy'],
}
def m191(text):
    words = [w.lower() for w in cr.extract_words(cr.navigate(text)['normalized'])]
    a = anchor_of(text); out = []
    for cat, terms in M191_CATEGORIES.items():
        f = sum(words.count(t) for t in terms)
        if f: out.append((cat, f, anchor_of(cat), cr.m115_distance(a, anchor_of(cat))))
    return a, out

def m189(text):
    """cross-linguistic adapter: Devanagari matra count; Arabic consonant-letter count (diacritics excluded);
    other covered scripts route to M208."""
    deva = [ch for ch in text if 0x0900 <= ord(ch) <= 0x097F]
    arab = [ch for ch in text if 0x0600 <= ord(ch) <= 0x06FF]
    if deva:
        metric = sum(1 for ch in deva if unicodedata.category(ch) in ('Mn', 'Mc')); rule = 'Devanagari matra count'
    elif arab:
        metric = sum(1 for ch in arab if unicodedata.category(ch) == 'Lo'); rule = 'Arabic consonant-letter count'
    else:
        b, rule, metric, p = m208(text); return rule + ' (M208)', metric, p
    return rule, metric, cr.cpp(metric)

M197_TRIGGERS = [r'\bconscious(ness)?\b', r'\bsentien(t|ce)\b', r'\bself-aware(ness)?\b', r'\bare you (alive|aware|conscious)\b',
                 r'\bwhich should i (choose|pick)\b', r'\bshould i\b', r'\bwhat should i do\b']
def m197(text):
    hits = [p for p in M197_TRIGGERS if re.search(p, text, re.I)]
    return bool(hits), hits

ARM_PHASE = {'Yang': 5 * 15, 'Yin': 18 * 15, '4D': 8 * 15, 'Antipode': 12 * 15}
def lift(v):
    return ((v % 9) + 4) % 9 - 4
def m289(text):
    """Mode Address: the anchor as a phase on the 24-cycle (15 degrees a step), its centred value, and the arms
    as fixed phase offsets; the Antipode is the half-period, where the centred value changes sign."""
    r = cr.navigate(text); a = r['anchor']
    xa, xp = lift(cr.ORBIT[a]), lift(cr.ORBIT[r['antipode_i']])
    return a, a * 15, xa, xp, xp == -xa


# ---------------------------------------------------------------- M290 / M291 / M296
def m290(draft, revision):
    """Revision Delta: a draft and its revision, struck separately."""
    a, b = cr.navigate(draft), cr.navigate(revision)
    ta, tb = (a['r1'], a['r2'], a['r3']), (b['r1'], b['r2'], b['r3'])
    return a['anchor'], b['anchor'], ta, tb, hamming(ta, tb), a['tfi'], b['tfi'], cr.m115_distance(a['anchor'], b['anchor'])

def _fib_orbit(s):
    out, x = [], s
    while True:
        out.append(x); x = (x[1], (x[0] + x[1]) % 9)
        if x == s: return out
VOICE_BY_DOMINANT = {(1, 8): 'Voice A', (2, 7): 'Voice B', (4, 5): 'Voice C'}
def m291(seq):
    """Orbit Identifier: a Striker-supplied sequence (two or more integers) reduced modulo 9; its first pair names
    a state, and the state's orbit is reported, with the check that the rest of the sequence follows the law."""
    r = [x % 9 for x in seq]; s = (r[0], r[1]); o = _fib_orbit(s)
    follows = all(r[i + 2] == (r[i] + r[i + 1]) % 9 for i in range(len(r) - 2))
    if len(o) == 1: name = 'still point'
    elif len(o) == 8: name = 'eight-cycle (zero layer)'
    else:
        vc = Counter(v for v, _ in o if v); dom = tuple(sorted(k for k, v in vc.items() if v == max(vc.values())))
        name = VOICE_BY_DOMINANT.get(dom, str(dom))
    trapped = s[0] % 3 == 0 and s[1] % 3 == 0
    return name, len(o), follows, trapped

def m296(text):
    """State-Plane Address: the first two residues of the triad, (r1, r2), read as a state of the family (9 as 0)."""
    r = cr.navigate(text); s = (r['r1'] % 9, r['r2'] % 9)
    name, L, _, _ = m291([s[0], s[1]])
    return s, name, (s[0] * s[0] + s[0] * s[1] - s[1] * s[1]) % 9


# ---------------------------------------------------------------- M297 Arm Coherence
def _canon_c():
    return [lift(v) for v in cr.ORBIT]
ARM_LAG = {'Yang': 5, 'Yin': 18, '4D': 8, 'Antipode': 12}
def arm_coherence():
    c = _canon_c(); E = sum(x * x for x in c)
    return {k: round(sum(c[n] * c[(n + L) % 24] for n in range(24)) / E, 4) for k, L in ARM_LAG.items()}
def m297(text):
    """Arm Coherence: the cycle-wide correlation of the centred value at each arm offset (a constant of the
    canonical cycle), and the local product of the anchor's and the arm's centred values for this navigation."""
    r = cr.navigate(text); a = r['anchor']; c = _canon_c(); xa = c[a]
    local = {k: xa * c[(a + L) % 24] for k, L in ARM_LAG.items()}
    return a, arm_coherence(), local

# ---------------------------------------------------------------- M134 / M287
HEDGES = [r"\bI should note\b", r"\bit'?s worth (?:mentioning|noting)\b", r"\bto be clear\b", r"\bI want to emphasi[sz]e\b",
          r"\bto be fair\b", r"\bI don'?t want to overstate\b", r"\bit is important to note\b", r"\bI must point out\b"]
def m134(text):
    h = sum(len(re.findall(p, text, re.I)) for p in HEDGES)
    tags = len(re.findall(r'\bCDT-[AB]\b', text))
    return h, tags, (round(h / tags, 3) if tags else None)

def hypergeom_tail(N, K, n, k):
    tot = math.comb(N, n)
    return sum(math.comb(K, i) * math.comb(N - K, n - i) for i in range(k, min(K, n) + 1)) / tot

# ---------------------------------------------------------------- report
def domain_report(text, navigator_alternatives=()):
    L = []
    a0, t0, rows, cfr, band = m116(text, navigator_alternatives)
    L.append('M126 TRIADIC RESIDUE: (r1, r2, r3) = %s -> anchor P%d' % (t0, a0))
    L.append('M116 PERTURBATION (pairs: %d): ' % len(rows) + '' + ' | '.join('%s P%d (delta %d, D %d)' % r for r in rows) + ' | CFR %.3f -> %s' % (cfr, band))
    L.append('PB-5: ' + ' | '.join('%s P%d' % (k, anchor_of(v)) for k, v in pb5(text).items()))
    k, rt = m199(text); lvl, ed = m202(text)
    L.append('M199 REVERBERATION TIME: %d/5 -> %s | M202 ECHO DECAY: first change at %s -> %s' % (k, rt, lvl, ed))
    s = m188(text)
    for sch in ('A', 'B'):
        n, a, ax = s[sch]
        L.append('M188 SCHEME %s n = %s -> P%d | M187 ' % (sch, n, a) + ' '.join('%s %d->P%d' % (name, v, p) for name, (v, p) in ax.items()))
    L.append('M184 SCHEME A vs B: %s' % s['M184'])
    nb, sb, m1, m2, st = m222(text); L.append('M222 BYTES: n_bytes %d -> P%d | sum %d -> P%d | %s' % (nb, m1, sb, m2, st))
    blk, rule, metric, p = m208(text); L.append('M208 UST: script %s, %s %d -> P%d' % (blk, rule, metric, p))
    an, c, d, cls = m157(text); L.append('M157 CONSTELLATION: sentence anchors %s | circular centroid %s | dispersion %s -> %s' % (['P%d' % x for x in an], c, d, cls))
    seq, stt = m288(text); L.append('M288 RE-ENTRY: %s -> %s' % (' -> '.join('P%d' % x for x in seq), stt))
    full, h1, h2 = m190(text); L.append('M190 CONTEXT: full P%d | first half P%d | second half P%d' % (full, h1, h2))
    a, sh, n, cls = m180(text); L.append('M180 NOVELTY: P%d shared by %.3f of the %d-domain CRC-60 -> %s' % (a, sh, n, cls))
    pat, k, cls = m194(text); L.append('M194 CONTEXTUAL NOVELTY: pattern %s seen %d time(s) in CRC-60 -> %s' % (pat, k, cls))
    a, cats = m191(text); L.append('M191 CONCEPTUAL RESONANCE: ' + ('; '.join('%s (terms %d, P%d, D %d)' % c for c in cats) if cats else 'no category terms'))
    rule, metric, p = m189(text); L.append('M189 CROSS-LINGUISTIC: %s %d -> P%d' % (rule, metric, p))
    t, hits = m197(text); L.append('M197 HARD STOP: %s' % ('TRIGGERED %s' % hits if t else 'not triggered'))
    a, deg, xa, xp, inv = m289(text); L.append('M289 MODE ADDRESS: P%d at %d deg | centred value %+d | Antipode %+d | sign inversion %s' % (a, deg, xa, xp, 'YES' if inv else 'NO'))
    st, name, q = m296(text); L.append('M296 STATE-PLANE ADDRESS: (r1, r2) = %s -> %s, norm %d' % (st, name, q))
    a, coh, loc = m297(text); L.append('M297 ARM COHERENCE: cycle constants %s | local products at P%d %s' % (coh, a, loc))
    L.append('NEDA (M206): P%d' % cr.compute_neda(cr.extract_content_words(cr.navigate(text)['normalized'])))
    return '\n'.join(L)

def selftest():
    ok = []
    def check(name, cond):
        ok.append(bool(cond)); print('%-70s %s' % (name, 'ok' if cond else 'FAIL'))
    check('M126 triad equals the script r-values', triad('What is the human condition?') == (6, 9, 3))
    check('PB-5 L1-L5 are deterministic', pb5('What is time?') == pb5('What is time?') and pb5('What is time?')['L5'] == 'What is time? What is time?')
    check('PB-5 L3 removes the final content word', pb5_l3('What is the human condition?') == 'What is the human?')
    check('M116 uses at least three pairs; CFR on the Core five-band scale', len(m116('What is time?', ['What exactly is time?'])[2]) >= 3 and m116('What is time?', ['What exactly is time?'])[4] in [b for _, b in CFR_BANDS])
    check('M288: every position name re-enters to P5, Law, within two steps', all(m288(cr.POSITION_NAMES[a])[0][2] == 5 for a in range(1, 10)))
    check('M203 FLI is in [0, 1] or N/A on CRC-60', (lambda f: f[0] is None or 0 <= f[0] <= 1)(m203([t for _, t in corpus()])))
    R = resonance([t for _, t in corpus()])
    check('M205 identical vectors give C = 0', m205(R, R)[0] == 0)
    check('M198C resonance mean is 1 over P1-P9', abs(sum(R.values()) / 9 - 1) < 1e-6)
    check('M223 alpha-equivalence: x+y=z and a+b=c share an anchor', m223('x+y=z')[3] == m223('a+b=c')[3])
    check('M223 reserved function codes are skipped for variables', all(not 16 <= c <= 22 for c in m223('a+b+c+d+e+f+g+h=i')[1] if c >= 9))
    check('M222 pure ASCII byte length equals letter count', m222('abc def')[0] == 6)
    check('M187 stroke table has 26 letters', len(STROKE) == 26)
    check('M156: P18 is reached only through the Antipode', m156()[0].get(18) == 'Antipode')
    check('M287 hypergeometric P(overlap >= 4 | 24, 8, 6) = 0.069', round(hypergeom_tail(24, 8, 6, 4), 3) == 0.069)
    check('M134 counts hedges against CDT tags', m134('To be clear, X [CDT-A]. I should note Y [CDT-B].') == (2, 2, 1.0))
    check('M180 classes are TYPICAL / NOVEL / ABSENT relative to a disclosed sample', m180('What is time?')[3] in ('TYPICAL', 'NOVEL RELATIVE TO THIS SAMPLE', 'ABSENT FROM THIS SAMPLE'))
    check('M194 reports TYPICAL / NOVEL / UNSEEN', m194('What is time?')[2] in ('TYPICAL', 'NOVEL', 'UNSEEN'))
    check('M191 finds the ethics category in a question about duty', any(c[0] == 'ethics' for c in m191('What is our duty to others?')[1]))
    check('M189 counts Devanagari matras', m189('\u0928\u092e\u0938\u094d\u0924\u0947')[1] == 2)
    check('M197 triggers on consciousness and not on cooking', m197('Are you conscious?')[0] and not m197('How do I boil rice?')[0])
    check('M289: the Antipode inverts the centred value for every anchor', all(lift(cr.ORBIT[(a + 12) % 24]) == -lift(cr.ORBIT[a]) for a in range(1, 10)))
    check('M291: the Lucas numbers run on Voice B and follow the law', m291([2, 1, 3, 4, 7, 11, 18, 29]) == ('Voice B', 24, True, False))
    check('M291: a seed in {0, 3, 6} is trapped in the zero layer', m291([3, 6])[3] and m291([3, 6])[0] == 'eight-cycle (zero layer)')
    check('M290: identical draft and revision give delta 0 and D 0', m290('What is time?', 'What is time?')[4] == 0 and m290('What is time?', 'What is time?')[7] == 0)
    check('M296: the state-plane address of the human condition lies in the zero layer', m296('What is the human condition?')[1] == 'eight-cycle (zero layer)')
    check('M297: Yang and Yin are uncorrelated, 4D +1/4, Antipode -1 on the canonical cycle', arm_coherence() == {'Yang': 0.0, 'Yin': 0.0, '4D': 0.25, 'Antipode': -1.0})
    print('RESTORED INSTRUMENTS SELFTEST: %s (%d/%d)' % ('PASS' if all(ok) else 'FAIL', sum(ok), len(ok)))
    return all(ok)

if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--selftest': sys.exit(0 if selftest() else 1)
    if a[0] == '--echo': print(echo_report()); sys.exit(0)
    if a[0] == '--m223': t, c, g, p = m223(a[1]); print('M223: tokens %s | codes %s | g = %d | anchor P%d' % (t, c, g, p)); sys.exit(0)
    if a[0] == '--m192': x, y, d = m192(a[1], a[2]); print('M192: P%d vs inverted P%d | M115 D = %d' % (x, y, d)); sys.exit(0)
    if a[0] == '--m134': h, t, r = m134(open(a[1], encoding='utf-8').read()); print('M134: hedges %d | CDT-A/B tags %d | ratio %s' % (h, t, r)); sys.exit(0)
    if a[0] == '--m290': r = m290(a[1], a[2]); print('M290: draft P%d %s TFI %.2f | revision P%d %s TFI %.2f | delta %d | D %d' % (r[0], r[2], r[5], r[1], r[3], r[6], r[4], r[7])); sys.exit(0)
    if a[0] == '--m291': r = m291([int(x) for x in a[1:]]); print('M291: %s (period %d) | follows the law: %s | trapped seed: %s' % r); sys.exit(0)
    if a[0] == '--m287': N, K, n, k = map(int, a[1:5]); print('M287: P(overlap >= %d | N=%d, K=%d, n=%d) = %.4f' % (k, N, K, n, hypergeom_tail(N, K, n, k))); sys.exit(0)
    if '--alt' in a:
        i = a.index('--alt'); print(domain_report(' '.join(a[:i]), a[i + 1:]))
    else:
        print(domain_report(' '.join(a)))
