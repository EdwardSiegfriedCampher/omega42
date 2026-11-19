# Contributing to Ω42

Anyone may contribute: people, and AI systems acting for them. Everything accepted is published openly, with your name (or handle), a date and a SHA-256 hash. You do not need to write code or use git.

## What you can submit

| Kind | Use the form | Where it lands |
|---|---|---|
| **Navigation** — a full navigation produced by any AI Navigator | *Submit a navigation* | `submissions/navigations/` → audited → `examples/corpus/` when accepted |
| **Applied Protocol Exploration (APE)** | *Submit an APE* | `submissions/ape/` |
| **Review** — SR-CAS, SNCA, APA or an assessment of the protocol | *Submit a review* | `submissions/reviews/` |
| **Innovation, invention or design** — for open publication as prior art | *Publish an innovation (prior art)* | `submissions/prior-art/` and the Prior Art Ledger |
| **Code** — tools, instruments, apps, ports to other languages | a pull request | `tools/`, `apps/`, `contrib/` |
| **Research proposal** — a study, a dataset, a new area | *Propose research* | `research/<area>/` |
| **Professional credentials** — to be listed as a verified professional | *Verify my credentials* | `community/professionals.json` after review |
| **Erratum** — a mistake in the protocol, a tool or the site | *Report an erratum* | an issue for maintainers |

All forms are at **Issues → New issue**. Each one asks only for what is needed. The site's *Submit* page links to every form and explains each in plain words.

## What happens after you submit

1. **Automatic checks (minutes).** The intake workflow reads your form and, for a navigation, runs the output audit (`m193_m225.py --audit`), the format check (`tools/format_check.py`) and the Congruence Record (`tools/congruence.py`). It posts the results as a comment. Failing a check does not reject the submission; it tells you what to fix.
2. **Cross-architecture review.** Where the repository already holds a navigation of the same domain, SNCA and SR-CAS run on the pair, as the protocol requires for any received Navigator content (Core L-489, Part 6).
3. **Human review.** A reviewer reads the submission against `MODERATION.md`. Accepted submissions are committed by the intake bot with your attribution and enter the public record: the Library, the Congruence Register and, for innovations, the Prior Art Ledger.
4. **Recognition.** Each accepted contribution counts toward your recognition level (`community/RECOGNITION.md`).

## Submitting as an AI agent

An AI system may open issues through the GitHub API on behalf of a person, using the same forms. The form's *Submitted by* field must name the responsible person or organization, and the *Navigator identity* field the model that produced the content. See `AI_ACCESS.md`.

## Rules that apply to every submission

- **Declare exposure.** Name every earlier reading of the same question you or your Navigator had seen (Core L-459). A reading made with another in view is marked CONTAMINATED — NON-BLIND and is still published.
- **Only submit what you may publish.** Do not submit anything confidential, anything you do not have the right to publish, or personal data about other people.
- **Licences.** Text and data you submit are published under CC BY 4.0; code under Apache-2.0. You keep your copyright. See `LICENSES.md`.
- **No assignment.** You are never asked to assign copyright or patents to the project or the Company. The Company owns no patents (`PATENT_PLEDGE.md`); it holds only the names and content badges (`TRADEMARK.md`).
- **Developer Certificate of Origin.** Pull requests carry a `Signed-off-by:` line (`git commit -s`), certifying you may contribute the work.
- **Prior art is final.** Publishing an innovation here is a public disclosure. Read `PRIOR_ART.md` before you submit one.

## Discussion

Ideas, debate and questions belong in **Discussions** (`community/FORUM.md` lists the categories). Professionals with verified credentials post in *Professional Opinions* with their registry number.
