scope = {'supported': {'policy_search'}, 'excluded': {'payments', 'voice'}}
print(sorted(scope['supported']), 'payments' in scope['supported'])
