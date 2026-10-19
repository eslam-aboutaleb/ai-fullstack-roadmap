true_positive, false_positive, false_negative = 6, 2, 4
precision = true_positive / (true_positive + false_positive)
recall = true_positive / (true_positive + false_negative)
print(precision, recall)
