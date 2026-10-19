from collections import deque
tasks = {'T1': {'status': 'queued'}}
seen, queue = {'T1'}, deque(['T1'])
if 'T1' not in seen:
    queue.append('T1')
task_id = queue.popleft()
print(task_id, tasks[task_id]['status'])
