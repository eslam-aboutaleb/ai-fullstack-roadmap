"""Structural conversion preserves unknown facts instead of guessing."""
def migrate(old):
    level = old.get('level')
    issues = []
    if level is None:
        level = 'unknown'
        issues.append('level requires confirmation')
    if level not in {'unknown', 'basic', 'fluent'}:
        raise ValueError('unsupported level')
    return dict(schema_version=2, language=old['language'], level=level), issues
record, issues = migrate({'language': 'Spanish'})
assert record['level'] == 'unknown' and issues
assert migrate({'language': 'Spanish', 'level': 'fluent'})[1] == []
print('missing fact preserved as unknown; confirmation issue recorded')
