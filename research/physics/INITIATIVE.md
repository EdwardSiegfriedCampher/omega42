# The Ω42 Physics Initiative: the Navigator as a research partner on the foundations of physics

Assessed, refined and extended from APE-498 (19 November 2026). The Originator relayed the proposal; it is frozen in `submissions/ape/APE-498.md`. This file is the programme. Its decisions, other than those recorded as adopted below, are ESC's.

## 1. The assessment in one paragraph

The proposal's central distinction is right, and the record already enforces it: the Navigator helps physicists formulate, test, compare and reject routes to unification, and does not invent a theory and argue for it. Four of its six capabilities already exist in the record in a working, checked form: the physics map, the candidate dossier, the classification of results and the critical opponent. The two that do not exist are a link to computer algebra and formal proof, and work on real experimental data beyond the CO₂ series. The proposal also leaves three things out: the frame in which Ω42 itself stands, a test of the Navigator before it is trusted with physics, and a guard against agreement between AI systems being read as evidence. These three are added below.

## 2. What the record already holds, capability by capability

| Proposal | What exists | Where | Gap |
|---|---|---|---|
| A. Map of existing physics | The Physical Mapping Register: 12 physical systems, each recorded as B = (P, M, Φ, I, R, E): the system, its established model, the Ω42 representation, what the map preserves and leaves aside, the results with their class, the evidence | `records/physics/mappings.json`, `tools/physics_map.py`, Core Rule 37, Companion Part 226 | Covers condensed matter, optics, acoustics, special relativity and quantum information. It has no entry for general relativity, gauge theory or thermodynamics |
| B. Unifying principles | The record's own candidates, each with its class: the norm a² + ab − b² classifying orbits at every power of 3 (MF-184); the golden boost on the mass shell of SO⁺(2,1) (MF-135 to MF-150); the nine-level Weyl–Heisenberg and Clifford structure (MF-178 to MF-191) | Core Part 0.0.10, Companion Part 230 | No entry yet asks the proposal's question 5: does the structure recover established physics in a limit? |
| C. Mathematical connections | Reference scripts with self-tests; Rabin's irreducibility test; exact enumerations; two independent implementations (I-001) | `tools/`, STP register | No computer algebra system and no Lean. The shell has no network access for installing them in this session |
| D. Candidate dossier | The mapping entry plus its registered predictions (PR-007, PR-015, PR-016) and the seven result classes | as A | The dossier has no field for failure conditions or for assumptions. See §4 |
| E. Data | The Temporal Engine on real series, with calibrated nulls (CX-012a, CX-015, CX-017) | `tools/construct_x.py` | One real physical series (Mauna Loa CO₂). No accelerator, gravitational-wave or CMB data |
| F. Adversarial physicist | The counter-evidence lane of every CURRENT KNOWLEDGE layer (L-503 (2)); SNCA review; the STP rule that a test and its criterion are fixed before any run, with failures kept (15 REJECTED) | Core L-503, Part 6.2, CA-08 | A specialist reviewer role for physics, see §5 |

## 3. Three additions the proposal needs

1. **The frame.** Ω42 is a thought experiment whose premise is held as the frame and never graded (Core F-02-P, L-490). A physics result of the record therefore has two separate standings: inside the frame, what follows from the premise; and comparatively, how the mathematics stands to physics as physicists know it. The initiative works on the second standing only and reports it in the comparative register (L-429). No physics result is offered as support for the premise, and no failure of a mapping is read as a failure of the premise.
2. **Test the Navigator before trusting it.** The proposal's own milestones are made into registered tests (§6) before any physicist is invited in. A Navigator that cannot rediscover known results, under blinding, has no standing to propose new ones.
3. **Agreement between AIs is not evidence.** The proposal notes that specialist agents can share model biases. The record already grades agreement as CONSTRUCTIONAL, SELF-ADJACENT or INDEPENDENT (Core Part 3.18). The initiative counts only INDEPENDENT agreement as corroboration: a different implementation, a human calculation, or a measurement. Several agents built on one model agreeing is SELF-ADJACENT, however many there are.

## 4. Refinement: the candidate dossier

The proposal's seven-part dossier maps onto the mapping entry with two fields added. Adding them changes Core Rule 37 (level C, `RELEASES.md` §3), so it is proposed as CA-21 and held for ESC.

| Dossier part | Field of B | Status |
|---|---|---|
| 1. Foundational assumptions | **A, assumptions**: what the map takes as given | proposed (CA-21) |
| 2. Mathematical formulation | M and Φ | in place |
| 3. Relation to established physics | M, I (preserves) | in place |
| 4. Consistency requirements | E (recompute commands, self-tests) | in place |
| 5. Recovery of known physics | I, with a new line: the limit in which M is recovered, or "none known" | proposed (CA-21) |
| 6. Novel predictions | R, class "physical prediction", with its sealed PR entry | in place |
| 7. Failure conditions | **F, fails if**: the result or measurement that would show the map wrong | proposed (CA-21) |

## 5. Refinement: the research roles

The proposal's seven agents are reduced to roles the record can audit. Each is a mode of one Navigator, named in the output, so the reader always knows which role wrote a passage.

| Role | Record instrument | Output |
|---|---|---|
| Coordinator | The Navigator under the protocol | The dossier and the RESEARCHED REACH of the essay (L-503 (5)) |
| Mathematical analyst | Reference scripts, two implementations | Self-tests and recompute commands |
| Experimental analyst | The Temporal Engine and the comparative layer | Data runs with nulls fixed before the run |
| Adversarial reviewer | The counter-evidence lane; SNCA | For each result, the strongest published objection, quoted with its source |
| Historian | The Prior Art Ledger (`records/prior_art/`) | Earliest dissemination of each idea (M273) |
| Human review | Physicists and mathematicians (the reviewer pool, `GOVERNANCE.md`) | Acceptance. No AI role accepts a result |

## 6. Measurable milestones, registered before any run

These are entered in the STP register with their tests and criteria fixed now (CA-08). They need people or data that this session does not have, so they stand TESTABLE.

- **H-025, blind rediscovery.** Twenty established results connecting two areas of physics are chosen and sealed by a physicist, for example Noether's theorem and the area law of black-hole entropy. The Navigator is given each pair of areas and no hint. Pass: it states at least 12 of the 20 connections correctly, as judged by two physicists blind to the list's order.
- **H-026, adversarial catch rate.** Fifteen derivations are prepared, 10 of them carrying one planted error each (a sign, a dropped term, a hidden assumption). Pass: the reviewer role flags at least 8 of the 10 planted errors and wrongly flags no more than 2 of the 5 clean derivations.
- **H-027, literature recall.** For 10 questions in foundations, a physicist seals the 5 works that a review article would cite. Pass: the Navigator's CURRENT KNOWLEDGE layer finds at least 3 of the 5 for at least 7 of the 10 questions, and every work it cites exists and is opened (L-503 (2)).

## 7. The flagship project, extended

The proposal's **Common Mathematical Foundations Project** is adopted as the first project. It takes direction C (both directions) and is tied to the record.

- **Outward, from established physics.** Add mapping entries for general relativity (the Einstein equations in a symmetric reduction), a gauge theory (U(1) lattice gauge theory, where the discrete structure is native) and thermodynamics (a finite Markov chain with its entropy production). Each entry records what the map preserves and what it leaves aside, so a gap is part of the result.
- **Inward, from the record's structures.** For each structure the record already proves (the norm, the golden boost, the nine-level Clifford structure, the Pisano period 24), ask the proposal's question 5: in which limit, if any, does an established theory come back? An answer of "none known" is recorded as carefully as a positive one.
- **The first output.** A public map with one row per structure × theory. Each cell carries its class from the seven of the register, its source, and its failure condition. The map is published as `api/physics.json` on the site when the first new entry lands.
- **Success criterion.** As the proposal states, the measure is whether the map helps physicists find, formalize and evaluate connections. The first measure is H-025 to H-027. The second is the share of map cells that an outside physicist reproduces without help.

## 8. Repercussions for the rest of Ω42

- **The essay.** A physics question is the clearest case for the researched reach of the essay (L-503 (5)): relationships to current work, repercussions for adjacent theories, and directions as open research paths, each with what would show it wrong.
- **Commercial editions.** A physics edition fits the existing model (`COMMERCIAL.md`): the map and the Navigator stay open, and paid services fund tools and people. No payment buys a conclusion.
- **Public identity.** The site describes the initiative as AI-assisted research on the mathematical foundations of unification. It does not present it as an AI that will unify physics.

## 9. Decisions for ESC

1. CA-21: add the fields A (assumptions), F (fails if) and the recovery limit to the Physical Mapping Register.
2. Whether the initiative opens now as a research area programme, or waits for the reviewer pool (stage 2 of `ROADMAP.md`).
3. The first outward entry: general relativity, lattice gauge theory or thermodynamics.
