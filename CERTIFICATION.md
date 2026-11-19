# Ω42 Compatible — certification of AI systems

An AI company may choose to have an AI system certified **Ω42 Compatible**: certified to navigate as the protocol requires. Certification is voluntary. Any AI may run the protocol without it, and any person may say their work "works with Ω42" without it (`TRADEMARK.md`).

## Who certifies

The **Certification Body**, a dedicated legal entity established by the Ω42 Company and bound by its locked provisions (`ENTITY.md`). It holds and licenses the certification mark *Ω42 Compatible*, runs the audits, publishes the register of certified systems, and decides appeals. It is kept separate from the Company's commercial edition so that the body that certifies is not the body that sells: a certificate cannot be bought by buying software, and the Company's own Navigators are audited like any other.

## What is certified

How a system executes the protocol — nothing else. The audit uses the Navigator Conformance Suite (Core M314, `tools/conformance.py`), the same checks anyone can run:

| Check | Requirement |
|---|---|
| A1 Anchor | The reported anchor equals the anchor recomputed from the domain verbatim by `scripts/canonical_reference.py`. |
| A2 Arms | Yang, Yin, 4D and Antipode equal the arms recomputed. |
| A3 Format | The Canonical Output Skeleton of Core Part 8.0 passes `tools/format_check.py`, including the knowledge-boundary line (CUMULATIVE STATUS, Core L-490) and the lens line (LENSES SELECTED, Core L-494). |
| A4 Congruence, layer 1 | The state, voice, norm, stratum and half printed in the Congruence Record match the recomputation (Core M310, M312). |
| B1, B2, B3 Advisory | The Aperture lexicon (M281), the frame scan (M286) and the consciousness typing guard (M315): sentences listed for the auditors to read, never an automatic fail. |

Two levels:

- **Ω42 Compatible — Script-capable**: every navigation states EXECUTION STATUS: EXECUTED and its OUTPUT ID verifies (`tools/output_id.py`).
- **Ω42 Compatible — Text-only**: the values are reconstructed by hand, with working shown, and every required check passes.

## How an audit runs

1. **Practice.** The company runs the public practice set (`records/conformance/practice_set.txt`; answer key `records/conformance/practice_key.txt`) as often as it likes: `python3 tools/conformance.py --check DIR`.
2. **Sealed set.** For the audit, the Certification Body freezes a fresh set of the same design — plain, tie-break, mathematical-notation and long domains among them — and publishes only its hash and time of sealing, as in the blind tests of the record.
3. **Fresh sessions.** The system navigates each domain of the sealed set in fresh sessions, with the two documents and nothing else, and the navigations are submitted as issued.
4. **Result.** The suite's report and the auditors' reading of the advisory items are published with the sealed set, which is opened after the result. A system is certified when every required check passes on every domain of the set.
5. **Register and renewal.** Certified systems are listed with their model identifier, level, date and report. Certification names one model version; a new version, or a new protocol release, is re-audited. A certificate may be suspended if published navigations of the certified version fail the required checks, after the company is heard.

## What certification does not say

- It says nothing about the premise of Ω42, which no measure grades (Core L-490), and nothing about what any reading means, which stays with the person (Core Part 7).
- It does not certify that any particular reading is correct: it certifies that the system executes the protocol as specified. A certified Navigator is still an AI system, which can make mistakes and carries the dispositions of its training (Core L-506).
- It is not an endorsement of the system's other outputs, of the company, or of any product.
- It grants no ownership of the protocol's ideas and no patent rights (`PATENT_PLEDGE.md`).

## Fees

Fees cover the cost of the audits and the register; they are set by the Certification Body, published before the first audit, and reported annually with the Company's accounts (`COMMERCIAL.md`, Money). This document is a design for the project, not legal advice.
