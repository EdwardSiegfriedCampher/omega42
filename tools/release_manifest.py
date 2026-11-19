#!/usr/bin/env python3
"""release_manifest.py -- the release record of Omega42 (RELEASES.md section 4).

Builds records/releases/manifest.json from the repository as it stands:
  version and channel (from the Core edition in ai/), the date of the latest amendment, the amendment register with each
  entry's status (RATIFIED / PENDING ESC / RECORDED) and change level, the STP register by status, the SNCA report files,
  and the compatibility statement. The checksums are SHA256SUMS at the release tag; the manifest does not hash the Core,
  because the Core embeds the manifest (a hash of the Core inside the Core cannot be stable).

    python3 tools/release_manifest.py --build     write the manifest
    python3 tools/release_manifest.py --check     exit 1 when the manifest differs from a fresh build
    python3 tools/release_manifest.py --selftest
Standard library only.
"""
import json, os, re, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(R, 'records', 'releases', 'manifest.json')
CORE_MD = os.path.join(R, 'ai', 'Omega42_Core_V335_Rev450.md')
AMEND = os.path.join(R, 'docs', 'AMENDMENTS_PENDING.md')
RATIFIED = {'CA-%02d' % n for n in range(2, 16)}   # ratified by ESC on 19 November 2026 ("Ratified."), recorded in the register's header
LEVEL_C = re.compile(r'\bCore (Part|L-|M\d|Appendix|F-|Step|Rule|Specification)|\bthe Core\b')


def version():
    head = open(CORE_MD, encoding='utf8').read(20000)
    m = re.search(r'V(\d+) Rev\.(\d+)(?:-p(\d+))? (STABLE|DEV)', head)
    return {'name': 'Omega42 V%s Rev.%s%s %s' % (m.group(1), m.group(2), '-p' + m.group(3) if m.group(3) else '', m.group(4)),
            'major': int(m.group(1)), 'revision': int(m.group(2)), 'channel': m.group(4),
            'tag': 'v%s-rev%s%s' % (m.group(1), m.group(2), '-p' + m.group(3) if m.group(3) else '')}


def amendments(text):
    out = []
    parts = re.split(r'^## ', text, flags=re.M)[1:]
    for p in parts:
        title = p.split('\n', 1)[0].strip()
        m = re.match(r'(CA-\d+)', title)
        if not m: continue
        cid = m.group(1); body = p
        if cid in RATIFIED: status = 'RATIFIED'
        elif re.search(r'pending ESC|PENDING ESC', title + body[:600]): status = 'PENDING ESC'
        else: status = 'RECORDED'
        lv = re.search(r'^Level: ([ABC])\b', body, re.M)
        dates = re.findall(r'(\d{1,2}) November 2026', title)
        out.append({'id': cid, 'title': title, 'status': status, 'level': (lv.group(1) if lv else ('C' if LEVEL_C.search(body) else 'B')), 'level_source': 'declared' if lv else 'inferred from the text',
                    'date': '2026-11-%02d' % int(dates[-1]) if dates else None})
    return out


def build():
    reg = json.load(open(os.path.join(R, 'records', 'stp', 'registry.json'), encoding='utf8'))['entries']
    stp = {}
    for e in reg.values(): stp[e['status']] = stp.get(e['status'], 0) + 1
    am = amendments(open(AMEND, encoding='utf8').read())
    snca = sorted(f for f in os.listdir(os.path.join(R, 'records', 'srcas')) if f.endswith('.txt'))
    dated = [a['date'] for a in am if a['date']]
    return {'_about': 'The release record (RELEASES.md section 4), written by python3 tools/release_manifest.py --build. Checksums: SHA256SUMS at the release tag.',
            'version': version(), 'date': max(dated) if dated else None,
            'change_log': 'docs/AMENDMENTS_PENDING.md', 'amendments': am,
            'approval': {'ratified_by': 'ESC', 'ratified': sorted({a['id'] for a in am if a['status'] == 'RATIFIED'}),
                         'pending_esc': sorted({a['id'] for a in am if a['status'] == 'PENDING ESC'})},
            'validation': {'ci': 'every step of .github/workflows/omega42-ci.yml must pass', 'stp_by_status': dict(sorted(stp.items())),
                           'stp_entries': len(reg), 'snca_reports': len(snca)},
            'compatibility': 'The Companion elaborates the Core and never modifies it (Core Part 10.5.1); where they differ, the Core holds.',
            'checksums': 'SHA256SUMS'}


def dump(m): return json.dumps(m, indent=1, ensure_ascii=False) + '\n'


def selftest():
    t = '## CA-90: A Core law (20 November 2026; PENDING ESC)\nCore L-1 changed.\n## CA-03: x\nCompanion only.\n## notes\n'
    a = amendments(t)
    ok = [a[0]['status'] == 'PENDING ESC', a[0]['level'] == 'C', a[0]['date'] == '2026-11-20', a[1]['status'] == 'RATIFIED', a[1]['level'] == 'B', len(a) == 2]
    print('RELEASE MANIFEST SELFTEST:', 'PASS' if all(ok) else 'FAIL %s' % ok); return all(ok)


if __name__ == '__main__':
    a = sys.argv[1:]
    if a == ['--build']:
        os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, 'w', encoding='utf8').write(dump(build())); print('manifest written')
    elif a == ['--check']:
        same = os.path.exists(OUT) and open(OUT, encoding='utf8').read() == dump(build())
        print('RELEASE MANIFEST:', 'PASS' if same else 'FAIL (run --build)'); sys.exit(0 if same else 1)
    elif a == ['--selftest']:
        sys.exit(0 if selftest() else 1)
    else:
        print(__doc__)
