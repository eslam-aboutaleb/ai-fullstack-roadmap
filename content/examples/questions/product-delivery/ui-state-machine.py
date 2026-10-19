transitions = {('idle', 'submit'): 'pending', ('pending', 'delta'): 'streaming',
               ('streaming', 'completed'): 'completed', ('streaming', 'failed'): 'incomplete'}
state = transitions[('idle', 'submit')]
state = transitions[(state, 'delta')]
print(state)
