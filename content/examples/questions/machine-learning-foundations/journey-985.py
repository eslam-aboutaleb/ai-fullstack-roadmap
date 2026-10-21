points=[0.0,1.0,9.0,10.0]
centers=[0.0,10.0]
groups=[[],[]]
for point in points:
    chosen=min(range(len(centers)),key=lambda i:abs(point-centers[i]))
    groups[chosen].append(point)
updated=[sum(group)/len(group) for group in groups]
assert updated == [0.5,9.5]
print(updated)
