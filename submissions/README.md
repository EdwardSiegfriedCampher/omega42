# Submissions

Place a navigation here as a plain-text file (`*.txt`), in the canonical skeleton of Core Part 8.0, ending with the Navigator Signature.

On every push and pull request, CI runs the output audit (L-457) on each file in this folder against the known corpus:

```
python3 scripts/m193_m225.py scripts/canonical_reference.py --audit submissions/FILE.txt --corpus examples/corpus
```

A submission that fails the audit fails the build. Declare every reading of the same question you had seen under CONTEXT EXPOSURE (L-459). Accepted navigations join `examples/corpus/`; acceptance is by the Originator (F-06).
