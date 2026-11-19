# Open publication and prior art

Ω42 publishes every accepted innovation, invention, design, method and piece of code openly, with a date and a cryptographic hash. The aim is a public commons: once an idea is published here, anyone may use it, and a later applicant cannot claim it as new.

**This page explains how the commons works. It is not legal advice.** Patent law differs between countries. If you hold or plan to seek a patent, speak to a patent attorney before you submit anything.

## How a disclosure is made public

When an innovation is accepted (form: *Publish an innovation (prior art)*):

1. Its full text, figures and any code are committed to `submissions/prior-art/` under a disclosure ID such as `PA-2026-0001`.
2. The intake bot computes the SHA-256 of the disclosure and appends a line to `records/prior_art/ledger.jsonl`: ID, title, contributor, area, the date of first public submission (the issue's creation time, UTC), the date of acceptance, and the hash.
3. The commit is pushed to the public repository and the disclosure appears on the site's *Prior Art* page, where it can be searched and cited.
4. At each release the repository is archived, and where the Zenodo integration is enabled (`.zenodo.json`) the archive receives a DOI. Mirrors at Software Heritage and the Internet Archive are requested by the release workflow.
5. Optionally, the ledger hash can be anchored with OpenTimestamps; the proof file is stored beside the ledger.

The issue itself is public from the moment it is opened, so the date of disclosure is the issue's creation time, even before review.

## What a good disclosure contains

Patent examiners and courts look for a disclosure that is **public, dated and enabling**: it describes the idea in enough detail that a skilled person could carry it out. The form asks for:

- a title and a one-paragraph summary;
- the problem it solves;
- a full description, with every variant you can think of;
- drawings, diagrams, equations or code where they help;
- how to make and use it;
- the field and the keywords someone searching for it would use.

Vague disclosures ("an Ω42-based method for better batteries") protect little. Specific ones protect much more.

## What you should know before you submit

- **You lose the chance to patent it yourself in most countries.** Many jurisdictions require absolute novelty: once you publish, you can no longer patent the idea. Some (for example the United States) give the inventor a one-year grace period after their own disclosure; most of Europe does not.
- **It may not stop every patent.** Publication is evidence that can be cited against a later application or used to challenge a granted patent. It does not prevent someone from filing, and it does not cover improvements you did not describe.
- **You must have the right to publish it.** Do not disclose an employer's or client's confidential work.
- **It is permanent.** Published disclosures are not withdrawn, except for legal takedowns (`MODERATION.md`).

## Ω42-generated content

Every navigation, APE and review in this repository is also openly published, dated and hashed. When a navigation describes a design or method, the contributor may additionally file it through the prior-art form so that it is indexed as a disclosure.

## The project holds no patents

The Ω42 Company owns no patent rights and never asks contributors to assign any; every idea in the record stays free for anyone to explore and extend (`PATENT_PLEDGE.md`).

## Licence

Disclosures are published under CC BY 4.0 and code under Apache-2.0, whose patent grant means a contributor licenses any of their own patent claims that the contributed code practises (`LICENSES.md`).

## Acknowledged prior art

Ω42 asserts priority only for what it adds. Two results it builds on were public before it (ESC decision D-16, 19 November 2026):

- **The 24-step period.** The Fibonacci numbers repeat modulo 9 with period 24, a case of the Pisano periods studied in classical number theory (D. D. Wall, "Fibonacci series modulo m", *American Mathematical Monthly* 67, 1960).
- **The 24-step pattern of digital roots.** The repeating digital roots of the Fibonacci numbers appear in the published problem literature (*American Mathematical Monthly*, problem 10974) and on public sites such as goldennumber.net.

The creation dates of the formal builds, from the Originator's private archive, are kept in `records/prior_art/build_dates.json` as evidence of when each build existed. The public date of a build is its first commit or release in this repository.
