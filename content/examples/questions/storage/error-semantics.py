responses = [{'status': 'ok', 'items': []}, {'status': 'unavailable', 'items': None}]
print(*(response['status'] for response in responses))
