turns = [{'item': 'I1', 'reviewed': True}, {'item': 'I2', 'reviewed': False}]
current, prior_approval = turns[-1], turns[0]
can_write = current['reviewed'] and current['item'] == prior_approval['item']
print(can_write)
