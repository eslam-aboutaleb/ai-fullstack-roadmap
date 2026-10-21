"""Explicit supported-version conversion, not a universal schema engine."""
def decode(wire):
    version = wire.get('schema_version')
    if version == 1:
        return {'display_name': wire['name']}
    if version == 2:
        return {'display_name': wire['display_name']}
    raise ValueError('unsupported schema version')
assert decode({'schema_version': 1, 'name': 'Example'}) == decode({'schema_version': 2, 'display_name': 'Example'})
try:
    decode({'schema_version': 3, 'label': 'Example'})
except ValueError:
    pass
else:
    raise AssertionError('future schema guessed')
print('supported historical payloads decoded; future schema rejected')
