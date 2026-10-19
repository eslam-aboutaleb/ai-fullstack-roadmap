choose = lambda needs_durable_branching: 'durable workflow' if needs_durable_branching else 'plain service'
print(choose(False), choose(True))
