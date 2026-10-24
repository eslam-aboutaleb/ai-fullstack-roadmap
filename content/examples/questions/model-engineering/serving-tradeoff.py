runs = [{'name': 'small_batch', 'throughput': 20, 'p95_ms': 500},
        {'name': 'large_batch', 'throughput': 40, 'p95_ms': 1500}]
allowed = [run for run in runs if run['p95_ms'] <= 800]
print(max(allowed, key=lambda run: run['throughput'])['name'])
