train = [0.0, 2.0]
validation = [100.0]
mean = sum(train)/len(train)
transformed_train = [value-mean for value in train]
transformed_validation = [value-mean for value in validation]
assert mean == 1.0
assert transformed_train == [-1.0, 1.0]
assert transformed_validation == [99.0]
leaked_mean = sum(train+validation)/len(train+validation)
assert leaked_mean != mean
print("training mean=1.0; held-out transform=99.0")
