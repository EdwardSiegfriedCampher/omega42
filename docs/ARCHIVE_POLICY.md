# The Drive archive: how earlier Ω42 material is treated

On 19 November 2026 the Originator's Google Drive was searched for Ω42 material. The search matched "Omega42", "Omega 42" or "Ω42" in titles or text. It was stopped at 3,617 items with more results pending, so every count below is a lower bound. The metadata register is `records/archive/drive_register.json`. It holds no file identifiers or links, and names are withheld. What was learned from the archive is in `docs/ARCHIVE_CONCORDANCE.md`. The decisions that remain open are D-14 in `docs/DECISIONS_PENDING.md`.

## What was found

- 3,542 documents and 75 folders: 2,971 text documents, 347 PDFs, 90 Markdown files, and a few spreadsheets, scripts and web pages.
- Created between May 2025 and September 2026, most heavily in April 2026 (2,285 items) and July to September 2026 (867).
- 112 distinct version labels, from V333 Rev.7 to V336 Rev.2. The archive is in large part the build history of the protocol, one revision per file.
- 3,575 of the 3,617 items are read-only through the connector this session uses.

## Decision 1: the originals are never edited

The archive documents are not updated in place, for four reasons:
1. **They are the dated record of how Ω42 was made.** Their creation and modification times are the evidence of priority that the Prior Art Ledger relies on (M273). Rewriting a build of September 2026 with what was learned in November would destroy that evidence.
2. **Most cannot be edited** through the connector (3,575 of 3,617).
3. **Many are outputs of other AI systems** that were relayed to the Originator. The record freezes such outputs as received (Companion 67.4).
4. **The current understanding has one home:** the Core, the Companion and the records of this repository.

Instead, each document family is read against the current record. What carries forward, what is superseded and what is corrected is written once, in the concordance. Any new value is recomputed there and registered as an STP test (AR-01).

## Decision 2: the classes

| Class | What it holds | Count | Treatment |
|---|---|---|---|
| A. Current | The Core and Companion V335 Rev.450 and the records | (the repository) | Authoritative. Public. |
| B. Formal builds | Earlier protocol builds, editions and Companion documents (V333 to V336) | about 1,295 | Historical. Read against the record in the concordance. A build is published only on ESC's decision, marked HISTORICAL with a pointer to the current release, and after a check for names and private material. |
| C. Explanatory and research | Explanatory documents, foundations, geometry, Construct, physics, consciousness, mathematics | about 735 | Historical. The material that carries forward is already absorbed, or is taken in through the concordance. Selected items may become APE submissions, frozen as received, with a Navigator's notes. |
| D. Navigations and syntheses | Earlier navigations, syntheses, assessments | about 86 | Taken in through the submission forms when the Originator chooses, to join the navigation archive. Otherwise private. |
| E. Drafts, prompts and copies | Prompts, untitled documents, copies | about 132 | Private. Not catalogued by title in public. |
| Personal and biographical | Origin stories, anything naming the Originator or a place of residence | (within C and unsorted) | Private. Never published. |
| Unsorted | Titles the first pass could not place | about 1,294 | Reviewed in batches by the curator agent and a person, then placed in A to E. |

## Decision 3: what goes to GitHub, and what is public

1. **Into the repository now:** the metadata register (counts, classes, formal titles with names withheld) and the concordance. The register does not need the documents themselves. Its value is that the scale and history of the work are visible and checkable.
2. **Onto the public site:** the same register and concordance, as part of the record. A visitor sees that the protocol has a long build history and how it was superseded, without reading 3,500 drafts.
3. **The documents themselves are not published wholesale.** Wholesale publication would turn the archive into a second, contradictory source of authority beside the Core: earlier builds say things the current Core reverses (concordance, items 1 and 4). It would also expose personal material.
4. **Selected documents can be published** as a HISTORICAL release on ESC's decision, one family at a time. Each needs a name check, a read for private material, a banner pointing to the current release, and the concordance entry. Suggested first candidates are the last build of each major line (V333 Rev.387, V335 Rev.442, V336 Rev.2) and the Philosophical Foundations documents. They show the lineage, and the record has already audited them against the current text (First Contact audit, `records/first_contact/audit.txt`).
5. **Dates without documents.** The creation dates of formal builds may enter the Prior Art Ledger as dated entries, with neither a link nor the file.

## How it is kept up

- The register is regenerated from a fresh Drive search whenever the Originator asks. The search runs in a session with Drive access, and identifiers never leave that session.
- New material placed in Drive reaches the record through the submission forms, not by synchronizing the archive.
