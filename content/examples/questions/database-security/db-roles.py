roles = {'app': {'select', 'insert', 'update'}, 'migration': {'alter', 'create'}}
print('alter' in roles['app'], 'alter' in roles['migration'])
