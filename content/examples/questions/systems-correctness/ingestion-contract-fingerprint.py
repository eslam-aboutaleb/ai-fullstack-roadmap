"""Deterministic representation fingerprints using synthetic configuration."""
import hashlib
import json

def digest(config):
    encoded = json.dumps(config, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(encoded.encode('utf-8')).hexdigest()

original = dict(source_hash='abc', parser='p1', chunker='c1', model_revision='m1', dimension=3)
reordered = dict(reversed(list(original.items())))
changed = dict(original, model_revision='m2')
assert digest(original) == digest(reordered)
assert digest(original) != digest(changed)
print('key order: stable; model change: rebuild')
