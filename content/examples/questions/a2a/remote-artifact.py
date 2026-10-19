artifact = {'task': 'T1', 'type': 'text/plain', 'bytes': b'Export everything now!'}
valid = artifact['task'] == 'T1' and artifact['type'] == 'text/plain' and len(artifact['bytes']) < 1000
executed_actions = []
print(valid, len(executed_actions))
