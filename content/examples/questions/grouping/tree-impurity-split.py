"""Gini reduction for a declared binary split."""
def gini(labels):
    return 1-sum((labels.count(label)/len(labels))**2 for label in set(labels))
parent = [0, 0, 1, 1]
left, right = [0, 0], [1, 1]
gain = gini(parent) - (len(left)*gini(left)+len(right)*gini(right))/len(parent)
assert gain == 0.5
print('pure child split reduces Gini impurity by 0.5')
