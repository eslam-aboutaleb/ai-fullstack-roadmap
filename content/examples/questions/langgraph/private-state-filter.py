state = {'task': 'T1', 'status': 'waiting', 'internal_notes': 'private', 'token': 'secret'}
public = {key: state[key] for key in ('task', 'status')}
print(sorted(public))
