proposals = [{'tool': 'read_policy'}, {'final': 'exchange only'}]
allowed, tool_calls, outcome = {'read_policy'}, 0, 'incomplete'
for proposal in proposals[:3]:
    if 'final' in proposal:
        outcome = 'completed'
        break
    if proposal['tool'] not in allowed:
        outcome = 'denied'
        break
    tool_calls += 1
print(outcome, tool_calls)
