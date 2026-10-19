internal = {'kind': 'model_chunk', 'run': 'T1', 'content': 'Hello', 'private_state': 'secret'}
public = {'type': 'delta', 'task_id': internal['run'], 'text': internal['content']}
assert 'private_state' not in public
print(public)
