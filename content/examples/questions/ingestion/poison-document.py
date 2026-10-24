active_revision = 1
replacement = {'revision': 2, 'source_nonempty': True, 'chunks': []}
if replacement['source_nonempty'] and not replacement['chunks']:
    status = 'quarantined'
else:
    active_revision, status = replacement['revision'], 'active'
print(active_revision, status)
