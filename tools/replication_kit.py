#!/usr/bin/env python3
"""replication_kit.py -- the kit for an independent implementation of the mathematical register (Companion Part 220.12; stage 5 of maturity).

A Navigator of any model family, or a mathematician, receives this kit and nothing else: the definitions, and for every result its statement,
domain and derivation, without the code of the tools. They implement each check in their own way and return, for each result, REPRODUCED,
NOT REPRODUCED or NOT ATTEMPTED with their output. A reproduced result gains 'independent implementation' in its proof completeness.

    python3 tools/replication_kit.py            the kit, in Markdown
    python3 tools/replication_kit.py --check    every result of the register is in the kit
Standard library only.
"""
import json, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = os.environ.get('OMEGA42_REG', os.path.join(REPO, 'records', 'math', 'results.json'))
HEAD = """# Omega42 replication kit

Implement each result below independently, in any language, from these definitions alone, and report for each one:
REPRODUCED, NOT REPRODUCED or NOT ATTEMPTED, with your computed values.

## Definitions

- The states are the pairs (a, b) of integers modulo 9; there are 81.
- The law is A(a, b) = (b, a + b), the matrix A = [[0, 1], [1, 1]]; it is multiplication by phi = (1 + sqrt5)/2 in Z[phi], with (a, b) = a + b phi.
- The form is Q(a, b) = b^2 - ab - a^2; Q(As) = -Q(s).
- The shear is B = [[1, 0], [3, 1]].
- The law check of a message of marks d_1, ..., d_n is the state reached from (0, 0) by s -> (b, a + b + d) for each mark.
- Status: EXACT results are computed or proved; CONDITIONAL results hold under the named premise.

## Results
"""
def kit(results):
    out = [HEAD]
    for r in results:
        out.append('### %s [%s]\n\n%s.\n\n- Domain: %s.\n- Derivation: %s.\n- Depends on: %s.\n- Report: REPRODUCED / NOT REPRODUCED / NOT ATTEMPTED, with your values.\n'
                   % (r['id'], r['status'], r['statement'].rstrip('.'), r['domain'].rstrip('.'), r['derivation'].rstrip('.'), r.get('depends') or 'none'))
    return '\n'.join(out)
if __name__ == '__main__':
    R = json.load(open(REG, encoding='utf-8'))['results']
    a = sys.argv[1:]
    if a == ['--check']:
        k = kit(R); miss = [r['id'] for r in R if ('### %s [' % r['id']) not in k]
        print('REPLICATION KIT: %d results | %s' % (len(R), 'PASS' if not miss else 'FAIL: ' + ', '.join(miss))); sys.exit(1 if miss else 0)
    if not a: print(kit(R)); sys.exit(0)
    print(__doc__); sys.exit(2)
