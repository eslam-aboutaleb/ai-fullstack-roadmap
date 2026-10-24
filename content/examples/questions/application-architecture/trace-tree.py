spans = [{'id': 'api', 'parent': None, 'trace': 'trace1'},
         {'id': 'worker', 'parent': 'api', 'trace': 'trace1'},
         {'id': 'retrieve', 'parent': 'worker', 'trace': 'trace1'}]
assert len({span['trace'] for span in spans}) == 1
print(*(span['id'] for span in spans))
