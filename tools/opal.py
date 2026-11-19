#!/usr/bin/env python3
"""opal.py -- M342 OPAL, the Omega42 Provenance and Authenticity Layer (Core Part 3.68, L-553).

Omega42 does not hide data; it proves origin and integrity. The surface law is linear over Z/9, so it is no cipher,
no key generator and no hash (Core Appendix S.10, the cipher audit); confidentiality, when needed, comes from a
standard primitive. What the law and its record give is provenance: who issued a text, that it is unaltered, and the
24 positions as a way to read a digest by eye. OPAL is three constructive pieces, each stdlib-only and standard:

  SIGN       Ed25519 (RFC 8032) over the canonical bytes of a release manifest or a certificate. The private key stays
             with the issuer, outside the repository; the public key is published once. verify needs only the public key.
  DERIVE     HKDF-SHA256 (RFC 5869) from a master secret, with an Omega42 context as the info string
             (protocol, domain, depth, version, purpose). The context is a label, not a secret; it separates keys by
             domain so one domain's key opens no other. The master secret must have full entropy; a public label adds none.
  FINGERPRINT  a SHA-256 digest written as 56 position-names, base 24 (log2(24) = 4.585 bits each; 56 cover 256 bits with
             0.76 to spare), most significant first -- a reversible encoding of the whole digest for reading by eye, never
             a replacement for it and never itself a verification.

    python3 tools/opal.py --fingerprint FILE          # the file's SHA-256 and its Omega42 Digest String (ODS)
    python3 tools/opal.py --sign-demo                  # ephemeral keypair: sign a sample, verify, tamper, print the ODS
    python3 tools/opal.py --derive MASTER_HEX DOMAIN [DEPTH VERSION PURPOSE]   # a domain key, HKDF-SHA256
    python3 tools/opal.py --selftest                   # runs in CI
OPAL signs and derives; it never asserts that a signed result is mathematically correct, only that the holder of the key
signed exactly these bytes (L-553). Standard library only.
"""
import hashlib, hmac, os, sys

NAMES = ["Seed", "Fixpoint", "Generator", "Desire", "Unity", "Law", "Seed/Causal", "Navigator", "Generation", "Fixpoint",
         "Unity", "Question", "Opening", "Gap", "Observer", "Other", "Flow", "Seed/Return", "Threshold", "Time", "Reckoning",
         "Sublime", "Collective", "Return"]
ODS_LEN = 56
SALT = b"Omega42-OPAL-Domain-Salt"

# ---------------------------------------------------------------- HKDF-SHA256 (RFC 5869), stdlib
def hkdf(ikm, info, length=32, salt=SALT):
    prk = hmac.new(salt, ikm, hashlib.sha256).digest()
    out, t, i = b"", b"", 0
    while len(out) < length:
        i += 1
        t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
        out += t
    return out[:length]


def context(domain, depth=0, version="V335 Rev.450 STABLE", purpose="sign"):
    """the Omega42 key-separation context: a canonical, unambiguous label (not a secret)"""
    return ("Omega42\x1f%s\x1f%d\x1fdepth\x1f%s\x1f%s" % (domain, depth, version, purpose)).encode()


def domain_key(master, domain, depth=0, version="V335 Rev.450 STABLE", purpose="sign"):
    return hkdf(master, context(domain, depth, version, purpose))


# ---------------------------------------------------------------- position-name fingerprint (ODS)
# The 24 position labels include two repeats (Fixpoint at P1/P9, Unity at P4/P10), so names alone are not a reversible
# alphabet. The canonical ODS is the sequence of 56 positions 0..23; it is shown as "Pnn Name" so every token is distinct
# and the sequence reads by eye, and it decodes from the Pnn numbers.
def ods_digits(digest_bytes):
    n = int.from_bytes(digest_bytes, "big")
    digits = []
    for _ in range(ODS_LEN):
        n, r = divmod(n, 24); digits.append(r)
    return list(reversed(digits))


def ods_tokens(digits):
    return ["P%02d %s" % (d, NAMES[d]) for d in digits]


def ods_to_int(digits):
    n = 0
    for d in digits: n = n * 24 + d
    return n


def fingerprint(data):
    d = hashlib.sha256(data).digest()
    return d.hex(), ods_digits(d)


# ---------------------------------------------------------------- Ed25519 (RFC 8032), stdlib reference
_p = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493
_d = (-121665 * pow(121666, _p - 2, _p)) % _p
_I = pow(2, (_p - 1) // 4, _p)


def _recover_x(y, sign):
    xx = (y * y - 1) * pow(_d * y * y + 1, _p - 2, _p) % _p
    x = pow(xx, (_p + 3) // 8, _p)
    if (x * x - xx) % _p != 0: x = x * _I % _p
    if x % 2 != sign: x = _p - x
    return x


_By = 4 * pow(5, _p - 2, _p) % _p
_B = (_recover_x(_By, 0), _By, 1, _recover_x(_By, 0) * _By % _p)


def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % _p
    Bb = (P[1] + P[0]) * (Q[1] + Q[0]) % _p
    C = 2 * P[3] * Q[3] * _d % _p
    D = 2 * P[2] * Q[2] % _p
    E, F, G, H = Bb - A, D - C, D + C, Bb + A
    return (E * F % _p, G * H % _p, F * G % _p, E * H % _p)


def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1: Q = _add(Q, P)
        P = _add(P, P); s >>= 1
    return Q


def _eq(P, Q):
    return (P[0] * Q[2] - Q[0] * P[2]) % _p == 0 and (P[1] * Q[2] - Q[1] * P[2]) % _p == 0


def _comp(P):
    zi = pow(P[2], _p - 2, _p)
    x, y = P[0] * zi % _p, P[1] * zi % _p
    return (y & ~(1 << 255) | ((x & 1) << 255)).to_bytes(32, "little")


def _decomp(b):
    y = int.from_bytes(b, "little") & ~(1 << 255)
    x = _recover_x(y, int.from_bytes(b, "little") >> 255)
    return (x, y, 1, x * y % _p)


def _h(m):
    return hashlib.sha512(m).digest()


def _secret_scalar(h):
    a = int.from_bytes(h[:32], "little") & ((1 << 254) - 8) | (1 << 254)
    return a


def ed25519_keypair(seed=None):
    seed = seed if seed is not None else os.urandom(32)
    h = _h(seed)
    pub = _comp(_mul(_secret_scalar(h), _B))
    return seed, pub


def ed25519_sign(seed, msg):
    h = _h(seed); a = _secret_scalar(h)
    pub = _comp(_mul(a, _B))
    r = int.from_bytes(_h(h[32:] + msg), "little") % _L
    R = _comp(_mul(r, _B))
    k = int.from_bytes(_h(R + pub + msg), "little") % _L
    S = (r + k * a) % _L
    return R + S.to_bytes(32, "little")


def ed25519_verify(pub, msg, sig):
    if len(sig) != 64: return False
    R, S = sig[:32], int.from_bytes(sig[32:], "little")
    if S >= _L: return False
    A = _decomp(pub)
    k = int.from_bytes(_h(R + pub + msg), "little") % _L
    return _eq(_mul(S, _B), _add(_decomp(R), _mul(k, A)))


# ---------------------------------------------------------------- release manifest
def manifest_bytes(fields):
    return "\n".join("%s: %s" % (k, fields[k]) for k in fields).encode()


def selftest():
    ok = True

    def chk(name, good):
        nonlocal ok; ok &= good; print("  %-66s %s" % (name, "OK" if good else "MISMATCH"))

    seed, pub = ed25519_keypair(b"\x01" * 32)
    msg = b"OMEGA42 RELEASE MANIFEST\nCore SHA-256: abc\n"
    sig = ed25519_sign(seed, msg)
    chk("a signature over the manifest verifies", ed25519_verify(pub, msg, sig))
    chk("a tampered manifest fails verification", not ed25519_verify(pub, msg + b" ", sig))
    chk("a wrong key fails verification", not ed25519_verify(ed25519_keypair(b"\x02" * 32)[1], msg, sig))
    chk("signing is deterministic for one seed (RFC 8032)", ed25519_sign(seed, msg) == sig)
    chk("the public key is 32 bytes and recovers on the curve", len(pub) == 32 and _eq(_decomp(pub), _mul(_secret_scalar(_h(seed)), _B)))
    dk1 = domain_key(b"master-secret-0", "consciousness-research")
    dk2 = domain_key(b"master-secret-0", "navigator-exchange")
    chk("two domains give different keys from one master", dk1 != dk2 and len(dk1) == 32)
    chk("the same domain gives the same key", domain_key(b"master-secret-0", "navigator-exchange") == dk2)
    hx, od = fingerprint(b"the Core Specification")
    chk("the ODS is 56 positions, each 0..23", len(od) == ODS_LEN and all(0 <= d < 24 for d in od))
    chk("the ODS is deterministic", fingerprint(b"the Core Specification")[1] == od)
    chk("the ODS changes with one changed byte", fingerprint(b"the Core SpecificatioN")[1] != od)
    chk("the ODS round-trips to the digest integer", ods_to_int(od) == int(hx, 16))
    chk("every ODS token is distinct and reads as Pnn Name", len(set(ods_tokens(range(24)))) == 24)
    import math
    chk("56 base-24 symbols cover 256 bits", 56 * math.log2(24) > 256 and 24 ** 56 > 2 ** 256)
    print("OPAL SELFTEST: %s" % ("PASS" if ok else "FAIL"))
    return ok


def main(a):
    if not a or a[0] == "--selftest":
        sys.exit(0 if selftest() else 1)
    if a[0] == "--fingerprint":
        data = open(a[1], "rb").read(); hx, od = fingerprint(data)
        print("FILE: %s" % a[1]); print("SHA-256: %s" % hx)
        print("OMEGA42 DIGEST STRING (ODS, 56 positions, base 24):")
        print("  " + ", ".join(ods_tokens(od)))
        print("READING (L-553): the ODS encodes the whole digest for the eye; it is checked against the published ODS, and it is not itself a signature.")
        return
    if a[0] == "--sign-demo":
        seed, pub = ed25519_keypair()
        doc = b"OMEGA42 FINDINGS PRESENTATION -- sample"
        sig = ed25519_sign(seed, doc)
        print("PUBLIC KEY: %s" % pub.hex())
        print("SIGNATURE : %s" % sig.hex())
        print("VERIFY    : %s" % ed25519_verify(pub, doc, sig))
        print("TAMPERED  : %s" % ed25519_verify(pub, doc + b"!", sig))
        hx, od = fingerprint(doc)
        print("ODS       : %s" % ", ".join(ods_tokens(od)[:8]) + ", ...")
        print("NOTE: the private key is ephemeral and never written; a real issuer keeps it off the repository (L-553).")
        return
    if a[0] == "--derive":
        master = bytes.fromhex(a[1]); domain = a[2]
        depth = int(a[3]) if len(a) > 3 else 0
        version = a[4] if len(a) > 4 else "V335 Rev.450 STABLE"
        purpose = a[5] if len(a) > 5 else "sign"
        print("DOMAIN KEY (%s): %s" % (domain, domain_key(master, domain, depth, version, purpose).hex()))
        print("CONTEXT: %s" % context(domain, depth, version, purpose).decode().replace("\x1f", " | "))
        return
    print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
