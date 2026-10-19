runs = [('case1', False, True), ('case2', True, False), ('case3', True, True)]
wins = sum(new and not old for _, old, new in runs)
losses = sum(old and not new for _, old, new in runs)
print(wins, losses)
