def pack(items, limit):
    selected, used = [], 0
    for item in items:
        if item["tokens"] < 0: raise ValueError("invalid cost")
        if used + item["tokens"] <= limit:
            selected.append(item)
            used += item["tokens"]
    return selected
assert len(pack([{"tokens": 4}, {"tokens": 8}], 10)) == 1
# Production budgeting must count the rendered prompt and reserve output space.
