# The Ω42 Physics Initiative: the Navigator as a research partner on the foundations of physics

Assessed, refined and extended from APE-498 to APE-501 (19 November 2026). Open decisions are kept one by one in `docs/DECISIONS_PENDING.md`. The Originator relayed the proposal; it is frozen in `submissions/ape/APE-498.md`. This file is the programme. Its decisions, other than those recorded as adopted below, are ESC's.

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
4. Whether the physics material becomes Companion Part 233 when the initiative opens (section 10).
5. The appointment of a scientific lead, which starts the first-year calendar.

## 10. The detailed architecture (APE-499): assessed and refined

The second proposal gives the programme its working form: three tracks, six laboratories, seven platform layers, six gates, a research memory and an observatory. It agrees with sections 1 to 8. The table records what each part becomes in the record.

| Proposal | In the record | Refinement |
|---|---|---|
| Track A (physics to foundations), Track B (foundations to physics) | The outward and inward directions of section 7 | none |
| Track C (convergence and falsification) | The STP register, SNCA review, the counter-evidence lane | Track C's reviewer must be a human or an AI system of a different architecture. A reviewer on the same model is SELF-ADJACENT (Core Part 3.18), and Track C would then reconcile rather than challenge |
| Track C's "ranked research agenda" | — | **Questions** are ranked, never theories. The ranking criteria (mathematical maturity, empirical reach, cost) are published before any ranking is made |
| Six laboratories | Research areas under `research/physics/` | Virtual until the scientific lead is appointed. A laboratory owes reliable contributions, not a theory of unification |
| Layer 1, Core | The Core | none |
| Layer 2, evidence and provenance | Ω42-T01: status, test qualification, provenance and readiness kept apart (Core Part 10.5); each STP run records environment, code and data fingerprints | none. The proposal's own warning holds: a numerically implemented model is not thereby established |
| Layer 3, knowledge graph | The Physical Mapping Register | The proposal's seven relation labels become the graph's edge vocabulary, mapped onto the register's result classes: **mathematically equivalent** and **derived from** → established mathematical result or Ω42 internal result; **related by a limiting approximation** → the recovery limit (CA-21); **shares a structure** → structural correspondence; **empirically associated** → empirical comparison; **conjectured** → physical hypothesis; **disputed** → listed with both sides' sources. An edge never carries a stronger label than its weakest source supports |
| Layer 4, mathematics and computation | Reference scripts with self-tests, and the PHB-01 benchmark | SymPy, Lean and Jupyter are not installed here and package installs are off. Until they are, the standard library is used and each result says so. The reproduction rule (code, versions, inputs, outputs, environment) is already enforced by the STP run record |
| Layer 5, discovery and hypothesis | PROPOSED status; a suggestion is labeled PROPOSED until a registered test runs | none |
| Layer 6, six roles | The modes of section 5 | Literature analyst = historian plus the four lanes; synthesis researcher = coordinator. Named in each output |
| Layer 7, interface | The Lab and the site | A physics tab follows the first new mapping entry |
| A separate "Physics Research Companion" | — | **Not a second document.** It becomes a Part of the one Companion (proposed Part 233) when ESC opens the initiative. Two Companions would be two sources of authority over one Core (Core Part 10.5.1) |
| Gates G1 to G6 | G2 novelty = the Prior Art Ledger; G3 formalisation = registration with criterion fixed (CA-08); G4 consistency = self-tests and two implementations; G5 empirical relevance = the fails-if field (CA-21); G6 review = SNCA and human review | Adopted. A question that stops at a gate is recorded, with the gate and the reason, as REJECTED entries are kept today |
| Research identifiers Ω42-PHY-QG-0001 | PM- (mappings), PR- (predictions), H- (tests) | Adopted as **PHY-<laboratory>-<nnnn>** for an investigation, which links its PM-, PR- and H- entries |
| Benchmark suite with known answers | **PHB-01, run today: 5 of 5 established results reproduced, each control failing** (Noether; the geodesic equation from the variational principle; ln 2 for a Bell pair; dS/dM = 1/T_H; the Newtonian limit with its 3/4 correction). The control residual for a circle of latitude is 0.4546, which is sin 1 · cos 1 as theory requires | PHB-01 tests the toolkit, not the Navigator: its author knew the answers (CONSTRUCTIONAL). The Navigator is tested by H-025 to H-027, and by **H-028**: questions whose correct answer is "unknown" or "disputed" |
| The AI never certifies its own discoveries | `GOVERNANCE.md` §5; `agents/curator/SPEC.md` | Made precise: the STP runner sets VERIFIED COMPUTATION mechanically against a criterion fixed beforehand by a person. That is a record of a computation, not an acceptance. Entry into the initiative's accepted research record is by human review (G6) only |
| Unification Research Observatory, quarterly landscape report | The CURRENT KNOWLEDGE layer and the quarterly review (`RELEASES.md` §1) | Adopted as a quarterly report under the same source rules as L-503: dated sources, a search for challenge beside every search for agreement, no ranking of theories |
| First-year calendar | — | Kept as the plan. Its Q1 needs a scientific lead, so the calendar starts when one is appointed. Two of the 90-day items exist now: the record formats and a benchmark baseline. The knowledge graph exists in part (the register) |

## 11. The narrowed first year (APE-500)

The third review argues that the plan is too large for a first year, and that the method should come before the organization. The argument is sound, and the programme now takes this form.

- **Three groups, not six laboratories.** (1) Established physics and mathematical structures; (2) foundational principles and theory development; (3) mathematical validation and scientific criticism. Group 3 is Track C, with the independence rule of section 10. The six laboratories stay the long-term map.
- **Four subjects.** General relativity and spacetime geometry; quantum mechanics and quantum field theory; information theory and thermodynamics; the mathematical structures under physical law. Cosmology, particle physics and experiment enter as constraints, not as programmes.
- **Qualification before speculation.** The Navigator earns the right to propose by passing a qualification: retrieval (H-027), reproduction (PHB-01 for the toolkit, H-025 for the Navigator), error-finding (H-026) and knowing when it does not know (H-028). It is never measured by the sophistication of its speculation.
- **The adversarial reviewer's task.** "Assume the proposal is wrong; find the strongest reason why." The reviewer reconstructs the argument independently, searches for counterexamples and compares it with evidence. A human reviewer is required for any result the programme calls important.
- **No league table.** A candidate gets a profile of seven dimensions with no total: mathematical precision, internal consistency, recovery of established physics, empirical adequacy, novel predictions, reproducibility and open problems. Each dimension is marked MET, PARTLY, NOT MET or UNKNOWN. This replaces the ranked agenda of section 10 for theories. Questions may still be ordered, by criteria published first.
- **The central instrument: relationship classification.** `tools/relation_engine.py` classifies a proposed connection between two structures by fixed rules on two axes that are never merged:
  - *mathematical standing:* REJECTED, ANALOGY, ESTABLISHED CONNECTION, NEW DERIVATION or CONJECTURE;
  - *physical standing:* EXPERIMENTALLY SUPPORTED, TESTABLE PROPOSITION, CONSEQUENCE NAMED, NO TEST, or NO PHYSICAL CONSEQUENCE STATED.

  The order of the rules carries the discipline. A counterexample outranks everything. A map that is not defined precisely cannot rise above analogy. A published derivation is a known relation, whoever rediscovers it. A new derivation is a conjecture until someone else recomputes it. A profile that carries a score is refused. Five worked records are in `records/physics/relations.json`, with their classes in `relations_classified.json`, checked in CI:

| Record | Connection | Mathematical | Physical |
|---|---|---|---|
| R-001 | rotation invariance ↔ angular momentum (Noether) | ESTABLISHED CONNECTION | CONSEQUENCE NAMED, NO TEST |
| R-002 | horizon area ↔ entropy (first law, S = A/4) | ESTABLISHED CONNECTION | CONSEQUENCE NAMED, NO TEST |
| R-003 | E8 spectrum of the critical Ising chain ↔ the golden ratio (PM-008) | ESTABLISHED CONNECTION | EXPERIMENTALLY SUPPORTED (CoNb₂O₆, 2010) |
| R-004 | acoustic stacks ↔ the record's optical engine (PM-003) | CONJECTURE: the author's self-test only, no independent recomputation | CONSEQUENCE NAMED, NO TEST |
| R-005 | entanglement ↔ spacetime geometry, as a one-line statement | ANALOGY: no map written out | NO PHYSICAL CONSEQUENCE STATED |

  R-004 shows the engine's strictness: one of the record's own correspondences stays a conjecture until someone else recomputes it. R-005 is the flagship question as most people state it. The flagship's first task is to replace it with precise versions from the literature and classify each one.
- **One Navigator, five capabilities.** Retrieval, mathematical reasoning, computational execution, hypothesis exploration and independent criticism, coordinated by one Navigator that keeps the record. More autonomous agents are added only when a registered test shows that they improve the work.
- **The first year.** Q1: build and qualify the Navigator, and reproduce known results. Gate: the qualification tests pass. Q2: the qualification project, symmetry and conservation, across mechanics, field theory and general relativity. Gate: one dossier checked by someone independent. Q3: the flagship, quantum information and spacetime geometry, in both directions. Gate: one dual-direction investigation with reproducible mathematics. Q4: independent review, publication, assessment of the Navigator, partnerships. The action–causality–emergence study moves to year two.
- **The team.** A scientific director, two or three physicists or mathematical researchers, one AI and computational engineer, an external advisory group and specialist reviewers on call. Funding never decides whether a conclusion is accepted.

## 12. The review of the whole update (APE-501)

The fourth review assessed the update as a whole: CA-19, CA-21, the opening, the benchmarks, the timestamp failure and the release architecture. Its refinements are applied as follows.

- **CA-19 (the researched reach).** All four refinements are now in Core L-503 (5) and Companion 12.5.3 to 12.5.6: research limited to materially relevant aspects, with a declared scope and a stopping rule; counter-evidence sought without false balance; seven named kinds of relationship, with causation stated only where supported; and a CORRECTION block when the reach finds an error in THE ANSWER, which stays as sealed beside it. Every [n] must resolve to a full reference in the layer, and the line must report its completeness. The format check enforces both. Archived records are read under the rules of their date.
- **CA-21 (the dossier).** The dossier standard has thirteen sections: question, hypothesis, definitions, assumptions, formulation, derivation, relation to existing physics, recovery, failure conditions, predictions and tests, evidence and provenance, independent criticism, current assessment. Failure is kept in three kinds: mathematical, physical and explanatory. The recovery test is quantitative: equations, parameter regime, approximation and tolerance, stated by a physicist, never asserted by the Navigator. A section that does not apply is named as such, never filled with invented content. The Core change stays pending ESC (`docs/DECISIONS_PENDING.md` D-02).
- **Opening.** The Founding Research Pilot can open now. The Reviewed Research Programme waits for at least two independent external reviewers from different institutions (D-03).
- **Benchmarks.** H-024 to H-028 were tightened before any run: matched access and length, measures fixed in advance, mixed item types, varied and subtle planted errors, and a contamination guard (held-out items, a separate administrator, scores sealed until the end). "I cannot establish this" counts as correct where the evidence is insufficient.
- **What CI does not show.** Passing CI does not show that the researched reach improves answers, that the Navigator's physics is reliable, or that the thresholds are adequate. Those are H-024 to H-028, and the release record keeps the two apart (`records/releases/manifest.json`, dimensions).
