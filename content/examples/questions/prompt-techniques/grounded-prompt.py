sources = [{'id': 'P1', 'active': False}, {'id': 'P2', 'active': True}]
packet = {'instruction': 'Answer from evidence or state insufficient evidence',
          'evidence': [source['id'] for source in sources if source['active']]}
print(packet['evidence'])
