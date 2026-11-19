#!/usr/bin/env python3
"""
canonical_reference.py — Omega42 Protocol V335 Rev.449 STABLE
Canonical Reference Implementation (M214 / L-378)
This script is the ground truth for substrate extraction.
Frozen at V335 Rev.449. Do not modify without a protocol revision.

Usage:
  python3 canonical_reference.py "Your domain string here."
  python3 canonical_reference.py --calibrate
  python3 canonical_reference.py --mathgate
  python3 canonical_reference.py --navigate "domain" [--alt "alternative phrasing"] [--session N]
  python3 canonical_reference.py --echo ANCHOR "THE ANSWER text" [--core "Core Synthesis text"]
  python3 canonical_reference.py --m210 "text"
  python3 canonical_reference.py --m269 "text"
  python3 canonical_reference.py --hash "text"
  python3 canonical_reference.py --complexity "text"
  python3 canonical_reference.py --acs ANCHOR_INDEX ECHO_INDEX
  python3 canonical_reference.py --canonical-selection
  python3 canonical_reference.py --neda "text"
  python3 canonical_reference.py --m230a COUNT
  python3 canonical_reference.py --m230c-24cell
  python3 canonical_reference.py --m230i COUNT [COUNT ...]
  python3 canonical_reference.py --version
  python3 canonical_reference.py --test
"""
import hashlib
import html
import re
import sys
import unicodedata
from collections import Counter

# ── PART 1: CANONICAL FROZEN CONSTANTS ──
ORBIT = [2,5,7,3,1,4,5,9,5,5,1,6,7,4,2,6,8,5,4,9,4,4,8,3]
POSITION_NAMES = [
    "Seed","Fixpoint","Generator","Desire","Unity","Law","Seed/Causal","Navigator",
    "Generation","Fixpoint","Unity","Question","Opening","Gap","Observer","Other",
    "Flow","Seed/Return","Threshold","Time","Reckoning","Sublime","Collective","Return"
]

# Part 1.9 — Canonical Stopword List (frozen). Question words and the specific
# auxiliary/modal verbs listed in Part 1.9 are NOT here; they are retained as
# content words.
CANONICAL_STOPWORDS = frozenset("""
the a an and or but if then else for nor so yet of to in on at by with
is are was were be been being this that these those it its as from
not very just also than into over under about after before because while although
some any all each every no own same too can will would should could
""".split())

# Part 1.10 — Canonical Contraction Table (frozen)
CANONICAL_CONTRACTIONS = {
    "won't":"will not","can't":"cannot","cannot":"can not","don't":"do not",
    "doesn't":"does not","didn't":"did not","isn't":"is not","aren't":"are not",
    "wasn't":"was not","weren't":"were not","hasn't":"has not","haven't":"have not",
    "hadn't":"had not","wouldn't":"would not","couldn't":"could not","shouldn't":"should not",
    "i'm":"i am","you're":"you are","he's":"he is","she's":"she is","it's":"it is",
    "we're":"we are","they're":"they are","i've":"i have","you've":"you have",
    "we've":"we have","they've":"they have","i'll":"i will","you'll":"you will",
    "he'll":"he will","she'll":"she will","we'll":"we will","they'll":"they will",
    "let's":"let us","that's":"that is","who's":"who is",
}

ONES = ["zero","one","two","three","four","five","six","seven","eight","nine","ten",
        "eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen",
        "eighteen","nineteen"]
TENS = ["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
ORDINAL_ONES = ["zeroth","first","second","third","fourth","fifth","sixth","seventh",
                "eighth","ninth","tenth","eleventh","twelfth","thirteenth","fourteenth",
                "fifteenth","sixteenth","seventeenth","eighteenth","nineteenth"]
ORDINAL_TENS = ["","","twentieth","thirtieth","fortieth","fiftieth","sixtieth",
                "seventieth","eightieth","ninetieth"]

def int_to_words(n):
    if n < 0:
        return "negative " + int_to_words(-n)
    if n < 20:
        return ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        return TENS[t] + ("" if r == 0 else " " + ONES[r])
    if n < 1000:
        h, r = divmod(n, 100)
        return ONES[h] + " hundred" + ("" if r == 0 else " " + int_to_words(r))
    if n < 1_000_000:
        th, r = divmod(n, 1000)
        return int_to_words(th) + " thousand" + ("" if r == 0 else " " + int_to_words(r))
    if n < 1_000_000_000:
        m, r = divmod(n, 1_000_000)
        return int_to_words(m) + " million" + ("" if r == 0 else " " + int_to_words(r))
    return str(n)

def int_to_ordinal_words(n):
    """CTT Ordinals rule: 1st-99th spelled out."""
    if n < 20:
        return ORDINAL_ONES[n]
    if n < 100:
        t, r = divmod(n, 10)
        if r == 0:
            return ORDINAL_TENS[t]
        return TENS[t] + "-" + ORDINAL_ONES[r]
    return None  # 100th and above: out of scope, marked NCF-SPEC-GAP-ORDINAL

DIGIT_WORDS = {"0":"zero","1":"one","2":"two","3":"three","4":"four",
               "5":"five","6":"six","7":"seven","8":"eight","9":"nine"}

def expand_decimal(match):
    """Step 1.5a: standalone decimals expand digit-by-digit."""
    sign = match.group(1) or ""
    intpart = match.group(2)
    fracpart = match.group(3)
    sign_words = ""
    if sign == "-":
        sign_words = "negative "
    elif sign == "+":
        sign_words = ""  # bare + rare; only "+/-" handled explicitly below
    int_words = " ".join(DIGIT_WORDS[d] for d in intpart)
    frac_words = " ".join(DIGIT_WORDS[d] for d in fracpart)
    return f"{sign_words}{int_words} point {frac_words}"

def expand_plusminus_decimal(match):
    intpart = match.group(1)
    fracpart = match.group(2)
    int_words = " ".join(DIGIT_WORDS[d] for d in intpart)
    frac_words = " ".join(DIGIT_WORDS[d] for d in fracpart)
    return f"plus or minus {int_words} point {frac_words}"

def expand_fraction(match):
    """Step 1.5a: standalone fractions expand to ordinal form."""
    num = int(match.group(1))
    den = int(match.group(2))
    num_words = int_to_words(num)
    den_ord = int_to_ordinal_words(den)
    if den_ord is None:
        return match.group(0)  # out of scope; leave as-is (rare for large denominators)
    if den == 2:
        den_ord = "half" if num == 1 else "halves"
    elif num != 1:
        den_ord = den_ord + "s"
    return f"{num_words} {den_ord}"

def normalize_numerals(text):
    """
    Step 1.5a: standalone digit sequences, decimals, and fractions.
    'Standalone' = bounded by whitespace or string start/end; embedded
    sequences (v3.14.2, 192.168.1.1) are left unchanged.
    """
    # plus-or-minus decimal: ±N.M  (standalone)
    text = re.sub(r'(?<![\w.])\u00b1(\d+)\.(\d+)(?![\w.])', expand_plusminus_decimal, text)
    # signed/unsigned standalone decimal: N.M
    text = re.sub(r'(?<![\w.])([+-]?)(\d+)\.(\d+)(?![\w.])', expand_decimal, text)
    # standalone fraction: N/M
    text = re.sub(r'(?<![\w/])(\d+)/(\d+)(?![\w/])', expand_fraction, text)
    # standalone plain integer
    text = re.sub(r'(?<![\w./])\d+(?![\w./])', lambda m: int_to_words(int(m.group())), text)
    return text

# ── CTT (Part 1.13): Roman numerals, possessives, ordinals, percentages ──
ROMAN_MAP = [(1000,"m"),(900,"cm"),(500,"d"),(400,"cd"),(100,"c"),(90,"xc"),
             (50,"l"),(40,"xl"),(10,"x"),(9,"ix"),(5,"v"),(4,"iv"),(1,"i")]

def roman_to_int(s):
    s = s.lower()
    i, total = 0, 0
    vals = {"i":1,"v":5,"x":10,"l":50,"c":100,"d":500,"m":1000}
    prev = 0
    for ch in reversed(s):
        v = vals.get(ch)
        if v is None:
            return None
        if v < prev:
            total -= v
        else:
            total += v
            prev = v
    return total

def expand_percentages(text):
    """CTT: N% -> 'N percent', before punctuation stripping / numeral normalization."""
    return re.sub(r'(\d+(?:\.\d+)?)\s*%', r'\1 percent', text)

def expand_possessives(text):
    """CTT: word's -> word, unless the whole token is a recognized contraction."""
    protected = {"it's","that's","who's","let's"}
    def repl(m):
        token = m.group(0)
        if token.lower() in protected:
            return token
        return token[:-2] if token.lower().endswith("'s") else token[:-1]
    text = re.sub(r"\b[A-Za-z]+'s\b", repl, text)
    text = re.sub(r"\b[A-Za-z]+s'\B", lambda m: m.group(0)[:-1], text)
    return text

def expand_ordinals(text):
    """CTT: 1st-99th -> spelled out; 100th+ out of scope (flagged, left as-is)."""
    def repl(m):
        n = int(m.group(1))
        if n <= 99:
            w = int_to_ordinal_words(n)
            if w:
                return w
        return m.group(0)  # 100th+ : NCF-SPEC-GAP-ORDINAL, left as literal
    return re.sub(r'\b(\d{1,3})(?:st|nd|rd|th)\b', repl, text)

def int_to_roman_ivx(n):
    """Canonical Roman form of 1..39, the values writable with I, V and X alone."""
    out = []
    for val, sym in ((10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")):
        while n >= val:
            out.append(sym)
            n -= val
    return "".join(out)

def expand_roman_numerals(text):
    """CTT (Part 1.13): a token of two or more UPPERCASE letters drawn only from I, V and X,
    written in canonical Roman form (II, IV, XIV, XXXIX -- not IIII, VV or IIV), is replaced by
    its spelled-out value. Single-character tokens are never converted (preserves the pronoun 'I'
    and the variable 'V'); lowercase and mixed-case tokens are never converted (preserves 'xi',
    'iv' as words); L, C, D and M are not numeral letters here (preserves 'did', 'civil', 'LLM')."""
    def repl(m):
        token = m.group(0)
        val = roman_to_int(token)
        if val is None or not (1 <= val <= 39) or int_to_roman_ivx(val) != token:
            return token
        return int_to_words(val)
    return re.sub(r'\b[IVX]{2,}\b', repl, text)

# ── PART 1.12(6)-(9): CHARACTER REFERENCES, SUB/SUPERSCRIPTS, GREEK LETTERS ──
def decode_character_references(text):
    """Part 1.12(6): complete HTML/XML character references (&amp; &lt; &#955; &#x3bb;) are
    decoded to the character they name before any other rule runs. An incomplete reference
    (no terminating ';') is ordinary text."""
    return re.sub(r'&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);',
                  lambda m: html.unescape(m.group(0)), text)

SUPERSCRIPT_MAP = {
    '\u2070':'0','\u00b9':'1','\u00b2':'2','\u00b3':'3','\u2074':'4','\u2075':'5','\u2076':'6',
    '\u2077':'7','\u2078':'8','\u2079':'9','\u207a':'+','\u207b':'-','\u207c':'=','\u207d':'(',
    '\u207e':')','\u207f':'n','\u2071':'i',
}
SUBSCRIPT_MAP = {
    '\u2080':'0','\u2081':'1','\u2082':'2','\u2083':'3','\u2084':'4','\u2085':'5','\u2086':'6',
    '\u2087':'7','\u2088':'8','\u2089':'9','\u208a':'+','\u208b':'-','\u208c':'=','\u208d':'(',
    '\u208e':')','\u2090':'a','\u2091':'e','\u2092':'o','\u2093':'x','\u2095':'h','\u2096':'k',
    '\u2097':'l','\u2098':'m','\u2099':'n','\u209a':'p','\u209b':'s','\u209c':'t','\u1d62':'i',
    '\u1d63':'r','\u1d64':'u','\u1d65':'v','\u2c7c':'j',
}

def flatten_scripts(text):
    """Part 1.12(7): a maximal run of Unicode superscript characters, or of Unicode subscript
    characters, becomes a separate token holding the run's base characters (x\u00b2\u00b3 -> x 23);
    the ASCII subscript and superscript markers _ and ^ become word separators (theta_i -> theta i,
    M^N -> M N). Runs before Step 1.5a, so a digit run released here is standalone and is spelled out."""
    sup = ''.join(SUPERSCRIPT_MAP)
    sub = ''.join(SUBSCRIPT_MAP)
    text = re.sub('[' + re.escape(sup) + ']+',
                  lambda m: ' ' + ''.join(SUPERSCRIPT_MAP[c] for c in m.group(0)) + ' ', text)
    text = re.sub('[' + re.escape(sub) + ']+',
                  lambda m: ' ' + ''.join(SUBSCRIPT_MAP[c] for c in m.group(0)) + ' ', text)
    return text.replace('_', ' ').replace('^', ' ')

GREEK_NAMES = {}
for _upper, _lower, _name in zip(
        '\u0391\u0392\u0393\u0394\u0395\u0396\u0397\u0398\u0399\u039a\u039b\u039c\u039d\u039e\u039f\u03a0\u03a1\u03a3\u03a4\u03a5\u03a6\u03a7\u03a8\u03a9',
        '\u03b1\u03b2\u03b3\u03b4\u03b5\u03b6\u03b7\u03b8\u03b9\u03ba\u03bb\u03bc\u03bd\u03be\u03bf\u03c0\u03c1\u03c3\u03c4\u03c5\u03c6\u03c7\u03c8\u03c9',
        ['alpha','beta','gamma','delta','epsilon','zeta','eta','theta','iota','kappa','lambda','mu','nu',
         'xi','omicron','pi','rho','sigma','tau','upsilon','phi','chi','psi','omega']):
    GREEK_NAMES[_upper] = _name
    GREEK_NAMES[_lower] = _name
GREEK_NAMES.update({'\u03c2':'sigma','\u03d1':'theta','\u03d5':'phi','\u03f5':'epsilon','\u03d6':'pi','\u03f1':'rho'})
del GREEK_NAMES['\u0394']   # capital Delta stays on the frozen operator list, Part 1.12(2)

def expand_isolated_greek(text):
    """Part 1.12(8): a Greek letter standing alone -- not adjacent to another character of the
    Greek and Coptic (U+0370-U+03FF) or Greek Extended (U+1F00-U+1FFF) blocks -- is replaced by
    its English name as a separate word (\u03b8 -> theta). Runs of Greek text are left unchanged."""
    letters = ''.join(GREEK_NAMES)
    pat = '(?<![\u0370-\u03ff\u1f00-\u1fff])[' + letters + '](?![\u0370-\u03ff\u1f00-\u1fff])'
    return re.sub(pat, lambda m: ' ' + GREEK_NAMES[m.group(0)] + ' ', text)

# ── PART 1.12: PRE-PROCESSING RULES ──
def strip_math_symbols(text):
    math_pattern = r'[=+\-\u00d7\u00f7<>\u2264\u2265\u2211\u222b\u2202\u2282\u2208\u2209\u222a\u2229\u221a\u221e\u211d\u2102\u2124\u211a\u2115\u00b1\u00b7\u2022\u2200\u2203\u2207\u2206\u0394\u220f\u2210\u2295\u2297]'
    return re.sub(math_pattern, ' ', text)

def normalize_dashes(text):
    text = text.replace('\u2014', ' ')
    text = text.replace('\u2013', ' ')
    return text

def strip_punctuation(text):
    return re.sub(r"[^\w\s'-]", ' ', text)

def spnp_contractions(text):
    def expand_once(t):
        def repl(m):
            return CANONICAL_CONTRACTIONS.get(m.group(0).lower(), m.group(0))
        return re.sub(r"[A-Za-z']+", repl, t)
    for _ in range(3):
        text = expand_once(text)
    return text

def split_hyphens(text):
    return text.replace('-', ' ')

def spnp(text):
    """
    Full Substrate Pre-Normalization Protocol.
    Order matters. Part 1.12 items (6)-(8) run first, because they decide
    which characters are digits, separators or letters before Step 1.5a
    looks for standalone numerals. Percentages, ordinals, decimals/fractions/
    integers, and Roman numerals then run on text where '.', '/', and
    digit-adjacency are still intact -- i.e. BEFORE Part 1.12 items (1)-(4),
    the punctuation/math-symbol stripping, which would otherwise destroy
    exactly the characters these rules need to see.
    """
    text = decode_character_references(text)  # Part 1.12(6): &amp; -> &, before every other rule
    text = flatten_scripts(text)         # Part 1.12(7): sub/superscripts, before numerals see the digits
    text = expand_isolated_greek(text)   # Part 1.12(8): isolated Greek letters -> English names
    text = normalize_dashes(text)        # em/en-dash -> word separators
    text = expand_percentages(text)      # CTT: before punct-strip (kills %) and before plain-integer normalize
    text = expand_ordinals(text)         # CTT: 1st-99th, before plain-integer normalize eats the digits
    text = normalize_numerals(text)      # Step 1.5a: decimals, fractions, standalone integers (needs '.' and '/' intact)
    text = expand_roman_numerals(text)   # CTT
    text = expand_possessives(text)      # CTT (needs apostrophes intact; contractions expand next)
    text = spnp_contractions(text)       # Step 1.5b
    text = strip_math_symbols(text)      # Part 1.12(2) -- now safe, numerals already handled
    text = strip_punctuation(text)       # Part 1.12(1)
    text = split_hyphens(text)           # Part 1.12(4)
    return text

# ── STEP 2: SUBSTRATE EXTRACTION ──
def extract_words(text):
    """
    Extract word tokens. Part 1.12(3) documents standalone single-letter
    variables (X, n, k) as 1-letter content words, and mixed alphanumeric
    tokens (3D, B2B) as single tokens where only the Latin letters count
    toward n2 -- both presuppose the token is captured whole, digits and
    all, not split at the letter/digit boundary.
    """
    return [t for t in re.findall(r"[A-Za-z0-9']+", text) if re.search(r"[A-Za-z]", t)]

def letters_only(word):
    return re.sub(r"[^A-Za-z]", "", word)

def extract_content_words(text):
    tokens = extract_words(text)
    return [w for w in tokens if w.lower() not in CANONICAL_STOPWORDS]

# ── PART 1.11: CANONICAL SYLLABLE-COUNTING RULE ──
def count_syllables(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    true_vowels = set('aeiou')
    vowel_positions = set()
    for i, ch in enumerate(w):
        if ch in true_vowels:
            vowel_positions.add(i)
        elif ch in 'yw':
            left_is_vowel = (i > 0 and w[i-1] in true_vowels)
            right_is_vowel = (i < len(w)-1 and w[i+1] in true_vowels)
            if left_is_vowel or right_is_vowel:
                vowel_positions.add(i)
    if not vowel_positions:
        return 1
    sorted_pos = sorted(vowel_positions)
    groups = 1
    for i in range(1, len(sorted_pos)):
        if sorted_pos[i] != sorted_pos[i-1] + 1:
            groups += 1
    c = groups
    if w.endswith('e') and c >= 2:
        c -= 1
    return max(c, 1)

# ── PART 1.3: CPP AND ARITHMETIC ──
def digital_root(n):
    n = abs(int(n))
    if n == 0:
        return 9
    return 1 + (n - 1) % 9

def cpp(n):
    return digital_root(5 * n)

# ── STEP 3: THREE ENCODINGS ──
def compute_encodings(content_words):
    n1 = len(content_words)
    n2 = sum(len(letters_only(w)) for w in content_words)
    n3 = sum(count_syllables(w) for w in content_words)
    return n1, n2, n3

# ── STEP 5: ANCHOR DETERMINATION ──
def determine_anchor(n1, n2, n3):
    r1, r2, r3 = cpp(n1), cpp(n2), cpp(n3)
    votes = Counter([r1, r2, r3])
    top, freq = votes.most_common(1)[0]
    anchor = top if freq >= 2 else r1
    tfi_val = 0.00 if freq == 3 else (0.67 if freq == 2 else 1.00)
    return anchor, r1, r2, r3, tfi_val

# ── PART 1.6: TYPED COORDINATES; ACS (Part 3.4) ──
def typed(index):
    """Part 1.6 typed notation: position P, index i(P), orbit value v(P), character c(P)."""
    i = index % 24
    return {'P': 'P%d' % i, 'i': i, 'v': ORBIT[i], 'c': POSITION_NAMES[i]}

def acs(anchor_index, echo_index):
    """ACS = 1 - |v_S - v_A| / 8 on orbit VALUES: v_A = v(antipode of the anchor), v_S = v(echo anchor).
    Indices never enter the formula."""
    v_a = ORBIT[(anchor_index + 12) % 24]
    v_s = ORBIT[echo_index % 24]
    return round(1 - abs(v_s - v_a) / 8, 3), v_a, v_s

def acs_chance(anchor_index):
    """Expected ACS if the echo anchor were drawn uniformly from P1-P9 (the uniform reference)."""
    return round(sum(acs(anchor_index, e)[0] for e in range(1, 10)) / 9, 3)

def acs_block(anchor_index, echo_index):
    score, v_a, v_s = acs(anchor_index, echo_index)
    a, e, ap = typed(anchor_index), typed(echo_index), typed(anchor_index + 12)
    return "\n".join([
        "======= ACS OPERAND CHECK =======",
        f"ANCHOR: {a['P']} | i={a['i']} | v={a['v']} | c={a['c']}",
        f"ANTIPODE: {ap['P']} | i={ap['i']} | v_A = v({ap['P']}) = {v_a}",
        f"ECHO ANCHOR: {e['P']} | i={e['i']} | v_S = v({e['P']}) = {v_s}",
        f"ACS = 1 - |{v_s} - {v_a}| / 8 = {score:.3f}",
        f"CHANCE LEVEL (echo uniform over P1-P9): {acs_chance(anchor_index):.3f}",
        "======= END ACS OPERAND CHECK =======",
    ])

# ── STEP 7: ARM DERIVATION ──
def derive_arms(anchor):
    yang_i = (anchor + 5) % 24
    yin_i = (anchor + 18) % 24
    fourd_i = (anchor + 8) % 24
    antipode_i = (anchor + 12) % 24
    return yang_i, yin_i, fourd_i, antipode_i

def orbit_value(index):
    return ORBIT[index % 24]

# ── STEP 8: CCD / PAB ──
def is_crown(idx):
    return (idx - 3) % 4 == 0

def compute_ccd(anchor, yang_i, yin_i, fourd_i):
    crown_count = sum(is_crown(i) for i in [anchor, yang_i, yin_i, fourd_i])
    return crown_count / 4

# ── STEP 9: MOBIUS CHECK ──
def is_mobius(yang_i, yin_i, fourd_i):
    return any(18 <= i <= 23 for i in [yang_i, yin_i, fourd_i])

# ── FULL NAVIGATION PIPELINE ──
def spec_gaps(domain_text):
    """Out-of-scope forms found in the domain (Part 1.13, Step 1.5a), reported so the Navigator can mark them."""
    found = []
    for m in re.finditer(r'(?<![\w/])(\d+)/(\d+)(?![\w/])', domain_text):
        if int(m.group(2)) > 99:
            found.append("NCF-SPEC-GAP-ORDINAL")
    for m in re.finditer(r'\b(\d+)(?:st|nd|rd|th)\b', domain_text):
        if int(m.group(1)) >= 100:
            found.append("NCF-SPEC-GAP-ORDINAL")
    return sorted(set(found))

def navigate(domain_text):
    normalized = spnp(domain_text)
    content = extract_content_words(normalized)
    n1, n2, n3 = compute_encodings(content)
    anchor, r1, r2, r3, tfi = determine_anchor(n1, n2, n3)
    yang_i, yin_i, fourd_i, antipode_i = derive_arms(anchor)
    ccd = compute_ccd(anchor, yang_i, yin_i, fourd_i)
    pab = ccd <= 0.25
    mobius = is_mobius(yang_i, yin_i, fourd_i)
    return dict(
        domain=domain_text, normalized=normalized, content=content,
        n1=n1, n2=n2, n3=n3, r1=r1, r2=r2, r3=r3,
        anchor=anchor, anchor_value=orbit_value(anchor), anchor_name=POSITION_NAMES[anchor],
        tfi=tfi, yang_i=yang_i, yin_i=yin_i, fourd_i=fourd_i, antipode_i=antipode_i,
        ccd=ccd, pab=pab, mobius=mobius, gaps=spec_gaps(domain_text),
    )

# ── L-414: DOMAIN SHA-256 ──
def canonical_domain_form(domain_text):
    """L-414 / L-348: the form the domain hash is taken over. Unicode NFC, every run of
    whitespace collapsed to one space, ends trimmed, case-folded -- exactly the differences
    L-348 permits between two verbatim copies, and nothing more."""
    t = unicodedata.normalize('NFC', domain_text)
    t = re.sub(r'\s+', ' ', t).strip()
    return t.casefold()

def domain_sha256(domain_text):
    return hashlib.sha256(canonical_domain_form(domain_text).encode('utf-8')).hexdigest()

def substrate_sha256(content_words):
    """L-415: SHA-256 of a LOCKED SUBSTRATE line, the content words joined by ' * ' in order."""
    return hashlib.sha256(' * '.join(content_words).encode('utf-8')).hexdigest()

# ── L-417: SCRIPT SHA-256 ──
def script_sha256(path=None):
    """L-417: SHA-256 of this script's own source, taken over a canonical form (line endings
    as LF, trailing whitespace removed from every line, trailing blank lines removed) so that
    copying the script out of the document on different systems does not change the hash."""
    path = path or __file__
    with open(path, encoding='utf-8') as f:
        src = f.read()
    lines = [ln.rstrip() for ln in src.replace('\r\n', '\n').replace('\r', '\n').split('\n')]
    while lines and not lines[-1]:
        lines.pop()
    return hashlib.sha256('\n'.join(lines).encode('utf-8')).hexdigest()

# ── M269 / M271: MATHEMATICAL MARKERS ──
MATH_MARKER_CHARS = ('=+\u2212\u00d7\u00f7<>\u2264\u2265\u2211\u222b\u2202\u2282\u2208\u2209\u222a\u2229'
                     '\u221a\u221e\u211d\u2102\u2124\u211a\u2115_^'
                     + ''.join(SUPERSCRIPT_MAP) + ''.join(SUBSCRIPT_MAP))
LATEX_COMMAND = re.compile(r'\\[A-Za-z]+')

def math_tokens(domain_text):
    """Whitespace-delimited tokens of the verbatim domain that carry a mathematical marker
    (M269 trigger list): a marker character, a LaTeX command, or an isolated Greek letter."""
    out = []
    for tok in domain_text.split():
        if (any(c in MATH_MARKER_CHARS for c in tok) or LATEX_COMMAND.search(tok)
                or expand_isolated_greek(tok) != tok):
            out.append(tok)
    return out

def m269_rules(tok):
    rules = []
    if decode_character_references(tok) != tok:
        rules.append('1.12(6) character reference decoded')
    if any(c in SUPERSCRIPT_MAP or c in SUBSCRIPT_MAP for c in tok):
        rules.append('1.12(7) Unicode sub/superscript flattened')
    if '_' in tok or '^' in tok:
        rules.append('1.12(7) _ or ^ marker -> separator')
    if expand_isolated_greek(flatten_scripts(tok)) != flatten_scripts(tok):
        rules.append('1.12(8) isolated Greek letter -> name')
    if LATEX_COMMAND.search(tok):
        rules.append('1.12(9) LaTeX command name retained')
    if re.search('[' + re.escape('=+\u2212\u00d7\u00f7<>\u2264\u2265\u2211\u222b\u2202\u2282\u2208\u2209\u222a\u2229\u221a\u221e\u211d\u2102\u2124\u211a\u2115\u0394') + ']', tok):
        rules.append('1.12(2) operator stripped')
    return rules or ['1.12(1) punctuation only']

def m269_audit(domain_text):
    lines = ['======= M269 MATHEMATICAL DOMAIN EXTRACTION AUDIT TRAIL =======',
             f'DOMAIN SHA-256: {domain_sha256(domain_text)}']
    toks = math_tokens(domain_text)
    lines.append(f'MATHEMATICAL MARKERS DETECTED: {len(toks)}')
    lines.append('AUDIT TRAIL:')
    retained = 0
    for i, tok in enumerate(toks, 1):
        words = extract_content_words(spnp(tok))
        retained += len(words)
        lines.append(f"{i}. Original: {tok} | Transformation: {'; '.join(m269_rules(tok))} | "
                     f"Result: {' * '.join(words) if words else '(none)'}")
    lines.append(f'TOTAL MATHEMATICAL TOKENS PROCESSED: {len(toks)}')
    lines.append(f'TOTAL CONTENT WORDS RETAINED FROM MATH: {retained}')
    lines.append('======= END M269 MATHEMATICAL DOMAIN EXTRACTION AUDIT TRAIL =======')
    return '\n'.join(lines)

def m271_tier(domain_text):
    """M271 Domain Complexity Tier. Tier 3: n1 > 500, or any LaTeX command, or 10 or more
    mathematical tokens. Tier 2: n1 of 200 to 500, or 1 to 9 mathematical tokens.
    Tier 1: everything else."""
    n1 = navigate(domain_text)['n1']
    m = len(math_tokens(domain_text))
    latex = bool(LATEX_COMMAND.search(domain_text))
    if n1 > 500 or latex or m >= 10:
        tier = 3
    elif n1 >= 200 or m >= 1:
        tier = 2
    else:
        tier = 1
    return tier, n1, m, latex

# ── PART 3.21: DERIVED QUANTITY KNOWN-ANSWER SET ──
def m115_distance(a, b):
    """M115: distance between two anchors on the 24-cycle (anchors lie in 1-9, so the result is 0-8)."""
    d = abs(a - b) % 24
    return min(d, 24 - d)

def crs(anchor):
    """CRS: Crown-class positions among the anchor and its four arms (Yang, Yin, 4D, Antipode), over 5."""
    return round(sum(is_crown(i) for i in (anchor,) + derive_arms(anchor)) / 5, 2)

def mobius_active(anchor):
    yang_i, yin_i, fourd_i, _ = derive_arms(anchor)
    return any(18 <= i <= 23 for i in (yang_i, yin_i, fourd_i))

def pab_active(anchor):
    yang_i, yin_i, fourd_i, _ = derive_arms(anchor)
    return compute_ccd(anchor, yang_i, yin_i, fourd_i) <= 0.25

def sas(orig_anchor, echo_anchor):
    """M209 SAS = 0.50 AE + 0.35 AMF + 0.15 CC, with arm distances measured on the 24-cycle."""
    ae = 1.0 if orig_anchor == echo_anchor else 0.0
    oa, ea = derive_arms(orig_anchor)[:3], derive_arms(echo_anchor)[:3]
    d = sum(min(abs(x - y), 24 - abs(x - y)) for x, y in zip(oa, ea))
    amf = max(0.0, 1 - d / 36)
    cc = 0.6 * (mobius_active(orig_anchor) == mobius_active(echo_anchor)) + 0.4 * (pab_active(orig_anchor) == pab_active(echo_anchor))
    return round(0.50 * ae + 0.35 * amf + 0.15 * cc, 4)

def sri(tfi, cm, sas_v, acs_v, cfr):
    """SRI = 0.20(1 - TFI) + 0.25 CM + 0.20 SAS + 0.15 ACS + 0.20 CFR."""
    return round(0.20 * (1 - tfi) + 0.25 * cm + 0.20 * sas_v + 0.15 * acs_v + 0.20 * cfr, 5)

DERIVED_KNOWN_ANSWERS = (
    # (label, computed value, expected value)
    ("M115 distance P7-P6", lambda: m115_distance(7, 6), 1),
    ("M115 distance P7-P2", lambda: m115_distance(7, 2), 5),
    ("M115 distance P1-P9", lambda: m115_distance(1, 9), 8),
    ("CRS anchor P2", lambda: crs(2), 0.2),
    ("CRS anchor P3", lambda: crs(3), 0.6),
    ("CCD/PAB anchor P2", lambda: pab_active(2), True),
    ("CCD/PAB anchor P3", lambda: pab_active(3), False),
    ("Mobius anchor P2", lambda: mobius_active(2), True),
    ("Mobius anchor P9", lambda: mobius_active(9), False),
    ("SAS identical echo P5", lambda: sas(5, 5), 1.0),
    ("SAS P9 -> echo P3", lambda: sas(9, 3), 0.175),
    ("SRI (TFI 1.00, CM 0.75, SAS 0.175, ACS 0.875, CFR 0)", lambda: sri(1.0, 0.75, 0.175, 0.875, 0.0), 0.35375),
    ("SRI all maximal", lambda: sri(0.0, 1.0, 1.0, 1.0, 1.0), 1.0),
)

# ── M267-T: TEMPORAL DECOY (frozen rule; L-430) ──
import datetime as _dt

def temporal_decoy(utc_date, true_anchor):
    """Date-derived decoy anchor for M267 (Companion 32.4): D = day of the year of the SUBSTRATE_LOCKED
    temporal anchor's UTC date; decoy = P(1 + D mod 9); if that equals the true anchor, P(1 + (D + 1) mod 9).
    Frozen before outcomes are seen; a control, never a reading."""
    d = _dt.date.fromisoformat(utc_date).timetuple().tm_yday
    dec = 1 + d % 9
    if dec == true_anchor:
        dec = 1 + (d + 1) % 9
    return dec

# ── M230-A: RESONANCE LEDGER (frozen lists; Part 3.26) ──
M230A_TIER2_VALUES = (24, 9, 7, 6, 42)   # period; modulus and antipodal sum; the Aperture's denominator; Torsion Loop size; D = 6 x 7
M230A_TIER3_FEATURES = (
    "a: Torsion/Crown partition - distinguished states split into a six-element reversible cycle and a three-element collapsing set",
    "b: antipodal complementarity - 24 distinguished elements in 12 pairs whose members are additive inverses",
    "c: half-period negation - in a cyclic order of the elements, a shift by half the period maps each element to its inverse",
    "d: absent-fixed-point cycling - the system cycles because no attracting fixed point is available in its state space (Fact 6)",
    "e: shared generating recurrence - the object's counts follow x(n+2) = x(n+1) + x(n)",
)
M230A_COUNTING_FEATURE = {
    "polytope": "vertex count", "lattice": "dimension", "group": "order",
    "tiling": "order of its characteristic rotational symmetry", "diffraction pattern": "order of its rotational symmetry",
    "tuning system": "steps per octave", "time division": "units per cycle",
    "dynamical system": "number of state variables in its standard model",
}

def m230a_entry(count):
    """Tier 1 (placement, always) and tier 2 (count in the frozen value list). Tiers 3 and 4 are assessed
    against M230A_TIER3_FEATURES and recorded with their reason; they are not computable from a count."""
    pos = cpp(count)
    return {"count": count, "placement": f"P{pos}", "orbit_value": ORBIT[pos], "tier2": count in M230A_TIER2_VALUES}

def m230i_sensitivity(counts):
    """M230-I Representation Sensitivity Audit: placements of every admissible representation of one object,
    and the number of distinct positions they occupy. A spread of 1 means the placement is representation-robust."""
    placements = [f"P{cpp(c)}" for c in counts]
    return {"counts": list(counts), "placements": placements, "distinct": len(set(placements))}

def m230a_base_rate(upper=48):
    """Share of counts 1..upper that land in the frozen tier-2 list: the uniform base rate."""
    return round(sum(1 for n in range(1, upper + 1) if n in M230A_TIER2_VALUES) / upper, 4)

# ── M230-B / M230-C: STRUCTURAL AND GENERATIVE CORRESPONDENCE TESTS (Part 3.26) ──
def _cycle_type(perm):
    seen, ct = set(), []
    for i in range(len(perm)):
        if i in seen:
            continue
        c, j = 0, i
        while j not in seen:
            seen.add(j); j = perm[j]; c += 1
        ct.append(c)
    return tuple(sorted(ct, reverse=True))

def omega_full_cycle_type():
    """Cycle type of the transition T(a,b) = (b, a+b mod 9) on all 81 states: the full-space signature."""
    nxt = {(a, b): (b, (a + b) % 9) for a in range(9) for b in range(9)}
    seen, ct = set(), []
    for s in nxt:
        if s in seen:
            continue
        c, x = 0, s
        while x not in seen:
            seen.add(x); x = nxt[x]; c += 1
        ct.append(c)
    return tuple(sorted(ct, reverse=True))

def cell24_symmetry_profile():
    """M230-C on the 24-cell: generate its symmetry group (the Weyl group of F4) from reflections in the F4 roots,
    acting on the 24 vertices; report the group order, element orders, whether any symmetry is a single 24-cycle,
    and whether every order-12 element's sixth power is the central inversion v -> -v."""
    from fractions import Fraction as Fr
    from itertools import product as _prod
    from math import lcm
    h = Fr(1, 2)
    V = []
    for i in range(4):
        for s in (1, -1):
            v = [Fr(0)] * 4; v[i] = Fr(s); V.append(tuple(v))
    V += [tuple(s) for s in _prod((h, -h), repeat=4)]
    idx = {v: i for i, v in enumerate(V)}
    R = list(V)
    for i in range(4):
        for j in range(i + 1, 4):
            for si, sj in _prod((1, -1), repeat=2):
                v = [Fr(0)] * 4; v[i] = Fr(si); v[j] = Fr(sj); R.append(tuple(v))
    dot = lambda a, b: sum(x * y for x, y in zip(a, b))
    gens = {tuple(idx[tuple(x - 2 * dot(v, r) / dot(r, r) * y for x, y in zip(v, r))] for v in V) for r in R}
    ident = tuple(range(24))
    comp = lambda p, q: tuple(p[q[i]] for i in range(24))
    G, frontier = {ident}, [ident]
    while frontier:
        nf = []
        for g in frontier:
            for s in gens:
                k = comp(s, g)
                if k not in G:
                    G.add(k); nf.append(k)
        frontier = nf
    neg = tuple(idx[tuple(-x for x in v)] for v in V)
    def pw(p, k):
        r = ident
        for _ in range(k):
            r = comp(p, r)
        return r
    orders = Counter(lcm(*_cycle_type(g)) for g in G)
    o12 = [g for g in G if lcm(*_cycle_type(g)) == 12]
    return {"order": len(G), "max_element_order": max(orders),
            "single_24_cycle": any(_cycle_type(g) == (24,) for g in G),
            "order12_cycle_types": sorted({_cycle_type(g) for g in o12}),
            "order12_sixth_power_is_inversion": all(pw(g, 6) == neg for g in o12),
            "inversion_cycle_type": _cycle_type(neg)}

def t2_profile():
    """T^2 on the canonical orbit: cycle type, and whether (T^2)^6 = T^12 negates every value (half-period negation)."""
    t2 = tuple((i + 2) % 24 for i in range(24))
    return {"cycle_type": _cycle_type(t2), "sixth_power_negates": all((ORBIT[i] + ORBIT[(i + 12) % 24]) % 9 == 0 for i in range(24))}

# ── PART 1.8: CANONICAL SELECTION (L-423) ──
def _dr(n):
    return 9 if n % 9 == 0 else n % 9

def fib_orbits():
    """All orbits of the Fibonacci map (a,b) -> (b, dr(a+b)) on the 81 digit pairs (9 standing for 0)."""
    seen, orbits = {}, []
    for a in range(1, 10):
        for b in range(1, 10):
            if (a, b) in seen:
                continue
            o, x = [], (a, b)
            while x not in o:
                o.append(x)
                x = (x[1], _dr(x[0] + x[1]))
            for y in o:
                seen[y] = len(orbits)
            orbits.append(o)
    return orbits, seen

def _reading(state):
    out, x = [], state
    for _ in range(24):
        out.append(x[0])
        x = (x[1], _dr(x[0] + x[1]))
    return out

CRITERIA_K = (
    "K1: the orbit has complete spectrum (takes all nine values 1-9); among Fibonacci orbits mod 9 this is exactly the period-24 orbits.",
    "K2: the reading starts at the state (P0, P1) = (g1, g2), the two primitive roots of (Z/9Z)x written in increasing order.",
)

def canonical_selection():
    """Part 1.8.4 witness: enumerate every (orbit, starting state) reading of the period-24 orbits, apply the frozen
    criteria K, and report survivors; then apply the stated alternative criterion sets (the adversarial test)."""
    orbits, seen = fib_orbits()
    roots = sorted(g for g in (1, 2, 4, 5, 7, 8) if len({pow(g, k, 9) for k in range(1, 7)}) == 6)
    names = {seen[(1, 1)]: 'Voice A', seen[(1, 3)]: 'Voice B', seen[(2, 5)]: 'Voice C'}
    cands = [(names[i], st) for i, o in enumerate(orbits) if len(o) == 24 for st in o]

    def dominant(name):
        o = orbits[[k for k, v in names.items() if v == name][0]]
        c = Counter(v for v, _ in o)
        return tuple(sorted(v for v in c if c[v] == max(c.values())))

    def crown_split(st):
        v = _reading(st)
        nil = [i for i in range(24) if v[i] in (3, 6, 9)]
        return (sum(1 for i in nil if i >= 18), sum(1 for i in nil if i < 18))

    sets = [
        ("K (frozen)", lambda n, st: len(set(_reading(st))) == 9 and st == (roots[0], roots[1])),
        ("K-alt-1 (primitive roots, decreasing order)", lambda n, st: len(set(_reading(st))) == 9 and st == (roots[1], roots[0])),
        ("K-alt-2 (dominant pair adjacent)", lambda n, st: abs(dominant(n)[0] - dominant(n)[1]) == 1),
        ("K-alt-3 (Crown split 2:4 against the P18-P23 zone)", lambda n, st: crown_split(st) == (2, 4)),
    ]

    def status(surv):
        if not surv:
            return 'NO SURVIVOR'
        if len(surv) == 1:
            return 'UNIQUE'
        if len({n for n, _ in surv}) == 1:
            return 'UNDERDETERMINED (orbit unique, starting state open)'
        return 'NON-UNIQUE'

    rows = []
    for label, f in sets:
        surv = [(n, st) for n, st in cands if f(n, st)]
        rows.append((label, len(surv), sorted({n for n, _ in surv}), surv[0] if len(surv) == 1 else None, status(surv)))
    table = [(n, dominant(n), abs(dominant(n)[0] - dominant(n)[1]) == 1) for n in ('Voice A', 'Voice B', 'Voice C')]
    lines = ["======= CANONICAL SELECTION WITNESS (Part 1.8.4, L-423) =======",
             "CANDIDATE SPACE: Fibonacci map on (Z/9Z)^2 | STATES: 81 | ORBITS: %d (periods %s)" % (
                 len(orbits), ', '.join(str(len(o)) for o in orbits)),
             "PERIOD-24 ORBITS: 3 | CANDIDATE READINGS (orbit, starting state): %d" % len(cands),
             "PRIMITIVE ROOTS OF (Z/9Z)x: %s" % roots]
    lines += ["CRITERIA (frozen): " + c for c in CRITERIA_K]
    for n, d, adj in table:
        lines.append("ORBIT %s: complete spectrum YES | dominant pair %s | adjacent %s" % (n, d, 'YES' if adj else 'NO'))
    for label, k, orbs, one, st in rows:
        lines.append("%s: survivors %d %s%s -> %s" % (label, k, orbs, (' at start %s' % (one[1],)) if one else '', st))
    body = "\n".join(lines)
    lines.append("SELECTION SHA-256: " + hashlib.sha256(body.encode('utf-8')).hexdigest())
    lines.append("======= END CANONICAL SELECTION WITNESS =======")
    return "\n".join(lines), rows

def half_period_negation():
    """FP-HalfPeriodNegation: twelve Fibonacci steps multiply every state by -1 mod 9."""
    ok = 0
    for a in range(9):
        for b in range(9):
            x = [a, b]
            for _ in range(30):
                x.append((x[-1] + x[-2]) % 9)
            ok += all((x[n] + x[n + 12]) % 9 == 0 for n in range(18))
    return ok

# ── M206: NEDA (Normalized Entropy-Density Axis) ──
def compute_neda(content_words):
    """M206: Shannon entropy H of the case-folded letter distribution of the content words, normalized by
    H_max = log2(26); position = min(9, max(1, floor(H_norm x 9) + 1)). A companion reading, never the anchor."""
    import math
    letters = "".join(re.sub(r"[^A-Za-z]", "", w).lower() for w in content_words)
    if not letters:
        return None
    freq = Counter(letters)
    n = len(letters)
    h = -sum((c / n) * math.log2(c / n) for c in freq.values())
    return min(9, max(1, int(min(h / math.log2(26), 1.0) * 9) + 1))

# ── M211: PRE-NAVIGATION CALIBRATION ──
CALIBRATION_DOMAIN = "The quick brown fox jumps over the lazy dog."
CALIBRATION_EXPECTED_ANCHOR = 3  # P3 (Desire)

def run_calibration(verbose=True):
    result = navigate(CALIBRATION_DOMAIN)
    anchor = result['anchor']
    passed = (anchor == CALIBRATION_EXPECTED_ANCHOR)
    if verbose:
        print("======= M211 PRE-NAVIGATION CALIBRATION =======")
        print(f"CALIBRATION DOMAIN: {CALIBRATION_DOMAIN}")
        print(f"EXPECTED ANCHOR: P{CALIBRATION_EXPECTED_ANCHOR} ({POSITION_NAMES[CALIBRATION_EXPECTED_ANCHOR]})")
        print(f"ACTUAL ANCHOR: P{anchor} ({POSITION_NAMES[anchor]})")
        print(f"  n=({result['n1']},{result['n2']},{result['n3']}) r=({result['r1']},{result['r2']},{result['r3']})")
        print(f"CALIBRATION: {'PASS' if passed else 'FAIL'}")
        print("======= END M211 PRE-NAVIGATION CALIBRATION =======")
    return passed, anchor

def generate_m210_table(content_words):
    lines = ["# | Word | Letters | Syllables", "-" * 45]
    total_letters = 0
    total_syllables = 0
    for i, word in enumerate(content_words, 1):
        letters = len(letters_only(word))
        syllables = count_syllables(word)
        total_letters += letters
        total_syllables += syllables
        lines.append(f"{i:<3} | {word:<14} | {letters:>7} | {syllables:>9}")
    lines.append("-" * 45)
    n1 = len(content_words)
    lines.append(f"TOTALS: n1={n1} words, n2={total_letters} letters, n3={total_syllables} syllables")
    lines.append(f"M268 ROWS: {len(content_words)} | n1: {n1} | MATCH: {'YES' if len(content_words) == n1 else 'NO'}")
    return "\n".join(lines)

def math_gate():
    """MATH-GATE (Part 1.14, L-451): reconstruct the mathematical ground from first principles.
    Returns [(check, passed, detail)]. Every check is recomputed over Z/9Z; none reads ORBIT as given."""
    T = lambda s: (s[1], (s[0] + s[1]) % 9)
    states = [(a, b) for a in range(9) for b in range(9)]
    orbit_of, orbits = {}, []
    for s in states:
        if s in orbit_of:
            continue
        o, t = [s], T(s)
        while t != s:
            o.append(t)
            t = T(t)
        for u in o:
            orbit_of[u] = len(orbits)
        orbits.append(o)
    periods = sorted(len(o) for o in orbits)
    seq, s = [], (2, 5)
    for _ in range(24):
        seq.append(s[0] or 9)
        s = T(s)
    def power(s, n):
        for _ in range(n):
            s = T(s)
        return s
    N = lambda a, b: (a * a + a * b - b * b) % 9      # norm form of a + b*phi in Z[phi]/9
    p24 = [o for o in orbits if len(o) == 24]
    norm_classes = sorted(sorted({N(a, b) for a, b in o}) for o in p24)
    kernel = sorted(u for u in states if N(*u) == 0)
    p11 = sorted(u for u in states if power(u, 11)[0] == 6)
    out = []
    add = lambda name, ok, detail: out.append((name, bool(ok), detail))
    add("1 ring R = Z/9Z, residue 0 displayed as 9", (9 % 9) == 0, "9 residues")
    add("2 T(a,b) = (b, a+b mod 9) is a bijection (det = -1)", len({T(u) for u in states}) == 81, "81 images")
    add("3 state space |R^2| = 81", len(states) == 81, "81 states")
    add("4 period structure: every state periodic, no transients", sum(periods) == 81, "sum of cycle lengths 81")
    add("5 orbit census 1 + 8 + 24 + 24 + 24", periods == [1, 8, 24, 24, 24], str(periods))
    add("6 three period-24 orbits = 72 states", len(p24) == 3, "72 period-24 states, 8 period-8, 1 fixed")
    add("7 (2,5) lies on a period-24 orbit and regenerates ORBIT", seq == ORBIT, " ".join(map(str, seq)))
    add("8 P11 = 6 on the canonical reading", seq[11] == 6, "property, not selector: 9 states have P11 = 6, two on each period-24 orbit")
    add("8b P11 = 6 census", len(p11) == 9 and all(sum(1 for u in o if u in p11) == 2 for o in p24), str(p11))
    add("9 T^12 = -I on all 81 states, T^24 = I", all(power(u, 12) == ((-u[0]) % 9, (-u[1]) % 9) for u in states), "half-turn inversion")
    add("10 positions 3,7,11,15,19,23 carry 3,9,6,6,9,3", [seq[i] for i in (3, 7, 11, 15, 19, 23)] == [3, 9, 6, 6, 9, 3], "sixfold partition 6 x 4 = 24")
    add("11 G = 6 nilpotent (36 = 0 mod 9); nilpotent residues 3, 6, 0", [x for x in range(9) if (x * x) % 9 == 0] == [0, 3, 6], "6^2 = 36")
    add("12 x^2 = x + 1 has no root in Z/9Z", not [x for x in range(9) if (x * x - x - 1) % 9 == 0], "5 is not a square mod 9")
    add("13 norm form N = a^2 + ab - b^2: N(T s) = -N(s)", all(N(*T(u)) == (-N(*u)) % 9 for u in states), "Cassini invariant")
    add("13b norm classes separate the three orbits", norm_classes == [[1, 8], [2, 7], [4, 5]] and len(kernel) == 9, "canonical orbit N = {2,7}; kernel N = 0 holds 9 states")
    c_orbit = next(o for o in p24 if (2, 5) in o)
    n2 = sorted(u for u in states if N(*u) in (2, 7))
    add("13c N = +-2 is a post-selection invariant: it names the canonical orbit (24 states) and no starting state",
        n2 == sorted(c_orbit) and sum(1 for u in c_orbit if N(*u) == 7) == 12 and N(2, 5) == 7, "N(2,5) = -2; selector remains K")
    add("13d norm class = square of the Voice scale (1, 2, 4 -> 1, 4, 7)", [(c * c) % 9 for c in (1, 2, 4)] == [1, 4, 7], "FP-ScalarUnity")
    sel = canonical_selection()
    add("14 canonical status: frozen criteria K select (2,5) uniquely", sel[1][0][4] == 'UNIQUE', "Part 1.8.4 witness")
    add("15 42 = 2 x 24 - G", 2 * 24 - 6 == 42, "48 - 6")
    return out

def math_gate_block():
    rows = math_gate()
    lines = ["======= MATH-GATE (Part 1.14, L-451) ======="]
    for name, ok, detail in rows:
        lines.append(f"[{'PASS' if ok else 'FAIL'}] {name} | {detail}")
    lines.append(f"MATH-GATE: {'PASS' if all(r[1] for r in rows) else 'FAIL'} ({sum(r[1] for r in rows)}/{len(rows)})")
    lines.append("======= END MATH-GATE =======")
    return "\n".join(lines)

# Exposed Domain Register (Core Part 8.0, L-459): domains whose coordinates or readings appear in the
# protocol's own text. A navigation of one declares EXPOSED DOMAIN: YES and is excluded from convergence evidence.
EXPOSED_DOMAINS = (
    "The quick brown fox jumps over the lazy dog.",
    "What is the Human Condition?",
    "What is the human condition, exactly?",
    "Human Condition",
)

def is_exposed(domain_text):
    key = domain_sha256(domain_text)
    return any(domain_sha256(d) == key for d in EXPOSED_DOMAINS)

def selection_sha256():
    for line in canonical_selection()[0].split("\n"):
        if line.startswith("SELECTION SHA-256: "):
            return line.split(": ", 1)[1]

def navigation_block(domain_text, alt=None, session_index=1):
    """Part 8.0 skeleton, arithmetic sections: every value EXECUTED by this script (L-456).
    The Navigator pastes this block verbatim and writes only the synthesis sections."""
    r = navigate(domain_text)
    gate = math_gate()
    cal_ok, cal_anchor = run_calibration(verbose=False)
    tokens = extract_words(spnp(domain_text))
    removed = [w for w in tokens if w.lower() in CANONICAL_STOPWORDS]
    a = r['anchor']
    arms = [("Yang", r['yang_i']), ("Yin", r['yin_i']), ("4D", r['fourd_i']), ("Antipode", r['antipode_i'])]
    v_a, v_ap = ORBIT[a], ORBIT[r['antipode_i']]
    L = []
    L.append("EXECUTION STATUS: EXECUTED (canonical_reference.py --navigate) | SCRIPT SHA-256: " + script_sha256())
    L.append("SESSION NAVIGATION: %d" % session_index)
    L.append("[1] MATH-GATE: %s (FULL, %d/%d checks)" % ("PASS" if all(x[1] for x in gate) else "FAIL", sum(x[1] for x in gate), len(gate)))
    L.append("[2] M211 CALIBRATION: %s | expected P%d | actual P%d" % ("PASS" if cal_ok else "FAIL", CALIBRATION_EXPECTED_ANCHOR, cal_anchor))
    L.append("[3] M272 FRAME LOCK: written by the Navigator (Step 0.5)")
    L.append("[4] SUBSTRATE LOCK")
    L.append("    DOMAIN VERBATIM: " + domain_text)
    L.append("    DOMAIN SHA-256: " + domain_sha256(domain_text))
    L.append("    FUNCTION WORDS REMOVED: " + (", ".join(removed) if removed else "none"))
    L.append("    LOCKED SUBSTRATE: " + " * ".join(r['content']))
    L.append("    SUBSTRATE SHA-256: " + substrate_sha256(r['content']))
    L.append("    CANONICAL SUBSTRATE: Voice C read from (2, 5), canonically unique under K (Part 1.8.4)")
    L.append("    SELECTION SHA-256: " + selection_sha256())
    L.append("    GAPS: " + (" * ".join(r['gaps']) if r['gaps'] else "none"))
    L.append("    EXPOSED DOMAIN: " + ("YES (Exposed Domain Register, L-459): declare PROTOCOL-TEXT ECHO; not convergence evidence" if is_exposed(domain_text) else "NO"))
    L.append("[5] M210 EXTRACTION TABLE")
    L.extend("    " + x for x in generate_m210_table(r['content']).split("\n"))
    L.append("[6] ENCODING AND ANCHOR")
    L.append("    n = (%d, %d, %d) | r = (%d, %d, %d) | ANCHOR P%d (%s), v = %d | TFI = %.2f%s" % (
        r['n1'], r['n2'], r['n3'], r['r1'], r['r2'], r['r3'], a, POSITION_NAMES[a], v_a, r['tfi'],
        " (tie-break to r1)" if r['tfi'] == 1.0 else ""))
    L.append("[7] ARMS")
    for name, i in arms:
        L.append("    %-8s P%-2d %-14s v = %d%s" % (name, i, POSITION_NAMES[i], ORBIT[i], " | CROWN" if is_crown(i) else ""))
    L.append("    M88 CHECKSUM: dr(%d + %d) = %d -> %s" % (v_a, v_ap, _dr(v_a + v_ap), "PASS" if _dr(v_a + v_ap) == 9 else "FAIL"))
    L.append("[8] CCD = %.2f -> PAB %s | MOBIUS %s | RPI %s | CRS = %.2f" % (
        r['ccd'], "ACTIVE" if r['pab'] else "INACTIVE", "ACTIVE" if r['mobius'] else "INACTIVE",
        "ACTIVE" if 18 <= r['antipode_i'] <= 23 else "INACTIVE", crs(a)))
    if alt:
        ra = navigate(alt)
        same = ra['anchor'] == a
        L.append("[9] M116 ALTERNATIVE PHRASING: \"%s\" -> P%d | %s | CFR (1 alternative) = %.2f" % (
            alt, ra['anchor'], "SAME ANCHOR" if same else "DIFFERENT ANCHOR", 1.0 if same else 0.0))
    else:
        L.append("[9] M116 ALTERNATIVE PHRASING: NOT COMPUTED (no alternative supplied; rerun with --alt)")
    stab = []
    stab.append("tie-break anchor" if r['tfi'] == 1.0 else ("majority anchor" if r['tfi'] == 0.67 else "unanimous anchor"))
    if alt:
        stab.append("phrasing-stable" if same else "phrasing-sensitive (P%d -> P%d)" % (a, ra['anchor']))
    L.append("    STABILITY: " + ", ".join(stab))
    L.append("[10..] SYNTHESIS SECTIONS: written by the Navigator; M209 echo by --echo")
    return "\n".join(L)

# M209 worked-example fixture: a constructed text about no navigated domain (Core Part 8.0, L-459).
_FIXTURE_CORE = ("The harbour wall was built in the spring of a dry year. Stone was carried down from the quarry on the hill, "
                 "one cart at a time, and each block was set by hand. The masons worked from the north end toward the lighthouse.")
_FIXTURE_REST = ("By autumn the wall reached the lighthouse, and the boats tied up behind it for the first winter. "
                 "The town kept a record of every block that was laid.")

def echo_block(answer_text, anchor, core_text=None):
    """M209 synthesis echo, EXECUTED. Input: the full THE ANSWER text between its delimiters (Part 3.8).
    With core_text, the Core Synthesis echo (M209-C) is reported beside it as a secondary diagnostic."""
    def one(label, text):
        e = navigate(text)
        ea = e['anchor']
        score, v_a, v_s = acs(anchor, ea)
        return [
            "%s: n = (%d, %d, %d) | r = (%d, %d, %d) | ECHO ANCHOR P%d | TFI = %.2f" % (label, e['n1'], e['n2'], e['n3'], e['r1'], e['r2'], e['r3'], ea, e['tfi']),
            "    ECHO CLOSURE: %s | SAS = %.4f | ACS = 1 - |%d - %d| / 8 = %.3f | CHANCE LEVEL %.3f" % (
                "YES" if ea == anchor else "NO", sas(anchor, ea), v_s, v_a, score, acs_chance(anchor)),
        ]
    lines = ["======= M209 SYNTHESIS ECHO (EXECUTED) ======="]
    lines += one("M209 (THE ANSWER)", answer_text)
    if core_text:
        lines += one("M209-C (Core Synthesis, diagnostic)", core_text)
    lines.append("======= END M209 SYNTHESIS ECHO =======")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    print(f"SCRIPT SHA-256: {script_sha256()}")   # L-417: printed on every run
    if sys.argv[1] == "--version":
        sys.exit(0)
    elif sys.argv[1] == "--navigate":
        args = sys.argv[2:]
        alt = None; idx = 1
        if "--alt" in args:
            k = args.index("--alt"); alt = args[k + 1]; args = args[:k] + args[k + 2:]
        if "--session" in args:
            k = args.index("--session"); idx = int(args[k + 1]); args = args[:k] + args[k + 2:]
        print(navigation_block(" ".join(args), alt, idx))
        sys.exit(0)
    elif sys.argv[1] == "--echo":
        args = sys.argv[3:]
        core = None
        if "--core" in args:
            k = args.index("--core"); core = args[k + 1]; args = args[:k] + args[k + 2:]
        print(echo_block(" ".join(args), int(sys.argv[2]), core))
        sys.exit(0)
    elif sys.argv[1] == "--mathgate":
        print(math_gate_block())
        sys.exit(0 if all(r[1] for r in math_gate()) else 1)
    elif sys.argv[1] == "--m230i":
        r = m230i_sensitivity([int(x) for x in sys.argv[2:]])
        print(f"M230-I: counts {r['counts']} -> placements {r['placements']} | distinct positions: {r['distinct']}")
        sys.exit(0)
    elif sys.argv[1] == "--m230c-24cell":
        p = cell24_symmetry_profile(); t = t2_profile()
        print(f"M230-C 24-CELL: symmetry group order {p['order']} | max element order {p['max_element_order']} | single 24-cycle: {'YES' if p['single_24_cycle'] else 'NO'}")
        print(f"  order-12 cycle types {p['order12_cycle_types']} | sixth power = central inversion: {'YES' if p['order12_sixth_power_is_inversion'] else 'NO'}")
        print(f"  Omega42 T^2 on canonical orbit: cycle type {t['cycle_type']} | (T^2)^6 negates values: {'YES' if t['sixth_power_negates'] else 'NO'}")
        print(f"  Omega42 T on all 81 states: cycle type {omega_full_cycle_type()} | mapping freedom for f.c = T^2.f: {12 * 12 * 2}")
        sys.exit(0)
    elif sys.argv[1] == "--m230a":
        e = m230a_entry(int(sys.argv[2]))
        print(f"M230-A: count={e['count']} placement={e['placement']} (v={e['orbit_value']}) tier2={'YES' if e['tier2'] else 'NO'} | base rate (1-48)={m230a_base_rate()}")
        sys.exit(0)
    elif sys.argv[1] == "--neda":
        content = extract_content_words(spnp(" ".join(sys.argv[2:])))
        print(f"NEDA (M206): P{compute_neda(content)}")
        sys.exit(0)
    elif sys.argv[1] == "--canonical-selection":
        print(canonical_selection()[0])
        sys.exit(0)
    elif sys.argv[1] == "--acs":
        print(acs_block(int(sys.argv[2]), int(sys.argv[3])))
        sys.exit(0)
    elif sys.argv[1] == "--hash":
        print(f"DOMAIN SHA-256: {domain_sha256(' '.join(sys.argv[2:]))}")
        sys.exit(0)
    elif sys.argv[1] == "--m269":
        print(m269_audit(" ".join(sys.argv[2:])))
        sys.exit(0)
    elif sys.argv[1] == "--complexity":
        tier, n1, m, latex = m271_tier(" ".join(sys.argv[2:]))
        print(f"M271 COMPLEXITY TIER: {tier} | n1={n1} | MATHEMATICAL TOKENS={m} | LATEX={'YES' if latex else 'NO'}")
        sys.exit(0)
    if sys.argv[1] == "--calibrate":
        passed, anchor = run_calibration(verbose=True)
        sys.exit(0 if passed else 1)
    elif sys.argv[1] == "--m210":
        domain_text = " ".join(sys.argv[2:])
        normalized = spnp(domain_text)
        content = extract_content_words(normalized)
        print("======= M210 EXTRACTION VERIFICATION =======")
        print(generate_m210_table(content))
        print("======= END M210 EXTRACTION VERIFICATION =======")
    elif sys.argv[1] == "--test":
        test_cases = [
            ("The quick brown fox jumps over the lazy dog.", 3, "Calibration domain"),
        ]
        # Part 1.12 (6)-(9) frozen worked examples: (verbatim, expected content words)
        token_cases = [
            ("\\theta_i", ["theta", "i"]), ("\u03b8_i", ["theta", "i"]), ("\u03b8\u1d62", ["theta", "i"]),
            ("x\u00b2", ["x", "two"]), ("x^2", ["x", "two"]), ("x\u00b2\u00b3", ["x", "twenty", "three"]),
            ("A_1 B_2", ["one", "B", "two"]), ("M^N c_U", ["M", "N", "c", "U"]),
            ("\\sum_f", ["sum", "f"]), ("\\frac{M-1}{M}", ["frac", "M", "one", "M"]),
            ("\\lim_{n \\to \\infty}", ["lim", "n", "infty"]), ("R &amp; D", ["R", "D"]),
            ("\u0394x", ["x"]), ("2\u03c0 r", ["two", "pi", "r"]), ("\u03bb\u03cc\u03b3\u03bf\u03c2", []),
            ("input space X of size N", ["input", "space", "X", "size", "N"]),
            ("Photosystem II and chapter XIV", ["Photosystem", "two", "chapter", "fourteen"]),
            ("did civil mild LLM CCD xi IIII", ["did", "civil", "mild", "LLM", "CCD", "xi", "IIII"]),
            ("\u03be", ["xi"]),
        ]
        all_pass = True
        for domain, expected_words in token_cases:
            got = extract_content_words(spnp(domain))
            ok = got == expected_words
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] Part 1.12 example {domain!r} -> {got}")
        # ACS known-answer set (Part 3.4), including index/value collisions
        for (anc, echo, want) in ((1, 8, 0.875), (1, 4, 0.625), (7, 7, 1.0), (7, 4, 0.0), (5, 5, 0.875), (5, 1, 1.0)):
            got = acs(anc, echo)[0]
            ok = abs(got - want) < 1e-9
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] ACS anchor P{anc}, echo P{echo} -> {got:.3f} (expected {want:.3f})")
        ok = (acs_chance(7), acs_chance(5)) == (0.486, 0.819)
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] ACS chance levels P7 {acs_chance(7)}, P5 {acs_chance(5)}")
        # Part 3.21: derived quantity known-answer set
        for label, f, want in DERIVED_KNOWN_ANSWERS:
            got = f()
            ok = (abs(got - want) < 1e-9) if isinstance(want, float) else (got == want)
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] {label}: {got} (expected {want})")
        # L-430: temporal decoy (frozen rule) and temporal invariance of the coordinate
        for (day, true_a, want) in (("2026-10-03", 5, 7), ("2026-10-03", 7, 8), ("2026-01-01", 3, 2)):
            got = temporal_decoy(day, true_a)
            ok = got == want
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] Temporal decoy {day}, true P{true_a} -> P{got} (expected P{want})")
        r1, r2 = navigate("The quick brown fox jumps over the lazy dog."), navigate("The quick brown fox jumps over the lazy dog.")
        ok = (r1['n1'], r1['n2'], r1['n3'], r1['anchor']) == (r2['n1'], r2['n2'], r2['n3'], r2['anchor']) and 'datetime' not in navigate.__code__.co_names
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] Temporal invariance: the coordinate takes no temporal input and repeats exactly")
        # M230-A known answers
        for c, want in ((24, ("P3", True)), (9, ("P9", True)), (5, ("P7", False)), (2, ("P1", False))):
            e = m230a_entry(c); got = (e["placement"], e["tier2"])
            ok = got == want
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] M230-A count {c} -> {got} (expected {want})")
        ok = m230a_base_rate() == round(5 / 48, 4)
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] M230-A uniform base rate 1-48 = {m230a_base_rate()}")
        # M230-I known answers
        r = m230i_sensitivity(range(11, 17)); ok = r["distinct"] == 6 and r["placements"][2] == "P2"
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] M230-I microtubule protofilament counts 11-16 -> {r['distinct']} distinct positions (13 -> P2)")
        r = m230i_sensitivity([24, 24, 24]); ok = r["distinct"] == 1
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] M230-I identical representations -> spread 1")
        # M230-B/C known answers
        p = cell24_symmetry_profile(); t = t2_profile()
        ok = (p["order"], p["max_element_order"], p["single_24_cycle"], p["order12_cycle_types"], p["order12_sixth_power_is_inversion"]) == (1152, 12, False, [(12, 12)], True) \
            and t == {"cycle_type": (12, 12), "sixth_power_negates": True} and omega_full_cycle_type() == (24, 24, 24, 8, 1)
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] M230-C 24-cell: W(F4) order 1152, no order-24 symmetry, Coxeter (12,12) with c^6 = -I, matching T^2; T on 81 states (24,24,24,8,1)")
        # M206 NEDA known answers
        for d, want in (("The quick brown fox jumps over the lazy dog.", 9), ("aaaa bbbb", 2)):
            got = compute_neda(extract_content_words(spnp(d)))
            ok = got == want
            all_pass = all_pass and ok
            print(f"[{'PASS' if ok else 'FAIL'}] NEDA {d!r} -> P{got} (expected P{want})")
        # Part 1.8: canonical selection witness and half-period negation
        rows = canonical_selection()[1]
        got = [(r[1], r[4]) for r in rows]
        want = [(1, 'UNIQUE'), (1, 'UNIQUE'), (24, 'UNDERDETERMINED (orbit unique, starting state open)'), (36, 'NON-UNIQUE')]
        ok = got == want and rows[0][2] == ['Voice C'] and rows[1][2] == ['Voice B']
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] Canonical selection: K -> Voice C unique; K-alt-1 -> Voice B; K-alt-2 orbit only; K-alt-3 36 readings")
        ok = half_period_negation() == 81
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] Half-period negation holds for all 81 states")
        nb = navigation_block("What is the Human Condition?", "Human Condition")
        eb = echo_block(_FIXTURE_CORE + " " + _FIXTURE_REST, 6, _FIXTURE_CORE)
        ok = ("EXPOSED DOMAIN: YES" in nb and not is_exposed("Why does the harbour freeze late in winter?")
              and is_exposed("what is the human  condition?") and "ANCHOR P6" in nb and "-> P7 | DIFFERENT ANCHOR" in nb and "phrasing-sensitive (P6 -> P7)" in nb
              and "M209 (THE ANSWER): n = (38, 192, 49)" in eb and "ECHO ANCHOR P1" in eb
              and "n = (23, 114, 28)" in eb and "ECHO ANCHOR P7" in eb and "ECHO CLOSURE: YES" not in eb)
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] --navigate / --echo worked example (Part 8.0): P6, M116 P7; constructed echo fixture P1 / P7")
        ok = all(r[1] for r in math_gate())
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] MATH-GATE: all checks reconstruct the mathematical ground")
        ref = domain_sha256("The quick  brown fox ")
        ok = ref == domain_sha256("the quick brown fox") and ref != domain_sha256("The quick brown fox.")
        all_pass = all_pass and ok
        print(f"[{'PASS' if ok else 'FAIL'}] L-414 hash: whitespace and case folded, punctuation kept")
        for domain, expected, label in test_cases:
            result = navigate(domain)
            passed = result['anchor'] == expected
            all_pass = all_pass and passed
            status = "PASS" if passed else f"FAIL (expected P{expected}, got P{result['anchor']})"
            print(f"[{status}] {label}")
        sys.exit(0 if all_pass else 1)
    else:
        domain_text = " ".join(sys.argv[1:])
        result = navigate(domain_text)
        print(f"DOMAIN SHA-256: {domain_sha256(domain_text)}")
        print(f"n1={result['n1']} n2={result['n2']} n3={result['n3']}")
        print(f"anchor=P{result['anchor']}({result['anchor_value']}) tfi={result['tfi']:.2f}")
        print(f"gaps={' * '.join(result['gaps']) if result['gaps'] else 'none'}")
        print(f"content={' * '.join(result['content'])}")
        print(f"SUBSTRATE SHA-256: {substrate_sha256(result['content'])}")
