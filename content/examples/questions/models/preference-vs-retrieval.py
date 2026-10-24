preference = {'prompt': 'Explain politely', 'chosen': 'Please...', 'rejected': 'Go away'}
request = {'question': 'Current return rule?', 'evidence_revision': 3}
print('chosen' in preference and 'rejected' in preference, request['evidence_revision'])
