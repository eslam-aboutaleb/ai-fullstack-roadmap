store = {'T1': {'status': 'running', 'owner': 'A'}}
accepted = {'http_status': 202, 'task_id': 'T1', 'location': '/tasks/T1'}
print(accepted['http_status'], store[accepted['task_id']]['status'])
