extract = lambda passage: {'rule': passage['rule']}
format_answer = lambda facts: f"Rule: {facts['rule']}"
print(format_answer(extract({'rule': 'exchange only', 'source': 'P2'})))
