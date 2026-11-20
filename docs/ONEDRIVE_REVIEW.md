# Review of the OneDrive archive

On 19 November 2026 the Navigator surveyed the Originator's OneDrive through the Microsoft 365 connector, read-only. It looked for material on Ω42 and on the Construct. This page reports what was found, recomputes the arithmetic that could be checked, and recommends how to treat the material. The originals were not changed. File identifiers and links are not recorded, and personal files are counted but not named. The decisions are ESC's (`docs/DECISIONS_PENDING.md` D-16).

## What was surveyed

| Area | Size | Coverage |
|---|---|---|
| Documents | about 6.0 GB, about 4,214 items | The connector lists the first 1,000 items alphabetically (to the letter I). The rest were reached only through search |
| Drive root | 80 files | Listed in full |
| OMEGA 42 BOOKS | 19.9 MB | Listed in full: 4 folders, 108 files |
| Imports | 2.7 GB | An import of the Google Drive already registered (`records/archive/drive_register.json`). Sampled, not listed |
| Desktop | 22.3 GB | Only the Ω42 folder names were found by search |
| Organized folders (Protocol — Current, Protocol — Archive, The Construct, Formal Papers, Public and others) | 0 bytes | Created but empty. Provenance holds two shortcuts |

The register `records/archive/onedrive_register.json` lists 1,310 files and 66 folders, by category and without names. It is a lower bound.

## What the archive holds

| Category | Files | Same title in the Google Drive register |
|---|---|---|
| Construct theory (Construct, RTCM, THQT, Domain 0) | 366 | 113 |
| Other Ω42 material | 346 | 137 |
| Formal and constitutional papers | 147 | 113 |
| Protocol builds (V81 to V335 Rev.440) | 126 | 108 |
| AI essays, answers and transcripts | 110 | 54 |
| Book chapters and appendices | 76 | 9 |
| Construct versions (v2.2 to v12.0) | 33 | 28 |
| Lottery and prediction | 16 | 3 |
| Spreadsheets | 15 | 0 |
| Navigator and referee editions | 11 | 8 |
| Prompts, code | 13 | 5 |
| Personal or unrelated (excluded, not opened) | 51 | 5 |

Of 1,310 files, 583 (45%) share a title with a Google Drive item. The rest are OneDrive only: chiefly the book manuscripts, the 2025 Construct theory drafts, the spreadsheets of the original Excel construct, and 87 untitled drafts. 164 titles name an AI system as author or source. 81 titles announce a proof, derivation, unification or solved problem.

Three dated layers show in the titles:
1. **2020 to 2025, the Construct.** The Excel construct, lottery analysis, and the Construct, RTCM and THQT theories.
2. **Late 2025 to April 2026, the Ω42 Construct and Domain 0.** Construct versions 2 to 12, Domain 0 protocols, and the books.
3. **April to September 2026, the Protocol.** V81 to V335 Rev.440, the formal and constitutional papers, the GIM, Klein, Torus and Linguistic Universe editions, and the Philosophical Foundations.

The OneDrive copies of the V335 Rev.450 Core (375 KB) and Companion (220 KB) are earlier exports. The current build is larger (1.6 MB and 5.8 MB).

## Arithmetic recomputed

`records/archive/recompute_external.py` recomputes what could be checked. It was written after the documents were read, so it is a recomputation and not a registered STP test.

**The 24-cycle arithmetic test (version 2.0).**
- The orbit from (2, 5), its period of 24, its sum of 117, the crown values 3, 9, 6, 6, 9, 3, and the encoding dr(42n) ∈ {3, 6, 9} all hold.
- The antipodal rule holds in its digital-root form. Its plain-sum form, "must always be 9" (section 5.4), fails at position 7, where 9 + 9 = 18.
- The uniqueness of (2, 5) is not a property of the arithmetic. The pairs (2, 5), (5, 8) and (8, 2) share the period and the crown. Only the added conditions (a seed class {1, 2, 5}, the value 5) single out (2, 5).
- The encoding maps every phrase to one of three positions (3, 6 or 9), and positions 6 and 9 carry the same value. A reading therefore carries at most log₂ 3 ≈ 1.58 bits about its phrase. Agreement between AI systems on it shows that they count alike. It does not show that the structure forces the interpretation.

**A golden-ratio circulant graph of order 702.** None of its central statements holds:
- the eigenvalue 6 has multiplicity 27, not 1 (the graph has 27 components);
- φ² is not an eigenvalue;
- the involution n ↦ 351 − n has no fixed points, not six;
- the element 117 has order 6 in Z/702, not 42;
- the offsets are ≡ 0 mod 9, not ±3 or ±6.

The paper says it was submitted to a journal. It should not go forward.

**Cassini's identity.** An early conversation asks how −1 relates to the Fibonacci numbers. Its answer, Cassini's identity, is the law's norm at work: N(F_n, F_{n+1}) = (−1)^{n+1} for every n, checked to n = 30. The origin of the norm in V335 (Companion 233.12 M1) is already in the 2025 material.

**Prior art.** A 2025 note on the 24-repeat of Fibonacci digital roots cites a public web page on the same pattern. The period of the Fibonacci numbers modulo 9 is a classical result (Pisano periods), and the digital-root pattern appears in the published problem literature. The Prior Art Ledger should credit both, and assert priority only for what Ω42 adds.

## Proposal O42-PEP-2026-002 (Structural Spectrum)

This proposal (7 September 2026, against Rev.432) would show companion readings in every output by default. It is not in the V335 build. The step before adopting it is a registered test of whether the companion readings carry information about the domain beyond the canonical anchor. It would be measured across a fixed corpus, as the 1.58-bit limit above suggests. Until then it stays a proposal.

## Recommendations

1. **Security, now.** The Documents folder holds a file whose title says it contains a GitHub personal access token. It was not opened. Revoke that token in GitHub settings, create a new one if needed, and delete the file. Credentials do not belong in documents.
2. **One source of truth.** The repository is canonical; OneDrive and Google Drive are archives. Copy the V335 Rev.450 Core and Companion from the repository over the older OneDrive exports once ESC ratifies them.
3. **Fill the empty folders or remove them.** If kept, file each item by the archive classes A to E (`docs/ARCHIVE_POLICY.md`): Protocol — Current (class A), Protocol — Archive (B), The Construct and Formal Papers (C), Domain Navigations (D), Essays and Introductions (E). Origin — Lottery Data stays private.
4. **Do not import the Imports folder.** It duplicates the Google Drive register.
5. **Public release, one family at a time, marked HISTORICAL.** First candidates: the Construct versions 2 to 12 (the origin of the 24-cycle as a construct), and the Philosophical Foundations documents. The book manuscripts and AI transcripts stay private until ESC reviews them.
6. **Keep private:** lottery material, personal files, letters to named people, the account of the discovery (it names the Originator), and every document announcing a proof or a solved problem that has not passed a registered test.
7. **Withdraw** the circulant-graph paper and correct the antipodal wording in the 24-cycle test. Both are recorded here; the originals are unchanged.
8. **Register before running.** Any statement in the archive that is to enter Ω42 first goes into the STP register with its criterion, as RC-01 and AR-01 did.

## Filing record (20 November 2026)

ESC approved the filing (D-16). The Navigator moved 970 items within OneDrive through the connector. Nothing was deleted, renamed or opened for the move.

| Destination folder | Items |
|---|---|
| The Construct | 371 |
| Essays and Introductions | 165 |
| Formal Papers | 156 |
| To review — Duplicates and untitled drafts (the Imports folder is one item) | 99 |
| Protocol — Archive | 49 |
| Domain Navigations | 33 |
| To review — Unsorted | 29 |
| Meta and licensing | 26 |
| NCF proposals | 20 |
| Provenance | 13 |
| Origin — Lottery Data | 7 |
| Protocol — Current | 2 |

In Google Drive the same scheme now stands under one parent folder, Omega42 Archive (Protocol — Current, Protocol — Archive, The Construct, Formal Papers, Domain Navigations, Essays and Introductions, To review). Seven items were filed there: four protocol builds into Protocol — Archive, a duplicate build into To review, the Construct project folder (with its contents) into The Construct, and the Imports folder into To review. The Drive search index lags behind moves, so the loose files left at the top level are the next pass.

Personal files stayed where they were. The second half of the Documents folder (titles after the letter I) was not in the first listing and is the next filing pass. The file whose title names a GitHub token was neither opened nor moved.
