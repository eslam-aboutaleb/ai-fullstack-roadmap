canonical = {'contact': 'email', 'pending_action': 'confirm_exchange'}
canonical['contact'] = 'text'
working = {key: canonical[key] for key in ('contact', 'pending_action')}
print(working['contact'], working['pending_action'])
