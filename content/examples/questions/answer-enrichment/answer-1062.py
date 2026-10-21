x, y, w, learning_rate = 2.0, 3.0, 1.0, 0.1
loss = lambda value: (value*x-y)**2
gradient = 2*(w*x-y)*x
epsilon = 1e-5
numeric = (loss(w+epsilon)-loss(w-epsilon))/(2*epsilon)
assert abs(gradient-numeric) < 1e-8
updated = w-learning_rate*gradient
assert abs(updated-1.4) < 1e-12
assert loss(updated) < loss(w)
print(f"gradient={gradient:.1f}; w={updated:.1f}; loss={loss(updated):.2f}")
