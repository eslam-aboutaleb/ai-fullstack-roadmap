case = {'id': 'case-stale-cache', 'input': {'source_revision': 2, 'cache_revision': 1},
        'configuration': 'cache-v1', 'expected': 'revision_must_match', 'observed': 'stale_answer'}
print(case['id'], case['expected'])
