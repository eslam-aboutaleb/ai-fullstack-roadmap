a = [1]
b = a
assert a is b
b.append(2)
assert a == [1, 2]
b = [9]
assert a == [1, 2] and b == [9] and a is not b
print(f"a={a}; b={b}")
