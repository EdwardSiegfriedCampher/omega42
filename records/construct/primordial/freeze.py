#!/usr/bin/env python3
"""freeze.py -- regenerate construct_frozen.json from the Originator's workbook PRIMORDIAL FRACTURE and prove that it is affine.

    python3 records/construct/primordial/freeze.py PATH/TO/PRIMORDIAL_FRACTURE.xlsx

Needs openpyxl. The workbook stays with the Originator (its SHA-256 is printed and frozen in FREEZE_OUTPUT.txt); CI uses the
frozen constants, so it needs neither the workbook nor openpyxl. Steps:
  1. evaluate every formula with xleval.py and compare with the values Excel cached in the file;
  2. read, for the 27 domain sheets (MP and the 26 derived), the constant K of every node cell: cell = Y_j + K, where Y is the
     Y-field (MP!J6:O6) and j the cell's position (its column inside its block);
  3. set the Y-field to random vectors, recompute the whole workbook, and confirm that every node cell moves by exactly the
     change in Y_j -- so K does not depend on Y and the frozen table is the whole Construct;
  4. confirm that the table regenerated here equals construct_frozen.json byte for byte.
"""
import hashlib, json, os, random, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import openpyxl, xleval
from openpyxl.utils import get_column_letter as L

path = sys.argv[1]
print('PRIMORDIAL FRACTURE SHA-256 %s' % hashlib.sha256(open(path, 'rb').read()).hexdigest())
wf = openpyxl.load_workbook(path); wv = openpyxl.load_workbook(path, data_only=True)
B = xleval.Book(wf)
sheets = [w.title for w in wf.worksheets]; DOM = [s for s in sheets if s not in ('REV', 'PRED')]
print('sheets %d: %s' % (len(sheets), ' '.join(sheets)))
cached = {ws.title: {(c.row, c.column): c.value for row in ws.iter_rows() for c in row} for ws in wv.worksheets}
num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool)
ok = bad = 0
for sh in sheets:
    for r in range(11, 40):
        for c in range(9, 42):
            x = B.f[sh].get((r, c))
            if isinstance(x, str) and x.startswith('=') and num(cached[sh].get((r, c))):
                v = B.val(sh, r, c); ok += v is not None and abs(v - cached[sh][(r, c)]) < 1e-9; bad += not (v is not None and abs(v - cached[sh][(r, c)]) < 1e-9)
print('1. formulas of rows 11-39, columns I-AO, all sheets: %d reproduce the cached value, %d do not' % (ok, bad))

BLOCKS = [9, 18, 27, 36]
NODE_ROWS = list(range(12, 22)) + list(range(23, 33))
def table(Bk, Y0):
    out = {'Y0': Y0, 'X0': [Bk.val('MP', 5, c) for c in range(10, 16)], 'domains': {}}
    for sh in DOM:
        f = Bk.f[sh]; d = {'rows': {}}
        for r in NODE_ROWS:
            for bi, c0 in enumerate(BLOCKS):
                lab = f.get((r, c0 - 1)); vals = [Bk.val(sh, r, c0 + j) for j in range(6)]
                if all(num(v) for v in vals):
                    d['rows']['%d.%d' % (r, bi)] = {'label': lab if isinstance(lab, str) else None, 'K': [vals[j] - Y0[j] for j in range(6)]}
        ec = []
        for r in (13, 24):
            for bi, c0 in enumerate(BLOCKS):
                m = re.match(r"=COUNTIF\(\$?([A-Z]+)\$?(\d+):\$?([A-Z]+)\$?(\d+),", f.get((r, c0)) or '')
                if m: ec.append({'row': r, 'block': bi, 'range': [m.group(1), int(m.group(2)), m.group(3), int(m.group(4))], 'cached': [cached[sh].get((r, c0 + j)) for j in range(6)]})
        d['echo'] = ec; d['seed'] = f.get((6, 10)) if sh != 'MP' else 'Y'
        tm = []
        for r in range(34, 61):
            for bi, c0 in enumerate(BLOCKS):
                ms = [re.match(r'=\$?([A-Z]+)\$?(\d+)$', x) if isinstance(x, str) else None for x in (f.get((r, c0 + j)) for j in range(6))]
                if all(ms): tm.append({'row': r, 'block': bi, 'cells': [[m.group(1), int(m.group(2))] for m in ms]})
        d['templates'] = tm; out['domains'][sh] = d
    return out
Y0 = [B.val('MP', 6, c) for c in range(10, 16)]
T0 = table(B, Y0)
print('2. constants read: %d domain sheets x %d node rows of six cells, %d echo counters, %d recorded templates' % (len(T0['domains']), len(T0['domains']['MP']['rows']), sum(len(d['echo']) for d in T0['domains'].values()), sum(len(d['templates']) for d in T0['domains'].values())))
rng = random.Random(42); tests = viol = 0
for t in range(4):
    Y = [rng.randint(-20, 60) for _ in range(6)]; B2 = xleval.Book(wf)
    for j, c in enumerate(range(10, 16)): B2.set('MP', L(c) + '6', Y[j])
    for sh in DOM:
        for r in NODE_ROWS:
            if r in (13, 24): continue
            for bi, c0 in enumerate(BLOCKS):
                for j in range(6):
                    v0, v1 = B.val(sh, r, c0 + j), B2.val(sh, r, c0 + j)
                    if num(v0) and num(v1): tests += 1; viol += abs((v1 - v0) - (Y[j] - Y0[j])) > 1e-9
print('3. %d node cells re-evaluated under 4 random Y-fields: %d move by other than the change in Y_j -- every node cell is Y_j + K' % (tests, viol))
frozen = json.load(open(os.path.join(HERE, 'construct_frozen.json')))
print('4. the table regenerated from the workbook equals construct_frozen.json: %s' % ('YES' if json.dumps(T0, sort_keys=True) == json.dumps(frozen, sort_keys=True) else 'NO'))
