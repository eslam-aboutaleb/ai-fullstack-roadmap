def domain_excerpt(document_id, principal):
    document = {'id': 'D1', 'owner': 'A', 'text': 'Exchange only'}
    if document_id != document['id'] or principal != document['owner']:
        raise PermissionError('not available')
    return document['text'][:2000]
def tool_adapter(arguments, authenticated_principal):
    return {'text': domain_excerpt(arguments['document_id'], authenticated_principal)}
print(tool_adapter({'document_id': 'D1'}, 'A')['text'])
