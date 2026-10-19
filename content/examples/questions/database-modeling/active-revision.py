generations = {1: {'complete': True}, 2: {'complete': False}}
active = 1
print(active, end=' ')
generations[2]['complete'] = True
if generations[2]['complete']:
    active = 2
print(active)
