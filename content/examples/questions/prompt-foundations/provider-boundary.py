provider_response = {'content': 'half an answer', 'stop_reason': 'limit'}
result = {'text': provider_response['content'],
          'status': 'completed' if provider_response['stop_reason'] == 'done' else 'incomplete',
          'usage': provider_response.get('usage')}
print(result['status'], result['usage'])
