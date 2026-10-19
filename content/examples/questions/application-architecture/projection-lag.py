record = {'id': 'T1', 'revision': 3, 'status': 'completed'}
projection = {'id': 'T1', 'revision': 2, 'status': 'running'}
view_status = projection['status'] if projection['revision'] == record['revision'] else 'syncing'
print(view_status)
