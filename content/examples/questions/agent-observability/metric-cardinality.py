event = {'operation': 'retrieve', 'outcome': 'timeout', 'task_id': 'T123', 'user_id': 'U456'}
labels = {key: event[key] for key in ('operation', 'outcome')}
print(sorted(labels))
