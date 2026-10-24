operations = {'op1', 'op2'}
audit_rows = [{'operation': 'op1'}]
missing = operations - {row['operation'] for row in audit_rows}
print(sorted(missing))
