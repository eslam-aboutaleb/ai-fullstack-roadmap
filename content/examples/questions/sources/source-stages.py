listing = {'id': 'D1', 'location': 'synthetic-file'}
raw = b'policy'
extracted = raw.decode('utf-8')
indexed = {'source': listing['id'], 'text': extracted}
print(indexed['source'], indexed['text'])
