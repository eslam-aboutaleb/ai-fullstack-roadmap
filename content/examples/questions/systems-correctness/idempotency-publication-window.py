"""Deterministic interleavings; no Redis or external effects."""
def can_start(state):
    return state['result'] is None and state['owner'] is None

unsafe = dict(result=None, owner='A')
unsafe['owner'] = None  # release first
assert can_start(unsafe)  # B can enter before publication
safe = dict(result=None, owner='A')
safe['result'] = {'operation': 'op-1', 'status': 'completed'}
assert not can_start(safe)
safe['owner'] = None
assert not can_start(safe)
print('release-first: duplicate window; publish-first: replay')
