milestones = {'vertical_slice': set(), 'retrieval': {'vertical_slice'},
              'generation': {'retrieval'}, 'deployment': {'generation'}}
complete = {'vertical_slice'}
ready = [name for name, prerequisites in milestones.items() if name not in complete and prerequisites <= complete]
print(ready)
