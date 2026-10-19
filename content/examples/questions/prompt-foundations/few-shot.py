request = {'examples': [
    {'input': 'known rule', 'output': 'answer with source'},
    {'input': 'no source', 'output': 'insufficient_evidence'},
], 'question': 'warranty?'}
print(len(request['examples']), request['question'])
