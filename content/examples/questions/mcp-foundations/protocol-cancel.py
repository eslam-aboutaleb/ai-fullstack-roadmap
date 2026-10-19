cancellation = {'state': 'requested', 'task': 'T1'}
tasks = {'T1': {'state': 'completed'}}
print(cancellation['state'], tasks[cancellation['task']]['state'])
