checkpoint = {'task': 'T1', 'schema': 1, 'completed': ['retrieve'],
              'next': 'review', 'operation': 'op1', 'status': 'waiting'}
print(checkpoint['next'], checkpoint['operation'])
