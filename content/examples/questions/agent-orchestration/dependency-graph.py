dependencies = {'policy': set(), 'status': set(), 'decide': {'policy', 'status'}}
completed = set()
ready = [step for step, parents in dependencies.items() if step not in completed and parents <= completed]
print(sorted(ready))
