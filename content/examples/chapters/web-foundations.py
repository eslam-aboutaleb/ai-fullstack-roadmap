def status_for(owner,record):
    if owner is None:
        return 401
    if record is None or record['owner'] != owner:
        return 404
    return 200

assert status_for('A', {'owner':'B'}) == 404
print(status_for('A', {'owner':'A'}))
