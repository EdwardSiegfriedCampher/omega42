"""A small evaluator for the formulas of PRIMORDIAL FRACTURE (references, ranges, + - * /, SUM, AVERAGE, INT, MOD, IF, AND, COUNTIF).
Inputs can be overridden; every other cell is computed from its formula. Unsupported formulas evaluate to None."""
import re, math
from openpyxl.utils import column_index_from_string as CI, get_column_letter as L

TOK = re.compile(r"""('(?:[^']+)'|[A-Za-z0-9_]+)!\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?|\$?([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?""")

class Book:
    def __init__(self, wf):
        self.f = {ws.title: {(c.row, c.column): c.value for row in ws.iter_rows() for c in row if c.value is not None} for ws in wf.worksheets}
        self.over = {}; self.memo = {}; self.code = {}
    def set(self, sheet, ref, value):
        m = re.match(r'([A-Z]+)(\d+)', ref); self.over[(sheet, int(m.group(2)), CI(m.group(1)))] = value; self.memo = {}
    def rng(self, sheet, c1, r1, c2, r2):
        out = []
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1): out.append(self.val(sheet, r, c))
        return out
    def compile(self, sheet, x):
        s = x[1:]
        def rep(m):
            if m.group(2):
                sh = m.group(1).strip("'"); a, b = m.group(2), m.group(3)
                if m.group(4): return '_R(%r,%d,%d,%d,%d)' % (sh, CI(a), int(b), CI(m.group(4)), int(m.group(5)))
                return '_V(%r,%d,%d)' % (sh, int(b), CI(a))
            a, b = m.group(6), m.group(7)
            if m.group(8): return '_R(%r,%d,%d,%d,%d)' % (sheet, CI(a), int(b), CI(m.group(8)), int(m.group(9)))
            return '_V(%r,%d,%d)' % (sheet, int(b), CI(a))
        out, i = [], 0
        strs = re.split(r'("[^"]*")', s)
        for k, part in enumerate(strs):
            if k % 2: out.append(part); continue
            part = TOK.sub(rep, part)
            part = re.sub(r'(?<![<>=!])=(?!=)', '==', part).replace('<>', '!=')
            part = re.sub(r'\bIF\(', '_IF(', part); part = re.sub(r'\bSUM\(', '_SUM(', part); part = re.sub(r'\bAVERAGE\(', '_AVG(', part)
            part = re.sub(r'\bINT\(', '_INT(', part); part = re.sub(r'\bMOD\(', '_MOD(', part); part = re.sub(r'\bAND\(', '_AND(', part)
            part = re.sub(r'\bCOUNTIF\(', '_CIF(', part); part = part.replace('^', '**')
            out.append(part)
        return ''.join(out)
    def val(self, sheet, r, c):
        k = (sheet, r, c)
        if k in self.over: return self.over[k]
        if k in self.memo: return self.memo[k]
        x = self.f.get(sheet, {}).get((r, c))
        if not (isinstance(x, str) and x.startswith('=')):
            self.memo[k] = x; return x
        if k not in self.code: self.code[k] = self.compile(sheet, x)
        self.memo[k] = None
        try: v = eval(self.code[k], {'_V': self.val, '_R': self.rng, '_IF': _IF, '_SUM': _SUM, '_AVG': _AVG, '_INT': _INT, '_MOD': _MOD, '_AND': _AND, '_CIF': _CIF})
        except Exception: v = None
        self.memo[k] = v; return v

def _flat(a):
    for x in a:
        if isinstance(x, list): yield from _flat(x)
        else: yield x
def _num(a): return [x for x in _flat(a) if isinstance(x, (int, float)) and not isinstance(x, bool)]
def _SUM(*a): return sum(_num(a))
def _AVG(*a):
    n = _num(a); return sum(n) / len(n) if n else None
def _INT(x): return math.floor(x) if x is not None else None
def _MOD(a, b): return a - b * math.floor(a / b)
def _IF(c, a, b=False): return a if c else b
def _AND(*a): return all(a)
def _CIF(rng, crit):
    vals = list(_flat(rng if isinstance(rng, list) else [rng]))
    if isinstance(crit, str) and crit[:1] in '<>':
        m = re.match(r'([<>]=?)(.*)', crit); op, t = m.group(1), float(m.group(2))
        f = {'>': lambda v: v > t, '<': lambda v: v < t, '>=': lambda v: v >= t, '<=': lambda v: v <= t}[op]
        return sum(1 for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool) and f(v))
    return sum(1 for v in vals if v == crit and v is not None)
