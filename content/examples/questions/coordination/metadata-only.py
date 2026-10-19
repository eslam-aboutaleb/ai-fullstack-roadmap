old = {'digest': 'abc', 'profile': 'v1', 'owner': 'A'}
new = {**old, 'owner': 'B'}
reembed = (old['digest'], old['profile']) != (new['digest'], new['profile'])
print(reembed, old['owner'] != new['owner'])
