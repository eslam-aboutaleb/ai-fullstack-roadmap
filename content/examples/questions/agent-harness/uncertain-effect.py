local = {'status': 'cancelled_wait', 'operation': 'op1'}
remote_ledger = {'op1': 'completed'}
print(local['status'], remote_ledger[local['operation']])
