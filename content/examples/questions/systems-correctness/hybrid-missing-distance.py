"""Preserve zero and missing distances while fusing synthetic ranks."""
import json
hits = [{'id': 'vector', 'distance': 0.0}, {'id': 'keyword', 'distance': None}]
restored = json.loads(json.dumps(hits))
assert restored[0]['distance'] == 0.0
assert restored[1]['distance'] is None
assert (0.0 or None) is None  # the bug an explicit None check avoids
ranks = {'vector': {'dense': 1}, 'keyword': {'lexical': 1}, 'both': {'dense': 2, 'lexical': 2}}
scores = {key: sum(1 / (60 + rank) for rank in channels.values()) for key, channels in ranks.items()}
assert scores['both'] > scores['vector'] == scores['keyword']
print('zero preserved; missing preserved; channel ranks fused separately')
