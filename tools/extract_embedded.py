#!/usr/bin/env python3
"""extract_embedded.py -- the self-contained release (Core L-493, Appendix R).

The Core Specification and the Companion Document are the whole release: every tool a Navigator runs, every record
computation, every register and every project policy is embedded in them as a block

    # ===== PATH BEGIN =====
    ...the file, line by line...
    # ===== PATH END =====

(the END line reads "# ===== PATH END ===== (no final newline)" when the file does not end with a newline), so that
the file written out is byte-identical to the repository's.
Every file of the repository is embedded except the six that cannot be: the two documents themselves, the two
lists of their hashes, and the sealed keys of the two open blind tests (OUTSIDE below; Core Appendix R.4).
This script lists the blocks, writes them out as files (so that a Navigator holding only the two documents has the
working tree), and verifies that the documents and a repository hold identical copies and that nothing required is
missing. A Navigator without this script copies the lines between a block's two markers into PATH by hand.

Usage:
    python3 tools/extract_embedded.py --list CORE.docx COMPANION.docx
    python3 tools/extract_embedded.py --extract OUTDIR CORE.docx COMPANION.docx
    python3 tools/extract_embedded.py --verify REPO CORE.docx COMPANION.docx
Standard library only.
"""
import html, os, re, sys, zipfile

BEGIN = re.compile(r'^# ===== (\S+) BEGIN =====$')
LEGACY = {'m193_m225.py': 'scripts/m193_m225.py', 'canonical_reference_av.py': 'scripts/canonical_reference_av.py',
          'omega42_ledger.py': 'scripts/omega42_ledger.py', 'stopword_harness.py': 'scripts/stopword_harness.py',
          'crc60_and_m267.py': 'scripts/crc60_and_m267.py', 'ground_challenge.py': 'scripts/ground_challenge.py'}
# what the release must carry (L-493): every file of the repository. The only files outside the two documents are those
# that cannot be inside them (Core Appendix R.4): the two documents themselves, the two lists of their hashes (a document
# cannot carry its own hash), the sealed keys of the open blind tests, held outside so that the tests stay blind, and the
# AI reading editions, which are renderings of the documents (tools/ai_edition.py).
OUTSIDE = {'docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx': 'the Core Specification itself',
           'docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx': 'the Companion Document itself',
           'SHA256SUMS': 'the hash of every file, the two documents included',
           'records/release_documents_SHA256.txt': 'the hash of the two documents',
           'records/blind_test_02/key.txt': 'the sealed key of blind test 02, lost (records/blind_test_02/KEY_LOST.txt); its hash is embedded (records/blind_test_02/SEALED_SHA256.txt)',
           'records/m267_pilot_01/key.txt': 'the sealed key of the M267 pilot, lost (records/m267_pilot_01/KEY_LOST.txt); its hash is embedded (records/m267_pilot_01/SEALED_SHA256.txt)',
           'ai/Omega42_Core_V335_Rev450.md': 'the Core rendered for AI readers by tools/ai_edition.py; a document cannot contain its own rendering',
           'ai/Omega42_Companion_V335_Rev450.md': 'the Companion rendered for AI readers by tools/ai_edition.py',
           'ai/Omega42_Navigator_Pack.md': 'the Navigator Pack rendered from the Core by tools/ai_edition.py',
           'ai/manifest.json': 'the section manifest of the AI reading editions, rendered by tools/ai_edition.py',
           'ai/Omega42_Existential_Framework.md': 'the Existential Framework rendered from Companion Part 145 by tools/ai_edition.py',
           'llms.txt': 'the index of the AI reading editions, rendered by tools/ai_edition.py'}
EXEMPT = {'tools/__init__.py'}


def paragraphs(path):
    x = zipfile.ZipFile(path).read('word/document.xml').decode('utf-8')
    for p in re.findall(r'<w:p[ >].*?</w:p>', x, re.S):
        lines, cur = [], ''
        for m in re.finditer(r'<w:t(?: [^>]*)?>(.*?)</w:t>|<w:br/>', p, re.S):
            if m.group(0) == '<w:br/>': lines.append(cur); cur = ''
            else: cur += html.unescape(m.group(1))
        lines.append(cur)
        yield lines


def blocks(paths):
    out = {}
    for path in paths:
        for lines in paragraphs(path):
            if not lines: continue
            first = lines[0]
            m = BEGIN.match(first) or (re.match(r'^# ===== (\S+) BEGIN =====', first) if first.startswith('# =====') else None)
            if m:
                name = m.group(1); end = '# ===== %s END =====' % name
                if name in LEGACY:          # legacy blocks of the frozen scripts: the markers are lines of the file itself
                    out[LEGACY.get(name, 'scripts/' + name)] = '\n'.join(lines).rstrip('\n') + '\n'
                    continue
                body = lines[1:]
                if body and body[-1] == end + ' (no final newline)':     # the file ends without a newline
                    out[name] = '\n'.join(body[:-1]); continue
                if body and body[-1] == end:
                    out[name] = '\n'.join(body[:-1]) + '\n'; continue
                out[name] = '\n'.join(body).rstrip('\n') + '\n'
            elif first.startswith('#!/usr/bin/env python3') and 'canonical_reference.py' in ''.join(lines[:3]):
                out['scripts/canonical_reference.py'] = '\n'.join(lines).rstrip('\n') + '\n'
    return out


def required(repo):
    """Every file of the repository but the .git directory, caches and the files OUTSIDE."""
    req = []
    for d, dirs, fs in os.walk(repo):
        dirs[:] = [x for x in dirs if x not in ('.git', '__pycache__')]
        for f in fs:
            r = os.path.relpath(os.path.join(d, f), repo)
            if r not in OUTSIDE and r not in EXEMPT and not r.endswith('.pyc'): req.append(r)
    return sorted(req)


def verify(repo, paths):
    B = blocks(paths); P = []
    for r in required(repo):
        if r not in B: P.append('not embedded: ' + r)
    for name, text in B.items():
        f = os.path.join(repo, name)
        if not os.path.exists(f): P.append('embedded but not in the repository: ' + name); continue
        disk = open(f, encoding='utf-8', newline='').read()
        exact = name not in LEGACY.values() and name != 'scripts/canonical_reference.py'
        if (disk != text) if exact else (disk.rstrip('\n') + '\n' != text): P.append('embedded copy differs: ' + name)
    for o in OUTSIDE:
        if o in B: P.append('embedded but required to stay outside: ' + o)
    print('SELF-CONTAINMENT (L-493): %d blocks embedded | %d files required (every file of the repository) | %d outside, each because it cannot be inside | problems %d' % (len(B), len(required(repo)), len(OUTSIDE), len(P)))
    for p in P: print('  ' + p)
    print('RESULT: %s' % ('PASS' if not P else 'FAIL'))
    return not P


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == '--list':
        for k, v in sorted(blocks(a[1:]).items()): print('%7d  %s' % (len(v), k))
    elif a[0] == '--extract':
        out = a[1]
        for k, v in blocks(a[2:]).items():
            p = os.path.join(out, k); os.makedirs(os.path.dirname(p) or '.', exist_ok=True)
            open(p, 'w', encoding='utf-8', newline='').write(v)
        print('extracted %d files into %s' % (len(blocks(a[2:])), out))
    elif a[0] == '--verify':
        sys.exit(0 if verify(a[1], a[2:]) else 1)
    else:
        print(__doc__); sys.exit(2)
