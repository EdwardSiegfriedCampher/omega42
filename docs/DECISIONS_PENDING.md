# Decisions pending ESC

On 19 November 2026 ESC ratified the recommended option in every decision below (D-01 to D-16). Each entry keeps its text and carries its ratification. New decisions are added below as they arise.

Each open decision is listed on its own, so that a decision on one never implies a decision on another (APE-501 section 9). Each entry gives the exact proposed change, the rule as it stands, the reason, what else it touches, the test evidence, and whether it changes normative behavior. The reviews' recommendations are quoted where they exist. They are advice; ESC decides.

## D-01 CA-19, the researched reach of the essay
- **RATIFIED by ESC, 19 November 2026:** CA-19 with the four refinements of APE-501, as applied in the Core text.
- **Proposed change:** Core L-503 condition (5) and Step 14.3, as now in the Core text (applied, pending ratification). The Navigator declares its scope (aspects judged materially relevant, those left aside, a stopping rule). It seeks credible counter-evidence without manufacturing disagreement. It names each relationship as analogy, correspondence, equivalence, derivation, correlation, causation or extension, with causation only where supported. It writes repercussions and directions where they apply. Every [n] resolves to a full reference in the layer. A CORRECTION block follows the essay when the reach finds a material error in THE ANSWER, which stands as sealed. The RESEARCHED REACH line reports its completeness.
- **Current rule (before CA-19):** sources never enter the essay (L-503 (1)); the essay does not instruct (Check 7).
- **Reason:** the Originator's direction of 19 November; the four refinements of APE-501 section 1, all applied.
- **Affects:** Step 14.3, L-503, Check 7, the format check from 20 November 2026, Companion 12.5.1 to 12.5.6.
- **Evidence:** 15 format-check self-tests (`python3 tools/format_check.py --selftest`). No navigation has yet used the reach.
- **Normative:** yes (level C).
- **Review's recommendation (APE-501):** approve with the four refinements.

## D-02 CA-21, the candidate dossier
- **RATIFIED by ESC, 19 November 2026:** CA-21. Rule 37 now names the assumptions (A), what would make an entry fail (F) and the recovery test; the register and tools/physics_map.py carry the three fields, with "not yet stated" for the twelve earlier entries until a physicist states them.
- **Proposed change:** Core Rule 37 gains three fields for each entry of the Physical Mapping Register: A (assumptions), F (fails if, kept apart as mathematical, physical and explanatory failure) and the recovery test (the limit in which the established theory returns, stated by a physicist with equations, parameter regime, approximation and tolerance, or "none known"). The thirteen-section dossier of APE-501 becomes the standard for significant investigations, in proportion: an inapplicable section is named as such, never filled.
- **Current rule:** B = (P, M, Φ, I, R, E).
- **Reason:** hidden assumptions and unproven recovery are the two common failures of speculative theory (APE-498, APE-501).
- **Affects:** `records/physics/mappings.json`, `tools/physics_map.py`, Companion Part 226.
- **Evidence:** none yet; the fields are empty until adopted.
- **Normative:** yes (level C).
- **Review's recommendation:** approve.

## D-03 Opening the Physics Initiative
- **RATIFIED by ESC, 19 November 2026:** opened as the Founding Research Pilot; the Reviewed Research Programme waits for two independent external reviewers.
- **Proposed change:** open now as the **Founding Research Pilot**: building the toolkit, testing the Navigator, reproducing known results, the first dossiers, inviting physicists and reviewers. The **Reviewed Research Programme**, which may publish reviewed scientific results, opens only when at least two independent external reviewers from different institutions are in place.
- **Reason:** APE-501 section 3.
- **Evidence:** PHB-01 (5 of 5, toolkit only); H-024 to H-028 not yet run.
- **Normative:** no (level B).

## D-04 The first outward physics entry
- **RATIFIED by ESC, 19 November 2026:** symmetry and conservation first, as the qualification project; then general relativity, thermodynamics and lattice gauge theory, in that order.
- **Options:** general relativity, thermodynamics, lattice gauge theory.
- **Review's recommendation (APE-501):** general relativity first (geometry, invariance, the equivalence principle, the action, the field equations), then thermodynamics, then lattice gauge theory. **Navigator's note:** symmetry and conservation is the qualification project before any of the three (APE-500).
- **Normative:** no.

## D-05 The shape of the initiative (APE-500 section 9)
- **RATIFIED by ESC, 19 November 2026:** structure C (a programme designed to become an institute); openness B (open core with private workspaces); foundations A (several competing foundations, weighed equally).
- **Decision 1, structure:** A independent programme; B dedicated institute; C a programme designed to become an institute. *Review's choice: C.*
- **Decision 2, openness:** A open from the beginning; B open core with private workspaces; C institution-led at first. *Review's choice: B.*
- **Decision 3, foundations:** A several competing foundations, weighed equally; B information leads; C relational and structural principles lead. *Review's choice: A.*
- **Navigator's note:** choice A on decision 3 matches the frame. No physics result is offered as support for the premise of Ω42, and the initiative remains able to challenge that premise (APE-501 section 13).

## D-06 CA-17, the axiom rule (Core 10.5.2)
- **RATIFIED by ESC, 19 November 2026:** the axiom rule, as now in Core 10.5.2.
- **Exact text:** "No result of Construct X becomes a foundational premise of Omega42 because Construct X produced it; it enters only through the review its status requires."
- **Current rule:** none on this point.
- **Reason:** review 2a55c661, section 7.
- **Affects:** Core Part 10.5.2 only. The other CA-17 items are applied and are not part of this decision.
- **Evidence:** not testable; a rule of admission.
- **Normative:** yes.

## D-07 Workbook MP!F10 and MP!G10: the MODE tie rule
- **RATIFIED by ESC, 19 November 2026:** the intended tie rule is the first value in argument order, as Excel computes it; the cached values 219 stand.
- **Facts (W-002):** a full LibreOffice recalculation agrees with the workbook on 104,917 of 104,925 formula cells. MP!F10 and MP!G10 differ because MODE breaks a tie differently: Excel gives 219, LibreOffice 218.
- **Decision:** state the intended tie rule (first in argument order, as Excel, or another).
- **Affects:** the cached values of two cells; no dependents beyond the error blocks (W-001).
- **Normative:** no (the workbook is frozen Classic; the decision documents its intent).

## D-08 Workbook REV!AJ51:AO51 (and REV!AI51): repair or retire
- **RATIFIED by ESC, 19 November 2026:** the cells are retired with a note, not repaired; the workbook stays frozen as Construct Classic.
- **Facts (W-002):** the COUNTIF criteria in these cells carry a silent #REF!; the six cells and REV!AI51 account for the remaining differences.
- **Decision:** repair the references, or retire the cells with a note.
- **Normative:** no.

## D-09 M310 congruence: orbit relation and matching
- **RATIFIED by ESC, 19 November 2026:** M310 reports the orbit relation with its exact chance and the one-to-one count of meetings (tools/congruence.py).
- **Proposed change:** add to M310 (tools/congruence.py) the orbit relation (equal Λ mod 9) and one-to-one matching of same-state and mirror meetings.
- **Evidence:** CAP-05 (VERIFIED COMPUTATION): orbit meetings occur at 0.86 of their exact chance, and matching lowers the count from 6 to 4 meetings.
- **Affects:** congruence counts reported in navigations.
- **Normative:** yes, for congruence reports.

## D-10 The curator's area proposals
- **RATIFIED by ESC, 19 November 2026:** the new area construct-and-workbook is accepted; the other proposals are accepted one by one by a person, since the spot check accepted half.
- **Proposed change:** accept or decline the agent layer's proposed areas (`records/curation/agent/catalogue.md`): 155 high-confidence and 254 low-confidence proposals, and a new area, construct-and-workbook (19 items).
- **Evidence:** a spot check accepted about 8 of 16 proposals. The baseline (`tools/curator.py`) stays unchanged until a person accepts a proposal.
- **Normative:** no.

## D-11 CA-22, chronology checks (L-542)
- **RATIFIED by ESC, 19 November 2026:** the records of APE-045 to APE-047 are confirmed as they stand; the true times cannot be recovered (COR-011).
- **Change, applied:** `tools/timestamp_check.py` in CI. Its rules: format YYYY-MM-DDTHH:MM:SSZ; no time later than the runner's clock plus 300 seconds; acceptance not before disclosure. It found and repaired 12 prose timestamps (COR-010).
- **Decision open:** APE-045 to APE-047 record acceptance 70 minutes before disclosure. The true times cannot be recovered from the record. ESC may supply them or confirm the records as they stand (COR-011).
- **Normative:** no (a check).

## D-12 Core margin
- **RATIFIED by ESC, 19 November 2026:** Rule 39 stays at 900 words; 850 is the working margin.
- **Recommendation (APE-501 section 7):** keep Rule 39 at 900 words, and aim for 830 to 850 words since the last seal. Never compress normative language to reach the number.
- **Now:** 880 words since seq_0185. The next seal resets the count.
- **Decision:** whether to adopt 850 as the working margin.

## D-13 The Meaningful Existence Initiative
- **RATIFIED by ESC, 19 November 2026:** the initiative is opened. The definitions ME-01 to ME-07 stay Companion terminology.
- **Proposed change:** open the initiative (`research/philosophy/MEANINGFUL_EXISTENCE.md`), paired with the Common Mathematical Foundations Project. Projects A (channels and their evidence) and B (habit series with the Temporal Engine) can start now. The case design of project C needs consent, ethics review and family researchers.
- **Also for ESC:** whether any of the definitions ME-01 to ME-07 (Companion 233.4) should enter Core Part 10.5. Until then they stay Companion terminology.
- **Evidence:** H-029 and H-030 (VERIFIED COMPUTATION); the Choice Engine selftest.
- **Normative:** no (level B), unless definitions enter the Core.

## D-14 The Drive archive
- **RATIFIED by ESC, 19 November 2026:** (1) publication of historical builds, one family at a time, marked HISTORICAL, each redacted of the Originator's name before it enters the repository; (2) the build dates are kept in records/prior_art/build_dates.json; (3) and (4) as recommended, to be carried out with the next archive pass.
- **Facts:** a search of the Originator's Google Drive found at least 3,617 items of Ω42 material: 112 version labels from V333 Rev.7 to V336 Rev.2, and 3,575 items read-only through the connector (`docs/ARCHIVE_POLICY.md`; `records/archive/drive_register.json`).
- **Applied (level B):** the originals are not edited. A metadata register with names withheld and no identifiers or links. The concordance (`docs/ARCHIVE_CONCORDANCE.md`). AR-01, which recomputed the archive's arithmetic: 6 of 9 statements hold, so the hypothesis that all hold is REJECTED.
- **For ESC:** (1) whether to publish selected historical builds, marked HISTORICAL, one family at a time; suggested first are V333 Rev.387, V335 Rev.442, V336 Rev.2 and the Philosophical Foundations documents; (2) whether the creation dates of formal builds enter the Prior Art Ledger; (3) whether the predictions P1 to P5 and I1 to I5 of the V336 Companion are registered in the STP register; (4) which navigations and syntheses (class D) to submit to the navigation archive.
- **Normative:** no.

## D-15 The October 2025 public repository
- **RATIFIED by ESC, 19 November 2026:** the migration into the existing public repository, its history kept: the October 2025 state tagged v2025.10-historical and kept under archive/2025-10/, the V335 tree on top. The account of the discovery stays where it already is, in the archive.
- **Facts:** the public repository holds the October 2025 edition: 17 files, one commit, under the Originator's personal account. Its README links to 11 files that do not exist; its validator rejects its own example and accepts an empty input; its simulator draws random lottery numbers; four licences conflict (`docs/PUBLIC_REPO_REVIEW.md`).
- **Recommended:** keep the founding PDFs and the 24-cycle as the historical origin (archive/2025-10/, marked HISTORICAL); replace everything else with the V335 tree in one commit after tagging the old state; remove the lottery framing and the unsourced quotation; enter its statements of results into the Speculation Register.
- **For ESC:** (1) approve the migration; (2) where the project lives (the present address carries the Originator's full name; planned: an organization account); (3) whether the account of the discovery stays public.
- **Normative:** no.

## D-16 The OneDrive archive
- **RATIFIED by ESC, 19 November 2026:** all six items. The token and its file are for the Originator to revoke and delete; the paper is withdrawn here (docs/ONEDRIVE_REVIEW.md); SS-01 is registered before any run; the prior art is credited in PRIOR_ART.md; the OneDrive material is filed under the folder scheme of docs/ARCHIVE_POLICY.md.
- **Facts:** at least 1,310 files and 66 folders of Ω42 and Construct material; 45% share a title with the Google Drive register; the Imports folder duplicates Google Drive; the organized folders are empty (`docs/ONEDRIVE_REVIEW.md`; `records/archive/onedrive_register.json`).
- **Applied (level B):** a metadata register with names withheld; recomputation of the 24-cycle test, the order-702 circulant graph and Cassini's identity (`records/archive/recompute_external.py`).
- **For ESC:** (1) revoke the GitHub token stored in a OneDrive document and delete the file; (2) replace the older Rev.450 exports in OneDrive after ratification; (3) withdraw the circulant-graph paper; (4) whether to register a test of proposal O42-PEP-2026-002 before adopting it; (5) public release by family, first the Construct versions 2 to 12; (6) credit the classical 24-period and the published digital-root pattern in the Prior Art Ledger.
- **Normative:** no.

## D-17 Speculation as a principal engine (CA-31)
- **Facts:** APE-510 proposes that speculation be one of Ω42's principal engines of discovery. Core L-491 already makes the scientific method one optional mode inside Ω42. Companion Part 234, research/philosophy/SPECULATIVE_FOUNDATIONS.md and the Exploration Register (EX-001 to EX-006) apply the proposal at level B.
- **Recommended:** ratify CA-31 as a Core principle beside L-491, with its governing line: never confuse what cannot currently be demonstrated with what cannot legitimately be explored.
- **For ESC:** (1) ratify CA-31 or keep it at level B; (2) where its Core sentence comes from in the Rule 39 word budget.
- **Normative:** yes, once ratified.

## D-18 Question Resolution and Navigation (CA-32)
- **Facts:** Some questions are answered by Ω42's own mathematics and rules; others need navigation beyond the structure; many need both. The website now asks for the approach (automatic by default) and hands the Navigator a prompt that names it.
- **Recommended:** ratify CA-32 as a short Core section, with the classification, routing and reporting detail kept in the Companion (a new Part, from docs/QUESTION_NAVIGATION.md).
- **For ESC:** (1) ratify CA-32 or keep it at level B; (2) its place in the Rule 39 word budget.
- **Normative:** yes, once ratified.

## D-19 Information integrity (CA-33, O42-IIRA-01)
- **Facts:** A proposal to apply Omega42 to AI-generated content, misinformation and disinformation, with six modules, an integrity profile instead of a trust score, five hypotheses and a benchmark design. Claim verification is usable now through the Navigator; whether Omega42's own mathematics adds value is untested.
- **Recommended:** approve the initiative in principle, starting with claim verification and provenance; register H-IIE01 to H-IIE05 under STP before any run; ratify CA-33's requirements in the Core.
- **For ESC:** (1) approve O42-IIRA-01; (2) ratify CA-33 or keep it at level B.
- **Normative:** CA-33 yes, once ratified; the initiative no.
