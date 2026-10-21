"""Set coverage and exclusion checks allow harmless rank swaps."""
def check_result(ids, required, forbidden):
    assert len(ids) == len(set(ids)), 'duplicate identities'
    assert required <= set(ids), 'missing required evidence'
    assert not forbidden.intersection(ids), 'ineligible evidence'

for ordering in (['rule', 'exception'], ['exception', 'rule']):
    check_result(ordering, {'rule', 'exception'}, {'private'})
try:
    check_result(['rule', 'private'], {'rule', 'exception'}, {'private'})
except AssertionError:
    pass
else:
    raise AssertionError('bad retrieval passed')
print('valid rank swaps pass; missing or forbidden evidence fails')
