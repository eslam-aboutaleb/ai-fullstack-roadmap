task = {'id': 'T1', 'status': 'accepted', 'artifacts': []}
task.update(status='completed', artifacts=[{'id': 'report1', 'type': 'text'}])
print(task['id'], task['status'], task['artifacts'][0]['id'])
