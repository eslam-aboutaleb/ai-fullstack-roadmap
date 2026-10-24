policies = [{'id': 'old', 'from': '2026-01-01', 'to': '2026-03-01'},
            {'id': 'new', 'from': '2026-03-01', 'to': '2027-01-01'}]
event_date = '2026-02-15'
print(next(policy['id'] for policy in policies if policy['from'] <= event_date < policy['to']))
