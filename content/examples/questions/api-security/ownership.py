principal = 'user-b'
record = {'id': 'T1', 'owner': 'user-a', 'text': 'private'}
result = record['text'] if record['owner'] == principal else 'denied'
print(result)
