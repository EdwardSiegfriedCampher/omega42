# Decisions pending ESC

Each open decision is listed on its own, so that a decision on one never implies a decision on another (APE-501 section 9). Each entry gives the exact proposed change, the rule as it stands, the reason, what else it touches, the test evidence, and whether it changes normative behavior. The reviews' recommendations are quoted where they exist. They are advice; ESC decides.

## D-01 CA-19, the researched reach of the essay
- **Proposed change:** Core L-503 condition (5) and Step 14.3, as now in the Core text (applied, pending ratification). The Navigator declares its scope (aspects judged materially relevant, those left aside, a stopping rule). It seeks credible counter-evidence without manufacturing disagreement. It names each relationship as analogy, correspondence, equivalence, derivation, correlation, causation or extension, with causation only where supported. It writes repercussions and directions where they apply. Every [n] resolves to a full reference in the layer. A CORRECTION block follows the essay when the reach finds a material error in THE ANSWER, which stands as sealed. The RESEARCHED REACH line reports its completeness.
- **Current rule (before CA-19):** sources never enter the essay (L-503 (1)); the essay does not instruct (Check 7).
- **Reason:** the Originator's direction of 19 November; the four refinements of APE-501 section 1, all applied.
- **Affects:** Step 14.3, L-503, Check 7, the format check from 20 November 2026, Companion 12.5.1 to 12.5.6.
- **Evidence:** 15 format-check self-tests (`python3 tools/format_check.py --selftest`). No navigation has yet used the reach.
- **Normative:** yes (level C).
- **Review's recommendation (APE-501):** approve with the four refinements.

## D-02 CA-21, the candidate dossier
- **Proposed change:** Core Rule 37 gains three fields for each entry of the Physical Mapping Register: A (assumptions), F (fails if, kept apart as mathematical, physical and explanatory failure) and the recovery test (the limit in which the established theory returns, stated by a physicist with equations, parameter regime, approximation and tolerance, or "none known"). The thirteen-section dossier of APE-501 becomes the standard for significant investigations, in proportion: an inapplicable section is named as such, never filled.
- **Current rule:** B = (P, M, Φ, I, R, E).
- **Reason:** hidden assumptions and unproven recovery are the two common failures of speculative theory (APE-498, APE-501).
- **Affects:** `records/physics/mappings.json`, `tools/physics_map.py`, Companion Part 226.
- **Evidence:** none yet; the fields are empty until adopted.
- **Normative:** yes (level C).
- **Review's recommendation:** approve.

## D-03 Opening the Physics Initiative
- **Proposed change:** open now as the **Founding Research Pilot**: building the toolkit, testing the Navigator, reproducing known results, the first dossiers, inviting physicists and reviewers. The **Reviewed Research Programme**, which may publish reviewed scientific results, opens only when at least two independent external reviewers from different institutions are in place.
- **Reason:** APE-501 section 3.
- **Evidence:** PHB-01 (5 of 5, toolkit only); H-024 to H-028 not yet run.
- **Normative:** no (level B).

## D-04 The first outward physics entry
- **Options:** general relativity, thermodynamics, lattice gauge theory.
- **Review's recommendation (APE-501):** general relativity first (geometry, invariance, the equivalence principle, the action, the field equations), then thermodynamics, then lattice gauge theory. **Navigator's note:** symmetry and conservation is the qualification project before any of the three (APE-500).
- **Normative:** no.

## D-05 The shape of the initiative (APE-500 section 9)
- **Decision 1, structure:** A independent programme; B dedicated institute; C a programme designed to become an institute. *Review's choice: C.*
- **Decision 2, openness:** A open from the beginning; B open core with private workspaces; C institution-led at first. *Review's choice: B.*
- **Decision 3, foundations:** A several competing foundations, weighed equally; B information leads; C relational and structural principles lead. *Review's choice: A.*
- **Navigator's note:** choice A on decision 3 matches the frame. No physics result is offered as support for the premise of Ω42, and the initiative remains able to challenge that premise (APE-501 section 13).

## D-06 CA-17, the axiom rule (Core 10.5.2)
- **Exact text:** "No result of Construct X becomes a foundational premise of Omega42 because Construct X produced it; it enters only through the review its status requires."
- **Current rule:** none on this point.
- **Reason:** review 2a55c661, section 7.
- **Affects:** Core Part 10.5.2 only. The other CA-17 items are applied and are not part of this decision.
- **Evidence:** not testable; a rule of admission.
- **Normative:** yes.

## D-07 Workbook MP!F10 and MP!G10: the MODE tie rule
- **Facts (W-002):** a full LibreOffice recalculation agrees with the workbook on 104,917 of 104,925 formula cells. MP!F10 and MP!G10 differ because MODE breaks a tie differently: Excel gives 219, LibreOffice 218.
- **Decision:** state the intended tie rule (first in argument order, as Excel, or another).
- **Affects:** the cached values of two cells; no dependents beyond the error blocks (W-001).
- **Normative:** no (the workbook is frozen Classic; the decision documents its intent).

## D-08 Workbook REV!AJ51:AO51 (and REV!AI51): repair or retire
- **Facts (W-002):** the COUNTIF criteria in these cells carry a silent #REF!; the six cells and REV!AI51 account for the remaining differences.
- **Decision:** repair the references, or retire the cells with a note.
- **Normative:** no.

## D-09 M310 congruence: orbit relation and matching
- **Proposed change:** add to M310 (tools/congruence.py) the orbit relation (equal Λ mod 9) and one-to-one matching of same-state and mirror meetings.
- **Evidence:** CAP-05 (VERIFIED COMPUTATION): orbit meetings occur at 0.86 of their exact chance, and matching lowers the count from 6 to 4 meetings.
- **Affects:** congruence counts reported in navigations.
- **Normative:** yes, for congruence reports.

## D-10 The curator's area proposals
- **Proposed change:** accept or decline the agent layer's proposed areas (`records/curation/agent/catalogue.md`): 155 high-confidence and 254 low-confidence proposals, and a new area, construct-and-workbook (19 items).
- **Evidence:** a spot check accepted about 8 of 16 proposals. The baseline (`tools/curator.py`) stays unchanged until a person accepts a proposal.
- **Normative:** no.

## D-11 CA-22, chronology checks (L-542)
- **Change, applied:** `tools/timestamp_check.py` in CI. Its rules: format YYYY-MM-DDTHH:MM:SSZ; no time later than the runner's clock plus 300 seconds; acceptance not before disclosure. It found and repaired 12 prose timestamps (COR-010).
- **Decision open:** APE-045 to APE-047 record acceptance 70 minutes before disclosure. The true times cannot be recovered from the record. ESC may supply them or confirm the records as they stand (COR-011).
- **Normative:** no (a check).

## D-12 Core margin
- **Recommendation (APE-501 section 7):** keep Rule 39 at 900 words, and aim for 830 to 850 words since the last seal. Never compress normative language to reach the number.
- **Now:** 880 words since seq_0185. The next seal resets the count.
- **Decision:** whether to adopt 850 as the working margin.

## D-13 The Meaningful Existence Initiative
- **Proposed change:** open the initiative (`research/philosophy/MEANINGFUL_EXISTENCE.md`), paired with the Common Mathematical Foundations Project. Projects A (channels and their evidence) and B (habit series with the Temporal Engine) can start now. The case design of project C needs consent, ethics review and family researchers.
- **Also for ESC:** whether any of the definitions ME-01 to ME-07 (Companion 233.4) should enter Core Part 10.5. Until then they stay Companion terminology.
- **Evidence:** H-029 and H-030 (VERIFIED COMPUTATION); the Choice Engine selftest.
- **Normative:** no (level B), unless definitions enter the Core.
