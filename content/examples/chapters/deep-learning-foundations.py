weight,input_value,target = 1.0,2.0,5.0
prediction = weight*input_value
gradient = 2*(prediction-target)*input_value
next_weight = weight-0.1*gradient
assert abs(next_weight-2.2) < 1e-12
print(round(next_weight,3))
