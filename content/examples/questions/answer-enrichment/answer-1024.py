def gradient(w, x, y):
    return 2*(w*x-y)*x
batch = [(1.0, 2.0), (2.0, 3.0)]
w, rate = 1.0, 0.1
full_mean_gradient = sum(gradient(w,x,y) for x,y in batch)/len(batch)
accumulated = 0.0
for x, y in batch:
    accumulated += gradient(w,x,y)/len(batch)
assert accumulated == full_mean_gradient == -3.0
updated = w-rate*accumulated
assert abs(updated-1.3) < 1e-12
print("mean gradient=-3.0; one update w=1.3")
