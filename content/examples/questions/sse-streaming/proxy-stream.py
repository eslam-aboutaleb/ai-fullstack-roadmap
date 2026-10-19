config = {'app_flushes': True, 'proxy_buffers': True, 'heartbeat_seconds': 15}
print('investigate_buffering' if config['proxy_buffers'] else 'measure_delivery')
