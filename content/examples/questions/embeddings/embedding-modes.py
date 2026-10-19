requests = [{'mode': 'query', 'text': 'sale'}, {'mode': 'document', 'text': 'sale'}]
print(*(request['mode'] for request in requests))
