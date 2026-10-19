replica_connections = {'A': {'C1'}, 'B': {'C2'}}
shared_tasks = {'T1': 'completed'}
new_connection = {'replica': 'B', 'task': 'T1'}
print(shared_tasks[new_connection['task']])
