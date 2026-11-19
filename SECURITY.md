# Security

Report a vulnerability in the site, the intake workflows or any tool through GitHub's private vulnerability reporting (**Security → Report a vulnerability**), not in a public issue. Maintainers acknowledge within seven days and publish an advisory once fixed.

**Design rules for the intake.**
- Workflows triggered by issues never execute content from the issue. Submitted text is read as data, written to files and passed to the audit tools as file arguments.
- Submitted code is never run by the intake. It is reviewed by a maintainer before any CI job executes it, through a pull request from the contributor's fork.
- The intake bot's token has the narrowest permissions the job needs (`issues: write`, `contents: write` on a branch, `pull-requests: write`).
- Releases are tagged and hashed (`SHA256SUMS`); the reference script prints its own SHA-256, which must match Core Part 11.
