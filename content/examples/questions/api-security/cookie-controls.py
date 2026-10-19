cookie = {'Secure': True, 'HttpOnly': True, 'SameSite': 'Lax'}
request = {'origin_allowed': True, 'csrf_valid': False, 'mutates': True}
accepted = request['origin_allowed'] and (not request['mutates'] or request['csrf_valid'])
print(accepted)
