failures = {'retrieval_language': 12, 'stream_reconnect': 3, 'ui_spacing': 1}
print(max(failures, key=failures.get))
