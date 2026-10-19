stream = [{'type': 'delta', 'text': 'Partial answer'}]
terminal = next((event['type'] for event in stream if event['type'] in {'completed', 'failed'}), None)
print('completed' if terminal == 'completed' else 'incomplete')
