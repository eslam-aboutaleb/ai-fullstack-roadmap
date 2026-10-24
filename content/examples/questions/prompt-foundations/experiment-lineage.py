import hashlib, json
profile = {'data': 'synthetic-v1', 'prompt': 'p1', 'model': 'fake-v1', 'seed': 7}
fingerprint = lambda item: hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()
original = fingerprint(profile)
profile['prompt'] = 'p2'
print(original != fingerprint(profile))
