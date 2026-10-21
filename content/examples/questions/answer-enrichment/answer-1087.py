def records():
    yield 2
    yield 3
iterator = records()
assert list(iterator) == [2, 3]
assert list(iterator) == []
assert list(records()) == [2, 3]
print("first=[2, 3]; exhausted=[]; fresh=[2, 3]")
