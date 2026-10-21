from math import exp, sqrt
def causal_output(values, position):
    query = values[position]
    visible = values[:position+1]
    scores = [query*key for key in visible]
    shift = max(scores)
    weights = [exp(score-shift) for score in scores]
    return sum(weight*value for weight, value in zip(weights, visible))/sum(weights)
a = [1.0, 2.0, 3.0]
b = [1.0, 2.0, 300.0]
assert causal_output(a, 1) == causal_output(b, 1)
assert causal_output(a, 2) != causal_output(b, 2)
print("future token cannot change position 1")
