# Prior Art Ledger

`ledger.jsonl` holds one JSON object per published disclosure, appended by the intake workflow when a disclosure is accepted, never edited afterwards:

`{"id": "PA-2026-0001", "title": "...", "contributor": "...", "area": "...", "disclosed_utc": "...", "accepted_utc": "...", "path": "submissions/prior-art/PA-2026-0001.md", "sha256": "..."}`

`disclosed_utc` is the creation time of the public issue that first carried the disclosure. `tools/prior_art.py --verify` recomputes every hash. See PRIOR_ART.md.
