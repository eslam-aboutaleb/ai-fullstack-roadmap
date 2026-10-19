import math
def softmax(scores):
    maximum = max(scores)
    weights = [math.exp(score - maximum) for score in scores]
    total = sum(weights)
    return [weight / total for weight in weights]
assert abs(sum(softmax([1000, 1001])) - 1.0) < 1e-9
# Full attention also uses scaled query-key products, masks, and value vectors.
