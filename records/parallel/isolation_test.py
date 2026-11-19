#!/usr/bin/env python3
# Usage: python3 records/parallel/isolation_test.py <repo root> <empty work dir>   (needs PyYAML; about 2-3 minutes)
"""Run every CI step (a) sequentially in one tree, (b) each in its own fresh copy, all at once; compare outputs and write sets."""
import yaml, subprocess, re, os, shutil, hashlib, time, json, sys
from concurrent.futures import ThreadPoolExecutor
REPO=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else '.'); W=os.path.abspath(sys.argv[2] if len(sys.argv)>2 else '/tmp/omega42_isolation'); os.makedirs(W,exist_ok=True)
wf=yaml.safe_load(open(REPO+'/.github/workflows/omega42-ci.yml'))
steps=[s for j in wf['jobs'].values() for s in j['steps'] if 'run' in s]
def cmd(s): c=s['run']; return 'true' if re.search(r'\bpip\b',c) else c
def snap(root):
    h={}
    for d,_,fs in os.walk(root):
        if '__pycache__' in d: continue
        for f in fs:
            p=os.path.join(d,f); h[os.path.relpath(p,root)]=hashlib.sha256(open(p,'rb').read()).hexdigest()
    return h
def norm(o): return re.sub(r'/[^\s]*?/iso_\d+','<ROOT>',o)
def run(i,root):
    t=time.time(); r=subprocess.run(['bash','--noprofile','--norc','-eo','pipefail','-c',cmd(steps[i])],cwd=root,capture_output=True,text=True)
    return r.returncode, hashlib.sha256(norm(r.stdout+r.stderr).encode()).hexdigest(), time.time()-t
base=snap(REPO)
# sequential, in one copy
seq_root=W+'/seq'; shutil.rmtree(seq_root,ignore_errors=True); shutil.copytree(REPO,seq_root)
t0=time.time(); seq=[run(i,seq_root) for i in range(len(steps))]; T_seq=time.time()-t0
# isolated, concurrent
roots=[]
for i in range(len(steps)):
    r=W+'/iso_%d'%i; shutil.rmtree(r,ignore_errors=True); shutil.copytree(REPO,r); roots.append(r)
t0=time.time()
with ThreadPoolExecutor(max_workers=os.cpu_count()) as ex: par=list(ex.map(lambda i: run(i,roots[i]), range(len(steps))))
T_par=time.time()-t0
writes=[]
for i,r in enumerate(roots):
    s=snap(r); writes.append(sorted(k for k in set(s)|set(base) if s.get(k)!=base.get(k)))
res=[]
for i,s in enumerate(steps):
    res.append(dict(step=i+1,name=s.get('name','')[:70],seq_rc=seq[i][0],par_rc=par[i][0],same_output=seq[i][1]==par[i][1],secs=round(seq[i][2],2),writes=writes[i]))
json.dump(dict(cpus=os.cpu_count(),T_seq=T_seq,T_par=T_par,res=res),open(W+'/isolation.json','w'),indent=1)
print('cpus',os.cpu_count(),'sequential %.1fs parallel %.1fs'%(T_seq,T_par))
for x in res:
    if x['seq_rc'] or x['par_rc'] or not x['same_output'] or x['writes']: print(x)
print('critical path (longest single step) %.1fs'%max(x['secs'] for x in res))
