runs = [{'dataset': 'q-v1', 'chunker': 'small', 'recall': 0.8, 'tokens': 500},
        {'dataset': 'q-v1', 'chunker': 'large', 'recall': 0.9, 'tokens': 1200}]
assert len({run['dataset'] for run in runs}) == 1
print(runs[1]['recall'], runs[1]['tokens'])
