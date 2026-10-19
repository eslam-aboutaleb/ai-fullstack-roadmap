manifest = {'collection': 'C1', 'generation': 3}
expected_old, prepared_new = 2, 4
accepted = manifest['generation'] == expected_old
if accepted:
    manifest['generation'] = prepared_new
print(accepted)
