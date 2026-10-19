frames = [b'\x00\x01', {'type': 'cancel', 'generation': 2}]
print('audio' if isinstance(frames[0], bytes) else 'control', frames[1]['type'])
