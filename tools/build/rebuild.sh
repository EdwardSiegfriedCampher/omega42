set -e
cd /home/claude/P && rm -f ../repo/docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx && zip -q -X -r ../repo/docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx '[Content_Types].xml' _rels docProps word
cd /home/claude/C && rm -f ../repo/docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx && zip -q -X -r ../repo/docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx '[Content_Types].xml' _rels docProps word
cd /home/claude/repo
python3 - <<'P'
import re,hashlib
p='records/release_documents_SHA256.txt'; s=open(p).read()
for f in ['docs/Omega42_Core_Specification_V335_Rev450_STABLE.docx','docs/Omega42_Companion_Document_V335_Rev450_STABLE.docx']:
    h=hashlib.sha256(open(f,'rb').read()).hexdigest()
    s=re.sub(r'[0-9a-f]{64}(  '+re.escape(f)+')', h+r'\1', s)
open(p,'w').write(s)
P
