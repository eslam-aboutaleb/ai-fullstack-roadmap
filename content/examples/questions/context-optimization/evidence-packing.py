budget, used, selected = 100, 0, []
for name, tokens in [('rule', 50), ('exception', 30), ('history', 60)]:
    if used+tokens <= budget:
        selected.append(name)
        used += tokens
print(selected, used)
