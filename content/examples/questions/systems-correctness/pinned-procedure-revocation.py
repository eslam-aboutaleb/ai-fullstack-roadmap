"""Pinned task references cannot override emergency revocation."""
versions = {'v3': ('verify', 'approve', 'apply'), 'v4': ('verify', 'second-review', 'approve', 'apply')}
task = {'procedure_version': 'v3', 'next_step': 'apply'}
revoked = {'v3'}
def next_action(task):
    version = task['procedure_version']
    if version in revoked:
        return 'blocked: migrate or review'
    if task['next_step'] not in versions[version]:
        raise ValueError('unknown step')
    return task['next_step']
assert next_action(task) == 'blocked: migrate or review'
assert task['procedure_version'] == 'v3'
print('pinned v3 retained for audit; execution blocked')
