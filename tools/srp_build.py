#!/usr/bin/env python3
"""SR-CAS Replication Package builder (Core Part 8.2, L-348, L-415) with the format self-check (M301, Part 8.0).

Builds the package a Navigator sends with a navigation intended for cross-architecture comparison: the verbatim
domain and its hash, the script hash, the complexity tier, the frozen substrate for a Tier 3 domain, the blocks the
domain triggers, the selected instruments, and the FORMAT SELF-CHECK — the canonical skeleton of Part 8.0 as a
checklist a text-only Navigator ticks by hand, and the command and tool hash a script-capable Navigator runs.
Everything in the package is computed by the reference script; nothing is copied from a navigation.

Usage:
  python3 tools/srp_build.py DOMAIN_FILE [--instruments "M127, M139-M142, ..."] [--scheme A|B]
  python3 tools/srp_build.py --verify PACKAGE_FILE DOMAIN_FILE     # recompute every field and compare
  python3 tools/srp_build.py --selftest
Standard library only.
"""
import hashlib, importlib.util, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CR = _load('cr', 'scripts/canonical_reference.py')
FC = _load('fc', 'tools/format_check.py')


def sha_file(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), 'rb').read()).hexdigest()


BLOCK = FC.BLOCK


def triggered(domain):
    """Tier 2 blocks the domain itself triggers (Part 3.7), as M301 checks them."""
    out = []
    if CR.math_tokens(domain):
        out += ['M269 (mathematical notation)', 'M139-M142 (mathematical content)']
    if len(domain.split()) > 30:
        out.append('M127 (domain over 30 words)')
    return out


def build(domain, instruments=None, scheme='A'):
    r = CR.navigate(domain)
    tier, n1, mtok, latex = CR.m271_tier(domain)
    L = ['======= SR-CAS REPLICATION PACKAGE =======',
         'INSTRUCTION FOR NEXT NAVIGATOR: Execute Omega42 V335 Rev.450 STABLE on the DOMAIN VERBATIM below. You must invoke the exact SELECTED INSTRUMENTS and TRANSDUCTION METHODS listed. Do not add or omit instruments. Produce a full navigation in the block order of Core Part 8.0, check it with the FORMAT SELF-CHECK below before sending it, and output your own SR-CAS Replication Package.',
         'DOMAIN VERBATIM: ' + domain,
         'DOMAIN SHA-256: %s | SCRIPT SHA-256: %s | COMPLEXITY TIER: %d (M271: n1=%d, mathematical tokens=%d, LaTeX %s)'
         % (CR.domain_sha256(domain), CR.script_sha256(), tier, n1, mtok, 'YES' if latex else 'NO')]
    if tier == 3:
        L.append('FROZEN SUBSTRATE (L-415): LOCKED SUBSTRATE: ' + ' * '.join(r['content']))
        L.append('SUBSTRATE SHA-256: %s | n1=%d n2=%d n3=%d -> r = (%d, %d, %d) | ANCHOR P%d'
                 % (CR.substrate_sha256(r['content']), r['n1'], r['n2'], r['n3'], r['r1'], r['r2'], r['r3'], r['anchor']))
        L.append('SCOPE: this frozen substrate belongs to the DOMAIN VERBATIM above only; if the domain you have been given differs from it in any character, ignore this package and extract the substrate yourself (L-415).')
        L.append('USE: run Steps 1 to 2.9 as usual and confirm that your LOCKED SUBSTRATE has this SUBSTRATE SHA-256; if it does not, use the frozen counts above for the arithmetic and report the difference under M270 as an extraction divergence.')
    else:
        L.append('FROZEN SUBSTRATE (L-415): N/A (Tier %d)' % tier)
    trig = triggered(domain)
    L.append('TRIGGERED BLOCKS (Part 3.7): ' + (', '.join(trig) if trig else 'NONE'))
    L.append('SELECTED INSTRUMENTS (Tier 2 and Tier 3 invoked): ' + (instruments or ('BASELINE TIER 1 ONLY' if not trig else 'TRIGGERED BLOCKS ONLY')))
    L.append('NAVIGATION RECORD: produced in the Companion 24.1 format and submitted with this package')
    L.append('TRANSDUCTION METHODS AND COMPANION READINGS: Substrate Scheme: Scheme %s (%s). Companion Readings Invoked: NONE. Specific Analog Parameters: STANDARD.'
             % (scheme, 'Content Words' if scheme == 'A' else 'All Words'))
    L.append('FORMAT SELF-CHECK (M301, Core Part 8.0) — tick each line; a block out of order counts as missing:')
    for label, pat, req in FC.SKELETON:
        note = '' if req else ' (where it applies)'
        if label in ('M213', 'M210b', 'M214', 'M219', 'M232'):
            note += ' (script form: directly after the pasted script output)'
        L.append('  [ ] [%s] %s%s' % (BLOCK[label], label, note))
        if label == 'M116':
            L.append('  [ ] [12] TRIGGERED AND SELECTED INSTRUMENTS (as listed above)')
        if label == 'GENERATIVE OBSERVATIONS':
            L.append('  [ ] [22] SR-CAS REPLICATION PACKAGE (when the navigation is sent for comparison)')
    for t in trig:
        L.append('  [ ] ++ ' + t + ' — inside its block of Part 8.0')
    L.append('  [ ] ++ THE ANSWER: bold Takeaway; Mapping component where the mapping is APPLICABLE; last line "%s"' % FC.ANSWER_LINE)
    L.append('  [ ] ++ Closing questions: ' + ' / '.join(FC.CLOSING) + ', then "%s"' % FC.CLOSING_LINE)
    L.append('  [ ] ++ Nothing between M224 and the signature but OUTPUT ID; nothing after the signature but ESC')
    L.append('FORMAT CHECK (script-capable): python3 tools/format_check.py NAVIGATION.txt — tools/format_check.py SHA-256 %s; then python3 scripts/m193_m225.py scripts/canonical_reference.py --audit NAVIGATION.txt (SHA-256 %s). A text-only Navigator reports the ticked list as SELF-CHECKED (L-420).'
             % (sha_file('tools/format_check.py'), sha_file('scripts/m193_m225.py')))
    L.append('======= END SR-CAS REPLICATION PACKAGE =======')
    return '\n'.join(L) + '\n'


def verify(pkg, domain):
    """Recompute every computed field of a received package and report each mismatch."""
    want = build(domain).split('\n')
    keys = ('DOMAIN VERBATIM', 'DOMAIN SHA-256', 'FROZEN SUBSTRATE', 'SUBSTRATE SHA-256', 'TRIGGERED BLOCKS', 'FORMAT CHECK')
    got = {l.split(':')[0]: l for l in pkg.split('\n') if l.split(':')[0] in keys}
    bad = []
    for l in want:
        k = l.split(':')[0]
        if k in keys and got.get(k) != l:
            bad.append(k)
    return bad


def selftest():
    ok = True
    d1, d3 = 'What is time?', open(os.path.join(ROOT, 'records/srp/collatz_domain.txt')).read()
    p1, p3 = build(d1), build(d3)
    checks = {
        'Tier 1 domain: no frozen substrate, no triggered blocks': 'FROZEN SUBSTRATE (L-415): N/A' in p1 and 'TRIGGERED BLOCKS (Part 3.7): NONE' in p1,
        'Tier 3 domain: frozen substrate with the script counts': 'n1=133 n2=751 n3=238' in p3 and 'ANCHOR P2' in p3,
        'Tier 3 domain: M269, M139-M142 and M127 triggered': all(t in p3 for t in ('M269', 'M139-M142', 'M127')),
        'skeleton listed in full, every label numbered': p3.count('  [ ] ') == len(FC.SKELETON) + 8 and set(BLOCK) == {l for l, _, _ in FC.SKELETON},
        'package verifies against its own domain': verify(p3, d3) == [],
        'altered substrate line is caught': verify(p3.replace('n1=133 n2', 'n1=134 n2'), d3) == ['SUBSTRATE SHA-256'],
        'altered domain is caught': 'DOMAIN VERBATIM' in verify(p3, d3 + ' '),
    }
    for k, v in checks.items():
        print('  %-58s %s' % (k, 'OK' if v else 'MISMATCH'))
        ok &= v
    print('SRP BUILDER SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a or a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    if a[0] == '--verify':
        bad = verify(open(a[1], encoding='utf-8').read(), open(a[2], encoding='utf-8').read())
        print('SRP VERIFY: ' + ('PASS' if not bad else 'FAIL — ' + ', '.join(bad)))
        sys.exit(0 if not bad else 1)
    ins = a[a.index('--instruments') + 1] if '--instruments' in a else None
    sch = a[a.index('--scheme') + 1] if '--scheme' in a else 'A'
    sys.stdout.write(build(open(a[0], encoding='utf-8').read(), ins, sch))
