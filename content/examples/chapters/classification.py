"""Cosine prototypes on declared numeric vectors, not neural encoder output."""
from math import sqrt

def unit(v):
    norm = sqrt(sum(x*x for x in v))
    if norm == 0: raise ValueError('zero vector')
    return [x/norm for x in v]
prototypes = {'A':unit([1,0]),'B':unit([0,1])}
query = unit([0.9,0.1])
scores = {label:sum(a*b for a,b in zip(query,vector)) for label,vector in prototypes.items()}
assert max(scores,key=scores.get) == 'A'
print('synthetic nearest prototype: A; real embeddings require the optional lab')
