messages = [{'role': 'system', 'content': 'Use approved sources'},
            {'role': 'user', 'content': 'Refund?'},
            {'role': 'tool', 'content': 'P2: exchange only'}]
print([message['role'] for message in messages])
