"""Demonstrate runtime vector validation before storing embedding provider responses."""
import math

class VectorValidationError(Exception):
    pass

def validate_embedding_response(vector, expected_dimension=1536):
    """
    Validate provider embedding array before inserting into vector database:
      1. Correct dimensionality (exact match).
      2. No NaN, Infinity, or -Infinity floating-point anomalies.
      3. Non-zero L2 norm (catch collapsed null vectors).
      4. Numerical element types.
    """
    if not isinstance(vector, (list, tuple)):
        raise VectorValidationError("Embedding must be a list or tuple")

    if len(vector) != expected_dimension:
        raise VectorValidationError(f"Dimension mismatch: expected {expected_dimension}, got {len(vector)}")

    sum_sq = 0.0
    for idx, val in enumerate(vector):
        if not isinstance(val, (int, float)):
            raise VectorValidationError(f"Non-numeric coordinate at index {idx}: {type(val)}")
        if math.isnan(val):
            raise VectorValidationError(f"NaN coordinate detected at index {idx}")
        if math.isinf(val):
            raise VectorValidationError(f"Infinite coordinate detected at index {idx}")
        sum_sq += val * val

    norm = math.sqrt(sum_sq)
    if norm < 1e-6:
        raise VectorValidationError("Collapsed zero-norm vector: all coordinates are near zero")

    return True

# 1. Valid embedding response:
valid_vec = [0.05] * 1536
assert validate_embedding_response(valid_vec, expected_dimension=1536) is True

# 2. Corrupted response with NaN:
nan_vec = [0.05] * 1536
nan_vec[42] = float('nan')
nan_rejected = False
try:
    validate_embedding_response(nan_vec, 1536)
except VectorValidationError:
    nan_rejected = True
assert nan_rejected is True

# 3. Dimension mismatch:
dim_rejected = False
try:
    validate_embedding_response([0.1] * 768, expected_dimension=1536)
except VectorValidationError:
    dim_rejected = True
assert dim_rejected is True

print(f"Vector validation verified: valid=True, nan_rejected={nan_rejected}, dim_rejected={dim_rejected}")
