approved = {'owner': 'A', 'item': 'I1', 'revision': 3, 'expires': 100}
request = {'owner': 'A', 'item': 'I2', 'revision': 4}
now = 50
valid = now < approved['expires'] and all(
    request[key] == approved[key] for key in ('owner', 'item', 'revision'))
print(valid)
