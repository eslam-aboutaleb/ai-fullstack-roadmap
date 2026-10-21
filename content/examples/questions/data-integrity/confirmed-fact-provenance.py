"""A narrow explicit authority policy for synthetic enrichment proposals."""
def apply(current, proposal):
    if current['status'] == 'confirmed' and proposal['status'] == 'inferred':
        return current
    return proposal
confirmed = dict(value='intermediate', status='confirmed', revision=3)
inferred = dict(value='expert', status='inferred', source='model-run-8')
assert apply(confirmed, inferred) is confirmed
unknown = dict(value=None, status='unknown')
assert unknown['value'] is None
print('confirmed fact retained; unknown not replaced by an invented default')
