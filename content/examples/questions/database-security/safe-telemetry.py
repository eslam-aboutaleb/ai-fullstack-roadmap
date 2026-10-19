event = {'duration_ms': 12, 'outcome': 'denied', 'document_text': 'private', 'token': 'secret'}
export = {key: event[key] for key in ('duration_ms', 'outcome')}
print(sorted(export))
