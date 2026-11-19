set -e
cd /home/claude/repo
python3 tools/srp_build.py records/srp/collatz_domain.txt --instruments "M127, M139-M142, M269, M125, M188, M187, M222, M223, M208, M189, M126, M157, M190, M288, M289, M296, M297, M291, M284" > records/srp/collatz_SRP.txt
python3 tools/srp_build.py records/srp/hydrogen_domain.txt --instruments "M127, M139-M142, M269, M125, M188, M187, M222, M223, M208, M189, M126, M157, M190, M288, M289, M296, M297, M284" > records/srp/hydrogen_SRP.txt
python3 - <<'P'
import re,hashlib
p='records/release_record_Rev450.txt'; s=open(p).read()
for f in ['tools/format_check.py']:
    h=hashlib.sha256(open(f,'rb').read()).hexdigest()
    s=re.sub(r'[0-9a-f]{64}(  '+re.escape(f)+')', h+r'\1', s)
open(p,'w').write(s)
P
