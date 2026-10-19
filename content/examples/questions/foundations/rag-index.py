document = {'id': 'D1', 'revision': 2, 'text': 'Sale: exchange only\nShipping: 3 days'}
chunks = [{'id': f"D1:r2:c{i}", 'text': text, 'vector': [float(i), 1.0]}
          for i, text in enumerate(document['text'].splitlines())]
evidence = {'source': chunks[0]['id'], 'text': chunks[0]['text']}
print(evidence['source'], evidence['text'])
