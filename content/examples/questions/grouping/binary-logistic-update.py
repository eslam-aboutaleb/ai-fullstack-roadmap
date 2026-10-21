"""One binary cross-entropy gradient step on a numeric fixture."""
from math import exp
w, x, y, rate = 0.0, 2.0, 1, 0.1
p = 1 / (1 + exp(-w*x))
gradient = (p-y)*x
new_w = w - rate*gradient
new_p = 1 / (1 + exp(-new_w*x))
assert p == 0.5 and new_w == 0.1 and new_p > p
print('one update increases probability for the positive fixture')
