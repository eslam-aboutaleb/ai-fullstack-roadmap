"""Actual Lloyd updates on a tiny one-dimensional numeric fixture."""
points = [0.0,1.0,9.0,10.0]
centers = [0.0,10.0]
for _ in range(10):
    groups = [[x for x in points if min(range(2),key=lambda i:abs(x-centers[i]))==group] for group in range(2)]
    if any(not group for group in groups): raise ValueError('empty cluster needs policy')
    updated = [sum(group)/len(group) for group in groups]
    if updated == centers: break
    centers = updated
assert centers == [0.5,9.5]
assert groups == [[0.0,1.0],[9.0,10.0]]
print('Lloyd centers: [0.5, 9.5]; partition verified')
