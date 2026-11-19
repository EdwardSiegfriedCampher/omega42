records/vault/ -- the example of Ω42-Envelope v1 (Core Part 3.77, M364; Companion Part 199).
research_note.txt.o42 is research_note.txt locked with the PUBLISHED demonstration passphrase
  omega42-demo-passphrase-not-secret
(domain research/notes, k = 3). It is an example, not a secret. CI opens it and compares the result with
research_note.txt byte for byte:
  python3 ../../tools/vault.py decrypt research_note.txt.o42 --password omega42-demo-passphrase-not-secret | diff - research_note.txt
