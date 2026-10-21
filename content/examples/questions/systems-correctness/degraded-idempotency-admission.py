"""Explicit degraded-mode policy for synthetic operations."""
def admission(*, read_only, coordinator_up, durable_destination_key):
    if read_only:
        return 'proceed-read'
    if durable_destination_key:
        return 'proceed-with-destination-dedup'
    if coordinator_up:
        return 'use-coordinator-and-reconcile'
    return 'defer-write'

assert admission(read_only=True, coordinator_up=False, durable_destination_key=False) == 'proceed-read'
assert admission(read_only=False, coordinator_up=False, durable_destination_key=False) == 'defer-write'
assert admission(read_only=False, coordinator_up=False, durable_destination_key=True) == 'proceed-with-destination-dedup'
print('reads proceed; unprotected writes defer; destination-dedup writes proceed')
