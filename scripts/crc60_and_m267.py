# ===== crc60_and_m267.py BEGIN =====
#!/usr/bin/env python3
"""crc60_and_m267.py -- the CRC-60 corpus, its matched null corpus, and M267 (the decoy-
coordinate control apparatus). Requires canonical_reference.py, imported as an argument
to load() or run alongside it on the same path.

Usage:
  python3 crc60_and_m267.py CANONICAL_REFERENCE.py freeze
  python3 crc60_and_m267.py CANONICAL_REFERENCE.py m220
  python3 crc60_and_m267.py CANONICAL_REFERENCE.py assign SEED
"""
import hashlib, importlib.util, json, random, re, sys


def load_canon(path):
    spec = importlib.util.spec_from_file_location("canon", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ M238 (Core, exact) three fixed variants
PB5L2 = dict(x.split('/') for x in
"big/large,small/little,fast/quick,slow/gradual,old/ancient,new/recent,good/fine,bad/poor,start/begin,end/finish,"
"help/assist,show/demonstrate,make/create,use/utilize,buy/purchase,find/locate,get/obtain,keep/retain,try/attempt,"
"want/desire,need/require,ask/inquire,say/state,tell/inform,think/believe,know/understand,see/observe,look/examine,"
"give/provide,take/acquire,happy/pleased,sad/unhappy,angry/upset,afraid/fearful,strong/powerful,weak/feeble,"
"rich/wealthy,poor/impoverished,hard/difficult,easy/simple,high/elevated,low/reduced,near/close,far/distant,"
"important/significant,common/typical,rare/uncommon,clear/evident,true/accurate,false/incorrect,whole/complete,"
"part/portion,many/numerous,few/scarce,always/constantly,never/rarely".split(','))
assert len(PB5L2) == 56, len(PB5L2)


def minimal(text, canon):
    return ' '.join(canon.extract_content_words(canon.spnp(text)))


def pb5_l1(text):
    return text.rstrip() + ' exactly'


def pb5_l2(text):
    def repl(m):
        w = m.group(0)
        r = PB5L2.get(w.lower())
        if r is None:
            return w
        return r.capitalize() if w[0].isupper() else r
    return re.sub(r"[A-Za-z']+", repl, text)


def variants(text, canon):
    return {'MINIMAL': minimal(text, canon), 'PB5L1': pb5_l1(text), 'PB5L2': pb5_l2(text)}


def m238(text, canon):
    base = canon.navigate(text)
    out = {'ORIGINAL': base['anchor']}
    stable = True
    for name, vtext in variants(text, canon).items():
        v = canon.navigate(vtext)
        out[name] = v['anchor']
        if v['anchor'] != base['anchor']:
            stable = False
    out['STATUS'] = 'STABLE' if stable else 'SENSITIVE'
    return out


# ------------------------------------------------------------------ neutral vocabulary pool (Companion 24.4)
NEUTRAL_WORDS = """
ox at up on in it is ax owl elk cat dog fox box hat sun sky ice oak elm ash bag jar cup pot pan bed
rug map pen key lid mug rope sock shoe coat belt lamp desk shelf couch chair table window mirror
curtain blanket pillow kettle teapot basket bucket ladder hammer wrench pencil crayon marker
scissor stapler blender toaster fridge freezer cabinet drawer closet hallway kitchen bedroom
bathroom driveway sidewalk pavement mailbox doorbell chimney fireplace staircase balcony
apartment building cottage cabin garage warehouse hotel motel airport station platform bicycle
scooter wagon truck trailer caravan carriage vessel canoe kayak sailboat ferry cruise voyage
journey suitcase backpack umbrella raincoat sweater jacket trousers sandals slippers necklace
bracelet earring wallet purse handbag notebook calendar magazine newspaper envelope postcard
package parcel delivery courier mailman postman bakery butcher grocer market vendor customer
cashier waiter waitress chef cook baker farmer rancher fisherman sailor pilot driver mechanic
plumber electrician carpenter painter tailor barber florist gardener librarian teacher student
neighbor stranger visitor guest tourist traveler pedestrian cyclist jogger swimmer skater skier
hiker camper picnic barbecue festival carnival parade concert theater cinema museum gallery
library bookstore bakery cafe restaurant diner tavern pub lounge lobby hallway elevator escalator
staircase rooftop terrace garden meadow orchard vineyard pasture prairie forest jungle desert
canyon valley plateau glacier volcano island peninsula harbor lagoon lakeside riverside seaside
countryside village hamlet township district province region continent nation kingdom empire
century decade morning evening midnight sunrise sunset daylight twilight rainbow thunder
lightning drizzle downpour blizzard snowfall hailstorm heatwave breeze gust gale storm cloud
mist fog dew frost drought flood tide wave current whirlpool waterfall stream brook creek pond
puddle fountain reservoir dam canal bridge tunnel highway freeway avenue boulevard alley lane
crossroad roundabout intersection sidewalk curb gutter pavement pathway trail track route
compass anchor sail mast deck cabin engine wheel axle brake pedal handlebar saddle helmet
buckle zipper button ribbon lace thread needle fabric cotton wool silk velvet linen leather
plastic rubber metal wood glass ceramic marble granite pebble boulder gravel sand clay mud
puddle dust ash smoke flame ember charcoal firewood matches candle lantern torch flashlight
battery cable wire socket switch outlet remote speaker headphones microphone camera television
radio telephone calendar clock watch alarm timer thermostat blanket mattress cushion hammock
tent tarp rope knot anchor paddle oar raft dinghy pier dock wharf jetty lighthouse buoy compass
apple banana orange lemon lime peach plum cherry grape melon berry mango papaya coconut walnut
almond peanut cashew raisin pretzel biscuit cracker pancake waffle omelet sausage bacon cheese
butter yogurt cereal oatmeal porridge sandwich burger noodle spaghetti dumpling pastry muffin
cupcake pudding custard jelly syrup honey vinegar mustard ketchup pepper cinnamon nutmeg ginger
parsley basil oregano thyme rosemary lettuce cabbage carrot potato onion garlic celery spinach
pumpkin zucchini eggplant cucumber broccoli mushroom radish turnip beetroot chestnut hazelnut
 ivy oboe aloe cocoa radio piano video studio curtain calendar furniture umbrella vacation orchestra chocolate chimney envelope daffodil aquarium binoculars watermelon caterpillar helicopter refrigerator supermarket motorcycle photograph neighborhood celebration organization information communication transportation imagination examination conversation congratulation entertainment appreciation accommodation determination investigation civilization documentary laboratory dictionary observatory territory anniversary xylophone accordion saxophone trombone clarinet harmonica dandelion buttercup marigold sunflower blueberry strawberry raspberry mayonnaise cauliflower asparagus artichoke pineapple grapefruit telescope microscope periscope kaleidoscope thermometer barometer newspaper encyclopedia avenue boulevard promenade esplanade architecture sculpture literature screamed strength stretched scratched
 eon onyx oasis igloo iguana violin balloon costume mystery thoughts screeched stretches sandwich portrait literary secretary customary momentary discovery machinery stationery watermelons caterpillars refrigerators extraordinary complimentary
 opal aria zebu ibis vanilla gorilla octopus alcohol banana potato tomato dinosaur telephone binocular apparatus complicated illustrated
 identity property majority minority television generation revelation sensation vacationer temperature necessary secondary voluntary responsibility availability probability unbelievable questionable comfortable considerable activity curiosity creativity electricity originality personality nationality hospitality escalation bureaucracy overactive historical uncertainty consistency transformation isolated
"""

# stable, deduplicated ordering
_seen = set()
NEUTRAL_LIST = []
for w in NEUTRAL_WORDS.split():
    w = w.lower()
    if w not in _seen:
        _seen.add(w)
        NEUTRAL_LIST.append(w)


# ------------------------------------------------------------------ CRC-60 domains (Companion 24.4)
DOMAINS = {
    'PHYSICS_MATH': [
        'Energy can neither be created nor destroyed',
        'The square root of two is irrational',
        'The speed of light is constant for every observer',
        'Light travels fastest through a vacuum',
        'Every action produces an equal and opposite reaction',
        'Entropy in a closed system never decreases',
        'Gravity bends the path of passing light',
        'The universe has been expanding since its origin',
        'Irrational numbers cannot be written as simple fractions',
        'Electric charge is conserved in every physical process',
        'Heat always flows from hot to cold',
        'Parallel lines never intersect in Euclidean space',
        'A triangle\'s interior angles sum to a straight line',
        'Magnetic monopoles have never been observed experimentally',
        'Quantum particles exist in superposition until measured',
        'Waves interfere constructively or destructively depending on phase',
        'Zero divided by any nonzero number equals zero',
        'Radioactive isotopes decay at a fixed statistical rate',
        'Prime numbers have exactly two distinct divisors',
        'Electrons occupy discrete energy levels around a nucleus',
    ],
    'BIO_MED': [
        'Antibiotics kill bacteria but not viruses',
        'Blood clots to stop bleeding',
        'Cells divide during growth',
        'Mitochondria generate most of a cell\'s energy',
        'Insulin lowers blood glucose after a meal',
        'Bacteria can develop resistance to overused antibiotics',
        'The skin acts as a barrier against pathogens',
        'Hormones regulate growth, metabolism, and reproduction',
        'Cancer arises from uncontrolled cellular division',
        'The spine protects the central nervous system',
        'Platelets help blood clot after injury',
        'DNA carries hereditary information between generations',
        'Neurons communicate through electrical and chemical signals',
        'Muscles contract when stimulated by motor neurons',
        'Photosynthesis converts sunlight into stored chemical energy',
        'Natural selection favors traits that improve survival',
        'Enzymes speed up reactions without being consumed',
        'The kidneys regulate the body\'s fluid and salt balance',
        'White blood cells defend the body against infection',
        'The heart pumps blood through a closed circulatory system',
    ],
    'PHIL_HUMANITIES': [
        'Art reflects the values of its own age',
        'Habit shapes character over decades',
        'Choice defines a person\'s character',
        'Freedom entails responsibility for one\'s own choices',
        'Language shapes the boundaries of human thought',
        'Power tends to corrupt those who hold it',
        'Memory constructs identity more than it records it',
        'Democracy depends on an informed and active citizenry',
        'Suffering often teaches lessons comfort cannot',
        'Truth sometimes conflicts with popular opinion',
        'Time heals wounds it cannot fully erase',
        'Justice requires treating equal cases equally',
        'Knowledge without wisdom often leads to harm',
        'Virtue is a habit cultivated through repeated practice',
        'Tradition binds generations across centuries of change',
        'Ambition can build great things or destroy them',
        'Progress often demands sacrificing old certainties',
        'Meaning is something people create, not merely find',
        'Courage means acting rightly despite genuine fear',
        'Love endures where mere passion eventually fades',
    ],
}


# ------------------------------------------------------------------ corpus construction, freezing, M267
CATEGORIES = ('PHYSICS_MATH', 'BIO_MED', 'PHIL_HUMANITIES')


def build_pool_index(canon):
    idx = {}
    for w in NEUTRAL_LIST:
        if w in canon.CANONICAL_STOPWORDS:
            continue  # a substitute that is itself a stopword would vanish on re-extraction
        idx.setdefault((len(w), canon.count_syllables(w)), []).append(w)
    return idx


def null_domain(text, pool_index, rng, canon):
    """Replace every content word with a distinct neutral word of the same (length,
    syllables), so n1, n2, n3 and therefore the anchor are unchanged by construction."""
    words = canon.extract_content_words(canon.spnp(text))
    used = set()
    out_words = []
    for w in words:
        key = (len(w), canon.count_syllables(w))
        options = [c for c in pool_index[key] if c not in used]
        if not options:
            raise ValueError('pool exhausted for key %r (word %r)' % (key, w))
        rng.shuffle(options)
        pick = options[0]
        assert pick not in canon.CANONICAL_STOPWORDS, pick
        used.add(pick)
        out_words.append(pick.capitalize() if w[0].isupper() else pick)
    return ' '.join(out_words) + '.'


def build_corpus(domains_by_category, canon):
    pool_index = build_pool_index(canon)
    rng = random.Random(60)  # fixed seed: reproducible null-corpus construction
    rows = []
    for cat in CATEGORIES:
        for text in domains_by_category[cat]:
            r = canon.navigate(text)
            m = m238(text, canon)
            null_text = null_domain(text, pool_index, rng, canon)
            nr = canon.navigate(null_text)
            assert (nr['n1'], nr['n2'], nr['n3']) == (r['n1'], r['n2'], r['n3']), (text, null_text)
            assert nr['anchor'] == r['anchor']
            rows.append({
                'category': cat, 'domain': text,
                'n1': r['n1'], 'n2': r['n2'], 'n3': r['n3'], 'anchor': r['anchor'],
                'm238_status': m['STATUS'],
                'null_domain': null_text,
            })
    triples = [(r['n1'], r['n2'], r['n3']) for r in rows]
    assert len(triples) == len(set(triples)) == 60, 'duplicate (n1,n2,n3) triple in CRC-60'
    return rows


def freeze_hash(rows):
    """SHA-256 over the 60 domain strings in fixed (category, list) order, then over the
    60 null strings in the same order. Two hashes: corpus identity and null-corpus identity."""
    corpus_bytes = '\n'.join(r['domain'] for r in rows).encode('utf-8')
    null_bytes = '\n'.join(r['null_domain'] for r in rows).encode('utf-8')
    return hashlib.sha256(corpus_bytes).hexdigest(), hashlib.sha256(null_bytes).hexdigest()


# ------------------------------------------------------------------ M267: decoy-coordinate control
def anchor_distribution():
    """The measured anchor distribution from Companion 31.2 (5,108 sentences)."""
    return {1: 0.1092, 2: 0.0871, 3: 0.1198, 4: 0.1366, 5: 0.0816,
            6: 0.0877, 7: 0.1161, 8: 0.1419, 9: 0.1198}  # N=5,108 (Companion 31.2)


def draw_decoy(real_anchor, rng):
    dist = anchor_distribution()
    choices, weights = zip(*[(k, v) for k, v in dist.items() if k != real_anchor])
    return rng.choices(choices, weights=weights, k=1)[0]


def m267_assign(rows, seed):
    """Build a blinded real/decoy assignment for a decoy-coordinate control run.
    Returns (panel_file, key_file): panel_file has no indication of which slot is real;
    key_file, kept by whoever runs the test, records the truth for later unblinding."""
    rng = random.Random(seed)
    panel, key = [], []
    for i, r in enumerate(rows):
        decoy = draw_decoy(r['anchor'], rng)
        slots = ['A', 'B']
        rng.shuffle(slots)
        real_slot, decoy_slot = slots
        item_id = 'CRC60-%02d' % (i + 1)
        panel.append({
            'item_id': item_id, 'domain': r['domain'],
            'slot_%s_anchor' % real_slot: r['anchor'],
            'slot_%s_anchor' % decoy_slot: decoy,
            'slot_A_synthesis': None, 'slot_B_synthesis': None,
            'ratings': {'specificity': None, 'non_obviousness': None, 'arm_relevance': None},
        })
        key.append({'item_id': item_id, 'real_slot': real_slot, 'real_anchor': r['anchor'], 'decoy_anchor': decoy})
    return panel, key


def m267_analyze(panel_with_ratings, key):
    """Given completed panel ratings and the key, report whether real syntheses were rated
    higher than decoy syntheses more often than chance (sign test on paired comparisons)."""
    key_by_id = {k['item_id']: k for k in key}
    wins_real = wins_decoy = ties = 0
    for item in panel_with_ratings:
        k = key_by_id[item['item_id']]
        real_slot = k['real_slot']
        decoy_slot = 'B' if real_slot == 'A' else 'A'
        r_real = item['ratings'].get('slot_%s_total' % real_slot)
        r_decoy = item['ratings'].get('slot_%s_total' % decoy_slot)
        if r_real is None or r_decoy is None:
            continue
        if r_real > r_decoy:
            wins_real += 1
        elif r_decoy > r_real:
            wins_decoy += 1
        else:
            ties += 1
    n = wins_real + wins_decoy
    return {'wins_real': wins_real, 'wins_decoy': wins_decoy, 'ties': ties, 'n_decisive': n,
            'real_win_rate': (wins_real / n) if n else None,
            'interpretation': ('NOT ENOUGH DECISIVE RATINGS' if n < 10 else
                               'no test run yet -- see Companion Part 31.5 for the significance procedure')}


def m220_balance(rows):
    """M220 Antipodal Corpus Balance: across the corpus, count how often each of the 24 positions is reached as an
    arm (Yang, Yin, 4D) or as the Antipode, group the hits into the twelve antipodal pairs (i, i+12), and list
    positions never reached. Anchors can only ever be P1-P9; this sees the other fifteen positions."""
    from collections import Counter
    hits = Counter()
    for r in rows:
        a = r['anchor']
        for off in (5, 18, 8, 12):
            hits[(a + off) % 24] += 1
    total = sum(hits.values())
    pairs = [(i, i + 12, hits.get(i, 0), hits.get(i + 12, 0)) for i in range(12)]
    return {'total_hits': total,
            'by_position': {('P%d' % p): hits.get(p, 0) for p in range(24)},
            'antipodal_pairs': [('P%d' % i, 'P%d' % j, a, b) for i, j, a, b in pairs],
            'never_reached': ['P%d' % p for p in range(24) if hits.get(p, 0) == 0]}


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(0)
    canon = load_canon(sys.argv[1])
    rows = build_corpus(DOMAINS, canon)
    if sys.argv[2] == 'freeze':
        h_corpus, h_null = freeze_hash(rows)
        print(json.dumps({'rows': rows, 'sha256_corpus': h_corpus, 'sha256_null': h_null}, indent=1))
    elif sys.argv[2] == 'm220':
        print(json.dumps(m220_balance(rows), indent=1))
    elif sys.argv[2] == 'assign' and len(sys.argv) >= 4:
        panel, key = m267_assign(rows, int(sys.argv[3]))
        print(json.dumps({'panel': panel, 'key': key}, indent=1))
    else:
        print(__doc__)
# ===== crc60_and_m267.py END =====
