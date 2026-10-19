tool = {'name': 'read_policy', 'description': 'Read an authorized policy by document ID',
        'required': ['document_id']}
agent = {'model': 'fake-model', 'instruction': 'Explain supported policy', 'tools': [tool], 'max_calls': 4}
print(agent['tools'][0]['name'], agent['max_calls'])
