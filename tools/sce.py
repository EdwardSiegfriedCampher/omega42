#!/usr/bin/env python3
"""sce.py -- M345 External-Theory Correspondence (Core Part 3.71, L-510, L-553): classify a proposed match between an Ω42
structure and a structure of an external theory, by the depth framework (Core Part 0.14.5), so a count-match is never
mistaken for a correspondence.

A claim is placed in one class, with the depth it earns and, for a count-match, the share of random small counts that would
match as well (the base rate):
  NATIVE COUNT (depth 1): a count forced within Ω42 (MF-44: inert at 3, first-lift valuation 1) set beside an
                         outside count; necessary on the Ω42 side, the bridge to the outside structure not yet derived.
  NUMERICAL RESONANCE  (depth 2): the count is one of the cycle's declared values, or a natural one-to-one cyclic order.
  PARTIAL STRUCTURAL   (depth 3): a shared declared feature, or an intrinsic map conjugate to T carrying such a feature.
  FULL STRUCTURAL      (depth 4): a generative correspondence f with f . S = T . f on the canonical orbit, value structure carried.
  PREDICTIVE           (depth 5): the correspondence foresaw a property later observed.
  DERIVED              : an exact arithmetic fact of Ω42 itself (not a correspondence with an outside theory).
  SPECULATION          : no map is derived; recorded as an open direction (Appendix S), never as achieved.
Physical correspondence is never settled here; it is a question of the Scientific Appendix (L-553). The classifier reports
what the match IS, not whether the physics is true.

    python3 tools/sce.py [--domain physics|cosmology|energy|spacetime|all]
    python3 tools/sce.py --selftest
Standard library only.
"""
import sys

# each claim: (domain, name, class, depth, base_rate, note). base_rate None unless it is a count-match.
CLAIMS = [
    ('physics', 'A induces a Lorentz transformation in SO+(3,1); iA in SL(2,C)', 'DERIVED', None, None,
     'exact arithmetic (tools/lorentz.py); a representation of A, not a derivation of physics'),
    ('physics', 'three 24-cycles <-> three fermion generations', 'NATIVE COUNT', 1, '3 = the norm classes of units mod 9 (MF-44)',
     'equal counts only; no gauge representation carried, so a fourth generation is not "forbidden" by physics here'),
    ('physics', 'the 8-cycle <-> eight gluons of SU(3)', 'NATIVE COUNT', 1, '8 = |F_9^x|, the residue order (MF-44)',
     'equal counts only; the 8-cycle carries no SU(3) adjoint structure'),
    ('physics', 'the fixed point <-> the Higgs condensate', 'NATIVE COUNT', 1, 'one fixed point, one vacuum',
     'a single-element match; no potential, vacuum value or mass term derived'),
    ('physics', 'the Yin arm <-> weak-force parity violation; T^12 <-> CP', 'SPECULATION', 2, None,
     'a structural analogy of an asymmetry; charge conjugation is not additive inversion'),
    ('cosmology', 'the 3-adic depth tower <-> the hierarchy of cosmic scales', 'SPECULATION', 2, None,
     'a scaling analogy (period x9 per level); periods are not physical length scales without a derived map'),
    ('cosmology', 'finite-level periodicity vs no nonzero periodic point in the inverse limit', 'DERIVED', None, None,
     'exact: T^(24*9^(k-1))=I at depth k, and the inverse limit has no nonzero periodic point (MATH-36)'),
    ('cosmology', 'the five orbit sectors <-> matter / dark matter / dark energy', 'NATIVE COUNT', 1, 'few sectors, few components',
     'a partition match; no stress-energy, coupling or equation of state derived'),
    ('cosmology', 'a depth-dependent vacuum term <-> evolving dark energy', 'SPECULATION', 2, None,
     'a candidate parametrisation; requires a derived coupling to gravity (Appendix S)'),
    ('energy', 'the 24-cycle organises coupled resonators for ambient-energy harvesting', 'SPECULATION', 2, None,
     'a control-architecture analogy; E_out <= E_in always, conservation intact'),
    ('energy', 'over-unity / Zero-Layer extraction / retrocausal entropy cancellation', 'REJECTED', None, None,
     'violates conservation and the second law; no energy source follows from the arithmetic (CERT-0008 line of reasoning)'),
    ('spacetime', 'the Lorentz representation constrains any coordinate-connection model', 'DERIVED', None, None,
     'the SO+(3,1) action is exact; it does not supply a metric or a wormhole solution'),
    ('spacetime', 'coordinate connection as admissible state correspondence', 'SPECULATION', 2, None,
     'a mathematical relation between states; no coordinate-to-geometry law is derived'),
    ('spacetime', 'macroscopic transport by norm-nullification / decoupling from the metric; the Aperture crossing the Zero Layer', 'REJECTED', None, None,
     'no derived metric; a traversable throat needs null-energy-condition-violating stress-energy and risks closed timelike curves; nothing about consciousness follows'),
]


def classify(name):
    for c in CLAIMS:
        if c[1] == name:
            return c
    return None


def report(domain='all'):
    L = ['======= M345 EXTERNAL-THEORY CORRESPONDENCE (Core Part 3.71, L-510, L-553) =======',
         'DOMAIN: %s' % domain,
         'Each proposed match placed by the depth framework; physical correspondence stays in the Scientific Appendix (L-553).', '']
    for dom, name, cls, depth, base, note in CLAIMS:
        if domain != 'all' and dom != domain:
            continue
        d = '' if depth is None else ' (depth %d)' % depth
        b = '' if base is None else ' [base rate: %s]' % base
        L.append('[%s] %s' % (dom.upper(), name))
        L.append('   CLASS: %s%s%s' % (cls, d, b))
        L.append('   %s' % note)
    L.append('')
    L.append('RULE: a count-match is a NATIVE COUNT (depth 1): forced in Ω42, not chance; a correspondence only with a carried map (L-510, L-556); SPECULATION is an open')
    L.append('direction of the Scientific Appendix, not an achievement; REJECTED names a claim that the arithmetic contradicts.')
    L.append('======= END M345 EXTERNAL-THEORY CORRESPONDENCE =======')
    return '\n'.join(L)


def selftest():
    ok = True
    cases = [
        ('the Lorentz representation is DERIVED, not a correspondence',
         classify('A induces a Lorentz transformation in SO+(3,1); iA in SL(2,C)')[2] == 'DERIVED'),
        ('three cycles <-> three generations is a NATIVE COUNT at depth 1',
         classify('three 24-cycles <-> three fermion generations')[2] == 'NATIVE COUNT' and
         classify('three 24-cycles <-> three fermion generations')[3] == 1),
        ('the eight-gluon match is depth 1, a count only',
         classify('the 8-cycle <-> eight gluons of SU(3)')[3] == 1),
        ('over-unity energy extraction is REJECTED',
         classify('over-unity / Zero-Layer extraction / retrocausal entropy cancellation')[2] == 'REJECTED'),
        ('FTL matter transport by decoupling from the metric is REJECTED',
         classify('macroscopic transport by norm-nullification / decoupling from the metric; the Aperture crossing the Zero Layer')[2] == 'REJECTED'),
        ('ambient harvesting is SPECULATION, not rejected and not achieved',
         classify('the 24-cycle organises coupled resonators for ambient-energy harvesting')[2] == 'SPECULATION'),
        ('no claim is graded a correspondence above depth 2 without a derived map',
         all(c[3] is None or c[3] <= 2 for c in CLAIMS if c[2] in ('NATIVE COUNT', 'SPECULATION'))),
        ('the inverse-limit non-periodicity is DERIVED',
         classify('finite-level periodicity vs no nonzero periodic point in the inverse limit')[2] == 'DERIVED'),
    ]
    for name, good in cases:
        print('  %-66s %s' % (name, 'OK' if good else 'MISMATCH')); ok &= good
    print('EXTERNAL-THEORY CORRESPONDENCE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--selftest':
        sys.exit(0 if selftest() else 1)
    dom = 'all'
    if a and a[0] == '--domain' and len(a) > 1:
        dom = a[1]
    print(report(dom))
