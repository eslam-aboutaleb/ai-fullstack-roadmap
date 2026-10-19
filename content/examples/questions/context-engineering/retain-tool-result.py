result = {'status': 'completed', 'rows': list(range(50)), 'artifact': 'artifact:T1'}
compact = {'status': result['status'], 'count': len(result['rows']), 'artifact': result['artifact']}
print(compact)
