#!/usr/bin/env python3
"""adaptor_rules.py -- the frozen counting rules of the adaptors of Core L-501 (Part 3.43), with their nulls.

Pure functions, no file access, so that the same rules run in tools/adaptors.py (M317) and in the free Strike app
(site/py/strike.py, under Pyodide). Each counter returns (n1, n2, n3) at three declared granularities; the coordinate
follows by the canonical projection. The stopword lists of the Latin-, Cyrillic-, Greek-, Arabic-, Hebrew- and
Devanagari-script adaptors are renderings of the frozen English list of Core Part 1.9 (articles, conjunctions,
prepositions, the copula, demonstratives, "it", quantifiers and the five modals), and question words are retained as
content words, as Part 1.9 retains them in English. The rules of each adaptor are versioned with the registry
(records/adaptors/registry.json); a change to them is a protocol revision (L-501).
"""
import re, unicodedata
from collections import Counter


def _nfc(t): return unicodedata.normalize('NFC', t)


def _strip(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')


# ---------------------------------------------------------------- KO-HANGUL-1: eojeol / syllable blocks / jamo
def hangul(text):
    t = _nfc(text); n1 = n2 = n3 = 0
    for tok in t.split():
        if any(0xAC00 <= ord(c) <= 0xD7A3 or 0x3131 <= ord(c) <= 0x318E for c in tok): n1 += 1
        for c in tok:
            if 0xAC00 <= ord(c) <= 0xD7A3: n2 += 1; n3 += 2 + (((ord(c) - 0xAC00) % 28) > 0)
            elif 0x3131 <= ord(c) <= 0x318E: n3 += 1
    return n1, n2, n3


# ---------------------------------------------------------------- alphabetic scripts: content words / letters / syllables
STOP = {
 'DE-LATN-1': set('der die das den dem des ein eine einen einem einer eines und oder aber wenn dann sonst für noch so doch von zu zum zur in im ins an am auf bei mit ist sind war waren sein gewesen seiend dies diese dieser dieses jene jener jenes es als aus nicht sehr nur auch über unter um nach vor weil während obwohl einige etwas irgendein alle jeder jede jedes kein keine eigen eigene gleich kann können wird werden würde sollte könnte'.split()),
 'FR-LATN-1': set('le la les l un une des et ou mais si alors sinon pour ni donc pourtant de du d à au aux en dans sur par avec est sont était étaient être été étant ce cet cette ces c ceci cela il elle son sa ses comme depuis ne pas n très juste aussi que qu sous environ après avant parce puisque pendant quelque quelques tout tous toute toutes chaque aucun aucune propre même trop peut pourra pourrait devrait s'.split()),
 'RU-CYRL-1': set('и или но если то иначе для ни так ещё же из к в во на у по с со есть это этот эта эти тот та те его её от не очень только также чем над под о об после до потому пока хотя некоторые любой все всё каждый никакой свой тоже может будет бы должен мог'.split()),
 'EL-GREK-1': set(_strip(w).lower() for w in 'ο η το οι τα του της των τον την ένας μια ένα και ή αλλά αν τότε για ούτε έτσι όμως από σε στο στη στον στην με είναι ήταν αυτό αυτός αυτή αυτά εκείνος εκείνη εκείνο ως όχι δεν πολύ μόνο επίσης παρά πάνω κάτω περί μετά πριν επειδή ενώ κάποιοι κάθε όλοι κανένας ίδιος μπορεί θα'.split()),
 'AR-ARAB-1': set('و أو لكن إذا ثم من إلى في على عن مع هو هي هم هذا هذه ذلك تلك أن إن كان كانت يكون ليس لا كل بعض أي جدا فقط أيضا من بعد قبل لأن بينما رغم يمكن سوف قد'.split()),
 'HE-HEBR-1': set('של את על עם אל מן גם כי אם אבל או לא זה זו זאת אלה הוא היא הם הן כל כמו יותר מאוד רק אחרי לפני בגלל בזמן יכול יכולה יהיה'.split()),
 'HI-DEVA-1': set('है हैं था थी थे होना हो और या लेकिन अगर तो के लिए न से में पर को का की यह वह ये वे इस उस एक भी बहुत केवल सिर्फ़ जैसे बाद पहले क्योंकि जबकि हालांकि कुछ कोई सब हर अपना वही सकता सकती सकते'.split()),
}
QUESTION = {'FR-LATN-1': {'qu', 'que', 'quoi', 'qui', 'quel', 'quelle', 'quels', 'quelles', 'comment', 'pourquoi', 'quand', 'où'}}


def _tokens_latin(text, lang):
    t = _nfc(text)
    if lang == 'FR-LATN-1':
        t = re.sub(r"\b([lLdDcCnNsSjJmMtT]|[qQ]u)['’]", r"\1 ", t)            # elisions split: l', d', c', n', s', j', m', t', qu'
    return re.findall(r"[^\W\d_]+", t)


def _vowel_groups(word, vowels):
    return len(re.findall('[%s]+' % vowels, word.lower()))


def latin(lang):
    V = {'DE-LATN-1': 'aeiouyäöü', 'FR-LATN-1': 'aeiouyàâäéèêëîïôöùûüÿœæ'}[lang]
    def count(text):
        toks = _tokens_latin(text, lang); words = []
        for i, w in enumerate(toks):
            lw = w.lower()
            if lw in QUESTION.get(lang, set()) and i == 0: words.append(w); continue
            if lw not in STOP[lang]: words.append(w)
        n3 = 0
        for w in words:
            g = max(1, _vowel_groups(w, V))
            if lang == 'FR-LATN-1' and g >= 2 and re.search(r'(e|es|ent)$', w.lower()): g -= 1   # silent final e, es, ent
            n3 += g
        return len(words), sum(len(w) for w in words), n3
    return count


def cyrillic(text):
    toks = re.findall(r'[Ѐ-ӿ]+', _nfc(text))
    words = [w for w in toks if w.lower() not in STOP['RU-CYRL-1']]
    return len(words), sum(len(w) for w in words), sum(max(1, len(re.findall('[аеёиоуыэюяіїєў]', w.lower()))) for w in words)


def greek(text):
    toks = re.findall(r'[Ͱ-Ͽἀ-῿]+', _nfc(text))
    words = [w for w in toks if _strip(w).lower() not in STOP['EL-GREK-1']]
    syl = 0
    for w in words:
        s = _strip(w).lower()
        s = re.sub(r'(αι|ει|οι|ου|υι)', 'α', s)                                 # the digraphs read as one vowel
        syl += max(1, len(re.findall('[αεηιουω]', s)))
    return len(words), sum(len(_strip(w)) for w in words), syl


def arabic(text):
    toks = re.findall(r'[ء-يً-ْٰ]+', _nfc(text))
    words = [w for w in toks if re.sub(r'[ً-ْٰ]', '', w) not in STOP['AR-ARAB-1']]
    n2 = sum(len(re.findall(r'[ء-ي]', w)) for w in words)
    n3 = sum(max(1, len(re.findall(r'[ً-ِٰ]', w)) + len(re.findall('[اويى]', w))) for w in words)   # ESTIMATE
    return len(words), n2, n3


def hebrew(text):
    toks = re.findall(r'[ְ-ׇא-ת]+', _nfc(text))
    words = [w for w in toks if re.sub(r'[ְ-ׇ]', '', w) not in STOP['HE-HEBR-1']]
    n2 = sum(len(re.findall(r'[א-ת]', w)) for w in words)
    n3 = sum(max(1, len(re.findall(r'[ֱ-ׇֻ]', w)) + len(re.findall('[וי]', w))) for w in words)        # ESTIMATE
    return len(words), n2, n3


def devanagari(text):
    toks = re.findall(r'[ऀ-ॿ]+', _nfc(text))
    words = [w for w in toks if w not in STOP['HI-DEVA-1']]
    n2 = n3 = 0
    for w in words:
        for i, c in enumerate(w):
            o = ord(c)
            cons = 0x0915 <= o <= 0x0939 or 0x0958 <= o <= 0x095F
            if 0x0904 <= o <= 0x0914: n2 += 1; n3 += 1                            # an independent vowel: one akshara
            elif cons:
                n3 += 1
                if not (i + 1 < len(w) and ord(w[i + 1]) == 0x094D): n2 += 1      # a consonant not closed by virama ends an akshara
            elif 0x093E <= o <= 0x094C: n3 += 1                                   # a dependent vowel sign
    return len(words), n2, n3


COUNTERS = {'KO-HANGUL-1': hangul, 'DE-LATN-1': latin('DE-LATN-1'), 'FR-LATN-1': latin('FR-LATN-1'), 'RU-CYRL-1': cyrillic,
            'EL-GREK-1': greek, 'AR-ARAB-1': arabic, 'HE-HEBR-1': hebrew, 'HI-DEVA-1': devanagari}
SCRIPTS = {'HANGUL': 'KO-HANGUL-1', 'CYRILLIC': 'RU-CYRL-1', 'GREEK': 'EL-GREK-1', 'ARABIC': 'AR-ARAB-1', 'HEBREW': 'HE-HEBR-1',
           'DEVANAGARI': 'HI-DEVA-1'}
DECLARED = {'de': 'DE-LATN-1', 'fr': 'FR-LATN-1'}     # Latin-script languages, by the Striker's declaration (LANGUAGE line)
OPEN_SCRIPTS = {'CJK': 'a frozen word segmentation and stroke table', 'HIRAGANA': 'a frozen reading table for kanji beside the kana',
                'KATAKANA': 'a frozen reading table for kanji beside the kana', 'THAI': 'a frozen word segmentation'}
PERTURB = {'KO-HANGUL-1': ('정확히', '당신의 말로'), 'DE-LATN-1': ('genau', 'In deinen eigenen Worten'), 'FR-LATN-1': ('exactement', 'Avec tes propres mots'),
           'RU-CYRL-1': ('точно', 'Своими словами'), 'EL-GREK-1': ('ακριβώς', 'Με δικά σου λόγια'), 'AR-ARAB-1': ('بالضبط', 'بكلماتك الخاصة'),
           'HE-HEBR-1': ('בדיוק', 'במילים שלך'), 'HI-DEVA-1': ('ठीक', 'अपने शब्दों में')}


def script_of(text):
    """The script a text is routed by (Core Part 3.43). Letters are counted by the first word of their Unicode name.
    Latin with at least half of the letters: LATIN, and the text stays on the canonical extraction, any other part read
    as a companion (M189). Otherwise the non-Latin script with the most letters; a tie between scripts goes to the one
    whose first letter comes first in the text. A single letter decides by itself. No letters: None."""
    c = Counter(); first = {}
    for i, ch in enumerate(_nfc(text)):
        if unicodedata.category(ch).startswith('L'):
            n = unicodedata.name(ch, '')
            k = n.split(' ')[0] if n else 'UNKNOWN'
            c[k] += 1; first.setdefault(k, i)
    if not c: return None
    total = sum(c.values())
    if 2 * c.get('LATIN', 0) >= total: return 'LATIN'
    return min((k for k in c if k != 'LATIN'), key=lambda k: (-c[k], first[k]))


def variants(adaptor, text):
    ap, pre = PERTURB[adaptor]
    toks = text.split()
    return (text.rstrip() + ' ' + ap, ' '.join(toks[:-1]), pre + ' ' + text)


# ---------------------------------------------------------------- nulls: the distribution of (anchor, state) a strike takes by chance
def _project(n1, n2, n3, determine_anchor):
    a, r1, r2, r3, t = determine_anchor(n1, n2, n3)
    return a, (r1 % 9, r2 % 9)


def null(name, determine_anchor, n1=None):
    """UNIFORM-729: residue triples uniform, as M310 takes them for the canonical record. The structural nulls take each
    adaptor's own constraint between its layers, enumerated over questions of 1 to 15 words of 1 to 6 units (frozen).
    With n1 given, the null is conditioned on the word count: the first layer is fixed at n1, so r1 = dr(5 n1), and the
    other two layers range as the null allows (Core L-501, M310: the reference chance of a meeting)."""
    P = Counter()
    if name == 'UNIFORM-729':
        for a in ([n1] if n1 is not None else range(1, 10)):
            for b in range(1, 10):
                for c in range(1, 10): P[_project(a, b, c, determine_anchor)] += 1
        return P
    for m in ([n1] if n1 is not None else range(1, 16)):
        lo = max(m, 1)
        for n2 in range(lo, 6 * lo + 1):
            if name == 'HANGUL-STRUCTURAL-1': rng = range(2 * n2, 3 * n2 + 1)          # jamo = 2 x blocks + finals
            elif name == 'AKSHARA-STRUCTURAL-1': rng = range(n2, 2 * n2 + 1)           # components = aksharas + signs
            elif name == 'ABJAD-STRUCTURAL-1': rng = range(max(m, 1), n2 + 1)          # vowel estimate between words and letters
            else: raise KeyError(name)
            for n3 in rng: P[_project(m, n2, n3, determine_anchor)] += 1
    return P


def rates(PA, PB):
    """Exact chance that a strike under null A and a strike under null B share a state, mirror one, or link."""
    ta, tb = sum(PA.values()), sum(PB.values())
    sa, sb, aa, ab, ya, yb = Counter(), Counter(), Counter(), Counter(), Counter(), Counter()
    for (a, s), w in PA.items(): sa[s] += w; aa[a] += w; ya[(a + 5) % 24] += w
    for (a, s), w in PB.items(): sb[s] += w; ab[a] += w; yb[(a + 5) % 24] += w
    neg = lambda s: ((-s[0]) % 9, (-s[1]) % 9)
    same = sum(sa[s] * sb[s] for s in sa) / (ta * tb)
    mirror = sum(sa[s] * sb[neg(s)] for s in sa if s != (0, 0)) / (ta * tb)
    link = (sum(ya[k] * ab[k] for k in ya) + sum(yb[k] * aa[k] for k in yb)) / (2 * ta * tb)
    return dict(state=same, mirror=mirror, link=link)
