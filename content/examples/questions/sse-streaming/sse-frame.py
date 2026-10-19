frame = 'id: 7\ndata: hello\ndata: world\n\n'
lines = frame[:-2].splitlines()
event_id = next(line[4:] for line in lines if line.startswith('id: '))
data = '\n'.join(line[6:] for line in lines if line.startswith('data: '))
print(event_id, data.replace('\n', '|'))
