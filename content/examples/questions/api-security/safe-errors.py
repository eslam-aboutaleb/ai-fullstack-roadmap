internal = {'reason': 'ownership mismatch', 'database': 'private-db-name'}
public = {'code': 'not_available', 'retryable': False}
assert 'private-db-name' not in str(public)
print(public)
