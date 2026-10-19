import hashlib, json
profile = {'source_digest': 'abc', 'chunk_words': 100, 'embedding': 'model-v1'}
fingerprint = lambda value: hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()
old = fingerprint(profile)
profile['chunk_words'] = 200
print(old != fingerprint(profile))
