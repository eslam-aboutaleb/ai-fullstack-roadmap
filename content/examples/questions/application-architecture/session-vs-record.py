messages = [{'id': f'M{i}', 'text': str(i)} for i in range(1, 4)]
session = {'connection': 'C1', 'working_messages': messages[-2:]}
print([message['id'] for message in session['working_messages']])
