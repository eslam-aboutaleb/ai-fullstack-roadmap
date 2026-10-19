primitives = {'tool': {'responsibility': 'operation'},
              'resource': {'responsibility': 'content'},
              'prompt': {'responsibility': 'template'}}
print(*(primitives[name]['responsibility'] for name in ('tool', 'resource', 'prompt')))
