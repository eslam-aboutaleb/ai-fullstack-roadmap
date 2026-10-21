"""Squared Euclidean and cosine relation for two unit vectors."""
from math import sqrt
u = [1.0,0.0]
v = [1/sqrt(2),1/sqrt(2)]
cosine = sum(a*b for a,b in zip(u,v))
squared = sum((a-b)**2 for a,b in zip(u,v))
assert abs(squared - (2-2*cosine)) < 1e-12
print('unit-vector distance relation verified; algorithm updates still matter')
