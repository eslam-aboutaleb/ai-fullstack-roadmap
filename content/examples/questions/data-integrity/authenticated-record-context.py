"""Requires cryptography==50.0.2; real AEAD with ephemeral synthetic data."""
import json
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def context(tenant, record):
    return json.dumps(dict(tenant=tenant, record=record, schema=1, purpose='private-field'), sort_keys=True).encode()
key = AESGCM.generate_key(bit_length=256)
aead = AESGCM(key)
nonce = os.urandom(12)
aad = context('T1', 'R1')
ciphertext = aead.encrypt(nonce, b'synthetic private value', aad)
assert aead.decrypt(nonce, ciphertext, aad) == b'synthetic private value'
tampered = ciphertext[:-1] + bytes([ciphertext[-1] ^ 1])
for payload, associated in ((tampered, aad), (ciphertext, context('T1', 'R2'))):
    try:
        aead.decrypt(nonce, payload, associated)
    except InvalidTag:
        pass
    else:
        raise AssertionError('invalid ciphertext or context accepted')
print('round trip verified; tampering and record substitution rejected')
