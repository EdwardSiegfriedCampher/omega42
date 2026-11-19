#!/usr/bin/env python3
"""relation_engine.py -- relationship classification.
Part of the Physics Initiative (research/physics/INITIATIVE.md section 11).

Takes a proposed connection between two structures (two areas of physics, or a structure of the record and an area of
physics) and classifies it by fixed rules, so that two readers given the same record reach the same class.

Two axes, never merged (Omega42-T01):
  MATHEMATICAL STANDING   REJECTED | ANALOGY | ESTABLISHED CONNECTION | NEW DERIVATION | CONJECTURE
  PHYSICAL STANDING       EXPERIMENTALLY SUPPORTED | TESTABLE PROPOSITION | CONSEQUENCE NAMED, NO TEST | NO PHYSICAL CONSEQUENCE STATED
and a profile of seven dimensions (APE-500 section 2E), each MET / PARTLY / NOT MET / UNKNOWN, with no total score.

A record is a JSON object:
  {"id", "a", "b", "statement",
   "definitions_precise": bool,            both structures defined, and the map between them written out
   "derivation": "none" | "published" | "new",
   "derivation_checked": bool,             a new derivation recomputed by an independent method or person
   "counterexample": bool,                 a case where the stated relation fails, inside its stated scope
   "structural_only": bool,                the two share a form (an equation shape, a group) with no map between them
   "physical_consequence": bool,           the relation implies something measurable
   "test_registered": str | null,          the STP id of a test fixed before any run
   "measured": str | null,                 a published measurement that agrees with the consequence (cited)
   "profile": {dimension: [value, note]}}
The rules are in classify(). Their order matters: a counterexample outranks everything; an undefined map cannot be
more than an analogy; a published derivation is a known relation, whoever rediscovers it.

    python3 tools/relation_engine.py FILE.json      classify each record in a JSON list
    python3 tools/relation_engine.py --selftest
Standard library only.
"""
import json, sys

DIMENSIONS = ("mathematical precision", "internal consistency", "recovery of established physics", "empirical adequacy",
              "novel predictions", "reproducibility", "open problems")
VALUES = ("MET", "PARTLY", "NOT MET", "UNKNOWN")


def classify(r):
    why = []
    if r.get("counterexample"):
        m = "REJECTED"; why.append("a counterexample inside the stated scope")
    elif not r.get("definitions_precise"):
        m = "ANALOGY"; why.append("the structures or the map between them are not defined precisely, so no derivation can be checked")
    elif r.get("derivation") == "published":
        m = "ESTABLISHED CONNECTION"; why.append("a published derivation exists")
    elif r.get("derivation") == "new" and r.get("derivation_checked"):
        m = "NEW DERIVATION"; why.append("a new derivation, recomputed independently")
    elif r.get("derivation") == "new":
        m = "CONJECTURE"; why.append("a new derivation not yet recomputed independently")
    elif r.get("structural_only"):
        m = "ANALOGY"; why.append("a shared form with no map between the structures")
    else:
        m = "CONJECTURE"; why.append("a defined map with no derivation")
    if r.get("physical_consequence") and r.get("measured") and m != "REJECTED":
        p = "EXPERIMENTALLY SUPPORTED"; why.append("measured: %s" % r["measured"])
    elif r.get("physical_consequence") and r.get("test_registered") and m != "REJECTED":
        p = "TESTABLE PROPOSITION"; why.append("test %s fixed before any run" % r["test_registered"])
    elif r.get("physical_consequence"):
        p = "CONSEQUENCE NAMED, NO TEST"
    else:
        p = "NO PHYSICAL CONSEQUENCE STATED"
    prof = r.get("profile", {})
    bad = [d for d in prof if d not in DIMENSIONS] + [d for d, v in prof.items() if v[0] not in VALUES]
    if bad:
        raise ValueError("unknown dimension or value: %s" % bad)
    profile = {d: prof.get(d, ["UNKNOWN", ""]) for d in DIMENSIONS}
    return {"id": r.get("id"), "mathematical_standing": m, "physical_standing": p, "because": why, "profile": profile}


def selftest():
    base = dict(id="T", a="x", b="y", statement="s", definitions_precise=True, derivation="none", derivation_checked=False,
                counterexample=False, structural_only=False, physical_consequence=False, test_registered=None)
    cases = [
        ("counterexample outranks a published derivation", dict(base, derivation="published", counterexample=True), "REJECTED", None),
        ("undefined map is an analogy even with a new derivation", dict(base, definitions_precise=False, derivation="new", derivation_checked=True), "ANALOGY", None),
        ("published derivation: established", dict(base, derivation="published"), "ESTABLISHED CONNECTION", None),
        ("checked new derivation", dict(base, derivation="new", derivation_checked=True), "NEW DERIVATION", None),
        ("unchecked new derivation is a conjecture", dict(base, derivation="new"), "CONJECTURE", None),
        ("shared form only: analogy", dict(base, structural_only=True), "ANALOGY", None),
        ("defined map, no derivation: conjecture", base, "CONJECTURE", None),
        ("consequence with registered test", dict(base, physical_consequence=True, test_registered="H-999"), None, "TESTABLE PROPOSITION"),
        ("consequence without test", dict(base, physical_consequence=True), None, "CONSEQUENCE NAMED, NO TEST"),
        ("a cited measurement: experimentally supported", dict(base, physical_consequence=True, measured="x 2010"), None, "EXPERIMENTALLY SUPPORTED"),
        ("a rejected relation is never a testable proposition", dict(base, counterexample=True, physical_consequence=True, test_registered="H-999"), "REJECTED", "CONSEQUENCE NAMED, NO TEST"),
    ]
    ok = True
    for name, r, m, p in cases:
        c = classify(r)
        good = (m is None or c["mathematical_standing"] == m) and (p is None or c["physical_standing"] == p)
        ok &= good; print(("  ok   " if good else "  FAIL ") + name)
    try:
        classify(dict(base, profile={"elegance": ["MET", ""]})); ok = False; print("  FAIL a dimension not among the seven is refused")
    except ValueError:
        print("  ok   a dimension not among the seven is refused")
    try:
        classify(dict(base, profile={"reproducibility": ["7/10", ""]})); ok = False; print("  FAIL a score is refused")
    except ValueError:
        print("  ok   a numerical score is refused")
    print("RELATION ENGINE SELFTEST:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        sys.exit(0 if selftest() else 1)
    if len(a) == 1:
        print(json.dumps([classify(r) for r in json.load(open(a[0], encoding="utf-8"))], indent=1, ensure_ascii=False))
    else:
        print(__doc__)
