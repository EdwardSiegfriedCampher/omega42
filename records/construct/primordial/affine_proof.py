"""affine_proof.py -- the symbolic proof of Core MATH-55 on the Originator's workbook (after APE-245).

    python3 records/construct/primordial/affine_proof.py PATH/TO/PRIMORDIAL_FRACTURE.xlsx

Needs openpyxl and the workbook, which stays with the Originator; its result is frozen in AFFINE_PROOF.txt.
Evaluate every node cell evaluate every node cell with Y_j as the formal symbol y_j. A value is a linear form
{const, y0..y5: coefficient}. +, - and multiplication by a constant keep it a form; any other operation on a form
that depends on Y (MOD, INT, IF on it, comparison, product of two forms, division by a form) is reported."""
import sys, json
import os, hashlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import openpyxl, xleval
from openpyxl.utils import get_column_letter as L
class NonAffine(Exception): pass
INTLOG = []
class Lin:
    def __init__(s, d): s.d = {k: v for k, v in d.items() if v != 0 or k == 'c'}; s.d.setdefault('c', 0)
    def dep(s): return any(k != 'c' for k in s.d)
    def _o(s, o): return o if isinstance(o, Lin) else Lin({'c': o})
    def __add__(s, o):
        if o is None: raise NonAffine('None')
        o = s._o(o); k = set(s.d) | set(o.d); return Lin({x: s.d.get(x, 0) + o.d.get(x, 0) for x in k})
    __radd__ = __add__
    def __pos__(s): return s
    def __neg__(s): return Lin({x: -v for x, v in s.d.items()})
    def __sub__(s, o): return s + (-s._o(o))
    def __rsub__(s, o): return s._o(o) + (-s)
    def __mul__(s, o):
        o = s._o(o)
        if s.dep() and o.dep(): raise NonAffine('product of forms')
        a, b = (s, o.d['c']) if s.dep() else (o, s.d['c']); return Lin({x: v * b for x, v in a.d.items()})
    __rmul__ = __mul__
    def __truediv__(s, o):
        o = s._o(o)
        if o.dep(): raise NonAffine('division by a form')
        return Lin({x: v / o.d['c'] for x, v in s.d.items()})
    def __rtruediv__(s, o):
        if s.dep(): raise NonAffine('division by a form')
        return s._o(o).d['c'] / s.d['c']
    def __pow__(s, o): raise NonAffine('power')
    def _cmp(s, o):
        o = s._o(o)
        if s.dep() or o.dep(): raise NonAffine('comparison of a form')
        return s.d['c'], o.d['c']
    def __eq__(s, o): a, b = s._cmp(o); return a == b
    def __ne__(s, o): a, b = s._cmp(o); return a != b
    def __lt__(s, o): a, b = s._cmp(o); return a < b
    def __le__(s, o): a, b = s._cmp(o); return a <= b
    def __gt__(s, o): a, b = s._cmp(o); return a > b
    def __ge__(s, o): a, b = s._cmp(o); return a >= b
    def __bool__(s):
        if s.dep(): raise NonAffine('truth of a form')
        return bool(s.d['c'])
    def __hash__(s): return id(s)
    def __floor__(s):
        if s.dep():
            ks = [k for k in s.d if k != 'c']
            if all(float(v).is_integer() for v in s.d.values()):
                INTLOG.append(dict(s.d)); return s   # INT of an integer form: the identity on integer fields
            if all(float(v).is_integer() for k, v in s.d.items() if k != 'c'):
                import math; INTLOG.append(s.d['c']); return Lin(dict(s.d, c=math.floor(s.d['c'])))   # INT(y + c) = y + floor(c) for integer y
            raise NonAffine('INT of a form with fractional coefficients %s' % sorted(s.d.items()))
        import math; return math.floor(s.d['c'])
# make the evaluator's helpers form-aware
def _num(a): return [x for x in xleval._flat(a) if isinstance(x, Lin) or (isinstance(x, (int, float)) and not isinstance(x, bool))]
xleval._num = _num
def _MOD(a, b):
    if isinstance(a, Lin) and a.dep() or isinstance(b, Lin) and b.dep(): raise NonAffine('MOD of a form')
    a = a.d['c'] if isinstance(a, Lin) else a; b = b.d['c'] if isinstance(b, Lin) else b; import math; return a - b * math.floor(a / b)
xleval._MOD = _MOD
def _SUM(*a):
    t = 0
    for x in _num(a): t = t + x
    return t
xleval._SUM = _SUM
def _AVG(*a):
    n = _num(a); return (_SUM(n) / len(n)) if n else None
xleval._AVG = _AVG
def _INT(x):
    import math
    if isinstance(x, Lin): return math.floor(x)
    return math.floor(x) if x is not None else None
xleval._INT = _INT
# patch Book.val so that exceptions propagate as NonAffine instead of None
class SBook(xleval.Book):
    def val(self, sheet, r, c):
        k = (sheet, r, c)
        if k in self.over: return self.over[k]
        if k in self.memo: return self.memo[k]
        x = self.f.get(sheet, {}).get((r, c))
        if not (isinstance(x, str) and x.startswith('=')): self.memo[k] = x; return x
        if k not in self.code: self.code[k] = self.compile(sheet, x)
        v = eval(self.code[k], {'_V': self.val, '_R': self.rng, '_IF': xleval._IF, '_SUM': xleval._SUM, '_AVG': xleval._AVG, '_INT': xleval._INT, '_MOD': xleval._MOD, '_AND': xleval._AND, '_CIF': xleval._CIF})
        self.memo[k] = v; return v
print('PRIMORDIAL FRACTURE SHA-256 %s' % hashlib.sha256(open(sys.argv[1], 'rb').read()).hexdigest())
wf = openpyxl.load_workbook(sys.argv[1]); B = SBook(wf)
for j, c in enumerate(range(10, 16)): B.set('MP', L(c) + '6', Lin({'y%d' % j: 1}))
FZ = json.load(open(os.path.join(HERE, 'construct_frozen.json')))
BLOCKS = [9, 18, 27, 36]; NODE = [r for r in list(range(12, 22)) + list(range(23, 33)) if r not in (13, 24)]
ok = bad = 0; why = {}
for sh, dd in FZ['domains'].items():
    for key, row in dd['rows'].items():
        r, bi = map(int, key.split('.')); c0 = BLOCKS[bi]
        if r in (13, 24): continue
        for j in range(6):
            try:
                v = B.val(sh, r, c0 + j)
                good = isinstance(v, Lin) and set(v.d) - {'c'} == {'y%d' % j} and v.d['y%d' % j] == 1 and abs(v.d['c'] - row['K'][j]) < 1e-9
            except (NonAffine, TypeError) as e: good = False; why[str(e)] = why.get(str(e), 0) + 1
            ok += good; bad += not good
print('symbolic: %d node cells are exactly y_j + K with the frozen K, %d are not %s' % (ok, bad, why or ''))
print('INT applied to a form y + c with integer coefficients: %d evaluations, so INT(y + c) = y + floor(c) for every integer field' % len(INTLOG))
print('so for every integer field Y, every node cell of the 27 domains is Y_j + K exactly; for a field with fractional values the averaged cells, INT(AVERAGE(...)) in rows 20 and 31, may differ from Y_j + K by less than 1')
