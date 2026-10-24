import math
left, right = [1, 0], [1, 1]
dot = sum(x*y for x, y in zip(left, right))
length = lambda vector: math.sqrt(sum(x*x for x in vector))
cosine = dot / (length(left) * length(right))
distance = math.sqrt(sum((x-y)**2 for x, y in zip(left, right)))
print(dot, round(cosine, 6), distance)
