"""Exact, one-dimensional distance fixture; not an ANN engine benchmark."""
rows = [("other", value) for value in range(10)] + [("mine", 10)]
def rank(items):
    return sorted(items, key=lambda item: abs(item[1]))
post = [row for row in rank(rows)[:10] if row[0] == "mine"]
pre = rank([row for row in rows if row[0] == "mine"])[:10]
assert post == [] and pre == [("mine", 10)]
print("post-filter:", post)
print("eligible-set:", pre)
