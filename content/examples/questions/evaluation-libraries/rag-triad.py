checks = {'context_relevance': True, 'groundedness': False, 'answer_relevance': True}
print([name for name, passed in checks.items() if not passed])
