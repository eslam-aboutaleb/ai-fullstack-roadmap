replicas, processes, pool, overflow, workers = 3, 2, 5, 5, 10
connections = replicas*processes*(pool+overflow)+workers
print(connections, connections <= 60)
