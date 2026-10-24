import json
row = {'case_id': 'case1', 'dataset': 'd1', 'configuration': 'cfg1',
       'deterministic_pass': True, 'judge_score': None, 'judge_error': 'timeout'}
loaded = json.loads(json.dumps(row))
print(loaded['case_id'], loaded['judge_score'])
