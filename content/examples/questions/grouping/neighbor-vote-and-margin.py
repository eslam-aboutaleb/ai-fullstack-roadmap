"""Numeric nearest-neighbor vote and a separate hinge-loss calculation."""
points = [(0.0, 'A'), (0.2, 'A'), (2.0, 'B')]
query = 0.1
near = sorted(points, key=lambda item:abs(item[0]-query))[:2]
assert [label for _,label in near] == ['A','A']
y, score = 1, 0.4
hinge = max(0, 1-y*score)
assert abs(hinge - 0.6) < 1e-12
print('local vote selects A; margin penalty is not a probability')
