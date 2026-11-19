#!/usr/bin/env python3
"""STP tests H-001..H-004: polarity structure of the Construct's 26 seeds, read from the original workbook.

Usage: python3 -I tools/test_seed_pairs.py <path-to-PRIMORDIAL-FRACTURE.xlsx>

Each domain sheet takes its seed row (J6:O6) from the MP sheet, where seed = Y + offset.
The test extracts the 26 offset vectors and checks the registered hypotheses.
Pass/fail criteria were fixed before running (docs/SPECULATION_REGISTER.md).
"""
import sys
import openpyxl
from openpyxl.utils import column_index_from_string as ci

ANTIPODE = {k: (9 - k) if k != 9 else 9 for k in range(1, 10)}


def offsets(path):
    wf = openpyxl.load_workbook(path, data_only=False)
    wv = openpyxl.load_workbook(path, data_only=True)
    mp = wv["MP"]
    Y = [mp.cell(6, ci("J") + i).value for i in range(6)]
    out = {}
    for s in wf.sheetnames:
        if s in ("MP", "REV", "PRED"):
            continue
        refs = [wf[s].cell(6, c).value.split("!")[1] for c in range(10, 16)]
        out[s] = tuple(mp[r].value - y for r, y in zip(refs, Y))
    return out


def main(path):
    off = offsets(path)
    neg = lambda o: tuple(-x for x in o)
    m9 = lambda o: tuple(x % 9 for x in o)
    pairs = sorted(tuple(sorted((a, b))) for a in off for b in off if a < b and off[b] == neg(off[a]))
    partner = {a: b for a, b in pairs} | {b: a for a, b in pairs}
    res = {}
    # H-001: the 26 seeds split into exactly 13 exact negation pairs
    res["H-001"] = len(off) == 26 and len(pairs) == 13 and len(partner) == 26
    # H-002: proposed labelling, partner of P_k is N_k for every k = 1..9
    res["H-002"] = all(partner.get(f"P{k}") == f"N{k}" for k in range(1, 10))
    # H-003: the 26 seeds are pairwise distinct mod 9 (needed for a literal F27 Singer cycle)
    res["H-003"] = len({m9(o) for o in off.values()}) == 26
    # H-004: anchor join, sheet N_{antipode-label} is the polarity partner of P_k, for all anchors k
    #        (antipode arm value 9 - k carried by the sheet whose label value -j = 9 - k, i.e. j = k)
    res["H-004"] = all(partner.get(f"P{k}") == f"N{k}" for k in range(1, 10))
    # H-005 (found during the test): mod 9, N_k equals P_(9-k) for the six Lower World anchors
    res["H-005"] = all(m9(off[f"N{k}"]) == m9(off[f"P{ANTIPODE[k]}"]) for k in (1, 2, 4, 5, 7, 8))
    print("pairs:", pairs)
    print("distinct mod 9:", len({m9(o) for o in off.values()}))
    for k, v in res.items():
        print(f"{k}: {'PASS' if v else 'FAIL'}")
    return res


if __name__ == "__main__":
    main(sys.argv[1])
