import math
logits = {'exchange': 2.0, 'refund': 0.0}
temperature = 0.5
peak = max(logits.values())
weights = {token: math.exp((value - peak) / temperature) for token, value in logits.items()}
probs = {token: value / sum(weights.values()) for token, value in weights.items()}
print(max(probs, key=probs.get), round(sum(probs.values()), 6))
