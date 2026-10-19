branches = {'policy': {'required': True, 'status': 'ok'},
            'order': {'required': True, 'status': 'unavailable'}}
complete = all(branch['status'] == 'ok' for branch in branches.values() if branch['required'])
print('completed' if complete else 'partial')
