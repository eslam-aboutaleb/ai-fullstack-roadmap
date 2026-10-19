signals = {'process_alive': True, 'oldest_task_seconds': 90}
if signals['oldest_task_seconds'] > 60:
    alert = {'name': 'task_delay', 'runbook': 'worker-recovery'}
    print(alert['name'], alert['runbook'])
