job = {'checkpoint': 'page2', 'lease_until': 10, 'complete': False}
now = 20
print(job['checkpoint'], 'resume' if not job['complete'] and now > job['lease_until'] else 'wait')
