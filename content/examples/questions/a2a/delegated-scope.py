delegation = {'task': 'T1', 'audience': 'translator', 'resources': {'excerpt:D1:r2'}, 'expires': 100}
requested_resource = 'collection:all'
print(requested_resource in delegation['resources'])
