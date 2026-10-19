connection = {'id': 'C1', 'state': 'closed'}
session = {'id': 'S1', 'task': 'T1'}
tasks = {'T1': 'running'}
print(connection['state'], tasks[session['task']])
