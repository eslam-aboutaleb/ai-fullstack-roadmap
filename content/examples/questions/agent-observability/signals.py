log = {'event': 'task_failed', 'trace': 'trace1'}
span = {'id': 'span2', 'parent': 'span1'}
metric = {'task_failed_total': 1}
print(log['event'], span['id'], metric['task_failed_total'])
