hits = [{'source': 'D1', 'modality': 'text', 'score': 0.8},
        {'source': 'D1', 'modality': 'image', 'score': 12.0},
        {'source': 'D2', 'modality': 'image', 'score': 9.0}]
print(sorted({hit['source'] for hit in hits}))
