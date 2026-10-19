state = {'task': 'T1', 'needs_review': True, 'evidence': ['P2:r2']}
next_node = 'review' if state['needs_review'] else 'finish'
print(next_node)
