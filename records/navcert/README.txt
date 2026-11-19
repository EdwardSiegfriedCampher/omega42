records/navcert/ -- the Navigator's self-assessment (M370; Companion Part 201).
Signed with the PUBLISHED demonstration key bytes(range(32)); a demonstration, not a credential.
As a self-assessment it is capped at level 1 (Registered, self-assessed). CI verifies the signature:
  python3 ../../tools/navcert.py verify navigator_self_assessment.json
