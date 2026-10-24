baseline = {'overall': 0.85, 'rare_escalation': 0.9}
adapted = {'overall': 0.9, 'rare_escalation': 0.7}
accept = adapted['overall'] >= baseline['overall'] and adapted['rare_escalation'] >= 0.85
print(accept)
