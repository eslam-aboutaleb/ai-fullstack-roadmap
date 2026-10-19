ui = {'status': 'completed', 'operation': 'op1'}
effect_ledger = {}
consistent = ui['status'] != 'completed' or ui['operation'] in effect_ledger
print(consistent)
