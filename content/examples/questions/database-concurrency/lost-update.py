record = {'count': 0, 'version': 1}
def save(expected_version):
    if record['version'] != expected_version:
        return False
    record['count'] += 1
    record['version'] += 1
    return True
print(save(1), save(1), record['count'])
