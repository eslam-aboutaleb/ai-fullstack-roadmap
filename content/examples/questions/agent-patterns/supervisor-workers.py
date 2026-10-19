workers = {'policy': lambda: {'source': 'P2'}, 'status': lambda: {'order': 'O1'}}
results = {name: work() for name, work in workers.items()}
print(sorted(results))
