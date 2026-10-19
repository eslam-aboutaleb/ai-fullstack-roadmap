evidence = {'label': 'E1', 'source': 'D1', 'revision': 2,
            'span': [10, 30], 'text': 'Exchange only', 'scope': 'A'}
required = {'label', 'source', 'revision', 'span', 'text', 'scope'}
print(required <= evidence.keys())
