from math import exp, isfinite
logits = [1000.0, 1001.0]
shift = max(logits)
weights = [exp(value-shift) for value in logits]
probabilities = [value/sum(weights) for value in weights]
assert all(isfinite(value) for value in probabilities)
assert abs(sum(probabilities)-1) < 1e-12
print("softmax=" + ",".join(f"{value:.4f}" for value in probabilities))
