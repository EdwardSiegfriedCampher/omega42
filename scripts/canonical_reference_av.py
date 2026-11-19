# ===== canonical_reference_av.py BEGIN =====
# Omega42 V335 Rev.449 -- canonical A/V reference: frozen boundary extractor (M247),
# media navigability gate (M265), corpus profiler (M266).
# Python standard library only. Integer arithmetic throughout, so two compliant
# implementations given the same frozen input must return identical counts.
import zlib, struct, wave, io, hashlib, sys, os
from collections import Counter

ORBIT = [2, 5, 7, 3, 1, 4, 5, 9, 5, 5, 1, 6, 7, 4, 2, 6, 8, 5, 4, 9, 4, 4, 8, 3]
POSITION_NAMES = ['Seed', 'Fixpoint', 'Generator', 'Desire', 'Unity', 'Law', 'Seed/Causal',
                  'Navigator', 'Generation', 'Fixpoint', 'Unity', 'Question', 'Opening', 'Gap',
                  'Observer', 'Other', 'Flow', 'Seed/Return', 'Threshold', 'Time', 'Reckoning',
                  'Sublime', 'Collective', 'Return']
UNITS = (1, 2, 4, 5, 7, 8)

# ---- frozen constants (CDT-B design choices; changing any one is a new revision) ----
IMG_GRID = 64                 # square grid the image is reduced to
IMG_BITS = (2, 4, 6)          # luminance quantisation: 4, 16, 64 levels (coarse, mid, fine)
IMG_MINCELLS = (164, 82, 41)  # minimum component area in grid cells: 4%, 2%, 1% of 4096
AUD_RATE = 8000               # Hz, frozen analysis rate (any source rate >= 8000 accepted)
AUD_FRAME = 160               # 20 ms
AUD_RATIO = (1, 16)           # frame is active if energy * 16 >= max frame energy
AUD_GAPS = (8, 1)             # frames closed: coarse layer (n1), mid layer (n3)
AUD_MINRUN = 2                # fine layer drops active runs shorter than 2 frames
AUD_MIN_FRAMES = 10           # shorter than 200 ms is not navigable
AUD_MIN_EMAX = 16 * 16 * AUD_FRAME   # loudest frame must reach RMS >= 16 (of 32768)
LOW_STRUCTURE_N2 = 3          # fewer fine boundary units than this is flagged LOW-STRUCTURE


# ------------------------------------------------------------------ CPP and arms
def digital_root(n):
    n = abs(int(n))
    return 9 if n == 0 else 1 + (n - 1) % 9


def cpp(n):
    return digital_root(5 * n)


def determine_anchor(n1, n2, n3):
    r1, r2, r3 = cpp(n1), cpp(n2), cpp(n3)
    top, freq = Counter([r1, r2, r3]).most_common(1)[0]
    anchor = top if freq >= 2 else r1
    tfi = 0.00 if freq == 3 else (0.67 if freq == 2 else 1.00)
    return anchor, r1, r2, r3, tfi


def derive_arms(a):
    return (a + 5) % 24, (a + 18) % 24, (a + 8) % 24, (a + 12) % 24


def regime(i):
    u1 = ORBIT[i % 24] in UNITS
    u2 = ORBIT[(i + 1) % 24] in UNITS
    return ('U' if u1 else 'N') + ('U' if u2 else 'N')


def is_crown(i):
    return (i - 3) % 4 == 0


# ------------------------------------------------------------------ image path
def decode_png_luma(data):
    """8-bit, non-interlaced PNG -> (width, height, luminance rows). Alpha over white."""
    if data[:8] != bytes([137, 80, 78, 71, 13, 10, 26, 10]):
        raise ValueError('NOT-PNG')
    pos, idat, plte = 8, [], None
    w = h = bd = ct = il = None
    while pos < len(data):
        ln = struct.unpack('>I', data[pos:pos + 4])[0]
        typ = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if typ == b'IHDR':
            w, h, bd, ct, _c, _f, il = struct.unpack('>IIBBBBB', body)
        elif typ == b'PLTE':
            plte = body
        elif typ == b'IDAT':
            idat.append(body)
        elif typ == b'IEND':
            break
    if bd != 8 or il != 0 or ct not in (0, 2, 3, 4, 6):
        raise ValueError('UNSUPPORTED-PNG (need 8-bit non-interlaced; convert first)')
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(b''.join(idat))
    stride = w * ch
    prev = bytearray(stride)
    p = 0
    lum = []
    for _ in range(h):
        ft = raw[p]
        cur = bytearray(raw[p + 1:p + 1 + stride])
        p += 1 + stride
        if ft == 1:
            for i in range(ch, stride):
                cur[i] = (cur[i] + cur[i - ch]) & 255
        elif ft == 2:
            for i in range(stride):
                cur[i] = (cur[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                left = cur[i - ch] if i >= ch else 0
                cur[i] = (cur[i] + ((left + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = cur[i - ch] if i >= ch else 0
                b = prev[i]
                c = prev[i - ch] if i >= ch else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                cur[i] = (cur[i] + pr) & 255
        elif ft != 0:
            raise ValueError('BAD-PNG-FILTER')
        row = []
        for x in range(w):
            if ct == 0:
                y = cur[x]
            elif ct == 3:
                k = cur[x] * 3
                y = (299 * plte[k] + 587 * plte[k + 1] + 114 * plte[k + 2] + 500) // 1000
            elif ct == 4:
                g, al = cur[2 * x], cur[2 * x + 1]
                y = (g * al + 255 * (255 - al) + 127) // 255
            else:
                k = x * ch
                R, G, B = cur[k], cur[k + 1], cur[k + 2]
                if ct == 6:
                    al = cur[k + 3]
                    R = (R * al + 255 * (255 - al) + 127) // 255
                    G = (G * al + 255 * (255 - al) + 127) // 255
                    B = (B * al + 255 * (255 - al) + 127) // 255
                y = (299 * R + 587 * G + 114 * B + 500) // 1000
            row.append(y)
        lum.append(row)
        prev = cur
    return w, h, lum


def grid_from_luma(w, h, lum):
    """Centre-crop to a square, box-average to IMG_GRID x IMG_GRID with integer floor edges."""
    G = IMG_GRID
    s = min(w, h)
    if s < G:
        raise ValueError('TOO-SMALL (shorter side must be >= %d)' % G)
    x0, y0 = (w - s) // 2, (h - s) // 2
    edges = [(i * s) // G for i in range(G + 1)]
    grid = []
    for gy in range(G):
        ya, yb = y0 + edges[gy], y0 + edges[gy + 1]
        row = []
        for gx in range(G):
            xa, xb = x0 + edges[gx], x0 + edges[gx + 1]
            tot = 0
            for yy in range(ya, yb):
                tot += sum(lum[yy][xa:xb])
            row.append(tot // ((yb - ya) * (xb - xa)))
        grid.append(row)
    return grid


def median3(g):
    G = len(g)
    out = []
    for y in range(G):
        row = []
        for x in range(G):
            vals = sorted(g[min(G - 1, max(0, y + dy))][min(G - 1, max(0, x + dx))]
                          for dy in (-1, 0, 1) for dx in (-1, 0, 1))
            row.append(vals[4])
        out.append(row)
    return out


def count_components(q, min_cells):
    G = len(q)
    seen = [[False] * G for _ in range(G)]
    n = 0
    for sy in range(G):
        for sx in range(G):
            if seen[sy][sx]:
                continue
            v = q[sy][sx]
            seen[sy][sx] = True
            stack, area = [(sy, sx)], 0
            while stack:
                y, x = stack.pop()
                area += 1
                for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                    if 0 <= ny < G and 0 <= nx < G and not seen[ny][nx] and q[ny][nx] == v:
                        seen[ny][nx] = True
                        stack.append((ny, nx))
            if area >= min_cells:
                n += 1
    return n


def image_counts(w, h, lum):
    """M247 image rule. n1 = coarse regions; n3 = coarse+mid; n2 = coarse+mid+fine.
    Nested by construction, so n2 >= n3 >= n1."""
    g = median3(grid_from_luma(w, h, lum))
    c = [count_components([[v >> (8 - b) for v in row] for row in g], m)
         for b, m in zip(IMG_BITS, IMG_MINCELLS)]
    return c[0], c[0] + c[1] + c[2], c[0] + c[1]


# ------------------------------------------------------------------ audio path
def read_wav_mono(source):
    src = io.BytesIO(source) if isinstance(source, (bytes, bytearray)) else source
    w = wave.open(src)
    if w.getsampwidth() != 2:
        raise ValueError('UNSUPPORTED-WAV (need 16-bit PCM; convert first)')
    ch, sr = w.getnchannels(), w.getframerate()
    raw = w.readframes(w.getnframes())
    vals = struct.unpack('<%dh' % (len(raw) // 2), raw)
    if ch > 1:
        vals = [sum(vals[i:i + ch]) // ch for i in range(0, len(vals) - ch + 1, ch)]
    return sr, list(vals)


def to_analysis_rate(samples, sr):
    if sr < AUD_RATE:
        raise ValueError('RATE-TOO-LOW (need >= %d Hz)' % AUD_RATE)
    if sr == AUD_RATE:
        return list(samples)
    out = []
    for j in range((len(samples) * AUD_RATE) // sr):
        a, b = (j * sr) // AUD_RATE, ((j + 1) * sr) // AUD_RATE
        seg = samples[a:b]
        out.append(sum(seg) // len(seg))
    return out


def _runs(mask):
    n, prev = 0, False
    for m in mask:
        if m and not prev:
            n += 1
        prev = m
    return n


def _close_gaps(mask, g):
    out, L, i = list(mask), len(mask), 0
    while i < L:
        if not out[i]:
            j = i
            while j < L and not out[j]:
                j += 1
            if i > 0 and j < L and (j - i) <= g:
                for k in range(i, j):
                    out[k] = True
            i = j
        else:
            i += 1
    return out


def _drop_short(mask, minrun):
    out, L, i = list(mask), len(mask), 0
    while i < L:
        if out[i]:
            j = i
            while j < L and out[j]:
                j += 1
            if (j - i) < minrun:
                for k in range(i, j):
                    out[k] = False
            i = j
        else:
            i += 1
    return out


def audio_counts(samples8k):
    """M247 audio rule. Fine events = runs of active 20 ms frames; n3 and n1 come from
    closing gaps of <= 1 and <= 8 frames. Nested by construction (n2 >= n3 >= n1)."""
    E = [sum(x * x for x in samples8k[i:i + AUD_FRAME])
         for i in range(0, len(samples8k) - AUD_FRAME + 1, AUD_FRAME)]
    if len(E) < AUD_MIN_FRAMES:
        raise ValueError('TOO-SHORT')
    emax = max(E)
    if emax < AUD_MIN_EMAX:
        raise ValueError('NO-SIGNAL')
    mask = [e * AUD_RATIO[1] >= emax * AUD_RATIO[0] for e in E]
    mask = _drop_short(mask, AUD_MINRUN)
    return (_runs(_close_gaps(mask, AUD_GAPS[0])), _runs(mask), _runs(_close_gaps(mask, AUD_GAPS[1])))


# ------------------------------------------------------------------ perturbation family (M265 Check 4)
def _lcg(seed):
    s = seed
    while True:
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        yield (s >> 16) % 5 - 2          # -2 .. +2


def image_perturbations(w, h, lum):
    def clip(v):
        return 0 if v < 0 else (255 if v > 255 else v)
    rng = _lcg(7)
    out = {'bright+3': (w, h, [[clip(v + 3) for v in r] for r in lum]),
           'bright-3': (w, h, [[clip(v - 3) for v in r] for r in lum])}
    out['noise2'] = (w, h, [[clip(v + next(rng)) for v in r] for r in lum])
    out['shift+2'] = (w - 2, h - 2, [r[2:] for r in lum[2:]])
    out['shift-2'] = (w - 2, h - 2, [r[:-2] for r in lum[:-2]])
    return out


def audio_perturbations(s):
    def clip(v):
        return -32768 if v < -32768 else (32767 if v > 32767 else v)
    rng = _lcg(5)
    pk = max(abs(x) for x in s) or 1
    return {'gain0.5': [x // 2 for x in s],
            'gain1.25': [clip(x * 5 // 4) if pk * 5 // 4 <= 32767 else x for x in s],
            'dither2': [clip(x + next(rng)) for x in s],
            'trim10ms': s[80:],
            'requant10': [(x >> 6) << 6 for x in s]}


# ------------------------------------------------------------------ calibration inputs (generated, never stored)
def cal_image_simple():
    return 128, 128, [[40 if x < 42 else (128 if x < 86 else 220) for x in range(128)] for _ in range(128)]


def cal_image_complex():
    return 128, 128, [[30 if ((x // 32) + (y // 32)) % 2 == 0 else 220 for x in range(128)] for y in range(128)]


def _burst(frames, amp=8000):
    return [amp if (i // 20) % 2 == 0 else -amp for i in range(frames * AUD_FRAME)]


def cal_audio_simple():
    return _burst(50)


def cal_audio_complex():
    silence = lambda f: [0] * (f * AUD_FRAME)
    group = _burst(5) + silence(5) + _burst(5) + silence(5) + _burst(5)
    return group + silence(20) + group + silence(3)


CAL_EXPECTED = {'image-simple': (3, 9, 6), 'image-complex': (16, 48, 32),
                'audio-simple': (1, 1, 1), 'audio-complex': (2, 6, 6)}


def qualify():
    """M265 extractor qualification: determinism, content-sensitivity, hierarchy on calibration inputs."""
    got = {}
    w, h, l = cal_image_simple(); got['image-simple'] = image_counts(w, h, l)
    w, h, l = cal_image_complex(); got['image-complex'] = image_counts(w, h, l)
    got['audio-simple'] = audio_counts(cal_audio_simple())
    got['audio-complex'] = audio_counts(cal_audio_complex())
    ok_match = all(got[k] == CAL_EXPECTED[k] for k in CAL_EXPECTED)
    w, h, l = cal_image_simple()
    ok_det = image_counts(w, h, l) == got['image-simple'] and audio_counts(cal_audio_complex()) == got['audio-complex']
    ok_sens = got['image-complex'][1] > got['image-simple'][1] and got['audio-complex'][1] > got['audio-simple'][1]
    ok_hier = all(n2 >= n3 >= n1 >= 1 for (n1, n2, n3) in got.values())
    return {'counts': got, 'match': ok_match, 'determinism': ok_det,
            'content_sensitivity': ok_sens, 'hierarchy': ok_hier,
            'pass': ok_match and ok_det and ok_sens and ok_hier}


# ------------------------------------------------------------------ gate and navigation
def _gate(medium, base_counts, perturbed_counts, rerun_counts):
    n1, n2, n3 = base_counts
    a0 = determine_anchor(n1, n2, n3)[0]
    anchors = {k: determine_anchor(*c)[0] for k, c in perturbed_counts.items() if c is not None}
    c1 = (rerun_counts == base_counts)
    c3 = (n2 >= n3 >= n1 >= 1)
    stable = all(a == a0 for a in anchors.values()) and all(c is not None for c in perturbed_counts.values())
    flags = []
    if n2 < LOW_STRUCTURE_N2:
        flags.append('LOW-STRUCTURE')
    if not stable:
        flags.append('PERTURBATION-SENSITIVE')
    verdict = 'NOT NAVIGABLE' if not (c1 and c3) else ('NAVIGABLE' if not flags else 'NAVIGABLE WITH FLAGS')
    votes = Counter([a0] + list(anchors.values()))
    modal = votes.most_common(1)[0][0]
    return {'medium': medium, 'counts': base_counts, 'anchor': a0, 'check1_determinism': c1,
            'check3_hierarchy': c3, 'check4_stable': stable, 'perturbed_anchors': anchors,
            'modal_anchor': modal, 'flags': flags, 'verdict': verdict}


def analyse_image(data):
    w, h, lum = decode_png_luma(data)
    base = image_counts(w, h, lum)
    per = {}
    for k, (pw, ph, pl) in image_perturbations(w, h, lum).items():
        try:
            per[k] = image_counts(pw, ph, pl)
        except ValueError:
            per[k] = None
    g = _gate('image', base, per, image_counts(w, h, lum))
    g['bytes_sha256'] = hashlib.sha256(data).hexdigest()
    return g


def analyse_audio(data):
    sr, v = read_wav_mono(data)
    s = to_analysis_rate(v, sr)
    base = audio_counts(s)
    per = {}
    for k, ps in audio_perturbations(s).items():
        try:
            per[k] = audio_counts(ps)
        except ValueError:
            per[k] = None
    g = _gate('audio', base, per, audio_counts(s))
    g['bytes_sha256'] = hashlib.sha256(data).hexdigest()
    return g


def analyse(path):
    data = open(path, 'rb').read()
    ext = os.path.splitext(path)[1].lower()
    if ext == '.png':
        return analyse_image(data)
    if ext == '.wav':
        return analyse_audio(data)
    raise ValueError('UNSUPPORTED-FORMAT (convert to 8-bit PNG or 16-bit PCM WAV first)')


def report(path, label=''):
    q = qualify()
    print('======= M265 MEDIA NAVIGABILITY GATE =======')
    print('EXTRACTOR QUALIFICATION: %s' % ('PASS' if q['pass'] else 'FAIL'))
    try:
        g = analyse(path)
    except ValueError as e:
        print('INPUT: %s' % os.path.basename(path))
        print('VERDICT: NOT NAVIGABLE (%s)' % e)
        print('======= END M265 MEDIA NAVIGABILITY GATE =======')
        return None
    print('MEDIUM: %s | INPUT SHA-256: %s' % (g['medium'], g['bytes_sha256']))
    print('CHECK 1 (DETERMINISM): %s' % ('PASS' if g['check1_determinism'] else 'FAIL'))
    print('CHECK 2 (CONTENT-SENSITIVITY, on calibration pair): %s' % ('PASS' if q['content_sensitivity'] else 'FAIL'))
    print('CHECK 3 (HIERARCHY n2>=n3>=n1>=1): %s' % ('PASS' if g['check3_hierarchy'] else 'FAIL'))
    print('CHECK 4 (PERTURBATION STABILITY): %s | anchors under perturbation: %s'
          % ('STABLE' if g['check4_stable'] else 'UNSTABLE',
             ' '.join('%s=P%s' % (k, v) for k, v in g['perturbed_anchors'].items())))
    print('FLAGS: %s' % (', '.join(g['flags']) or 'NONE'))
    print('VERDICT: %s' % (g['verdict'] if q['pass'] else 'NOT NAVIGABLE (extractor failed qualification)'))
    print('======= END M265 MEDIA NAVIGABILITY GATE =======')
    n1, n2, n3 = g['counts']
    a, r1, r2, r3, tfi = determine_anchor(n1, n2, n3)
    print('======= M247 MEDIA EXTRACTION =======')
    print('LABEL (not counted): %s' % label)
    print('n1=%d n2=%d n3=%d | r1=%d r2=%d r3=%d | TFI=%.2f' % (n1, n2, n3, r1, r2, r3, tfi))
    yang, yin, fourd, ant = derive_arms(a)
    for nm, i in (('ANCHOR', a), ('YANG', yang), ('YIN', yin), ('4D', fourd), ('ANTIPODE', ant)):
        print('%s: P%d=%d (%s) regime=%s crown=%s' % (nm, i, ORBIT[i], POSITION_NAMES[i], regime(i), 'Y' if is_crown(i) else 'N'))
    ccd = sum(is_crown(i) for i in (a, yang, yin, fourd)) / 4
    mob = any(18 <= i <= 23 for i in (yang, yin, fourd))
    print('CCD=%s MOEBIUS=%s' % (ccd, 'ACTIVE' if mob else 'INACTIVE'))
    if 'PERTURBATION-SENSITIVE' in g['flags']:
        print('CONVERGENCE MAP: modal anchor P%d; anchors seen: %s; confine the reading to properties shared by every anchor.'
              % (g['modal_anchor'], sorted(set([g['anchor']] + list(g['perturbed_anchors'].values())))))
    print('======= END M247 MEDIA EXTRACTION =======')
    return g


def _lcg_wide(seed):
    s = seed
    while True:
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        yield s >> 4                       # 27 bits


def shuffled_control(path):
    """M266 structure control: destroy spatial/temporal arrangement, keep the value histogram.
    Returns the counts after shuffling, or None if no boundary structure survives."""
    ext = os.path.splitext(path)[1].lower()
    data = open(path, 'rb').read()
    rng = _lcg_wide(11)

    def shuffled(seq):
        out = list(seq)
        for i in range(len(out) - 1, 0, -1):
            j = next(rng) % (i + 1)
            out[i], out[j] = out[j], out[i]
        return out
    try:
        if ext == '.png':
            w, h, lum = decode_png_luma(data)
            sh = shuffled([v for r in lum for v in r])
            n = image_counts(w, h, [sh[y * w:(y + 1) * w] for y in range(h)])
        else:
            sr, v = read_wav_mono(data)
            s = to_analysis_rate(v, sr)
            nf = len(s) // AUD_FRAME
            frames = [s[i * AUD_FRAME:(i + 1) * AUD_FRAME] for i in range(nf)]
            n = audio_counts([x for f in shuffled(frames) for x in f])
    except ValueError:
        return None
    return n if n[0] >= 1 else None


def profile(paths):
    """M266 Media Corpus Profile over a Striker-supplied sample of media items."""
    rows = []
    for pth in paths:
        try:
            g = analyse(pth)
        except ValueError as e:
            rows.append((os.path.basename(pth), 'NOT NAVIGABLE', str(e), None, None))
            continue
        sc = shuffled_control(pth)
        sa = determine_anchor(*sc)[0] if sc is not None else None
        rows.append((os.path.basename(pth), g['verdict'], ','.join(g['flags']), g['anchor'], sa))
    n = len(rows)
    nav = [r for r in rows if r[1] != 'NOT NAVIGABLE']
    stable = [r for r in nav if 'PERTURBATION-SENSITIVE' not in r[2]]
    low = [r for r in nav if 'LOW-STRUCTURE' in r[2]]
    hist = Counter(r[3] for r in nav)
    changed = [r for r in nav if r[4] != r[3]]
    print('======= M266 MEDIA CORPUS PROFILE =======')
    print('ITEMS: %d | NAVIGABLE: %d | STABLE: %d | LOW-STRUCTURE: %d' % (n, len(nav), len(stable), len(low)))
    print('ANCHOR HISTOGRAM (navigable): %s' % dict(sorted(hist.items())))
    print('STRUCTURE CONTROL: anchor changed or extraction failed after shuffling in %d of %d navigable items' % (len(changed), len(nav)))
    print('SAMPLE-ONLY: this profiles the supplied sample, not the training set it was drawn from, and not what any model learned.')
    print('======= END M266 MEDIA CORPUS PROFILE =======')
    return rows


def calibrate():
    q = qualify()
    print('======= M211-AV PRE-NAVIGATION CALIBRATION =======')
    for k in CAL_EXPECTED:
        print('%s: expected %s | actual %s | %s' % (k, CAL_EXPECTED[k], q['counts'][k], 'PASS' if q['counts'][k] == CAL_EXPECTED[k] else 'FAIL'))
    print('determinism=%s content_sensitivity=%s hierarchy=%s' % (q['determinism'], q['content_sensitivity'], q['hierarchy']))
    print('CALIBRATION-AV: %s' % ('PASS' if q['pass'] else 'FAIL'))
    print('======= END M211-AV PRE-NAVIGATION CALIBRATION =======')
    return q['pass']


if __name__ == '__main__':
    if len(sys.argv) >= 2 and sys.argv[1] == '--calibrate-av':
        sys.exit(0 if calibrate() else 1)
    elif len(sys.argv) >= 3 and sys.argv[1] == '--navigate':
        report(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '')
    elif len(sys.argv) >= 3 and sys.argv[1] == '--profile':
        profile(sys.argv[2:])
    else:
        print('usage: --calibrate-av | --navigate FILE [LABEL] | --profile FILE...')
# ===== canonical_reference_av.py END =====
