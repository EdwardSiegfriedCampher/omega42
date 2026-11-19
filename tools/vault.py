#!/usr/bin/env python3
"""vault.py -- M364 Ω42-Envelope v1 and the Ω42 Vault (Core Part 3.77; APE-436, F175; Core Appendix S.10).

The security rests on standard, reviewed primitives only: scrypt (password hardening), HKDF-SHA256 (key derivation
and Ω42 domain separation), AES-256-GCM (authenticated encryption), Ed25519 (optional sender signature, tools/opal.py).
Ω42 supplies the architecture: the domain path of every key, the readable 24-position fingerprint of every envelope
and key (OPAL, M342), the authenticated header, the key-rotation version. Ω42's groups supply no hardness and are
never used to scramble data: their orders are built from 2 and 3 alone (Companion 198.3).

    python3 tools/vault.py encrypt-text "MESSAGE" --password P [--domain D] [--k K]     -> an envelope (JSON)
    python3 tools/vault.py decrypt FILE.o42 --password P                                -> the plaintext
    python3 tools/vault.py lock FILE --password P [--domain D]                          -> FILE.o42 (a whole file)
    python3 tools/vault.py unlock FILE.o42 --password P                                 -> FILE (restored)
    python3 tools/vault.py newmaster MASTERFILE                                         a random 32-byte master key
    python3 tools/vault.py lock FILE --master MASTERFILE --domain project/dataset [--rotation N]
    python3 tools/vault.py inspect FILE.o42                                             the header and fingerprints
    python3 tools/vault.py --selftest
"""
import base64, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag
import hashlib
import opal

PROTOCOL = 'Omega42-Envelope'; VERSION = 1
SCRYPT = dict(n=2 ** 15, r=8, p=1)          # about 32 MiB per derivation; tune upward for long-term secrets
CIPHER = 'AES-256-GCM'


def b64(x):
    return base64.b64encode(x).decode('ascii')


def ub64(x):
    return base64.b64decode(x.encode('ascii'), validate=True)


def info(domain, k, rotation, purpose):
    # the Ω42 domain path: every key is bound to protocol, version, domain, configuration, rotation and purpose
    return '\x1f'.join(['Omega42-Envelope-v1', domain, 'k=%d' % k, 'rot=%d' % rotation, purpose]).encode('utf-8')


def hkdf(ikm, salt, inf):
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=inf).derive(ikm)


def key_from_password(password, salt, domain, k, rotation):
    base = hashlib.scrypt(password.encode('utf-8'), salt=salt, dklen=32, maxmem=64 * 1024 * 1024, **SCRYPT)
    return hkdf(base, salt, info(domain, k, rotation, 'encrypt'))


def key_from_master(master, salt, domain, k, rotation):
    return hkdf(master, salt, info(domain, k, rotation, 'encrypt'))


def key_id(master, domain, k, rotation):
    """a public identifier of a derived key: its own HKDF output under purpose 'key-id', in ODS tokens -- never the key."""
    kid = hkdf(master, b'Omega42-key-id', info(domain, k, rotation, 'key-id'))
    return ' '.join(opal.ods_tokens(opal.ods_digits(kid))[:4])


def aad(header):
    return json.dumps(header, sort_keys=True, separators=(',', ':')).encode('utf-8')


def seal(data, *, password=None, master=None, domain='default', k=2, rotation=1, name=None, sign_seed=None):
    if (password is None) == (master is None):
        raise ValueError('give a password or a master key, not both')
    if not 1 <= k <= 20:
        raise ValueError('k is a public configuration label between 1 and 20, not a security parameter')
    salt, nonce = os.urandom(16), os.urandom(12)
    header = dict(protocol=PROTOCOL, version=VERSION, cipher=CIPHER, omega42_k=k, domain=domain, rotation=rotation,
                  kdf='scrypt+hkdf' if password is not None else 'master+hkdf', created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    if password is not None:
        header['scrypt'] = SCRYPT
        key = key_from_password(password, salt, domain, k, rotation)
    else:
        header['key_id'] = key_id(master, domain, k, rotation)
        key = key_from_master(master, salt, domain, k, rotation)
    if name:
        header['name'] = name
    ct = AESGCM(key).encrypt(nonce, data, aad(header))
    env = dict(header=header, salt=b64(salt), nonce=b64(nonce), ciphertext=b64(ct))
    env['fingerprint'] = fingerprint(env)
    if sign_seed is not None:
        pub = opal.ed25519_keypair(sign_seed)[1]
        env['signature'] = dict(scheme='Ed25519', public=pub.hex(), sig=opal.ed25519_sign(sign_seed, signed_bytes(env)).hex())
    return env


def signed_bytes(env):
    return aad(dict(h=env['header'], s=env['salt'], n=env['nonce'], c=env['ciphertext']))


def fingerprint(env):
    d = hashlib.sha256(signed_bytes(env)).digest()
    return ' '.join(opal.ods_tokens(opal.ods_digits(d))[:6])


def open_(env, *, password=None, master=None):
    h = env['header']
    if h.get('protocol') != PROTOCOL:
        raise ValueError('unknown protocol')
    if h.get('version') != VERSION:
        raise ValueError('unsupported version')
    if h.get('cipher') != CIPHER:
        raise ValueError('unsupported cipher')
    k = int(h['omega42_k'])
    if not 1 <= k <= 20:
        raise ValueError('invalid Ω42 configuration')
    salt, nonce, ct = ub64(env['salt']), ub64(env['nonce']), ub64(env['ciphertext'])
    if len(salt) != 16 or len(nonce) != 12:
        raise ValueError('invalid envelope parameters')
    if env.get('fingerprint') != fingerprint(env):
        raise ValueError('fingerprint mismatch: the envelope was altered')
    if 'signature' in env:
        s = env['signature']
        if not opal.ed25519_verify(bytes.fromhex(s['public']), signed_bytes(env), bytes.fromhex(s['sig'])):
            raise ValueError('signature invalid')
    if h['kdf'] == 'scrypt+hkdf':
        if password is None:
            raise ValueError('this envelope needs a password')
        if h.get('scrypt') != SCRYPT:
            raise ValueError('unsupported scrypt parameters')
        key = key_from_password(password, salt, h['domain'], k, h['rotation'])
    else:
        if master is None:
            raise ValueError('this envelope needs the master key of its domain')
        if key_id(master, h['domain'], k, h['rotation']) != h['key_id']:
            raise ValueError('wrong master key, domain or rotation for this envelope')
        key = key_from_master(master, salt, h['domain'], k, h['rotation'])
    try:
        return AESGCM(key).decrypt(nonce, ct, aad(h))
    except InvalidTag:
        raise ValueError('authentication failed: wrong key, or the ciphertext or header was altered')


# ------------------------------------------------------------------ selftest and CLI
def selftest():
    msg = 'Ω42: a mathematical structure with an open ontological question.'.encode('utf-8')
    e1 = seal(msg, password='a-long-example-passphrase', k=3, domain='research/notes')
    e2 = seal(msg, password='a-long-example-passphrase', k=3, domain='research/notes')
    def fails(env, **kw):
        try:
            open_(env, **kw); return False
        except ValueError:
            return True
    t = json.loads(json.dumps(e1)); c = bytearray(ub64(t['ciphertext'])); c[5] ^= 1; t['ciphertext'] = b64(bytes(c)); t['fingerprint'] = fingerprint(t)
    hd = json.loads(json.dumps(e1)); hd['header']['domain'] = 'research/other'; hd['fingerprint'] = fingerprint(hd)
    fp = json.loads(json.dumps(e1)); c2 = bytearray(ub64(fp['ciphertext'])); c2[0] ^= 1; fp['ciphertext'] = b64(bytes(c2))
    ver = json.loads(json.dumps(e1)); ver['header']['version'] = 2
    master = os.urandom(32)
    m1 = seal(b'dataset row 1', master=master, domain='lab/cal', rotation=1)
    m2 = seal(b'dataset row 1', master=master, domain='lab/cal', rotation=2)
    seed = bytes(range(32))
    sg = seal(b'signed note', password='pw-example-123', sign_seed=seed)
    sgt = json.loads(json.dumps(sg)); sgt['header']['name'] = 'forged'; sgt['fingerprint'] = fingerprint(sgt)
    cases = [
        ('round trip: the right password recovers the message', open_(e1, password='a-long-example-passphrase') == msg),
        ('the same message twice gives different envelopes (fresh salt and nonce)', e1['ciphertext'] != e2['ciphertext'] and e1['salt'] != e2['salt']),
        ('a wrong password fails authentication', fails(e1, password='a-wrong-passphrase')),
        ('one flipped ciphertext bit fails authentication', fails(t, password='a-long-example-passphrase')),
        ('an altered authenticated header fails (domain changed)', fails(hd, password='a-long-example-passphrase')),
        ('an altered envelope with a stale fingerprint is refused before decryption', fails(fp, password='a-long-example-passphrase')),
        ('an unsupported version is rejected', fails(ver, password='a-long-example-passphrase')),
        ('master-key domains: the right master opens, another master is refused by key id',
         open_(m1, master=master) == b'dataset row 1' and fails(m1, master=os.urandom(32))),
        ('rotation: the same domain under rotations 1 and 2 has different key ids', m1['header']['key_id'] != m2['header']['key_id']),
        ('Ed25519: a signed envelope verifies; a header change with a recomputed fingerprint fails the signature',
         open_(sg, password='pw-example-123') == b'signed note' and fails(sgt, password='pw-example-123')),
        ('the fingerprint is six ODS tokens', len(e1['fingerprint'].split(' ')) == 12),
    ]
    ok = True
    for name, good in cases:
        print('%s %s' % (name, 'PASS' if good else 'FAIL')); ok &= bool(good)
    print('Ω42-ENVELOPE SELFTEST: %s' % ('PASS' if ok else 'FAIL'))
    return ok


def arg(a, flag, default=None):
    return a[a.index(flag) + 1] if flag in a else default


def main(a):
    if a[:1] == ['--selftest']:
        return 0 if selftest() else 1
    if a[:1] == ['newmaster']:
        open(a[1], 'wb').write(os.urandom(32)); os.chmod(a[1], 0o600); print('master key written to %s (keep it secret)' % a[1]); return 0
    pw = arg(a, '--password'); mf = arg(a, '--master'); master = open(mf, 'rb').read() if mf else None
    dom = arg(a, '--domain', 'default'); k = int(arg(a, '--k', '2')); rot = int(arg(a, '--rotation', '1'))
    if a[:1] == ['encrypt-text']:
        print(json.dumps(seal(a[1].encode('utf-8'), password=pw, master=master, domain=dom, k=k, rotation=rot), indent=1)); return 0
    if a[:1] == ['decrypt']:
        sys.stdout.buffer.write(open_(json.load(open(a[1])), password=pw, master=master)); return 0
    if a[:1] == ['lock']:
        env = seal(open(a[1], 'rb').read(), password=pw, master=master, domain=dom, k=k, rotation=rot, name=os.path.basename(a[1]))
        json.dump(env, open(a[1] + '.o42', 'w'), indent=1); print('locked %s -> %s.o42 | fingerprint %s' % (a[1], a[1], env['fingerprint'])); return 0
    if a[:1] == ['unlock']:
        env = json.load(open(a[1])); out = a[1][:-4] if a[1].endswith('.o42') else a[1] + '.out'
        open(out, 'wb').write(open_(env, password=pw, master=master)); print('unlocked %s -> %s' % (a[1], out)); return 0
    if a[:1] == ['inspect']:
        env = json.load(open(a[1]))
        print(json.dumps(env['header'], indent=1)); print('fingerprint: %s%s' % (env['fingerprint'], ' | signed (Ed25519)' if 'signature' in env else '')); return 0
    print(__doc__); return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
