from math import exp

logits = [1000.0,1001.0]
shifted = [exp(value-max(logits)) for value in logits]
probabilities = [value/sum(shifted) for value in shifted]
assert abs(sum(probabilities)-1) < 1e-12
print([round(value,6) for value in probabilities])
