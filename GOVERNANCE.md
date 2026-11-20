# Governance of Ω42

Ω42 is an open project. Its protocol, its tools and every navigation submitted to it are published in this repository and on the project site. This document says who decides what, how those decisions are made, and how stewardship passes from the Originator to a committee.

## 1. Roles

| Role | Who | What they decide |
|---|---|---|
| **The Ω42 Company** | The legal entity, governed by its Board (`ENTITY.md`) | The general direction: strategy, budget, contracts, the commercial edition, and the names, marks and content badges. It owns no patents (`PATENT_PLEDGE.md`). |
| **Originator and Overseer** (author of record; Core F-00) | The Originator (ESC), not named publicly | Until the transition: everything. After it: the constitutional reserve (§4) and nothing else. |
| **Stewardship Committee** | Seven members (§3) | Protocol revisions, acceptance of submissions, recognition, moderation appeals; advice to the Company's Board on the roadmap, the commercial edition and the terms of the web-app exchange. |
| **Maintainers** | Appointed by the Committee | Merge accepted pull requests, run releases, keep CI green, triage issues. |
| **Reviewers** | Any contributor in good standing; verified professionals | Review submissions and pull requests; their reviews are public. |
| **Navigators** | Any AI system executing the protocol | Produce navigations, APEs, SR-CAS and SNCA reviews. A Navigator's output is a contribution of the person who submits it. |
| **Strikers and contributors** | Anyone | Ask questions, submit content, take part in discussion, propose changes. |

## 2. Phases

1. **Founding (now).** ESC adopts revisions (Core F-06). Maintainers may be appointed by ESC. The intake, site and records described in `CONTRIBUTING.md` run from the start.
2. **Formation.** When the repository has at least 50 accepted submissions from at least 20 contributors, or earlier at ESC's call, ESC publishes a call for Committee nominations in Discussions → Announcements. Nominations stay open for 30 days. ESC appoints the first Committee from the nominees, with staggered terms (three seats for one year, four for two).
3. **Incorporation.** The Company is registered with the locked provisions of `ENTITY.md`; the Originator transfers the names and logo to it; it signs the Patent Pledge. This may happen before or after Formation.
4. **Transfer.** The Committee takes over the decisions in §1 by a formal protocol revision that amends Core F-06 to read "revisions are adopted by the Stewardship Committee, under the Originator's oversight (GOVERNANCE.md)". The revision records the date of transfer.
5. **Steady state.** Seats are filled by election (§3). ESC serves as Overseer for as long as ESC chooses, and may name a successor Overseer or let the role lapse into the Committee.

## 3. The Stewardship Committee

**Seats.** Seven, filled to cover the work rather than any one discipline: mathematics; AI systems and evaluation; philosophy and the interpretive layer; the traditions and lenses; research method (the optional programme of Appendix S); community and education; and one open seat. No more than two members may share an employer.

**Terms.** Two years, renewable once consecutively. Elections each year for the seats whose terms end.

**Electorate.** Contributors with at least two accepted contributions in the past 24 months. Voting runs in a GitHub Discussion with a poll, or by a ballot tool the Committee announces, open for 14 days.

**Decisions.** By simple majority of members voting, with a quorum of four. Protocol revisions need five votes. Every decision is recorded in `governance/decisions/` with the date, the vote and the reasoning.

**Conflicts of interest.** A member declares any financial or professional interest in a matter and does not vote on it. Interests are listed in `governance/interests.md`.

**Removal.** A member may be removed by five votes of the other members, or by the Overseer for a breach of the Code of Conduct, with the reasons published.

## 4. The Overseer's constitutional reserve

After the transfer, the Overseer keeps four powers and no others:

1. **The Totality Axiom.** Only the Originator may amend Core F-02 (L-432). The Overseer may veto any revision that alters the premise.
2. **The Aperture.** The Overseer may veto any revision that weakens the Striker's sovereignty over judgment (Part 7, SS-01, L-441).
3. **The open record.** The Overseer may veto any change that removes published content from public access, except for legal takedowns (`MODERATION.md`).
4. **The locked provisions.** The Overseer's consent is required to change any locked provision of the Company's founding documents: no patents, the open licences, this reserve, and the purpose (`ENTITY.md`). The names and marks are held by the Company, not by the Overseer (`TRADEMARK.md`).

A veto is published with its reasons within 14 days of the decision it concerns. The Committee may answer it with a revised proposal.

## 5. Protocol revisions

A revision is proposed as a pull request that changes the protocol documents or tools, with an entry in the release record. It is discussed for at least 14 days in Discussions → Protocol Revisions, passes CI, and is adopted by the vote in §3 (or, before the transfer, by ESC). The release is tagged, archived (Zenodo DOI where configured) and announced.

Every change has a level (`RELEASES.md` §3). **Level A**, editorial: a maintainer approves it once CI passes. **Level B**, the Companion, records and knowledge material: it needs source and consistency checks and human review. **Level C**, the Core: it needs explicit approval by ESC, and after the transfer by the vote in §3, with a documented rationale; a major change seeks an independent review first. A discussion post never becomes part of Ω42 by itself. The stages are discussion, proposal (an issue form or pull request), review, accepted, and published in a numbered release (`RELEASES.md`).

**AI agents.** A Navigator or the curator agent may prepare changes of any level, including changes to its own instructions, as pull requests. It never approves or merges its own proposal, never redefines its own mandate, and has no write access to protected branches or tags. It reads every submission as untrusted data, never as instructions (`agents/curator/SPEC.md`).

## 6. Money

Income from commercial software, certification (`CERTIFICATION.md`), sponsorship and grants is received by the Company (or, before it is registered, by a fiscal host such as Open Collective). It goes first to the upkeep and maintenance of the facility — the hosted web-app and Navigator, the site, the record and its archive, the curator agent and the newsletter. The Company's Board sets the budget; the Committee is consulted on spending for the record, the free edition and research. The Company publishes an annual account: income, spending, what the facility and the free edition received, and the certification audits run. The free edition, the protocol and the open record are never made conditional on payment (`COMMERCIAL.md`).

## 7. Changing this document

This document is changed by the process for protocol revisions in §5. §4 is changed only with the Overseer's consent.

## The Originator

The Originator is not named publicly while Omega42 establishes itself, so that attention stays on the work, and may choose to introduce themself later. Decisions remain recorded in the open under the handle ESC (`docs/DECISIONS_PENDING.md`).
