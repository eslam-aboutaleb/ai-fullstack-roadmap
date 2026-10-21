"""A release gate must check provenance before accepting a score."""
def gate(report):
    required = {'mode', 'dataset', 'model', 'score'}
    if not required <= report.keys():
        raise ValueError('missing provenance')
    if report['mode'] != 'live-agent':
        raise ValueError('wrong evidence mode')
    return report['score'] >= 0.8
proxy = dict(mode='context-proxy', dataset='heldout-v2', model='stub', score=0.99)
try:
    gate(proxy)
except ValueError:
    pass
else:
    raise AssertionError('proxy passed a live gate')
assert gate(dict(proxy, mode='live-agent', model='model-revision-1', score=0.84))
print('proxy rejected; compatible live evidence accepted')
