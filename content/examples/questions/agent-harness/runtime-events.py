event = {'version': 1, 'task_id': 'T1', 'sequence': 7, 'type': 'delta', 'payload': {'text': 'hello'}}
valid = event['version'] == 1 and event['sequence'] >= 0
print(valid, event['task_id'], event['sequence'])
