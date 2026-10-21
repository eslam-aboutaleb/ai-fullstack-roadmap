"""Requires cryptography==50.0.2; direct re-encryption, not KMS rewrapping."""
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
keys = {name: AESGCM.generate_key(bit_length=256) for name in ('k1', 'k2')}
aad = b'tenant:T1|record:R1|schema:1'
def encrypt(key_id, value):
    nonce = os.urandom(12)
    return dict(key_id=key_id, nonce=nonce, ciphertext=AESGCM(keys[key_id]).encrypt(nonce, value, aad))
def decrypt(envelope):
    return AESGCM(keys[envelope['key_id']]).decrypt(envelope['nonce'], envelope['ciphertext'], aad)
old = encrypt('k1', b'synthetic value')
rotated = encrypt('k2', decrypt(old))
assert decrypt(old) == decrypt(rotated) == b'synthetic value'
assert rotated['key_id'] == 'k2'
assert rotated['nonce'] != old['nonce'] or keys['k1'] != keys['k2']
print('old readable; new key active; plaintext preserved during rotation')
