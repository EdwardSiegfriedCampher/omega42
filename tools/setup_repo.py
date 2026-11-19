#!/usr/bin/env python3
"""setup_repo.py -- points the repository's own links at its GitHub name (SETUP.md).

    python3 tools/setup_repo.py OWNER/REPO
Replaces {{REPO}} in .github/ISSUE_TEMPLATE/config.yml and sets "repo" in site/config.json. The site build does the
same for the site at every build, from $GITHUB_REPOSITORY."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2 or '/' not in sys.argv[1]: print(__doc__); sys.exit(1)
repo = sys.argv[1]
p = os.path.join(ROOT, '.github', 'ISSUE_TEMPLATE', 'config.yml'); s = open(p).read().replace('{{REPO}}', repo); open(p, 'w').write(s)
c = os.path.join(ROOT, 'site', 'config.json'); cfg = json.load(open(c)); cfg['repo'] = repo; json.dump(cfg, open(c, 'w'), indent=2)
o = repo.split('/')[0]
p = os.path.join(ROOT, 'README.md'); s = open(p, encoding='utf-8').read().replace('omega42.github.io/omega42', '%s.github.io/%s' % (o.lower(), repo.split('/')[1])); open(p, 'w', encoding='utf-8').write(s)
p = os.path.join(ROOT, '.github', 'CODEOWNERS'); s = open(p).read().replace('@omega42/', '@%s/' % o); open(p, 'w').write(s)
print('repository links now point at', repo)
