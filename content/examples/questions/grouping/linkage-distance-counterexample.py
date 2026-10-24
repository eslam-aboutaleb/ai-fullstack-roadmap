"""Single and complete linkage emphasize different cross-group pairs."""
a,b = [0.0,1.0],[2.0,10.0]
distances = [abs(x-y) for x in a for y in b]
single,complete = min(distances),max(distances)
assert single==1.0 and complete==10.0
print('single linkage: 1.0; complete linkage: 10.0')
