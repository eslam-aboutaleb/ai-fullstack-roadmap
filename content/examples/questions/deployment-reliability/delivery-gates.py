release = {'source': 'synthetic-commit', 'artifact': 'image-digest', 'tests_pass': True,
           'secrets_external': True, 'rollback_tested': False}
print(release['tests_pass'] and release['secrets_external'] and release['rollback_tested'])
