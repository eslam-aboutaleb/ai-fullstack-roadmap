choose = lambda allowed, complete: 'denied' if not allowed else ('answer' if complete else 'clarify')
print(choose(False, False), choose(True, False))
