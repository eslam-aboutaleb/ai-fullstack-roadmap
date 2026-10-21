def shared(value, tags=[]):
    tags.append(value)
    return tags
assert shared("A") == ["A"]
assert shared("B") == ["A", "B"]
def fresh(value, tags=None):
    tags = [] if tags is None else tags
    tags.append(value)
    return tags
assert fresh("A") == ["A"]
assert fresh("B") == ["B"]
print("shared default leaks; fresh default isolates")
