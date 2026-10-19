allowed, effects = {'read_policy'}, []
proposal = 'send_private_documents'
if proposal in allowed:
    effects.append(proposal)
status = 'allowed' if proposal in allowed else 'denied'
assert effects == []
print(status, len(effects))
