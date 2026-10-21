from math import dist
training = [((0.0, 0.0), "A"), ((10.0, 10.0), "B")]
query = (1.0, 1.0)
point, label = min(training, key=lambda pair: dist(query, pair[0]))
assert label == "A" and point == (0.0, 0.0)
print("nearest label=A")
