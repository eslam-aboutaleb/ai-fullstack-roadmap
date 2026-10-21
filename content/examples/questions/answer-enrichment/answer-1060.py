true_positive, false_positive, false_negative = 90, 99, 10
precision = true_positive / (true_positive + false_positive)
recall = true_positive / (true_positive + false_negative)
assert abs(precision - 90 / 189) < 1e-12
assert recall == 0.9
print(f"precision={precision:.4f}; recall={recall:.4f}")
