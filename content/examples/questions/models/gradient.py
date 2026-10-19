x, target, weight, learning_rate = 2, 6, 1, 0.1
gradient = 2*x*(weight*x-target)
weight -= learning_rate*gradient
prediction = weight*x
print(weight, prediction, round((prediction-target)**2, 6))
