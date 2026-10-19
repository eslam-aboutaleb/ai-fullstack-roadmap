progress = {'uploaded': True, 'extracted': True, 'embedded': False, 'active': False}
status = 'ready' if progress['active'] else 'indexing'
print(status, progress['active'])
