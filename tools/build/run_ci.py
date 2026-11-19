import yaml, subprocess, sys, re
wf = yaml.safe_load(open('/home/claude/repo/.github/workflows/omega42-ci.yml'))
steps = [s for j in wf['jobs'].values() for s in j['steps'] if 'run' in s]
bad = 0
for s in steps:
    cmd = s['run']
    if re.search(r'\bpip\b', cmd): cmd = 'true'
    r = subprocess.run(['bash', '--noprofile', '--norc', '-eo', 'pipefail', '-c', cmd], cwd='/home/claude/repo', capture_output=True, text=True, env=dict(__import__('os').environ, GITHUB_WORKSPACE='/home/claude/repo'))
    ok = r.returncode == 0; bad += not ok
    print(('PASS ' if ok else 'FAIL ') + s.get('name', cmd[:60]))
    if not ok: print(r.stdout[-1500:], r.stderr[-1500:])
print('STEPS %d, FAILED %d' % (len(steps), bad))
