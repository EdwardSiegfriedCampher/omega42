#!/usr/bin/env python3
"""Independent second implementation of the Classic seed-row tests (Omega42 I-001).

Shares no code with construct_x.py or stp.py and uses a different read path:
  * opens the .xlsx as a zip archive and parses the sheet XML with the standard library (no openpyxl);
  * takes each seed sheet's own cached values in J6:O6 (the row the sheet imports from MP),
    and Reference Vector Y from MP!J6:O6 cached values; it never evaluates a formula.
The main implementation (stp.py) evaluates the MP formulas instead, so agreement between the two
cross-checks the formulas, the cached values and the test logic at once.

Usage: python3 -I tools/independent_check.py WORKBOOK.xlsx   -> JSON on stdout (numbers and labels only)
Antipode (Core definition): anchor k -> 9 - k, shown 9 when the residue is 0.
"""
import json, re, sys, zipfile
import xml.etree.ElementTree as ET

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def sheet_paths(z):
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    target = {r.get("Id"): r.get("Target") for r in rels.iter(REL + "Relationship")}
    out = {}
    for s in wb.find("m:sheets", NS):
        t = target[s.get("{%s}id" % NS["r"])].lstrip("/")
        out[s.get("name")] = t if t.startswith("xl/") else "xl/" + t
    return out


def row_values(z, path, row, cols="JKLMNO"):
    want = {f"{c}{row}" for c in cols}
    got = {}
    for _, el in ET.iterparse(z.open(path)):
        if el.tag == "{%s}c" % NS["m"] and el.get("r") in want:
            v = el.find("m:v", NS)
            got[el.get("r")] = float(v.text) if v is not None else None
        if el.tag == "{%s}row" % NS["m"]:
            if int(el.get("r")) > row:
                break
            el.clear()
    return [got.get(f"{c}{row}") for c in cols]


def main(path):
    z = zipfile.ZipFile(path)
    sp = sheet_paths(z)
    Y = row_values(z, sp["MP"], 6)
    seeds = [s for s in sp if re.fullmatch(r"[PN][1-9]|T[1-4]|[NP][UD]", s)]
    off = {}
    for s in seeds:
        r = row_values(z, sp[s], 6)
        off[s] = tuple(int(round(a - b)) for a, b in zip(r, Y))
    # exact integer negation pairs
    pairs = sorted(sorted([a, b]) for a in off for b in off if a < b and all(x == -y for x, y in zip(off[a], off[b])))
    partner = {}
    for a, b in pairs:
        partner[a], partner[b] = b, a
    disp = lambda r: 9 if r % 9 == 0 else r % 9
    R1, R2 = [], []
    for k in range(1, 10):
        a = disp(9 - k)                                   # Antipode value
        j = next(j for j in range(1, 10) if (-j - a) % 9 == 0)   # N-sheet carrying value a
        if partner.get(f"P{k}") == f"N{j}":
            R1.append(k)
        if [x % 9 for x in off[f"P{a}"]] == [x % 9 for x in off[partner[f"P{k}"]]]:
            R2.append(k)
    units = [1, 2, 4, 5, 7, 8]
    inv = {u: [v for v in units if u * v % 9 == 1][0] for u in units}
    circuit = [1, 2, 4, 8, 7, 5]
    h005 = all([x % 9 for x in off[f"N{k}"]] == [x % 9 for x in off[f"P{9 - k}"]] for k in units)
    h011 = all([x % 9 for x in off[f"P{k}"]] == [2 * inv[k] * c % 9 for c in circuit] for k in units)
    h014 = all(off[f"P{k}"] == (k,) * 6 and off[f"N{k}"] == (-k,) * 6 for k in range(1, 10))
    print(json.dumps({"method": "raw XML, cached J6:O6 of each seed sheet minus cached MP!J6:O6; no formula evaluation",
                      "seed_sheets": len(off), "pairs": pairs, "partner_of_P": {k: partner[f"P{k}"] for k in range(1, 10)},
                      "R1_holds_for": R1, "R2_holds_for": R2, "R2_fails_for": [k for k in range(1, 10) if k not in R2],
                      "H005": h005, "H011": h011, "H014": h014}))


if __name__ == "__main__":
    main(sys.argv[1])
