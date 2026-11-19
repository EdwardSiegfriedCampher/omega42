#!/usr/bin/env python3
"""Omega42 Speculation Test Protocol (CA-08): persistent register, pre-registration and test runner.

  python3 tools/stp.py register              # write pre-registered entries (criterion fixed, NOT RUN)
  python3 tools/stp.py run [ID ...]          # execute registered tests; results appended, never overwritten
  python3 tools/stp.py report                # regenerate docs/SPECULATION_REGISTER.md from the register

Register: records/stp/registry.json. Every entry keeps: id, date, origin, hypothesis, scope, falsification,
test, data, criterion, blinding, status_on_pass, status_on_fail, consequence, supersedes, and a list of runs
(each with time, code sha256, data sha256, run_state, outcome, result). Entries are never deleted.
Run states: NOT RUN, RAN, NOT RUNNABLE (data or definition missing). Outcomes: PASS, FAIL.
Workbook path: env OMEGA42_WORKBOOK (original PRIMORDIAL FRACTURE .xlsx, read-only).
"""
import datetime, hashlib, itertools, json, math, os, random, statistics as st, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "records" / "stp" / "registry.json"
DATA = ROOT / "records" / "data"
sys.path.insert(0, str(ROOT / "tools"))
import construct_x as cx  # noqa: E402
U = cx.U

STATUSES = ("PROPOSED", "INTERPRETIVE", "UNPROVEN", "TESTABLE", "VERIFIED COMPUTATION", "PROVED", "REJECTED", "REVISED")  # Omega42-T01


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16] if path and Path(path).exists() else None


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def load():
    return json.loads(REG.read_text()) if REG.exists() else {"entries": {}}


def save(reg):
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(reg, indent=1, ensure_ascii=False))

# ------------------------------------------------------------------ workbook extraction (formula-level)
def workbook_offsets(path):
    """Seed offsets recomputed from formulas (not cached values), plus cached-value agreement."""
    import openpyxl
    from openpyxl.utils import column_index_from_string as ci
    wf = openpyxl.load_workbook(path, data_only=False)
    wv = openpyxl.load_workbook(path, data_only=True)
    mpf, mpv = wf["MP"], wv["MP"]

    def ev(ref, depth=0):
        v = mpf[ref.replace("$", "")].value
        if isinstance(v, (int, float)):
            return v
        if not (isinstance(v, str) and v.startswith("=")) or depth > 20:
            raise ValueError(f"unsupported cell {ref}: {v!r}")
        terms = [t for t in v[1:].replace("+", " ").split() if t]
        return sum(ev(t, depth + 1) for t in terms)
    Y = [ev(mpf.cell(6, ci("J") + i).coordinate) for i in range(6)]
    off, agree, missing = {}, True, 0
    for s in wf.sheetnames:
        if s in ("MP", "REV", "PRED"):
            continue
        refs = [wf[s].cell(6, c).value.split("!")[1] for c in range(10, 16)]
        vals = [ev(r) for r in refs]
        cached = [mpv[r.replace("$", "")].value for r in refs]
        missing += sum(c is None for c in cached)
        agree &= all(c is None or c == v for c, v in zip(cached, vals))
        off[s] = tuple(v - y for v, y in zip(vals, Y))
    return off, {"cached_agree": agree, "cached_missing": missing}


def _pairs(off):
    neg = lambda o: tuple(-x for x in o)
    pairs = sorted(tuple(sorted((a, b))) for a in off for b in off if a < b and off[b] == neg(off[a]))
    return pairs, {a: b for a, b in pairs} | {b: a for a, b in pairs}


def m9(o): return tuple(x % 9 for x in o)
def antipode(k): return 9 if k == 9 else 9 - k

# ------------------------------------------------------------------ test functions: return (passed, result)
def wb():
    p = os.environ.get("OMEGA42_WORKBOOK")
    if not p or not Path(p).exists():
        raise FileNotFoundError("set OMEGA42_WORKBOOK to the original workbook")
    return p


def t_H001():
    off, integ = workbook_offsets(wb()); pairs, partner = _pairs(off)
    return len(off) == 26 and len(pairs) == 13 and len(partner) == 26, {"pairs": pairs, **integ}


def t_H002():
    off, _ = workbook_offsets(wb()); _, partner = _pairs(off)
    per = {k: partner[f"P{k}"] for k in range(1, 10)}
    return all(per[k] == f"N{k}" for k in per), {"partner_of_P": per}


def t_H003():
    off, _ = workbook_offsets(wb())
    n = len({m9(o) for o in off.values()})
    return n == 26, {"distinct_mod_9": n, "zero_mod_9": [s for s, o in off.items() if m9(o) == (0,) * 6]}


def t_H004R1():
    off, _ = workbook_offsets(wb()); _, partner = _pairs(off)
    # label level: antipode value a = 9-k is carried by the N-sheet whose label value -j = a (mod 9), i.e. j = k
    per = {k: partner[f"P{k}"] == f"N{(-antipode(k)) % 9 or 9}" for k in range(1, 10)}
    return all(per.values()), {"holds_for": [k for k, v in per.items() if v],
                               "fails_for": [k for k, v in per.items() if not v]}


def t_H004R2():
    off, _ = workbook_offsets(wb()); _, partner = _pairs(off)
    # value level: offset of the antipode's P-sheet equals the polarity partner's offset mod 9
    per = {k: m9(off[f"P{antipode(k)}"]) == m9(off[partner[f"P{k}"]]) for k in range(1, 10)}
    return all(per.values()), {"holds_for": [k for k, v in per.items() if v],
                               "fails_for": [k for k, v in per.items() if not v]}


def t_H005():
    off, _ = workbook_offsets(wb())
    per = {k: m9(off[f"N{k}"]) == m9(off[f"P{antipode(k)}"]) for k in (1, 2, 4, 5, 7, 8)}
    return all(per.values()), per


def t_H007a():
    ok, res = t_H004R2()
    return sorted(res["fails_for"]) == [3, 6], {"property_absent_for": res["fails_for"]}


def t_H007b():
    ok, res = t_H004R2()
    return sorted(res["fails_for"]) == [3, 6, 9], {"property_absent_for": res["fails_for"],
                                                     "crown_digit_class": [3, 6, 9]}


def t_H008():
    off, integ = workbook_offsets(wb())
    return integ["cached_agree"] and integ["cached_missing"] == 0, integ


def t_CX001():
    t = cx.selftest()
    keys = [k for k in t if k.startswith(("F9", "F27", "g^(n+13)", "seed labels"))]
    return all(t[k] for k in keys), {k: t[k] for k in keys}


def t_CX002():
    out, r = {}, random.Random(5)
    for g in (cx.Z12, cx.UNITS9, cx.S3):
        ax = g.axioms()
        # sequence generated by a fixed left transformation every d steps: x_{t+d} = rho * x_t
        d, rho = 4, r.choice(g.elements)
        seq = [r.choice(g.elements) for _ in range(d)]
        while len(seq) < 40:
            seq.append(g.op(rho, seq[-d]))
        exact = cx.template_accuracy(g, seq, d) == 1.0
        # composition: the lag-2d rule equals the lag-d rule applied twice
        comp = cx.check_relation(lambda z: z, lambda z: g.op(rho, z),
                                 lambda a, b: g.op(rho, a) == g.op(g.op(rho, rho), b), g.elements)[0]
        out[g.name] = {**ax, "template_exact": exact, "composition": comp}
    passed = all(v["closure"] and v["identity"] and v["inverse"] and v["associativity"] and v["template_exact"]
                 and v["composition"] == cx.NO_COUNTEREXAMPLE for v in out.values())
    return passed, out


def t_CX004():
    F = cx.FIELD
    ok1 = all(cx.seed_between(q, p) == cx.partner_label(cx.seed_between(p, q))
              for p in F for q in F if p != q)
    t = cx.selftest()
    ok2 = t["702 directed pairs <-> 702 affine maps (bijection)"] and t["every directed pair has exactly one seed"]
    return ok1 and ok2, {"reverse_edge_is_partner_seed": ok1, "bijections": ok2}


def t_CX005():
    t = cx.selftest()
    return t["13 rounds x 9 triples; 351 pairs exactly once"], {"rounds": 13, "pairs_once": 351}


def t_CX006():
    r, bad = random.Random(9), 0
    for _ in range(5000):
        X = [r.randint(1, 49) for _ in range(6)]; Y = [r.randint(1, 49) for _ in range(6)]
        mode = r.choice(["units", "symmetric", "modular"])
        a = cx.compare(X, Y, "positional", mode, tau=5)["score"]
        b = cx.compare(X, Y, "matching", mode, tau=5)["score"]
        c = cx.compare(X, Y, "pooled", mode, tau=5)["score"]
        bad += not (a <= b <= c)
    return bad == 0, {"trials": 5000, "violations_of_positional<=matching<=pooled": bad}


def t_CX007():
    hits = 0
    for s in range(40):
        r = random.Random(1000 + s)
        hits += cx.temporal_scan([r.gauss(100, 10) for _ in range(182)], surrogates=39, seed=s)["p"] <= 0.05
    lin = cx.temporal_scan([3 * t + 10 for t in range(182)], surrogates=39)["p"]
    return hits <= 5 and lin == 1.0, {"noise_series": 40, "false_positives_p<=0.05": hits, "linear_trend_p": lin}


def sunspots():
    return [float(x) for x in (DATA / "sunspots_yearly_silso_v2.csv").read_text().split(",")]


def t_H006b():
    x = sunspots()
    a = cx.temporal_scan(x, null="iid"); b = cx.temporal_scan(x, null="block")
    ok = all(v["p"] <= 0.05 and v["fundamental_heuristic"] in (10, 11, 12) for v in (a, b))
    return ok, {"iid": a, "block": b}


def pi_digits(n):
    q, r, t, k, m, x, out = 1, 0, 1, 1, 3, 3, []
    while len(out) < n:
        if 4 * q + r - t < m * t:
            out.append(m); q, r, m = 10 * q, 10 * (r - m * t), (10 * (3 * q + r)) // t - 10 * m
        else:
            q, r, t, k, m, x = q * k, (2 * q + r) * x, t * x, k + 1, (q * (7 * k + 2) + r * x) // (t * x), x + 2
    return out


def t_H006c():
    x = pi_digits(400)
    a = cx.temporal_scan(x, null="iid"); b = cx.temporal_scan(x, null="block")
    return a["p"] > 0.05 and b["p"] > 0.05, {"first_digits": x[:10], "iid": a, "block": b}


def t_H010():
    # among moduli with period 24 and the mirror at 12 (proved: m in {6, 9, 18}), which carry the Construct's
    # two-world split, i.e. the non-units of Z/m form an additive ideal (Z/m is a local ring)?
    from math import gcd
    out = {}
    for m in range(3, 2001):
        A12 = None
        a, b, c, d = 1, 0, 0, 1                      # A^k as [[a, b], [c, d]], A = [[0, 1], [1, 1]]
        for _ in range(12):
            a, b, c, d = b, (a + b) % m, d, (c + d) % m
        if (a, b, c, d) != (m - 1, 0, 0, m - 1):
            continue
        x, y, k = 0, 1, 0
        while True:
            x, y = y, (x + y) % m; k += 1
            if (x, y) == (0, 1): break
        if k != 24:
            continue
        nonunits = [r for r in range(m) if gcd(r, m) != 1]
        ideal = all((u + v) % m in nonunits for u in nonunits for v in nonunits)
        out[m] = ideal
    return [m for m, v in out.items() if v] == [9], {"moduli_with_period_24_and_mirror": list(out), "two_world_split_holds_for": [m for m, v in out.items() if v]}


def t_H011():
    off, _ = workbook_offsets(wb())
    circuit = (1, 2, 4, 8, 7, 5)
    inv = {u: next(v for v in (1, 2, 4, 5, 7, 8) if u * v % 9 == 1) for u in (1, 2, 4, 5, 7, 8)}
    per = {k: m9(off[f"P{k}"]) == tuple(2 * inv[k] * c % 9 for c in circuit) for k in (1, 2, 4, 5, 7, 8)}
    return all(per.values()), {"P_k_offset_equals_(2/k)*doubling_circuit": per}



# ------------------------------------------------------------------ v2.1: representation, classification, correspondence
def t_OP01a():
    disp_ok = all(cx.residue(cx.display(r)) == r for r in range(9)) and sorted(cx.display(r) for r in range(9)) == list(range(1, 10))
    dr_ok = all(cx.digital_root(n) == cx.display(n % 9) for n in range(1, 100001))
    return disp_ok and dr_ok, {"display_bijection": disp_ok, "digital_root_equals_display_of_residue_n<=100000": dr_ok}


def t_OP01b():
    import re, openpyxl
    from openpyxl.utils import range_boundaries, get_column_letter
    wf = openpyxl.load_workbook(wb(), data_only=False)
    DISP = re.compile(r"^=IF\(MOD\((.+?),\s*9\)\s*=\s*0,\s*9,\s*MOD\(\1,\s*9\)\)$")
    REF = re.compile(r"(?:'?([A-Za-z0-9 ]+)'?!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")
    formulas, disp = {}, set()
    for ws in wf.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    formulas[(ws.title, c.coordinate)] = c.value
                    if DISP.match(c.value.replace(" ", "")) or DISP.match(c.value):
                        disp.add((ws.title, c.coordinate))
    def refs(sheet, f):
        out = []
        for sh, c1, r1, c2, r2 in REF.findall(f.split("(", 1)[-1] if False else f[1:]):
            sh = sh or sheet
            if c2:
                mnc, mnr, mxc, mxr = range_boundaries(f"{c1}{r1}:{c2}{r2}")
                out += [(sh, f"{get_column_letter(cc)}{rr}") for cc in range(mnc, mxc + 1) for rr in range(mnr, mxr + 1)]
            else:
                out.append((sh, f"{c1}{r1}"))
        return out
    deps = {}
    for k, f in formulas.items():
        for r in refs(k[0], f):
            deps.setdefault(r, []).append(k)
    classes = {"display_or_mod": 0, "plain_copy": 0, "no_arithmetic": 0, "arithmetic_reduced_downstream": 0, "arithmetic_unreduced": 0}
    examples = []
    for d in disp:
        for k in deps.get(d, []):
            f = formulas[k]
            if "MOD(" in f.upper():
                classes["display_or_mod"] += 1
            elif re.fullmatch(r"=\+?'?[A-Za-z0-9 ]*'?!?\$?[A-Z]{1,3}\$?\d+", f.replace(" ", "")):
                classes["plain_copy"] += 1
            elif not re.search(r"[+\-*/]|SUM\(|AVERAGE\(|PRODUCT\(", f.upper()[1:]):
                classes["no_arithmetic"] += 1
            elif deps.get(k) and all("MOD(" in formulas[j].upper() for j in deps[k]):
                classes["arithmetic_reduced_downstream"] += 1
            else:
                classes["arithmetic_unreduced"] += 1
                if len(examples) < 8:
                    examples.append(f"{k[0]}!{k[1]}")
    return classes["arithmetic_unreduced"] == 0, {"display_cells": len(disp), "formulas": len(formulas), **classes, "examples": examples}


def _period_sig(m):
    per = {}
    for o in cx.orbits(m):
        for s in o:
            per[s] = len(o)
    return lambda s, mm: ((2 * cx.norm(s, mm)) ** 2 % mm, per[s])


def t_UP01():
    ok, res = cx.is_complete_classifier(9, _period_sig(9))
    return ok, res


def t_UP01b():
    ok, res = cx.is_complete_classifier(27, _period_sig(27))
    return ok, res


def t_UP01c():
    out = {m: cx.is_complete_classifier(m, cx.lam)[0] for m in (3, 9, 27, 81, 243, 729)}
    return all(out.values()), {"Lambda_complete_for_m": out}


def t_UP02():
    orb = next(o for o in cx.orbits(9) if (2, 5) in o)
    cls = [s for s in [(a, b) for a in range(9) for b in range(9)] if cx.lam(s, 9) == cx.lam((2, 5), 9)]
    return sorted(orb) == sorted(cls), {"signature_of_(2,5)": cx.lam((2, 5), 9), "states_with_it": len(cls), "orbit_size": len(orb)}


def t_UP03a():
    inv, anti = cx.quadratic_forms_up_to_sign(9)
    Nmult = {((k) % 9, (k) % 9, (-k) % 9) for k in range(9)}
    return set(anti) == Nmult and inv == [(0, 0, 0)], {"invariant_forms": inv, "anti_invariant_forms": sorted(anti)}


def t_UP04a():
    import itertools
    # additive homomorphisms (Z/9)^2 -> F3^3 are fixed by the images of e1, e2, each of order dividing 3 in F3^3: any v works
    F3 = list(itertools.product(range(3), repeat=3))
    max_rank = 0
    for v1 in F3:
        for v2 in F3:
            img = {tuple((a * x + b * y) % 3 for x, y in zip(v1, v2)) for a in range(3) for b in range(3)}
            max_rank = max(max_rank, len(img))
    # subfields of F27 have order 3^d with d | 3, so 9 elements is impossible
    subfield_sizes = [3 ** d for d in (1, 3)]
    no_surjection = max_rank < 27
    return no_surjection and 9 not in subfield_sizes, {"largest_additive_image": max_rank, "F27_subfield_sizes": subfield_sizes}


def t_H014():
    off, _ = workbook_offsets(wb())
    per = {k: off[f"P{k}"] == (k,) * 6 and off[f"N{k}"] == (-k,) * 6 for k in range(1, 10)}
    return all(per.values()), {"P_k = Y + k and N_k = Y - k entrywise holds for": [k for k, v in per.items() if v]}


def t_H013():
    import re, openpyxl
    wf = openpyxl.load_workbook(wb()); wv = openpyxl.load_workbook(wb(), data_only=True)
    pat = re.compile(r"^=\+?\$?([A-Z]+)(\d+)\+\$?([A-Z]+)(\d+)$")
    vals = []
    for ws in wf.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = c.value
                if isinstance(v, str):
                    m = pat.match(v.replace(" ", ""))
                    if m and int(m.group(4)) - int(m.group(2)) == 12:
                        a, b = ws[m.group(1) + m.group(2)].value, ws[m.group(3) + m.group(4)].value
                        if all(isinstance(x, str) and "MOD(" in x for x in (a, b)):
                            vals.append(wv[ws.title][c.coordinate].value)
    red = [v % 9 for v in vals if isinstance(v, (int, float))]
    from collections import Counter
    return len(red) > 0 and all(r == 0 for r in red), {"twelve_apart_sums": len(vals), "residues_mod_9": dict(sorted(Counter(red).items()))}


# ------------------------------------------------------------------ close-out tests (CA-14), registered 18 Nov 2026
def _rot(o): return {tuple(o[i:] + o[:i]) for i in range(len(o))}


def t_H016():
    off, _ = workbook_offsets(wb())
    per = {k: tuple(-v for v in off[f"N{k}"]) in _rot(list(off[f"P{k}"])) for k in range(1, 10)}
    return all(per.values()), {"holds_for": [k for k, v in per.items() if v], "fails_for": [k for k, v in per.items() if not v]}


def t_H016b():
    off, _ = workbook_offsets(wb())
    hw = [3, 6, 9]
    m = {f"P{a}~N{b}": tuple(-v for v in off[f"N{b}"]) in _rot(list(off[f"P{a}"])) for a in hw for b in hw}
    lw = {f"P{a}~N{b}": tuple(-v for v in off[f"N{b}"]) in _rot(list(off[f"P{a}"])) for a in U for b in U if a != b}
    return all(m.values()) and not any(lw.values()), {"higher_world_all_9_related": all(m.values()),
                                                      "lower_world_cross_relations": [k for k, v in lw.items() if v]}


def t_W001():
    import openpyxl, re
    from openpyxl.utils import column_index_from_string as ci
    p = wb(); wf = openpyxl.load_workbook(p, data_only=False); wv = openpyxl.load_workbook(p, data_only=True)
    nform = nocache = 0; errs = {}
    for ws in wf.worksheets:
        vs = wv[ws.title]
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    nform += 1; v = vs[c.coordinate].value
                    if v is None: nocache += 1
                    elif isinstance(v, str) and v.startswith("#"): errs.setdefault(v, []).append(f"{ws.title}!{c.coordinate}")
    pat = re.compile(r"(?:'?([A-Za-z0-9 ]+)'?!)?\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?")
    err_cells = {(e.split("!")[0], e.split("!")[1]) for v in errs.values() for e in v}
    def hit(sheet, m, t):
        s = m[0] or sheet; c2 = m[3] or m[1]; r2 = m[4] or m[2]
        col = ci(re.match(r"[A-Z]+", t[1]).group()); row = int(re.search(r"\d+", t[1]).group())
        return s == t[0] and ci(m[1]) <= col <= ci(c2) and int(m[2]) <= row <= int(r2)
    deps = set()
    for ws in wf.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("=") and (ws.title, c.coordinate) not in err_cells:
                    for m in pat.findall(c.value):
                        if any(hit(ws.title, m, t) for t in err_cells): deps.add(f"{ws.title}!{c.coordinate}")
    res = {"sheets": len(wf.sheetnames), "formula_cells_openpyxl": nform, "no_cached_value": nocache,
           "errors": {k: len(v) for k, v in errs.items()}, "error_cells": errs, "dependents_outside_error_blocks": sorted(deps)}
    ok = (len(wf.sheetnames) == 29 and nocache == 167 and res["errors"] == {"#DIV/0!": 7, "#REF!": 16}
          and all(e.startswith("MP!") and e[3] in "RSTUVWX" and e.endswith("74") for e in errs["#DIV/0!"])
          and all(e.startswith("P9!") and e[-2:] in ("90", "91") for e in errs["#REF!"]) and not deps)
    return ok, res


def _f729():
    # F729 = F3[x]/(p6), p6 irreducible of degree 6, elements as 6-tuples (low degree first)
    import itertools as it
    def mul(a, b, p):
        r = [0] * 11
        for i, x in enumerate(a):
            for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % 3
        for k in range(10, 5, -1):
            c = r[k]
            if c:
                for i in range(6): r[k - 6 + i] = (r[k - 6 + i] - c * p[i]) % 3
                r[k] = 0
        return tuple(r[:6])
    def pw(a, e, p):
        out, b = (1, 0, 0, 0, 0, 0), a
        while e:
            if e & 1: out = mul(out, b, p)
            b = mul(b, b, p); e >>= 1
        return out
    elems = list(it.product(range(3), repeat=6))
    for p in it.product(range(3), repeat=6):        # monic x^6 + p5 x^5 + ... + p0
        if p[0] == 0: continue
        x = (0, 1, 0, 0, 0, 0)
        # irreducible iff x^(3^6) = x and gcd conditions: x^(3^2) != x and x^(3^3) != x and x^(3^1) != x suffices for degree 6
        if pw(x, 729, p) == x and pw(x, 9, p) != x and pw(x, 27, p) != x and pw(x, 3, p) != x:
            # also need no factor of degree 1,2,3 dividing: for degree 6 the check x^(3^6)=x with x^(3^2), x^(3^3) != x is
            # necessary; verify irreducibility by element count of the subfield test below
            return elems, (lambda a, b, p=p: mul(a, b, p)), (lambda a, e, p=p: pw(a, e, p)), p
    raise RuntimeError("no irreducible sextic found")


def t_UP04b():
    elems, mul, pw, p = _f729()
    one = (1, 0, 0, 0, 0, 0); zero = (0,) * 6
    add = lambda a, b: tuple((x + y) % 3 for x, y in zip(a, b))
    nonzero = [e for e in elems if e != zero]
    field = all(any(mul(a, b) == one for b in nonzero) for a in nonzero[:60])  # spot inverse check
    is_field = sum(1 for a in nonzero if pw(a, 728) == one) == 728                # every nonzero a has a^728 = 1
    sub9 = [a for a in elems if pw(a, 9) == a]; sub27 = [a for a in elems if pw(a, 27) == a]
    inter = [a for a in sub9 if a in sub27]
    # explicit embeddings of Construct X's F9 (phi^2 = phi + 1) and F27 (g^3 = g - 1, POLY) into F729
    sq = lambda a: mul(a, a)
    phis = [a for a in elems if sq(a) == add(a, one)]
    neg = lambda a: tuple((-x) % 3 for x in a)
    gs = [a for a in elems if mul(sq(a), a) == add(a, neg(one))]
    def hom_ok(root, deg, rel):
        # map c0 + c1 r (+ c2 r^2) and check multiplicativity on all pairs via construct_x arithmetic
        powers = [one, root, sq(root)][:deg]
        emb = lambda c: tuple(sum(ci * pk[j] for ci, pk in zip(c, powers)) % 3 for j in range(6))
        import itertools as it
        E = list(it.product(range(3), repeat=deg))
        return all(emb(rel(a, b)) == mul(emb(a), emb(b)) for a in E for b in E)
    f9_ok = bool(phis) and hom_ok(phis[0], 2, lambda a, b: cx.f9_mul(a, b))
    f27_ok = bool(gs) and hom_ok(gs[0], 3, lambda a, b: cx.f_mul(a, b))
    res = {"sextic": p, "is_field": is_field, "subfield_9": len(sub9), "subfield_27": len(sub27), "intersection": len(inter),
           "phi_roots": len(phis), "g_roots": len(gs), "F9_embeds": f9_ok, "F27_embeds": f27_ok}
    return is_field and len(sub9) == 9 and len(sub27) == 27 and len(inter) == 3 and f9_ok and f27_ok, res


def _pmod(a, b):
    a = a[:]
    while len(a) >= len(b) and any(a):
        if a[-1] == 0: a.pop(); continue
        c = a[-1] * pow(b[-1], -1, 3) % 3; sh = len(a) - len(b)
        for i, y in enumerate(b): a[sh + i] = (a[sh + i] - c * y) % 3
        a.pop()
    while a and a[-1] == 0: a.pop()
    return a


def _pgcd(a, b):
    while b and any(b): a, b = b, _pmod(a, b)
    return a


def _xpow_minus_x(e, p):
    """(x^(3^e) - x) mod p as a coefficient list, low degree first; p monic of degree 6."""
    mul = lambda a, b: _pmod([sum(a[i] * b[k - i] for i in range(len(a)) if 0 <= k - i < len(b)) % 3 for k in range(len(a) + len(b) - 1)], p)
    r = [0, 1]
    for _ in range(e):
        r2 = [1]; base = r
        for _ in range(3): r2 = mul(r2, base)
        r = r2
    r = r + [0] * (2 - len(r)) if len(r) < 2 else r[:]
    r[1] = (r[1] - 1) % 3
    while r and r[-1] == 0: r.pop()
    return r


def _f729_rabin():
    import itertools as it
    for c in it.product(range(3), repeat=6):
        if c[0] == 0: continue
        p = list(c) + [1]
        if _xpow_minus_x(6, p) == [] and len(_pgcd(p, _xpow_minus_x(2, p))) == 1 and len(_pgcd(p, _xpow_minus_x(3, p))) == 1:
            return tuple(c)
    raise RuntimeError


def t_UP04bR1():
    """Corrected UP-04b: sextic chosen by Rabin's irreducibility test (gcd conditions), then the field is verified."""
    global _f729
    sextic = _f729_rabin()
    old = _f729
    import itertools as it
    def mul(a, b, p=sextic):
        r = [0] * 11
        for i, x in enumerate(a):
            for j, y in enumerate(b): r[i + j] = (r[i + j] + x * y) % 3
        for k in range(10, 5, -1):
            cc = r[k]
            if cc:
                for i in range(6): r[k - 6 + i] = (r[k - 6 + i] - cc * p[i]) % 3
                r[k] = 0
        return tuple(r[:6])
    def pw(a, e):
        out, b = (1, 0, 0, 0, 0, 0), a
        while e:
            if e & 1: out = mul(out, b)
            b = mul(b, b); e >>= 1
        return out
    elems = list(it.product(range(3), repeat=6))
    _f729 = lambda: (elems, mul, pw, sextic)
    try:
        return t_UP04b()
    finally:
        _f729 = old


def t_QA01():
    outs = [cx.question_address(p, k) for p in range(24) for k in range(1, 10)]
    again = [cx.question_address(p, k) for p in range(24) for k in range(1, 10)]
    valid = all(o["seed"] in cx.SEED_LABELS and o["destination"] != o["domain"] for o in outs)
    return len(outs) == 216 and outs == again and valid, {"inputs": len(outs), "deterministic": outs == again, "valid_nodes": valid,
            "distinct_nodes": len({(o["domain"], o["seed"]) for o in outs})}


def t_QA02():
    doms = {cx.question_address(p, k)["domain"] for p in range(24) for k in range(1, 10)}
    missing = sorted(set(itertools.product(range(3), repeat=3)) - doms)
    return missing == [(0, 0, 0), (0, 0, 1), (0, 0, 2)], {"domains_reached": len(doms), "unreached": missing}


def t_W002():
    import openpyxl
    rp = os.environ.get("OMEGA42_RECALC")
    if not rp or not Path(rp).exists():
        raise FileNotFoundError("set OMEGA42_RECALC to the LibreOffice-recalculated copy")
    f = openpyxl.load_workbook(wb(), data_only=False); v = openpyxl.load_workbook(wb(), data_only=True)
    r = openpyxl.load_workbook(rp, data_only=True)
    n = 0; diff = []
    for ws in f.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    a, b = v[ws.title][c.coordinate].value, r[ws.title][c.coordinate].value
                    if a is None: continue
                    n += 1
                    if not (a == b or (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-9)):
                        diff.append(f"{ws.title}!{c.coordinate}")
    want = ["MP!F10", "MP!G10"] + [f"REV!{c}51" for c in ("AI", "AJ", "AK", "AL", "AN", "AO")]
    return sorted(diff) == sorted(want), {"compared": n, "differences": sorted(diff),
            "explanation": "REV!AJ51:AO51 (5 cells) use #REF! as a COUNTIF criterion: Excel stores 0, LibreOffice reports #REF!; AI51 sums them. MP!F10 = MODE of 27 values with a three-way tie (218, 219, 220 seven times each): Excel returns the first in argument order (219), LibreOffice the smallest (218); G10 is its residue. No formula depends on F10 or G10."}


def t_H017():
    out = {}
    for slope in (0.0, 0.5):
        r = random.Random(7); prof = [0, 6, 4, 5, 9, 14, 12]
        x = [50 + slope * t + 3 * prof[t % 7] + r.gauss(0, 3) for t in range(182)]
        out[slope] = cx.baselines(x, 7, int(182 * 0.6))
    win = lambda b: b["lis"] < b["seasonal_naive"]
    return (not win(out[0.0])) and win(out[0.5]), {"no_trend": {k: out[0.0][k] for k in ("lis", "seasonal_naive")},
                                                    "trend_0.5_per_day": {k: out[0.5][k] for k in ("lis", "seasonal_naive")}}


def t_H017b():
    out = {}
    for slope in (0.0, 0.5, 1.0, 2.0):
        r = random.Random(7); prof = [0, 6, 4, 5, 9, 14, 12]
        x = [50 + slope * t + 3 * prof[t % 7] + r.gauss(0, 3) for t in range(182)]
        b = cx.baselines(x, 7, int(182 * 0.6)); out[slope] = {"lis": b["lis"], "seasonal_naive": b["seasonal_naive"]}
    inv = len({v["lis"] for v in out.values()}) == 1
    return inv and out[1.0]["lis"] < out[1.0]["seasonal_naive"] and out[2.0]["lis"] < out[2.0]["seasonal_naive"], {"by_slope": out, "lis_error_trend_invariant": inv}


def t_H018():
    """Speculation: within each CX-010 family, the Classic polarity pairs never split (both g^n and g^(n+13) in one family)."""
    _, res = t_CX010()
    fams = [set(f) for f in res["families_as_seed_exponents"]]
    split = [n for n in range(26) if not any(n in f and (n + 13) % 26 in f for f in fams)]
    return not split, {"pairs_split": split}


def t_H019():
    _, res = t_CX010()
    zero = (0, 0, 0)
    fam_of = {}
    pts = list(itertools.product(range(3), repeat=3))
    # rebuild families as point sets (CX-010 reports seed exponents; recompute points directly)
    frob = lambda a: cx.f_mul(cx.f_mul(a, a), a)
    seen = set()
    for q0 in pts:
        if q0 in seen: continue
        fam, st_ = set(), [q0]
        while st_:
            q = st_.pop()
            if q in fam: continue
            fam.add(q); st_ += [cx.f_neg(q), frob(q)]
        for q in fam: fam_of[q] = len(seen)
        seen |= fam
    always = [k for k in range(1, 10) if all(fam_of[cx.question_address(p, k)["domain"]] == fam_of[cx.question_address(p + 12, k)["domain"]] for p in range(12))]
    return always == [3, 6, 9], {"anchors_where_every_antipodal_pair_shares_a_family": always}


def _seasonal(seed, n=600, period=7, slope=0.0, amp=4.0, sd=3.0):
    r = random.Random(seed)
    prof = [amp * math.sin(2 * math.pi * i / period) + (i % 3) for i in range(period)]
    return [50 + slope * t + prof[t % period] + r.gauss(0, sd) for t in range(n)]


def t_H021():
    """Noise gains: seasonal-naive (1 - B^d) 2, Lagged-Increment (1 - B)(1 - B^d) 4, Construct Engine scalar (1 - B^d)^2 6.
    On stationary seasonal series the held-out MAE ratios should approach sqrt(2) and sqrt(3)."""
    d, ratios_lis, ratios_ce = 7, [], []
    for i in range(200):
        x = _seasonal(5000 + i); cut = int(len(x) * 0.6); ts = range(max(cut, 2 * d + 1), len(x) - 1)
        sn = st.mean(abs(x[t + 1] - x[t + 1 - d]) for t in ts)
        li = st.mean(abs(x[t + 1] - (x[t] + x[t + 1 - d] - x[t - d])) for t in ts)
        ce = st.mean(abs(x[t + 1] - (2 * x[t + 1 - d] - x[t + 1 - 2 * d])) for t in ts)
        ratios_lis.append(li / sn); ratios_ce.append(ce / sn)
    rl, rc = st.mean(ratios_lis), st.mean(ratios_ce)
    ok = abs(rl / math.sqrt(2) - 1) <= 0.10 and abs(rc / math.sqrt(3) - 1) <= 0.10
    return ok, {"lis_over_seasonal_naive": round(rl, 4), "predicted": round(math.sqrt(2), 4),
                "construct_engine_over_seasonal_naive": round(rc, 4), "predicted_ce": round(math.sqrt(3), 4)}


def t_CX013():
    """Power of the block null by block length on a period-12 seasonal series (n = 240, sd 3)."""
    out = {}
    for B in (6, 12, 24, 48):
        k = 0
        for i in range(20):
            x = _seasonal(7000 + i, n=240, period=12, slope=0.02, amp=2.0, sd=3.0)
            k += cx.temporal_scan(x, null="block", surrogates=99, seed=i, block_len=B)["p"] <= 0.05
        out[B] = k
    vals = [out[b] for b in (6, 12, 24, 48)]
    return vals[0] > vals[-1] and all(a >= b for a, b in zip(vals, vals[1:])), {"detections_of_20_by_block_length": out}


def t_CX003():
    """The Lab's Polarity and Seed Navigator shows, for each of the 26 seeds, the same exact-negative partner
    as the workbook (H-001), and the offset rows it displays are exact negatives."""
    import subprocess
    js = ROOT / "tools" / "lab_selftest.js"
    out = json.loads(subprocess.run(["node", str(js), str(ROOT / "site" / "construct_x_lab.html")], capture_output=True,
                                    text=True, check=True).stdout)
    _, h1 = t_H001()
    wb_partner = {}
    for a, b in h1["pairs"]:
        wb_partner[a], wb_partner[b] = b, a
    lab = out["partners"]; offs = out["offsets"]
    mism = [s for s in wb_partner if lab.get(s) != wb_partner[s]]
    neg = [s for s in lab if any(x != -y for x, y in zip(offs[s], offs[lab[s]]))]
    return len(lab) == 26 and not mism and not neg, {"seeds": len(lab), "partner_mismatches": mism, "non_negative_offsets": neg,
                                                    "page_errors": out["errors"]}


def t_CX008():
    """Transformation Laboratory (Python engine): exact on a rule-generated melody; after a rule change the
    template fails on the changed part, so the composition-consistency check reports the change."""
    motif = [0, 4, 7, 4, 2, 5, 9, 5]
    seq = [(m + 5 * (t // 8)) % 12 for t, m in enumerate(motif * 6)]
    exact = cx.template_accuracy(cx.Z12, seq, 8)
    changed = seq[:24] + [(m + 2 * (t // 8)) % 12 for t, m in enumerate(motif * 3, start=24)]
    ts = range(32, len(changed) - 1)
    after = sum(cx.template_forecast(cx.Z12, changed, t, 8) == changed[t + 1] for t in ts) / len(ts)
    near = [t for t in range(8, len(changed) - 1) if cx.template_forecast(cx.Z12, changed, t, 8) != changed[t + 1]]
    return exact == 1.0 and after == 1.0 and near and min(near) >= 23 and max(near) <= 31, {
        "melody_accuracy_lag8": exact, "accuracy_after_new_rule_settles": after, "failures_at": near}


def t_CX009():
    """The permanent register: every entry carries the CA-08 fields, every run carries code fingerprints and a time,
    no registered entry has disappeared, and each superseded entry is REVISED."""
    reg = load(); E = reg["entries"]
    need = ("id", "origin", "hypothesis", "scope", "falsification", "test", "data", "criterion", "blinding",
            "on_pass", "on_fail", "consequence", "status", "runs")
    missing = {k: [f for f in need if f not in e] for k, e in E.items() if any(f not in e for f in need)}
    bad_runs = [k for k, e in E.items() for r in e["runs"] if r["run_state"] == "RAN" and (not r.get("code_sha") or not r.get("time"))]
    ids_in_code = {d["id"] for d in PRE}
    gone = sorted(ids_in_code - set(E))
    sup = {e.get("supersedes") for e in E.values() if e.get("supersedes")}
    not_revised = sorted(s for s in sup if s in E and E[s]["status"] != "REVISED")
    return not missing and not bad_runs and not gone and not not_revised, {"entries": len(E), "missing_fields": missing,
            "runs_without_fingerprint": bad_runs[:10], "deleted_entries": gone, "superseded_not_revised": not_revised}


def t_CX015():
    k = sum(cx.temporal_scan(_ar1(3000 + i, phi=0.9), null="block", surrogates=99, seed=i)["p"] <= 0.05 for i in range(40))
    return k <= 5, {"false_positives_of_40": k, "phi": 0.9, "block_len": 24}


def t_CX016():
    W = cx.williams_schedule(6)
    rows = all(sorted(r) == list(range(1, 7)) for r in W)
    cols = all(sorted(W[i][j] for i in range(6)) == list(range(1, 7)) for j in range(6))
    tr = [(r[j], r[j + 1]) for r in W for j in range(5)]
    guide = [[1, 2, 6, 3, 5, 4], [2, 3, 1, 4, 6, 5], [3, 4, 2, 5, 1, 6], [4, 5, 3, 6, 2, 1], [5, 6, 4, 1, 3, 2], [6, 1, 5, 2, 4, 3]]
    gen = all(len(set((r[j], r[j + 1]) for r in cx.williams_schedule(n) for j in range(n - 1))) == n * (n - 1) for n in (2, 4, 8, 10, 12))
    return rows and cols and len(set(tr)) == 30 and W == guide and gen, {"latin": rows and cols, "ordered_transitions": len(set(tr)),
                                                                        "matches_guide_table": W == guide, "even_n_2_to_12": gen}


def t_CX017():
    out = {}
    for name, x in (("co2", co2()), ("sunspots", sunspots()), ("pi", pi_digits(400) if "pi_digits" in globals() else None)):
        if x is None: continue
        r = cx.temporal_scan(x, null="iid")
        out[name] = {"p": r["p"], "base": r["candidate_base_lag"], "base_status": r["base_lag_status"], "interp": r["periodicity_interpretation"]}
    ok = out["co2"]["interp"] == "supported" and out["sunspots"]["interp"] == "unsupported" and out.get("pi", {}).get("interp", "unsupported") == "unsupported"
    return ok, out


def t_CX009R1():
    reg = load(); E = reg["entries"]
    need = ("id", "origin", "hypothesis", "scope", "falsification", "test", "data", "criterion", "blinding",
            "on_pass", "on_fail", "consequence", "status", "runs", "status_history")
    missing = {k: [f for f in need if f not in e] for k, e in E.items() if any(f not in e for f in need)}
    legacy = {"H-001", "H-002", "H-003", "H-004", "H-005", "UP-01d"}
    bad = sorted({k for k, e in E.items() for r in e["runs"] if r["run_state"] == "RAN" and not r.get("code_sha")} - legacy)
    gone = sorted({d["id"] for d in PRE} - set(E))
    revised_ok = all(E[k]["status"] == "REVISED" for k in ("H-004", "UP-04b", "CX-010"))
    return not missing and not bad and not gone and revised_ok, {"entries": len(E), "missing_fields": missing,
            "unfingerprinted_runs_outside_legacy": bad, "legacy_unfingerprinted": sorted(legacy), "deleted_entries": gone,
            "revised_entries_kept": revised_ok}


def t_H023():
    """White residuals around a trend: the skill of the best lag over the drift baseline is built in by the noise gains."""
    sk = []
    for i in range(100):
        r = random.Random(9000 + i); x = [0.3 * t + r.gauss(0, 1) for t in range(326)]
        cut = int(326 * 0.6); lags = range(2, 25)
        best = min(lags, key=lambda d: cx._mae(x, d, 0, cut))
        sk.append(1 - cx._mae(x, best, cut, 326) / cx._mae(x, 1, cut, 326))
    m = st.mean(sk); pred = 1 - math.sqrt(4 / 6)
    return abs(m - pred) <= 0.03, {"mean_skill_on_white_noise": round(m, 4), "predicted": round(pred, 4),
                                   "sunspot_observed_skill": 0.115}


# ------------------------------------------------------------------ capability tests (CAP-01 to CAP-05), 19 Nov 2026
def _same_orbit_walk(x, y, m):
    a, b = x
    for _ in range(8 * m):          # the longest orbit at depth m has 8 m / 3 states
        if (a, b) == y: return True
        a, b = b, (a + b) % m
        if (a, b) == x: return False
    return False


def t_CAP01():
    import time
    rng = random.Random(101); m = 3 ** 7
    T = lambda v, n: _walk(v, n, m)
    pairs = []
    for _ in range(2000):
        x = (rng.randrange(m), rng.randrange(m)); y = (rng.randrange(m), rng.randrange(m)); pairs.append((x, y))
    for _ in range(1000):
        r = rng.choice([0, 0, 1, 2, 3]); x = (3 ** r * rng.randrange(m) % m, 3 ** r * rng.randrange(m) % m)
        pairs.append((x, T(x, rng.randrange(1, 6000))))
    for _ in range(1000):     # same valuation, chosen to share N^2 or not
        r = rng.choice([0, 1, 2]); x = (3 ** r * rng.randrange(1, m) % m, 3 ** r * rng.randrange(1, m) % m)
        y = (3 ** r * rng.randrange(1, m) % m, 3 ** r * rng.randrange(1, m) % m); pairs.append((x, y))
    wrong = sum((cx.lam(x, m) == cx.lam(y, m)) != _same_orbit_walk(x, y, m) for x, y in pairs if x != (0, 0) and y != (0, 0))
    same = sum(_same_orbit_walk(x, y, m) for x, y in pairs)
    big = 3 ** 100; t0 = time.time()
    deep = [(3 ** r * rng.randrange(big) % big, 3 ** r * rng.randrange(big) % big) for r in (0, 5, 40, 77, 99) for _ in range(2000)]
    labels = [cx.lam(v, big) for v in deep]
    dt = time.time() - t0
    walked = [cx.lam(_walk(v, 10 ** 6 + 7, big), big) == l for v, l in zip(deep[:200], labels[:200])]
    rs = sorted({l[0] for l in labels})
    return wrong == 0 and dt < 5 and all(walked) and rs == [0, 5, 40, 77, 99], {
        "pairs_checked_at_3^7": len(pairs), "same_orbit_pairs": same, "disagreements": wrong,
        "states_classified_at_3^100": len(deep), "seconds": round(dt, 3), "valuations_seen": rs,
        "invariant_after_10^6_steps": all(walked)}


def _walk(v, n, m):
    """T^n by the closed form T^n = F(n-1) I + F(n) A on (Z/m)^2, using fast Fibonacci mod m."""
    def fib(k):
        def f(k):
            if k == 0: return (0, 1)
            a, b = f(k >> 1); c = a * ((2 * b - a) % m) % m; d = (a * a + b * b) % m
            return (d, (c + d) % m) if k & 1 else (c, d)
        return f(k)
    Fn, Fn1 = fib(n); Fm1 = (Fn1 - Fn) % m
    a, b = v
    return ((Fm1 * a + Fn * b) % m, (Fn * a + Fn1 * b) % m)


def t_CAP02():
    R = cx.steiner_rounds(); pts = cx.FIELD; idx = {p: i for i, p in enumerate(pts)}
    sched = [[(idx[a], idx[b]) for line in rnd for a, b in itertools.combinations(line, 2)] for rnd in R]
    cover = {tuple(sorted(p)) for rnd in sched for p in rnd}
    rng = random.Random(202)
    def random_sched():
        out = []
        for _ in range(13):
            perm = list(range(27)); rng.shuffle(perm)
            out.append([tuple(sorted(pr)) for k in range(9) for pr in itertools.combinations(perm[3 * k:3 * k + 3], 2)])
        return out
    def recover(sc, trials):
        hits = 0
        for _ in range(trials):
            bias = set(rng.sample(range(27), 3)); truth = [rng.gauss(0, 1) for _ in range(40)]
            reads = [[t + rng.gauss(0, 1) + (1.2 if i in bias else 0) for t in truth] for i in range(27)]
            dis = [[] for _ in range(27)]
            for rnd in sc:
                for a, b in rnd:
                    d = st.mean(abs(u - v) for u, v in zip(reads[a], reads[b])); dis[a].append(d); dis[b].append(d)
            score = [st.mean(d) if d else 0 for d in dis]
            top = set(sorted(range(27), key=lambda i: -score[i])[:3]); hits += top == bias
        return hits / trials
    rs_cov = [len({p for rnd in random_sched() for p in rnd}) for _ in range(200)]
    st_rate = recover(sched, 300); rnd_rate = st.mean(recover(random_sched(), 1) for _ in range(300))
    return len(cover) == 351 and max(rs_cov) < 351 and st_rate >= 0.9 and st_rate > rnd_rate, {
        "steiner_pairs_covered": len(cover), "random_schedule_pairs_covered_mean": round(st.mean(rs_cov), 1),
        "random_schedule_pairs_covered_max": max(rs_cov), "steiner_recovers_all_3_biased": round(st_rate, 3),
        "random_schedule_recovers_all_3_biased": round(rnd_rate, 3)}


def t_CAP03():
    rng = random.Random(303); n = 100000; pooled = matching = removed = 0
    for _ in range(n):
        Y = rng.sample(range(1, 50), 6); X = rng.sample(range(1, 50), 6)
        p = cx.compare(X, Y, "pooled")["score"]; q = cx.compare(X, Y, "matching")["score"]
        pooled += p >= 4; matching += q >= 4; removed += (p >= 4 and q < 4)
    share = removed / pooled if pooled else 0
    cl = (cx.compare([38, 3, 9, 13, 21, 36], [36, 1, 11, 12, 17, 31], "pooled")["score"],
          cx.compare([38, 3, 9, 13, 21, 36], [36, 1, 11, 12, 17, 31], "matching")["score"])
    return share >= 0.10, {"draws": n, "pooled_flag_rate": round(pooled / n, 4), "matching_flag_rate": round(matching / n, 4),
                           "share_of_pooled_flags_without_independent_support": round(share, 4)}


def t_CAP04():
    rng = random.Random(404); d = 7; right = by_train = 0; N = 300; rows = []
    for i in range(N):
        slope = rng.uniform(0, 1.5); sd = 3.0; prof = [rng.uniform(-6, 6) for _ in range(d)]
        x = [50 + slope * t + prof[t % d] + rng.gauss(0, sd) for t in range(182)]
        cut = int(182 * 0.6)
        D = [x[t] - x[t - d] for t in range(d, cut)]
        predict_lis = st.mean(D) ** 2 > st.pvariance(D)          # (d s)^2 > 2 sigma^2, read off the training part
        ts = range(cut, 181)
        lis = st.mean(abs(x[t + 1] - (x[t] + x[t + 1 - d] - x[t - d])) for t in ts)
        sn = st.mean(abs(x[t + 1] - x[t + 1 - d]) for t in ts)
        tr = range(2 * d, cut - 1)
        lis_tr = st.mean(abs(x[t + 1] - (x[t] + x[t + 1 - d] - x[t - d])) for t in tr)
        sn_tr = st.mean(abs(x[t + 1] - x[t + 1 - d]) for t in tr)
        right += predict_lis == (lis < sn); by_train += (lis_tr < sn_tr) == (lis < sn)
    return right / N >= 0.85, {"series": N, "law_predicts_held_out_winner": round(right / N, 3),
                               "training_error_predicts_held_out_winner": round(by_train / N, 3)}


def t_PHB01():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import physics_bench as pb
    r = pb.run()
    return r["passed"] == 5, {k: v for k, v in r.items()}


def t_H029():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import choice_engine as ce
    c81, n81 = ce.orbit_change_share(81)
    c243, n243 = ce.orbit_change_share(243, 200000, 29)
    s81, s243 = c81 / n81, c243 / n243
    return s81 > 0.95 and s243 > s81, {"mod_81": f"{c81}/{n81} = {s81:.6f}", "mod_243_sampled": f"{c243}/{n243} = {s243:.6f}",
                                       "mod_9": "4768/6480 = 0.735802", "mod_27": "482992/530712 = 0.910083"}


def t_H030():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import choice_engine as ce
    c, n = ce.orbit_change_share(729, 200000, 30)
    keep = 1 - c / n
    return 0.0027 <= keep <= 0.0043, {"mod_729_sampled_unchanged": f"{n - c}/{n} = {keep:.6f}", "predicted": "0.0103 / 3 = 0.0034, band 0.0027 to 0.0043",
                                      "earlier_unchanged": "0.264 (9), 0.090 (27), 0.030 (81), 0.010 (243 sampled)"}


def t_AR01():
    """Arithmetic statements in the archive heads (docs/ARCHIVE_CONCORDANCE.md), each recomputed."""
    import math
    m = 9; T = lambda v: (v[1], (v[0] + v[1]) % m)
    def orbit_len(v):
        s, n = T(v), 1
        while s != v: s, n = T(s), n + 1
        return n
    rem, r = [], 1
    for _ in range(6): r = r * 10 % 7; rem.append(r)
    phi = (1 + 5 ** 0.5) / 2
    checks = {
        "C1 (2, 5) lies on a 24-cycle mod 9 [V336 Companion]": orbit_len((2, 5)) == 24,
        "C2 the digits of 1/7 are the units mod 9 [V336 Companion]": sorted({1, 4, 2, 8, 5, 7}) == [u for u in range(1, 9) if math.gcd(u, 9) == 1],
        "C3 the remainders of 1/7 are the nonzero residues mod 7 [V336 Companion]": sorted(rem) == list(range(1, 7)),
        "C4 168 = 24 x 7 [V336 Companion]": 24 * 7 == 168,
        "C5 chance of an anchor in {3, 6, 9} is 1/3 [V336 Companion I3]": abs(3 / 9 - 1 / 3) < 1e-12,
        "C6 Planck frequency / (27 phi) = 42 Hz [formal discovery document]": abs(5.4e43 / (27 * phi) - 42) / 42 < 0.1,
        "C7 3.23 x 10^9 has digit sum 23 -> 5 [formal discovery document]": 3230000000 % 9 == 5,
        "C8 18 is a Fibonacci number ('324 = 18^2, square of reduced Fibonacci') [formal discovery document]": 18 in (1, 2, 3, 5, 8, 13, 21, 34),
        "C9 324 = 0 mod 27 and mod 9 [formal discovery document]": 324 % 27 == 0 and 324 % 9 == 0,
    }
    failed = [k for k, v in checks.items() if not v]
    return not failed, {"held": sum(checks.values()), "of": len(checks), "failed": failed,
                        "values": {"C6": "%.3e Hz" % (5.4e43 / (27 * phi)), "C7": "3,230,000,000 mod 9 = %d" % (3230000000 % 9)}}


def t_TR01():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import transformability as tr, io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf): good = tr.selftest()
    return good, {"lines": [l.strip() for l in buf.getvalue().splitlines() if l.strip()]}


def t_RC01():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import choice_engine as ce
    noscalar = not any(ce.scalar_consensus_ever(9, k) for k in range(9))
    radius = ce.real_consensus_radius()
    return noscalar and abs(radius - 5 ** 0.5 / 2) < 1e-4, {"scalar_consensus_mod_9": "never, for every k in 0..8 (exhaustive, 72 steps)", "least_real_radius": round(radius, 4),
                                                          "agreement_by_one_added_term": "yes (choice_engine selftest)"}


def t_RC01R1():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import choice_engine as ce
    from fractions import Fraction as Fr
    noscalar = not any(ce.scalar_consensus_ever(9, k) for k in range(9))
    radius = ce.real_consensus_radius()
    rational_singular = [str(x) for x in (Fr(n, d) for d in range(1, 60) for n in range(-180, 181)) if x * x - x - 1 == 0]
    grows = []
    for pull in (Fr(-1), Fr(1, 2), Fr(1), Fr(2)):
        d0 = (Fr(1), Fr(0)); d = d0
        for _ in range(40): d = (d[1] - pull * d[0], d[0] + d[1] - pull * d[1])
        grows.append(abs(d[0]) + abs(d[1]) > 1000)
    phi = (1 + 5 ** 0.5) / 2; sneg = -1 / phi; v = (1.0, -1 / phi)
    vanish = abs(v[1] - sneg * v[0]) < 1e-12 and abs(v[0] + v[1] - sneg * v[1]) < 1e-12
    ok = noscalar and abs(radius - 5 ** 0.5 / 2) < 1e-4 and not rational_singular and all(grows) and vanish
    return ok, {"mod_9_agreement": "never" if noscalar else "found", "least_real_radius": round(radius, 4), "rational_pulls_making_T_minus_s_singular": rational_singular,
                "rational_difference_grows_beyond_1000_in_40_steps_for_pulls_-1_1/2_1_2": grows, "real_eigen_difference_vanishes_at_s=-1/phi": vanish}


def t_RC01R2():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import choice_engine as ce
    from fractions import Fraction as Fr
    noscalar = not any(ce.scalar_consensus_ever(9, k) for k in range(9))
    radius = ce.real_consensus_radius()
    rational_singular = [str(x) for x in (Fr(n, d) for d in range(1, 60) for n in range(-180, 181)) if x * x - x - 1 == 0]
    grows = []
    for pull in (Fr(-1), Fr(1, 2), Fr(1), Fr(2)):
        d = (Fr(1), Fr(0))
        for _ in range(40): d = (d[1] - pull * d[0], d[0] + d[1] - pull * d[1])
        grows.append(abs(d[0]) + abs(d[1]) > 10)
    phi = (1 + 5 ** 0.5) / 2; sneg = -1 / phi; v = (1.0, -1 / phi)
    vanish = abs(v[1] - sneg * v[0]) < 1e-12 and abs(v[0] + v[1] - sneg * v[1]) < 1e-12
    ok = noscalar and abs(radius - 5 ** 0.5 / 2) < 1e-4 and not rational_singular and all(grows) and vanish
    return ok, {"mod_9_agreement": "never" if noscalar else "found", "least_real_radius": round(radius, 4), "rational_pulls_making_T_minus_s_singular": rational_singular,
                "rational_difference_grows_beyond_10x_in_40_steps_for_pulls_-1_1/2_1_2": grows, "real_eigen_difference_vanishes_at_s=-1/phi": vanish}


def t_CAP05():
    import congruence as cg
    reg = cg.load_register()
    items = [(tag, cg.sig(text)) for tag, text in reg] if isinstance(reg, list) else [(k, cg.sig(v)) for k, v in reg.items()]
    S = [s["state"] for _, s in items]; n = len(S)
    lamS = [cx.lam(s, 9) for s in S]
    pairs = list(itertools.combinations(range(n), 2))
    same = [(i, j) for i, j in pairs if S[i] == S[j]]
    mirr = [(i, j) for i, j in pairs if S[i] == cg.neg(S[j]) and S[i] != (0, 0)]
    orb = [(i, j) for i, j in pairs if lamS[i] == lamS[j]]
    orb_only = [p for p in orb if p not in same and p not in mirr]
    # exact chance of the same orbit over the 729 residue triples (the same null as layer 3)
    P = [cx.lam(cg.bl.frequency(a, b)["state"], 9) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
    cnt = Counter(P); p_orb = sum(v * v for v in cnt.values()) / len(P) ** 2
    expected = p_orb * len(pairs); ratio = len(orb) / expected if expected else 0
    meet = same + mirr
    # one-to-one matching of meetings: the largest set of meetings sharing no domain (greedy is exact enough? use brute bipartite-free max matching)
    import networkx as nx
    G = nx.Graph(); G.add_edges_from(meet)
    matched = len(nx.max_weight_matching(G, maxcardinality=True)) if meet else 0
    return ratio <= 1.2 and matched < len(meet), {"domains": n, "pairs": len(pairs), "same_state": len(same), "mirror": len(mirr),
            "same_orbit": len(orb), "same_orbit_beyond_state_and_mirror": len(orb_only), "chance_same_orbit_per_pair": round(p_orb, 4),
            "expected_same_orbit": round(expected, 2), "observed_over_expected": round(ratio, 3),
            "pooled_meetings": len(meet), "one_to_one_meetings": matched}


def t_CAP01R1():
    ok, res = t_CAP01()
    rng = random.Random(101)
    for _ in range(2000): rng.randrange(3 ** 7); rng.randrange(3 ** 7)
    big = 3 ** 100; rr = random.Random(7)
    deep = [(r, (3 ** r * rr.randrange(big) % big, 3 ** r * rr.randrange(big) % big)) for r in (0, 5, 40, 77, 99) for _ in range(2000)]
    at_least = all(cx.lam(v, big)[0] >= r for r, v in deep)
    exact_when_unit = all(cx.lam(v, big)[0] == r for r, v in deep if (v[0] // 3 ** r) % 3 or (v[1] // 3 ** r) % 3)
    good = res["disagreements"] == 0 and res["seconds"] < 5 and res["invariant_after_10^6_steps"] and at_least and exact_when_unit
    return good, {**res, "valuation_at_least_construction_exponent": at_least, "valuation_exact_when_quotient_is_primitive": exact_when_unit}


def t_UP01e():
    rows = {}
    ok = True
    for k in range(1, 7):
        m = 3 ** k; orbs = cx.orbits(m)
        lens = Counter(len(o) for o in orbs)
        want = Counter({1: 1, **{8 * 3 ** (j - 1): 3 ** (j - 1) for j in range(1, k + 1)}})
        rows[k] = {"orbits": len(orbs), "formula": (m + 1) // 2, "lengths_match": lens == want}
        ok &= len(orbs) == (m + 1) // 2 and lens == want
    return ok, rows


def t_CX010():
    zero = (0, 0, 0)
    pts = [p for p in itertools.product(range(3), repeat=3)]
    frob = lambda a: cx.f_mul(cx.f_mul(a, a), a)
    seen, fams = set(), []
    for p in pts:
        if p in seen: continue
        fam, stack = set(), [p]
        while stack:
            q = stack.pop()
            if q in fam: continue
            fam.add(q); stack += [cx.f_neg(q), frob(q)]
        seen |= fam; fams.append(sorted(fam))
    sizes = sorted(len(f) for f in fams)
    # invariant: minimal polynomial over F3 up to x -> -x, via (trace, norm) up to common sign... computed as the
    # set {(Tr a, s2(a), N a)} of the family's elementary symmetric data, which must be constant on a family up to sign
    def sym(a):
        a1, a3, a9 = a, frob(a), frob(frob(a))
        tr = cx.f_add(cx.f_add(a1, a3), a9)
        s2 = cx.f_add(cx.f_add(cx.f_mul(a1, a3), cx.f_mul(a3, a9)), cx.f_mul(a1, a9))
        nm = cx.f_mul(cx.f_mul(a1, a3), a9)
        return tr, s2, nm
    def canon(a):
        t1, t2 = sym(a), sym(cx.f_neg(a))
        return min(t1, t2)
    inv_const = all(len({canon(a) for a in f}) == 1 for f in fams)
    separates = len({canon(f[0]) for f in fams}) == len(fams)
    return sizes == [1, 2, 6, 6, 6, 6] and inv_const and separates, {"family_sizes": sizes, "invariant_constant": inv_const,
                                                                       "invariant_separates": separates,
                                                                       "families_as_seed_exponents": [sorted(cx.SINGER.index(q) for q in f if q != zero) for f in fams]}


def _weekly(seed=5, n=182):
    r = random.Random(seed); prof = [0, 6, 4, 5, 9, 14, 12]
    return [50 + 0.05 * t + 3 * prof[t % 7] + r.gauss(0, 3) for t in range(n)]


def t_CX011():
    x = _weekly(); res = cx.temporal_scan(x, null="block", surrogates=99)
    b = res["baselines"]
    return b["lis_beats_all_baselines"], {"best": res["best"], **b}


def _ar1(seed, n=300, phi=0.5):
    r = random.Random(seed); x = [0.0]
    for _ in range(n - 1): x.append(phi * x[-1] + r.gauss(0, 1))
    return x


def _fp(null, block_len=None):
    return sum(cx.temporal_scan(_ar1(1000 + i), null=null, surrogates=99, seed=i, block_len=block_len)["p"] <= 0.05 for i in range(40))


def t_CX012a():
    k = _fp("block"); return k <= 5, {"false_positives_of_40": k, "block_len": 24}


def t_CX012b():
    k = _fp("iid"); return k <= 5, {"false_positives_of_40": k}


def co2():
    rows = (DATA / "mauna_loa_co2_monthly_nist_1974_1987.csv").read_text().split()[1:]
    return [float(r.split(",")[2]) for r in rows]


def t_H006d():
    x = co2()
    b = cx.temporal_scan(x, null="block"); i = cx.temporal_scan(x, null="iid")
    return b["p"] <= 0.05 and b["candidate_base_lag"] in (11, 12, 13), {"block": b, "iid_transition_report": i}


def t_I001():
    import subprocess
    out = subprocess.run([sys.executable, "-I", str(ROOT / "tools" / "independent_check.py"), wb()],
                         capture_output=True, text=True, check=True).stdout
    ind = json.loads(out)
    _, r1 = t_H004R1(); _, r2 = t_H004R2(); _, p1 = t_H001(); _, h2 = t_H002()
    main = {"pairs": [list(p) for p in p1["pairs"]], "partner_of_P": {str(k): v for k, v in h2["partner_of_P"].items()},
            "R1_holds_for": r1["holds_for"], "R2_holds_for": r2["holds_for"], "H005": t_H005()[0],
            "H011": t_H011()[0], "H014": t_H014()[0], "R2_fails_for": r2["fails_for"]}
    diff = {k: (main[k], ind.get(k)) for k in main if main[k] != ind.get(k)}
    return not diff, {"agree_on": sorted(k for k in main if k not in diff), "differences": diff,
                      "independent_reads": ind.get("method")}

TESTS = {"H-013": t_H013, "H-014": t_H014, "OP-01a": t_OP01a, "OP-01b": t_OP01b, "UP-01": t_UP01, "UP-01b": t_UP01b, "UP-01c": t_UP01c, "UP-02": t_UP02, "UP-03a": t_UP03a, "UP-04a": t_UP04a, "H-010": t_H010, "H-011": t_H011, "H-001": t_H001, "H-002": t_H002, "H-003": t_H003, "H-004-R1": t_H004R1, "H-004-R2": t_H004R2,
         "H-005": t_H005, "H-007a": t_H007a, "H-007b": t_H007b, "H-008": t_H008, "CX-001": t_CX001,
         "CX-002": t_CX002, "CX-004": t_CX004, "CX-005": t_CX005, "CX-006": t_CX006, "CX-007": t_CX007,
         "H-006b": t_H006b, "H-006c": t_H006c, "H-016": t_H016, "H-016b": t_H016b, "W-001": t_W001,
         "UP-04b": t_UP04b, "W-002": t_W002, "H-017": t_H017, "H-017b": t_H017b, "H-018": t_H018, "H-019": t_H019, "H-021": t_H021, "CX-003": t_CX003, "CX-008": t_CX008, "CX-009": t_CX009, "CX-009-R1": t_CX009R1, "CX-015": t_CX015, "CX-016": t_CX016, "CX-017": t_CX017, "H-023": t_H023, "CAP-01": t_CAP01, "CAP-01-R1": t_CAP01R1, "CAP-02": t_CAP02, "CAP-03": t_CAP03, "CAP-04": t_CAP04, "CAP-05": t_CAP05, "PHB-01": t_PHB01, "H-029": t_H029, "H-030": t_H030, "AR-01": t_AR01, "TR-01": t_TR01, "RC-01": t_RC01, "RC-01-R1": t_RC01R1, "RC-01-R2": t_RC01R2, "CX-013": t_CX013, "QA-01": t_QA01, "QA-02": t_QA02, "UP-04b-R1": t_UP04bR1, "UP-01e": t_UP01e, "CX-010-D": t_CX010, "CX-011": t_CX011, "CX-012a": t_CX012a,
         "CX-012b": t_CX012b, "H-006d": t_H006d, "I-001": t_I001}

# ------------------------------------------------------------------ pre-registration
WB = "original workbook (PRIMORDIAL FRACTURE), formulas recomputed from MP; cached values checked"
PRE = [
 dict(id="H-001", origin="CA-08 first run; seed rows read from MP", hypothesis="The 26 seeds split into 13 pairs whose offset vectors are exact integer negatives",
      scope="Construct Classic workbook, MP seed rows", falsification="fewer than 13 exact negation pairs, or a seed left unpaired",
      test="t_H001, formula-level recomputation", data=WB, criterion="13 pairs covering all 26 seeds", blinding="replication of an earlier run",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="pairing becomes CLASSIC-DERIVED polarity", supersedes=None),
 dict(id="H-002", origin="Navigator's proposed labelling", hypothesis="The partner of P_k is N_k for every k = 1..9",
      scope="workbook", falsification="any k whose partner is not N_k", test="t_H002", data=WB, criterion="all 9 hold",
      blinding="replication", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="labelling corrected if rejected", supersedes=None),
 dict(id="H-003", origin="F27 model", hypothesis="The workbook literally implements the F27 Singer cycle (26 seeds distinct mod 9)",
      scope="workbook", falsification="fewer than 26 distinct offsets mod 9", test="t_H003", data=WB, criterion="26 distinct",
      blinding="replication", on_pass="CROSS-VALIDATED", on_fail="REJECTED", consequence="F27 is X-CONSTRUCTED if rejected", supersedes=None),
 dict(id="H-004", origin="anchor-join speculation", hypothesis="The Antipode arm lands on the seed's polarity partner for every anchor",
      scope="workbook", falsification="see H-004-R1/R2", test="original script duplicated the H-002 condition", data=WB,
      criterion="all 9 anchors", blinding="n/a", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="superseded: test implementation incomplete (did not compute the arm); replaced by H-004-R1 and H-004-R2", supersedes=None),
 dict(id="H-004-R1", origin="H-004, corrected per external review", hypothesis="Label level: the Antipode value a = 9-k is carried by sheet N_j with -j = a (mod 9); that sheet is the polarity partner of P_k, for every anchor k",
      scope="workbook labels + offsets", falsification="any anchor where the partner differs", test="t_H004R1 (computes arm value, then sheet, then compares)", data=WB,
      criterion="all 9 anchors; per-anchor list recorded", blinding="NOT BLIND: the Navigator stated 7 of 9 before this implementation",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="defines where label-level navigation and polarity agree", supersedes="H-004"),
 dict(id="H-004-R2", origin="H-004, corrected per external review", hypothesis="Value level: the offset of P_(9-k) equals, mod 9, the offset of the polarity partner of P_k, for every anchor k",
      scope="workbook offsets mod 9", falsification="any anchor where they differ", test="t_H004R2", data=WB,
      criterion="all 9 anchors; per-anchor list recorded", blinding="NOT BLIND for Lower World anchors (implied by H-005); Higher World anchors not previously computed in the register",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="defines where value-level navigation and polarity agree", supersedes="H-004"),
 dict(id="H-005", origin="found during the H-001 run", hypothesis="Mod 9, N_k = P_(9-k) for k in {1,2,4,5,7,8}",
      scope="workbook", falsification="any k failing", test="t_H005", data=WB, criterion="all 6 hold",
      blinding="replication", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="MODULAR_ANTIPODE relation type", supersedes=None),
 dict(id="H-007a", origin="review: structural part of H-007", hypothesis="Anchors 3 and 6, and only they, lack the value-level property of H-004-R2",
      scope="workbook", falsification="the set of anchors lacking the property is not exactly {3, 6}", test="t_H007a", data=WB,
      criterion="failure set == {3, 6}", blinding="NOT BLIND: designer inspected Higher World offsets while writing tests; exploratory",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="if rejected, the 3/6 exception is not specific to 3 and 6", supersedes=None),
 dict(id="H-007b", origin="review: interpretive part of H-007", hypothesis="The anchors lacking the H-004-R2 property are exactly the Crown digit class {3, 6, 9} (Core M244 definition of Crown digits)",
      scope="workbook + Core definition", falsification="failure set differs from {3, 6, 9}", test="t_H007b", data=WB,
      criterion="failure set == {3, 6, 9}", blinding="NOT BLIND (as H-007a); exploratory, criterion from an independent Core definition",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="if passed: the polarity exception coincides with the Crown/Torsion split", supersedes=None),
 dict(id="H-008", origin="review: cached-value risk", hypothesis="Cached workbook values for all 26 seed rows equal formula recomputation, with none missing",
      scope="workbook", falsification="any disagreement or missing value", test="t_H008", data=WB, criterion="agree and 0 missing",
      blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="data integrity record for H-001..H-007", supersedes=None),
 dict(id="CX-001", origin="review 5.1", hypothesis="F9 and F27 are fields as constructed; phi and g are primitive; partners are 13 powers apart; labels biject onto nonzero elements",
      scope="Construct X substrate", falsification="any failed axiom or order", test="t_CX001 (exhaustive)", data="none",
      criterion="all checks pass", blinding="blind", on_pass="PROVED", on_fail="REJECTED", consequence="X substrate certified", supersedes=None),
 dict(id="CX-002", origin="review 5.6", hypothesis="Group-relative templates are exact on rule-generated sequences, and lag-2d equals lag-d applied twice, in Z/12, (Z/9)^x and S3",
      scope="declared groups", falsification="any failed axiom, inexact template or composition counterexample", test="t_CX002", data="generated",
      criterion="all pass in all three groups", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="G engine certified for groups", supersedes=None),
 dict(id="CX-004", origin="review 5.2", hypothesis="702 directed pairs biject with seeds and affine maps; the reverse edge uses the partner seed",
      scope="Construct X address", falsification="any pair without a unique seed or with a non-partner reverse", test="t_CX004 (exhaustive)", data="none",
      criterion="all 702 pass", blinding="blind", on_pass="PROVED", on_fail="REJECTED", consequence="702-node navigator certified", supersedes=None),
 dict(id="CX-005", origin="review 5.3", hypothesis="13 rounds of 9 triples cover all 351 pairs exactly once",
      scope="Construct X schedule", falsification="any pair missing or repeated", test="t_CX005 (exhaustive)", data="none",
      criterion="351 pairs, each once", blinding="blind", on_pass="PROVED", on_fail="REJECTED", consequence="scheduler certified", supersedes=None),
 dict(id="CX-006", origin="review 5.4", hypothesis="For any fields and mode: positional <= matching <= pooled",
      scope="comparison engine", falsification="any violation", test="t_CX006, 5000 random cases", data="generated",
      criterion="0 violations", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="operator ordering for reports", supersedes=None),
 dict(id="CX-007", origin="review 5.5", hypothesis="The corrected temporal engine keeps its false-positive rate near 5% on noise and reports no cycle for a pure trend",
      scope="temporal engine, iid null", falsification="more than 5 of 40 noise series at p <= 0.05, or trend p != 1", test="t_CX007", data="generated",
      criterion="<= 5 of 40 and trend p = 1", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="temporal engine calibrated", supersedes=None),
 dict(id="H-006", origin="CA-08 first run", hypothesis="Weekly-cycle detection works on a real series with an independently known weekly cycle",
      scope="real daily data", falsification="p > 0.05 or fundamental != 7 on held-out data", test="temporal_scan, both nulls", data="NOT AVAILABLE in this session (shell network off; fetch tool returns summaries, not data)",
      criterion="p <= 0.05 under both nulls and fundamental = 7", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="first real-data validation", supersedes=None),
 dict(id="H-006b", origin="review: real-data positive control", hypothesis="On the SILSO yearly sunspot series (1700-2025), whose ~11-year Schwabe cycle is independently established, the engine finds the cycle",
      scope="real annual data", falsification="p > 0.05 under either null, or fundamental not in {10, 11, 12}", test="temporal_scan, iid and block nulls", data="records/data/sunspots_yearly_silso_v2.csv (SILSO V2.0, transcribed via the fetch tool; spot checks: n=326, 1700=8.3, 1957=269.3, 2019=3.6, 2024=154.7)",
      criterion="p <= 0.05 under both nulls and fundamental in {10, 11, 12}", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="first real-data validation of the temporal engine", supersedes=None),
 dict(id="H-006c", origin="review: negative control", hypothesis="On the first 400 decimal digits of pi, where no cycle is expected, the engine reports no structure",
      scope="real (non-simulated) sequence", falsification="p <= 0.05 under either null", test="temporal_scan, iid and block nulls", data="pi digits computed by spigot",
      criterion="p > 0.05 under both nulls", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="engine does not invent cycles in patternless data", supersedes=None),
 dict(id="H-010", origin="uniqueness review: the Construct's two worlds", hypothesis="Among all moduli 3..2000 with period 24 and the mirror A^12 = -I, the Construct's two-world split (non-units form an additive ideal) holds for 9 alone",
      scope="moduli 3..2000 (the proof of Companion 130.2 shows only 6, 9, 18 qualify for every m)", falsification="the split holds for 6 or 18, or fails for 9", test="t_H010 (exhaustive)", data="none",
      criterion="split holds exactly for {9}", blinding="NOT BLIND: equivalent to 'one prime' (Z/m local iff m a prime power), expected by theory",
      on_pass="PROVED", on_fail="REJECTED", consequence="POST-SELECTION STRUCTURAL PROPERTY of the necessity proof (anti-retrofitting rule): an equivalent reading of condition (3), never a new selection criterion", supersedes=None),
 dict(id="H-011", origin="uniqueness review: the Construct's generator", hypothesis="In the workbook, the offset row of P_k is (2/k) times the doubling circuit mod 9, for k in {1,2,4,5,7,8}",
      scope="workbook", falsification="any k failing", test="t_H011", data=WB, criterion="all 6 hold",
      blinding="NOT BLIND: pattern seen while reading offsets", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="POST-SELECTION corroboration of K2: the Construct's own engine is the generator 2", supersedes=None),

 dict(id="OP-01a", origin="review OP-01", hypothesis="Construct X keeps residues 0-8 internally; display (0 shown as 9) is a bijection that round-trips, and the Core's digital root equals display of the residue for every n >= 1",
      scope="Construct X; n up to 100000", falsification="any failed round trip or any n where they differ", test="t_OP01a", data="none",
      criterion="all hold", blinding="blind", on_pass="PROVED", on_fail="REJECTED", consequence="representation separated from arithmetic", supersedes=None),
 dict(id="OP-01b", origin="review OP-01", hypothesis="In the original workbook, every formula that does arithmetic on a displayed value (0 shown as 9) is reduced mod 9 again, directly or by every formula downstream",
      scope="all formulas of the workbook", falsification="any arithmetic use of a displayed value that is never reduced", test="t_OP01b (static formula audit, one level downstream)", data=WB,
      criterion="zero unreduced arithmetic uses", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if rejected, the listed cells need a review: a shown 9 may be counted as nine rather than zero", supersedes=None),
 dict(id="UP-01", origin="review UP-01", hypothesis="On (Z/9)^2 the pair (Q^2, period), Q = 2N, is constant on each orbit and separates all 5 orbits",
      scope="81 states", falsification="an orbit with two signatures or two orbits sharing one", test="t_UP01 (exhaustive)", data="none",
      criterion="complete classifier", blinding="NOT BLIND: reported by the review", on_pass="PROVED", on_fail="REJECTED", consequence="finite orbit classifier mod 9", supersedes=None),
 dict(id="UP-01b", origin="extension of UP-01", hypothesis="(Q^2, period) stays a complete orbit classifier on (Z/27)^2",
      scope="729 states, 14 orbits", falsification="two orbits sharing a signature", test="t_UP01b (exhaustive)", data="none",
      criterion="complete classifier", blinding="NOT BLIND: the Navigator expected failure (the three r = 1 orbits all have N^2 = 0 mod 27)", on_pass="PROVED", on_fail="REJECTED",
      consequence="if rejected, the classifier needs the 3-adic valuation (the Core's Lambda address)", supersedes=None),
 dict(id="UP-01c", origin="Core orbit address Lambda", hypothesis="Lambda(x) = (r, N(u)^2 mod 3^(k-r)), x = 3^r u, is a complete orbit classifier on (Z/3^k)^2 for every k (proof in CA-11); checked for k = 1..6",
      scope="up to 531441 states", falsification="any k where Lambda fails", test="t_UP01c (exhaustive)", data="none",
      criterion="complete for k = 1..6", blinding="NOT BLIND: k <= 5 was run before registration", on_pass="PROVED", on_fail="REJECTED", consequence="classification architecture for the uniqueness proof", supersedes=None),
 dict(id="UP-02", origin="review UP-02", hypothesis="The canonical orbit is exactly the set of states whose Lambda signature equals that of the seed (2, 5)",
      scope="81 states", falsification="the signature class differs from the orbit", test="t_UP02 (exhaustive)", data="none",
      criterion="class == orbit", blinding="blind", on_pass="PROVED", on_fail="REJECTED", consequence="K-uniqueness restated as a classification statement", supersedes=None),
 dict(id="UP-03a", origin="review UP-03 (invariant discovery)", hypothesis="Mod 9, the only quadratic form invariant under T is 0, and the anti-invariant forms are exactly the multiples k*N",
      scope="all 729 forms c1 a^2 + c2 ab + c3 b^2 mod 9", falsification="any other invariant or anti-invariant form", test="t_UP03a (exhaustive)", data="none",
      criterion="invariant = {0}; anti-invariant = {kN}", blinding="blind", on_pass="PROVED", on_fail="REJECTED",
      consequence="N is the unique quadratic witness of the mirror, up to scale", supersedes=None),
 dict(id="UP-04a", origin="review UP-04", hypothesis="No additive surjection (Z/9)^2 -> F3^3 exists, and F9 is not a subfield of F27, so Omega42's 81 states and Construct X's 27 points have no structure-preserving link of these two kinds",
      scope="additive homomorphisms; subfields", falsification="a surjective additive map, or a 9-element subfield of F27", test="t_UP04a (exhaustive + subfield lattice)", data="none",
      criterion="no surjection and no embedding", blinding="blind", on_pass="PROVED", on_fail="REJECTED",
      consequence="the Omega42-Construct X link stays analogical (Singer cycles in dimensions 2 and 3), CDT-B", supersedes=None),
 dict(id="H-014", origin="terminology work: Core 0.9.1 states N_k = Y - k and P_k = Y + k", hypothesis="Entrywise, every P-seed row is Y + (k, k, k, k, k, k) and every N-seed row is Y - (k, ..., k), as Core 0.9.1 reads",
      scope="workbook MP seed rows", falsification="any k where the offset row is not constant k", test="t_H014", data=WB,
      criterion="all 9 k hold", blinding="NOT BLIND: H-011 had already shown the Lower World offsets are (2/k) x doubling circuit", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if rejected, Core 0.9.1 needs a corrected formula for ESC to ratify; the Navigator does not change it", supersedes=None),
 dict(id="H-013", origin="speculation on OP-01b: the twelve-apart sums may be a hand-built check of the antipodal rule",
      hypothesis="Every workbook sum of two displayed roots taken twelve rows apart reduces mod 9 to residue 0 (displayed 9)",
      scope="workbook, all sheets", falsification="any such sum with a nonzero residue mod 9", test="t_H013", data=WB,
      criterion="all residues 0", blinding="blind (the values were not inspected mod 9 before registration)",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="if passed, the sums read as antipodal checks; if rejected, they are not", supersedes=None),
 dict(id="CX-010", origin="review 9", hypothesis="The 27 domains contain families related by shared invariants under polarity, transposition or affine maps",
      scope="Construct X + Classic domain outputs", falsification="no shared invariant beyond those forced by construction", test="to be defined: invariant list, transformations, domain outputs",
      data="not yet defined", criterion="to be fixed before any run", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="structural resonance engine", supersedes=None),

 dict(id="H-016", origin="close-out review: 'direct N/P polarity at anchors 3 and 6'", hypothesis="For every k = 1..9, the negated offset of N_k is a cyclic rotation of the offset of P_k (direct pairing up to rotation)",
      scope="workbook seed offsets", falsification="any k where -N_k is not a rotation of P_k", test="t_H016", data=WB, criterion="all 9 k hold",
      blinding="NOT BLIND: offsets inspected before registration", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="reconciles the review's direct pairing with H-001's exact (crossed) pairing: two different relations", supersedes=None),
 dict(id="H-016b", origin="Navigator speculation on H-016", hypothesis="Rotation-negation does not single out a partner in the Higher World (each of N3, N6, N9 is a rotation-negation of each of P3, P6, P9), while in the Lower World it relates no P_a to N_b with a != b",
      scope="workbook seed offsets", falsification="a Higher World pair that is not related, or any Lower World cross relation", test="t_H016b", data=WB,
      criterion="all 9 Higher World combinations related and 0 Lower World cross relations", blinding="NOT BLIND: offsets inspected before registration",
      on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="if passed: only exact positional negation (H-001) fixes the Higher World partners; the crossed pairing P3-N6, P6-N3 is the workbook's own", supersedes=None),
 dict(id="W-001", origin="close-out review section 3 (workbook errors)", hypothesis="The workbook has 29 sheets, 167 formula cells without cached values, 7 #DIV/0! at MP!R74:X74 and 16 #REF! at P9!T90:AA91, and no formula outside those two blocks depends on them",
      scope="all formulas", falsification="any count differs or any dependent exists", test="t_W001 (static dependency scan)", data=WB,
      criterion="all counts as stated and zero dependents", blinding="replication of the review's counts; the dependency part is new", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed, both error blocks are isolated: they cannot affect any other workbook output", supersedes=None),
 dict(id="UP-04b", origin="close-out review: F9 and F27 in a common overfield", hypothesis="F729 contains exactly one subfield of order 9 and one of order 27, they meet in F3, and Construct X's F9 (phi^2 = phi + 1) and F27 (g^3 = g - 1) both embed as fields",
      scope="F729 built as F3[x]/(sextic)", falsification="wrong subfield sizes or intersection, or a failed embedding", test="t_UP04b (exhaustive)", data="none",
      criterion="9, 27, intersection 3, both embeddings multiplicative on all pairs", blinding="blind (expected by theory)", on_pass="PROVED", on_fail="REJECTED",
      consequence="F9-F27 Singer-Cycle Correspondence gains a common overfield; UP-04a stands (no embedding of one in the other)", supersedes=None),
 dict(id="UP-01e", origin="close-out review: orbit-count law", hypothesis="On (Z/3^k)^2 there are (3^k + 1)/2 orbits of T: one fixed zero state and 3^(j-1) orbits of length 8*3^(j-1) for j = 1..k",
      scope="k = 1..6 exhaustive; proof as corollary of UP-01d", falsification="any k with a different count or length profile", test="t_UP01e", data="none",
      criterion="all k = 1..6 match", blinding="NOT BLIND: k = 2, 3, 5 counts known", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="depth-tower table follows from a formula", supersedes=None),
 dict(id="CX-010-D", origin="review 9; defines CX-010 at close-out", hypothesis="Under the order-6 group generated by polarity (x -> -x) and Frobenius (x -> x^3), the 27 domains fall into 6 families of sizes 1, 2, 6, 6, 6, 6, and the minimal polynomial up to x -> -x is constant on each family and separates them",
      scope="Construct X domains F27", falsification="other family sizes, or an invariant that varies inside a family or repeats across families", test="t_CX010 (exhaustive)", data="none",
      criterion="sizes [1,2,6,6,6,6], invariant constant and separating", blinding="blind (computed after registration; sizes predicted by theory)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="defines the Structural Family Register of the 27 domains (X-CONSTRUCTED)", supersedes="CX-010"),
 dict(id="CX-011", origin="close-out review section 4: compare with ordinary forecasters", hypothesis="On the synthetic weekly demonstration series, the Lagged-Increment Model at the selected lag has lower held-out error than every baseline (seasonal-naive, persistence, drift, training mean, training trend)",
      scope="one synthetic series (seed 5, 182 days)", falsification="any baseline with error <= LIS", test="t_CX011", data="generated",
      criterion="LIS strictly best", blinding="NOT BLIND: the v2.3 self-test printed seasonal-naive 7.7 < LIS 10.5 on a similar series before registration", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if rejected, the Temporal Engine is a stability detector, not a forecaster", supersedes=None),
 dict(id="CX-012a", origin="close-out review: justify the block length", hypothesis="With block length 24, the block null keeps the false-positive rate at or below 5 of 40 on AR(1) noise (phi = 0.5, n = 300) that has no cycle",
      scope="40 generated series, 99 surrogates each", falsification="more than 5 of 40 at p <= 0.05", test="t_CX012a", data="generated",
      criterion="<= 5 of 40", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="block length 24 calibrated for short-memory noise", supersedes=None),
 dict(id="CX-012b", origin="close-out review: iid null under dependence", hypothesis="The iid null keeps the false-positive rate at or below 5 of 40 on the same AR(1) series",
      scope="as CX-012a", falsification="more than 5 of 40", test="t_CX012b", data="generated",
      criterion="<= 5 of 40", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED", consequence="if rejected, the iid null is unsafe under serial dependence and the block null should be primary", supersedes=None),
 dict(id="I-001", origin="close-out review: independent reproduction", hypothesis="An independent implementation (tools/independent_check.py: raw XML, cached values, no shared code) reproduces the pairs, partners, H-004-R1/R2 anchor lists, H-005, H-011 and H-014 of the main implementation",
      scope="workbook seed rows", falsification="any difference", test="t_I001", data=WB,
      criterion="no differences", blinding="same author, different code and read path; not an independent reviewer", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="H-004 results become reproducible by a second implementation", supersedes=None),
 dict(id="UP-04b-R1", origin="UP-04b, corrected: the first run used an incomplete irreducibility test (accepted x^6 + x^5 + 1, a product of factors of degrees 1, 2, 3)", hypothesis="F729 contains exactly one subfield of order 9 and one of order 27, they meet in F3, and Construct X's F9 (phi^2 = phi + 1) and F27 (g^3 = g - 1) both embed as fields",
      scope="F729 = F3[x]/(sextic chosen by Rabin's test)", falsification="as UP-04b", test="t_UP04bR1 (Rabin test, then every nonzero element checked for a^728 = 1)", data="none",
      criterion="as UP-04b: 9, 27, intersection 3, both embeddings multiplicative on all pairs", blinding="NOT BLIND: the defective first run had been seen", on_pass="PROVED", on_fail="REJECTED",
      consequence="as UP-04b", supersedes="UP-04b"),
 dict(id="QA-01", origin="close-out: Question-to-Address Mapping Rule, candidate QAM-1 (CA-14)", hypothesis="QAM-1 is total and deterministic on all 216 Axis readings (24 positions x 9 anchors) and returns a valid Matrix node each time",
      scope="Construct X address engine", falsification="any reading without a node, or two runs that differ", test="t_QA01", data="none",
      criterion="216 valid nodes, identical on rerun", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="QAM-1 becomes IMPLEMENTED; adoption stays with ESC", supersedes=None),
 dict(id="QA-02", origin="Navigator speculation on QAM-1", hypothesis="QAM-1 reaches exactly 24 of the 27 domains; the 3 unreached are the line (0, 0, c), because the canonical orbit mod 3 never passes through (0, 0)",
      scope="216 Axis readings", falsification="any other set of unreached domains", test="t_QA02", data="none",
      criterion="unreached == {(0,0,0), (0,0,1), (0,0,2)}", blinding="blind (predicted from the period-8 Fibonacci cycle mod 3 before any run)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: under QAM-1 the origin line of the Matrix is reserved, never addressed by a question", supersedes=None),
 dict(id="W-002", origin="close-out review: H-008 needed a fresh spreadsheet recalculation", hypothesis="A full LibreOffice recalculation (forced on load; control copy without cached values gives the same result) agrees with the workbook's cached values on every formula cell except MP!F10, MP!G10 and REV!AI51, AJ51, AK51, AL51, AN51, AO51",
      scope="all 104,925 formula cells with cached values", falsification="any other difference, or any of the eight agreeing", test="t_W002 (env OMEGA42_RECALC)", data=WB + "; LibreOffice recalculation of it (not stored: contains the Originator's name)",
      criterion="difference set equals the eight cells", blinding="NOT BLIND: the comparison was run and the eight cells traced before registration; this entry records the finding reproducibly", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="H-008 gains a recalculation check; two Classic fragilities recorded: silent #REF! criteria in REV and an engine-dependent MODE tie in MP!F10", supersedes=None),
 dict(id="H-017", origin="Navigator speculation from H-006d vs CX-011", hypothesis="The Lagged-Increment Model beats seasonal-naive when trend and season combine, and loses to it when there is no trend: on the weekly demonstration profile (seed 7), it loses at slope 0 and wins at slope 0.5 per day",
      scope="two synthetic series, lag 7, held-out 40%", falsification="LIS wins at slope 0 or loses at slope 0.5", test="t_H017", data="generated",
      criterion="loses at slope 0 and wins at slope 0.5", blinding="blind (seed 7 not run before registration)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: the LIS forecast is the seasonal-difference-with-drift forecaster; use it when trend and season coexist, seasonal-naive otherwise", supersedes=None),
 dict(id="H-017b", origin="H-017 rejected at slope 0.5 (LIS 4.42 vs seasonal-naive 4.17); a Gaussian error calculation puts the crossover near slope 0.5", hypothesis="The LIS held-out error does not change with a linear trend, and LIS beats seasonal-naive at slopes 1.0 and 2.0 per day on the same profile and noise",
      scope="as H-017 plus slopes 1.0 and 2.0", falsification="LIS error changes with slope, or seasonal-naive wins at 1.0 or 2.0", test="t_H017b", data="generated",
      criterion="identical LIS error at all slopes and LIS < seasonal-naive at 1.0 and 2.0", blinding="NOT BLIND: noise seed and slopes 0, 0.5 already seen", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: LIS cancels linear trend exactly; choose LIS over seasonal-naive once trend per cycle exceeds roughly the noise level", supersedes="H-017"),
 dict(id="H-018", origin="Navigator speculation, close-out reply", hypothesis="No CX-010 family separates a Classic polarity pair: for every seed g^n, its partner g^(n+13) = -g^n lies in the same family",
      scope="26 seeds, 6 families", falsification="any pair split across two families", test="t_H018", data="none",
      criterion="0 split pairs", blinding="blind (not computed before registration; expected because negation is one of the two generators)", on_pass="PROVED", on_fail="REJECTED",
      consequence="if passed: the domain families are unions of whole polarity pairs, so the Classic Polarity Pairing is a sub-structure of the X families", supersedes=None),
 dict(id="H-019", origin="Navigator speculation, close-out reply", hypothesis="Under QAM-1, the antipodal readings (p, p + 12) land in the same CX-010 family for every p exactly when the anchor k is a Crown digit (3, 6, 9)",
      scope="12 antipodal position pairs x 9 anchors", falsification="the set of anchors with this property differs from {3, 6, 9}", test="t_H019", data="none",
      criterion="anchor set == [3, 6, 9]", blinding="blind (not computed before registration; Frobenius could add anchors)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: under QAM-1 the Crown anchors are the ones whose antipodes stay in one structural family", supersedes=None),
 dict(id="H-021", origin="Companion sweep: Part 108.3 (the Construct Engine loses to the latest row on slow sequences) read beside CX-011", hypothesis="On stationary seasonal series with Gaussian noise, held-out MAE relative to seasonal-naive is sqrt(2) for the Lagged-Increment Model and sqrt(3) for the Construct Engine's scalar rule, the square roots of their noise gains 4/2 and 6/2",
      scope="200 generated series, period 7, n = 600, no trend", falsification="either mean ratio more than 10% from its prediction", test="t_H021", data="generated",
      criterion="both ratios within 10% of sqrt(2) and sqrt(3)", blinding="blind (predicted from the operator coefficients before any run)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: one law (noise gain = sum of squared operator coefficients) explains CX-011, H-017b and Companion 108.3 together", supersedes=None),
 dict(id="CX-013", origin="Companion sweep: Part 108.3 holds that a block shuffle keeping runs of the rule's interval keeps the rule's own evidence", hypothesis="The block null loses power as its block length grows past the cycle: on period-12 seasonal series, detections at p <= 0.05 fall (weakly) from block 6 to 12 to 24 to 48, and strictly from 6 to 48",
      scope="20 generated series per block length (n = 240, period 12, amplitude 2, sd 3, slope 0.02), 99 surrogates", falsification="detections rise with block length at any step, or equal at 6 and 48", test="t_CX013", data="generated",
      criterion="non-increasing in block length and strictly lower at 48 than at 6", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: Companion 108.3 is confirmed for Construct X; the block length 24 of CX-012a buys calibration with power, and the block-null-primary proposal of CA-14 needs a block shorter than the cycle", supersedes=None),
 dict(id="CX-003", origin="CA-08 review 8A (proposed, never registered until the 19 Nov audit)", hypothesis="The Lab's Polarity and Seed Navigator gives, for every one of the 26 seeds, the workbook's exact-negative partner (H-001), and the offset rows it shows for a seed and its partner are exact negatives",
      scope="site/construct_x_lab.html, all 26 seeds", falsification="any mismatch", test="t_CX003 (headless browser, tools/lab_selftest.js)", data=WB + " and the published Lab page",
      criterion="26 seeds, 0 mismatches, 0 non-negative offset pairs", blinding="blind (not checked seed by seed before registration)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the navigator is CROSS-VALIDATED against the workbook", supersedes=None),
 dict(id="CX-008", origin="CA-08 review 8F (proposed, never registered until the 19 Nov audit)", hypothesis="The Transformation Laboratory's template is exact on the rule-generated melody at lag 8, and when the rule changes (step 5 to step 2 from t = 24) its failures fall only in the window where the lag-8 history straddles the change (t = 23 to 31), after which it is exact again",
      scope="Z/12, 48 notes", falsification="accuracy below 1 on the melody, failures outside 23 to 31, or none", test="t_CX008", data="generated",
      criterion="exact, failures confined to 23..31, exact after", blinding="blind (window predicted from lag 8 before running)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the composition-consistency test localises a rule change to within one lag", supersedes=None),
 dict(id="CX-009", origin="CA-08 review 8G (proposed, never registered until the 19 Nov audit)", hypothesis="The permanent register keeps every CA-08 field for every entry, a code fingerprint and time for every run, every entry ever registered, and REVISED for every superseded entry",
      scope="records/stp/registry.json", falsification="any missing field, unfingerprinted run, deleted entry, or superseded entry not REVISED", test="t_CX009", data="records/stp/registry.json",
      criterion="all four checks clean", blinding="NOT BLIND: the UP-04b overwrite was found by the audit rerun before registration and fixed in the runner", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the register meets its own specification", supersedes=None),
 dict(id="CX-015", origin="19 Nov audit: on sunspots the block null rejects (p = 0.005) where the iid null does not (p = 0.885)", hypothesis="With block length 24 the block null keeps the false-positive rate at or below 5 of 40 on smooth AR(1) noise (phi = 0.9, n = 300) with no cycle",
      scope="40 generated series, 99 surrogates", falsification="more than 5 of 40 at p <= 0.05", test="t_CX015", data="generated",
      criterion="<= 5 of 40", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if rejected, the block null is miscalibrated on smooth series and its sunspot result is not evidence of a cycle", supersedes=None),
 dict(id="CX-016", origin="19 Nov audit: the guide prints a Williams schedule that no code generated", hypothesis="construct_x.williams_schedule(6) is a Latin square covering all 30 ordered transitions once, equals the guide's printed table, and the construction balances carryover for every even n from 2 to 12",
      scope="n = 2..12 even", falsification="any check fails", test="t_CX016", data="none",
      criterion="all checks pass", blinding="NOT BLIND: the guide's table was verified by hand before registration", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the Six-Treatment Williams Crossover Schedule becomes IMPLEMENTED", supersedes=None),
 dict(id="CX-017", origin="review 2a55c661 section 4D, applied at the 19 Nov audit", hypothesis="The new periodicity interpretation reads supported on Mauna Loa CO2, unsupported on sunspots and unsupported on the first 400 digits of pi (iid null)",
      scope="three real or reference series", falsification="any other reading", test="t_CX017", data="records/data/ (co2, sunspots); pi digits",
      criterion="supported / unsupported / unsupported", blinding="NOT BLIND: p values of all three known from H-006b, H-006c, H-006d", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the Temporal Engine reports a conservative verdict alongside its numbers", supersedes=None),
 dict(id="CX-009-R1", origin="CX-009 rejected: six legacy runs (the CA-08 first runs of H-001 to H-005 and the proof record UP-01d) predate the runner and carry no fingerprint; and 'superseded implies REVISED' was a wrong criterion (H-017 is superseded by a refinement after a genuine failure and is rightly REJECTED)", hypothesis="Every entry carries the CA-08 fields and a status history; every run made by the runner carries a code fingerprint (the six legacy runs are the only exceptions); no entry has been deleted; and the REVISED entries H-004, UP-04b and CX-010 keep REVISED after rerun",
      scope="records/stp/registry.json", falsification="any check fails", test="t_CX009R1", data="records/stp/registry.json",
      criterion="all four checks clean", blinding="NOT BLIND: written after CX-009 failed", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the register meets its specification with its legacy exceptions named", supersedes="CX-009"),
 dict(id="H-023", origin="19 Nov audit: on sunspots the block null rejects (p = 0.005) and the iid null does not (p = 0.885), while the block null is calibrated on smooth noise (CX-015)", hypothesis="On white residuals around a trend, the kind of series the iid null generates, the Lagged-Increment Model's skill over the drift baseline is built in at 1 - sqrt(4/6) = 0.184 by the noise gains 4 and 6, so a smooth real series whose observed skill falls below that (sunspots, 0.115) cannot reach significance under the iid null",
      scope="100 generated series, n = 326 (the sunspot length), slope 0.3, sd 1", falsification="mean skill more than 0.03 from 0.184", test="t_H023", data="generated",
      criterion="|mean skill - 0.184| <= 0.03", blinding="blind (predicted from the operator coefficients before running)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: the iid null is biased against detection on smooth series, because its surrogates carry a built-in skill; the block null is the informative test there (CX-015), with blocks shorter than the cycle (CX-013)", supersedes=None),
 dict(id="CAP-01", origin="capability test 1 (19 Nov 2026): orbit addressing at any depth", hypothesis="The Complete Orbit Signature names orbits without walking them: on 4,000 state pairs at depth 3^7 (random, same-orbit by construction, and same-valuation) Lambda agrees with orbit membership found by walking in every case; and 10,000 states at depth 3^100, with valuations 0, 5, 40, 77 and 99, are classified in under 5 seconds, each label unchanged after 10^6 + 7 steps",
      scope="(Z/3^7)^2 and (Z/3^100)^2", falsification="any disagreement, a slow classification, a label that changes, or a valuation lost", test="t_CAP01", data="generated (seed 101)",
      criterion="0 disagreements; < 5 s; labels invariant; valuations [0, 5, 40, 77, 99] recovered", blinding="blind (the depth cap at r = 30 in 2.3.1 was fixed before registration)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="orbit classification becomes an O(depth) computation at any depth, where it was an enumeration to 3^6", supersedes=None),
 dict(id="CAP-02", origin="capability test 2: balanced comparison of 27 Navigators", hypothesis="The 13-round schedule compares all 351 pairs of 27 Navigators exactly once, where no random schedule of the same size does (200 tried); and from scheduled pairwise disagreement it identifies all three planted biased Navigators in at least 90% of 300 trials, more often than a random schedule of the same size",
      scope="27 simulated Navigators, 40 items, bias 1.2 sd", falsification="coverage below 351, a random schedule reaching 351, recovery below 0.9 or not above the random schedule's", test="t_CAP02", data="generated (seed 202)",
      criterion="351; random < 351; recovery >= 0.9 and > random", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="inter-Navigator agreement can be measured completely and evenly, so a biased reader shows", supersedes=None),
 dict(id="CAP-03", origin="capability test 3: independent support in comparison", hypothesis="Under uniform draws of six distinct values from 1 to 49 for Y and X, at least 10% of the Classic pooled flags (4 of 6) rest on references reused by more than one observation, so one-to-one matching withdraws them",
      scope="100,000 draws", falsification="share below 10%", test="t_CAP03", data="generated (seed 303)",
      criterion="share of pooled flags not met by matching >= 0.10", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the Construct can tell a flag carried by independent support from one carried by a reused reference", supersedes=None),
 dict(id="CAP-04", origin="capability test 4: choosing a forecaster before seeing the held-out data", hypothesis="On 300 series with a period-7 cycle, random slope 0 to 1.5 and noise sd 3, the noise-gain law read off the training part alone (LIS wins iff mean(D)^2 > var(D) for the seasonal differences D) names the held-out winner between the Lagged-Increment Model and seasonal-naive in at least 85% of series",
      scope="300 generated series, n = 182, 60/40 split", falsification="below 85%", test="t_CAP04", data="generated (seed 404)",
      criterion=">= 0.85", blinding="blind", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the instrument can say which rule to trust before the held-out data exist", supersedes=None),
 dict(id="CAP-05", origin="capability test 5 = CX-018 (Navigator speculation of 19 Nov): congruence of the Navigator Synthesis at orbit level and with matching", hypothesis="On the Congruence Register, same-orbit meetings (equal Lambda mod 9) occur at no more than 1.2 times their exact chance over the 729 residue triples, and one-to-one matching of the same-state and mirror meetings counts fewer meetings than pooling them",
      scope="records/congruence/domains.txt (all registered domains)", falsification="orbit ratio above 1.2, or matching not lower", test="t_CAP05", data="records/congruence/domains.txt",
      criterion="observed/expected <= 1.2 and matched < pooled", blinding="blind (not computed before registration)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: orbit-level congruence sits at chance, and matching is the part of the new mathematics that changes congruence counts", supersedes=None),
 dict(id="CAP-01-R1", origin="CAP-01, corrected: its valuation clause demanded exactly [0, 5, 40, 77, 99], but a state built as 3^r times a random pair has valuation at least r (exactly r only when the quotient pair is primitive)", hypothesis="As CAP-01, with the valuation clause stated correctly: every constructed state's valuation is at least its construction exponent r, and exactly r when the quotient pair is not divisible by 3",
      scope="as CAP-01", falsification="any disagreement, a slow classification, a changed label, or a valuation below r or wrong for a primitive quotient", test="t_CAP01R1", data="generated (seeds 101, 7)",
      criterion="0 disagreements; < 5 s; labels invariant; both valuation clauses hold", blinding="NOT BLIND: written after CAP-01's run", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="as CAP-01", supersedes="CAP-01"),
 dict(id="PHB-01", origin="Physics Initiative (APE-499): the known-answer benchmark, first computational part", hypothesis="The toolkit reproduces five established results (Noether's link between rotation invariance and angular momentum; the geodesic equation from the variational principle; the entanglement entropy ln 2 of a Bell pair; the black-hole first law dS/dM = 1/T_H; the Newtonian limit of relativistic kinetic energy with its (3/4)(v/c)^2 correction), and each paired control fails",
      scope="tools/physics_bench.py, five results, each with a control", falsification="any result outside its tolerance, or any control that passes", test="t_PHB01", data="none (computation only)",
      criterion="B1 drift < 1e-9 and control > 1e-3; B2 residual < 1e-4 and control > 0.1; B3 |S - ln 2| < 1e-12 and product < 1e-12; B4 rel. error < 1e-6 and control > 0.5; B5 correction ratio within 1e-2 of 1 at c = 100, 1000 and control off by > 0.4; all five", blinding="NOT BLIND: the answers are textbook results known to the author (CONSTRUCTIONAL, Core Part 3.18)", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the toolkit is fit for the reproduction milestone; it says nothing about the Navigator finding results it was not told (H-025)", supersedes=None),
 dict(id="H-029", origin="Navigator speculation of 19 November 2026 (the two layers of existence, Companion Part 233)", hypothesis="The share of single added terms (choices) that move a state of (Z/3^k)^2 to another orbit of the law keeps rising with the resolution: above 0.95 at 3^4, and higher still at 3^5",
      scope="(Z/81)^2 exhaustively (6,561 states x 6,560 nonzero offsets); (Z/243)^2 by 200,000 sampled pairs (seed 29)", falsification="share at 81 not above 0.95, or the sampled share at 243 not above the share at 81", test="t_H029", data="computation only",
      criterion="share(81) > 0.95 and share(243, sampled) > share(81)", blinding="NOT BLIND: the shares at 9 (0.736) and 27 (0.910) were computed before registration; 81 and 243 were not", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: at fine resolution nearly every choice changes the cycle a state lives in; the law alone never does", supersedes=None),
 dict(id="H-030", origin="Navigator observation of 19 November 2026 on the H-029 shares (Companion Part 233.8)", hypothesis="The share of single added terms that leave the orbit unchanged falls by about a third at each power of 3: at 3^6 it lies near 0.0103 / 3",
      scope="(Z/729)^2, 200,000 sampled (state, nonzero offset) pairs, seed 30", falsification="unchanged share outside 0.0027 to 0.0043", test="t_H030", data="computation only",
      criterion="0.0027 <= unchanged share at 729 <= 0.0043", blinding="blind for 729 (not computed before registration); the pattern was read from 9, 27, 81 and 243", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: the pattern holds one level beyond the data it was read from; a proof is still owed (UNPROVEN as a theorem)", supersedes=None),
 dict(id="AR-01", origin="The Drive archive read through the current record (docs/ARCHIVE_CONCORDANCE.md, 19 November 2026)", hypothesis="Every arithmetic statement checked in the heads of the archive (the V336 Rev.1 Companion and the formal discovery document of December 2025) recomputes as stated",
      scope="nine statements: five from the V336 Rev.1 Companion, four from the formal discovery document", falsification="any statement that does not recompute as stated", test="t_AR01", data="the statements as quoted in docs/ARCHIVE_CONCORDANCE.md",
      criterion="9 of 9 recompute", blinding="NOT BLIND: the statements were recomputed while reading, before registration; this entry records the recomputation reproducibly", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the archive's arithmetic is sorted into what carries forward and what does not; a failed statement is corrected in the concordance, never in the original", supersedes=None),
 dict(id="TR-01", origin="APE-503 to APE-505 (ME-01 to ME-03), received 19 November 2026", hypothesis="The mathematics of ME-01 to ME-03 recomputes as stated, and its counterparts in the law hold: det[b, T b] = N(b), so a one-direction choice is controlling exactly when N(b) is a unit; and history carries log2 9 bits when one coordinate of the state is observed",
      scope="ME-02 at a = -3, beta = 6 (fixed points, stability, bistable band, hysteresis); ME-01's learning identity; the law mod 9 and 27", falsification="any value that does not recompute", test="t_TR01", data="computation only",
      criterion="every check of tools/transformability.py --selftest passes", blinding="NOT BLIND: computed while reading, before registration; this entry records the recomputation reproducibly", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="the models of ME-02 and ME-03 enter the record as checked mathematics, beside the law, with their differences stated (Companion 233.13)", supersedes=None),
 dict(id="RC-01", origin="Navigator answer of 19 November 2026 (relations and consensus) and APE-506 (ME-04)", hypothesis="Two persons who each follow the law cannot reach the same state by symmetric scalar influence alone: modulo 9 never, for any influence k; over the reals the difference grows at least by sqrt(5)/2 per step for every strength of pull",
      scope="(Z/9)^2, every pair of distinct states, every k, 72 steps; the reals, pull 2a in [-3, 3]", falsification="any pair that agrees, or a real pull with spectral radius below 1", test="t_RC01", data="computation only",
      criterion="no agreement mod 9 and least radius = sqrt(5)/2 within 1e-4", blinding="NOT BLIND: computed before registration; recorded reproducibly", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="if passed: agreement between persons who each follow the law needs a choice aimed at their difference, or influence shaped by the law itself; averaging alone never yields it", supersedes=None),
 dict(id="RC-01-R1", origin="APE-508: the review of RC-01's wording (19 November 2026)", hypothesis="Persons who each follow the law do not reach agreement by symmetric scalar influence alone: modulo 9 never, for any influence; over the reals no pull contracts both modes (the least spectral radius of T - s is sqrt(5)/2), no rational pull makes T - s singular, so a nonzero difference with rational coordinates never vanishes and eventually grows; a real difference lying on the contracting eigenvector can shrink, and vanishes when s = -1/phi or phi",
      scope="as RC-01, with the real-number statement corrected", falsification="any agreement mod 9; a pull with radius below sqrt(5)/2; a rational pull making T - s singular; a rational difference that does not grow; or the eigenvector exception failing", test="t_RC01R1", data="computation only",
      criterion="all five checks hold", blinding="NOT BLIND: computed before registration", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="supersedes RC-01, whose wording said every difference grows; the corrected statement keeps the exception", supersedes="RC-01"),
 dict(id="RC-01-R2", origin="RC-01-R1 test-design defect: its growth threshold (1,000 in 40 steps) exceeds what the bound gives at pull 1/2 (1.118^40 = 87)", hypothesis="As RC-01-R1: no agreement by symmetric scalar influence mod 9; over the reals no pull contracts both modes (least radius sqrt(5)/2); no rational pull makes T - s singular, so a nonzero rational difference never vanishes and grows; a real difference on the contracting eigenvector can shrink, and vanishes at s = -1/phi or phi",
      scope="as RC-01-R1", falsification="as RC-01-R1, with growth judged as more than tenfold in 40 steps (the bound gives at least 1.118^40 = 87)", test="t_RC01R2", data="computation only",
      criterion="all five checks hold, growth threshold tenfold in 40 steps", blinding="NOT BLIND: the defect of RC-01-R1 was seen before registration", on_pass="VERIFIED COMPUTATION", on_fail="REJECTED",
      consequence="supersedes RC-01-R1, whose threshold was a test-design defect", supersedes="RC-01-R1"),
]
FIRST_RUN = {  # results of the 18 Nov 2026 first run, kept as history
 "H-001": "PASS", "H-002": "FAIL", "H-003": "FAIL", "H-004": "FAIL (reported 7 of 9; script duplicated H-002)", "H-005": "PASS"}


def register():
    reg = load()
    for e in PRE:
        if e["id"] in reg["entries"]:
            continue
        e = dict(e, date=now(), runs=[], status="UNPROVEN")
        if e["id"] in FIRST_RUN:
            e["runs"].append({"time": "2026-11-18 (first run)", "run_state": "RAN", "outcome": FIRST_RUN[e["id"]],
                              "result": "see CA-08 first run", "code_sha": None, "data_sha": None})
        if e["id"] == "H-004":
            e["status"] = "UNPROVEN"
        if e["id"] in ("H-006", "CX-010"):
            e["runs"].append({"time": now(), "run_state": "NOT RUNNABLE", "outcome": None,
                              "result": e["data"], "code_sha": None, "data_sha": None})
        reg["entries"][e["id"]] = e
    save(reg)
    print(f"registered: {len(reg['entries'])} entries")


def run(ids=None):
    reg = load()
    code_sha = {"stp": sha(__file__), "construct_x": sha(cx.__file__)}
    wbp = os.environ.get("OMEGA42_WORKBOOK")
    for i in ids or list(TESTS):
        e = reg["entries"][i]
        try:
            passed, result = TESTS[i]()
            state, outcome = "RAN", "PASS" if passed else "FAIL"
            new = e["on_pass"] if passed else e["on_fail"]
            if e["status"] == "REVISED":
                new = "REVISED"   # a REVISED entry keeps its status on rerun; the run stays on file
            if new != e["status"]:
                e.setdefault("status_history", []).append({"time": now(), "from": e["status"], "to": new,
                                                           "reason": f"run outcome {outcome}"})
            e["status"] = new
        except FileNotFoundError as ex:
            state, outcome, result = "NOT RUNNABLE", None, str(ex)
        dsha = sha(wbp) if "workbook" in e["data"] else sha(DATA / "sunspots_yearly_silso_v2.csv") if "sunspot" in e["data"] else sha(DATA / "mauna_loa_co2_monthly_nist_1974_1987.csv") if "co2" in e["data"] else None
        e["runs"].append({"time": now(), "run_state": state, "outcome": outcome, "result": result,
                          "code_sha": code_sha, "data_sha": dsha,
                          "environment": {"python": sys.version.split()[0], "platform": sys.platform},
                          "author": "Navigator (claude-opus-5-5)", "reviewer": None})
        print(f"{i:9s} {state:12s} {outcome or '-':5s} -> {e['status']}")
    save(reg)


INDEPENDENT = {"H-001", "H-002", "H-004-R1", "H-004-R2", "H-005", "H-011", "H-014", "CX-003"}


def evidence(e):
    """Three provenance dimensions, kept as metadata beside the status (they never replace it)."""
    last = e["runs"][-1] if e["runs"] else {}
    m = "M" if e["status"] == "PROVED" else "-"
    c = "C" if last.get("run_state") == "RAN" and last.get("outcome") == "PASS" else "-"
    i = "I" if e["id"] in INDEPENDENT else "-"
    return m + c + i


def report():
    reg = load()
    lines = ["# Ω42 Speculation Register (generated by tools/stp.py — do not edit by hand)", "",
             "Statuses: " + " · ".join(STATUSES) + ". Run states: NOT RUN · RAN · NOT RUNNABLE. Entries are never deleted.", "",
             "Evidence (review 2a55c661, section 6): M = mathematical, a written proof; C = computational, the registered test ran and passed;",
             "I = independent, reproduced by a separate implementation (I-001, tools/independent_check.py) or checked against a second artefact (CX-003).", "",
             "| ID | Hypothesis | Criterion (fixed before run) | Blinding | Last run | Evidence | Status |", "|---|---|---|---|---|---|---|"]
    for e in reg["entries"].values():
        last = e["runs"][-1] if e["runs"] else {"run_state": "NOT RUN", "outcome": None, "result": ""}
        res = last["result"]
        if isinstance(res, dict):
            res = "; ".join(f"{k}={v}" for k, v in res.items() if k in ("holds_for", "fails_for", "property_absent_for",
                            "distinct_mod_9", "false_positives_p<=0.05", "violations_of_positional<=matching<=pooled",
                            "cached_agree", "cached_missing"))
        ev = evidence(e)
        lines.append(f"| {e['id']} | {e['hypothesis']} | {e['criterion']} | {e['blinding']} | "
                     f"{last['run_state']} {last['outcome'] or ''} {res if isinstance(res, str) else ''} | {ev} | **{e['status']}** |")
    (ROOT / "docs" / "SPECULATION_REGISTER.md").write_text("\n".join(lines) + "\n")
    print("report written")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "report"
    {"register": register, "run": lambda: run(sys.argv[2:] or None), "report": report}[cmd]()
