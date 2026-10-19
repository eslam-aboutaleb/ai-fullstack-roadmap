key = lambda tenant: (tenant, 'D1:r2', 'prompt-v3', 'refund?')
cache = {key('A'): 'private answer'}
print(key('A') == key('B'), end=' ')
cache.clear()
print(len(cache))
