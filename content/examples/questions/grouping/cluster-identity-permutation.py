"""Pairwise co-membership is invariant to arbitrary cluster-number names."""
a,b = [0,0,1,1],[8,8,3,3]
def pairs(labels):
    return {(i,j) for i in range(len(labels)) for j in range(i+1,len(labels)) if labels[i]==labels[j]}
assert pairs(a)==pairs(b)
assert a != b
print('different cluster IDs; identical membership relation')
