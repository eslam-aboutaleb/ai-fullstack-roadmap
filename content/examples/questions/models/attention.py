import math
query, keys = [1, 0], [[1, 0], [0, 1]]
values = [[10, 0], [0, 20]]
scores = [sum(q*k for q, k in zip(query, key))/math.sqrt(2) for key in keys]
weights = [math.exp(score) for score in scores]
weights = [weight/sum(weights) for weight in weights]
output = [sum(weight*value[j] for weight, value in zip(weights, values)) for j in range(2)]
print(weights[0] > weights[1], len(output))
