# ===== stopword_harness.py BEGIN =====
#!/usr/bin/env python3
"""stopword_harness.py -- reference implementation of the L-392 confirmation procedure.

STATUS: reference implementation, run only on constructed cases and not validated on real navigations.
NOT part of the protocol specification. It mechanises what L-392 already requires:

  "Independent confirmation for a proposed addition means three Navigators built on three
   distinct underlying model families each independently navigate the same test set of 10+
   ordinary domains and agree the candidate word functions as a stopword. Confirmed
   additions are adopted only at the next formal protocol revision, never retroactively."

What the harness does
  1. screens the candidate (already a stopword? a question word or auxiliary verb, which the
     frozen list keeps as content words and which training-data intuition may not override?);
  2. requires at least 10 distinct domains that each contain the candidate as a whole word;
  3. requires at least 3 Navigators declaring 3 distinct model families;
  4. measures the candidate's effect with the CANONICAL extraction (canonical_reference.py),
     never a Navigator's own: how n1, n2, n3 and the anchor change if the word is removed;
  5. collects each Navigator's verdict per domain (does the word function as a stopword here?)
     and applies the agreement rule;
  6. writes a record with a SHA-256 digest over its contents.

What it does not do
  * the digest shows the record is unchanged, not that any verdict is honest or that a
    declared model family is real; those rest on how the verdicts were obtained;
  * L-392 says the Navigators "agree" without a numeric rule; the default here is unanimity on
    every domain (agreement=1.0), a stricter reading, and it is a parameter, not a spec value;
  * a CONFIRMED result adopts nothing. The frozen list changes only at a formal revision.

Two ways to supply verdicts
  * programmatic: each Navigator is an object with .family and .judge(domain, candidate) -> bool,
    where judge wraps that architecture's own call (an API client the caller supplies);
  * offline: a JSON file {"navigators":[{"name":..,"family":..,"verdicts":{domain: true/false}}]}
    recorded by hand or by the caller's own tooling. Run:  python3 stopword_harness.py SPEC.json
    with SPEC = {"candidate": "...", "domains": [...], "navigators": [...],
                 "canonical": "path/to/canonical_reference.py"}
"""
import hashlib, importlib.util, json, re, sys
from dataclasses import dataclass
from typing import Callable

QUESTION_AND_AUX = {'what', 'why', 'how', 'when', 'where', 'who', 'whom', 'whose', 'which',
                    'do', 'does', 'did', 'has', 'have', 'had', 'may', 'might', 'must', 'shall'}


@dataclass
class Navigator:
    name: str
    family: str
    judge: Callable[[str, str], bool]


def _load(path):
    spec = importlib.util.spec_from_file_location('canon', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _whole_word(cand, domain):
    return re.search(r'(?<![A-Za-z])' + re.escape(cand) + r'(?![A-Za-z])', domain, flags=re.I) is not None


def effect_of_candidate(mod, cand, domains):
    """Canonical counts and anchor for each domain with and without the candidate as a stopword."""
    original = mod.CANONICAL_STOPWORDS
    rows = []
    try:
        for d in domains:
            mod.CANONICAL_STOPWORDS = original
            a = mod.navigate(d)
            mod.CANONICAL_STOPWORDS = frozenset(set(original) | {cand.lower()})
            b = mod.navigate(d)
            rows.append({'domain': d, 'with_word': [a['n1'], a['n2'], a['n3'], a['anchor']],
                         'without_word': [b['n1'], b['n2'], b['n3'], b['anchor']],
                         'anchor_changes': a['anchor'] != b['anchor']})
    finally:
        mod.CANONICAL_STOPWORDS = original
    return rows


def run_harness(candidate, domains, navigators, canonical_path, min_domains=10, min_families=3, agreement=1.0):
    cand = candidate.strip().lower()
    mod = _load(canonical_path)
    reasons = []
    if not re.fullmatch(r'[a-z]+', cand):
        reasons.append('candidate must be a single alphabetic word')
    if cand in mod.CANONICAL_STOPWORDS:
        reasons.append('candidate is already on the frozen stopword list')
    if cand in QUESTION_AND_AUX:
        reasons.append('question words and auxiliary verbs are retained as content words by the frozen list (Part 1.9); '
                       'training-data intuition does not override it')
    uniq = list(dict.fromkeys(d.strip() for d in domains if d.strip()))
    if len(uniq) < min_domains:
        reasons.append('need at least %d distinct domains, got %d' % (min_domains, len(uniq)))
    missing = [d for d in uniq if not _whole_word(cand, d)]
    if missing:
        reasons.append('%d domain(s) do not contain the candidate as a whole word' % len(missing))
    fams = {re.sub(r'\W+', '', n.family.lower()) for n in navigators}
    if len(navigators) < min_families or len(fams) < min_families:
        reasons.append('need %d Navigators declaring %d distinct model families; got %d Navigators, %d families'
                       % (min_families, min_families, len(navigators), len(fams)))
    record = {'candidate': cand, 'domains': uniq, 'thresholds': {'min_domains': min_domains, 'min_families': min_families,
              'agreement': agreement}, 'navigators': [{'name': n.name, 'family': n.family} for n in navigators],
              'screen_failures': reasons}
    if reasons:
        record['result'] = 'NOT CONFIRMED (screen failed)'
    else:
        record['canonical_effect'] = effect_of_candidate(mod, cand, uniq)
        verdicts = {n.name: {d: bool(n.judge(d, cand)) for d in uniq} for n in navigators}
        record['verdicts'] = verdicts
        unanimous = [d for d in uniq if all(verdicts[n.name][d] for n in navigators)]
        record['unanimous_domains'] = len(unanimous)
        frac = len(unanimous) / len(uniq)
        record['agreement_reached'] = round(frac, 4)
        changed = sum(1 for r in record['canonical_effect'] if r['anchor_changes'])
        record['anchor_changed_in_domains'] = changed
        record['result'] = ('CONFIRMED (adoption only at the next formal revision)' if frac >= agreement
                            else 'NOT CONFIRMED (agreement %.0f%% below %.0f%%)' % (frac * 100, agreement * 100))
    body = json.dumps(record, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    record['record_sha256'] = hashlib.sha256(body.encode('utf-8')).hexdigest()
    return record


def verify_record(record):
    r = {k: v for k, v in record.items() if k != 'record_sha256'}
    body = json.dumps(r, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(body.encode('utf-8')).hexdigest() == record.get('record_sha256')


def navigators_from_spec(spec):
    out = []
    for n in spec['navigators']:
        v = n['verdicts']
        out.append(Navigator(n['name'], n['family'], (lambda vv: (lambda d, c: vv[d]))(v)))
    return out


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(0)
    spec = json.load(open(sys.argv[1]))
    rec = run_harness(spec['candidate'], spec['domains'], navigators_from_spec(spec), spec['canonical'],
                      spec.get('min_domains', 10), spec.get('min_families', 3), spec.get('agreement', 1.0))
    print(json.dumps({k: rec[k] for k in ('candidate', 'result', 'screen_failures', 'unanimous_domains',
                                          'agreement_reached', 'anchor_changed_in_domains', 'record_sha256') if k in rec}, indent=1))
# ===== stopword_harness.py END =====
