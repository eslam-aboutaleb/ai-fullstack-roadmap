import math
def checked(vector, dimension):
    if len(vector) != dimension:
        raise ValueError("incompatible dimension")
    values = [float(x) for x in vector]
    if not all(math.isfinite(x) for x in values):
        raise ValueError("non-finite embedding")
    return values
assert checked([1, 2], 2) == [1.0, 2.0]
