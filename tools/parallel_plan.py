#!/usr/bin/env python3
"""M300 Parallel Execution Plan (Core L-485, Part 3.33).

Omega42 work is a directed acyclic graph of tasks. An edge u -> v means v may not start until u is done,
for one of three reasons:
  DATA     v reads what u produces (the anchor needs the counts);
  SEAL     v needs nothing from u but must follow it so that u cannot be shaped by v
           (a reading is sealed before the mapping is computed; a freeze precedes its computation);
  ADAPT    v was designed in the light of u's result (a later pilot frozen after an earlier one).
Two tasks may run in parallel exactly when neither reaches the other. Some tasks must also be ISOLATED:
they run in separate contexts (fresh sessions, different makers), because their worth is that they
are independent; running them side by side in one context gives concurrency, not independence.

Checks:
  acyclic; every reading is sealed before any mapping; no path from a mapping or correspondence task
  into the reading chain (L-484 E, the truth architecture's 'alongside, never above'); every computation
  follows its freeze; a correspondence batch is declared, all candidates at once, before any is computed,
  and its ledger waits for every candidate (L-484 C); isolated groups are marked.

Usage:
  python3 tools/parallel_plan.py --selftest        checks, a leak control, and a concurrent recomputation
  python3 tools/parallel_plan.py --schedule        the canonical example plan, as parallel waves
Standard library only.
"""
import sys, os, subprocess
from concurrent.futures import ThreadPoolExecutor

class Plan:
    def __init__(self):
        self.kind, self.edges, self.isolated = {}, [], {}
    def task(self, name, kind, isolated=None):
        self.kind[name] = kind
        if isolated: self.isolated.setdefault(isolated, []).append(name)
        return name
    def dep(self, u, v, why):
        assert u in self.kind and v in self.kind, (u, v)
        assert why in ('DATA', 'SEAL', 'ADAPT')
        self.edges.append((u, v, why))
    def succ(self):
        s = {k: [] for k in self.kind}
        for u, v, _ in self.edges: s[u].append(v)
        return s
    def reach(self, u):
        s, seen, st = self.succ(), set(), [u]
        while st:
            x = st.pop()
            for y in s[x]:
                if y not in seen: seen.add(y); st.append(y)
        return seen
    def waves(self):
        """Kahn levels in canonical (sorted) order: wave k holds every task whose predecessors are all in waves < k."""
        indeg = {k: 0 for k in self.kind}
        for _, v, _ in self.edges: indeg[v] += 1
        s, out, cur = self.succ(), [], sorted(k for k in self.kind if indeg[k] == 0)
        done = 0
        while cur:
            out.append(cur); done += len(cur); nxt = []
            for u in cur:
                for v in s[u]:
                    indeg[v] -= 1
                    if indeg[v] == 0: nxt.append(v)
            cur = sorted(nxt)
        if done != len(self.kind): raise ValueError('CYCLE')
        return out
    def check(self):
        errs = []
        try: self.waves()
        except ValueError: return ['plan has a cycle']
        R = {k: self.reach(k) for k in self.kind}
        reading_chain = [k for k, t in self.kind.items() if t in ('reading', 'seal')]
        for k, t in self.kind.items():
            if t in ('mapping', 'correspondence', 'ledger'):
                hit = [r for r in reading_chain if r in R[k]]
                if hit: errs.append('firewall: %s reaches the reading chain at %s' % (k, hit[0]))
            if t == 'mapping':
                seals = [s for s in self.kind if self.kind[s] == 'seal' and k in R[s]]
                if not seals: errs.append('mapping %s is not preceded by a sealed reading' % k)
            if t in ('compute', 'correspondence'):
                fr = [f for f in self.kind if self.kind[f] == 'freeze' and k in R[f]]
                if not fr: errs.append('%s %s is not preceded by a freeze' % (t, k))
            if t == 'ledger':
                cands = [c for c in self.kind if self.kind[c] == 'correspondence' and c.split(':')[0] == k.split(':')[0]]
                miss = [c for c in cands if k not in R[c]]
                if miss: errs.append('ledger %s does not wait for %s' % (k, miss[0]))
        for g, names in self.isolated.items():
            for a in names:
                for b in names:
                    if a != b and b in R[a]: errs.append('isolated group %s: %s reaches %s' % (g, a, b))
        return errs

def example():
    """Domains d1-d3 navigated; an object o1 mapped beside d1; a correspondence batch of four candidates;
    three Navigators reproducing d1; two blind replies; two pre-registered pilots frozen together."""
    P = Plan(); t = P.task; e = P.dep
    t('MATH-GATE', 'ground'); t('FRAME-LOCK', 'ground'); e('MATH-GATE', 'FRAME-LOCK', 'DATA')
    for d in ('d1', 'd2', 'd3'):
        t(d + ':substrate', 'lock'); e('FRAME-LOCK', d + ':substrate', 'DATA')
        for n in ('n1', 'n2', 'n3'):
            t(d + ':' + n, 'count'); e(d + ':substrate', d + ':' + n, 'DATA')
        t(d + ':anchor', 'arith')
        for n in ('n1', 'n2', 'n3'): e(d + ':' + n, d + ':anchor', 'DATA')
        for a in ('yang', 'yin', '4d', 'antipode'):
            t(d + ':arm-' + a, 'arith'); e(d + ':anchor', d + ':arm-' + a, 'DATA')
        t(d + ':reading', 'reading')
        for a in ('yang', 'yin', '4d', 'antipode'): e(d + ':arm-' + a, d + ':reading', 'DATA')
        t(d + ':seal', 'seal'); e(d + ':reading', d + ':seal', 'DATA')
        for g in ('jargon-answer', 'jargon-essay'):
            t(d + ':' + g, 'gate'); e(d + ':seal', d + ':' + g, 'DATA')
        t(d + ':M224', 'gate'); e(d + ':jargon-answer', d + ':M224', 'DATA'); e(d + ':jargon-essay', d + ':M224', 'DATA')
    # mapping beside d1: object and measurement fixed when asked; computed only after the seal
    t('o1:measure-freeze', 'freeze'); t('o1:mapping', 'mapping'); t('d1+o1:join', 'join')
    e('o1:measure-freeze', 'o1:mapping', 'DATA'); e('d1:seal', 'o1:mapping', 'SEAL')
    e('o1:mapping', 'd1+o1:join', 'DATA'); e('d1:M224', 'd1+o1:join', 'DATA')
    # correspondence batch B: one freeze declares the screen, the universe and all candidates
    t('B:freeze', 'freeze'); t('B:ledger', 'ledger')
    for k in ('k1', 'k2', 'k3', 'k4'):
        t('B:C11-' + k, 'correspondence'); e('B:freeze', 'B:C11-' + k, 'DATA')
        t('B:C1-10-' + k, 'correspondence'); e('B:C11-' + k, 'B:C1-10-' + k, 'DATA')
        e('B:C1-10-' + k, 'B:ledger', 'DATA')
    # reproducibility: the same frozen domain, three Navigators in fresh sessions (isolated)
    for j in ('nav-A', 'nav-B', 'nav-C'):
        t('d1@' + j, 'reading', isolated='SR-CAS'); e('FRAME-LOCK', 'd1@' + j, 'DATA')
    t('SR-CAS', 'compare')
    for j in ('nav-A', 'nav-B', 'nav-C'): e('d1@' + j, 'SR-CAS', 'DATA')
    # blind test: brief, key and scoring rule sealed first; replies isolated; each checked independently
    t('BT:seal', 'freeze')
    for f in ('family-1', 'family-2'):
        t('BT:reply-' + f, 'reply', isolated='S7'); e('BT:seal', 'BT:reply-' + f, 'SEAL')
        t('BT:check-' + f, 'compute'); e('BT:reply-' + f, 'BT:check-' + f, 'DATA')
    t('BT:verdict', 'compare'); e('BT:check-family-1', 'BT:verdict', 'DATA'); e('BT:check-family-2', 'BT:verdict', 'DATA')
    # two pilots frozen together run together; a pilot designed from a result waits for it
    for p in ('pA', 'pB'):
        t(p + ':freeze', 'freeze'); t(p + ':compute', 'compute'); e(p + ':freeze', p + ':compute', 'SEAL')
    t('pC:freeze', 'freeze'); t('pC:compute', 'compute'); e('pC:freeze', 'pC:compute', 'SEAL')
    e('pA:compute', 'pC:freeze', 'ADAPT')
    return P

def schedule(P):
    W = P.waves()
    for i, w in enumerate(W): print('wave %2d (%d in parallel): %s' % (i + 1, len(w), ', '.join(w)))
    print('tasks %d | waves %d | widest wave %d | isolated groups %s' % (len(P.kind), len(W), max(len(w) for w in W),
          {g: len(v) for g, v in P.isolated.items()}))
    return W

def concurrent_recompute(root):
    """Recompute the four physical pilots concurrently and compare each with its recorded output."""
    dirs = ['records/pilot_0%d' % i for i in (1, 2, 3, 4)]
    def one(d):
        r = subprocess.run([sys.executable, 'compute.py'], cwd=os.path.join(root, d), capture_output=True, text=True)
        return r.stdout == open(os.path.join(root, d, 'compute_output.txt')).read()
    with ThreadPoolExecutor(max_workers=4) as ex: res = list(ex.map(one, dirs))
    return dict(zip(dirs, res))

def selftest():
    ok = True
    P = example(); errs = P.check(); W = P.waves()
    print('example plan: %d tasks, %d waves, widest %d, checks %s' % (len(P.kind), len(W), max(len(w) for w in W), errs or 'CLEAN'))
    ok &= not errs and len(W) == 11
    # leak controls: each must be caught
    controls = {
        'mapping feeds the reading': lambda Q: Q.dep('o1:mapping', 'd1:reading', 'DATA'),
        'mapping before the seal': lambda Q: Q.edges.remove(('d1:seal', 'o1:mapping', 'SEAL')),
        'correspondence feeds a reading': lambda Q: Q.dep('B:ledger', 'd2:reading', 'DATA'),
        'ledger before a candidate': lambda Q: Q.edges.remove(('B:C1-10-k4', 'B:ledger', 'DATA')),
        'isolated replies linked': lambda Q: Q.dep('BT:reply-family-1', 'BT:reply-family-2', 'DATA'),
        'compute without freeze': lambda Q: Q.edges.remove(('pB:freeze', 'pB:compute', 'SEAL')),
        'cycle': lambda Q: Q.dep('d3:seal', 'd3:substrate', 'DATA'),
    }
    for name, f in controls.items():
        Q = example(); f(Q); caught = bool(Q.check())
        print('  control %-32s %s' % (name, 'CAUGHT' if caught else 'MISSED')); ok &= caught
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    rc = concurrent_recompute(root)
    print('concurrent recomputation of pilots 01-04 equals the records: %s' % rc); ok &= all(rc.values())
    print('PARALLEL PLAN SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok

if __name__ == '__main__':
    if '--schedule' in sys.argv: P = example(); schedule(P); print('checks:', P.check() or 'CLEAN')
    else: sys.exit(0 if selftest() else 1)
