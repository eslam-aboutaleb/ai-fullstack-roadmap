record = {'source': 'D1', 'revision': 2, 'tenant': 'A', 'profile': 'v1', 'vector': [1, 0]}
print({key: record[key] for key in ('source', 'revision')})
