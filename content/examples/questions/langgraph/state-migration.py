saved = {'schema': 1, 'task': 'T1'}
owners = {'T1': 'A'}
if saved['schema'] == 1:
    saved = {**saved, 'schema': 2, 'scope': owners[saved['task']]}
print(saved['schema'], saved['scope'])
