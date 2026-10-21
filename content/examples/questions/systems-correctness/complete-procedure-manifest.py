"""Validate ordered identities and version for a synthetic procedure."""
def validate(rows, version, expected):
    if [row['step'] for row in rows] != expected:
        raise ValueError('missing, duplicate or reordered step')
    if any(row['version'] != version for row in rows):
        raise ValueError('mixed version')
    return True

rows = [dict(step=i, version='v3') for i in (1, 2, 3, 4)]
assert validate(rows, 'v3', [1, 2, 3, 4])
for broken in (rows[:2] + rows[3:], rows[:2] + rows[1:3], rows[::-1]):
    try:
        validate(broken, 'v3', [1, 2, 3, 4])
    except ValueError:
        pass
    else:
        raise AssertionError('invalid procedure accepted')
print('complete accepted; missing, duplicate and reordered steps rejected')
