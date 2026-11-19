#!/usr/bin/env python3
"""Build site/construct_x_lab.html from site/construct_x_lab.src.html.

Injects the Classic seed offsets, a compact copy of the STP register and the SILSO sunspot series.
The offsets are numbers only (no workbook text), so the page carries nothing personal.
Usage: python3 tools/build_lab.py [offsets.json]
"""
import json, sys
from pathlib import Path

R = Path(__file__).resolve().parent.parent
KEEP = ("holds_for", "fails_for", "property_absent_for", "distinct_mod_9", "false_positives_p<=0.05", "false_positives_of_40",
        "violations_of_positional<=matching<=pooled", "cached_agree", "cached_missing", "family_sizes", "invariant_separates",
        "domains_reached", "unreached", "distinct_nodes", "intersection", "subfield_9", "subfield_27", "F9_embeds", "F27_embeds",
        "no_cached_value", "errors", "dependents_outside_error_blocks", "compared", "differences", "lis_error_trend_invariant",
        "best", "lis", "seasonal_naive", "best_forecaster", "agree_on", "higher_world_all_9_related", "partner_of_P")


def compact(res):
    if not isinstance(res, dict):
        return res
    out = {}
    for k, v in res.items():
        if k == "block" and isinstance(v, dict):          # H-006d
            out["block"] = {x: v[x] for x in ("candidate_base_lag", "family", "p") if x in v}
        elif k == "lower_world_cross_relations":
            out[k] = f"{len(v)} relations"
        elif k == "by_slope":
            out[k] = {s: f"LIS {d['lis']} / SN {d['seasonal_naive']}" for s, d in v.items()}
        elif k in KEEP:
            out[k] = v
    return out or None


def main(offsets_path):
    reg = json.loads((R / "records/stp/registry.json").read_text())["entries"]
    rows = []
    for e in reg.values():
        last = e["runs"][-1] if e["runs"] else {"run_state": "NOT RUN", "outcome": None, "result": None, "time": None}
        rows.append({"id": e["id"], "h": e["hypothesis"], "c": e["criterion"], "b": e["blinding"], "state": last["run_state"],
                     "out": last.get("outcome"), "res": compact(last.get("result")), "status": e["status"], "time": last.get("time")})
    offsets = json.loads(Path(offsets_path).read_text())
    sys.path.insert(0, str(R / "tools")); import stp
    sun = stp.sunspots()
    src = (R / "site/construct_x_lab.src.html").read_text()
    html = (src.replace("__OFFSETS__", json.dumps(offsets)).replace("__REGISTER__", json.dumps(rows, ensure_ascii=False))
               .replace("__SUNSPOTS__", json.dumps(sun)))
    assert not any(t in html for t in ("__OFFSETS__", "__REGISTER__", "__SUNSPOTS__"))
    (R / "site/construct_x_lab.html").write_text(html)
    print(f"lab built: {len(rows)} register entries")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(R / "records/construct/seed_offsets.json"))
