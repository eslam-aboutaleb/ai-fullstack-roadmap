state = {'revision':4,'deleted':True,'text':''}
incoming = {'revision':3,'deleted':False,'text':'old content'}
if incoming['revision'] > state['revision']:
    state = incoming
assert state['deleted'] and state['text'] == ''
print(state['revision'],state['deleted'])
