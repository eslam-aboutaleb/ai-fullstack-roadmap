factories = {'memory': lambda: {'backend': 'memory'},
             'test': lambda: {'backend': 'test'}}
def build(name):
    if name not in factories:
        raise ValueError('unsupported backend')
    return factories[name]()
print(build('memory')['backend'])
