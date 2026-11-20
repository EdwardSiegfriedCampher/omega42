set -e
cd /home/claude/repo; S=/home/claude/work   # S: the work folder holding the build kit (tools/build/) and its outputs
python3 tools/consciousness.py --baseline > records/consciousness/CT-S7_baseline.txt
python3 tools/ape_register.py > records/ape/findings.txt
python3 tools/release_manifest.py --build > /dev/null
bash $S/prebuild.sh; python3 $S/dump.py >/dev/null; python3 $S/embed_all.py | tail -1; bash $S/rebuild.sh
python3 tools/core_sample.py > /tmp/s.txt
if ! python3 tools/output_id.py --verify /tmp/s.txt | grep -q VERIFIED; then
  OLD=$(grep -o "OUTPUT ID: [0-9a-f]*" /tmp/s.txt | cut -d' ' -f3); NEW=$(python3 tools/output_id.py /tmp/s.txt | grep -o "[0-9a-f]\{64\}")
  python3 - $OLD $NEW <<'P'
import sys; sys.path.insert(0,'/home/claude')
from dx import Doc, psub_main as ps
P=Doc('/home/claude/P'); ps(P,"OUTPUT ID: "+sys.argv[1],"OUTPUT ID: "+sys.argv[2]); P.save()
P
  bash $S/rebuild.sh; python3 tools/core_sample.py > /tmp/s.txt
fi
python3 tools/output_id.py --verify /tmp/s.txt
python3 tools/ai_edition.py --build > /dev/null   # the AI reading editions, rendered from the final documents (Companion Part 142)
python3 $S/dump.py >/dev/null
set +e
python3 $S/run_ci.py > $S/ci_out.txt 2>&1; grep "^FAIL\|STEPS" $S/ci_out.txt
find . -type f ! -name SHA256SUMS ! -path './.git/*' ! -path '*/__pycache__/*' | sed 's|^\./||' | LC_ALL=C sort | xargs -d '\n' sha256sum > SHA256SUMS && sha256sum -c SHA256SUMS --quiet && echo SUMS OK
cp docs/*.docx $S/
