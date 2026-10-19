backend = {'native_filters': True, 'durable': False, 'native_lexical': False}
required = {'native_filters', 'durable'}
print(all(backend[name] for name in required))
