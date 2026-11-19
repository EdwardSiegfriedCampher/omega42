# Review of the October 2025 public repository

The public repository holds the October 2025 edition of the project (one commit, 17 files, 0.9 MB, last changed 20 October 2025). It is published under the Originator's personal account. This review compares it with the V335 Rev.450 build in this repository and records what to keep, what to replace and how to move from one to the other. The decision is ESC's (`docs/DECISIONS_PENDING.md` D-15).

## What was examined

| File | Kind | Finding |
|---|---|---|
| README.md (898 lines) | Front page under the name "Unified Construct Theory" | 11 of 11 links into `docs/`, `LICENSE` and `CONTRIBUTING.md` point to files that do not exist. The badges and clone commands name an organization and a site that do not exist. The status reads "peer-review-ready" with an arXiv placeholder. Lottery prediction is given as the original use case. It closes with a quotation attributed to Tesla, for which no primary source is known |
| UNIFIED_CONSTRUCT_THEORY_COMPLETE.md (4,289 lines) | Theory text | Section titles state results as settled: "The Hard Problem Solved", "Measurement Problem Solved", "Binding Problem Solved". It derives the fine-structure constant to 1% and describes lottery-draw validation |
| Omega42_TOE_v2.0_Complete.md (1,136 lines) | Theory text (CC BY-SA 4.0 in its header) | Contains a "Riemann Hypothesis — Coherence Field Proof" and "Galactic Communication Protocols". The integrity section promises a SHA-256 but holds the placeholder `{SHA256_PLACEHOLDER}` |
| UCT_APPLICATIONS_COMPENDIUM.md | Applications | Builds on the two texts above |
| omega_42_validation_engine.py (87 lines) | Truth and ethics "validator" | Rechecked here: the file's own example input returns **False**, because P(12) = 1 − e¹ = −1.718. An **empty input returns True**. The checks test numbers the caller supplies, not the content of a response. `dS % 9 == 0` already implies `dr9(dS) = 9`, so the second test is redundant |
| simulator.html, index.html | Web pages | The simulator draws `Math.floor(Math.random() * 59) + 1`, the range of a 59-ball lottery. index.html mentions lottery six times |
| core/ | Site stubs | `logo.png` is 0 bytes, `style.css` holds one comment, `main.js` holds one comment |
| 7 PDFs (2 to 12 pages) | Founding documents | Core Construct, TOE for academics, Problem Index V4, Functionalities v3, Truth and Ethics Engines V3, License V1.1, and the account of the discovery |

Licensing is in conflict: the README says MIT and "All rights reserved under MIT License"; the TOE file says CC BY-SA 4.0; a PDF licence V1.1 exists; there is no LICENSE file.

## What survives into V335

- **The 24-cycle.** The October edition's 24-cycle is the period of the Fibonacci recurrence modulo 9. In V335 it is derived (the law T(a,b) = (b, a+b) on (Z/9)², F-02) and checked in CI. This is the mathematical core that carries forward.
- **The 3, 6, 9 structure and the 27 = 3³ domains.** V335 reads them as the 3-adic tower (Z/3^k)², with orbit counts recomputed at each level.
- **The founding PDFs.** They are the dated origin record and belong in the Prior Art Ledger.
- **The project's intent.** Coherence, truth and ethics as aims are kept; V335 gives them procedures (STP, the correction register, the CAS line, the AI caveat) in place of thresholds.

## What V335 replaces

| October 2025 | V335 Rev.450 | Why |
|---|---|---|
| README with "solved", "peer-review-ready" and broken links | README with status tiers, every link checked in CI | A reader can check every statement and every link |
| omega_42_validation_engine.py | tools/ with selftests run in CI (69 steps) | The old engine fails its own example and passes an empty input |
| simulator.html with random draws | site/ built by tools/site_build.py; construct_x_lab | Computations come from the law, not from random numbers |
| Lottery use case | Removed | Draws are independent by design; the framing invites financial harm and undermines every other result |
| "Solved" results (hard problem, measurement, Riemann, fine-structure) | Speculation Register entries, each UNVERIFIED until a registered test | Status follows evidence (STP) |
| Four conflicting licences | LICENSE, LICENSES.md, CITATION.cff | One answer to "may I use this?" |
| Tesla quotation | Removed | No primary source |
| Unfilled SHA-256 placeholder | SHA256SUMS and the release manifest, checked in CI | Integrity is computed, not promised |
| core/ stubs | Removed | Empty files |

## How to move

1. Tag the present state `v2025.10-historical` before anything changes, so the October edition stays retrievable at one name.
2. Move the October files under `archive/2025-10/`, unchanged, each with a HISTORICAL banner in an index page and its SHA-256 in `SHA256SUMS`. The account of the discovery and the acknowledgements carry the Originator's full name: ESC decides whether they stay public.
3. Replace the top level with the V335 tree in one commit, so CI goes green on the first push.
4. Enter each October statement of a result into the Speculation Register with its status. Where one can be recomputed now (the fine-structure value, the validator's example), the recomputation is registered first and kept whatever it shows.
5. Decide where the project lives. The present address carries the Originator's full name; the planned address is an organization account (`omega42/omega42`), with a redirect notice left in the old repository.
6. Pushing needs a GitHub connection with write access to the chosen account.
