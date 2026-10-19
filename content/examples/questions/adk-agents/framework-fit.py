need = {'model_chooses_tools': False, 'known_steps': True, 'durable_wait': False}
choice = 'agent' if need['model_chooses_tools'] else 'fixed_workflow'
print(choice)
