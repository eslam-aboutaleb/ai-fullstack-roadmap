hits = [{'id': 'B1', 'tenant': 'B', 'score': 0.99},
        {'id': 'A1', 'tenant': 'A', 'score': 0.95}]
eligible = [hit for hit in hits if hit['tenant'] == 'A']
print([hit['id'] for hit in sorted(eligible, key=lambda hit: -hit['score'])[:1]])
