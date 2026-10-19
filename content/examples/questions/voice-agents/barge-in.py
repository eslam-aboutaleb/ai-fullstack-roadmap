active_generation = 2
frames = [{'generation': 1, 'audio': 'old'}, {'generation': 2, 'audio': 'new'}]
print([frame['audio'] for frame in frames if frame['generation'] == active_generation])
