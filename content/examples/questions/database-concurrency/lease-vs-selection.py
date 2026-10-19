job = {'owner': None, 'lease_until': 0}
now = 10
selected = job['lease_until'] <= now
if selected:
    job.update(owner='B', lease_until=20)
print('eligible' if selected else 'busy', job['owner'])
