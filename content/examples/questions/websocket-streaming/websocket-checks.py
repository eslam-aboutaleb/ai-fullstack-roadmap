required = {'reconnect', 'duplicate_command', 'expired_auth', 'slow_consumer'}
executed = {'reconnect', 'duplicate_command', 'expired_auth'}
print(sorted(required-executed))
