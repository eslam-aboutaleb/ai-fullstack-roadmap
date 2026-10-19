sessions = [{'pending': []} for _ in range(2)]
sessions[0]['pending'].append('change')
print(sessions[0] is not sessions[1], len(sessions[1]['pending']))
