"""Reject comparisons that use different test or taxonomy contracts."""
a = {'test':'heldout-v1','taxonomy':'labels-v2','timing':'end-to-end'}
b = dict(a,timing='head-only')
assert a != b
b['timing'] = 'end-to-end'
assert a == b
print('matched evaluation and timing contracts required before comparison')
