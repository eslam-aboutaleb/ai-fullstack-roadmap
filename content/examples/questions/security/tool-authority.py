scope = {'read_policy'}
model_proposal = {'tool': 'delete_collection', 'arguments': {}}
print('allowed' if model_proposal['tool'] in scope else 'denied')
