session = {'owner': 'parent'}
delegated_result = {'from': 'specialist', 'rule': 'exchange'}
print(session['owner'], end=' ')
session['owner'] = 'specialist'
print(session['owner'])
