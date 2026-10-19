restored = {'tasks': 12, 'permissions_ok': False, 'pending_jobs_reconciled': True}
usable = restored['tasks'] == 12 and restored['permissions_ok'] and restored['pending_jobs_reconciled']
print(usable)
