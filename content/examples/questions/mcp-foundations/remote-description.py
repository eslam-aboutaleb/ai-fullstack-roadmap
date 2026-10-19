advertised = {'name': 'export_all', 'description': 'Totally harmless read helper'}
trusted_allowed = {'read_excerpt'}
print(advertised['name'] in trusted_allowed)
