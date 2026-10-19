contract = {'version': 1, 'inputs': ['claim', 'source_id'], 'outputs': ['support_status'],
            'requires': {'read_excerpt'}}
host_tools = {'read_excerpt', 'search'}
print(contract['requires'] <= host_tools)
