tools = [{'name': 'search_policy', 'mode': 'read'}, {'name': 'create_request', 'mode': 'write'}]
mode = 'read'
print([tool['name'] for tool in tools if tool['mode'] == mode])
