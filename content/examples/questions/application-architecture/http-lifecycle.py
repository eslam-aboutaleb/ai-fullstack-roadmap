def create_task(body):
    if not isinstance(body.get('question'), str) or not body['question'].strip():
        return 400, {'error': 'question_required'}
    return 202, {'task_id': 'T1', 'status_url': '/tasks/T1'}

print(create_task({})[0], create_task({'question': 'policy?'})[0],
      create_task({'question': 'policy?'})[1]['status_url'])
