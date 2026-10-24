import math
samples_ms = [1, 2, 3, 4, 100]
p95 = sorted(samples_ms)[math.ceil(0.95*len(samples_ms))-1]
print(p95)
