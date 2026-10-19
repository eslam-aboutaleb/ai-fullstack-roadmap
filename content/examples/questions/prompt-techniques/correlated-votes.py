from collections import Counter
outputs = ['refund allowed'] * 3
winner = Counter(outputs).most_common(1)[0][0]
current_rule = 'exchange only'
print(winner, winner == current_rule)
