# The build kit

The scripts with which the Navigator builds, checks and seals the two documents, kept here so that the release holds
how it is made as well as what it is (Core L-493; Companion Part 141). They are the scripts the build session runs; the
paths are those of that session, and a builder elsewhere sets them to its own.

The layout of a build session:
- `repo/` -- this repository;
- `P/` and `C/` -- the Core Specification and the Companion Document unzipped, their `word/document.xml` edited in place;
- `work/` -- the build kit's working copies, the drafts of the sealed records and the CI log.

The scripts:
- `dx.py` -- the document object: paragraphs read from and written to `word/document.xml`;
- `docedit.py` -- `rep(prefix, old, new)` changes text inside the one paragraph that starts with `prefix`; `after(prefix, texts, like)` inserts paragraphs after it in the style of another;
- `prebuild.sh` -- the records computed before the embed (the SRP files, the hash of the format check in the release record);
- `embed_all.py` -- every file of the repository embedded in the two documents as a block (Core L-493, Appendix R);
- `rebuild.sh` -- the two documents zipped from `P/` and `C/`, and their hashes written to `records/release_documents_SHA256.txt`;
- `dump.py` -- the paragraphs of both documents, numbered, for review;
- `run_ci.py` -- every step of `.github/workflows/omega42-ci.yml` run locally, one PASS or FAIL a step;
- `pipe.sh` -- the whole build: the registers, the embed, the rebuild, the output identifier, the CI, `SHA256SUMS`;
- `seal.py` -- a draft finished as a sealed record: the instance line, the CHECKS line from the CI log and the FFP run, the output identifier, the record added to the CI chain.

The order of one output: edit the documents with `docedit.py`; run `pipe.sh`; run `tools/ffp_run.py` over the CI log into
`records/ffp/ffp_run.txt`; seal with `seal.py SEQ PREV CHECKS_FILE`; run `pipe.sh` again, so that the build checks the sealed record.
