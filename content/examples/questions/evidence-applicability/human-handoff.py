handoff = {'task': 'T1', 'reason': 'conflicting_rules', 'sources': ['P1:r2', 'P2:r3'],
           'owner': 'review_queue', 'pending_action': 'decide_applicability'}
print(handoff['task'], handoff['reason'], handoff['owner'])
