def read(owner, principal):
    return 'private policy' if owner == principal else None
assert read('A', 'A') == 'private policy'
assert read('A', 'B') is None
print('isolation checks passed')
