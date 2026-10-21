"""Silhouette for four points under a declared two-group partition."""
x,labels = [0.0,1.0,9.0,10.0],[0,0,1,1]
scores = []
for i,value in enumerate(x):
    own = [abs(value-other) for j,other in enumerate(x) if j!=i and labels[j]==labels[i]]
    other = [abs(value-other) for j,other in enumerate(x) if labels[j]!=labels[i]]
    a,b = sum(own)/len(own),sum(other)/len(other)
    scores.append((b-a)/max(a,b))
assert all(0 < score <= 1 for score in scores)
assert len(set(labels))==2 and len(set(labels))<len(x)
print('silhouette positive for the fixture; a single group would be undefined')
