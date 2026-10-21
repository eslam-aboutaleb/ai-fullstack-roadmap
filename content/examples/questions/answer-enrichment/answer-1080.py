wrong = [lambda: i for i in range(3)]
right = [lambda i=i: i for i in range(3)]
assert [f() for f in wrong] == [2, 2, 2]
assert [f() for f in right] == [0, 1, 2]
print("late=[2, 2, 2]; bound=[0, 1, 2]")
