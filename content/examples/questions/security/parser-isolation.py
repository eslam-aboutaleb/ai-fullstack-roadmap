policy = {'max_bytes': 2_000_000, 'timeout_seconds': 5,
          'read_only_root': True, 'outbound_network': True}
acceptable = policy['read_only_root'] and not policy['outbound_network']
print(acceptable)
