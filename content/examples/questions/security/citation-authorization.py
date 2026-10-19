citations = {'C1': {'document': 'D1', 'revision': 2, 'span': [0, 20], 'owner': 'A'}}
viewer = 'B'
source = citations['C1']
print(source['span'] if source['owner'] == viewer else 'denied')
