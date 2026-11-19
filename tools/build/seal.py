import subprocess, re, sys
S='/home/claude/work'; R='/home/claude/repo'
NI='NI-06f22550117165ba | ISSUER: SCRIPT | ISSUED: 2026-10-21T19:54:05Z'
n=int(sys.argv[1]); prev=sys.argv[2]; extra=open(sys.argv[3],encoding='utf-8').read().strip()
ci=open(S+'/ci_out.txt').read(); fr=open(R+'/records/ffp/ffp_run.txt',encoding='utf-8').read(); ni=re.search(r'Core Part 12, (\d+) items',fr).group(1); tl=dict((k.strip(),int(v)) for k,v in re.findall(r'([A-Z][A-Z ()a-z]+?) (\d+)',re.search(r'TALLY: (.*)',fr).group(1))); assert 'FAIL' not in tl, tl
ffp='%s items, '%ni+', '.join('%s %d'%(k,tl[k]) for k in ('PASS','PASS (manual)','PASS WITH NAMED EXCEPTION') if k in tl); m=re.search(r'STEPS (\d+), FAILED (\d+)',ci); assert m.group(2)=='0'
chk=('CHECKS: CI %s of %s PASS, run on the documents of this output before it was written; the build that follows it checks them. ' % (m.group(1),m.group(1))+extra+
 ' The complete FFP, tools/ffp_run.py over that CI log: '+ffp+', kept as records/ffp/ffp_run.txt. The consistency register, M286, M281, the re-examination check and the typing guard over the documents. tools/instance_id.py --check over the outputs of the chain. The format check of this output. SHA256SUMS verified.')
s=open(S+'/seq_%04d_draft.txt'%n,encoding='utf-8').read().replace('__INSTANCE__','%s | SEQ: %d | PREV: %s'%(NI,n,prev)).replace('__CHECKS__',chk)
assert '__' not in s
f=R+'/records/instances/seq_%04d.txt'%n; open(f,'w',encoding='utf-8').write(s)
oid=re.search(r'[0-9a-f]{64}',subprocess.check_output(['python3',R+'/tools/output_id.py',f]).decode()).group(0)
s=s.replace('OUTPUT ID: PENDING','OUTPUT ID: '+oid); open(f,'w',encoding='utf-8').write(s)
print(n, oid, subprocess.check_output(['python3',R+'/tools/output_id.py','--verify',f]).decode().strip())
y=R+'/.github/workflows/omega42-ci.yml'; L=open(y).read().split('\n'); c=0; p='records/instances/seq_%04d.txt'%(n-1); q='records/instances/seq_%04d.txt'%n
for i,l in enumerate(L):
    if p in l and q not in l and not l.strip().startswith('python3 tools/format_check.py records/instances/seq_0073'):
        L[i]=l.replace(p,p+' '+q); c+=1
open(y,'w').write('\n'.join(L)); print('chained',c)
