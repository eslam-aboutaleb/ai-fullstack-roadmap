answer = {'claim': 'Refund allowed', 'source': 'P2:r2'}
reviewed_support = {('Exchange allowed', 'P2:r2'): True}
schema_valid = set(answer) == {'claim', 'source'}
supported = reviewed_support.get((answer['claim'], answer['source']), False)
print(f'schema_valid={schema_valid} supported={supported}')
