import sys; sys.path.insert(0,'/home/claude'); from dx import Doc
for d in ['P','C']:
    D=Doc('/home/claude/'+d); open(f'/home/claude/work/now_{d}.txt','w').write('\n'.join(f'{i}\t{t}' for i,(a,b,t) in enumerate(D.all())))
