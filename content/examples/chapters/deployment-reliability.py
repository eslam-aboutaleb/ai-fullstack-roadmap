def max_connections(web_replicas, workers_per_replica, pool_size, overflow, worker_pools):
    return web_replicas * workers_per_replica * (pool_size + overflow) + worker_pools
assert max_connections(3, 2, 5, 2, 8) == 50
# Reserve additional database headroom for migrations, monitoring, and operators.
