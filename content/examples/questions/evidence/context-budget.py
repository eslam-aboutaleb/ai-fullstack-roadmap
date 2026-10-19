capacity = 8000
reserved = {'output': 1000, 'instructions_and_tools': 1200, 'history': 1500, 'margin': 300}
evidence_budget = capacity-sum(reserved.values())
assert evidence_budget >= 0
print(evidence_budget)
