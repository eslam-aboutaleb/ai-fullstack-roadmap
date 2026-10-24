lease = {'owner': 'B', 'token': 8}
releasing_token = 7
if lease and lease['token'] == releasing_token:
    lease = None
print(lease['owner'])
