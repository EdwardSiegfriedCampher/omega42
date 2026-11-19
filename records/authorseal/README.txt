records/authorseal/ -- the demonstration of the Author Seal (M374; Companion Part 203).
demo_essay.seal is a three-draft history signed with the PUBLISHED demonstration key bytes(range(32)); the key file and
the private snapshot are not kept. demo_essay.txt is the last draft. CI verifies the chain and the final file and
recomputes the report:
  python3 ../../tools/authorseal.py verify demo_essay.seal --final demo_essay.txt
  python3 ../../tools/authorseal.py report demo_essay.seal | diff - demo_report.txt
