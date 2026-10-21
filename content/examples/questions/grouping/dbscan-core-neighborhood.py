"""Exact core-neighborhood test; self counts toward minimum support."""
points = [0.0,0.1,0.2,4.0]
radius,minimum = 0.15,3
neighbors = {i:[j for j,y in enumerate(points) if abs(x-y)<=radius] for i,x in enumerate(points)}
core = {i for i,near in neighbors.items() if len(near)>=minimum}
border = {i for i in range(len(points)) if i not in core and any(j in core for j in neighbors[i])}
noise = set(range(len(points))) - core - border
assert core=={1} and border=={0,2} and noise=={3}
print('core: {1}; border: {0, 2}; noise: {3}')
