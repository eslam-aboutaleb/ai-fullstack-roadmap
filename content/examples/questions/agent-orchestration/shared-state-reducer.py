left = [{'id': 'E1', 'text': 'policy'}]
right = [{'id': 'E1', 'text': 'policy'}, {'id': 'E2', 'text': 'status'}]
merged = {event['id']: event for event in left+right}
print(sorted(merged))
