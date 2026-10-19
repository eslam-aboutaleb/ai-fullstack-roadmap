state = {'revision': 13, 'answer': 'current'}
late = {'revision': 12, 'answer': 'obsolete'}
if late['revision'] >= state['revision']:
    state = late
print(state['revision'])
