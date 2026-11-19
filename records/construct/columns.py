#!/usr/bin/env python3
"""columns.py -- the vertical columns and the diagonals of the Construct's squares, read exactly from the workbook's frozen constants
(records/construct/primordial/construct_frozen.json; Core MATH-55; Companion Part 111). Obligation 4 of the Construct papers
asks what the vertical nodes are; the workbook seeds no domain from a column, so this record states only what the columns
hold, and section V what the diagonals that do seed domains hold. Every cell is Y_j + K, so a column is one field position j read through the constants K of its rows.
Standard library only.
"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
F = json.load(open(os.path.join(HERE, 'primordial', 'construct_frozen.json')))
MP = F['domains']['MP']['rows']
NAMES = ['first (Negative Lower World)', 'second (Positive Lower World)', 'third (Mixed Higher World)', 'fourth (Reversed Higher World)']
def K(r, b): return [int(round(x)) for x in MP['%d.%d' % (r, b)]['K']]
def square(rows, b): return [K(r, b) for r in rows]          # rows x columns
def col(sq, j): return [sq[r][j] for r in range(6)]
def step(seq):
    """the multiplier m (mod 9) with seq[i+1] = m * seq[i] for every i, if one exists, else the additive step, else None"""
    s = [v % 9 for v in seq]
    for m in range(1, 9):
        if all((m * s[i]) % 9 == s[i + 1] for i in range(len(s) - 1)): return 'x%d' % m
    for a in range(1, 9):
        if all((s[i] + a) % 9 == s[i + 1] for i in range(len(s) - 1)): return '+%d' % a
    return None
FIRST, SECOND = range(14, 20), range(25, 31)
print('I. THE FIRST LAYER (rows 14-19 of each block) [EXACT]')
for b in range(4):
    sq = square(FIRST, b); diag = K(12, b)
    flat = all(len(set(r)) == 1 for r in sq)
    same = all(col(sq, j) == col(sq, 0) for j in range(6))
    print('  %s block: every row constant: %s; every column carries the offsets %s: %s; and these equal its first diagonal (row 12): %s'
          % (NAMES[b], 'YES' if flat else 'NO', col(sq, 0), 'YES' if same else 'NO', 'YES' if col(sq, 0) == diag else 'NO'))
print('  so in the first layer a row moves the whole field by one offset, and a column holds one field number under every offset')
print('II. THE SECOND LAYER (rows 25-30) [EXACT; mod 9]')
def inverse(x, y):
    if x is None or y is None: return False
    if x[0] == 'x' and y[0] == 'x': return (int(x[1:]) * int(y[1:])) % 9 == 1
    if x[0] == '+' and y[0] == '+': return (int(x[1:]) + int(y[1:])) % 9 == 0
    return False
for b in range(4):
    sq = square(SECOND, b)
    halves = [[r for r in sq if r[0] > 0], [r for r in sq if r[0] < 0]]
    parts = []
    for h, name in zip(halves, ('positive', 'negative')):
        if not h: continue
        rs = {step(r) for r in h}; cs = {step([r[j] for r in h]) for j in range(6)}
        rr = rs.pop() if len(rs) == 1 else None; cc = cs.pop() if len(cs) == 1 else None
        parts.append('%s rows: along a row %s, down a column %s, each undoing the other: %s' % (name, rr, cc, 'YES' if inverse(rr, cc) else 'NO'))
    latin_c = all(len(set(col(sq, j))) == 6 for j in range(6)); latin_r = all(len(set(r)) == 6 for r in sq)
    print('  %s block: %s; six different offsets in every row: %s, in every column: %s' % (NAMES[b], '; '.join(parts), 'YES' if latin_r else 'NO', 'YES' if latin_c else 'NO'))
print('  2 x 5 = %d = 1 (mod 9): in the Lower World the rows double and the columns halve, and the two directions are the canonical seeds 2 and 5, each the inverse of the other' % (2 * 5))
print('III. WHAT A COLUMN REACHES (residues mod 9, for any field number y) [EXACT]')
for b in range(4):
    offs = col(square(FIRST, b), 0)
    reach = {}
    for y in range(9):
        rs = sorted({(y + o) % 9 for o in offs}); reach[y] = rs
    own = all(all((r - y) % 3 == 0 for r in reach[y]) for y in range(9)); other = all(all((r - y) % 3 != 0 for r in reach[y]) and len(reach[y]) == 6 for y in range(9))
    print('  %s block: a column reaches %s' % (NAMES[b], 'the six residues of the other two classes mod 3' if other else 'the three residues of its own class mod 3' if own else 'a mixed set'))
print('  so a Lower World column holds every value its number is not, mod 3, and a Higher World column the three values it is, mod 3')
print('IV. THE COUNT [EXACT]')
sets = [frozenset(col(square(FIRST, b), 0)) for b in range(4)]
print('  4 blocks x 6 columns = 24 vertical places; as sets of offsets the four blocks give %d kinds, the fourth repeating the third: %s' % (len(set(sets)), 'YES' if sets[2] == sets[3] else 'NO'))
print('  so 24 vertical places hold %d distinct columns, as 24 horizontal places hold 18 distinct rows' % (len(set(sets)) * 6))
print('V. THE DIAGONALS [EXACT; mod 9]')
def diag(sq): return [sq[i][i] for i in range(6)]
def anti(sq): return [sq[5 - j][j] for j in range(6)]
for b in range(4):
    for name, rows, d1, d2 in (('first', FIRST, 12, 21), ('second', SECOND, 23, 32)):
        sq = square(rows, b); m, a = diag(sq), anti(sq)
        halves = lambda s: [s[:3], s[3:]] if b >= 2 else [s]
        def stp(s):
            parts = halves(s); out = []
            for h in parts:
                st = None; q = [v % 9 for v in h]
                for mm in range(1, 9):
                    if all((mm * q[i]) % 9 == q[i + 1] for i in range(len(q) - 1)): st = 'x%d' % mm; break
                if st is None:
                    for ad in range(0, 9):
                        if all((q[i] + ad) % 9 == q[i + 1] for i in range(len(q) - 1)): st = '+%d' % ad; break
                out.append(st or 'none')
            return '/'.join(out)
        print('  %s block, %s layer: the main diagonal is row %d: %s, stepping %s; the anti-diagonal is row %d: %s, stepping %s'
              % (NAMES[b], name, d1, 'YES' if m == K(d1, b) else 'NO', stp(m), d2, 'YES' if a == K(d2, b) else 'NO', stp(a)))
print('  a diagonal moves along a row and down a column at once, so its step is the two steps combined: in the second layer of the Lower World')
print('  the main diagonal combines x2 with x5 = x%d (stillness: one offset all the way), and the anti-diagonal x2 with x2 = x%d' % ((2 * 5) % 9, (2 * 2) % 9))
def orbit(s):
    o, x = [], s
    while x not in o: o.append(x); x = (x[1], (x[0] + x[1]) % 9)
    return frozenset(o)
V = {'A': orbit((1, 1)), 'C': orbit((2, 5))}; V['B'] = next(orbit(s) for s in [(a, c) for a in range(1, 9) for c in range(1, 9)] if len(orbit(s)) == 24 and orbit(s) not in V.values())
name = {v: k for k, v in V.items()}
for u in (4, 7):
    print('  x%d carries the voices of the family: %s' % (u, ', '.join('%s -> %s' % (k, name[frozenset(((u * a) % 9, (u * c) % 9) for a, c in V[k])]) for k in 'ABC')))
print('  so x4, the step of the anti-diagonal, walks the three voices in turn, and three steps bring each home (4 x 4 x 4 = 64 = 1 mod 9)')
print('VI. EVERY DOMAIN CARRIES THE FOUR DIRECTIONS [EXACT]')
import re
def colidx(s):
    n = 0
    for ch in s: n = n * 26 + ord(ch) - 64
    return n
same = 0
for dname, d in F['domains'].items():
    if dname == 'MP': continue
    m = re.match(r'=MP!([A-Z]+)(\d+)', d['seed']); c, r = colidx(m.group(1)), int(m.group(2))
    b = [i for i, x in enumerate((9, 18, 27, 36)) if x <= c < x + 6][0]
    sk = MP['%d.%d' % (r, b)]['K']
    nodes = [k for k in d['rows'] if int(k.split('.')[0]) not in (13, 24)]          # rows 13 and 24 hold the echo counters, not nodes
    same += all(abs(d['rows'][k]['K'][j] - MP[k]['K'][j] - sk[j]) < 1e-9 for k in nodes for j in range(6))
print('  derived domains whose every node cell is Domain Zero\'s constant plus the shift of their own seed: %d of %d' % (same, len(F['domains']) - 1))
print('  so each of the 27 domains is Domain Zero rebuilt on its own field, and its squares carry, relative to that field, the same rows, columns and diagonals:')
print('  forward along a row, return down a column, stillness on the main diagonal and the turn on the anti-diagonal; the columns seed no domain of their own')
lens = {v: ((len({(v * 2 ** k) % 9 for k in range(6)}), len({(v * 5 ** k) % 9 for k in range(6)})) if v % 3 else (len({(v + 3 * k) % 9 for k in range(3)}), len({(v + 6 * k) % 9 for k in range(3)}))) for v in range(1, 10)}
print('  forward and return paths, by value 1 to 9: %s -- always of one length, since each direction is the inverse of the other' % ', '.join('%d:%d/%d' % (v, a, b) for v, (a, b) in lens.items()))
