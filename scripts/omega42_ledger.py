# ===== omega42_ledger.py BEGIN =====
#!/usr/bin/env python3
"""omega42_ledger.py -- reference append-only ledger for Companion Part 24.

STATUS: reference implementation, run only on constructed cases and not validated on real navigations.
NOT part of the protocol specification. Part 24.1 specifies the record format and
leaves storage to the Striker's own deployment; this file is one such deployment.

What it does
  * stores Navigation Records (24.1) and Negative Result entries (24.2), one JSON
    object per line, each chained to the previous by SHA-256, so any later edit,
    deletion or reordering is detected by `verify`;
  * validates every record against the 24.1 / 24.2 field lists before appending;
  * checks the arithmetic inside a navigation record (r = dr(5n), anchor by
    majority vote, arm offsets) so an internally inconsistent record is refused;
  * checks that the record carries its domain, substrate and script hashes (L-414, L-415, L-417)
    and its temporal state: M273 anchors from an external time source, and the knowledge boundary (L-430);
  * optionally recomputes n1, n2, n3 and both content hashes from domain_verbatim with
    canonical_reference.py, refusing a record computed under a different script version.

What it does not do
  * it cannot prove a record is true, only that it is unchanged since it was appended;
  * it does not store Striker-Side Journal content (24.3), which the Navigator never accesses.

M91-2 (Execute-Do-Not-Recall): records must never be fed back into a Navigator during a
navigation. `query` refuses to run while OMEGA42_NAVIGATION_ACTIVE=1 is set.

Usage
  python3 omega42_ledger.py append LEDGER RECORD.json [--canonical PATH_TO_canonical_reference.py]
  python3 omega42_ledger.py verify LEDGER
  python3 omega42_ledger.py query  LEDGER [--anchor N] [--navigator NAME]
"""
import hashlib, json, os, re, sys
from collections import Counter

GENESIS = '0' * 64
ORBIT_NAMES = ['Seed', 'Fixpoint', 'Generator', 'Desire', 'Unity', 'Law', 'Seed/Causal', 'Navigator',
               'Generation', 'Fixpoint', 'Unity', 'Question', 'Opening', 'Gap', 'Observer', 'Other', 'Flow',
               'Seed/Return', 'Threshold', 'Time', 'Reckoning', 'Sublime', 'Collective', 'Return']
ORBIT = [2, 5, 7, 3, 1, 4, 5, 9, 5, 5, 1, 6, 7, 4, 2, 6, 8, 5, 4, 9, 4, 4, 8, 3]

# ---- field lists exactly as written in Companion 24.1 and 24.2 ----
NAV_FIELDS = ['navigation_id', 'protocol_version', 'navigator', 'date', 'domain_verbatim', 'arithmetic', 'anchor',
              'arms', 'flags', 'fidelity', 'convergence_map', 'instruments_invoked', 'gaps', 'answer_hash', 'hashes', 'temporal_state']
HASH_FIELDS = ['domain_sha256', 'substrate_sha256', 'script_sha256']   # L-414, L-415, L-417
NEG_FIELDS = ['navigation_id', 'domain_verbatim', 'anchor', 'issue_observed', 'gaps', 'what_would_need_to_change']


def digital_root(n):
    n = abs(int(n))
    return 9 if n == 0 else 1 + (n - 1) % 9


def anchor_from_counts(n1, n2, n3):
    r = [digital_root(5 * n) for n in (n1, n2, n3)]
    top, freq = Counter(r).most_common(1)[0]
    return (top if freq >= 2 else r[0]), r


def _canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def _hash(seq, prev, kind, record):
    return hashlib.sha256(_canon({'seq': seq, 'prev': prev, 'kind': kind, 'record': record}).encode('utf-8')).hexdigest()


def validate_navigation(r):
    errs = []
    for f in NAV_FIELDS:
        if f not in r:
            errs.append('missing field: ' + f)
    if errs:
        return errs
    if not isinstance(r['navigator'], dict) or not r['navigator'].get('name') or not r['navigator'].get('organisation'):
        errs.append('navigator needs name and organisation')
    else:
        nm = r['navigator']['name'].lower()
        if 'multi-navigator' in nm or nm in ('the navigator', 'ensemble'):
            errs.append('navigator name is a collective or generic label (Part 0.0 signature rule)')
    a = r['arithmetic']
    for k in ('n1', 'n2', 'n3', 'r1', 'r2', 'r3'):
        if not isinstance(a.get(k), int):
            errs.append('arithmetic.%s must be an integer' % k)
    if not errs:
        for i, k in enumerate(('n1', 'n2', 'n3')):
            if a['r%d' % (i + 1)] != digital_root(5 * a[k]):
                errs.append('arithmetic.r%d != dr(5*%s)' % (i + 1, k))
        anchor, _ = anchor_from_counts(a['n1'], a['n2'], a['n3'])
        an = r['anchor']
        if an.get('position') != anchor:
            errs.append('anchor.position %s != majority-vote anchor %s' % (an.get('position'), anchor))
        else:
            if an.get('value') != ORBIT[anchor % 24]:
                errs.append('anchor.value does not match the orbit value at that position')
            if an.get('character') != ORBIT_NAMES[anchor % 24]:
                errs.append('anchor.character does not match the position name')
            ar = r['arms']
            want = {'yang': (anchor + 5) % 24, 'yin': (anchor + 18) % 24, '4d': (anchor + 8) % 24, 'antipode': (anchor + 12) % 24}
            for k, v in want.items():
                got = ar.get(k)
                if got != v:
                    errs.append('arms.%s position %s != %s' % (k, got, v))
    if not re.fullmatch(r'[0-9a-f]{64}', str(r['answer_hash'])):
        errs.append('answer_hash must be 64 hex characters')
    if not isinstance(r['hashes'], dict):
        errs.append('hashes must be an object')
    else:
        for k in HASH_FIELDS:
            if not re.fullmatch(r'[0-9a-f]{64}', str(r['hashes'].get(k, ''))):
                errs.append('hashes.%s must be 64 hex characters' % k)
    ts = r['temporal_state']
    if not isinstance(ts, dict) or not isinstance(ts.get('anchors'), list) or not isinstance(ts.get('knowledge_boundary'), dict):
        errs.append('temporal_state must hold an anchors list and a knowledge_boundary object (M273)')
    else:
        states = {'SUBSTRATE_LOCKED', 'SYNTHESIS_FROZEN', 'COMPARATIVE_PERSPECTIVE_OPENED', 'COMPARATIVE_MATERIAL_INGESTED', 'REVIEW_COMPLETED'}
        for a in ts['anchors']:
            if not isinstance(a, dict) or a.get('state') not in states or not str(a.get('utc', '')).endswith('Z') \
                    or not str(a.get('time_source', '')).strip() or not isinstance(a.get('independently_checked'), bool):
                errs.append('each temporal anchor needs state, utc (ISO 8601, Z), time_source and independently_checked (M273)')
                break
        if not any(isinstance(a, dict) and a.get('state') == 'SUBSTRATE_LOCKED' for a in ts['anchors']):
            errs.append('temporal_state needs a SUBSTRATE_LOCKED anchor (M273)')
    if not isinstance(r['gaps'], list):
        errs.append('gaps must be a list')
    for k in ('tier2', 'tier3'):
        if k not in r['instruments_invoked']:
            errs.append('instruments_invoked.%s missing' % k)
    for k in ('tfi', 'ccd', 'mobius', 'pab'):
        if k not in r['flags']:
            errs.append('flags.%s missing' % k)
        elif k in ('tfi', 'ccd') and (isinstance(r['flags'][k], bool) or not isinstance(r['flags'][k], (int, float))):
            errs.append('flags.%s must be a number' % k)
        elif k in ('mobius', 'pab') and not isinstance(r['flags'][k], bool):
            errs.append('flags.%s must be true or false' % k)
    for k in ('sas', 'acs', 'sri', 'crs', 'pnfa'):
        if k not in r['fidelity']:
            errs.append('fidelity.%s missing' % k)
        else:
            v = r['fidelity'][k]
            if v is not None and (isinstance(v, bool) or not isinstance(v, str if k == 'pnfa' else (int, float))):
                errs.append('fidelity.%s must be %s or null' % (k, 'text' if k == 'pnfa' else 'a number'))
    for k in ('minimal', 'pb5l1', 'pb5l2', 'robust_core'):
        if k not in r['convergence_map']:
            errs.append('convergence_map.%s missing' % k)
    return errs


def validate_negative(r):
    errs = ['missing field: ' + f for f in NEG_FIELDS if f not in r]
    return errs


def check_against_canonical(record, module_path):
    """Recompute n1, n2, n3 from domain_verbatim with canonical_reference.py; return list of mismatches."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('canon', module_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    h = record['hashes']
    if h['domain_sha256'] != mod.domain_sha256(record['domain_verbatim']):
        return ['hashes.domain_sha256 does not match domain_verbatim (L-414)']
    if h['script_sha256'] != mod.script_sha256(module_path):
        return ['record was computed under a different canonical_reference.py (SCRIPT SHA-256 differs, L-417): '
                're-derive it under the current script (M270), or append without --canonical']
    res = mod.navigate(record['domain_verbatim'])
    a = record['arithmetic']
    out = []
    for k in ('n1', 'n2', 'n3'):
        if res[k] != a[k]:
            out.append('%s: record %s, canonical script %s' % (k, a[k], res[k]))
    if h['substrate_sha256'] != mod.substrate_sha256(res['content']):
        out.append('hashes.substrate_sha256 does not match the canonical locked substrate (L-415)')
    return out


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding='utf-8') as fh:
        return [json.loads(line) for line in fh if line.strip()]


def verify(path):
    prev, problems = GENESIS, []
    for i, e in enumerate(_read(path)):
        if e['seq'] != i:
            problems.append('entry %d: sequence number %s' % (i, e['seq']))
        if e['prev'] != prev:
            problems.append('entry %d: chain broken (prev hash mismatch)' % i)
        if _hash(e['seq'], e['prev'], e['kind'], e['record']) != e['hash']:
            problems.append('entry %d: contents do not match their hash' % i)
        prev = e['hash']
    return problems


def append(path, kind, record, canonical=None):
    errs = validate_navigation(record) if kind == 'navigation' else validate_negative(record)
    if not errs and kind == 'navigation' and canonical:
        errs = check_against_canonical(record, canonical)
    if errs:
        raise ValueError('; '.join(errs))
    problems = verify(path)
    if problems:
        raise RuntimeError('ledger fails verification, refusing to append: ' + problems[0])
    entries = _read(path)
    seq = len(entries)
    prev = entries[-1]['hash'] if entries else GENESIS
    e = {'seq': seq, 'prev': prev, 'kind': kind, 'record': record, 'hash': _hash(seq, prev, kind, record)}
    with open(path, 'a', encoding='utf-8') as fh:
        fh.write(_canon(e) + '\n')
    return e['hash']


def query(path, anchor=None, navigator=None):
    if os.environ.get('OMEGA42_NAVIGATION_ACTIVE') == '1':
        raise PermissionError('M91-2: records may not be read while a navigation is active')
    out = []
    for e in _read(path):
        r = e['record']
        if anchor is not None:
            pos = r.get('anchor', {}).get('position') if isinstance(r.get('anchor'), dict) else r.get('anchor')
            if pos != anchor:
                continue
        if navigator is not None and r.get('navigator', {}).get('name') != navigator:
            continue
        out.append(e)
    return out


def record_from_navigation(nav, navigator_name, organisation, answer_text, date, protocol_version='V335 Rev.449 STABLE',
                           navigation_id=None, fidelity=None, convergence_map=None, tier2=None, tier3=None, gaps=None):
    """Build a 24.1 record from canonical_reference.navigate() output (a dict)."""
    a = nav['anchor']
    arms = {'yang': nav['yang_i'], 'yin': nav['yin_i'], '4d': nav['fourd_i'], 'antipode': nav['antipode_i']}
    return {
        'navigation_id': navigation_id or hashlib.sha256((nav['domain'] + date).encode()).hexdigest()[:12],
        'protocol_version': protocol_version,
        'navigator': {'name': navigator_name, 'organisation': organisation},
        'date': date, 'domain_verbatim': nav['domain'],
        'arithmetic': {k: nav[k] for k in ('n1', 'n2', 'n3', 'r1', 'r2', 'r3')},
        'anchor': {'position': a, 'character': ORBIT_NAMES[a % 24], 'value': ORBIT[a % 24]},
        'arms': arms,
        'flags': {'tfi': nav['tfi'], 'ccd': nav['ccd'], 'mobius': nav['mobius'], 'pab': nav['pab']},
        'fidelity': fidelity or {'sas': None, 'acs': None, 'sri': None, 'crs': None, 'pnfa': None},
        'convergence_map': convergence_map or {'minimal': None, 'pb5l1': None, 'pb5l2': None, 'robust_core': None},
        'instruments_invoked': {'tier2': tier2 or [], 'tier3': tier3 or []},
        'gaps': gaps or [],
        'answer_hash': hashlib.sha256(answer_text.encode('utf-8')).hexdigest(),
    }


if __name__ == '__main__':
    av = sys.argv[1:]
    if not av:
        print(__doc__)
        sys.exit(0)
    try:
        if av[0] == 'append':
            canon = av[av.index('--canonical') + 1] if '--canonical' in av else None
            rec = json.load(open(av[2]))
            kind = 'negative_result' if 'issue_observed' in rec else 'navigation'
            print('appended', append(av[1], kind, rec, canon))
        elif av[0] == 'verify':
            p = verify(av[1]); print('LEDGER INTACT' if not p else 'LEDGER BROKEN: ' + '; '.join(p)); sys.exit(1 if p else 0)
        elif av[0] == 'query':
            an = int(av[av.index('--anchor') + 1]) if '--anchor' in av else None
            nv = av[av.index('--navigator') + 1] if '--navigator' in av else None
            for e in query(av[1], an, nv):
                print(e['seq'], e['kind'], e['record'].get('navigation_id'), e['record'].get('domain_verbatim'))
        else:
            print(__doc__)
    except (ValueError, RuntimeError, PermissionError) as ex:
        print('REFUSED:', ex); sys.exit(2)
# ===== omega42_ledger.py END =====
