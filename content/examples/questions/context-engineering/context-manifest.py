now = 20
blocks = [{'name': 'policy', 'origin': 'P2:r2', 'relevant': True, 'expires': 30, 'tokens': 40},
          {'name': 'old_memory', 'origin': 'M1', 'relevant': True, 'expires': 10, 'tokens': 20}]
selected = [block for block in blocks if block['relevant'] and block['expires'] > now]
print([block['name'] for block in selected])
