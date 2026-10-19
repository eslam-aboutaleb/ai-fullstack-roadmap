worker = {'accepting': True, 'task': 'T1', 'operation': 'op1', 'checkpoint': 'chunked'}
worker.update(accepting=False, status='recoverable')
print(worker['accepting'], worker['status'], worker['operation'])
