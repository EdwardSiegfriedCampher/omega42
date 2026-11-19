#!/usr/bin/env python3
"""records/opal/compute.py -- the reproducible witness behind CERT-0008.
It states, by direct arithmetic, why the surface law is no cipher (descriptive facts, not an attack), and that the OPAL
provenance layer is constructive and self-consistent. Run from this directory: python3 compute.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools'))
import opal

T = lambda s: (s[1] % 9, (s[0] + s[1]) % 9)
add = lambda a, b: ((a[0] + b[0]) % 9, (a[1] + b[1]) % 9)
STATES = [(a, b) for a in range(9) for b in range(9)]

# 1. the surface law is linear over Z/9: T(x+y) = T(x)+T(y), so any number of keyed rounds compose to one affine map
linear = all(T(add(x, y)) == add(T(x), T(y)) for x in STATES for y in STATES)
# 2. the whole state space is 81; the orbit of a state is public (computable by anyone)
codebook = len(STATES)
# 3. the Hermitian determinant mod 9 takes all 9 residues: an at-most-9-valued output, no hash
delta = {(t * t - x * x - y * y - z * z) % 9 for t in range(9) for x in range(9) for y in range(9) for z in range(9)}
# 4. the OPAL layer is constructive and self-consistent (fixed seed, deterministic)
seed, pub = opal.ed25519_keypair(b'\x07' * 32)
doc = b'OMEGA42 PROVENANCE WITNESS'
sig = opal.ed25519_sign(seed, doc)
verify_ok = opal.ed25519_verify(pub, doc, sig)
tamper_ok = opal.ed25519_verify(pub, doc + b'.', sig)
dk1 = opal.domain_key(b'\x07' * 32, 'consciousness-research')
dk2 = opal.domain_key(b'\x07' * 32, 'navigator-exchange')
hx, od = opal.fingerprint(doc)

print('OMEGA42 OPAL WITNESS (CERT-0008)')
print('law is linear over Z/9 (T(x+y)=T(x)+T(y)):', linear)
print('surface codebook (states):', codebook)
print('Hermitian determinant mod 9, number of distinct outputs:', len(delta))
print('signature verifies:', verify_ok, '| tampered verifies:', tamper_ok)
print('domain keys for two domains differ:', dk1 != dk2)
print('public key:', pub.hex())
print('signature:', sig.hex())
print('ODS length:', len(od), '| first eight:', ', '.join(opal.ods_tokens(od)[:8]))
print('CONCLUSION: no secure cipher, key generator, hash or signature follows from the surface law; provenance is signed, not hidden.')
