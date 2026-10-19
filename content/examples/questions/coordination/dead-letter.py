failed = {'operation': 'op1', 'attempt': 'attempt3', 'reason': 'unsupported_format'}
replay = {**failed, 'attempt': 'attempt4', 'profile': 'extractor-v2'}
print(replay['operation'], replay['attempt'])
