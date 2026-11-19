# Releases of Ω42

The repository is the public source of truth. The Navigator interprets the protocol and the governance process decides what it contains. This document says how a release is made, what it carries and how a Navigator names the release it used.

## 1. Rhythm

| When | What happens |
|---|---|
| Continuous | Intake. Submissions, corrections, questions, examples and proposals arrive through the issue forms (`CONTRIBUTING.md`). |
| Weekly | Curation. The curator baseline and its agent layer sort what arrived (`agents/curator/SPEC.md`). The register, the catalogue and the open findings are refreshed in a pull request. |
| Monthly | Stable release, when there is an approved change to release. Approved changes enter the Core, the Companion, the records and the Navigator pack together, under one release tag. The cadence is a ceiling on how often the stable text changes, not an obligation to change it; experiments wait in DEV. |
| Quarterly | Major review. Architecture, terminology (Ω42-T01), validation standards and governance are read as a whole. |
| As required | Urgent correction. A serious error, a security problem or a misleading normative statement is corrected in a patch release, with its own record. |

Receiving material often does not mean changing the Core often. The Core changes only at a stable or patch release, and only by the levels of §3.

## 2. Version names

The protocol keeps its name, `Omega42 V<major> Rev.<revision> <channel>`, for example `V335 Rev.450 STABLE`.

- **V** (major). A change to the architecture, the fundamental method or the normative principles.
- **Rev** (revision). New instruments, laws, sections, tools or compatible additions. Every stable release that changes the Core or the Companion gets a new Rev.
- **Patch suffix** `-p<n>`. Corrections, clarifications and editorial repairs that change no rule, for example `Rev.450-p1`.
- **Channel.** `STABLE` for an approved release. `DEV` for the development stream on its own branch, where experimental material is worked on without changing the stable text. A Navigator names the channel it read.

The git tag repeats the name in a form git accepts, for example `v335-rev450`. Tags are protected and releases are immutable once published (`SETUP.md`, step 12).

## 3. Change levels

| Level | What it covers | What it needs |
|---|---|---|
| A, editorial | Spelling, formatting, broken references, non-substantive clarification | Prepared and checked by a Navigator or the curator agent. A maintainer approves it, and CI must pass. |
| B, Companion and knowledge | Examples, research notes, extended registers, terminology registers, domain material, records | Source and consistency checks, and human review. |
| C, Core | Normative rules, definitions, the method, validation requirements, the authority of the protocol | Explicit approval by ESC, and after the transfer by the Committee (`GOVERNANCE.md` §5), with a documented rationale in `docs/AMENDMENTS_PENDING.md`. Major changes seek an independent review before release. |

## 4. What every release carries

`tools/release_manifest.py --build` writes `records/releases/manifest.json` from the repository as it stands. CI checks that the manifest matches the repository (`--check`). The release record contains:

1. the version name and channel;
2. the publication date;
3. the change log, which is the amendment register `docs/AMENDMENTS_PENDING.md`, with the levels of §3 (declared on a `Level:` line from CA-19 onward, inferred from the text for earlier entries);
4. the affected sections, named in each amendment;
5. the validation report: the CI result (every step must pass), the Speculation Test Protocol register by status (`records/stp/registry.json`) and the reports of `records/srcas/`;
6. the compatibility statement between the Core and the Companion: the Companion elaborates the Core and never modifies it (Core Part 10.5.1);
7. the checksums (`SHA256SUMS`) and the fixed release tag;
8. the record of human approval: each amendment with its status, RATIFIED by ESC or PENDING ESC;
9. five separate dimensions: integrity, CI compliance, protocol compliance, scientific review and release approval. A release that is technically valid is not thereby correct in content, and passing CI is not scientific review;
10. answers to three questions: is it compatible with the previous release, has a normative rule changed, and does a Navigator or a record need updating;
11. the count of entries in the correction and learning register (`records/corrections/register.json`).

Before a push or a release, a person checks the target repository and branch, reads the full change list, and runs the scan for names, email addresses, access tokens, private paths and unpublished personal material. The full CI then runs on the exact commit. An AI maintainer prepares the change and never authorizes its own publication.

## 5. How a Navigator names its release

A Navigator writes the version in every output (`NAVIGATOR: … * V335 Rev.450 STABLE`). The identity block's CONTEXT EXPOSURE line (Core Part 8.1) states what the Navigator read: the Core, the Companion and which Parts. A Navigator that read only part of the protocol says which part. "Latest" is never a version name. A Navigator that fetched the repository names the release tag, or the commit if it read an untagged state.
