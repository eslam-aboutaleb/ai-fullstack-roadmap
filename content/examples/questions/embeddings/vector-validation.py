import math
vector, expected_dimension = [0.2, float('nan')], 2
valid = len(vector) == expected_dimension and all(math.isfinite(x) for x in vector)
print(valid)
