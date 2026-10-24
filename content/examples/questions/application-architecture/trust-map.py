boundaries = {'browser': {'authentication', 'input_validation'},
              'document': {'parser_isolation', 'tool_policy'},
              'citation': {'resource_authorization'}}
print(all(bool(controls) for controls in boundaries.values()))
