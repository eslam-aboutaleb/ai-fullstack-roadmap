config = {'secret_from_runtime': True, 'tls_server_verified': True, 'secret_logged': False}
print(config['secret_from_runtime'] and config['tls_server_verified'] and not config['secret_logged'])
