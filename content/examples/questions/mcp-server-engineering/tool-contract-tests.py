def excerpt(document_id, limit):
    if document_id != 'D1' or not 0 < limit <= 20:
        raise ValueError('invalid arguments')
    return 'Exchange only'[:limit]
assert excerpt('D1', 8) == 'Exchange'
try:
    excerpt('D1', 1000)
except ValueError:
    pass
else:
    raise AssertionError('unbounded request accepted')
print('contract checks passed')
