expected_tools = {'read_policy'}
observed_tools = ['read_policy', 'get_order']
print(expected_tools <= set(observed_tools))
